from __future__ import annotations

from pathlib import Path

from .models import CrawlResult


def write_jsonl(results: list[CrawlResult], output_path: str | Path) -> None:
    """Definierte Output-Schnittstelle: JSONL für spätere DB-Pipelines."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for result in results:
            handle.write(result.to_json_line())
            handle.write("\n")
