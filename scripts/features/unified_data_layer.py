#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一数据访问层 v1.0
- 多数据源统一接口
- 数据验证和清洗
- 缺失值智能处理
- 数据质量评分
"""

import sys
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import numpy as np
import pandas as pd

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataValidator:
    """数据验证器"""
    
    @staticmethod
    def is_valid(value: Any) -> bool:
        """检查值是否有效（非None、非nan、非空）"""
        if value is None:
            return False
        if isinstance(value, float) and (np.isnan(value) or np.isinf(value)):
            return False
        if isinstance(value, str) and value.strip() in ['', 'N/A', 'nan', 'None']:
            return False
        return True
    
    @staticmethod
    def validate_price(data: Dict) -> tuple:
        """验证价格数据"""
        critical_fields = ['current', 'high', 'low', 'volume']
        important_fields = ['open', 'close', 'change_pct']
        
        critical_valid = sum(1 for f in critical_fields if DataValidator.is_valid(data.get(f)))
        important_valid = sum(1 for f in important_fields if DataValidator.is_valid(data.get(f)))
        
        critical_score = (critical_valid / len(critical_fields)) * 60
        important_score = (important_valid / len(important_fields)) * 40
        
        return critical_score + important_score, critical_valid == len(critical_fields)
    
    @staticmethod
    def validate_technical(data: Dict) -> tuple:
        """验证技术分析数据"""
        critical_fields = ['support_near', 'resistance_near']
        important_fields = ['rsi', 'macd', 'atr']
        
        critical_valid = sum(1 for f in critical_fields if DataValidator.is_valid(data.get(f)))
        important_valid = sum(1 for f in important_fields if DataValidator.is_valid(data.get(f)))
        
        critical_score = (critical_valid / len(critical_fields)) * 60
        important_score = (important_valid / len(important_fields)) * 40
        
        return critical_score + important_score, critical_valid == len(critical_fields)


class DataQualityScorer:
    """数据质量评分器"""
    
    @staticmethod
    def get_quality_label(score: float) -> tuple:
        """获取数据质量标签"""
        if score >= 90:
            return '高置信度', '✅', '数据完整可靠'
        elif score >= 70:
            return '中等置信度', '⚠️', '部分数据为估算值'
        elif score >= 50:
            return '低置信度', '❌', '大量数据缺失，建议谨慎使用'
        else:
            return '不可用', '🚫', '数据严重缺失，不可依赖'


class MissingValueHandler:
    """缺失值处理器"""
    
    @staticmethod
    def handle_missing_support(current_price: float, hist_data: pd.DataFrame) -> Dict:
        """
        支撑阻力位缺失时的降级方案
        使用ATR和均线计算
        """
        try:
            # 计算ATR
            high = hist_data['High']
            low = hist_data['Low']
            close = hist_data['Close']
            
            tr1 = high - low
            tr2 = abs(high - close.shift(1))
            tr3 = abs(low - close.shift(1))
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(14).mean().iloc[-1]
            
            # 使用ATR计算支撑阻力
            support_near = current_price - atr * 2
            support_far = current_price - atr * 3
            resistance_near = current_price + atr * 2
            resistance_far = current_price + atr * 3
            
            # 计算距离百分比
            support_near_pct = ((support_near - current_price) / current_price) * 100 if current_price > 0 else 0
            support_far_pct = ((support_far - current_price) / current_price) * 100 if current_price > 0 else 0
            resistance_near_pct = ((resistance_near - current_price) / current_price) * 100 if current_price > 0 else 0
            resistance_far_pct = ((resistance_far - current_price) / current_price) * 100 if current_price > 0 else 0
            
            return {
                'support_near': support_near,
                'support_far': support_far,
                'resistance_near': resistance_near,
                'resistance_far': resistance_far,
                'support_near_pct': support_near_pct,
                'support_far_pct': support_far_pct,
                'resistance_near_pct': resistance_near_pct,
                'resistance_far_pct': resistance_far_pct,
                'atr': atr,
                'data_quality': 'estimated',
                'estimation_method': 'ATR计算'
            }
        except Exception as e:
            logger.error(f"支撑阻力位降级计算失败: {e}")
            return {
                'support_near': current_price * 0.92,
                'support_far': current_price * 0.88,
                'resistance_near': current_price * 1.08,
                'resistance_far': current_price * 1.15,
                'support_near_pct': -8.0,
                'support_far_pct': -12.0,
                'resistance_near_pct': 8.0,
                'resistance_far_pct': 15.0,
                'data_quality': 'fallback',
                'estimation_method': '默认比例'
            }
    
    @staticmethod
    def handle_missing_industry(symbol: str) -> Dict:
        """行业信息缺失时的降级方案"""
        
        # 根据股票代码范围推断
        industry_map = {
            '60': ('工业', '工业板块', '成熟期', '中'),
            '00': ('科技', '科技板块', '成长期', '中'),
            '30': ('综合', '创业板', '成长期', '高'),
            '68': ('科技', '科创板', '成长期', '高'),
        }
        
        prefix = symbol[:2]
        industry, sector, cycle, risk = industry_map.get(prefix, ('综合', '综合板块', '未知', '中'))
        
        return {
            'industry': industry,
            'sector': sector,
            'cycle': cycle,
            'risk': risk,
            'name_cn': industry,
            'name': industry,
            'data_quality': 'estimated',
            'estimation_method': '股票代码推断'
        }
    
    @staticmethod
    def handle_missing_financial() -> Dict:
        """财务数据缺失时的默认值"""
        return {
            'debt_ratio': 50.0,
            'current_ratio': 1.5,
            'roe': 10.0,
            'gross_margin': 30.0,
            'status': '数据缺失',
            'data_quality': 'default',
            'estimation_method': '行业默认值'
        }


class UnifiedDataLayer:
    """统一数据访问层"""
    
    def __init__(self):
        self.validator = DataValidator()
        self.scorer = DataQualityScorer()
        self.missing_handler = MissingValueHandler()
    
    def process_data(self, symbol: str, raw_data: Dict, hist_data: pd.DataFrame = None) -> Dict:
        """
        处理原始数据，确保数据完整性和有效性
        
        Args:
            symbol: 股票代码
            raw_data: 原始数据字典
            hist_data: 历史K线数据
        
        Returns:
            处理后的数据字典，包含数据质量标记
        """
        processed = raw_data.copy()
        
        # 1. 处理价格数据
        if 'price' in processed:
            price_data = processed['price']
            if price_data.get('current') is None or np.isnan(price_data.get('current', 0)):
                logger.warning(f"{symbol}: 价格数据缺失")
                price_data['data_quality'] = 'missing'
            
            # 验证并评分
            score, is_valid = DataValidator.validate_price(price_data)
            price_data['quality_score'] = score
            price_data['quality_label'], price_data['quality_icon'], price_data['quality_desc'] = \
                DataQualityScorer.get_quality_label(score)
        
        # 2. 处理技术分析数据
        if 'technical' in processed:
            tech_data = processed['technical']
            patterns = tech_data.get('patterns', {})
            
            # 检查支撑阻力位是否为nan
            if 'support_near' in patterns and (patterns['support_near'] is None or np.isnan(patterns.get('support_near', 0))):
                logger.warning(f"{symbol}: 支撑阻力位数据缺失，启动降级计算")
                
                if hist_data is not None and not hist_data.empty:
                    current_price = processed.get('price', {}).get('current', 0)
                    if current_price > 0:
                        # 使用降级方案计算
                        estimated_sr = MissingValueHandler.handle_missing_support(current_price, hist_data)
                        patterns.update(estimated_sr)
                        
                        # 标记为估算数据
                        tech_data['data_quality'] = 'estimated'
                        tech_data['estimation_method'] = estimated_sr.get('estimation_method')
            
            # 验证并评分
            score, is_valid = DataValidator.validate_technical(patterns)
            tech_data['quality_score'] = score
            tech_data['quality_label'], tech_data['quality_icon'], tech_data['quality_desc'] = \
                DataQualityScorer.get_quality_label(score)
        
        # 3. 处理行业数据
        if 'industry' in processed:
            industry_data = processed['industry']
            
            # 检查关键字段是否缺失
            if industry_data.get('cycle') == '未知' or industry_data.get('risk') == '未知':
                logger.warning(f"{symbol}: 行业信息不完整")
                
                # 使用降级方案
                estimated_industry = MissingValueHandler.handle_missing_industry(symbol)
                
                # 只填充缺失的字段
                for key, value in estimated_industry.items():
                    if key not in industry_data or industry_data.get(key) in ['未知', None, '']:
                        industry_data[key] = value
                
                industry_data['data_quality'] = 'estimated'
        
        # 4. 处理财务数据
        if 'financial' in processed:
            financial_data = processed['financial']
            
            # 检查关键财务指标是否缺失
            if not financial_data.get('debt_ratio') or financial_data.get('status') == '数据缺失':
                logger.warning(f"{symbol}: 财务数据缺失")
                
                # 使用默认值
                default_financial = MissingValueHandler.handle_missing_financial()
                for key, value in default_financial.items():
                    if key not in financial_data or financial_data.get(key) is None:
                        financial_data[key] = value
        
        # 5. 添加总体数据质量评分
        overall_score = self._calculate_overall_score(processed)
        processed['data_quality_score'] = overall_score
        processed['data_quality_label'], processed['data_quality_icon'], processed['data_quality_desc'] = \
            DataQualityScorer.get_quality_label(overall_score)
        
        return processed
    
    def _calculate_overall_score(self, data: Dict) -> float:
        """计算总体数据质量分数"""
        scores = []
        weights = []
        
        # 价格数据权重40%
        if 'price' in data and 'quality_score' in data['price']:
            scores.append(data['price']['quality_score'])
            weights.append(0.4)
        
        # 技术分析权重30%
        if 'technical' in data and 'quality_score' in data['technical']:
            scores.append(data['technical']['quality_score'])
            weights.append(0.3)
        
        # 财务数据权重20%
        if 'financial' in data:
            financial_score = 100 if data['financial'].get('status') not in ['数据缺失', '高风险'] else 60
            scores.append(financial_score)
            weights.append(0.2)
        
        # 行业数据权重10%
        if 'industry' in data:
            industry_score = 100 if data['industry'].get('cycle') != '未知' else 50
            scores.append(industry_score)
            weights.append(0.1)
        
        # 加权平均
        if scores and weights:
            return sum(s * w for s, w in zip(scores, weights)) / sum(weights)
        else:
            return 50.0  # 默认中等质量


def safe_analysis(fallback_value=None, log_error=True):
    """
    统一的错误处理装饰器
    
    用法:
        @safe_analysis(fallback_value={})
        def analyze_something(data):
            return process(data)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                
                # 验证结果
                if result is None:
                    if log_error:
                        logger.warning(f"{func.__name__} returned None")
                    return fallback_value if fallback_value is not None else {}
                
                if isinstance(result, dict) and not result:
                    if log_error:
                        logger.warning(f"{func.__name__} returned empty dict")
                    return fallback_value if fallback_value is not None else {}
                
                return result
                
            except Exception as e:
                if log_error:
                    logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
                return fallback_value if fallback_value is not None else {}
        
        return wrapper
    return decorator


# 便捷函数
def process_stock_data(symbol: str, raw_data: Dict, hist_data: pd.DataFrame = None) -> Dict:
    """
    便捷函数：处理股票数据
    
    Args:
        symbol: 股票代码
        raw_data: 原始数据
        hist_data: 历史K线数据
    
    Returns:
        处理后的数据，包含质量标记
    """
    layer = UnifiedDataLayer()
    return layer.process_data(symbol, raw_data, hist_data)


if __name__ == '__main__':
    # 测试代码
    print("=" * 80)
    print("统一数据层测试")
    print("=" * 80)
    
    # 测试1: 价格验证
    test_price = {
        'current': 100.0,
        'high': 105.0,
        'low': 98.0,
        'volume': 1000000,
    }
    score, is_valid = DataValidator.validate_price(test_price)
    print(f"\n测试1 - 价格验证: 分数={score}, 有效={is_valid}")
    
    # 测试2: 数据质量标签
    label, icon, desc = DataQualityScorer.get_quality_label(85)
    print(f"测试2 - 质量标签: {label} {icon} - {desc}")
    
    # 测试3: 缺失值处理
    estimated = MissingValueHandler.handle_missing_industry('603986')
    print(f"\n测试3 - 行业推断: {estimated}")
    
    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)
