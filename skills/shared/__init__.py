#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""共享模块 - 统一导入入口"""

import importlib.util
from pathlib import Path

from .evidence import EvidenceItem, EvidenceLedger
from .localization import (
    MISSING_TEXT,
    normalize_report_text,
    safe_cn,
    stock_display_name,
    translate_action,
    translate_industry,
    translate_rating,
    translate_sector,
)
from .patterns import normalize_pattern_report
from .report_quality_gate import (
    ReportQualityIssue,
    assert_report_quality,
    issues_to_dicts,
    validate_chinese_report,
)


BASE_DIR = Path(__file__).resolve().parent


def _load_class(relative_path: str, module_name: str, class_name: str):
    path = BASE_DIR / relative_path
    if not path.exists():
        return None
    spec = importlib.util.spec_from_file_location(module_name, path)
    if not spec or not spec.loader:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, class_name, None)


CitationValidator = _load_class(
    "citation-validator/validator.py",
    "shared_citation_validator",
    "CitationValidator",
)
RiskMonitor = _load_class(
    "risk-monitor/monitor.py",
    "shared_risk_monitor",
    "RiskMonitor",
)

__all__ = [
    'CitationValidator',
    'RiskMonitor',
    'EvidenceItem',
    'EvidenceLedger',
    'MISSING_TEXT',
    'normalize_report_text',
    'normalize_pattern_report',
    'safe_cn',
    'stock_display_name',
    'translate_action',
    'translate_industry',
    'translate_rating',
    'translate_sector',
    'ReportQualityIssue',
    'assert_report_quality',
    'issues_to_dicts',
    'validate_chinese_report',
]
