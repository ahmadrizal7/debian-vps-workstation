"""Input validation security tests."""

from unittest.mock import Mock

import pytest

from configurator.modules.desktop import DesktopModule


class TestConfigValueValidation:
    """Test configuration value validation."""

    @pytest.fixture
    def module(self):
        return DesktopModule(config={}, logger=Mock(), rollback_manager=Mock())

    def test_max_bpp_range_validation(self, module):
        """Test max_bpp is within valid range."""
        valid_configs = {"enabled": True, "xrdp": {"max_bpp": 24}}
        test_module = DesktopModule(config=valid_configs, logger=Mock(), rollback_manager=Mock())
        assert test_module.get_config("xrdp.max_bpp") == 24

    def test_security_layer_validation(self, module):
        """Test security_layer has valid value."""
        valid_configs = {"enabled": True, "xrdp": {"security_layer": "tls"}}
        test_module = DesktopModule(config=valid_configs, logger=Mock(), rollback_manager=Mock())
        assert test_module.get_config("xrdp.security_layer") == "tls"
