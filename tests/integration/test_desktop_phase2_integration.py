"""
Integration tests for DesktopModule Phase 2 features (Compositor & Polkit).

Tests the configuration of XFCE compositor and Polkit rules with current API.
"""

from unittest.mock import Mock, patch

import pytest

from configurator.modules.desktop import DesktopModule


class TestDesktopPhase2Integration:
    """Integration tests for Phase 2: XFCE Compositor & Polkit Rules."""

    @pytest.fixture
    def module(self):
        """Create Desktop module with Phase 2 config."""
        config = {
            "enabled": True,
            "compositor": {"mode": "optimized"},
            "polkit": {"allow_colord": True, "allow_packagekit": True},
        }
        logger = Mock()
        rollback_manager = Mock()
        return DesktopModule(config=config, logger=logger, rollback_manager=rollback_manager)

    def test_configure_compositor_creates_config(self, module):
        """Test that compositor configuration creates XML config."""
        mock_user = Mock()
        mock_user.pw_name = "testuser"
        mock_user.pw_uid = 1000
        mock_user.pw_dir = "/home/testuser"

        with patch("configurator.modules.desktop.pwd") as mock_pwd:
            mock_pwd.getpwall.return_value = [mock_user]
            with patch("configurator.utils.file.write_file") as mock_write:
                with patch("os.makedirs"):
                    with patch("os.path.isdir", return_value=True):
                        with patch("shutil.chown"):
                            result = module._optimize_xfce_compositor()

        assert result is True
        # Should have written compositor config
        assert mock_write.called

    def test_configure_polkit_creates_rules(self, module):
        """Test that Polkit configuration creates rule files."""
        with patch("configurator.utils.file.write_file") as mock_write:
            with patch("os.path.isdir", return_value=True):
                with patch.object(module, "run") as mock_run:
                    mock_run.return_value = Mock(success=True)
                    result = module._configure_polkit_rules()

        assert result is True
        # Should have written both colord and packagekit rules
        write_calls = [str(call) for call in mock_write.call_args_list]
        assert any("colord" in call for call in write_calls)
        assert any("packagekit" in call for call in write_calls)

    def test_full_configure_calls_phase2_methods(self, module):
        """Test that configure() calls Phase 2 methods."""
        with patch.object(module, "_optimize_xrdp_performance", return_value=True):
            with patch.object(module, "_optimize_xfce_compositor", return_value=True) as mock_comp:
                with patch.object(module, "_configure_polkit_rules", return_value=True) as mock_pol:
                    with patch.object(module, "_install_themes", return_value=True):
                        with patch.object(module, "_install_icons", return_value=True):
                            with patch.object(module, "_configure_fonts", return_value=True):
                                with patch.object(module, "_configure_zsh", return_value=True):
                                    module.configure()

        assert mock_comp.called, "Compositor method should be called"
        assert mock_pol.called, "Polkit method should be called"
