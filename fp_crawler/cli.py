from __future__ import annotations

import argparse
import asyncio

from .config import ThirdPartyCookieMode, load_config
from .output import write_jsonl
from .playwright_program import run_live_crawl


def build_parser() -> argparse.ArgumentParser:
    """
    Erstellt den ArgumentParser für die CLI-Schnittstelle.
    Definiert die erwarteten Eingabeparameter (Config-Pfad, Output-Pfad, 3P-Cookie-Modus).
    """
    parser = argparse.ArgumentParser(description="Fingerprinting Crawler")
    parser.add_argument("--config", required=True, help="Pfad zur JSON/YAML Konfiguration")
    parser.add_argument("--output", required=True, help="Pfad zur JSONL Ausgabedatei")
    parser.add_argument(
        "--mode",
        choices=[ThirdPartyCookieMode.ON.value, ThirdPartyCookieMode.OFF.value],
        default=ThirdPartyCookieMode.OFF.value,
        help="Bestimmt, ob Third-Party-Cookies zugelassen werden oder nicht.",
    )
    return parser


def main() -> None:
    """
    Haupteinstiegspunkt des Skripts.
    Liest die Argumente ein, lädt die Pydantic-Konfiguration und startet
    den asynchronen Playwright-Crawl-Prozess (asyncio.run).
    Am Ende werden die Ergebnisse als JSONL-Datei geschrieben.
    """
    args = build_parser().parse_args()
    config = load_config(args.config)
    mode = ThirdPartyCookieMode(args.mode)
    
    # asyncio.run blockiert, bis alle asynchronen Crawl-Tasks abgeschlossen sind
    results = asyncio.run(run_live_crawl(config, mode))
    
    write_jsonl(results, args.output)


if __name__ == "__main__":
    main()
