#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一数据层 Protocol 定义

设计原则（参考 manmankan 的防腐层模式）:
- 每个领域独立 Protocol (QuoteSource / KlineSource / FinancialSource)
- 实现者只负责 "网络 I/O + source-specific 字段 rename 到标准 schema"
- domain model 永不感知数据源差异（防腐层）
- 链式编排由 SourceChain 统一接管（熔断器/并发 race/debug_log/_source 标注）

priority 约定:
- 0-9   保留给极顶档（未来 ToB 付费 + 自部署）
- 10-19 内置付费（tushare）
- 20-29 内置免费稳定（baostock）
- 30-39 内置免费 race（eastmoney / sina）
- 40-49 内置免费兜底
- 50-89 留给用户自定义源
- 90-99 保留给极兜底 fallback
"""

from __future__ import annotations

import time
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable
from datetime import datetime

import pandas as pd

logger = logging.getLogger(__name__)


# ── 标准 Schema 定义 ──────────────────────────────────────────

@dataclass
class QuoteData:
    """实时行情标准 schema"""
    symbol: str
    name: str = ""
    price: float = 0.0
    open: float = 0.0
    high: float = 0.0
    low: float = 0.0
    close: float = 0.0
    volume: float = 0.0
    amount: float = 0.0
    change_pct: float = 0.0
    turnover_rate: float = 0.0
    market_cap: float = 0.0
    pe: float = 0.0
    pb: float = 0.0
    source: str = ""
    fetched_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if v != 0 or k in ('price', 'open', 'high', 'low', 'close')}


@dataclass
class KlineData:
    """K 线标准 schema"""
    symbol: str
    df: pd.DataFrame = field(default_factory=pd.DataFrame)
    source: str = ""
    fetched_at: datetime = field(default_factory=datetime.now)

    REQUIRED_COLUMNS = ['date', 'open', 'high', 'low', 'close']

    def is_valid(self) -> bool:
        if self.df.empty:
            return False
        return all(col in self.df.columns for col in self.REQUIRED_COLUMNS)


@dataclass
class FinancialData:
    """财务数据标准 schema"""
    symbol: str
    eps: float = 0.0
    bvps: float = 0.0
    ocfps: float = 0.0
    roe: float = 0.0
    gross_margin: float = 0.0
    net_margin: float = 0.0
    revenue_yoy: float = 0.0
    profit_yoy: float = 0.0
    debt_ratio: float = 0.0
    source: str = ""
    fetched_at: datetime = field(default_factory=datetime.now)
    report_period: str = ""


# ── Protocol 定义 ──────────────────────────────────────────────

@runtime_checkable
class QuoteSource(Protocol):
    name: str
    priority: int
    def is_available(self) -> bool: ...
    def fetch_quote(self, symbol: str) -> Optional[QuoteData]: ...


@runtime_checkable
class KlineSource(Protocol):
    name: str
    priority: int
    def is_available(self) -> bool: ...
    def fetch_kline(self, symbol: str, start: Optional[str] = None, end: Optional[str] = None) -> Optional[KlineData]: ...


@runtime_checkable
class FinancialSource(Protocol):
    name: str
    priority: int
    def is_available(self) -> bool: ...
    def fetch_financial(self, symbol: str) -> Optional[FinancialData]: ...


# ── 熔断器 ────────────────────────────────────────────────────

class CircuitBreaker:
    def __init__(self, name: str, failure_threshold: int = 3, recovery_seconds: int = 300):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_seconds = recovery_seconds
        self._failures = 0
        self._last_failure_time: Optional[float] = None
        self._state = "closed"

    def record_success(self):
        self._failures = 0
        self._state = "closed"

    def record_failure(self):
        self._failures += 1
        self._last_failure_time = time.time()
        if self._failures >= self.failure_threshold:
            self._state = "open"
            logger.warning(f"Circuit breaker [{self.name}] triggered, {self._failures} consecutive failures")

    def is_available(self) -> bool:
        if self._state == "closed":
            return True
        if self._state == "open":
            if self._last_failure_time and (time.time() - self._last_failure_time > self.recovery_seconds):
                self._state = "half_open"
                return True
            return False
        return True

    @property
    def state(self) -> str:
        return self._state


# ── 责任链 ────────────────────────────────────────────────────

class SourceChain:
    def __init__(self, sources: List):
        self.sources = sorted(sources, key=lambda s: s.priority)
        self.breakers: Dict[str, CircuitBreaker] = {s.name: CircuitBreaker(s.name) for s in sources}

    def fetch(self, method_name: str, *args, **kwargs) -> Optional[Any]:
        from concurrent.futures import ThreadPoolExecutor, as_completed

        priority_groups: Dict[int, List] = {}
        for s in self.sources:
            if s.is_available() and self.breakers[s.name].is_available():
                priority_groups.setdefault(s.priority, []).append(s)

        for priority in sorted(priority_groups.keys()):
            group = priority_groups[priority]

            if len(group) == 1:
                source = group[0]
                try:
                    method = getattr(source, method_name)
                    result = method(*args, **kwargs)
                    if result is not None:
                        self.breakers[source.name].record_success()
                        logger.debug(f"[{source.name}] success (priority={priority})")
                        return result
                    else:
                        self.breakers[source.name].record_failure()
                except Exception as e:
                    self.breakers[source.name].record_failure()
                    logger.debug(f"[{source.name}] error: {e} (priority={priority})")
            else:
                with ThreadPoolExecutor(max_workers=len(group)) as executor:
                    futures = {}
                    for source in group:
                        method = getattr(source, method_name)
                        futures[executor.submit(method, *args, **kwargs)] = source

                    for future in as_completed(futures, timeout=10):
                        source = futures[future]
                        try:
                            result = future.result()
                            if result is not None:
                                self.breakers[source.name].record_success()
                                for f in futures:
                                    f.cancel()
                                logger.debug(f"[{source.name}] race winner (priority={priority})")
                                return result
                            else:
                                self.breakers[source.name].record_failure()
                        except Exception:
                            self.breakers[source.name].record_failure()

        logger.warning(f"All sources failed (method={method_name})")
        return None


# ── 数据新鲜度 ────────────────────────────────────────────────

@dataclass
class Freshness:
    data_cutoff: Optional[datetime] = None
    cache_age_seconds: float = 0.0
    is_stale: bool = False
    phase: str = "unknown"

    @property
    def label(self) -> str:
        if self.is_stale:
            return "stale"
        if self.cache_age_seconds < 60:
            return "realtime"
        if self.cache_age_seconds < 300:
            return "delayed"
        return "stale"


# ── 统一数据层 Facade ─────────────────────────────────────────

class DataLayer:
    """
    统一数据层入口：所有模块通过 DataLayer 获取数据。
    同一只股票只取一次数据，全局缓存复用。
    """

    def __init__(self):
        from skills.shared.data_layer.sources import (
            AkShareQuoteSource, AkShareKlineSource, AkShareFinancialSource,
            EfinanceQuoteSource, SinaQuoteSource, BaostockKlineSource, BaostockFinancialSource,
        )

        self._quote_chain = SourceChain([
            EfinanceQuoteSource(),
            SinaQuoteSource(),
            AkShareQuoteSource(),
        ])

        self._kline_chain = SourceChain([
            BaostockKlineSource(),
            AkShareKlineSource(),
        ])

        self._financial_chain = SourceChain([
            BaostockFinancialSource(),
            AkShareFinancialSource(),
        ])

        self._cache: Dict[str, tuple] = {}
        self._cache_ttl = 300

    def _cache_key(self, category: str, symbol: str, **kwargs) -> str:
        extra = "_".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
        return f"{category}:{symbol}:{extra}"

    def _get_cached(self, key: str) -> Optional[Any]:
        if key in self._cache:
            data, ts = self._cache[key]
            age = time.time() - ts
            if age < self._cache_ttl:
                return data
            else:
                del self._cache[key]
        return None

    def _set_cached(self, key: str, data: Any):
        self._cache[key] = (data, time.time())

    def get_quote(self, symbol: str) -> Optional[QuoteData]:
        key = self._cache_key("quote", symbol)
        cached = self._get_cached(key)
        if cached is not None:
            return cached
        result = self._quote_chain.fetch("fetch_quote", symbol)
        if result is not None:
            self._set_cached(key, result)
        return result

    def get_kline(self, symbol: str, start: Optional[str] = None, end: Optional[str] = None) -> Optional[KlineData]:
        key = self._cache_key("kline", symbol, start=start or "", end=end or "")
        cached = self._get_cached(key)
        if cached is not None:
            return cached
        result = self._kline_chain.fetch("fetch_kline", symbol, start=start, end=end)
        if result is not None:
            self._set_cached(key, result)
        return result

    def get_financial(self, symbol: str) -> Optional[FinancialData]:
        key = self._cache_key("financial", symbol)
        cached = self._get_cached(key)
        if cached is not None:
            return cached
        result = self._financial_chain.fetch("fetch_financial", symbol)
        if result is not None:
            self._set_cached(key, result)
        return result

    def get_freshness(self, symbol: str) -> Freshness:
        now = datetime.now()
        from datetime import time as dt_time
        t = now.time()
        if dt_time(9, 15) <= t < dt_time(9, 30):
            phase = "pre_market"
        elif dt_time(9, 30) <= t < dt_time(11, 30) or dt_time(13, 0) <= t < dt_time(15, 0):
            phase = "trading"
        elif dt_time(11, 30) <= t < dt_time(13, 0):
            phase = "post_market"
        else:
            phase = "closed"

        key = self._cache_key("quote", symbol)
        is_stale = False
        cache_age = 0.0
        data_cutoff = None
        if key in self._cache:
            data, ts = self._cache[key]
            cache_age = time.time() - ts
            if hasattr(data, 'fetched_at'):
                data_cutoff = data.fetched_at
            if phase == "trading" and cache_age > 60:
                is_stale = True
            elif phase != "trading" and cache_age > 3600:
                is_stale = True

        return Freshness(data_cutoff=data_cutoff, cache_age_seconds=cache_age, is_stale=is_stale, phase=phase)

    def clear_cache(self, symbol: Optional[str] = None):
        if symbol:
            keys_to_remove = [k for k in self._cache if f":{symbol}:" in k]
            for k in keys_to_remove:
                del self._cache[k]
        else:
            self._cache.clear()

    def health_check(self) -> Dict[str, Any]:
        results = {}
        for chain_name, chain in [("quote", self._quote_chain), ("kline", self._kline_chain), ("financial", self._financial_chain)]:
            sources_status = {}
            for s in chain.sources:
                available = s.is_available()
                breaker = chain.breakers.get(s.name)
                breaker_state = breaker.state if breaker else "unknown"
                sources_status[s.name] = {"priority": s.priority, "available": available, "breaker": breaker_state}
            results[chain_name] = sources_status
        return results


_data_layer: Optional[DataLayer] = None

def get_data_layer() -> DataLayer:
    global _data_layer
    if _data_layer is None:
        _data_layer = DataLayer()
    return _data_layer
