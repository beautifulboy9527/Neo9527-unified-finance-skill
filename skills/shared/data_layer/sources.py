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
            return QuoteData(
                symbol=symbol,
                name=str(r.get('名称', '')),
                price=float(r.get('最新价', 0) or 0),
                open=float(r.get('今开', 0) or 0),
                high=float(r.get('最高', 0) or 0),
                low=float(r.get('最低', 0) or 0),
                close=float(r.get('收盘价', 0) or 0),
                volume=float(r.get('成交量', 0) or 0),
                amount=float(r.get('成交额', 0) or 0),
                change_pct=float(r.get('涨跌幅', 0) or 0),
                turnover_rate=float(r.get('换手率', 0) or 0),
                market_cap=float(r.get('总市值', 0) or 0),
                pe=float(r.get('市盈率-动态', 0) or 0),
                pb=float(r.get('市净率', 0) or 0),
                source=self.name,
            )
        except Exception as e:
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
                close=float(fields[2] or 0),
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
            lg = bs.login()
            if lg.error_code != '0':
                return None
            try:
                prefix = "sh" if symbol.startswith("6") else "sz"
                # 增长数据
                rs = bs.query_growth_data(code=f"{prefix}.{symbol}", year=2024, quarter=4)
                rows = []
                while rs.next():
                    rows.append(rs.get_row_data())
                if not rows:
                    return None
                r = rows[0]
                return FinancialData(
                    symbol=symbol,
                    revenue_yoy=float(r.get('YOYEquity', 0) or 0),
                    profit_yoy=float(r.get('YOYAsset', 0) or 0),
                    source=self.name,
                )
            finally:
                bs.logout()
        except Exception as e:
            logger.debug(f"[baostock] financial error: {e}")
            return None
