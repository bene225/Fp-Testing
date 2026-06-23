from __future__ import annotations

from urllib.parse import urlparse

from .config import CrawlerConfig, SiteTarget, ThirdPartyCookieMode
from .models import CrawlResult


def analyze_historical_snapshot(
    target: SiteTarget,
    script_urls: list[str],
    config: CrawlerConfig,
) -> CrawlResult:
    """Heuristik-Programm: Domain-Matching gegen bekannte FP-Akteure."""

    known_domains = set(config.known_fingerprinting_domains)
    first_party_host = urlparse(str(target.url)).hostname or ""

    first_party_calls = 0
    third_party_calls = 0
    third_party_beacon_calls = 0

    for script_url in script_urls:
        host = urlparse(script_url).hostname or ""
        if not host:
            continue

        if host == first_party_host or host.endswith(f".{first_party_host}"):
            if host in known_domains:
                first_party_calls += 1
            continue

        if host in known_domains:
            third_party_calls += 1
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
