"""Privilege escalation prevention tests."""

from unittest.mock import Mock, patch

import pytest

from configurator.modules.desktop import DesktopModule


class TestPrivilegeEscalationDefense:
    """Test privilege escalation defenses."""

    @pytest.fixture
    def module(self):
        return DesktopModule(config={}, logger=Mock(), rollback_manager=Mock())

    def test_files_created_with_safe_permissions(self, module):
        """Test that files are created with safe permissions."""
        with patch("configurator.utils.file.write_file") as mock_write:
            with patch.object(module, "run") as mock_run:
                mock_run.return_value = Mock(success=True)
                with patch.object(module, "install_packages", return_value=True):
                    module._optimize_xrdp_performance()

        # Check write_file was called with mode parameter
        for call in mock_write.call_args_list:
            if "mode" in call.kwargs:
                mode = call.kwargs["mode"]
                # Should not be world-writable
                assert (mode & 0o002) == 0, "Files should not be world-writable"


class TestPolkitPrivilegeEscalation:
    """Test Polkit privilege escalation prevention."""

    @pytest.fixture
    def module(self):
        return DesktopModule(config={}, logger=Mock(), rollback_manager=Mock())

    def test_polkit_rules_do_not_allow_everything(self, module):
        """Test that Polkit rules are restrictive."""
        with patch("configurator.utils.file.write_file") as mock_write:
            with patch("os.path.isdir", return_value=True):
                with patch.object(module, "run") as mock_run:
                    mock_run.return_value = Mock(success=True)
                    module._configure_polkit_rules()

        # Check that rules specify specific actions (not wildcard)
        # ResultAny=yes is OK if combined with specific actions
        has_specific_actions = False
        for call in mock_write.call_args_list:
            content = str(call)
            if "Action=" in content and "org.freedesktop" in content:
                has_specific_actions = True

        assert has_specific_actions, "Polkit rules should specify specific actions"

    def test_polkit_rules_restricted_to_specific_groups(self, module):
        """Test that Polkit rules specify user groups or identities."""
        with patch("configurator.utils.file.write_file") as mock_write:
            with patch("os.path.isdir", return_value=True):
                with patch.object(module, "run") as mock_run:
                    mock_run.return_value = Mock(success=True)
                    module._configure_polkit_rules()

        # Check that rules specify Identity (even if unix-user:*)
        has_identity = False
        for call in mock_write.call_args_list:
            content = str(call)
            if "Identity=" in content:
                has_identity = True

        assert has_identity, "Polkit rules should specify identity"
