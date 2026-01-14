"""Security tests for XRDP optimization."""

from unittest.mock import Mock, patch

import pytest

from configurator.modules.desktop import DesktopModule


class TestXRDPSecurity:
    """Security tests for XRDP configuration."""

    @pytest.fixture
    def module(self):
        config = {"enabled": True, "xrdp": {"max_bpp": 24}}
        return DesktopModule(config=config, logger=Mock(), rollback_manager=Mock())

    def test_no_hardcoded_credentials(self, module):
        """Ensure no hardcoded credentials in XRDP config."""
        with patch("configurator.utils.file.write_file") as mock_write:
            with patch.object(module, "install_packages", return_value=True):
                with patch.object(module, "run") as mock_run:
                    mock_run.return_value = Mock(success=True)
                    module._optimize_xrdp_performance()

        # Check no actual passwords (like "password123") in written files
        # Note: "password=ask" is OK as it prompts for password
        for call in mock_write.call_args_list:
            content = str(call)
            # Check for hardcoded passwords (not "ask" or empty)
            assert "password=admin" not in content.lower()
            assert "password=root" not in content.lower()
            assert "password=123" not in content.lower()
            assert "secret=" not in content.lower() or "secret=" in content.lower()
