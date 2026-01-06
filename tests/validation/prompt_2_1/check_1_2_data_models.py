#!/usr/bin/env python3
"""Validate CIS data models"""

import inspect
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from configurator.security.cis_scanner import CheckResult, CISCheck, ScanReport, Severity, Status


def validate_data_models():
    """Validate CIS data model structures"""

    print("CIS Data Model Validation")
    print("=" * 60)

    # Check Severity enum
    assert hasattr(Severity, "CRITICAL"), "Missing CRITICAL severity"
    assert hasattr(Severity, "HIGH"), "Missing HIGH severity"
    assert hasattr(Severity, "MEDIUM"), "Missing MEDIUM severity"
    assert hasattr(Severity, "LOW"), "Missing LOW severity"
    print("✅ Severity enum complete (4 levels)")

    # Check Status enum
    assert hasattr(Status, "PASS"), "Missing PASS status"
    assert hasattr(Status, "FAIL"), "Missing FAIL status"
    assert hasattr(Status, "MANUAL"), "Missing MANUAL status"
    assert hasattr(Status, "NOT_APPLICABLE"), "Missing NOT_APPLICABLE status"
    assert hasattr(Status, "ERROR"), "Missing ERROR status"
    print("✅ Status enum complete (5 states)")

    # Check CISCheck dataclass
    check_fields = [f.name for f in inspect.signature(CISCheck).parameters.values()]
    required_fields = ["id", "title", "description", "rationale", "severity"]
    for field in required_fields:
        assert field in check_fields, f"CISCheck missing field: {field}"
    print(f"✅ CISCheck dataclass complete ({len(check_fields)} fields)")

    # Check CheckResult dataclass
    result_fields = [f.name for f in inspect.signature(CheckResult).parameters.values()]
    assert "check" in result_fields, "CheckResult missing 'check'"
    assert "status" in result_fields, "CheckResult missing 'status'"
    assert "message" in result_fields, "CheckResult missing 'message'"
    print(f"✅ CheckResult dataclass complete ({len(result_fields)} fields)")

    # Check ScanReport dataclass
    report_fields = [f.name for f in inspect.signature(ScanReport).parameters.values()]
    assert "results" in report_fields, "ScanReport missing 'results'"
    assert "score" in report_fields, "ScanReport missing 'score'"
    print(f"✅ ScanReport dataclass complete ({len(report_fields)} fields)")

    # Check method existence
    assert hasattr(CheckResult, "to_dict"), "CheckResult missing to_dict()"
    assert hasattr(ScanReport, "get_summary"), "ScanReport missing get_summary()"
    print("✅ Required methods present")

    print("=" * 60)
    print("✅ Data models validated")
    return True


if __name__ == "__main__":
    sys.exit(0 if validate_data_models() else 1)
