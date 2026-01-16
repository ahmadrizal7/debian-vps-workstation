"""
Pytest configuration and fixtures for the test suite.
"""

import sys
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(autouse=True)
def restore_dependency_registry():
    """Restore default dependencies after tests that clear the registry."""
    # Let the test run
    yield

    # After test: ensure defaults are restored
    from configurator.dependencies.registry import DependencyRegistry, ModuleDependencyInfo

    # If registry was cleared during test, repopulate
    if len(DependencyRegistry.get_all()) < 5:  # Minimal check
        defaults = [
            ModuleDependencyInfo("system", priority=10),
            ModuleDependencyInfo("security", depends_on=["system"], priority=20),
            ModuleDependencyInfo("rbac", depends_on=["security"], priority=25),
            ModuleDependencyInfo("desktop", depends_on=["system", "security"], priority=30),
            ModuleDependencyInfo("python", depends_on=["system"], priority=50),
            ModuleDependencyInfo("nodejs", depends_on=["system"], priority=50),
            ModuleDependencyInfo("golang", depends_on=["system"], priority=50),
            ModuleDependencyInfo("rust", depends_on=["system"], priority=50),
            ModuleDependencyInfo("java", depends_on=["system"], priority=50),
            ModuleDependencyInfo("php", depends_on=["system"], priority=50),
            ModuleDependencyInfo("git", depends_on=["system"], priority=40),
            ModuleDependencyInfo("docker", depends_on=["system", "security"], priority=40),
            ModuleDependencyInfo("databases", depends_on=["system"], priority=50),
            ModuleDependencyInfo("devops", depends_on=["system", "python"], priority=50),
            ModuleDependencyInfo("vscode", depends_on=["desktop"], priority=60),
            ModuleDependencyInfo("cursor", depends_on=["desktop"], priority=60),
            ModuleDependencyInfo("neovim", depends_on=["system"], priority=50),
            ModuleDependencyInfo("wireguard", depends_on=["security"], priority=30),
            ModuleDependencyInfo("caddy", depends_on=["security"], priority=30),
            ModuleDependencyInfo("netdata", depends_on=["system"], priority=90),
        ]
        for dep in defaults:
            DependencyRegistry.register(dep)


@pytest.fixture
def mock_logger():
    """Create a mock logger."""
    logger = MagicMock()
    logger.info = MagicMock()
    logger.warning = MagicMock()
    logger.error = MagicMock()
    logger.debug = MagicMock()
    return logger


@pytest.fixture
def mock_config() -> Dict[str, Any]:
    """Create a minimal test configuration."""
    return {
        "system": {
            "hostname": "test-workstation",
            "timezone": "UTC",
            "locale": "en_US.UTF-8",
            "swap_size_gb": 0,
            "kernel_tuning": False,
        },
        "security": {
            "enabled": True,
        },
        "desktop": {
            "enabled": True,
        },
        "languages": {
            "python": {"enabled": True},
            "nodejs": {"enabled": False},
        },
        "tools": {
            "docker": {"enabled": False},
            "git": {"enabled": False},
            "editors": {
                "vscode": {"enabled": False},
            },
        },
        "interactive": False,
    }


@pytest.fixture
def temp_config_file(tmp_path):
    """Create a temporary configuration file."""
    config_content = """
system:
  hostname: test-server
  timezone: UTC

languages:
  python:
    enabled: true
"""
    config_file = tmp_path / "test-config.yaml"
    config_file.write_text(config_content)
    return config_file


@pytest.fixture
def mock_os_release(tmp_path):
    """Create a mock /etc/os-release file for Debian 13."""
    os_release_content = """PRETTY_NAME="Debian GNU/Linux 13 (trixie)"
NAME="Debian GNU/Linux"
VERSION_ID="13"
VERSION="13 (trixie)"
VERSION_CODENAME=trixie
ID=debian
HOME_URL="https://www.debian.org/"
"""
    os_release = tmp_path / "os-release"
    os_release.write_text(os_release_content)
    return os_release


@pytest.fixture
def mock_run_command(monkeypatch):
    """Mock the run_command function to avoid actual shell commands."""
    from configurator.utils.command import CommandResult

    def mock_run(command, **kwargs):
        return CommandResult(
            command=command if isinstance(command, str) else " ".join(command),
            return_code=0,
            stdout="",
            stderr="",
        )

    monkeypatch.setattr("configurator.utils.command.run_command", mock_run)
    return mock_run
