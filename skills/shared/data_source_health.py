#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Data-source health checks for auditable finance reports."""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime
from importlib.util import find_spec
import os
from typing import Callable, Dict, Iterable, List


PROXY_ENV_VARS = ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy")


PROVIDERS = {
    "akshare": {
        "name": "AkShare",
        "purpose": "A股行情、财务指标、资金流向",
        "critical": True,
        "live_probe": "_probe_akshare",
    },
    "yfinance": {
        "name": "yfinance",
        "purpose": "美股、港股、海外行情与基础财务字段",
        "critical": True,
        "live_probe": "_probe_yfinance",
    },
    "pandas": {
        "name": "pandas",
        "purpose": "表格处理与时间序列计算",
        "critical": True,
    },
    "numpy": {
        "name": "numpy",
        "purpose": "数值计算与指标计算",
        "critical": True,
    },
    "baostock": {
        "name": "Baostock",
        "purpose": "A股历史行情与财务备用数据源",
        "critical": False,
        "live_probe": "_probe_baostock",
    },
    "efinance": {
        "name": "efinance",
        "purpose": "A股行情备用数据源",
        "critical": False,
        "live_probe": "_probe_efinance",
    },
    "tushare": {
        "name": "Tushare",
        "purpose": "A股行情、财务和基础数据备用源，需要 Token",
        "critical": False,
    },
}


def check_provider(
    module_name: str,
    meta: Dict,
    *,
    live: bool = False,
    sample_symbol: str = "002050",
    suppress_proxy: bool = False,
) -> Dict:
    available = find_spec(module_name) is not None
    status = "可用" if available else "不可用"
    severity = "正常" if available else ("阻断" if meta.get("critical") else "提示")
    action = "无需处理" if available else f"安装或配置 {meta['name']} 后再生成依赖该数据源的真实报告"
    item = {
        "module": module_name,
        "name": meta["name"],
        "purpose": meta["purpose"],
        "status": status,
        "severity": severity,
        "available": available,
        "critical": bool(meta.get("critical")),
        "action": action,
        "live_checked": False,
        "live_status": "未检查",
        "live_message": "默认仅检查本地依赖；使用 doctor --live 才会请求真实接口。",
    }
    if live and available and meta.get("live_probe"):
        probe = LIVE_PROBES.get(meta["live_probe"])
        if probe:
            with _temporary_proxy_suppression(suppress_proxy):
                item.update(probe(sample_symbol))
            if suppress_proxy:
                item["proxy_suppressed"] = True
    elif live and available:
        item.update({
            "live_checked": False,
            "live_status": "不适用",
            "live_message": "该依赖为本地计算或需要额外凭证，未做实时请求。",
        })
    return item


def check_data_sources(
    providers: Iterable[str] | None = None,
    *,
    live: bool = False,
    sample_symbol: str = "002050",
    suppress_proxy: bool = False,
) -> Dict:
    selected = list(providers) if providers else ["akshare", "yfinance", "pandas", "numpy", "baostock", "efinance", "tushare"]
    items: List[Dict] = [
        check_provider(name, PROVIDERS[name], live=live, sample_symbol=sample_symbol, suppress_proxy=suppress_proxy)
        for name in selected
        if name in PROVIDERS
    ]
    critical_missing = [item for item in items if item["critical"] and not item["available"]]
    live_failures = [item for item in items if item.get("live_checked") and item.get("live_status") == "请求失败"]
    available_count = sum(1 for item in items if item["available"])
    live_success_count = sum(1 for item in items if item.get("live_status") == "请求成功")

    if critical_missing:
        status = "需要处理"
        summary = "存在核心依赖不可用，报告必须明确披露缺失来源，不能用模拟数据补齐。"
    elif live and live_failures:
        status = "接口异常"
        summary = "本地依赖已安装，但部分实时数据请求失败；请检查网络、代理、接口限流或数据源变更。"
    else:
        status = "正常"
        summary = "核心依赖可用；若需要确认实时行情接口，请运行 doctor --live。"
        if live:
            summary = "核心依赖可用，实时请求探测已完成。"

    return {
        "success": True,
        "checked_at": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "summary": summary,
        "available_count": available_count,
        "total_count": len(items),
        "live_checked": live,
        "live_success_count": live_success_count,
        "proxy_suppressed": bool(suppress_proxy and live),
        "critical_missing": [item["name"] for item in critical_missing],
        "live_failures": [item["name"] for item in live_failures],
        "items": items,
    }


@contextmanager
def _temporary_proxy_suppression(enabled: bool):
    if not enabled:
        yield
        return
    saved = {name: os.environ.get(name) for name in PROXY_ENV_VARS}
    for name in PROXY_ENV_VARS:
        os.environ.pop(name, None)
    try:
        yield
    finally:
        for name, value in saved.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value


def classify_live_error(exc: Exception | str) -> Dict:
    """Classify live provider failures into actionable, machine-readable buckets."""

    message = str(exc)
    lowered = message.lower()
    proxy_vars = [
        name
        for name in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy")
        if os.environ.get(name)
    ]

    if any(token in lowered for token in ["proxyerror", "cannot connect to proxy", "winerror 10061", "connection refused"]):
        error_type = "proxy_connection_refused"
        action_hint = "检查代理服务是否启动，或清理 HTTP_PROXY/HTTPS_PROXY/ALL_PROXY 后重试。"
    elif "remotedisconnected" in lowered or "remote end closed connection" in lowered:
        error_type = "remote_disconnected"
        action_hint = "数据源主动断开连接，通常与限流、接口变更或网络出口有关；稍后重试或切换备用源。"
    elif "unable to open database file" in lowered:
        error_type = "local_cache_error"
        action_hint = "本地缓存数据库无法打开；检查 yfinance/peewee 缓存目录权限，或将 TMP/TEMP 指向可写目录后重试。"
    elif any(token in lowered for token in ["timed out", "timeout", "read timed out"]):
        error_type = "timeout"
        action_hint = "请求超时；建议降低频率、延长超时或切换网络出口。"
    elif any(token in lowered for token in ["name resolution", "getaddrinfo", "nodename nor servname"]):
        error_type = "dns_failure"
        action_hint = "DNS 解析失败；检查网络、DNS 或代理配置。"
    elif any(token in lowered for token in ["ssl", "certificate", "tls"]):
        error_type = "tls_failure"
        action_hint = "TLS/证书握手失败；检查证书链、代理证书或数据源 HTTPS 策略。"
    elif "empty" in lowered or "返回为空" in message:
        error_type = "empty_response"
        action_hint = "接口返回为空；确认样本代码、交易日和接口字段是否仍有效。"
    else:
        error_type = "unknown_live_error"
        action_hint = "查看 live_message 原始错误，并尝试 doctor --live 更换样本代码复核。"

    return {
        "error_type": error_type,
        "action_hint": action_hint,
        "proxy_env_present": bool(proxy_vars),
        "proxy_env_vars": proxy_vars,
    }


def _probe_akshare(sample_symbol: str) -> Dict:
    try:
        import akshare as ak

        hist = ak.stock_zh_a_hist(symbol=sample_symbol, period="daily", adjust="qfq")
        ok = hist is not None and not getattr(hist, "empty", True)
        return {
            "live_checked": True,
            "live_status": "请求成功" if ok else "请求失败",
            "live_message": "已获取A股日线样本。" if ok else "接口返回为空。",
            **({} if ok else classify_live_error("返回为空")),
        }
    except Exception as exc:
        return {
            "live_checked": True,
            "live_status": "请求失败",
            "live_message": f"实时请求失败：{exc}",
            **classify_live_error(exc),
        }


def _probe_yfinance(sample_symbol: str) -> Dict:
    try:
        import yfinance as yf

        symbol = "AAPL" if sample_symbol.isdigit() else sample_symbol
        hist = yf.Ticker(symbol).history(period="5d")
        ok = hist is not None and not getattr(hist, "empty", True)
        return {
            "live_checked": True,
            "live_status": "请求成功" if ok else "请求失败",
            "live_message": "已获取海外股票日线样本。" if ok else "接口返回为空。",
            **({} if ok else classify_live_error("返回为空")),
        }
    except Exception as exc:
        return {
            "live_checked": True,
            "live_status": "请求失败",
            "live_message": f"实时请求失败：{exc}",
            **classify_live_error(exc),
        }


def _probe_baostock(sample_symbol: str) -> Dict:
    try:
        import baostock as bs

        code = f"sh.{sample_symbol}" if sample_symbol.startswith("6") else f"sz.{sample_symbol}"
        login = bs.login()
        if login.error_code != "0":
            return {
                "live_checked": True,
                "live_status": "请求失败",
                "live_message": f"登录失败：{login.error_msg}",
                **classify_live_error(login.error_msg),
            }
        rs = bs.query_history_k_data_plus(code, "date,open,high,low,close", start_date="2026-01-01")
        rows = []
        while (rs.error_code == "0") and rs.next():
            rows.append(rs.get_row_data())
            if rows:
                break
        bs.logout()
        ok = bool(rows)
        return {
            "live_checked": True,
            "live_status": "请求成功" if ok else "请求失败",
            "live_message": "已获取 Baostock 行情样本。" if ok else "Baostock 返回为空。",
            **({} if ok else classify_live_error("返回为空")),
        }
    except Exception as exc:
        try:
            import baostock as bs
            bs.logout()
        except Exception:
            pass
        return {
            "live_checked": True,
            "live_status": "请求失败",
            "live_message": f"实时请求失败：{exc}",
            **classify_live_error(exc),
        }


def _probe_efinance(sample_symbol: str) -> Dict:
    try:
        import efinance as ef

        hist = ef.stock.get_quote_history(sample_symbol)
        ok = hist is not None and not getattr(hist, "empty", True)
        return {
            "live_checked": True,
            "live_status": "请求成功" if ok else "请求失败",
            "live_message": "已获取 efinance 行情样本。" if ok else "efinance 返回为空。",
            **({} if ok else classify_live_error("返回为空")),
        }
    except Exception as exc:
        return {
            "live_checked": True,
            "live_status": "请求失败",
            "live_message": f"实时请求失败：{exc}",
            **classify_live_error(exc),
        }


LIVE_PROBES: Dict[str, Callable[[str], Dict]] = {
    "_probe_akshare": _probe_akshare,
    "_probe_yfinance": _probe_yfinance,
    "_probe_baostock": _probe_baostock,
    "_probe_efinance": _probe_efinance,
}


__all__ = ["check_data_sources", "check_provider", "classify_live_error", "PROVIDERS"]
