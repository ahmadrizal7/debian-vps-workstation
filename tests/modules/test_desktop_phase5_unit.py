"""
Unit tests for Phase 5 terminal tools configuration methods.
"""

from unittest.mock import Mock, patch

import pytest

from configurator.modules.desktop import DesktopModule


class TestBatConfigurationMethods:
    """Unit tests for bat configuration methods."""

    @pytest.fixture
    def module(self):
        config = {
            "desktop": {
                "terminal_tools": {
                    "bat": {"theme": "TwoDark", "line_numbers": True, "git_integration": True}
                }
            }
        }
        return DesktopModule(config=config, logger=Mock(), rollback_manager=Mock())

    @patch("configurator.modules.desktop.pwd")
    @patch.object(DesktopModule, "run")
    def test_configure_bat_advanced_creates_config_directory(self, mock_run, mock_pwd, module):
        """Test that bat config directory is created."""
        mock_user = Mock()
        mock_user.pw_name = "testuser"
        mock_user.pw_uid = 1000
        mock_user.pw_dir = "/home/testuser"

        mock_pwd.getpwall.return_value = [mock_user]
        mock_pwd.getpwnam.return_value = mock_user

        module._configure_bat_advanced()

        # Verify mkdir called
        mkdir_calls = [str(c) for c in mock_run.call_args_list if "mkdir" in str(c)]
        assert any(".config/bat" in config_call for config_call in mkdir_calls)

    @patch("configurator.modules.desktop.pwd")
    @patch.object(DesktopModule, "run")
    def test_configure_bat_advanced_writes_config_file(self, mock_run, mock_pwd, module):
        """Test that bat config file is written."""
        mock_user = Mock()
        mock_user.pw_name = "testuser"
        mock_user.pw_uid = 1000
        mock_user.pw_dir = "/home/testuser"

        mock_pwd.getpwall.return_value = [mock_user]
        mock_pwd.getpwnam.return_value = mock_user

        module._configure_bat_advanced()

        # Verify tee called with config content
        tee_calls = [c for c in mock_run.call_args_list if "tee" in str(c)]
        assert any(".config/bat/config" in str(config_call) for config_call in tee_calls)

    @patch("configurator.modules.desktop.pwd")
    @patch.object(DesktopModule, "run")
    def test_configure_bat_registers_rollback(self, mock_run, mock_pwd, module):
        """Test that rollback action is registered."""
        mock_user = Mock()
        mock_user.pw_name = "testuser"
        mock_user.pw_uid = 1000
        mock_user.pw_dir = "/home/testuser"

        mock_pwd.getpwall.return_value = [mock_user]
        mock_pwd.getpwnam.return_value = mock_user

        module._configure_bat_advanced()

        # Verify rollback registered
        assert module.rollback_manager.add_command.called

        rollback_calls = [str(c) for c in module.rollback_manager.add_command.call_args_list]
        assert any(".config/bat" in rollback_call for rollback_call in rollback_calls)


class TestIntegrationScriptCreation:
    """Unit tests for integration script creation."""

    @pytest.fixture
    def module(self):
        config = {"desktop": {"terminal_tools": {}}}
        return DesktopModule(config=config, logger=Mock(), rollback_manager=Mock())

    @patch("configurator.modules.desktop.pwd")
    @patch.object(DesktopModule, "run")
    def test_create_tool_integration_scripts_creates_all_scripts(self, mock_run, mock_pwd, module):
        """Test that all three integration scripts are created."""
        mock_user = Mock()
        mock_user.pw_name = "testuser"
        mock_user.pw_uid = 1000
        mock_user.pw_dir = "/home/testuser"

        mock_pwd.getpwall.return_value = [mock_user]
        mock_pwd.getpwnam.return_value = mock_user

        module._create_tool_integration_scripts()

        # Verify all scripts created
        tee_calls = [str(c) for c in mock_run.call_args_list if "tee" in str(c)]

        assert any("preview" in call for call in tee_calls)
        assert any("search" in call for call in tee_calls)
        assert any("goto" in call for call in tee_calls)

    @patch("configurator.modules.desktop.pwd")
    @patch.object(DesktopModule, "run")
    def test_scripts_made_executable(self, mock_run, mock_pwd, module):
        """Test that scripts are made executable."""
        mock_user = Mock()
        mock_user.pw_name = "testuser"
        mock_user.pw_uid = 1000
        mock_user.pw_dir = "/home/testuser"

        mock_pwd.getpwall.return_value = [mock_user]
        mock_pwd.getpwnam.return_value = mock_user

        module._create_tool_integration_scripts()

        # Verify chmod +x called
        chmod_calls = [str(c) for c in mock_run.call_args_list if "chmod +x" in str(c)]

        assert len(chmod_calls) >= 3  # At least one for each script


class TestOptionalToolsInstallation:
    """Unit tests for optional tools installation."""

    @pytest.fixture
    def module(self):
        config = {
            "desktop": {
                "terminal_tools": {"optional": {"ripgrep": True, "fd": True, "delta": True}}
            }
        }
        return DesktopModule(config=config, logger=Mock())

    @patch.object(DesktopModule, "install_packages")
    def test_install_optional_tools_installs_ripgrep(self, mock_install_pkg, module):
        """Test that ripgrep is installed when configured."""
        with patch.object(module, "_install_git_delta"):
            module._install_optional_productivity_tools()

        # Verify ripgrep in packages
        all_packages = []
        for pkg_call in mock_install_pkg.call_args_list:
            all_packages.extend(pkg_call[0][0])

        assert "ripgrep" in all_packages

    @patch.object(DesktopModule, "install_packages")
    def test_install_optional_tools_respects_config(self, mock_install_pkg, module):
        """Test that optional tools respect configuration."""
        # Disable ripgrep
        module.config["desktop"]["terminal_tools"]["optional"]["ripgrep"] = False

        with patch.object(module, "_install_git_delta"):
            module._install_optional_productivity_tools()

        all_packages = []
        for pkg_call in mock_install_pkg.call_args_list:
            all_packages.extend(pkg_call[0][0])

        # Should NOT include ripgrep
        assert "ripgrep" not in all_packages
