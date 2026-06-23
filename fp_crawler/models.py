from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, HttpUrl


class PhaseName(str, Enum):
    """Zeitlich getrennte Messphasen für die Forschungsfragen."""

    BEFORE_BANNER = "before_banner"
    AFTER_ACCEPT = "after_accept"
    AFTER_REJECT = "after_reject"


class PhaseMetrics(BaseModel):
    """Anzahl der Fingerprinting-Aufrufe pro API in einer Phase."""

    canvas_calls: int = 0
    audio_calls: int = 0


class CrawlResult(BaseModel):
    """Stabiles Output-Schema für DB-Import oder JSONL-Export."""

    url: HttpUrl
    category: str
    third_party_mode: str
    status: str
    first_party_calls: int = 0
    third_party_calls: int = 0
    third_party_beacon_calls: int = 0
    phases: dict[PhaseName, PhaseMetrics] = Field(default_factory=dict)
    error: str | None = None

    def to_json_line(self) -> str:
        """Schnittstelle: genau eine JSON-Zeile pro Ergebnis."""

        return self.model_dump_json()
