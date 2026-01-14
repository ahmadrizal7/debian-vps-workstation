"""
Integration tests for full phase integration.
"""

from unittest.mock import Mock, patch

import pytest

from configurator.modules.desktop import DesktopModule


class TestDesktopPhasesIntegration:
    """Integration tests for all phases together."""

    @pytest.fixture
    def module(self):
        config = {
            "enabled": True,
            "xrdp": {"max_bpp": 24},
            "compositor": {"mode": "optimized"},
            "polkit": {"allow_colord": True},
        }
        return DesktopModule(config=config, logger=Mock(), rollback_manager=Mock())

    def test_full_configure_runs_all_phases(self, module):
        """Test that full configure runs all phases."""
        with patch.object(module, "_optimize_xrdp_performance", return_value=True):
            with patch.object(module, "_optimize_xfce_compositor", return_value=True):
                with patch.object(module, "_configure_polkit_rules", return_value=True):
                    with patch.object(module, "_install_themes", return_value=True):
                        with patch.object(module, "_install_icons", return_value=True):
                            with patch.object(module, "_configure_fonts", return_value=True):
                                with patch.object(module, "_configure_zsh", return_value=True):
                                    result = module.configure()
        assert result is True
