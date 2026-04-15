#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Financial Analyzer - 财务异常检测
整合自 china-stock-analysis 的财务分析能力
"""

import sys
import os
import json
import argparse
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Windows 编码修复
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class RiskLevel(Enum):
    """风险等级"""
    LOW = "🟢 低风险"
    MEDIUM = "🟡 中风险"
    HIGH = "🔴 高风险"


@dataclass
class AnomalyResult:
    """异常检测结果"""
    anomaly_type: str
    severity: str  # mild/moderate/severe
    description: str
    data: Dict
    recommendation: str


@dataclass
class FinancialAnalysisResult:
    """财务分析结果"""
    code: str
    name: str
    risk_level: RiskLevel
    anomalies: List[AnomalyResult]
    overall_score: float  # 0-100
    key_metrics: Dict
    summary: str


class FinancialAnomalyDetector:
    """财务异常检测器"""
    
    def __init__(self, code: str, name: str = ""):
        self.code = code
        self.name = name
        
    def detect_receivable_anomaly(self, 
                                    revenue_growth: float,
                                    receivable_growth: float,
                                    industry_avg_growth: float = 0.1) -> Optional[AnomalyResult]:
        """
        应收账款异常检测
        
        规则: 应收账款增速 > 营收增速 × 1.5
        """
        threshold = revenue_growth * 1.5
        
        if receivable_growth > threshold:
            severity = "severe" if receivable_growth > revenue_growth * 2 else "moderate"
            return AnomalyResult(
                anomaly_type="应收账款异常",
                severity=severity,
                description=f"应收账款增速({receivable_growth*100:.1f}%)远超营收增速({revenue_growth*100:.1f}%)",
                data={
                    "revenue_growth": revenue_growth,
                    "receivable_growth": receivable_growth,
                    "threshold": threshold
                },
                recommendation="可能存在赊销激增或虚增收入的情况，需结合现金流验证"
            )
        return None
    
    def detect_cash_flow_anomaly(self,
                                   net_profit: float,
                                   operating_cashflow: float,
                                   net_profit_growth: float = 0.1,
                                   ocf_growth: float = -0.1) -> Optional[AnomalyResult]:
        """
        现金流背离检测
        
        规则: 净利润增长但经营现金流下降 (背离)
        """
        if net_profit_growth > 0.1 and ocf_growth < -0.1:
            # 盈利质量不佳的信号
            ratio = operating_cashflow / net_profit if net_profit > 0 else 0
            return AnomalyResult(
                anomaly_type="现金流背离",
                severity="moderate" if ratio > 0.5 else "severe",
                description=f"净利润增长但经营现金流下降，盈利质量存疑 (OCF/净利润={ratio:.2f})",
                data={
                    "net_profit": net_profit,
                    "operating_cashflow": operating_cashflow,
                    "ratio": ratio
                },
                recommendation="检查是否存在应收账款堆积或存货积压"
            )
        return None
    
    def detect_inventory_anomaly(self,
                                   revenue_growth: float,
                                   inventory_growth: float) -> Optional[AnomalyResult]:
        """
        存货异常检测
        
        规则: 存货增速 > 营收增速 × 2
        """
        threshold = revenue_growth * 2
        
        if inventory_growth > threshold:
            severity = "severe" if inventory_growth > revenue_growth * 3 else "moderate"
            return AnomalyResult(
                anomaly_type="存货异常",
                severity=severity,
                description=f"存货增速({inventory_growth*100:.1f}%)远超营收增速({revenue_growth*100:.1f}%)",
                data={
                    "revenue_growth": revenue_growth,
                    "inventory_growth": inventory_growth
                },
                recommendation="可能存在滞销或库存积压风险"
            )
        return None
    
    def detect_gross_margin_anomaly(self,
                                     gross_margin: float,
                                     industry_avg: float = 0.30,
                                     margin_volatility: float = 0.05) -> Optional[AnomalyResult]:
        """
        毛利率异常检测
        
        规则: 波动 > 行业均值 × 2
        """
        deviation = abs(gross_margin - industry_avg) / industry_avg
        
        if deviation > 0.5:  # 偏离超过50%
            return AnomalyResult(
                anomaly_type="毛利率异常",
                severity="severe" if deviation > 1.0 else "moderate",
                description=f"毛利率({gross_margin*100:.1f}%)偏离行业均值({industry_avg*100:.1f}%)",
                data={
                    "gross_margin": gross_margin,
                    "industry_avg": industry_avg,
                    "deviation": deviation
                },
                recommendation="检查是否具有护城河优势或存在财务操纵嫌疑"
            )
        return None
    
    def detect_related_party_anomaly(self,
                                      related_party_ratio: float) -> Optional[AnomalyResult]:
        """
        关联交易异常检测
        
        规则: 关联交易占比 > 30%
        """
        if related_party_ratio > 0.30:
            severity = "severe" if related_party_ratio > 0.50 else "moderate"
            return AnomalyResult(
                anomaly_type="关联交易异常",
                severity=severity,
                description=f"关联交易占比({related_party_ratio*100:.1f}%)过高",
                data={"related_party_ratio": related_party_ratio},
                recommendation="存在利益输送嫌疑，需重点关注交易定价合理性"
            )
        return None
    
    def detect_non_recurring_anomaly(self,
                                       non_recurring_ratio: float) -> Optional[AnomalyResult]:
        """
        非经常性损益异常检测
        
        规则: 非经常性损益占比 > 30%
        """
        if non_recurring_ratio > 0.30:
            return AnomalyResult(
                anomaly_type="非经常性损益异常",
                severity="moderate",
                description=f"非经常性损益占比({non_recurring_ratio*100:.1f}%)过高，主业盈利能力存疑",
                data={"non_recurring_ratio": non_recurring_ratio},
                recommendation="关注扣非净利润，评估主业真实盈利能力"
            )
        return None
    
    def analyze(self, financial_data: Dict) -> FinancialAnalysisResult:
        """
        综合财务分析
        
        Args:
            financial_data: {
                "revenue_growth": float,
                "receivable_growth": float,
                "inventory_growth": float,
                "net_profit": float,
                "operating_cashflow": float,
                "gross_margin": float,
                "related_party_ratio": float,
                "non_recurring_ratio": float,
                "debt_ratio": float,
                "current_ratio": float
            }
        """
        anomalies = []
        
        # 应收款异常
        ar_anomaly = self.detect_receivable_anomaly(
            financial_data.get('revenue_growth', 0),
            financial_data.get('receivable_growth', 0)
        )
        if ar_anomaly:
            anomalies.append(ar_anomaly)
        
        # 现金流背离
        cf_anomaly = self.detect_cash_flow_anomaly(
            financial_data.get('net_profit', 0),
            financial_data.get('operating_cashflow', 0),
            financial_data.get('net_profit_growth', 0),
            financial_data.get('ocf_growth', 0)
        )
        if cf_anomaly:
            anomalies.append(cf_anomaly)
        
        # 存货异常
        inv_anomaly = self.detect_inventory_anomaly(
            financial_data.get('revenue_growth', 0),
            financial_data.get('inventory_growth', 0)
        )
        if inv_anomaly:
            anomalies.append(inv_anomaly)
        
        # 毛利率异常
        gm_anomaly = self.detect_gross_margin_anomaly(
            financial_data.get('gross_margin', 0),
            financial_data.get('industry_avg', 0.30)
        )
        if gm_anomaly:
            anomalies.append(gm_anomaly)
        
        # 关联交易
        rp_anomaly = self.detect_related_party_anomaly(
            financial_data.get('related_party_ratio', 0)
        )
        if rp_anomaly:
            anomalies.append(rp_anomaly)
        
        # 非经常性损益
        nr_anomaly = self.detect_non_recurring_anomaly(
            financial_data.get('non_recurring_ratio', 0)
        )
        if nr_anomaly:
            anomalies.append(nr_anomaly)
        
        # 计算风险等级
        severe_count = sum(1 for a in anomalies if a.severity == "severe")
        moderate_count = sum(1 for a in anomalies if a.severity == "moderate")
        
        if severe_count > 0:
            risk_level = RiskLevel.HIGH
            overall_score = max(20, 100 - severe_count * 30 - moderate_count * 15)
        elif moderate_count > 2:
            risk_level = RiskLevel.MEDIUM
            overall_score = max(40, 100 - moderate_count * 20)
        elif moderate_count > 0:
            risk_level = RiskLevel.MEDIUM
            overall_score = max(60, 100 - moderate_count * 15)
        else:
            risk_level = RiskLevel.LOW
            overall_score = 100
        
        summary = f"发现 {len(anomalies)} 项异常: {severe_count}项严重, {moderate_count}项中等"
        
        return FinancialAnalysisResult(
            code=self.code,
            name=self.name,
            risk_level=risk_level,
            anomalies=anomalies,
            overall_score=overall_score,
            key_metrics=financial_data,
            summary=summary
        )


def main():
    parser = argparse.ArgumentParser(description='财务异常检测器')
    parser.add_argument('--code', required=True, help='股票代码')
    parser.add_argument('--name', default='', help='股票名称')
    parser.add_argument('--output', default='financial_analysis.json', help='输出文件')
    
    args = parser.parse_args()
    
    # 示例数据 (实际使用时从 data_fetcher 获取)
    sample_data = {
        "revenue_growth": 0.15,
        "receivable_growth": 0.25,  # 应收款增速 > 营收增速 × 1.5
        "inventory_growth": 0.20,
        "net_profit": 100,
        "operating_cashflow": 80,
        "gross_margin": 0.35,
        "industry_avg": 0.30,
        "related_party_ratio": 0.10,
        "non_recurring_ratio": 0.05,
        "debt_ratio": 0.50,
        "current_ratio": 1.5
    }
    
    detector = FinancialAnomalyDetector(args.code, args.name)
    result = detector.analyze(sample_data)
    
    print(f"📊 {args.code} 财务异常检测")
    print(f"风险等级: {result.risk_level.value}")
    print(f"综合评分: {result.overall_score}/100")
    print(f"异常数量: {len(result.anomalies)}")
    print()
    
    for anomaly in result.anomalies:
        print(f"[{anomaly.severity.upper()}] {anomaly.anomaly_type}")
        print(f"  {anomaly.description}")
        print(f"  建议: {anomaly.recommendation}")
        print()
    
    # 保存结果
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump({
            'code': result.code,
            'name': result.name,
            'risk_level': result.risk_level.value,
            'overall_score': result.overall_score,
            'anomalies': [
                {
                    'type': a.anomaly_type,
                    'severity': a.severity,
                    'description': a.description,
                    'recommendation': a.recommendation
                } for a in result.anomalies
            ]
        }, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 结果已保存到 {args.output}")


if __name__ == '__main__':
    main()
