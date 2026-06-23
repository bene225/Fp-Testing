import json
import tempfile
import unittest

from fp_crawler.config import CrawlerConfig, ThirdPartyCookieMode, load_config


class ConfigTests(unittest.TestCase):
    def test_load_json_config(self):
        payload = {
            "targets": [
                {"url": "https://example.com", "category": "news_politics"},
            ],
            "max_retries": 1,
        }

        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
            json.dump(payload, handle)
            temp_path = handle.name

        cfg = load_config(temp_path)
        self.assertIsInstance(cfg, CrawlerConfig)
        self.assertEqual(cfg.max_retries, 1)
        self.assertEqual(cfg.targets[0].category, "news_politics")
        self.assertEqual(ThirdPartyCookieMode.OFF.value, "3p_off")


if __name__ == "__main__":
    unittest.main()
