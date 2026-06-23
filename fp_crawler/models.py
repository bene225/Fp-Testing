from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, HttpUrl


class PhaseName(str, Enum):
    """
    Zeitlich getrennte Messphasen für die Forschungsfragen.
    Repräsentiert die drei Hauptzustände einer besuchten Webseite:
    Vor dem Banner, nach der Zustimmung (Accept) und nach der Ablehnung (Reject).
    """

    BEFORE_BANNER = "before_banner"
    AFTER_ACCEPT = "after_accept"
    AFTER_REJECT = "after_reject"


class PhaseMetrics(BaseModel):
    """
    Anzahl der Fingerprinting-Aufrufe pro API in einer Phase.
    Nutzt Pydantic für Typsicherheit bei den gesammelten Daten.
    """

    canvas_calls: int = 0
    audio_calls: int = 0


class CrawlResult(BaseModel):
    """
    Stabiles Output-Schema für DB-Import oder JSONL-Export.
    Die Verwendung von Pydantic garantiert, dass alle erforderlichen
    Felder mit den korrekten Datentypen vorhanden sind, bevor sie exportiert werden.
    """

    url: HttpUrl
    category: str
    third_party_mode: str
    status: str
    first_party_calls: int = 0
    third_party_calls: int = 0
    third_party_beacon_calls: int = 0
    # Speichert die Metriken zu jeder Phase als Dictionary
    phases: dict[PhaseName, PhaseMetrics] = Field(default_factory=dict)
    error: str | None = None

    def to_json_line(self) -> str:
        """
        Schnittstelle: genau eine JSON-Zeile pro Ergebnis.
        Verwendet Pydantics model_dump_json(), um das Schema sicher
        und ohne Zeilenumbrüche zu serialisieren. Ideal für JSONL.
        """
        return self.model_dump_json()
