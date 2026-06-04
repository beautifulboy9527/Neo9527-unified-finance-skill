#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能行业/板块翻译器 v1.0
自动翻译英文行业/板块名称为中文
"""

# 常见行业中文翻译映射（通用）
INDUSTRY_TRANSLATIONS = {
    # 科技
    'Technology': '科技',
    'Software': '软件',
    'Semiconductors': '半导体',
    'Semiconductor Equipment & Materials': '半导体设备与材料',
    'Electronic Components': '电子元件',
    'Consumer Electronics': '消费电子',
    'Communication Equipment': '通信设备',
    
    # 工业制造
    'Industrials': '工业',
    'Machinery': '机械',
    'Farm & Heavy Construction Machinery': '工程机械',
    'Construction Machinery': '工程机械',
    'Electrical Equipment & Parts': '电气设备',
    'Industrial Machinery': '工业机械',
    'Auto Components': '汽车零部件',
    'Aerospace & Defense': '航空航天',
    
    # 能源
    'Energy': '能源',
    'Oil & Gas': '石油天然气',
    'Oil & Gas E&P': '油气勘探',
    'Oil & Gas Refining & Marketing': '油气炼化',
    'Renewable Energy': '可再生能源',
    'Solar': '太阳能',
    
    # 材料
    'Basic Materials': '基础材料',
    'Chemicals': '化工',
    'Specialty Chemicals': '特种化工',
    'Building Materials': '建材',
    'Steel': '钢铁',
    'Metals & Mining': '金属采矿',
    
    # 金融
    'Financial Services': '金融服务',
    'Banks': '银行',
    'Insurance': '保险',
    'Asset Management': '资产管理',
    'Capital Markets': '资本市场',
    
    # 医疗
    'Healthcare': '医疗健康',
    'Biotechnology': '生物技术',
    'Drug Manufacturers': '制药',
    'Medical Devices': '医疗器械',
    'Diagnostics & Research': '诊断与研究',
    
    # 消费
    'Consumer Cyclical': '可选消费',
    'Consumer Defensive': '必选消费',
    'Retail': '零售',
    'E-commerce': '电商',
    'Apparel Stores': '服装零售',
    'Luxury Goods': '奢侈品',
    'Restaurants': '餐饮',
    
    # 家电
    'Furnishings, Fixtures & Appliances': '家具家电',
    'Household Durables': '耐用消费品',
    'Consumer Electronics': '消费电子',
    
    # 地产
    'Real Estate': '房地产',
    'Real Estate Development': '房地产开发',
    'REITs': '房地产信托',
    
    # 公用事业
    'Utilities': '公用事业',
    'Utilities - Regulated': '公用事业（管制）',
    'Utilities - Renewable': '公用事业（新能源）',
    
    # 通信
    'Communication Services': '通信服务',
    'Telecom Services': '电信服务',
    'Internet Content & Information': '互联网信息',
    
    # 其他
    'Agriculture': '农业',
    'Leisure Products': '休闲用品',
    'Business Services': '商业服务',
    'Education': '教育',
    'Transportation': '交通运输',
    'Logistics': '物流',
}

# 板块中文翻译映射
SECTOR_TRANSLATIONS = {
    'Technology': '科技板块',
    'Financial Services': '金融板块',
    'Healthcare': '医疗板块',
    'Consumer Cyclical': '消费板块',
    'Energy': '能源板块',
    'Industrials': '工业板块',
    'Basic Materials': '基础材料板块',
    'Real Estate': '房地产板块',
    'Utilities': '公用事业板块',
    'Communication Services': '通信板块',
    'Consumer Defensive': '消费防御板块',
}

def translate_industry(industry_en: str) -> str:
    """翻译行业名称为中文"""
    if not industry_en:
        return '未知'
    
    # 1. 直接匹配
    if industry_en in INDUSTRY_TRANSLATIONS:
        return INDUSTRY_TRANSLATIONS[industry_en]
    
    # 2. 包含匹配（处理复合词）
    for en, cn in INDUSTRY_TRANSLATIONS.items():
        if en.lower() in industry_en.lower():
            return cn
    
    # 3. 如果已经是中文，直接返回
    if not industry_en.isascii():
        return industry_en
    
    # 4. 返回原文
    return industry_en

def translate_sector(sector_en: str) -> str:
    """翻译板块名称为中文"""
    if not sector_en:
        return '未知'
    
    # 1. 直接匹配
    if sector_en in SECTOR_TRANSLATIONS:
        return SECTOR_TRANSLATIONS[sector_en]
    
    # 2. 移除"板块"后缀再匹配
    base_sector = sector_en.replace('板块', '').strip()
    if base_sector in SECTOR_TRANSLATIONS:
        return SECTOR_TRANSLATIONS[base_sector]
    
    # 3. 如果已经是中文，直接返回
    if not sector_en.isascii():
        return sector_en
    
    # 4. 返回原文
    return sector_en

# 使用示例
if __name__ == '__main__':
    # 测试翻译
    test_cases = [
        'Technology',
        'Semiconductors',
        'Farm & Heavy Construction Machinery',
        'Electrical Equipment & Parts',
        'Industrials',
        'Healthcare',
        'Biotechnology',
        'Oil & Gas',
        'Consumer Cyclical',
    ]
    
    print("行业翻译测试:")
    for industry in test_cases:
        print(f"{industry:40s} → {translate_industry(industry)}")
    
    print("\n板块翻译测试:")
    for sector in ['Technology', 'Healthcare', 'Industrials', 'Financial Services']:
        print(f"{sector:30s} → {translate_sector(sector)}")
