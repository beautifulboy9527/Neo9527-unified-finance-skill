#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Collect real stock data when providers are available, without fabricated fallbacks."""

from __future__ import annotations

from datetime import datetime
import importlib
from importlib.util import find_spec
from pathlib import Path
from typing import Any, Dict, Iterable, Optional


def _num(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        text = str(value).replace(",", "").replace("%", "").strip()
        if text in {"", "--", "None", "nan", "NaN", "暂无数据"}:
            return None
        return float(text)
    except (TypeError, ValueError):
        return None


def _first(row: Any, names: Iterable[str]) -> Any:
    for name in names:
        try:
            value = row.get(name)
        except AttributeError:
            value = None
        if value not in [None, "", "--"]:
            return value
    return None


def _pandas_module():
    if find_spec("pandas") is None:
        return None
    return importlib.import_module("pandas")


def _enhanced_technical_module():
    try:
        return importlib.import_module("skills.shared.technical_indicators")
    except Exception:
        return None


class StockDataCollector:
    """Best-effort data collector with explicit missing-source disclosure."""

    def collect(self, symbol: str) -> Dict:
        market = self._detect_market(symbol)
        result = self._empty_result(symbol, market)

        if market == "cn":
            self._collect_cn(symbol, result)
        else:
            self._collect_yfinance(symbol, result)

        result["success"] = bool(
            result["market_data"]
            or result["technical_analysis"]
            or result["financial_fields"]
            or result["valuation_fields"]
        )
        if not result["success"]:
            result["warnings"].append("未获得可验证行情、财务或估值字段，报告不会使用模拟数据补齐。")
        return result

    def collect_price_csv(self, path: str, symbol: str = "", timeframe: str = "日线") -> Dict:
        """Load a real OHLC CSV and derive technical analysis from it."""

        result = self._empty_result(symbol or Path(path).stem, "manual")
        result["sources"].append({"name": "本地K线CSV", "status": "已读取", "fields": []})

        pd = _pandas_module()
        if pd is None:
            result["warnings"].append("pandas 未安装，无法读取本地 K 线 CSV。")
            return result

        try:
            csv_path = Path(path)
            hist = pd.read_csv(csv_path)
        except Exception as exc:
            result["warnings"].append(f"本地 K 线 CSV 读取失败：{exc}")
            return result

        return self._collect_price_frame(result, hist, source_name="本地K线CSV", missing_message="本地 K 线 CSV 缺少日期、开盘、最高、最低、收盘等必要字段，未生成技术面图表。", timeframe=timeframe)

    def collect_price_rows(self, rows: list[Dict], symbol: str = "", timeframe: str = "日线") -> Dict:
        """Load real OHLC rows from an API payload and derive technical analysis."""

        result = self._empty_result(symbol or "payload", "manual")
        result["sources"].append({"name": "外部K线数组", "status": "已读取", "fields": []})

        pd = _pandas_module()
        if pd is None:
            result["warnings"].append("pandas 未安装，无法读取外部 K 线数组。")
            return result
        if not rows:
            result["warnings"].append("外部 K 线数组为空，未生成技术面图表。")
            return result

        try:
            hist = pd.DataFrame(rows)
        except Exception as exc:
            result["warnings"].append(f"外部 K 线数组读取失败：{exc}")
            return result

        return self._collect_price_frame(result, hist, source_name="外部K线数组", missing_message="外部 K 线数组缺少日期、开盘、最高、最低、收盘等必要字段，未生成技术面图表。", timeframe=timeframe)

    def _collect_price_frame(self, result: Dict, hist: Any, *, source_name: str, missing_message: str, timeframe: str) -> Dict:
        normalized = self._normalize_history_columns(hist)
        technical = self._technical_from_history(normalized, timeframe=timeframe)
        if not technical or not technical.get("candles"):
            result["warnings"].append(missing_message)
            return result

        technical["multi_timeframe"] = self._multi_timeframe_from_history(normalized)
        result["technical_analysis"] = technical
        result["market_data"]["price"] = technical.get("current_price")
        result["valuation_fields"]["current_price"] = technical.get("current_price")
        for source in result["sources"]:
            if source.get("name") == source_name:
                source["fields"] = ["K线", "支撑位", "压力位", "均线", "成交量", "RSI", "MACD", "布林带", "ATR"]
                break
        result["success"] = True
        return result

    def _empty_result(self, symbol: str, market: str) -> Dict:
        return {
            "success": False,
            "symbol": symbol,
            "market": market,
            "collected_at": datetime.now().isoformat(timespec="seconds"),
            "profile": {},
            "market_data": {},
            "technical_analysis": {},
            "financial_fields": {},
            "valuation_fields": {},
            "fundamental_analysis": {},
            "warnings": [],
            "sources": [],
        }

    def _detect_market(self, symbol: str) -> str:
        if symbol.isdigit() and len(symbol) == 6:
            return "cn"
        if symbol.endswith(".HK") or symbol.isdigit():
            return "hk"
        return "us"

    def _collect_cn(self, symbol: str, result: Dict) -> None:
        if find_spec("akshare") is None:
            result["warnings"].append("AkShare 未安装，无法自动采集 A 股行情、财务指标和估值字段。")
            result["sources"].append({"name": "AkShare", "status": "不可用", "fields": []})
        else:
            self._collect_cn_akshare(symbol, result)

        if not result.get("technical_analysis"):
            self._collect_cn_efinance(symbol, result)

        if not result.get("technical_analysis"):
            self._collect_cn_baostock(symbol, result)

    def _collect_cn_akshare(self, symbol: str, result: Dict) -> None:
        ak = importlib.import_module("akshare")
        fields = []

        try:
            spot = ak.stock_zh_a_spot_em()
            row_set = spot[spot["代码"].astype(str) == str(symbol)]
            if not row_set.empty:
                row = row_set.iloc[0]
                name = str(_first(row, ["名称"]) or "")
                price = _num(_first(row, ["最新价", "收盘"]))
                result["profile"].update({"name": name})
                result["market_data"].update({
                    "name": name,
                    "price": price,
                    "change_pct": _num(_first(row, ["涨跌幅"])),
                    "volume": _num(_first(row, ["成交量"])),
                    "high": _num(_first(row, ["最高"])),
                    "low": _num(_first(row, ["最低"])),
                    "open": _num(_first(row, ["今开", "开盘"])),
                    "prev_close": _num(_first(row, ["昨收"])),
                })
                result["valuation_fields"].update({
                    "current_price": price,
                    "pe": _num(_first(row, ["市盈率-动态", "市盈率", "市盈率动态"])),
                    "pb": _num(_first(row, ["市净率"])),
                })
                fields.extend(["行情快照", "当前价格", "市盈率", "市净率"])
            else:
                result["warnings"].append("AkShare 实时行情未找到该股票代码。")
        except Exception as exc:
            result["warnings"].append(f"AkShare 实时行情采集失败：{exc}")

        try:
            hist = ak.stock_zh_a_hist(symbol=symbol, period="daily", adjust="qfq")
            self._merge_cn_history(result, hist, source_name="AkShare", fields=fields)
        except Exception as exc:
            result["warnings"].append(f"AkShare 历史行情采集失败：{exc}")

        try:
            fin = ak.stock_financial_analysis_indicator(symbol=symbol)
            if fin is not None and not fin.empty:
                row = fin.iloc[0]
                financial_fields = {
                    "gross_margin": _num(_first(row, ["销售毛利率", "毛利率"])),
                    "net_margin": _num(_first(row, ["销售净利率", "净利率"])),
                    "roe": _num(_first(row, ["净资产收益率", "ROE"])),
                    "debt_ratio": _num(_first(row, ["资产负债率"])),
                }
                result["financial_fields"].update({k: v for k, v in financial_fields.items() if v is not None})
                fields.extend(["毛利率", "净利率", "净资产收益率", "资产负债率"])
            else:
                result["warnings"].append("AkShare 财务指标为空。")
        except Exception as exc:
            result["warnings"].append(f"AkShare 财务指标采集失败：{exc}")

        self._collect_cn_akshare_financial_extensions(ak, symbol, result, fields)

        result["sources"].append({"name": "AkShare", "status": "已调用", "fields": sorted(set(fields))})

    def _collect_cn_akshare_financial_extensions(self, ak: Any, symbol: str, result: Dict, fields: list[str]) -> None:
        """Best-effort A-share financial extensions; never fabricate missing fields."""

        extension_specs = [
            ("stock_financial_abstract", {"symbol": symbol}, "财务摘要"),
            ("stock_financial_abstract_ths", {"symbol": symbol}, "同花顺财务摘要"),
            ("stock_financial_report_sina", {"stock": symbol, "symbol": "利润表"}, "利润表"),
            ("stock_financial_report_sina", {"stock": symbol, "symbol": "现金流量表"}, "现金流量表"),
        ]
        extracted = set()
        for func_name, kwargs, label in extension_specs:
            func = getattr(ak, func_name, None)
            if not callable(func):
                continue
            try:
                frame = func(**kwargs)
                if frame is None or getattr(frame, "empty", True):
                    result["warnings"].append(f"AkShare {label}为空。")
                    continue
                row = frame.iloc[0]
                extracted.update(self._merge_financial_extension_row(row, result))
            except TypeError:
                continue
            except Exception as exc:
                result["warnings"].append(f"AkShare {label}采集失败：{exc}")
        if extracted:
            fields.extend(sorted(extracted))

    def _merge_financial_extension_row(self, row: Any, result: Dict) -> set[str]:
        field_specs = {
            "revenue_growth": (["营业收入同比增长率", "营业总收入同比增长率", "营收同比增长率", "营业收入增长率"], "收入增速"),
            "profit_growth": (["净利润同比增长率", "归母净利润同比增长率", "净利润增长率"], "利润增速"),
            "operating_cash_flow": (["经营活动产生的现金流量净额", "经营现金流量净额", "经营现金流净额"], "经营现金流"),
            "net_income": (["净利润", "归属于母公司所有者的净利润", "归母净利润"], "净利润"),
            "gross_margin": (["销售毛利率", "毛利率"], "毛利率"),
            "net_margin": (["销售净利率", "净利率"], "净利率"),
            "roe": (["净资产收益率", "ROE", "加权净资产收益率"], "净资产收益率"),
            "debt_ratio": (["资产负债率"], "资产负债率"),
        }
        extracted = set()
        for target_key, (aliases, label) in field_specs.items():
            if result["financial_fields"].get(target_key) is not None:
                continue
            value = _num(_first(row, aliases))
            if value is None:
                continue
            result["financial_fields"][target_key] = value
            extracted.add(label)
        return extracted

    def _collect_cn_efinance(self, symbol: str, result: Dict) -> None:
        if find_spec("efinance") is None:
            result["sources"].append({"name": "efinance", "status": "不可用", "fields": []})
            return

        fields = []
        try:
            ef = importlib.import_module("efinance")
            hist = ef.stock.get_quote_history(symbol)
            if hist is None or getattr(hist, "empty", True):
                result["warnings"].append("efinance 历史行情返回为空。")
            else:
                name = _first(hist.iloc[-1], ["股票名称", "名称"])
                if name:
                    result["profile"].setdefault("name", str(name))
                    result["market_data"].setdefault("name", str(name))
                self._merge_cn_history(result, hist, source_name="efinance", fields=fields)
        except Exception as exc:
            result["warnings"].append(f"efinance 历史行情采集失败：{exc}")

        result["sources"].append({"name": "efinance", "status": "已调用", "fields": sorted(set(fields))})

    def _collect_cn_baostock(self, symbol: str, result: Dict) -> None:
        if find_spec("baostock") is None:
            result["sources"].append({"name": "Baostock", "status": "不可用", "fields": []})
            return

        pd = _pandas_module()
        if pd is None:
            result["warnings"].append("pandas 未安装，无法整理 Baostock 历史行情。")
            return

        bs = importlib.import_module("baostock")
        fields = []
        logged_in = False
        try:
            code = f"sh.{symbol}" if str(symbol).startswith("6") else f"sz.{symbol}"
            login = bs.login()
            logged_in = True
            if getattr(login, "error_code", "0") != "0":
                result["warnings"].append(f"Baostock 登录失败：{getattr(login, 'error_msg', '')}")
            else:
                # 获取公司基本信息（名称、上市日期等）
                try:
                    stock_basic = bs.query_stock_basic(code=code)
                    if getattr(stock_basic, "error_code", "0") == "0" and stock_basic.next():
                        row_data = stock_basic.get_row_data()
                        if len(row_data) >= 2:
                            stock_name = row_data[1]  # 第二个字段是股票名称
                            if stock_name and stock_name not in ("", "None"):
                                result["profile"].update({"name": stock_name})
                                result["market_data"].update({"name": stock_name})
                                fields.append("公司名称")
                except Exception as exc:
                    result["warnings"].append(f"Baostock 公司基本信息采集失败：{exc}")

                # 获取成长能力数据（收入增长率、利润增长率等）
                try:
                    from datetime import datetime
                    current_year = datetime.now().year
                    current_quarter = (datetime.now().month - 1) // 3 + 1
                    
                    # 尝试最近几个季度的数据
                    for year in [current_year, current_year - 1]:
                        for quarter in [current_quarter, current_quarter - 1, 4, 3, 2, 1]:
                            if quarter < 1:
                                continue
                            growth_data = bs.query_growth_data(code=code, year=year, quarter=quarter)
                            if getattr(growth_data, "error_code", "0") == "0" and growth_data.next():
                                row_data = growth_data.get_row_data()
                                if len(row_data) >= 8:
                                    # 字段顺序: code, pubDate, statDate, YOYEquity, YOYAsset, YOYNI, YOYEPSBasic, YOYPNI
                                    profit_growth = _num(row_data[5])  # YOYNI: 净利润增长率
                                    revenue_growth = _num(row_data[7])  # YOYPNI: 营业收入增长率
                                    
                                    if profit_growth is not None:
                                        result["financial_fields"]["profit_growth"] = profit_growth
                                        fields.append("利润增长率")
                                    if revenue_growth is not None:
                                        result["financial_fields"]["revenue_growth"] = revenue_growth
                                        fields.append("收入增长率")
                                    break
                        if "revenue_growth" in result.get("financial_fields", {}):
                            break
                except Exception as exc:
                    result["warnings"].append(f"Baostock 成长能力数据采集失败：{exc}")

                rs = bs.query_history_k_data_plus(
                    code,
                    "date,open,high,low,close,volume",
                    start_date="2025-01-01",
                    frequency="d",
                    adjustflag="2",
                )
                rows = []
                while getattr(rs, "error_code", "0") == "0" and rs.next():
                    rows.append(rs.get_row_data())
                if not rows:
                    result["warnings"].append("Baostock 历史行情返回为空。")
                else:
                    hist = pd.DataFrame(rows, columns=["日期", "开盘", "最高", "最低", "收盘", "成交量"])
                    self._merge_cn_history(result, hist, source_name="Baostock", fields=fields)
        except Exception as exc:
            result["warnings"].append(f"Baostock 历史行情采集失败：{exc}")
        finally:
            if logged_in:
                try:
                    bs.logout()
                except Exception:
                    pass
        result["sources"].append({"name": "Baostock", "status": "已调用", "fields": sorted(set(fields))})

    def _merge_cn_history(self, result: Dict, hist: Any, *, source_name: str, fields: list[str]) -> None:
        technical = self._technical_from_history(hist, timeframe="日线")
        if not technical:
            result["warnings"].append(f"{source_name} 历史行情样本不足或字段不完整，未生成技术面图表。")
            return

        technical["multi_timeframe"] = self._multi_timeframe_from_history(hist)
        result["technical_analysis"].update(technical)
        if technical.get("current_price") is not None:
            if result["market_data"].get("price") is None:
                result["market_data"]["price"] = technical.get("current_price")
            if result["valuation_fields"].get("current_price") is None:
                result["valuation_fields"]["current_price"] = technical.get("current_price")
        fields.extend(["日线K线", "支撑位", "压力位", "均线", "成交量", "RSI", "MACD", "布林带", "ATR"])

    def _collect_yfinance(self, symbol: str, result: Dict) -> None:
        if find_spec("yfinance") is None:
            result["warnings"].append("yfinance 未安装，无法自动采集海外股票行情和基础财务字段。")
            result["sources"].append({"name": "yfinance", "status": "不可用", "fields": []})
            return

        yf = importlib.import_module("yfinance")
        fields = []
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info or {}
            hist = ticker.history(period="3mo")
            name = info.get("longName") or info.get("shortName") or symbol
            result["profile"].update({
                "name": name,
                "sector": info.get("sector"),
                "industry": info.get("industry"),
            })
            result["fundamental_analysis"].update({
                "industry": info.get("industry"),
                "business_summary": info.get("longBusinessSummary"),
            })
            if hist is not None and not hist.empty:
                latest = hist.iloc[-1]
                price = _num(latest.get("Close"))
                result["market_data"].update({
                    "name": name,
                    "price": price,
                    "high": _num(latest.get("High")),
                    "low": _num(latest.get("Low")),
                    "open": _num(latest.get("Open")),
                    "volume": _num(latest.get("Volume")),
                })
                technical = self._technical_from_history(hist, timeframe="日线")
                if technical:
                    technical["multi_timeframe"] = self._multi_timeframe_from_history(hist)
                    result["technical_analysis"].update(technical)
                fields.extend(["行情快照", "日线技术指标"])
            result["valuation_fields"].update({
                "current_price": result["market_data"].get("price"),
                "eps": _num(info.get("trailingEps")),
                "bps": _num(info.get("bookValue")),
                "pe": _num(info.get("trailingPE") or info.get("forwardPE")),
                "pb": _num(info.get("priceToBook")),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
            })
            result["valuation_fields"] = {k: v for k, v in result["valuation_fields"].items() if v not in [None, ""]}
            fields.extend(["每股收益", "每股净资产", "市盈率", "市净率"])
        except Exception as exc:
            result["warnings"].append(f"yfinance 采集失败：{exc}")

        result["sources"].append({"name": "yfinance", "status": "已调用", "fields": sorted(set(fields))})

    def _normalize_history_columns(self, hist: Any) -> Any:
        rename = {}
        aliases = {
            "日期": {"日期", "date", "Date", "交易日期", "时间"},
            "开盘": {"开盘", "open", "Open", "开盘价"},
            "最高": {"最高", "high", "High", "最高价"},
            "最低": {"最低", "low", "Low", "最低价"},
            "收盘": {"收盘", "close", "Close", "收盘价"},
            "成交量": {"成交量", "volume", "Volume", "vol", "Vol"},
        }
        for target, names in aliases.items():
            for column in hist.columns:
                if str(column).strip() in names:
                    rename[column] = target
                    break
        return hist.rename(columns=rename)

    def _multi_timeframe_from_history(self, hist: Any) -> Dict:
        pd = _pandas_module()
        if pd is None or hist is None or getattr(hist, "empty", True):
            return {}

        normalized = self._normalize_history_columns(hist).copy()
        if "日期" not in normalized.columns:
            try:
                normalized = normalized.reset_index().rename(columns={"index": "日期", "Date": "日期"})
            except Exception:
                return {}
        required = ["日期", "开盘", "最高", "最低", "收盘"]
        if any(column not in normalized.columns for column in required):
            return {}

        clean = normalized.copy()
        clean["日期"] = pd.to_datetime(clean["日期"], errors="coerce")
        for column in ["开盘", "最高", "最低", "收盘", "成交量"]:
            if column in clean.columns:
                clean[column] = pd.to_numeric(clean[column], errors="coerce")
        clean = clean.dropna(subset=required).sort_values("日期")
        if clean.empty:
            return {}

        frames = {}
        daily = self._technical_from_history(clean, timeframe="日线")
        if daily:
            frames["日线"] = self._timeframe_summary(daily)

        indexed = clean.set_index("日期")
        agg = {"开盘": "first", "最高": "max", "最低": "min", "收盘": "last"}
        if "成交量" in indexed.columns:
            agg["成交量"] = "sum"
        for label, rule in (("周线", "W-FRI"), ("月线", "ME")):
            try:
                sampled = indexed.resample(rule).agg(agg).dropna(subset=["开盘", "最高", "最低", "收盘"]).reset_index()
            except ValueError:
                sampled = indexed.resample("M" if label == "月线" else "W-FRI").agg(agg).dropna(subset=["开盘", "最高", "最低", "收盘"]).reset_index()
            technical = self._technical_from_history(sampled, timeframe=label)
            if technical:
                frames[label] = self._timeframe_summary(technical)
        return frames

    def _timeframe_summary(self, technical: Dict) -> Dict:
        return {
            "timeframe": technical.get("timeframe"),
            "lookback": technical.get("lookback"),
            "trend": technical.get("trend"),
            "change": technical.get("change_20d"),
            "support_level": technical.get("support_level"),
            "resistance_level": technical.get("resistance_level"),
            "rsi14": technical.get("rsi14"),
            "macd_status": (technical.get("macd") or {}).get("status"),
            "bollinger_position": (technical.get("bollinger") or {}).get("position"),
            "volume_status": technical.get("volume_status"),
        }

    def _technical_from_history(self, hist: Any, timeframe: str = "日线") -> Dict:
        if hist is None or getattr(hist, "empty", True):
            return {}

        hist = self._normalize_history_columns(hist)
        date_col = "日期" if "日期" in hist.columns else None
        open_col = "开盘" if "开盘" in hist.columns else "Open"
        close_col = "收盘" if "收盘" in hist.columns else "Close"
        high_col = "最高" if "最高" in hist.columns else "High"
        low_col = "最低" if "最低" in hist.columns else "Low"
        volume_col = "成交量" if "成交量" in hist.columns else "Volume"
        required = [open_col, close_col, high_col, low_col]
        if any(col not in hist.columns for col in required):
            return {}

        pd = _pandas_module()
        if pd is None:
            return {}

        clean = hist.copy()
        for col in required + ([volume_col] if volume_col in clean.columns else []):
            clean[col] = pd.to_numeric(clean[col], errors="coerce")
        clean = clean.dropna(subset=required)
        if date_col and date_col in clean.columns:
            clean = clean.sort_values(date_col)
        if len(clean) < 20:
            return {
                "timeframe": timeframe,
                "lookback": f"最近{len(clean)}个交易日",
                "trend": "样本不足，趋势待验证",
                "candles": self._candles(clean, date_col, open_col, high_col, low_col, close_col, volume_col if volume_col in clean.columns else None),
            }

        close = clean[close_col].astype(float)
        high = clean[high_col].astype(float)
        low = clean[low_col].astype(float)
        open_ = clean[open_col].astype(float)
        ma5 = float(close.rolling(5).mean().iloc[-1])
        ma20 = float(close.rolling(20).mean().iloc[-1])
        current = float(close.iloc[-1])
        if current > ma5 > ma20:
            trend = f"{timeframe}偏强"
        elif current < ma5 < ma20:
            trend = f"{timeframe}偏弱"
        else:
            trend = f"{timeframe}震荡"

        start = float(close.iloc[-20])
        change_20d = current / start - 1 if start else None
        volume = _num(clean[volume_col].iloc[-1]) if volume_col in clean.columns else None
        volume_ma20 = None
        volume_status = "成交量数据不足"
        if volume_col in clean.columns and len(clean[volume_col].dropna()) >= 20:
            volume_ma20 = float(clean[volume_col].astype(float).rolling(20).mean().iloc[-1])
            if volume is not None and volume_ma20:
                ratio = volume / volume_ma20
                if ratio >= 1.5:
                    volume_status = "明显放量"
                elif ratio >= 1.1:
                    volume_status = "温和放量"
                elif ratio <= 0.7:
                    volume_status = "明显缩量"
                else:
                    volume_status = "量能平稳"
        recent_high = float(high.tail(20).max())
        recent_low = float(low.tail(20).min())
        support = self._support_level(low.tail(20), close.tail(20))
        resistance = self._resistance_level(high.tail(20), close.tail(20))
        support_tests = self._level_tests(low.tail(20), support, tolerance=0.012)
        resistance_tests = self._level_tests(high.tail(20), resistance, tolerance=0.012)
        support_distance = (current / support - 1) if support else None
        resistance_distance = (resistance / current - 1) if resistance else None
        candles = self._candles(clean.tail(20), date_col, open_col, high_col, low_col, close_col, volume_col if volume_col in clean.columns else None)
        self._attach_ma_series(candles, close.rolling(5).mean().tail(20).tolist(), close.rolling(20).mean().tail(20).tolist())
        rsi14 = self._rsi(close, 14)
        macd = self._macd(close)
        bollinger = self._bollinger(close)
        atr14 = self._atr(high, low, close, 14)
        volume_price_signal = self._volume_price_signal(open_, close, volume, volume_ma20)
        dominant_pattern = self._dominant_pattern(clean.tail(40), date_col, high_col, low_col, close_col, timeframe)
        enhanced = self._enhanced_technical(clean, timeframe)
        confluence = enhanced.get("confluence_support_resistance", {}) if isinstance(enhanced, dict) else {}
        nearest_support = confluence.get("nearest_support") if isinstance(confluence, dict) else None
        nearest_resistance = confluence.get("nearest_resistance") if isinstance(confluence, dict) else None
        if nearest_support and nearest_support.get("price") is not None:
            support = float(nearest_support["price"])
            support_tests = max(support_tests, int(nearest_support.get("touchpoints", 0) or 0))
            support_distance = (current / support - 1) if support else None
        if nearest_resistance and nearest_resistance.get("price") is not None:
            resistance = float(nearest_resistance["price"])
            resistance_tests = max(resistance_tests, int(nearest_resistance.get("touchpoints", 0) or 0))
            resistance_distance = (resistance / current - 1) if resistance else None
        return {
            "timeframe": timeframe,
            "lookback": "最近20个交易日",
            "trend": trend,
            "current_price": current,
            "ma5": ma5,
            "ma20": ma20,
            "change_20d": change_20d,
            "latest_volume": volume,
            "volume_ma20": volume_ma20,
            "volume_status": volume_status,
            "support_level": support,
            "resistance_level": resistance,
            "support_tests": support_tests,
            "resistance_tests": resistance_tests,
            "support_strength": self._level_strength(support_tests),
            "resistance_strength": self._level_strength(resistance_tests),
            "support_source": nearest_support.get("sources", []) if nearest_support else ["pivot"],
            "resistance_source": nearest_resistance.get("sources", []) if nearest_resistance else ["pivot"],
            "support_confidence": nearest_support.get("confidence") if nearest_support else self._level_strength(support_tests),
            "resistance_confidence": nearest_resistance.get("confidence") if nearest_resistance else self._level_strength(resistance_tests),
            "support_distance_pct": support_distance,
            "resistance_distance_pct": resistance_distance,
            "recent_high": recent_high,
            "recent_low": recent_low,
            "rsi14": rsi14,
            "macd": macd,
            "bollinger": bollinger,
            "atr14": atr14,
            "atr14_pct": atr14 / current if atr14 is not None and current else None,
            "volume_price_signal": volume_price_signal,
            "dominant_pattern": dominant_pattern,
            "enhanced": enhanced,
            "candles": candles,
        }

    def _enhanced_technical(self, clean: Any, timeframe: str) -> Dict:
        """Attach optional enhanced indicators only when computed from real K-line data."""
        if timeframe != "日线":
            return {}
        module = _enhanced_technical_module()
        if module is None:
            return {}
        try:
            result = module.enhanced_technical_analysis(clean, lookback=min(len(clean), 100))
            indicators = result.get("indicators", {}) if isinstance(result, dict) else {}
            if not indicators:
                return {}
            return {
                "vwap": indicators.get("vwap", {}),
                "fibonacci_retracements": indicators.get("fibonacci_retracements", {}),
                "volume_profile": indicators.get("volume_profile", {}),
                "liquidity_pools": indicators.get("liquidity_pools", {}),
                "dynamic_levels": indicators.get("dynamic_levels", {}),
                "confluence_support_resistance": indicators.get("confluence_support_resistance", {}),
                "candlestick_patterns": indicators.get("candlestick_patterns", {}),
                "trendlines": indicators.get("trendlines", {}),
                "adx": indicators.get("adx", {}),
                "summary": result.get("summary", {}),
            }
        except Exception:
            return {}

    def _rsi(self, close: Any, period: int = 14) -> Optional[float]:
        if len(close) <= period:
            return None
        delta = close.diff()
        gains = delta.clip(lower=0)
        losses = -delta.clip(upper=0)
        avg_gain = gains.rolling(period).mean().iloc[-1]
        avg_loss = losses.rolling(period).mean().iloc[-1]
        if avg_loss == 0:
            return 100.0
        return round(float(100 - (100 / (1 + avg_gain / avg_loss))), 2)

    def _macd(self, close: Any) -> Dict:
        if len(close) < 26:
            return {}
        exp12 = close.ewm(span=12, adjust=False).mean()
        exp26 = close.ewm(span=26, adjust=False).mean()
        dif = exp12 - exp26
        dea = dif.ewm(span=9, adjust=False).mean()
        hist = dif - dea
        latest_hist = float(hist.iloc[-1])
        prev_hist = float(hist.iloc[-2])
        if latest_hist > 0 and prev_hist <= 0:
            status = "金叉"
        elif latest_hist < 0 and prev_hist >= 0:
            status = "死叉"
        elif latest_hist > 0:
            status = "多头区间"
        elif latest_hist < 0:
            status = "空头区间"
        else:
            status = "中性"
        return {
            "dif": round(float(dif.iloc[-1]), 4),
            "dea": round(float(dea.iloc[-1]), 4),
            "hist": round(latest_hist, 4),
            "status": status,
        }

    def _bollinger(self, close: Any, period: int = 20) -> Dict:
        if len(close) < period:
            return {}
        mid = close.rolling(period).mean()
        std = close.rolling(period).std()
        upper = mid + 2 * std
        lower = mid - 2 * std
        current = float(close.iloc[-1])
        upper_value = float(upper.iloc[-1])
        mid_value = float(mid.iloc[-1])
        lower_value = float(lower.iloc[-1])
        if current > upper_value:
            position = "突破上轨"
        elif current < lower_value:
            position = "跌破下轨"
        elif current >= mid_value:
            position = "中轨上方"
        else:
            position = "中轨下方"
        return {
            "upper": round(upper_value, 2),
            "mid": round(mid_value, 2),
            "lower": round(lower_value, 2),
            "position": position,
        }

    def _atr(self, high: Any, low: Any, close: Any, period: int = 14) -> Optional[float]:
        if len(close) <= period:
            return None
        prev_close = close.shift(1)
        true_range = (high - low).to_frame("hl")
        true_range["hc"] = (high - prev_close).abs()
        true_range["lc"] = (low - prev_close).abs()
        atr = true_range.max(axis=1).rolling(period).mean().iloc[-1]
        return round(float(atr), 2)

    def _support_level(self, lows: Any, closes: Any) -> Optional[float]:
        values = [float(item) for item in lows.dropna().tolist()]
        if not values:
            return None
        current = float(closes.iloc[-1])
        pivot_lows = self._pivot_lows(values)
        candidates = [value for value in pivot_lows if value < current]
        if not candidates and len(values) > 1:
            candidates = [value for value in values[:-1] if value < current]
        return round(max(candidates) if candidates else min(values), 2)

    def _resistance_level(self, highs: Any, closes: Any) -> Optional[float]:
        values = [float(item) for item in highs.dropna().tolist()]
        if not values:
            return None
        current = float(closes.iloc[-1])
        pivot_highs = self._pivot_highs(values)
        candidates = [value for value in pivot_highs if value > current]
        if not candidates:
            candidates = [value for value in values if value > current]
        return round(min(candidates) if candidates else max(values), 2)

    def _pivot_lows(self, values: list[float]) -> list[float]:
        pivots = []
        for index in range(1, len(values) - 1):
            if values[index] <= values[index - 1] and values[index] <= values[index + 1]:
                pivots.append(values[index])
        return pivots

    def _pivot_highs(self, values: list[float]) -> list[float]:
        pivots = []
        for index in range(1, len(values) - 1):
            if values[index] >= values[index - 1] and values[index] >= values[index + 1]:
                pivots.append(values[index])
        return pivots

    def _level_tests(self, values: Any, level: Optional[float], tolerance: float = 0.01) -> int:
        if level is None:
            return 0
        count = 0
        for value in values.dropna().tolist():
            numeric = float(value)
            if level and abs(numeric / level - 1) <= tolerance:
                count += 1
        return count

    def _level_strength(self, tests: int) -> str:
        if tests >= 3:
            return "强"
        if tests >= 2:
            return "中"
        if tests == 1:
            return "弱"
        return "待确认"

    def _volume_price_signal(self, open_: Any, close: Any, volume: Optional[float], volume_ma20: Optional[float]) -> str:
        if volume is None or not volume_ma20:
            return "量价关系暂无足够数据"
        price_change = float(close.iloc[-1]) / float(close.iloc[-2]) - 1 if len(close) >= 2 and float(close.iloc[-2]) else 0
        up_day = float(close.iloc[-1]) >= float(open_.iloc[-1])
        volume_ratio = volume / volume_ma20
        if price_change > 0.02 and volume_ratio >= 1.2:
            return "放量上涨"
        if price_change < -0.02 and volume_ratio >= 1.2:
            return "放量下跌"
        if up_day and volume_ratio <= 0.8:
            return "缩量反弹"
        if not up_day and volume_ratio <= 0.8:
            return "缩量回落"
        return "量价配合一般"

    def _dominant_pattern(self, rows: Any, date_col: Optional[str], high_col: str, low_col: str, close_col: str, timeframe: str) -> Dict:
        if len(rows) < 20:
            return {"timeframe": timeframe, "name": "样本不足", "description": "K线样本不足，暂不判断形态。", "confidence": "低"}
        highs = [float(item) for item in rows[high_col].dropna().tolist()]
        lows = [float(item) for item in rows[low_col].dropna().tolist()]
        closes = [float(item) for item in rows[close_col].dropna().tolist()]
        if len(highs) < 20 or len(lows) < 20 or len(closes) < 20:
            return {"timeframe": timeframe, "name": "样本不足", "description": "K线字段不完整，暂不判断形态。", "confidence": "低"}

        current = closes[-1]
        ma5 = sum(closes[-5:]) / 5
        ma20 = sum(closes[-20:]) / 20
        recent_high = max(highs[-20:])
        recent_low = min(lows[-20:])
        double_top = self._double_level_pattern(highs, closes, kind="top")
        double_bottom = self._double_level_pattern(lows, closes, kind="bottom")

        candidates = []
        if double_top:
            candidates.append(double_top)
        if double_bottom:
            candidates.append(double_bottom)
        if current > ma5 > ma20 and recent_high and current >= recent_high * 0.985:
            candidates.append({
                "name": "上升趋势延续",
                "score": 70,
                "description": f"{timeframe}收盘价位于五日、二十日均线上方，并接近最近20日高点，趋势仍偏强。",
                "confidence": "中",
            })
        elif current < ma5 < ma20 and recent_low and current <= recent_low * 1.015:
            candidates.append({
                "name": "下跌趋势延续",
                "score": 70,
                "description": f"{timeframe}收盘价位于五日、二十日均线下方，并接近最近20日低点，趋势仍偏弱。",
                "confidence": "中",
            })
        else:
            range_pct = (recent_high / recent_low - 1) if recent_low else 0
            if range_pct <= 0.12:
                candidates.append({
                    "name": "区间震荡",
                    "score": 45,
                    "description": f"{timeframe}价格在最近20个交易日高低点之间反复运行，尚未形成明确突破。",
                    "confidence": "中",
                })

        if not candidates:
            return {"timeframe": timeframe, "name": "形态不明确", "description": f"{timeframe}暂未识别出可靠主形态，优先观察均线和支撑压力。", "confidence": "低"}
        best = max(candidates, key=lambda item: item.get("score", 0))
        return {key: value for key, value in best.items() if key != "score"} | {"timeframe": timeframe}

    def _double_level_pattern(self, values: list[float], closes: list[float], kind: str) -> Optional[Dict]:
        pivots = []
        for index in range(2, len(values) - 2):
            window = values[index - 2:index + 3]
            value = values[index]
            if kind == "top" and value == max(window):
                pivots.append((index, value))
            if kind == "bottom" and value == min(window):
                pivots.append((index, value))
        if len(pivots) < 2:
            return None
        first, second = pivots[-2], pivots[-1]
        if first[1] == 0 or abs(second[1] / first[1] - 1) > 0.025:
            return None
        current = closes[-1]
        if kind == "top":
            neckline = min(closes[first[0]:second[0] + 1])
            confirmed = current < neckline
            return {
                "name": "双顶风险" if confirmed else "双顶雏形",
                "score": 85 if confirmed else 55,
                "description": "最近两个阶段高点接近，价格未能有效突破前高；若收盘跌破颈线，回撤风险会明显上升。",
                "confidence": "中" if confirmed else "低",
            }
        neckline = max(closes[first[0]:second[0] + 1])
        confirmed = current > neckline
        return {
            "name": "双底修复" if confirmed else "双底雏形",
            "score": 85 if confirmed else 55,
            "description": "最近两个阶段低点接近，价格尝试在相近区域获得承接；若收盘站上颈线，修复形态才更可靠。",
            "confidence": "中" if confirmed else "低",
        }

    def _candles(self, rows: Any, date_col: Optional[str], open_col: str, high_col: str, low_col: str, close_col: str, volume_col: Optional[str] = None) -> list[Dict]:
        candles = []
        for index, row in rows.iterrows():
            date_value = row.get(date_col) if date_col else index
            candles.append({
                "date": str(date_value)[:10],
                "open": _num(row.get(open_col)),
                "high": _num(row.get(high_col)),
                "low": _num(row.get(low_col)),
                "close": _num(row.get(close_col)),
                "volume": _num(row.get(volume_col)) if volume_col else None,
            })
        return [item for item in candles if all(item.get(key) is not None for key in ("open", "high", "low", "close"))]

    def _attach_ma_series(self, candles: list[Dict], ma5_values: list, ma20_values: list) -> None:
        for candle, ma5, ma20 in zip(candles, ma5_values, ma20_values):
            if ma5 == ma5:
                candle["ma5"] = round(float(ma5), 2)
            if ma20 == ma20:
                candle["ma20"] = round(float(ma20), 2)


def collect_stock_data(symbol: str) -> Dict:
    return StockDataCollector().collect(symbol)


def collect_price_csv(path: str, symbol: str = "", timeframe: str = "日线") -> Dict:
    return StockDataCollector().collect_price_csv(path, symbol=symbol, timeframe=timeframe)


def collect_price_rows(rows: list[Dict], symbol: str = "", timeframe: str = "日线") -> Dict:
    return StockDataCollector().collect_price_rows(rows, symbol=symbol, timeframe=timeframe)


__all__ = ["StockDataCollector", "collect_stock_data", "collect_price_csv", "collect_price_rows"]
