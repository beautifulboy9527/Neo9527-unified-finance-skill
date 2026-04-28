#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Evidence ledger for finance reports.

Every material data point should carry source, timestamp, quality, and whether it
is reported, estimated, or a model assumption. This keeps reports auditable.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict, List


SOURCE_RATINGS = {
    "sec.gov": "A",
    "annual report": "A",
    "exchange filing": "A",
    "akshare": "B",
    "eastmoney": "B",
    "sina finance": "B",
    "yfinance": "B",
    "yahoo finance": "B",
    "coingecko": "B",
    "defillama": "B",
    "model_default": "E",
    "unverified": "E",
}


@dataclass
class EvidenceItem:
    data_point: str
    value: Any
    source: str
    rating: str
    fetched_at: str
    as_of: str = ""
    field: str = ""
    unit: str = ""
    quality: str = "reported"
    verified: bool = True
    note: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)


class EvidenceLedger:
    """Collect and score evidence used by a report or model."""

    def __init__(self):
        self.items: List[EvidenceItem] = []

    def add(
        self,
        data_point: str,
        value: Any,
        source: str,
        *,
        as_of: str = "",
        field: str = "",
        unit: str = "",
        quality: str = "reported",
        verified: bool = True,
        note: str = "",
    ) -> Dict:
        rating = self.rate_source(source)
        item = EvidenceItem(
            data_point=data_point,
            value=value,
            source=source,
            rating=rating,
            fetched_at=datetime.now().isoformat(),
            as_of=as_of,
            field=field,
            unit=unit,
            quality=quality,
            verified=verified,
            note=note,
        )
        self.items.append(item)
        return item.to_dict()

    def add_assumption(
        self,
        data_point: str,
        value: Any,
        *,
        note: str,
        source: str = "model_default",
    ) -> Dict:
        return self.add(
            data_point,
            value,
            source,
            quality="assumption",
            verified=False,
            note=note,
        )

    def to_list(self) -> List[Dict]:
        return [item.to_dict() for item in self.items]

    def sources(self) -> List[str]:
        return sorted({item.source for item in self.items})

    def summary(self) -> Dict:
        ratings = [item.rating for item in self.items]
        unverified = [item for item in self.items if not item.verified]
        estimated = [item for item in self.items if item.quality in {"estimated", "assumption"}]
        return {
            "items": len(self.items),
            "sources": self.sources(),
            "ratings": {rating: ratings.count(rating) for rating in sorted(set(ratings))},
            "unverified_count": len(unverified),
            "estimated_count": len(estimated),
            "quality_score": self.quality_score(),
        }

    def quality_score(self) -> int:
        if not self.items:
            return 0

        rating_score = {
            "A": 100,
            "B": 85,
            "C": 65,
            "D": 40,
            "E": 20,
        }
        scores = []
        for item in self.items:
            item_score = rating_score.get(item.rating, 20)
            if not item.verified:
                item_score -= 15
            if item.quality == "estimated":
                item_score -= 8
            elif item.quality == "assumption":
                item_score -= 12
            scores.append(max(0, item_score))

        return int(round(sum(scores) / len(scores)))

    @staticmethod
    def rate_source(source: str) -> str:
        lowered = (source or "unknown").lower()
        for key, rating in SOURCE_RATINGS.items():
            if key in lowered:
                return rating
        return "E"
