from scripts.features.simple_backtest import simple_backtest_validation
from scripts.features.sentiment_enhanced import SentimentAnalyzer


def test_simple_backtest_marks_rule_hits_as_unverified():
    result = simple_backtest_validation(
        {"macd_status": "金叉", "rsi": 75, "trend": "强势多头"},
        "AAPL",
    )

    assert result
    assert all(item["verified"] is False for item in result)
    assert all(item["win_rate"] is None for item in result)
    assert all(item["sample_size"] == 0 for item in result)


def test_sentiment_headline_fetch_does_not_fallback_to_synthetic_news(monkeypatch):
    class BrokenTicker:
        @property
        def news(self):
            raise RuntimeError("news unavailable")

    class FakeYFinance:
        @staticmethod
        def Ticker(symbol):
            return BrokenTicker()

    import sys

    monkeypatch.setitem(sys.modules, "yfinance", FakeYFinance)

    analyzer = SentimentAnalyzer()
    assert analyzer._fetch_news_headlines("AAPL") == []
