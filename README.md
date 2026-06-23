# Fp-Testing
Crawler for testing websites fingerprinting

## Quickstart

```bash
python -m pip install -r requirements.txt
playwright install chromium
python -m fp_crawler.cli --config /abs/path/config.json --output /abs/path/results.jsonl --mode 3p_off
```

## Config (Pydantic)

```json
{
  "targets": [
    { "url": "https://example.com", "category": "news_politics" }
  ],
  "known_fingerprinting_domains": ["fingerprintjs.com"],
  "timeout_ms": 25000,
  "settle_wait_ms": 4000,
  "max_retries": 2
}
```

- `fp_crawler/playwright_program.py`: Live-Messung mit Monkey-Patching (Canvas + Audio API)
- `fp_crawler/historical_program.py`: Historische Heuristik per Domain-Matching
- `fp_crawler/models.py`: Definierte Output-Schnittstelle (JSONL)
- `fp_crawler/config.py`: Extra Config mit Pydantic und Type-Hints
