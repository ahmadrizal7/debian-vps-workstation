import pytest
from pydantic import ValidationError

from configurator.config_schema import Config, SecurityConfig, SystemConfig


def test_valid_system_config():
    config = SystemConfig(hostname="valid-hostname", swap_size_gb=4)
    assert config.hostname == "valid-hostname"
    assert config.swap_size_gb == 4


def test_invalid_hostname():
    with pytest.raises(ValidationError):
        SystemConfig(hostname="Invalid Hostname")


def test_invalid_swap_size():
    with pytest.raises(ValidationError):
        SystemConfig(swap_size_gb=-1)


def test_security_defaults():
    config = SecurityConfig()
    assert config.enabled is True
    assert config.ufw.ssh_port == 22


def test_security_cannot_be_disabled():
    with pytest.raises(ValidationError):
        SecurityConfig(enabled=False)


def test_full_config_structure():
    config = Config()
    assert config.system.hostname == "dev-workstation"
    assert config.security.enabled is True
    assert config.languages.python.enabled is True
    assert config.languages.golang.enabled is False


def test_partial_update():
    # Simulate loading partial config from dict
    data = {
        "system": {"hostname": "new-host"},
        "tools": {"editors": {"vscode": {"enabled": False}}},
    }
    # Note: Pydantic models don't support partial updates directly in constructor
    # without preserving defaults unless we handle it carefully.
    # However, we can construct the object using default factories.
    # In ConfigManager, we'll merge dicts and then validate.

    # We can test validation of a merged dict
    config = Config(**{"system": {"hostname": "new-host"}})
    assert config.system.hostname == "new-host"
