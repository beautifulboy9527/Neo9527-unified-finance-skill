#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股选股器 v3.0 - Phase 4 数据源稳定性

新增功能:
- Phase 3: 预设策略、技术面筛选、多因子评分
- Phase 4: 数据源健康检查、自动降级、数据质量评分
"""

import sys
import os
from typing import Dict, List, Optional, Any
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 添加路径
SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SKILL_DIR)

try:
    import akshare as ak
    import pandas as pd
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False

# 导入策略和技术筛选
try:
    from screening_strategies import get_strategy, list_strategies, get_strategy_criteria, get_strategy_weights
    from technical_screener import run_technical_check, list_technical_checks
    from screener_data_source import get_screener_data_manager, DataQualityScorer
except ImportError:
    from skills.stock_skill.screening_strategies import get_strategy, list_strategies, get_strategy_criteria, get_strategy_weights
    from skills.stock_skill.technical_screener import run_technical_check, list_technical_checks
    from skills.stock_skill.screener_data_source import get_screener_data_manager, DataQualityScorer


def _num(value: Any) -> Optional[float]:
    """安全转换为数值"""
    if value is None:
        return None
    try:
        text = str(value).replace(",", "").replace("%", "").strip()
        if text in {"", "--", "None", "nan", "NaN", "暂无数据", "-"}:
            return None
        return float(text)
    except (TypeError, ValueError):
        return None


class EnhancedScreener:
    """增强选股器 v3.0 - Phase 4 数据源稳定性"""
    
    def __init__(self, use_fallback: bool = True):
        self.name = "EnhancedScreener"
        self.version = "3.0.0"
        self.use_fallback = use_fallback
        self.data_manager = get_screener_data_manager() if use_fallback else None
    
    def screen(
        self,
        scope: str = 'hs300',
        strategy: Optional[str] = None,
        criteria: Optional[Dict] = None,
        technical_checks: Optional[List[str]] = None,
        use_scoring: bool = False,
        industry: Optional[str] = None,
        top: int = 20,
        source: Optional[str] = None,  # Phase 4: 指定数据源
    ) -> Dict:
        """
        执行增强选股
        
        Args:
            scope: 选股范围 (hs300/zz500/all/a50)
            strategy: 预设策略名称 (value/growth/dividend/garp/turnaround/defensive/quality)
            criteria: 自定义筛选条件
            technical_checks: 技术面检查列表
            use_scoring: 是否启用多因子评分
            industry: 行业筛选
            top: 返回TOP N
        """
        if not AKSHARE_AVAILABLE:
            return {
                'success': False,
                'error': 'AkShare 未安装',
                'stocks': []
            }
        
        print(f"🔍 开始选股 (范围: {scope})...")
        
        # 1. 确定筛选条件
        final_criteria = {}
        strategy_info = None
        
        if strategy:
            strategy_info = get_strategy(strategy)
            if strategy_info:
                final_criteria = strategy_info.get("criteria", {})
                print(f"  📋 策略: {strategy_info['name']} - {strategy_info['description']}")
            else:
                print(f"  ⚠️ 未知策略: {strategy}")
        
        # 合并自定义条件
        if criteria:
            final_criteria.update(criteria)
        
        # 2. 获取股票池
        stock_pool = self._get_stock_pool(scope, industry)
        print(f"  📊 股票池: {len(stock_pool)} 只")
        
        if not stock_pool:
            return {
                'success': False,
                'error': '获取股票池失败',
                'stocks': []
            }
        
        # 3. 获取财务数据
        print("  📥 获取财务数据...")
        financial_data = self._get_financial_data(stock_pool)
        financial_data = self._drop_unverified_financial_rows(financial_data)
        
        if financial_data.empty:
            return {
                'success': False,
                'error': '没有取得可验证财务数据，未使用默认值生成选股结果',
                'stocks': []
            }
        
        # 4. 应用筛选条件
        print("  🔎 筛选中...")
        filtered_df = self._apply_criteria(financial_data, final_criteria)
        print(f"  ✅ 基础筛选: {len(filtered_df)} 只")
        
        # 5. 技术面筛选 (如果有)
        if technical_checks:
            print("  📈 技术面筛选...")
            filtered_df = self._apply_technical_filter(filtered_df, technical_checks)
            print(f"  ✅ 技术筛选: {len(filtered_df)} 只")
        
        # 6. 多因子评分
        if use_scoring and strategy_info:
            print("  🎯 多因子评分...")
            weights = strategy_info.get("scoring_weights", {})
            filtered_df = self._calculate_scores(filtered_df, weights)
        
        # 7. 排序
        sort_by = "composite_score" if use_scoring and "composite_score" in filtered_df.columns else "roe"
        if strategy_info and not use_scoring:
            sort_by = strategy_info.get("sort_by", "roe")
        
        if sort_by in filtered_df.columns:
            ascending = strategy_info.get("sort_ascending", False) if strategy_info else False
            filtered_df = filtered_df.sort_values(sort_by, ascending=ascending)
        
        # 8. 取TOP N
        result_df = filtered_df.head(top)
        
        # 9. 格式化输出
        stocks = result_df.to_dict('records')
        
        # Phase 4: 添加数据质量评分
        result = {
            'success': True,
            'scope': scope,
            'strategy': strategy,
            'strategy_info': strategy_info,
            'criteria': final_criteria,
            'technical_checks': technical_checks,
            'total_stocks': len(stock_pool),
            'filtered_stocks': len(filtered_df),
            'top_stocks': len(stocks),
            'stocks': stocks,
            'timestamp': datetime.now().isoformat(),
        }
        
        # 添加数据质量标签
        if self.data_manager:
            result = DataQualityScorer.add_quality_to_result(result)
            result['data_source_health'] = self.data_manager.get_health_report()
        
        return result
    
def _get_stock_pool(self, scope: str, industry: Optional[str] = None) -> List[str]:
        """获取股票池 - Phase 4 使用数据源管理器"""
        stocks = []
        
        # Phase 4: 使用数据源管理器（带降级和缓存）
        if self.data_manager:
            stocks = self.data_manager.get_stock_pool_with_fallback(scope)
            print(f"  📊 股票池 ({scope}): {len(stocks)} 只")
        else:
            # 兼容模式：直接调用 akshare
            try:
                if scope == 'hs300':
                    df = ak.index_stock_cons_weight_csindex(symbol='000300')
                    stocks = df['成分券代码'].tolist()
                elif scope == 'zz500':
                    df = ak.index_stock_cons_weight_csindex(symbol='000905')
                    stocks = df['成分券代码'].tolist()
                elif scope == 'a50':
                    df = ak.index_stock_cons_weight_csindex(symbol='000016')
                    stocks = df['成分券代码'].tolist()
                elif scope == 'all':
                    df = ak.stock_zh_a_spot_em()
                    stocks = df['代码'].tolist()
                else:
                    df = ak.index_stock_cons_weight_csindex(symbol='000300')
                    stocks = df['成分券代码'].tolist()
                print(f"  📊 股票池: {len(stocks)} 只")
            except Exception as e:
                print(f"  ❌ 获取股票池失败: {e}")
        
        # 行业筛选
        if industry and stocks:
            try:
                industry_stocks = self._filter_by_industry(stocks, industry)
                if industry_stocks:
                    stocks = industry_stocks
                    print(f"  🏭 行业筛选 ({industry}): {len(stocks)} 只")
            except Exception as e:
                print(f"  ⚠️ 行业筛选失败: {e}")
        
        return stocks
    
    def _filter_by_industry(self, stocks: List[str], industry: str) -> List[str]:
        """按行业筛选"""
        industry_stocks = []
        
        for code in stocks[:50]:  # 限制数量避免超时
            try:
                info = ak.stock_individual_info_em(symbol=code)
                if info is not None and not info.empty:
                    stock_industry = info[info['item'] == '行业']['value'].values
                    if len(stock_industry) > 0 and industry in str(stock_industry[0]):
                        industry_stocks.append(code)
            except:
                continue
        
        return industry_stocks
    
    def _get_financial_data(self, stocks: List[str]) -> pd.DataFrame:
        """获取财务数据 - Phase 4 使用数据源管理器"""
        all_data = []
        max_stocks = min(len(stocks), 150)
        
        for i, code in enumerate(stocks[:max_stocks]):
            if i % 30 == 0:
                print(f"    进度: {i}/{max_stocks}")
            
            # Phase 4: 使用数据源管理器（带降级）
            if self.data_manager:
                data = self.data_manager.get_financial_data_with_fallback(code)
                if data:
                    all_data.append(data)
            else:
                # 兼容模式
                try:
                    df = ak.stock_financial_analysis_indicator(symbol=code)
                    
                    if df is not None and not df.empty:
                        latest = df.iloc[0]
                        
                        stock_data = {
                            'code': code,
                            'pe': _num(latest.get('市盈率')),
                            'pb': _num(latest.get('市净率')),
                            'roe': _num(latest.get('净资产收益率')),
                            'roa': _num(latest.get('总资产净利润(ROA)')),
                            'gross_margin': _num(latest.get('销售毛利率')),
                            'net_margin': _num(latest.get('销售净利率')),
                            'debt_ratio': _num(latest.get('资产负债率')),
                            'current_ratio': _num(latest.get('流动比率')),
                        }
                        
                        if len(df) >= 2:
                            prev = df.iloc[1]
                            prev_roe = _num(prev.get('净资产收益率'))
                            if stock_data['roe'] and prev_roe:
                                stock_data['roe_growth'] = stock_data['roe'] - prev_roe
                        
                        all_data.append(stock_data)
                except:
                    continue
        
        return pd.DataFrame(all_data)

    def _drop_unverified_financial_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        """剔除没有核心财务字段的股票，避免默认值或空值进入选股结果。"""
        if df.empty:
            return df
        core_fields = ["pe", "pb", "roe"]
        for field in core_fields:
            if field not in df.columns:
                df[field] = None
        verified_mask = df[core_fields].notna().any(axis=1)
        if "data_quality" in df.columns:
            verified_mask &= df["data_quality"].fillna("").astype(str).str.lower() != "unavailable"
        dropped = len(df) - int(verified_mask.sum())
        if dropped:
            print(f"  ⚠️ 剔除财务数据不可验证股票: {dropped} 只")
        return df[verified_mask].copy()
    
    def _apply_criteria(self, df: pd.DataFrame, criteria: Dict) -> pd.DataFrame:
        """应用筛选条件"""
        if df.empty:
            return df
        
        mask = pd.Series([True] * len(df), index=df.index)
        
        # 估值筛选
        if criteria.get('pe_max'):
            pe_val = df['pe'].fillna(0)
            mask &= (pe_val > 0) & (pe_val <= criteria['pe_max'])
        
        if criteria.get('pb_max'):
            pb_val = df['pb'].fillna(0)
            mask &= (pb_val > 0) & (pb_val <= criteria['pb_max'])
        
        # 盈利筛选
        if criteria.get('roe_min'):
            mask &= df['roe'].fillna(0) >= criteria['roe_min']
        
        if criteria.get('roa_min'):
            mask &= df['roa'].fillna(0) >= criteria['roa_min']
        
        if criteria.get('gross_margin_min'):
            mask &= df['gross_margin'].fillna(0) >= criteria['gross_margin_min']
        
        if criteria.get('net_margin_min'):
            mask &= df['net_margin'].fillna(0) >= criteria['net_margin_min']
        
        # 财务安全筛选
        if criteria.get('debt_ratio_max'):
            mask &= df['debt_ratio'].fillna(100) <= criteria['debt_ratio_max']
        
        if criteria.get('current_ratio_min'):
            mask &= df['current_ratio'].fillna(0) >= criteria['current_ratio_min']
        
        return df[mask]
    
    def _apply_technical_filter(self, df: pd.DataFrame, checks: List[str]) -> pd.DataFrame:
        """应用技术面筛选"""
        if df.empty or not checks:
            return df
        
        print(f"    技术面检查: {checks}")
        passed_codes = []
        max_stocks = min(len(df), 50)  # 限制数量避免超时
        
        for i, row in df.head(max_stocks).iterrows():
            code = row.get('code')
            try:
                # 获取K线数据
                kline_df = ak.stock_zh_a_hist(symbol=code, period="daily", adjust="qfq")
                
                if kline_df is None or len(kline_df) < 60:
                    continue
                
                # 提取价格和成交量
                prices = kline_df['收盘'].tolist()
                prices = prices[::-1]  # 反转，使最新价格在前
                
                volumes = kline_df['成交量'].tolist()
                volumes = volumes[::-1]
                
                # 执行技术检查
                all_pass = True
                for check_id in checks:
                    result = run_technical_check(check_id, prices, volumes)
                    if not result.get('signal', False):
                        all_pass = False
                        break
                
                if all_pass:
                    passed_codes.append(code)
                    
            except Exception as e:
                continue
        
        # 过滤
        if passed_codes:
            df = df[df['code'].isin(passed_codes)]
            print(f"    ✅ 技术筛选通过: {len(passed_codes)} 只")
        else:
            print(f"    ⚠️ 技术筛选无通过股票")
        
        return df
    
    def _calculate_scores(self, df: pd.DataFrame, weights: Dict) -> pd.DataFrame:
        """计算多因子评分"""
        if df.empty:
            return df
        
        # 估值因子 (PE/PB越低越好)
        def valuation_score(row):
            score = 0
            pe = row.get('pe', 0) or 0
            pb = row.get('pb', 0) or 0
            
            if pe > 0:
                if pe < 15:
                    score += 40
                elif pe < 25:
                    score += 30
                elif pe < 35:
                    score += 20
                else:
                    score += 10
            
            if pb > 0:
                if pb < 2:
                    score += 30
                elif pb < 3:
                    score += 20
                elif pb < 5:
                    score += 10
            
            return score
        
        # 盈利因子 (ROE/毛利率越高越好)
        def profitability_score(row):
            score = 0
            roe = row.get('roe', 0) or 0
            gross = row.get('gross_margin', 0) or 0
            net = row.get('net_margin', 0) or 0
            
            if roe > 20:
                score += 40
            elif roe > 15:
                score += 30
            elif roe > 10:
                score += 20
            
            if gross > 40:
                score += 30
            elif gross > 30:
                score += 20
            elif gross > 20:
                score += 10
            
            if net > 15:
                score += 30
            elif net > 10:
                score += 20
            elif net > 5:
                score += 10
            
            return score
        
        # 安全因子 (负债率越低越好)
        def safety_score(row):
            score = 0
            debt = row.get('debt_ratio', 100) or 100
            current = row.get('current_ratio', 0) or 0
            
            if debt < 30:
                score += 40
            elif debt < 50:
                score += 30
            elif debt < 60:
                score += 20
            
            if current > 2:
                score += 30
            elif current > 1.5:
                score += 20
            elif current > 1:
                score += 10
            
            return score
        
        # 计算各因子分数
        df['valuation_score'] = df.apply(valuation_score, axis=1)
        df['profitability_score'] = df.apply(profitability_score, axis=1)
        df['safety_score'] = df.apply(safety_score, axis=1)
        df['growth_score'] = df['roe_growth'].fillna(0).apply(lambda x: min(100, max(0, 50 + x * 2)))
        
        # 综合评分 (加权)
        df['composite_score'] = (
            df['valuation_score'] * weights.get('valuation', 0.25) +
            df['profitability_score'] * weights.get('profitability', 0.25) +
            df['safety_score'] * weights.get('safety', 0.25) +
            df['growth_score'] * weights.get('growth', 0.25)
        )
        
        return df


# ============ 快速使用函数 ============

def screen_stocks_v2(
    scope: str = 'hs300',
    strategy: Optional[str] = None,
    **kwargs
) -> Dict:
    """快速选股 (v2)"""
    screener = EnhancedScreener()
    return screener.screen(
        scope=scope,
        strategy=strategy,
        criteria=kwargs.get('criteria'),
        technical_checks=kwargs.get('technical_checks'),
        use_scoring=kwargs.get('use_scoring', False),
        industry=kwargs.get('industry'),
        top=kwargs.get('top', 20),
    )


# ============ 格式化输出 ============

def format_screening_output(result: Dict) -> str:
    """格式化选股结果输出"""
    if not result.get('success'):
        return f"❌ {result.get('error', '选股失败')}"
    
    lines = []
    lines.append("=" * 60)
    lines.append("📊 智能选股结果")
    lines.append("=" * 60)
    
    # 策略信息
    if result.get('strategy_info'):
        info = result['strategy_info']
        lines.append(f"\n📋 策略: {info['name']}")
        lines.append(f"   {info['description']}")
    
    # 筛选统计
    lines.append(f"\n📈 筛选统计:")
    lines.append(f"   股票池: {result.get('total_stocks', 0)} 只")
    lines.append(f"   符合条件: {result.get('filtered_stocks', 0)} 只")
    lines.append(f"   展示TOP: {result.get('top_stocks', 0)} 只")
    
    # 技术面检查
    if result.get('technical_checks'):
        lines.append(f"\n📉 技术面条件: {', '.join(result['technical_checks'])}")
    
    # 股票列表
    stocks = result.get('stocks', [])
    if stocks:
        lines.append(f"\n{'─' * 60}")
        lines.append(f"{'序号':<4} {'代码':<8} {'PE':<8} {'PB':<8} {'ROE':<8} {'净利率':<8} {'评分':<6}")
        lines.append(f"{'─' * 60}")
        
        for i, stock in enumerate(stocks[:20], 1):
            code = stock.get('code', 'N/A')
            pe = stock.get('pe', 0) or 0
            pb = stock.get('pb', 0) or 0
            roe = stock.get('roe', 0) or 0
            net_margin = stock.get('net_margin', 0) or 0
            score = stock.get('composite_score', 0) or 0
            
            lines.append(f"{i:<4} {code:<8} {pe:<8.1f} {pb:<8.2f} {roe:<8.1f} {net_margin:<8.1f} {score:<6.1f}")
    else:
        lines.append("\n⚠️ 没有符合条件的股票")
    
    lines.append("\n" + "=" * 60)
    
    return "\n".join(lines)


# ============ 测试 ============

if __name__ == '__main__':
    print("=" * 60)
    print("A股选股器 v2.0 测试")
    print("=" * 60)
    
    # 列出可用策略
    print("\n📋 可用策略:")
    for s in list_strategies():
        print(f"  • {s['id']}: {s['name']} - {s['description']}")
    
    print("\n📈 可用技术检查:")
    for c in list_technical_checks():
        print(f"  • {c['id']}: {c['name']}")
    
    # 测试价值投资策略
    print("\n" + "=" * 60)
    print("测试: 价值投资策略 (hs300)")
    print("=" * 60)
    
    result = screen_stocks_v2(
        scope='hs300',
        strategy='value',
        use_scoring=True,
        top=10,
    )
    
    print(format_screening_output(result))
