#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified Finance Skill - 配置管理
统一输出路径和配置
"""

import os
from pathlib import Path

# 输出目录配置；默认写到项目内，允许用环境变量覆盖。
OUTPUT_BASE = Path(
    os.getenv(
        'NEO_FINANCE_OUTPUT_DIR',
        Path(__file__).resolve().parents[1] / 'outputs'
    )
)
OUTPUT_DIR = OUTPUT_BASE

# 子目录
OUTPUT_DIRS = {
    'reports': OUTPUT_BASE / 'reports',
    'charts': OUTPUT_BASE / 'charts',
    'data': OUTPUT_BASE / 'data',
    'logs': OUTPUT_BASE / 'logs',
    'cache': OUTPUT_BASE / 'cache',
}

# 确保目录存在
def ensure_output_dirs():
    """确保所有输出目录存在"""
    for name, path in OUTPUT_DIRS.items():
        path.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIRS

# 获取输出路径
def get_output_path(filename: str, category: str = 'reports') -> Path:
    """
    获取输出文件路径
    
    Args:
        filename: 文件名
        category: 类别
        
    Returns:
        完整路径
    """
    ensure_output_dirs()
    return OUTPUT_DIRS[category] / filename

# 初始化
ensure_output_dirs()
