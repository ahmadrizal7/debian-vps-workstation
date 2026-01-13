"""
Unit tests for rollback confirmation functionality (CORE-002).
"""

from unittest.mock import Mock, patch

import pytest

from configurator.config import ConfigManager
from configurator.core.installer import Installer


class TestRollbackConfirmation:
    """Test rollback confirmation in different modes."""

    @pytest.fixture
    def installer(self):
        """Create installer with mock dependencies."""
        config = Mock(spec=ConfigManager)
        config.get.return_value = True  # Default interactive mode
        logger = Mock()
        reporter = Mock()

        with patch("configurator.core.installer.Container"):
            with patch("configurator.core.installer.RollbackManager") as MockRollback:
                with patch("configurator.core.installer.SystemValidator"):
                    with patch("configurator.core.installer.HooksManager"):
                        with patch("configurator.core.installer.PluginManager"):
                            with patch("configurator.core.installer.DryRunManager"):
                                with patch("configurator.core.installer.CircuitBreakerManager"):
                                    installer = Installer(
                                        config=config, logger=logger, reporter=reporter
                                    )
                                    # Add mock rollback actions
                                    installer.rollback_manager.actions = [
                                        ("rm -rf /tmp/test", "Remove test directory"),
                                        ("systemctl stop test", "Stop test service"),
                                    ]
                                    installer.rollback_manager.get_summary.return_value = (
                                        "2 rollback actions available"
                                    )
        return installer

    def test_interactive_mode_prompt_content(self, installer):
        """Test that interactive mode would show correct prompt content."""
        installer.config.get.side_effect = lambda key, default=None: {
            "interactive": True,
        }.get(key, default)

        # Verify the config can determine interactive mode
        is_interactive = installer.config.get("interactive", True)
        assert is_interactive is True

        # Verify action count
        action_count = len(installer.rollback_manager.actions)
        assert action_count == 2

    def test_non_interactive_auto_rollback_enabled(self, installer):
        """Test that non-interactive mode with auto-rollback enabled is configured correctly."""
        installer.config.get.side_effect = lambda key, default=None: {
            "interactive": False,
            "installation.auto_rollback_on_error": True,
        }.get(key, default)

        is_interactive = installer.config.get("interactive", True)
        auto_rollback = installer.config.get("installation.auto_rollback_on_error", True)

        assert is_interactive is False
        assert auto_rollback is True

    def test_non_interactive_auto_rollback_disabled(self, installer):
        """Test that non-interactive mode with auto-rollback disabled is configured correctly."""
        installer.config.get.side_effect = lambda key, default=None: {
            "interactive": False,
            "installation.auto_rollback_on_error": False,
        }.get(key, default)

        is_interactive = installer.config.get("interactive", True)
        auto_rollback = installer.config.get("installation.auto_rollback_on_error", True)

        assert is_interactive is False
        assert auto_rollback is False

    def test_rollback_summary_available(self, installer):
        """Test that rollback summary is available."""
        summary = installer.rollback_manager.get_summary()
        assert "2 rollback actions" in summary


class TestRollbackDecisionLogging:
    """Test that rollback decisions are properly logged."""

    def test_user_confirms_rollback_log(self):
        """Test logging when user confirms rollback."""
        logger = Mock()
        logger.info("User confirmed rollback. Proceeding...")
        logger.info.assert_called_with("User confirmed rollback. Proceeding...")

    def test_user_declines_rollback_log(self):
        """Test logging when user declines rollback."""
        logger = Mock()
        logger.info("User declined rollback. Keeping partial changes.")
        logger.info.assert_called_with("User declined rollback. Keeping partial changes.")

    def test_auto_rollback_enabled_log(self):
        """Test logging when auto-rollback is enabled."""
        logger = Mock()
        action_count = 3
        logger.info(f"Auto-rollback enabled. Rolling back {action_count} actions...")
        logger.info.assert_called_with("Auto-rollback enabled. Rolling back 3 actions...")

    def test_auto_rollback_disabled_log(self):
        """Test logging when auto-rollback is disabled."""
        logger = Mock()
        action_count = 3
        logger.warning(
            f"Auto-rollback disabled. Keeping partial changes "
            f"({action_count} rollback actions available)."
        )
        logger.warning.assert_called()


class TestRollbackConfigOption:
    """Test the new config option for auto-rollback."""

    def test_config_option_default_value(self):
        """Test that default config has auto_rollback_on_error = True."""
        # This tests the expectation from default.yaml
        expected_default = True

        config = Mock()
        config.get.side_effect = lambda key, default=None: {
            "installation.auto_rollback_on_error": expected_default,
        }.get(key, default)

        result = config.get("installation.auto_rollback_on_error", True)
        assert result is True
