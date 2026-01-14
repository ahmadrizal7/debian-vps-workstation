"""Supply chain security tests for Phase 4."""

from unittest.mock import Mock, patch

import pytest

from configurator.modules.desktop import DesktopModule


class TestZshSupplyChain:
    """Test Zsh installation supply chain security."""

    @pytest.fixture
    def module(self):
        config = {"zsh": {"enabled": True}}
        return DesktopModule(config=config, logger=Mock(), rollback_manager=Mock())

    def test_oh_my_zsh_installation_secure(self, module):
        """Test that OMZ installation is secure."""
        with patch.object(module, "run") as mock_run:
            mock_run.return_value = Mock(success=True)
            with patch("configurator.modules.desktop.pwd") as mock_pwd:
                user = Mock(pw_name="test", pw_uid=1000, pw_dir="/home/test")
                mock_pwd.getpwall.return_value = [user]
                with patch("os.path.exists", return_value=False):
                    module._install_oh_my_zsh()

        # Should use HTTPS for OMZ download
        install_calls = [str(c) for c in mock_run.call_args_list if "install.sh" in str(c)]
        assert any("https://" in call for call in install_calls)
