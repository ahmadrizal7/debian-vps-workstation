"""Security tests for command injection prevention."""

from unittest.mock import Mock, patch

import pytest

from configurator.modules.desktop import DesktopModule


class TestCommandInjectionPrevention:
    """Test command injection prevention."""

    @pytest.fixture
    def module(self):
        return DesktopModule(config={}, logger=Mock(), rollback_manager=Mock())

    def test_username_validation_prevents_injection(self, module):
        """Test that malicious usernames are rejected."""
        with patch("configurator.modules.desktop.pwd") as mock_pwd:
            malicious_user = Mock()
            malicious_user.pw_name = "user;rm -rf /"
            malicious_user.pw_uid = 1000
            malicious_user.pw_dir = "/home/user"
            mock_pwd.getpwall.return_value = [malicious_user]

            with patch.object(module, "run") as mock_run:
                # Should not execute dangerous commands
                module._optimize_xfce_compositor()

                # Check no dangerous commands were run
                dangerous_patterns = [";rm", "&&rm", "|rm"]
                for call in mock_run.call_args_list:
                    cmd = str(call)
                    for pattern in dangerous_patterns:
                        assert pattern not in cmd
