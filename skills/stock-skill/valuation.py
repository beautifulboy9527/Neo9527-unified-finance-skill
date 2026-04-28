#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
估值计算器 v2.0

目标:
- 不把默认假设伪装成事实
- 估值结果附带证据账本、模型假设、敏感性分析和置信度
- 缺少关键数据时返回不可用，而不是使用硬编码股本等危险占位
"""

import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

from skills.shared.evidence import EvidenceLedger


class ValuationCalculator:
    """估值计算器"""

    SECTOR_BENCHMARKS = {
        "Technology": {"pe": 25, "pb": 6},
        "Communication Services": {"pe": 20, "pb": 3},
        "Consumer Cyclical": {"pe": 18, "pb": 3},
        "Consumer Defensive": {"pe": 20, "pb": 4},
        "Healthcare": {"pe": 22, "pb": 4},
        "Financial Services": {"pe": 12, "pb": 1.5},
        "Industrials": {"pe": 18, "pb": 3},
        "Energy": {"pe": 12, "pb": 1.8},
        "Utilities": {"pe": 15, "pb": 2},
        "Real Estate": {"pe": 14, "pb": 1.5},
        "Basic Materials": {"pe": 14, "pb": 2},
        "default": {"pe": 18, "pb": 2.5},
    }

    def __init__(self):
        self.name = "ValuationCalculator"
        self.version = "2.0.0"

    def calculate(self, symbol: str, methods: str = 'all', **params) -> Dict:
        """
        执行估值计算。

        Args:
            symbol: 股票代码
            methods: all/dcf/ddm/relative
            **params: 可覆盖模型假设，例如 discount_rate、terminal_growth、peer_pe、peer_pb
        """
        print(f"开始估值计算: {symbol}...")

        default_params = {
            'discount_rate': 0.10,
            'terminal_growth': 0.025,
            'forecast_years': 5,
            'margin_of_safety': 0.30,
            'required_return': 0.10,
            'dividend_growth': 0.03,
            'fcf_growth': None,
            'peer_pe': None,
            'peer_pb': None,
        }
        user_params = set(params.keys())
        calc_params = {**default_params, **params}

        market = self._detect_market(symbol)
        financial_data = self._get_financial_data(symbol, market)

        if not financial_data:
            return {
                'success': False,
                'error': '无法获取财务数据',
                'symbol': symbol,
                'market': market,
                'timestamp': datetime.now().isoformat()
            }

        ledger = financial_data.pop('_ledger', EvidenceLedger())
        assumptions = self._build_model_assumptions(calc_params, user_params, financial_data, ledger)

        valuations = {}
        warnings = list(financial_data.get('warnings', []))

        if methods in ['all', 'relative']:
            valuations['relative'] = self._relative_valuation(financial_data, calc_params, ledger)

        if methods in ['all', 'dcf']:
            valuations['dcf'] = self._dcf_valuation(financial_data, calc_params, ledger)

        if methods in ['all', 'ddm']:
            valuations['ddm'] = self._ddm_valuation(financial_data, calc_params, ledger)

        for method_result in valuations.values():
            warnings.extend(method_result.get('warnings', []))
            if method_result.get('error'):
                warnings.append(method_result['error'])

        combined = self._calculate_fair_value(valuations, financial_data)
        fair_value = combined['fair_value']
        current_price = financial_data.get('price', 0)

        print("  估值计算完成")

        return {
            'success': True,
            'symbol': symbol,
            'market': market,
            'current_price': current_price,
            'valuations': valuations,
            'fair_value': fair_value,
            'fair_value_basis': combined['basis'],
            'valuation_confidence': combined['confidence'],
            'methods_used': combined['methods_used'],
            'fallback_used': combined['fallback_used'],
            'margin_of_safety': calc_params['margin_of_safety'],
            'safe_price': fair_value * (1 - calc_params['margin_of_safety']) if fair_value else 0,
            'assumptions': assumptions,
            'warnings': self._dedupe(warnings + combined['warnings']),
            'evidence': ledger.to_list(),
            'evidence_summary': ledger.summary(),
            'data_quality_score': ledger.quality_score(),
            'timestamp': datetime.now().isoformat()
        }

    def _detect_market(self, symbol: str) -> str:
        if symbol.isdigit() and len(symbol) == 6:
            return 'cn'
        if symbol.endswith('.HK'):
            return 'hk'
        return 'us'

    def _get_financial_data(self, symbol: str, market: str) -> Optional[Dict]:
        ledger = EvidenceLedger()
        data = {
            '_ledger': ledger,
            'warnings': [],
        }

        try:
            if market == 'cn':
                return self._get_cn_financial_data(symbol, data, ledger)
            return self._get_yfinance_financial_data(symbol, data, ledger)
        except Exception as e:
            print(f"  数据获取失败: {e}")
            return None

    def _get_cn_financial_data(self, symbol: str, data: Dict, ledger: EvidenceLedger) -> Optional[Dict]:
        if not AKSHARE_AVAILABLE:
            data['warnings'].append('AkShare 未安装，A股估值数据不可用')
            return data

        try:
            df_quote = ak.stock_zh_a_spot_em()
            stock_quote = df_quote[df_quote['代码'] == symbol]
            if not stock_quote.empty:
                quote = stock_quote.iloc[0]
                self._record(data, ledger, 'price', quote.get('最新价'), 'AkShare/Eastmoney', '最新价', unit='CNY')
                self._record(data, ledger, 'name', quote.get('名称'), 'AkShare/Eastmoney', '名称')
        except Exception as e:
            data['warnings'].append(f'A股行情数据获取失败: {e}')

        try:
            import pandas as pd

            df_fin = ak.stock_financial_analysis_indicator(symbol=symbol)
            if df_fin is not None and not df_fin.empty:
                latest = df_fin.iloc[0]

                def get_value(keywords, default=0):
                    for col in df_fin.columns:
                        if any(kw in str(col) for kw in keywords):
                            value = latest[col]
                            return float(value) if value not in [None, ''] and not pd.isna(value) else default
                    return default

                self._record(data, ledger, 'eps', get_value(['每股收益', 'EPS']), 'AkShare', '每股收益')
                self._record(data, ledger, 'bps', get_value(['每股净资产', 'BPS']), 'AkShare', '每股净资产')
                self._record(data, ledger, 'pe', get_value(['市盈率', 'PE']), 'AkShare', '市盈率')
                self._record(data, ledger, 'pb', get_value(['市净率', 'PB']), 'AkShare', '市净率')
                dividend = get_value(['每股股利', '分红']) * 10
                self._record(data, ledger, 'dividend', dividend, 'AkShare', '每股股利', unit='CNY/share')
                self._record(data, ledger, 'dividend_yield', get_value(['股息率']) / 100, 'AkShare', '股息率')
                self._record(
                    data,
                    ledger,
                    'free_cash_flow',
                    get_value(['自由现金流', 'FCF']),
                    'AkShare',
                    '自由现金流',
                    note='A股接口可能缺少标准FCF口径，需核对现金流量表',
                )
        except Exception as e:
            data['warnings'].append(f'A股财务指标获取失败: {e}')

        if not data.get('price'):
            data['warnings'].append('当前价格缺失，估值结论不可直接使用')
        return data

    def _get_yfinance_financial_data(self, symbol: str, data: Dict, ledger: EvidenceLedger) -> Optional[Dict]:
        if not YFINANCE_AVAILABLE:
            data['warnings'].append('yfinance 未安装，美股/港股估值数据不可用')
            return data

        ticker = yf.Ticker(symbol)
        info = ticker.info

        field_map = [
            ('price', info.get('currentPrice') or info.get('regularMarketPrice'), 'currentPrice', 'USD'),
            ('name', info.get('longName', symbol), 'longName', ''),
            ('eps', info.get('trailingEps') or 0, 'trailingEps', 'USD/share'),
            ('bps', info.get('bookValue') or 0, 'bookValue', 'USD/share'),
            ('pe', info.get('trailingPE') or 0, 'trailingPE', 'x'),
            ('pb', info.get('priceToBook') or 0, 'priceToBook', 'x'),
            ('dividend', info.get('dividendRate') or 0, 'dividendRate', 'USD/share'),
            ('dividend_yield', info.get('dividendYield') or 0, 'dividendYield', ''),
            ('shares_outstanding', info.get('sharesOutstanding') or 0, 'sharesOutstanding', 'shares'),
            ('total_debt', info.get('totalDebt') or 0, 'totalDebt', 'USD'),
            ('cash', info.get('totalCash') or 0, 'totalCash', 'USD'),
            ('beta', info.get('beta') or 0, 'beta', ''),
            ('sector', info.get('sector') or '', 'sector', ''),
            ('industry', info.get('industry') or '', 'industry', ''),
        ]

        for key, value, field, unit in field_map:
            self._record(data, ledger, key, value, 'yfinance/Yahoo Finance', field, unit=unit)

        try:
            cashflow = ticker.cashflow
            if cashflow is not None and not cashflow.empty:
                fcf_history = self._extract_fcf_history(cashflow)
                if fcf_history:
                    self._record(
                        data,
                        ledger,
                        'free_cash_flow',
                        fcf_history[0],
                        'yfinance/Yahoo Finance',
                        'Free Cash Flow',
                        unit='USD',
                    )
                    data['free_cash_flow_history'] = fcf_history
        except Exception as e:
            data['warnings'].append(f'现金流数据获取失败: {e}')
            data['free_cash_flow'] = data.get('free_cash_flow', 0)

        if not data.get('price'):
            data['warnings'].append('当前价格缺失，估值结论不可直接使用')
        return data

    def _relative_valuation(self, data: Dict, params: Dict, ledger: EvidenceLedger) -> Dict:
        pe = data.get('pe', 0)
        pb = data.get('pb', 0)
        eps = data.get('eps', 0)
        bps = data.get('bps', 0)
        sector = data.get('sector') or 'default'
        benchmark = self.SECTOR_BENCHMARKS.get(sector, self.SECTOR_BENCHMARKS['default'])
        warnings = []
        valuations = {}

        peer_pe = params.get('peer_pe') or benchmark['pe']
        peer_pb = params.get('peer_pb') or benchmark['pb']

        if not params.get('peer_pe'):
            ledger.add_assumption(
                'peer_pe',
                peer_pe,
                note=f'未提供可比公司PE，使用{sector or "default"}板块默认参考值',
                source='model_default:sector_benchmark',
            )
            warnings.append('PE相对估值使用板块默认参考值，需替换为真实可比公司中位数')

        if not params.get('peer_pb'):
            ledger.add_assumption(
                'peer_pb',
                peer_pb,
                note=f'未提供可比公司PB，使用{sector or "default"}板块默认参考值',
                source='model_default:sector_benchmark',
            )
            warnings.append('PB相对估值使用板块默认参考值，需替换为真实可比公司中位数')

        if pe and pe > 0 and eps:
            valuations['pe_based'] = {
                'current_pe': pe,
                'benchmark_pe': peer_pe,
                'fair_value': eps * peer_pe,
                'overvalued': pe > peer_pe * 1.5,
                'benchmark_source': 'user_peer_input' if params.get('peer_pe') else 'sector_default_benchmark',
            }

        if pb and pb > 0 and bps:
            valuations['pb_based'] = {
                'current_pb': pb,
                'benchmark_pb': peer_pb,
                'fair_value': bps * peer_pb,
                'overvalued': pb > peer_pb * 1.5,
                'benchmark_source': 'user_peer_input' if params.get('peer_pb') else 'sector_default_benchmark',
            }

        return {
            'method': 'relative',
            'valuations': valuations,
            'warnings': warnings,
            'confidence': 'medium' if params.get('peer_pe') or params.get('peer_pb') else 'low',
        }

    def _dcf_valuation(self, data: Dict, params: Dict, ledger: EvidenceLedger) -> Dict:
        fcf = data.get('free_cash_flow', 0)
        shares = data.get('shares_outstanding', 0)
        warnings = []

        if not fcf or fcf <= 0:
            return {'method': 'DCF', 'error': '自由现金流数据不可用', 'fair_value': 0, 'warnings': []}
        if not shares or shares <= 0:
            return {
                'method': 'DCF',
                'error': '总股本/流通股本数据不可用，DCF每股价值不可计算',
                'fair_value': 0,
                'warnings': ['未使用硬编码股本假设，DCF已跳过'],
            }

        discount_rate = params['discount_rate']
        terminal_growth = params['terminal_growth']
        forecast_years = int(params['forecast_years'])

        if discount_rate <= terminal_growth:
            return {
                'method': 'DCF',
                'error': '折现率必须高于永续增长率',
                'fair_value': 0,
                'warnings': ['DCF参数不成立'],
            }

        fcf_growth, growth_source = self._estimate_fcf_growth(data, params, ledger)
        if growth_source != 'user_input':
            warnings.append('FCF增长率为估算/默认值，需用经营预测替换')

        pv_fcf, pv_terminal, enterprise_value = self._dcf_enterprise_value(
            fcf,
            fcf_growth,
            discount_rate,
            terminal_growth,
            forecast_years,
        )
        equity_value = enterprise_value + data.get('cash', 0) - data.get('total_debt', 0)
        fair_value = equity_value / shares if shares > 0 else 0

        return {
            'method': 'DCF',
            'free_cash_flow': fcf,
            'shares_outstanding': shares,
            'growth_rate': fcf_growth,
            'growth_source': growth_source,
            'discount_rate': discount_rate,
            'terminal_growth': terminal_growth,
            'forecast_years': forecast_years,
            'pv_fcf': pv_fcf,
            'pv_terminal': pv_terminal,
            'enterprise_value': enterprise_value,
            'equity_value': equity_value,
            'fair_value': fair_value,
            'sensitivity': self._dcf_sensitivity(fcf, shares, data, fcf_growth, discount_rate, terminal_growth, forecast_years),
            'warnings': warnings,
            'confidence': 'medium' if growth_source in {'user_input', 'historical_fcf'} else 'low',
        }

    def _ddm_valuation(self, data: Dict, params: Dict, ledger: EvidenceLedger) -> Dict:
        dividend = data.get('dividend', 0)
        if not dividend or dividend <= 0:
            return {'method': 'DDM', 'error': '无股息数据，不适用DDM', 'fair_value': 0, 'warnings': []}

        required_return = params['required_return']
        dividend_growth = params['dividend_growth']

        if required_return <= dividend_growth:
            return {
                'method': 'DDM',
                'error': '要求回报率必须高于股息增长率',
                'fair_value': 0,
                'warnings': ['DDM参数不成立'],
            }

        ledger.add_assumption(
            'dividend_growth',
            dividend_growth,
            note='股息增长率来自模型输入/默认值，需核对分红政策',
            source='model_default:ddm',
        )
        d1 = dividend * (1 + dividend_growth)
        fair_value = d1 / (required_return - dividend_growth)

        return {
            'method': 'DDM (Gordon Growth)',
            'current_dividend': dividend,
            'dividend_growth': dividend_growth,
            'required_return': required_return,
            'd1': d1,
            'fair_value': fair_value,
            'warnings': ['DDM仅适用于稳定分红公司'],
            'confidence': 'low',
        }

    def _calculate_fair_value(self, valuations: Dict, data: Dict) -> Dict:
        items: List[Tuple[str, float, float]] = []
        warnings = []

        relative = valuations.get('relative', {}).get('valuations', {})
        if relative.get('pe_based', {}).get('fair_value', 0) > 0:
            items.append(('relative_pe', relative['pe_based']['fair_value'], 0.25))
        if relative.get('pb_based', {}).get('fair_value', 0) > 0:
            items.append(('relative_pb', relative['pb_based']['fair_value'], 0.15))
        if valuations.get('dcf', {}).get('fair_value', 0) > 0:
            items.append(('dcf', valuations['dcf']['fair_value'], 0.45))
        if valuations.get('ddm', {}).get('fair_value', 0) > 0:
            items.append(('ddm', valuations['ddm']['fair_value'], 0.15))

        if not items:
            warnings.append('无可用估值方法，fair_value 回退为当前价格，仅作占位')
            return {
                'fair_value': data.get('price', 0),
                'basis': 'current_price_fallback',
                'methods_used': [],
                'fallback_used': True,
                'confidence': 'none',
                'warnings': warnings,
            }

        total_weight = sum(weight for _, _, weight in items)
        fair_value = sum(value * weight for _, value, weight in items) / total_weight
        methods = [name for name, _, _ in items]
        confidence = 'high' if len(items) >= 3 and 'dcf' in methods else 'medium' if len(items) >= 2 else 'low'

        return {
            'fair_value': fair_value,
            'basis': 'weighted_model_average',
            'methods_used': methods,
            'fallback_used': False,
            'confidence': confidence,
            'warnings': warnings,
        }

    def _build_model_assumptions(
        self,
        params: Dict,
        user_params: set,
        data: Dict,
        ledger: EvidenceLedger,
    ) -> List[Dict]:
        assumption_specs = [
            ('discount_rate', '折现率/WACC'),
            ('terminal_growth', '永续增长率'),
            ('forecast_years', '预测年数'),
            ('margin_of_safety', '安全边际'),
            ('required_return', 'DDM要求回报率'),
        ]
        assumptions = []
        for key, label in assumption_specs:
            source = 'user_input' if key in user_params else 'model_default'
            verified = key in user_params
            note = '用户输入' if verified else '模型默认值，需按公司和市场环境复核'
            assumptions.append({
                'name': key,
                'label': label,
                'value': params[key],
                'source': source,
                'verified': verified,
                'note': note,
            })
            if not verified:
                ledger.add_assumption(key, params[key], note=note, source=f'model_default:{key}')
        return assumptions

    def _estimate_fcf_growth(self, data: Dict, params: Dict, ledger: EvidenceLedger) -> Tuple[float, str]:
        if params.get('fcf_growth') is not None:
            return float(params['fcf_growth']), 'user_input'

        history = [value for value in data.get('free_cash_flow_history', []) if value and value > 0]
        if len(history) >= 2:
            latest = history[0]
            oldest = history[-1]
            years = max(len(history) - 1, 1)
            growth = (latest / oldest) ** (1 / years) - 1 if oldest > 0 else 0.03
            growth = max(-0.05, min(0.10, growth))
            ledger.add(
                'fcf_growth',
                growth,
                'yfinance/Yahoo Finance',
                quality='estimated',
                verified=True,
                note='由历史FCF粗略CAGR估算并限制在-5%到10%区间',
            )
            return growth, 'historical_fcf'

        ledger.add_assumption(
            'fcf_growth',
            0.03,
            note='缺少历史FCF序列，使用保守默认增长率',
            source='model_default:fcf_growth',
        )
        return 0.03, 'model_default'

    def _dcf_enterprise_value(
        self,
        fcf: float,
        growth: float,
        discount_rate: float,
        terminal_growth: float,
        years: int,
    ) -> Tuple[float, float, float]:
        pv_fcf = 0
        for year in range(1, years + 1):
            future_fcf = fcf * ((1 + growth) ** year)
            pv_fcf += future_fcf / ((1 + discount_rate) ** year)

        terminal_fcf = fcf * ((1 + growth) ** years) * (1 + terminal_growth)
        terminal_value = terminal_fcf / (discount_rate - terminal_growth)
        pv_terminal = terminal_value / ((1 + discount_rate) ** years)
        enterprise_value = pv_fcf + pv_terminal
        return pv_fcf, pv_terminal, enterprise_value

    def _dcf_sensitivity(
        self,
        fcf: float,
        shares: float,
        data: Dict,
        growth: float,
        discount_rate: float,
        terminal_growth: float,
        years: int,
    ) -> List[Dict]:
        rows = []
        for dr in [discount_rate - 0.01, discount_rate, discount_rate + 0.01]:
            for tg in [terminal_growth - 0.005, terminal_growth, terminal_growth + 0.005]:
                if dr <= tg:
                    continue
                _, _, ev = self._dcf_enterprise_value(fcf, growth, dr, tg, years)
                equity = ev + data.get('cash', 0) - data.get('total_debt', 0)
                rows.append({
                    'discount_rate': round(dr, 4),
                    'terminal_growth': round(tg, 4),
                    'fair_value': round(equity / shares, 4),
                })
        return rows

    def _extract_fcf_history(self, cashflow) -> List[float]:
        if 'Free Cash Flow' in cashflow.index:
            series = cashflow.loc['Free Cash Flow']
        else:
            ocf = cashflow.loc['Operating Cash Flow'] if 'Operating Cash Flow' in cashflow.index else None
            capex = cashflow.loc['Capital Expenditure'] if 'Capital Expenditure' in cashflow.index else None
            if ocf is None or capex is None:
                return []
            series = ocf + capex
        return [float(value) for value in series.tolist() if value == value]

    def _record(
        self,
        data: Dict,
        ledger: EvidenceLedger,
        key: str,
        value,
        source: str,
        field: str,
        *,
        unit: str = '',
        note: str = '',
    ):
        clean_value = self._safe_float(value)
        if clean_value is None and isinstance(value, str):
            clean_value = value
        if clean_value in [None, '']:
            return
        data[key] = clean_value
        ledger.add(key, clean_value, source, field=field, unit=unit, note=note)

    def _safe_float(self, value):
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _dedupe(self, values: List[str]) -> List[str]:
        seen = set()
        result = []
        for value in values:
            if value and value not in seen:
                seen.add(value)
                result.append(value)
        return result


def calculate_valuation(symbol: str, **params) -> Dict:
    """快速计算估值"""
    calculator = ValuationCalculator()
    return calculator.calculate(symbol, **params)


if __name__ == '__main__':
    result = calculate_valuation('AAPL')
    if result['success']:
        print(f"{result['symbol']} fair value: {result['fair_value']:.2f}")
        print(f"confidence: {result['valuation_confidence']}")
        print(f"warnings: {len(result['warnings'])}")
    else:
        print(f"估值失败: {result['error']}")
