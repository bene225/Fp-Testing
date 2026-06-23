from __future__ import annotations

import asyncio
from collections.abc import Callable
from urllib.parse import urlparse

from .config import CrawlerConfig, SiteTarget, ThirdPartyCookieMode
from .models import CrawlResult, PhaseMetrics, PhaseName


MONKEY_PATCH_SCRIPT = """
(() => {
  const counter = {
    before_banner: { canvas_calls: 0, audio_calls: 0 },
    after_accept: { canvas_calls: 0, audio_calls: 0 },
    after_reject: { canvas_calls: 0, audio_calls: 0 },
    phase: 'before_banner'
  };

  const bumpCanvas = () => { counter[counter.phase].canvas_calls += 1; };
  const bumpAudio = () => { counter[counter.phase].audio_calls += 1; };

  const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;
  CanvasRenderingContext2D.prototype.getImageData = function(...args) {
    bumpCanvas();
    return originalGetImageData.apply(this, args);
  };

  const originalCreateAnalyser = AudioContext.prototype.createAnalyser;
  AudioContext.prototype.createAnalyser = function(...args) {
    bumpAudio();
    return originalCreateAnalyser.apply(this, args);
  };

  window.__fpCounter = counter;
})();
"""


async def _set_phase(page, phase: PhaseName) -> None:
    await page.evaluate("phase => { window.__fpCounter.phase = phase; }", phase.value)


async def _read_phase(page, phase: PhaseName) -> PhaseMetrics:
    data = await page.evaluate(
        "phase => window.__fpCounter?.[phase] ?? { canvas_calls: 0, audio_calls: 0 }",
        phase.value,
    )
    return PhaseMetrics(**data)


async def _click_first_visible(page, selectors: list[str]) -> bool:
    for selector in selectors:
        element = page.locator(selector).first
        if await element.count() > 0:
            await element.click(timeout=2_500)
            return True
    return False


def _is_third_party(request_url: str, first_party_host: str) -> bool:
    req_host = urlparse(request_url).hostname or ""
    return bool(req_host and req_host != first_party_host and not req_host.endswith(f".{first_party_host}"))


async def _install_third_party_cookie_blocking(context, first_party_host: str) -> None:
    """Best effort: blockiert 3P Cookie Header und Set-Cookie Antworten."""

    async def route_handler(route, request):
        headers = dict(request.headers)
        if _is_third_party(request.url, first_party_host):
            headers.pop("cookie", None)
            upstream = await route.fetch(headers=headers)
            resp_headers = dict(upstream.headers)
            resp_headers.pop("set-cookie", None)
            await route.fulfill(
                status=upstream.status,
                headers=resp_headers,
                body=await upstream.body(),
            )
            return
        await route.continue_(headers=headers)

    await context.route("**/*", route_handler)


async def crawl_target(target: SiteTarget, config: CrawlerConfig, mode: ThirdPartyCookieMode) -> CrawlResult:
    """Live-Crawler mit Playwright und drei Messphasen."""

    first_party_host = urlparse(str(target.url)).hostname or ""
    for attempt in range(config.max_retries + 1):
        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as pw:
                browser = await pw.chromium.launch(headless=config.headless)
                context = await browser.new_context(
                    user_agent=config.user_agent,
                    ignore_https_errors=True,
                )
                if mode == ThirdPartyCookieMode.OFF:
                    await _install_third_party_cookie_blocking(context, first_party_host)

                page = await context.new_page()
                await page.add_init_script(MONKEY_PATCH_SCRIPT)
                await page.goto(str(target.url), wait_until="domcontentloaded", timeout=config.timeout_ms)

                await asyncio.sleep(config.settle_wait_ms / 1000)
                await _set_phase(page, PhaseName.BEFORE_BANNER)
                before = await _read_phase(page, PhaseName.BEFORE_BANNER)

                await _set_phase(page, PhaseName.AFTER_ACCEPT)
                await _click_first_visible(page, config.accept_selectors)
                await asyncio.sleep(config.settle_wait_ms / 1000)
                after_accept = await _read_phase(page, PhaseName.AFTER_ACCEPT)

                await _set_phase(page, PhaseName.AFTER_REJECT)
                await _click_first_visible(page, config.reject_selectors)
                await asyncio.sleep(config.settle_wait_ms / 1000)
                after_reject = await _read_phase(page, PhaseName.AFTER_REJECT)

                await context.close()
                await browser.close()

                return CrawlResult(
                    url=target.url,
                    category=target.category,
                    third_party_mode=mode.value,
                    status="ok",
                    phases={
                        PhaseName.BEFORE_BANNER: before,
                        PhaseName.AFTER_ACCEPT: after_accept,
                        PhaseName.AFTER_REJECT: after_reject,
                    },
                )
        except Exception as exc:  # noqa: BLE001
            if attempt >= config.max_retries:
                return CrawlResult(
                    url=target.url,
                    category=target.category,
                    third_party_mode=mode.value,
                    status="failed",
                    error=str(exc),
                )
            await asyncio.sleep(1 + attempt)

    return CrawlResult(
        url=target.url,
        category=target.category,
        third_party_mode=mode.value,
        status="failed",
        error="unknown crawler state",
    )


async def run_live_crawl(config: CrawlerConfig, mode: ThirdPartyCookieMode) -> list[CrawlResult]:
    """Getrenntes Playwright-Programm für Live-Messungen."""

    tasks: list[Callable[[], asyncio.Future[CrawlResult]]] = []
    for target in config.targets:
        tasks.append(lambda t=target: crawl_target(t, config, mode))
    return await asyncio.gather(*(task() for task in tasks))
