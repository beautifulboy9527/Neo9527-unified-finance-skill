import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from skills.shared.sentiment_enhanced import SentimentAnalyzer


def test_sentiment_headline_fetch_does_not_fallback_to_synthetic_news(monkeypatch):
    class BrokenTicker:
        @property
        def news(self):
            raise RuntimeError("news unavailable")

    class FakeYFinance:
        @staticmethod
        def Ticker(symbol):
            return BrokenTicker()

    monkeypatch.setitem(sys.modules, "yfinance", FakeYFinance)

    analyzer = SentimentAnalyzer()
    assert analyzer._fetch_news_headlines("AAPL") == []


def test_sentiment_analyzer_returns_unknown_for_empty_input():
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze([])
    assert result["sentiment"] == "unknown"
    assert result["alignment"] == "insufficient_data"
