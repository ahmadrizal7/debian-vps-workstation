"""
Integration test for full validation flow.

Tests the complete validation system from orchestrator through all tiers.
"""

from unittest.mock import Mock, patch

import pytest

from configurator.validators.base import ValidationSeverity
from configurator.validators.orchestrator import ValidationOrchestrator
from configurator.validators.tier1_critical.os_version import OSVersionValidator
from configurator.validators.tier1_critical.python_version import PythonVersionValidator
from configurator.validators.tier1_critical.root_access import RootAccessValidator
from configurator.validators.tier2_high.disk_space import DiskSpaceValidator
from configurator.validators.tier2_high.network import NetworkValidator
from configurator.validators.tier2_high.ram import RAMValidator
from configurator.validators.tier3_medium.dns import DNSValidator
from configurator.validators.tier3_medium.recommended_ram import RecommendedRAMValidator


@pytest.fixture
def mock_system_checks():
    """Mock all system checks to pass."""
    with (
        patch("configurator.validators.tier1_critical.os_version.get_os_info") as mock_os,
        patch("configurator.validators.tier1_critical.root_access.os.geteuid") as mock_root,
        patch("configurator.validators.tier2_high.ram.psutil.virtual_memory") as mock_ram,
        patch("configurator.validators.tier2_high.disk_space.shutil.disk_usage") as mock_disk,
        patch("configurator.validators.tier2_high.network.socket.socket") as mock_socket,
        patch(
            "configurator.validators.tier3_medium.recommended_ram.psutil.virtual_memory"
        ) as mock_rec_ram,
        patch("configurator.validators.tier3_medium.dns.socket.gethostbyname") as mock_dns,
    ):
        # Configure mocks for passing validation
        os_info = Mock()
        os_info.name = "debian"
        os_info.id = "debian"
        os_info.version_id = "13"
        os_info.pretty_name = "Debian 13 (Trixie)"
        mock_os.return_value = os_info

        mock_root.return_value = 0  # Root user

        # 8GB RAM
        mock_ram.return_value = Mock(total=8 * 1024**3)
        mock_rec_ram.return_value = Mock(total=8 * 1024**3)

        # 50GB disk
        mock_disk.return_value = Mock(free=50 * 1024**3)

        # Network connectivity
        mock_sock_instance = Mock()
        mock_sock_instance.connect_ex.return_value = 0
        mock_socket.return_value = mock_sock_instance

        # DNS resolution
        mock_dns.return_value = "1.2.3.4"

        yield


class TestValidationFlowIntegration:
    """Integration tests for complete validation flow."""

    def test_full_validation_all_pass(self, mock_system_checks):
        """Test complete validation when all checks pass."""
        orchestrator = ValidationOrchestrator()

        # Register all validators
        # Tier 1: Critical
        orchestrator.register_validator(1, OSVersionValidator())
        orchestrator.register_validator(1, PythonVersionValidator())
        orchestrator.register_validator(1, RootAccessValidator())

        # Tier 2: High
        orchestrator.register_validator(2, RAMValidator())
        orchestrator.register_validator(2, DiskSpaceValidator())
        orchestrator.register_validator(2, NetworkValidator())

        # Tier 3: Medium
        orchestrator.register_validator(3, RecommendedRAMValidator())
        orchestrator.register_validator(3, DNSValidator())

        # Run validation
        passed, results = orchestrator.run_validation(interactive=False, auto_fix=False)

        # Verify results
        assert passed is True
        assert len(results) == 8

        # All critical should pass
        critical_results = [r for r in results if r.severity == ValidationSeverity.CRITICAL]
        assert all(r.passed for r in critical_results)

        # All high should pass
        high_results = [r for r in results if r.severity == ValidationSeverity.HIGH]
        assert all(r.passed for r in high_results)

        # All medium should pass
        medium_results = [r for r in results if r.severity == ValidationSeverity.MEDIUM]
        assert all(r.passed for r in medium_results)

    @patch("configurator.validators.tier1_critical.os_version.get_os_info")
    def test_validation_stops_on_critical_failure(self, mock_os):
        """Test validation stops when critical validator fails."""
        # Mock unsupported OS
        os_info = Mock()
        os_info.name = "fedora"
        os_info.id = "fedora"
        os_info.version_id = "39"
        os_info.pretty_name = "Fedora 39"
        mock_os.return_value = os_info

        orchestrator = ValidationOrchestrator()

        # Register validators
        orchestrator.register_validator(1, OSVersionValidator())
        orchestrator.register_validator(2, RAMValidator())

        # Run validation
        passed, results = orchestrator.run_validation(interactive=False)

        # Should fail and not run tier 2
        assert passed is False
        assert len(results) == 1  # Only tier 1 ran
        assert results[0].severity == ValidationSeverity.CRITICAL
        assert results[0].passed is False

    @patch("configurator.validators.tier2_high.ram.psutil.virtual_memory")
    @patch("configurator.validators.tier1_critical.os_version.get_os_info")
    @patch("configurator.validators.tier1_critical.root_access.os.geteuid")
    def test_high_priority_warning_doesnt_stop(self, mock_root, mock_os, mock_ram):
        """Test high priority warnings don't stop installation."""
        # Mock passing critical
        os_info = Mock()
        os_info.name = "debian"
        os_info.id = "debian"
        os_info.version_id = "13"
        os_info.pretty_name = "Debian 13"
        mock_os.return_value = os_info

        mock_root.return_value = 0

        # Mock insufficient RAM (high priority)
        mock_ram.return_value = Mock(total=2 * 1024**3)  # 2GB

        orchestrator = ValidationOrchestrator()

        orchestrator.register_validator(1, OSVersionValidator())
        orchestrator.register_validator(1, RootAccessValidator())
        orchestrator.register_validator(2, RAMValidator())

        passed, results = orchestrator.run_validation(interactive=False)

        # All tiers should run
        assert len(results) == 3

        # Critical passes
        critical_results = [r for r in results if r.severity == ValidationSeverity.CRITICAL]
        assert all(r.passed for r in critical_results)

        # RAM fails but doesn't stop
        ram_result = next(r for r in results if "RAM" in r.validator_name)
        assert ram_result.passed is False

    @patch("configurator.validators.tier3_medium.recommended_ram.psutil.virtual_memory")
    @patch("configurator.validators.tier1_critical.os_version.get_os_info")
    @patch("configurator.validators.tier1_critical.root_access.os.geteuid")
    def test_medium_priority_failure_allows_installation(self, mock_root, mock_os, mock_ram):
        """Test medium priority failures allow installation to continue."""
        # Mock passing critical
        os_info = Mock()
        os_info.name = "debian"
        os_info.id = "debian"
        os_info.version_id = "13"
        os_info.pretty_name = "Debian 13"
        mock_os.return_value = os_info

        mock_root.return_value = 0

        # Mock RAM that meets minimum but not recommended
        mock_ram.return_value = Mock(total=4 * 1024**3)  # 4GB (minimum but not recommended 8GB)

        orchestrator = ValidationOrchestrator()

        orchestrator.register_validator(1, OSVersionValidator())
        orchestrator.register_validator(3, RecommendedRAMValidator())

        passed, results = orchestrator.run_validation(interactive=False)

        # Should pass overall
        assert passed is True

        # Medium priority should fail but not affect overall
        medium_result = next(r for r in results if r.severity == ValidationSeverity.MEDIUM)
        assert medium_result.passed is False

    def test_tier_execution_order(self, mock_system_checks):
        """Test validators run in correct tier order."""
        orchestrator = ValidationOrchestrator()

        execution_order = []

        class OrderTrackingValidator:
            """Validator that tracks execution order."""

            def __init__(self, name, tier):
                self.name = name
                self.tier = tier
                self.severity = ValidationSeverity.HIGH

            def validate(self):
                execution_order.append(f"tier{self.tier}_{self.name}")
                from configurator.validators.base import ValidationResult

                return ValidationResult(
                    validator_name=self.name,
                    severity=self.severity,
                    passed=True,
                    message="OK",
                )

        # Register validators out of order
        orchestrator.register_validator(3, OrderTrackingValidator("medium", 3))
        orchestrator.register_validator(1, OrderTrackingValidator("critical", 1))
        orchestrator.register_validator(2, OrderTrackingValidator("high", 2))

        orchestrator.run_validation(interactive=False)

        # Verify execution order: tier 1, then tier 2, then tier 3
        assert execution_order == ["tier1_critical", "tier2_high", "tier3_medium"]
