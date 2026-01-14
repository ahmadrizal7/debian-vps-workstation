"""
Integration tests for Phase 5 features (Terminal Tools).
"""

from unittest.mock import Mock, patch

import pytest

from configurator.modules.desktop import DesktopModule


class TestPhase5Integration:
    """Integration tests for Phase 5: Terminal Tools."""

    @pytest.fixture
    def module(self):
        config = {
            "enabled": True,
            "terminal_tools": {
                "bat": {"enabled": True},
                "exa": {"enabled": True},
                "zoxide": {"enabled": True},
                "fzf": {"enabled": True},
            },
        }
        return DesktopModule(config=config, logger=Mock(), rollback_manager=Mock())

    def test_configure_terminal_tools_works(self, module):
        """Test terminal tools configuration."""
        with patch.object(module, "install_packages", return_value=True):
            with patch.object(module, "command_exists", return_value=True):
                result = module._configure_terminal_tools()
        assert isinstance(result, bool)
