from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class ThirdPartyCookieMode(str, Enum):
    """Modus für den Browser: 3P-Cookies erlaubt oder blockiert."""

    ON = "3p_on"
    OFF = "3p_off"


class SiteTarget(BaseModel):
    """Ein einzelnes Crawl-Ziel mit URL und Kategorie."""

    url: HttpUrl
    category: Literal["news_politics", "shopping", "functional_control"]


class CrawlerConfig(BaseModel):
    """Zentrale Pydantic-Konfiguration für stabile Crawling-Läufe."""

    targets: list[SiteTarget] = Field(default_factory=list)
    headless: bool = True
    timeout_ms: int = 25_000
    settle_wait_ms: int = 4_000
    max_retries: int = 2
    user_agent: str = (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    )
    accept_selectors: list[str] = Field(
        default_factory=lambda: [
            "button:has-text('Akzeptieren')",
            "button:has-text('Accept all')",
            "#onetrust-accept-btn-handler",
        ]
    )
    reject_selectors: list[str] = Field(
        default_factory=lambda: [
            "button:has-text('Ablehnen')",
            "button:has-text('Reject all')",
            "#onetrust-reject-all-handler",
        ]
    )
    known_fingerprinting_domains: list[str] = Field(default_factory=list)

    @classmethod
    def from_json_file(cls, path: str | Path) -> "CrawlerConfig":
        """Lädt die Konfiguration aus einer JSON-Datei."""

        raw = Path(path).read_text(encoding="utf-8")
        return cls.model_validate_json(raw)

    @classmethod
    def from_yaml_file(cls, path: str | Path) -> "CrawlerConfig":
        """Optionales YAML-Loading für bequemes Studiendesign."""

        try:
            import yaml  # type: ignore
        except ImportError as exc:
            raise RuntimeError("YAML-Support benötigt 'pyyaml'.") from exc

        parsed = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        return cls.model_validate(parsed)


def load_config(path: str | Path) -> CrawlerConfig:
    """Einheitliche Ladefunktion für .json und .yaml/.yml."""

    suffix = Path(path).suffix.lower()
    if suffix == ".json":
        return CrawlerConfig.from_json_file(path)
    if suffix in {".yaml", ".yml"}:
        return CrawlerConfig.from_yaml_file(path)
    raise ValueError("Unsupported config format. Use JSON or YAML.")
