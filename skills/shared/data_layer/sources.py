#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据源实现：每个 Source 只负责 I/O + 字段 rename 到标准 schema
异常吞掉返 None，chain 负责 fallback
"""

from __future__ import annotations

import logging
from typing import Optional
from datetime import datetime

from skills.shared.data_layer import QuoteData, KlineData, FinancialData

logger = logging.getLogger(__name__)


# ── AkShare 数据源 ────────────────────────────────────────────

class AkShareQuoteSource:
    name = "akshare"
    priority = 35

    def is_available(self) -> bool:
        try:
            import akshare
            return True
        except ImportError:
            return False

    def fetch_quote(self, symbol: str) -> Optional[QuoteData]:
        try:
            import akshare as ak
            df = ak.stock_zh_a_spot_em()
            row = df[df['代码'] == symbol]
            if row.empty:
                return None
            r = row.iloc[0]
            q = QuoteData(
                symbol=symbol,
                price=float(r.get('最新价') or 0) if r.get('最新价') else None,
                open=float(r.get('今开') or 0) if r.get('今开') else None,
                high=float(r.get('最高') or 0) if r.get('最高') else None,
                low=float(r.get('最低') or 0) if r.get('最低') else None,
                close=float(r.get('收盘价') or 0) if r.get('收盘价') else None,
                volume=float(r.get('成交量') or 0) if r.get('成交量') else None,
                amount=float(r.get('成交额') or 0) if r.get('成交额') else None,
                change_pct=float(r.get('涨跌幅') or 0) if r.get('涨跌幅') else None,
                turnover_rate=float(r.get('换手率') or 0) if r.get('换手率') else None,
                market_cap=float(r.get('总市值') or 0) if r.get('总市值') else None,
                pe=float(r.get('市盈率-动态') or 0) if r.get('市盈率-动态') else None,
                pb=float(r.get('市净率') or 0) if r.get('市净率') else None,
                source=self.name,
            )
            # 核心字段缺失则返回None（防造假）
            if q.price is None:
                logger.debug(f"[akshare] quote for {symbol}: price missing, returning None")
                return None
            return q
        except Exception as e:
            logger.debug(f"[akshare] quote error: {e}")
            return None
            logger.debug(f"[akshare] quote error: {e}")
            return None


class AkShareKlineSource:
    name = "akshare_kline"
    priority = 35

    def is_available(self) -> bool:
        try:
            import akshare
            return True
        except ImportError:
            return False

    def fetch_kline(self, symbol: str, start: Optional[str] = None, end: Optional[str] = None) -> Optional[KlineData]:
        try:
            import akshare as ak
            import pandas as pd
            df = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date=start or "20240101", end_date=end or "20991231", adjust="qfq")
            if df.empty:
                return None
            df = df.rename(columns={
                '日期': 'date', '开盘': 'open', '收盘': 'close',
                '最高': 'high', '最低': 'low', '成交量': 'volume', '成交额': 'amount',
            })
            df['date'] = pd.to_datetime(df['date'])
            return KlineData(symbol=symbol, df=df, source=self.name)
        except Exception as e:
            logger.debug(f"[akshare] kline error: {e}")
            return None


class AkShareFinancialSource:
    name = "akshare_financial"
    priority = 35

    def is_available(self) -> bool:
        try:
            import akshare
            return True
        except ImportError:
            return False

    def fetch_financial(self, symbol: str) -> Optional[FinancialData]:
        try:
            import akshare as ak
            fa = ak.stock_financial_analysis_indicator(symbol=symbol, start_year="2024")
            if fa.empty:
                return None
            latest = fa.iloc[0]
            return FinancialData(
                symbol=symbol,
                eps=float(latest.get('摊薄每股收益(元)', 0) or 0),
                bvps=float(latest.get('每股净资产_调整前(元)', 0) or 0),
                ocfps=float(latest.get('每股经营性现金流(元)', 0) or 0),
                roe=float(latest.get('净资产收益率(%)', 0) or 0),
                gross_margin=float(latest.get('主营业务利润率(%)', 0) or 0),
                net_margin=float(latest.get('总资产利润率(%)', 0) or 0),
                source=self.name,
                report_period=str(latest.get('日期', '')),
            )
        except Exception as e:
            logger.debug(f"[akshare] financial error: {e}")
            return None


# ── Efinance 数据源 ───────────────────────────────────────────

class EfinanceQuoteSource:
    name = "efinance"
    priority = 30

    def is_available(self) -> bool:
        try:
            import efinance
            return True
        except ImportError:
            return False

    def fetch_quote(self, symbol: str) -> Optional[QuoteData]:
        try:
            import efinance as ef
            df = ef.stock.get_realtime_quotes()
            row = df[df['股票代码'] == symbol]
            if row.empty:
                return None
            r = row.iloc[0]
            return QuoteData(
                symbol=symbol,
                name=str(r.get('股票名称', '')),
                price=float(r.get('最新价', 0) or 0),
                open=float(r.get('今开', 0) or 0),
                high=float(r.get('最高', 0) or 0),
                low=float(r.get('最低', 0) or 0),
                close=float(r.get('收盘价', 0) or 0),
                volume=float(r.get('成交量', 0) or 0),
                amount=float(r.get('成交额', 0) or 0),
                change_pct=float(r.get('涨跌幅', 0) or 0),
                source=self.name,
            )
        except Exception as e:
            logger.debug(f"[efinance] quote error: {e}")
            return None


# ── 新浪财经数据源 ────────────────────────────────────────────

class SinaQuoteSource:
    name = "sina"
    priority = 31

    def is_available(self) -> bool:
        return True  # 新浪 API 无需额外安装

    def fetch_quote(self, symbol: str) -> Optional[QuoteData]:
        try:
            import requests
            # 新浪实时行情 API
            prefix = "sh" if symbol.startswith("6") else "sz"
            url = f"https://hq.sinajs.cn/list={prefix}{symbol}"
            headers = {"Referer": "https://finance.sina.com.cn"}
            resp = requests.get(url, headers=headers, timeout=5)
            if resp.status_code != 200:
                return None
            content = resp.text
            if '="' not in content:
                return None
            data_str = content.split('="')[1].rstrip('";\n')
            fields = data_str.split(',')
            if len(fields) < 32:
                return None
            return QuoteData(
                symbol=symbol,
                name=fields[0],
                open=float(fields[1] or 0),
                close=float(fields[2]) if fields[2] else None,
                price=float(fields[3] or 0),
                high=float(fields[4] or 0),
                low=float(fields[5] or 0),
                volume=float(fields[8] or 0),
                amount=float(fields[9] or 0),
                source=self.name,
            )
        except Exception as e:
            logger.debug(f"[sina] quote error: {e}")
            return None


# ── Baostock 数据源 ───────────────────────────────────────────

class BaostockKlineSource:
    name = "baostock"
    priority = 20

    def is_available(self) -> bool:
        try:
            import baostock
            return True
        except ImportError:
            return False

    def fetch_kline(self, symbol: str, start: Optional[str] = None, end: Optional[str] = None) -> Optional[KlineData]:
        try:
            import baostock as bs
            import pandas as pd
            lg = bs.login()
            if lg.error_code != '0':
                return None
            try:
                prefix = "sh" if symbol.startswith("6") else "sz"
                rs = bs.query_history_k_data_plus(
                    f"{prefix}.{symbol}",
                    "date,open,high,low,close,volume,amount",
                    start_date=start or "2024-01-01",
                    end_date=end or "2099-12-31",
                    frequency="d",
                    adjustflag="2",
                )
                rows = []
                while rs.next():
                    rows.append(rs.get_row_data())
                if not rows:
                    return None
                df = pd.DataFrame(rows, columns=rs.fields)
                for col in ['open', 'high', 'low', 'close', 'volume', 'amount']:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                df['date'] = pd.to_datetime(df['date'])
                return KlineData(symbol=symbol, df=df, source=self.name)
            finally:
                bs.logout()
        except Exception as e:
            logger.debug(f"[baostock] kline error: {e}")
            return None


class BaostockFinancialSource:
    name = "baostock_financial"
    priority = 20

    def is_available(self) -> bool:
        try:
            import baostock
            return True
        except ImportError:
            return False

    def fetch_financial(self, symbol: str) -> Optional[FinancialData]:
        try:
            import baostock as bs
            from datetime import datetime
            lg = bs.login()
            if lg.error_code != '0':
                return None
            try:
                prefix = "sh" if symbol.startswith("6") else "sz"
                code = f"{prefix}.{symbol}"
                # 自动选择最近可用季度
                now = datetime.now()
                year = now.year - 1 if now.month < 5 else now.year
                quarter = 4 if now.month < 5 else min((now.month - 1) // 3, 4)
                rs = bs.query_growth_data(code=code, year=year, quarter=quarter)
                rows = []
                while rs.next():
                    rows.append(rs.get_row_data())
                if not rows:
                    # 尝试上一季度
                    q = quarter - 1 if quarter > 1 else 4
                    y = year if quarter > 1 else year - 1
                    rs = bs.query_growth_data(code=code, year=y, quarter=q)
                    while rs.next():
                        rows.append(rs.get_row_data())
                if not rows:
                    return None
                r = rows[0]
                # query_growth_data fields by index:
                # 0:code, 1:pubDate, 2:statDate, 3:equityYOY, 4:assetYOY, 5:npYOY, 6:epsYOY, 7:orYOY
                def safe_float(val):
                    try:
                        return float(val) if val and val != '' else 0.0
                    except (ValueError, TypeError):
                        return 0.0
                return FinancialData(
                    symbol=symbol,
                    revenue_yoy=safe_float(r[7]) if len(r) > 7 else 0.0,  # orYOY = 营收同比增长率
                    profit_yoy=safe_float(r[5]) if len(r) > 5 else 0.0,   # npYOY = 净利润同比增长率
                    source=self.name,
                )
            finally:
                bs.logout()
        except Exception as e:
            logger.debug(f"[baostock] financial error: {e}")
            return None


# ── 加密货币数据源 (ccxt) ──────────────────────────────────────

class CcxtQuoteSource:
    """加密货币行情源 - 基于 ccxt (100+ 交易所)"""
    name = "ccxt"
    priority = 30

    def __init__(self, exchange: str = 'binance'):
        self.exchange_name = exchange
        self._exchange = None

    def _get_exchange(self):
        if self._exchange is None:
            try:
                import ccxt
                self._exchange = getattr(ccxt, self.exchange_name)({
                    'enableRateLimit': True,
                })
            except ImportError:
                raise ImportError("请安装 ccxt: pip install ccxt")
        return self._exchange

    def is_available(self) -> bool:
        try:
            import ccxt
            return True
        except ImportError:
            return False

    def fetch_quote(self, symbol: str) -> Optional[QuoteData]:
        try:
            exchange = self._get_exchange()
            ticker = exchange.fetch_ticker(symbol)
            if not ticker:
                return None
            return QuoteData(
                symbol=symbol,
                price=ticker.get('last'),
                open=ticker.get('open'),
                high=ticker.get('high'),
                low=ticker.get('low'),
                close=ticker.get('close'),
                volume=ticker.get('baseVolume'),
                amount=ticker.get('quoteVolume'),
                change_pct=ticker.get('percentage'),
                source=self.name,
            )
        except Exception as e:
            logger.debug(f"[ccxt] quote error for {symbol}: {e}")
            return None


# ── 外汇数据源 (yfinance) ──────────────────────────────────────

class YFinanceForexQuoteSource:
    """外汇行情源 - 基于 yfinance"""
    name = "yfinance_forex"
    priority = 30

    def is_available(self) -> bool:
        try:
            import yfinance
            return True
        except ImportError:
            return False

    def fetch_quote(self, symbol: str) -> Optional[QuoteData]:
        try:
            import yfinance as yf
            # yfinance 外汇格式: USD/CNY -> USDCNY=X
            ticker_symbol = symbol.replace('/', '') + '=X'
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info
            if not info or 'regularMarketPrice' not in info:
                # Fallback: 从历史数据获取最新价
                hist = ticker.history(period='1d')
                if hist.empty:
                    return None
                return QuoteData(
                    symbol=symbol,
                    price=float(hist['Close'].iloc[-1]),
                    open=float(hist['Open'].iloc[-1]),
                    high=float(hist['High'].iloc[-1]),
                    low=float(hist['Low'].iloc[-1]),
                    close=float(hist['Close'].iloc[-1]),
                    volume=float(hist['Volume'].iloc[-1]) if 'Volume' in hist.columns else None,
                    source=self.name,
                )
            return QuoteData(
                symbol=symbol,
                price=info.get('regularMarketPrice'),
                open=info.get('regularMarketOpen'),
                high=info.get('regularMarketDayHigh'),
                low=info.get('regularMarketDayLow'),
                close=info.get('regularMarketPrice'),
                volume=info.get('regularMarketVolume'),
                change_pct=info.get('regularMarketChangePercent'),
                source=self.name,
            )
        except Exception as e:
            logger.debug(f"[yfinance_forex] quote error for {symbol}: {e}")
            return None
