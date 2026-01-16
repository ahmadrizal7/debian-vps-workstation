"""
Unit tests for OS version validator.
"""

from unittest.mock import Mock, patch

from configurator.validators.base import ValidationSeverity
from configurator.validators.tier1_critical.os_version import OSVersionValidator


class TestOSVersionValidator:
    """Tests for OSVersionValidator."""

    @patch("configurator.validators.tier1_critical.os_version.get_os_info")
    def test_debian_13_passes(self, mock_get_os):
        """Test Debian 13 passes validation."""
        os_info = Mock()
        os_info.name = "debian"
        os_info.id = "debian"
        os_info.version_id = "13"
        os_info.pretty_name = "Debian 13 (Trixie)"
        mock_get_os.return_value = os_info

        validator = OSVersionValidator()
        result = validator.validate()

        assert result.passed is True
        assert result.severity == ValidationSeverity.CRITICAL

    @patch("configurator.validators.tier1_critical.os_version.get_os_info")
    def test_ubuntu_2204_passes(self, mock_get_os):
        """Test Ubuntu 22.04 passes validation."""
        os_info = Mock()
        os_info.name = "ubuntu"
        os_info.id = "ubuntu"
        os_info.version_id = "22.04"
        os_info.pretty_name = "Ubuntu 22.04 LTS"
        mock_get_os.return_value = os_info

        validator = OSVersionValidator()
        result = validator.validate()

        assert result.passed is True
        assert result.severity == ValidationSeverity.CRITICAL

    @patch("configurator.validators.tier1_critical.os_version.get_os_info")
    def test_ubuntu_2404_passes(self, mock_get_os):
        """Test Ubuntu 24.04 passes validation."""
        os_info = Mock()
        os_info.name = "ubuntu"
        os_info.id = "ubuntu"
        os_info.version_id = "24.04"
        os_info.pretty_name = "Ubuntu 24.04 LTS"
        mock_get_os.return_value = os_info

        validator = OSVersionValidator()
        result = validator.validate()

        assert result.passed is True

    @patch("configurator.validators.tier1_critical.os_version.get_os_info")
    def test_debian_12_fails(self, mock_get_os):
        """Test Debian 12 fails validation."""
        os_info = Mock()
        os_info.name = "debian"
        os_info.id = "debian"
        os_info.version_id = "12"
        os_info.pretty_name = "Debian 12 (Bookworm)"
        mock_get_os.return_value = os_info

        validator = OSVersionValidator()
        result = validator.validate()

        assert result.passed is False
        assert "Unsupported" in result.message
        assert "12" in result.current_value
        assert result.fix_suggestion is not None

    @patch("configurator.validators.tier1_critical.os_version.get_os_info")
    def test_unsupported_os(self, mock_get_os):
        """Test unsupported OS fails validation."""
        os_info = Mock()
        os_info.name = "fedora"
        os_info.id = "fedora"
        os_info.version_id = "39"
        os_info.pretty_name = "Fedora 39"
        mock_get_os.return_value = os_info

        validator = OSVersionValidator()
        result = validator.validate()

        assert result.passed is False
        assert "Unsupported" in result.message
        assert "fedora" in result.current_value.lower()
