"""Configuration validation tests for Phase 5."""

from unittest.mock import Mock

import pytest

from configurator.modules.desktop import DesktopModule


class TestTerminalToolsConfig:
    """Validate terminal tools configuration."""

    @pytest.fixture
    def module(self):
        config = {
            "terminal_tools": {
                "bat": {"enabled": True},
                "exa": {"enabled": True},
            }
        }
        return DesktopModule(config=config, logger=Mock(), rollback_manager=Mock())

    def test_config_valid(self, module):
        """Test that config is valid."""
        assert module.get_config("terminal_tools.bat.enabled") is True
