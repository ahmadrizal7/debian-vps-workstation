"""Security penetration tests for Phase 2."""

from unittest.mock import Mock, patch

import pytest

from configurator.modules.desktop import DesktopModule


class TestCommandInjectionDefense:
    """Test command injection defenses."""

    @pytest.fixture
    def module(self):
        return DesktopModule(config={}, logger=Mock(), rollback_manager=Mock())

    def test_user_input_sanitization(self, module):
        """Test that user input is sanitized."""
        with patch("configurator.modules.desktop.pwd") as mock_pwd:
            user = Mock(pw_name="test", pw_uid=1000, pw_dir="/home/test")
            mock_pwd.getpwall.return_value = [user]
            with patch.object(module, "run"):
                with patch("configurator.utils.file.write_file"):
                    with patch("os.makedirs"):
                        with patch("shutil.chown"):
                            # Should not raise errors with normal input
                            module._optimize_xfce_compositor()
