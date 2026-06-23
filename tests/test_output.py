import unittest

from fp_crawler.models import CrawlResult, PhaseMetrics, PhaseName


class OutputTests(unittest.TestCase):
    def test_result_serialization(self):
        result = CrawlResult(
            url="https://example.com",
            category="shopping",
            third_party_mode="3p_off",
            status="ok",
            phases={PhaseName.BEFORE_BANNER: PhaseMetrics(canvas_calls=2, audio_calls=1)},
        )

        line = result.to_json_line()
        self.assertIn('"status":"ok"', line)
        self.assertIn('"before_banner"', line)


if __name__ == "__main__":
    unittest.main()
