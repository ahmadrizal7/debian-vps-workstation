import os
import tempfile
import unittest
from pathlib import Path

from configurator.security.cis_report import CISReportGenerator
from configurator.security.cis_scanner import CheckResult, CISBenchmarkScanner, Status


class TestCISComplianceIntegration(unittest.TestCase):
    def setUp(self):
        self.scanner = CISBenchmarkScanner()

    def test_check_registration(self):
        """Verify that checks are registered correctly"""
        checks = self.scanner.checks
        self.assertGreater(len(checks), 100, "Should have more than 100 checks")

        categories = set(c.category for c in checks)
        expected = {
            "Initial Setup",
            "Services",
            "Network",
            "Logging",
            "Access Control",
            "System Maintenance",
        }
        self.assertTrue(expected.issubset(categories), f"Missing categories. Found: {categories}")

    def test_scan_execution(self):
        """Verify that scan runs and returns valid report"""
        report = self.scanner.scan(level=1)
        self.assertIsNotNone(report)
        self.assertEqual(len(report.results), len(self.scanner.checks))

        # Verify result structure
        for res in report.results:
            self.assertIsInstance(res, CheckResult)
            self.assertIsNotNone(res.check)
            self.assertIsInstance(res.status, Status)

        # Verify score
        summary = report.get_summary()
        self.assertIn("score", summary)
        self.assertTrue(0 <= summary["score"] <= 100)

    def test_reporting(self):
        """Verify report generation"""
        report = self.scanner.scan(level=1)

        with tempfile.TemporaryDirectory() as tmpdir:
            generator = CISReportGenerator(output_dir=tmpdir)

            # JSON
            json_path = generator.generate_json(report)
            self.assertTrue(os.path.exists(json_path))

            # HTML
            html_path = generator.generate_html(report)
            self.assertTrue(os.path.exists(html_path))
            content = Path(html_path).read_text()
            self.assertIn("CIS Debian Benchmark Scan Report", content)


if __name__ == "__main__":
    unittest.main()
