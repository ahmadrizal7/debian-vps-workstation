"""Supply chain security tests for Phase 3."""

from unittest.mock import Mock, patch

import pytest

from configurator.modules.desktop import DesktopModule


class TestThemeSupplyChain:
    """Test theme installation supply chain security."""

    @pytest.fixture
    def module(self):
        config = {"themes": {"install": ["nordic"]}}
        return DesktopModule(config=config, logger=Mock(), rollback_manager=Mock())

    def test_theme_installation_uses_safe_sources(self, module):
        """Test that themes are installed from safe sources."""
        with patch.object(module, "run") as mock_run:
            mock_run.return_value = Mock(success=True)
            with patch("os.path.exists", return_value=False):
                module._install_themes()

        # Should use git clone with HTTPS
        for call in mock_run.call_args_list:
            if "git clone" in str(call):
                assert "https://" in str(call)
