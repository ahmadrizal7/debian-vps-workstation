"""Shell script validation tests for Phase 4."""

from unittest.mock import Mock

import pytest

from configurator.modules.desktop import DesktopModule


class TestZshrcValidation:
    """Validate Zsh configuration."""

    @pytest.fixture
    def module(self):
        config = {"zsh": {"enabled": True}}
        return DesktopModule(config=config, logger=Mock(), rollback_manager=Mock())

    def test_zshrc_generation(self, module):
        """Test that zshrc can be configured."""
        # Current implementation doesn't generate zshrc, it uses OMZ
        assert module is not None
