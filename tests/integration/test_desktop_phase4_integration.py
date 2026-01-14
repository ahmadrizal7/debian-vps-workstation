"""
Integration tests for Phase 4 features (Zsh Environment).
"""

from unittest.mock import Mock, patch

import pytest

from configurator.modules.desktop import DesktopModule


class TestPhase4Integration:
    """Integration tests for Phase 4: Zsh Environment."""

    @pytest.fixture
    def module(self):
        config = {
            "enabled": True,
            "zsh": {"enabled": True, "set_default_shell": True},
        }
        return DesktopModule(config=config, logger=Mock(), rollback_manager=Mock())

    def test_configure_zsh_works(self, module):
        """Test Zsh configuration."""
        with patch.object(module, "_install_zsh_package", return_value=True):
            with patch.object(module, "_install_oh_my_zsh", return_value=True):
                with patch.object(module, "_install_zsh_plugins", return_value=True):
                    with patch.object(module, "_apply_zsh_to_all_users", return_value=True):
                        result = module._configure_zsh()
        assert result is True

    def test_install_zsh_package_works(self, module):
        """Test Zsh package installation."""
        with patch.object(module, "install_packages", return_value=True):
            with patch.object(module, "command_exists", return_value=True):
                result = module._install_zsh_package()
        assert result is True
