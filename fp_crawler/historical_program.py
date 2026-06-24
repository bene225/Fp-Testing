from __future__ import annotations

from urllib.parse import urlparse

from config import CrawlerConfig, SiteTarget, ThirdPartyCookieMode
from models import CrawlResult


def analyze_historical_snapshot(
    target: SiteTarget,
    script_urls: list[str],
    config: CrawlerConfig,
) -> CrawlResult:
    """
    Heuristik-Programm: Domain-Matching gegen bekannte FP-Akteure.
    Dieses Modul arbeitet nicht live im Browser, sondern analysiert statische Listen
    von Skript-URLs (historische Daten) anhand von bekannten Fingerprinting-Domains.
    """
    
    # Set-Datenstruktur für O(1) Lookups (schnelles Auffinden)
    known_domains = set(config.known_fingerprinting_domains)
    first_party_host = urlparse(str(target.url)).hostname or ""

    first_party_calls = 0
    third_party_calls = 0
    third_party_beacon_calls = 0

    # Iteriere über alle geladenen Skripte der untersuchten Seite
    for script_url in script_urls:
        host = urlparse(script_url).hostname or ""
        if not host:
            continue

        # Prüfe, ob das Skript vom selben Host oder einer Subdomain des Haupt-Hosts stammt
        if host == first_party_host or host.endswith(f".{first_party_host}"):
            if host in known_domains:
                first_party_calls += 1
            continue

        # Wenn es eine fremde Domain (Third-Party) ist
        if host in known_domains:
            third_party_calls += 1
            
            # Simple Heuristik: "beacon" oder "collect" weisen oft auf Tracking-Endpoints hin
            if "beacon" in script_url or "collect" in script_url:
                third_party_beacon_calls += 1

    return CrawlResult(
        url=target.url,
        category=target.category,
        third_party_mode=ThirdPartyCookieMode.ON.value,
        status="ok",
        first_party_calls=first_party_calls,
        third_party_calls=third_party_calls,
        third_party_beacon_calls=third_party_beacon_calls,
    )
