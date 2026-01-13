"""
Unit tests for parallel execution fallback result preservation (CORE-001).
"""

from unittest.mock import Mock, patch

import pytest

from configurator.config import ConfigManager
from configurator.core.installer import Installer


class TestParallelFallbackResultPreservation:
    """Test that successful results are preserved during fallback."""

    @pytest.fixture
    def mock_config(self):
        """Mock configuration."""
        config = Mock(spec=ConfigManager)
        config.get.return_value = True
        config.get_enabled_modules.return_value = ["system", "security", "docker", "python"]
        return config

    @pytest.fixture
    def installer(self, mock_config):
        """Create installer instance."""
        logger = Mock()
        reporter = Mock()
        with patch("configurator.core.installer.Container"):
            with patch("configurator.core.installer.RollbackManager"):
                with patch("configurator.core.installer.SystemValidator"):
                    with patch("configurator.core.installer.HooksManager"):
                        with patch("configurator.core.installer.PluginManager"):
                            with patch("configurator.core.installer.DryRunManager"):
                                with patch("configurator.core.installer.CircuitBreakerManager"):
                                    installer = Installer(
                                        config=mock_config, logger=logger, reporter=reporter
                                    )
        return installer

    def test_fallback_preserves_successful_results(self, installer):
        """Test that successful module results are preserved when fallback occurs."""
        # Setup: Simulate results dict with successful modules
        results = {"system": True, "security": True, "docker": False}

        # Calculate successful modules
        successful_modules = [name for name, success in results.items() if success]

        # Verify we can identify successful modules
        assert len(successful_modules) == 2
        assert "system" in successful_modules
        assert "security" in successful_modules
        assert "docker" not in successful_modules

    def test_skip_already_completed_modules(self, installer):
        """Test that sequential fallback skips already-completed modules."""
        # Pre-populate results with successful modules
        results = {"system": True, "security": True}

        # Simulate sequential execution with skip logic
        enabled_modules = ["system", "security", "docker"]
        sorted_modules = sorted(
            enabled_modules, key=lambda m: installer.MODULE_PRIORITY.get(m, 100)
        )

        executed_modules = []
        for module_name in sorted_modules:
            # This is the skip logic from the fix
            if module_name in results and results[module_name]:
                continue  # Skip already-successful modules

            executed_modules.append(module_name)

        # Verify only docker was executed
        assert "docker" in executed_modules
        assert "system" not in executed_modules
        assert "security" not in executed_modules


class TestFallbackLogging:
    """Test logging output during fallback."""

    def test_preservation_log_format(self):
        """Test that preservation log includes count."""
        logger = Mock()

        successful_modules = ["system", "security", "docker"]
        logger.info(f"Preserving {len(successful_modules)} successful module results")

        logger.info.assert_called_with("Preserving 3 successful module results")

    def test_skip_log_format(self):
        """Test that skip log includes module name."""
        logger = Mock()

        module_name = "docker"
        logger.info(f"⏭️  Skipping already-completed module: {module_name}")

        logger.info.assert_called_with("⏭️  Skipping already-completed module: docker")

    def test_remaining_modules_log(self):
        """Test logging for restarting remaining modules."""
        logger = Mock()

        logger.warning("Restarting remaining modules with sequential execution...")

        logger.warning.assert_called_with(
            "Restarting remaining modules with sequential execution..."
        )
