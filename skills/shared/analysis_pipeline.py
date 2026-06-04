#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全链路分析流水线 (Analysis Pipeline)

设计原则:
- 一次数据获取 → 多维度并行分析 → 统一输出
- 每个分析节点可独立禁用/启用
- 数据通过 DataLayer 统一缓存复用
- 分析结果可传递给 report 命令

Pipeline stages:
1. DataFetch    — DataLayer 统一获取行情+K线+财务数据
2. Fundamental  — 财务健康度分析
3. Valuation    — 三情景估值
4. Technical    — 技术分析 + 增强指标 (VWAP/Fibonacci/S-R/形态)
5. Signals      — 入场信号检测
6. Risk         — 风险预警 + 风控建议 (VaR/止损/仓位)
7. Evidence     — 数据溯源标记
8. Summary      — 综合结论生成
"""

from __future__ import annotations

import time
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class PipelineConfig:
    """Pipeline 配置"""
    stages: List[str] = field(default_factory=lambda: [
        "data", "fundamental", "valuation", "technical", "signals", "risk", "evidence", "summary"
    ])
    skip_stages: List[str] = field(default_factory=list)
    verbose: bool = True
    output_format: str = "terminal"  # terminal / dict / report_ready


@dataclass
class PipelineResult:
    """Pipeline 结果"""
    symbol: str = ""
    success: bool = False
    stages_completed: List[str] = field(default_factory=list)
    stages_failed: List[str] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)
    elapsed_seconds: float = 0.0
    summary: str = ""

    def to_report_data(self) -> Dict[str, Any]:
        """转换为 report 命令可直接使用的数据"""
        return {
            "financial_health": self.data.get("fundamental", {}),
            "valuation_workbench": self.data.get("valuation", {}),
            "risk_alerts": self.data.get("risk", {}),
            "technical_analysis": self.data.get("technical", {}),
            "fundamental_analysis": self.data.get("fundamental_fundamental", {}),
            "enhanced_technical": self.data.get("enhanced_technical", {}),
            "evidence_ledger": self.data.get("evidence", {}),
            "entry_signals": self.data.get("signals", {}),
            "risk_management": self.data.get("risk_management", {}),
            "data_sources": self.data.get("data_sources", {}),
        }


class AnalysisPipeline:
    """全链路分析流水线"""

    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or PipelineConfig()
        self._start_time = 0.0

    def _should_run(self, stage: str) -> bool:
        return stage in self.config.stages and stage not in self.config.skip_stages

    def _log(self, msg: str):
        if self.config.verbose:
            print(msg)

    def run(self, symbol: str, **kwargs) -> PipelineResult:
        """执行全链路分析"""
        result = PipelineResult(symbol=symbol)
        self._start_time = time.time()
        self._log(f"\n{'='*60}")
        self._log(f" Pipeline: 全链路分析 {symbol}")
        self._log(f"{'='*60}")

        # Stage 1: Data Fetch (统一数据层)
        if self._should_run("data"):
            try:
                data = self._fetch_data(symbol, **kwargs)
                result.data["collected_data"] = data
                result.data["data_sources"] = data.get("data_sources", {})
                result.stages_completed.append("data")
                self._log(f"  ✅ 数据获取完成 (来源: {data.get('sources', [])})")
            except Exception as e:
                result.stages_failed.append("data")
                self._log(f"  ❌ 数据获取失败: {e}")
                result.success = False
                result.summary = f"数据获取失败: {e}"
                result.elapsed_seconds = time.time() - self._start_time
                return result

        collected = result.data.get("collected_data", {})

        # Stage 2: Fundamental Analysis
        if self._should_run("fundamental"):
            try:
                health = self._analyze_fundamental(symbol, collected, **kwargs)
                result.data["fundamental"] = health
                result.stages_completed.append("fundamental")
                score = health.get("overall_score", "N/A")
                self._log(f"  ✅ 财务健康度: {score}")
            except Exception as e:
                result.stages_failed.append("fundamental")
                self._log(f"  ⚠️ 财务分析失败: {e}")

        # Stage 3: Valuation
        if self._should_run("valuation"):
            try:
                valuation = self._analyze_valuation(symbol, collected, **kwargs)
                result.data["valuation"] = valuation
                result.stages_completed.append("valuation")
                range_info = valuation.get("valuation_range", {})
                low = range_info.get("low", "N/A")
                high = range_info.get("high", "N/A")
                self._log(f"  ✅ 估值区间: {low} ~ {high}")
            except Exception as e:
                result.stages_failed.append("valuation")
                self._log(f"  ⚠️ 估值分析失败: {e}")

        # Stage 4: Technical + Enhanced
        if self._should_run("technical"):
            try:
                technical = self._analyze_technical(symbol, collected, **kwargs)
                result.data["technical"] = technical.get("basic", {})
                result.data["enhanced_technical"] = technical.get("enhanced", {})
                result.stages_completed.append("technical")
                trend = technical.get("basic", {}).get("trend", "N/A")
                self._log(f"  ✅ 技术分析: 趋势={trend}")
            except Exception as e:
                result.stages_failed.append("technical")
                self._log(f"  ⚠️ 技术分析失败: {e}")

        # Stage 5: Entry Signals
        if self._should_run("signals"):
            try:
                signals = self._analyze_signals(symbol, **kwargs)
                result.data["signals"] = signals
                result.stages_completed.append("signals")
                sig_count = len(signals.get("signals", []))
                self._log(f"  ✅ 入场信号: {sig_count} 个")
            except Exception as e:
                result.stages_failed.append("signals")
                self._log(f"  ⚠️ 信号分析失败: {e}")

        # Stage 6: Risk + Risk Management
        if self._should_run("risk"):
            try:
                risk_data = self._analyze_risk(symbol, collected, **kwargs)
                result.data["risk"] = risk_data.get("alerts", {})
                result.data["risk_management"] = risk_data.get("management", {})
                result.stages_completed.append("risk")
                severity = risk_data.get("alerts", {}).get("highest_severity_cn", "提示")
                self._log(f"  ✅ 风险等级: {severity}")
            except Exception as e:
                result.stages_failed.append("risk")
                self._log(f"  ⚠️ 风险分析失败: {e}")

        # Stage 7: Evidence
        if self._should_run("evidence"):
            try:
                evidence = self._build_evidence(symbol, result.data, collected)
                result.data["evidence"] = evidence
                result.stages_completed.append("evidence")
                self._log(f"  ✅ 数据溯源: {len(evidence.get('items', []))} 条")
            except Exception as e:
                result.stages_failed.append("evidence")
                self._log(f"  ⚠️ 溯源构建失败: {e}")

        # Stage 8: Summary
        if self._should_run("summary"):
            result.summary = self._generate_summary(result.data)
            result.stages_completed.append("summary")
            self._log(f"\n  📋 综合结论:")
            self._log(f"  {result.summary}")

        result.success = len(result.stages_failed) <= 1  # 允许1个阶段失败
        result.elapsed_seconds = time.time() - self._start_time

        self._log(f"\n  耗时: {result.elapsed_seconds:.1f}s | 完成: {len(result.stages_completed)}/{len(self.config.stages)}")
        self._log(f"{'='*60}\n")

        return result

    # ── Stage Implementations ──────────────────────────────────

    def _fetch_data(self, symbol: str, **kwargs) -> Dict:
        """统一数据获取"""
        import importlib.util, os
        SKILLS_DIR = kwargs.get("skills_dir", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        spec = importlib.util.spec_from_file_location(
            "stock_data_collector", os.path.join(SKILLS_DIR, "skills", "stock-skill", "stock_data_collector.py")
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        data = module.collect_stock_data(symbol)
        data["data_sources"] = {"collection": {"success": data.get("success", False), "sources": data.get("sources", [])}}
        return data

    def _analyze_fundamental(self, symbol: str, collected: Dict, **kwargs) -> Dict:
        """财务健康度分析"""
        import importlib.util, os
        SKILLS_DIR = kwargs.get("skills_dir", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        spec = importlib.util.spec_from_file_location(
            "financial_health", os.path.join(SKILLS_DIR, "skills", "stock-skill", "financial_health.py")
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        params = dict(collected.get("financial_fields", {}))
        params.update(kwargs.get("health_params", {}))
        return module.analyze_financial_health(symbol, **params)

    def _analyze_valuation(self, symbol: str, collected: Dict, **kwargs) -> Dict:
        """估值分析"""
        import importlib.util, os
        SKILLS_DIR = kwargs.get("skills_dir", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        spec = importlib.util.spec_from_file_location(
            "valuation_workbench", os.path.join(SKILLS_DIR, "skills", "stock-skill", "valuation_workbench.py")
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        params = dict(collected.get("valuation_fields", {}))
        params.update(kwargs.get("valuation_params", {}))
        return module.analyze_valuation_workbench(symbol, **params)

    def _analyze_technical(self, symbol: str, collected: Dict, **kwargs) -> Dict:
        """技术分析 + 增强指标"""
        import importlib.util, os
        SKILLS_DIR = kwargs.get("skills_dir", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        result = {"basic": {}, "enhanced": {}}

        # 基础技术分析
        basic = dict(collected.get("technical_analysis", {}))
        result["basic"] = basic

        # 增强技术指标
        try:
            ti_spec = importlib.util.spec_from_file_location(
                "technical_indicators", os.path.join(SKILLS_DIR, "skills", "shared", "technical_indicators.py")
            )
            ti_mod = importlib.util.module_from_spec(ti_spec)
            ti_spec.loader.exec_module(ti_mod)

            hist = basic.get("candles") or collected.get("market_data")
            if hist is not None:
                enhanced = {}
                for func_name, method in [("calculate_vwap", "vwap"), ("calculate_fibonacci_retracements", "fibonacci"), ("calculate_confluence_support_resistance", "support_resistance")]:
                    if hasattr(ti_mod, func_name):
                        try:
                            enhanced[method] = getattr(ti_mod, func_name)(hist)
                        except Exception:
                            enhanced[method] = None
                enhanced["patterns"] = basic.get("patterns", [])
                result["enhanced"] = enhanced
        except Exception as e:
            logger.debug(f"Enhanced technical failed: {e}")

        return result

    def _analyze_signals(self, symbol: str, **kwargs) -> Dict:
        """入场信号"""
        import importlib.util, os
        SKILLS_DIR = kwargs.get("skills_dir", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        spec = importlib.util.spec_from_file_location(
            "entry_signals", os.path.join(SKILLS_DIR, "skills", "stock-skill", "entry_signals.py")
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.analyze_entry_signals(symbol) or {}

    def _analyze_risk(self, symbol: str, collected: Dict, **kwargs) -> Dict:
        """风险预警 + 风控"""
        import importlib.util, os
        SKILLS_DIR = kwargs.get("skills_dir", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        result = {"alerts": {}, "management": {}}

        # 风险预警
        try:
            risk_spec = importlib.util.spec_from_file_location(
                "risk_alerts", os.path.join(SKILLS_DIR, "skills", "stock-skill", "risk_alerts.py")
            )
            risk_mod = importlib.util.module_from_spec(risk_spec)
            risk_spec.loader.exec_module(risk_mod)
            alerts_result = risk_mod.analyze_watchlist_alerts([symbol])
            result["alerts"] = alerts_result.get("items", [{}])[0] if alerts_result.get("items") else {}
        except Exception as e:
            logger.debug(f"Risk alerts failed: {e}")

        # 风控建议
        try:
            rm_spec = importlib.util.spec_from_file_location(
                "risk_management_pro", os.path.join(SKILLS_DIR, "skills", "stock-skill", "risk_management_pro.py")
            )
            rm_mod = importlib.util.module_from_spec(rm_spec)
            rm_spec.loader.exec_module(rm_mod)
            rm = rm_mod.RiskManagerPro()
            hist = collected.get("technical_analysis", {}).get("candles")
            if hist is not None:
                import pandas as pd
                if isinstance(hist, pd.DataFrame) and 'close' in hist.columns:
                    returns = hist['close'].pct_change().dropna()
                    if len(returns) > 20:
                        var_95 = rm.var_parametric(returns, confidence=0.95)
                        cvar = rm.cvar(returns, confidence=0.95)
                        result["management"] = {
                            "var": {"var_95": f"{var_95*100:.2f}", "cvar": f"{cvar*100:.2f}"},
                            "stop_loss": {},
                            "position_sizing": {},
                        }
        except Exception as e:
            logger.debug(f"Risk management failed: {e}")

        return result

    def _build_evidence(self, symbol: str, pipeline_data: Dict, collected: Dict) -> Dict:
        """数据溯源"""
        import importlib.util, os
        SKILLS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        try:
            ev_spec = importlib.util.spec_from_file_location(
                "evidence", os.path.join(SKILLS_DIR, "skills", "shared", "evidence.py")
            )
            ev_mod = importlib.util.module_from_spec(ev_spec)
            ev_spec.loader.exec_module(ev_mod)
            ledger = ev_mod.EvidenceLedger()

            # 标记数据来源
            for src in collected.get("sources", []):
                ledger.add(source=src, field="行情数据", grade="B", note="外部数据源")
            if collected.get("success"):
                ledger.add(source="实时接口", field="行情采集", grade="A", note="采集成功")

            # 标记各分析结果来源
            for stage_name in ["fundamental", "valuation", "technical", "signals", "risk"]:
                if stage_name in pipeline_data:
                    ledger.add(source=f"本地计算", field=f"{stage_name}分析", grade="B", note="基于采集数据计算")

            return {"items": ledger.to_list()}
        except Exception as e:
            logger.debug(f"Evidence failed: {e}")
            return {"items": []}

    def _generate_summary(self, data: Dict) -> str:
        """综合结论"""
        health = data.get("fundamental", {})
        valuation = data.get("valuation", {})
        risk = data.get("risk", {})
        signals = data.get("signals", {})

        parts = []

        # 财务结论
        score = health.get("overall_score", "N/A")
        if score != "N/A":
            try:
                s = float(score)
                if s >= 80:
                    parts.append("财务质量优秀")
                elif s >= 60:
                    parts.append("财务质量良好")
                elif s >= 40:
                    parts.append("财务质量一般")
                else:
                    parts.append("财务质量偏弱")
            except ValueError:
                parts.append(f"财务评分={score}")

        # 估值结论
        val_range = valuation.get("valuation_range", {})
        current = valuation.get("current_price")
        if val_range and current:
            low = val_range.get("low")
            high = val_range.get("high")
            if low and high:
                try:
                    if float(current) < float(low):
                        parts.append("估值偏低，可能存在安全边际")
                    elif float(current) > float(high):
                        parts.append("估值偏高，需谨慎")
                    else:
                        parts.append("估值处于合理区间")
                except ValueError:
                    pass

        # 风险结论
        severity = risk.get("highest_severity_cn", "提示")
        if severity != "提示":
            parts.append(f"风险等级={severity}")

        # 信号结论
        sig_score = signals.get("overall_score")
        if sig_score:
            parts.append(f"入场信号评分={sig_score}")

        return "；".join(parts) if parts else "分析数据不完整，无法生成综合结论"


__all__ = ["AnalysisPipeline", "PipelineConfig", "PipelineResult"]
