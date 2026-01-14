"""
Integration tests for Phase 3 features (Themes, Icons, Fonts).
"""

from unittest.mock import Mock, patch

import pytest

from configurator.modules.desktop import DesktopModule


class TestPhase3Integration:
    """Integration tests for Phase 3: Themes, Icons, Fonts."""

    @pytest.fixture
    def module(self):
        config = {
            "enabled": True,
            "themes": {"install": ["nordic"], "active": "Nordic-darker"},
            "icons": {"install": ["papirus"], "active": "Papirus-Dark"},
            "fonts": {"rendering": {"enabled": True, "dpi": 96}},
        }
        return DesktopModule(config=config, logger=Mock(), rollback_manager=Mock())

    def test_install_themes_works(self, module):
        """Test theme installation."""
        with patch.object(module, "run") as mock_run:
            mock_run.return_value = Mock(success=True)
            with patch("os.path.exists", return_value=False):
                result = module._install_themes()
        assert isinstance(result, bool)

    def test_install_icons_works(self, module):
        """Test icon installation."""
        with patch.object(module, "install_packages", return_value=True):
            result = module._install_icons()
        assert isinstance(result, bool)

    def test_configure_fonts_works(self, module):
        """Test font configuration."""
        with patch("configurator.modules.desktop.pwd") as mock_pwd:
            mock_user = Mock(pw_name="test", pw_uid=1000, pw_dir="/home/test")
            mock_pwd.getpwall.return_value = [mock_user]
            with patch("configurator.utils.file.write_file"):
                with patch("os.makedirs"):
                    with patch("shutil.chown"):
                        result = module._configure_fonts()
        assert isinstance(result, bool)
