#!/usr/bin/env python3
"""Test report generation"""

import json
import os
import sys
import tempfile
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from configurator.security.cis_report import CISReportGenerator
from configurator.security.cis_scanner import CISBenchmarkScanner


def test_report_generation():
    print("Report Generation Validation")
    print("=" * 60)

    scanner = CISBenchmarkScanner()
    report = scanner.scan(level=1)

    with tempfile.TemporaryDirectory() as tmpdir:
        generator = CISReportGenerator(output_dir=tmpdir)

        # Test JSON
        try:
            json_path = generator.generate_json(report)
            print(f"✅ JSON report generated: {json_path}")

            with open(json_path) as f:
                data = json.load(f)
                if data["total_checks"] > 100:
                    print("   ✅ JSON content sufficient (>100 checks)")
                else:
                    print("   ❌ JSON content missing checks")
                    return False
        except Exception as e:
            print(f"❌ JSON report generation failed: {e}")
            return False

        # Test HTML
        try:
            html_path = generator.generate_html(report)
            print(f"✅ HTML report generated: {html_path}")

            content = Path(html_path).read_text()
            if "CIS Debian Benchmark Scan Report" in content and "Compliance Score" in content:
                print("   ✅ HTML content contains header and score")
            else:
                print("   ❌ HTML content missing key elements")
                return False

            if "CRITICAL" in content:
                print("   ✅ HTML content shows severity levels")
            else:
                print("   ⚠️ HTML content missing CRITICAL text (might be if no criticals failed?)")
                if "Failed" in content:
                    print("   ✅ HTML content shows failures")
        except Exception as e:
            print(f"❌ HTML report generation failed: {e}")
            return False

    print("\n" + "=" * 60)
    print("✅ Reports validated")
    return True


if __name__ == "__main__":
    sys.exit(0 if test_report_generation() else 1)
