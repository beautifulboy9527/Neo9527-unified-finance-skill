import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from skills.shared import nl_intent_router
from skills.shared.nl_intent_router import route_query


def _reset_context():
    """Reset global router state between tests."""
    nl_intent_router._last_symbol = None


def test_routes_quick_stock_analysis():
    _reset_context()
    routed = route_query("帮我看下 AAPL")
    assert routed.intent == "quick_analyze"
    assert routed.argv == ["analyze", "AAPL"]
    assert routed.confidence > 0.7


def test_routes_strict_investor_report():
    _reset_context()
    routed = route_query("给我生成 002050 的正式研报")
    assert routed.intent == "report"
    assert routed.argv[:2] == ["report", "002050"]
    assert "--strict-data" in routed.argv
    assert "--enforce-freshness" in routed.argv


def test_routes_watchlist_add_with_targets():
    _reset_context()
    routed = route_query("把 002241 加到自选，目标 28，止损 18")
    assert routed.intent == "watchlist_add"
    assert routed.argv == [
        "watchlist", "add", "002241",
        "--target", "28", "--stop", "18",
    ]


def test_routes_portfolio_with_weights():
    _reset_context()
    routed = route_query("分析组合风险：600519 40%，002241 30%，000858 30%")
    assert routed.intent == "portfolio_analyze"
    assert routed.argv == [
        "portfolio", "warnings", "600519,002241,000858",
        "--weights", "0.4,0.3,0.3",
    ]


def test_routes_value_screening_with_technical_and_top_n():
    _reset_context()
    routed = route_query("筛选前10只价值股，要求金叉并按评分排序")
    assert routed.intent == "screen"
    assert routed.argv == [
        "screen", "--strategy", "value",
        "--technical", "golden-cross", "--scoring", "--top", "10",
    ]


def test_unknown_query_returns_guidance_without_command():
    _reset_context()
    routed = route_query("今天心情怎么样")
    assert routed.intent == "unknown"
    assert routed.argv == []
    assert routed.warnings


def test_context_continuation_uses_last_symbol():
    """After analyzing AAPL, '再看看估值' should continue with AAPL."""
    _reset_context()
    route_query("帮我看下 AAPL")
    routed = route_query("再看看估值")
    assert routed.intent == "valuation"
    assert "AAPL" in routed.argv
