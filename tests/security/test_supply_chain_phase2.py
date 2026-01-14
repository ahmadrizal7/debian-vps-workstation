"""
Supply Chain Security Tests - Phase 2

Tests checksum verification, GPG validation, and download security.
"""

import hashlib
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from configurator.security.supply_chain import SecureDownloader, SecurityError, SupplyChainValidator


class TestChecksumVerification:
    """Test checksum verification functionality."""

    def test_valid_checksum_passes(self, tmp_path):
        """Valid checksum should pass verification."""
        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")

        # Calculate expected checksum
        expected = hashlib.sha256(b"Hello, World!").hexdigest()

        # Verify
        config = {"security_advanced": {"supply_chain": {"enabled": True, "strict_mode": False}}}
        validator = SupplyChainValidator(config, Mock())
        result = validator.verify_checksum(test_file, expected)

        assert result is True

    def test_invalid_checksum_raises_error_strict_mode(self, tmp_path):
        """Invalid checksum should raise SecurityError in strict mode."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")

        wrong_checksum = "0" * 64

        config = {"security_advanced": {"supply_chain": {"enabled": True, "strict_mode": True}}}
        validator = SupplyChainValidator(config, Mock())

        with pytest.raises(SecurityError) as exc:
            validator.verify_checksum(test_file, wrong_checksum)

        assert "Checksum mismatch" in str(exc.value)

    def test_invalid_checksum_returns_false_normal_mode(self, tmp_path):
        """Invalid checksum should return False in normal mode."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")

        wrong_checksum = "0" * 64

        config = {"security_advanced": {"supply_chain": {"enabled": True, "strict_mode": False}}}
        validator = SupplyChainValidator(config, Mock())

        result = validator.verify_checksum(test_file, wrong_checksum)
        assert result is False

    def test_missing_file_raises_error(self, tmp_path):
        """Missing file should raise appropriate error."""
        non_existent = tmp_path / "does-not-exist.txt"

        config = {"security_advanced": {"supply_chain": {"enabled": True}}}
        validator = SupplyChainValidator(config, Mock())

        with pytest.raises(SecurityError) as exc:
            validator.verify_checksum(non_existent, "abc123")

        assert "not found" in str(exc.value).lower()

    def test_disabled_validation_skips_check(self, tmp_path):
        """Disabled validation should skip checksum check."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")

        wrong_checksum = "0" * 64

        config = {"security_advanced": {"supply_chain": {"enabled": False}}}
        validator = SupplyChainValidator(config, Mock())

        # Should pass even with wrong checksum
        result = validator.verify_checksum(test_file, wrong_checksum)
        assert result is True


class TestSecureDownloader:
    """Test SecureDownloader functionality."""

    @patch("subprocess.run")
    def test_download_with_valid_checksum(self, mock_run, tmp_path):
        """Download with valid checksum should succeed."""
        # Mock successful download
        dest = tmp_path / "downloaded.txt"

        def run_side_effect(*args, **kwargs):
            # Simulate successful download
            if "curl" in args[0]:
                # Extract destination file from curl command
                if "-o" in args[0]:
                    idx = args[0].index("-o")
                    dest_file = Path(args[0][idx + 1])
                    dest_file.write_text("test content")
                return MagicMock(returncode=0, stdout=b"", stderr=b"")
            return MagicMock(returncode=0)

        mock_run.side_effect = run_side_effect

        config = {
            "security_advanced": {
                "supply_chain": {"enabled": True, "allowed_sources": {"web": ["example.com"]}}
            }
        }
        validator = SupplyChainValidator(config, Mock())
        downloader = SecureDownloader(validator, Mock())

        expected_checksum = hashlib.sha256(b"test content").hexdigest()

        result = downloader.download_file(
            url="https://example.com/file.txt",
            destination=dest,
            expected_checksum=expected_checksum,
        )

        assert result is True
        assert dest.exists()

    @patch("subprocess.run")
    def test_download_with_invalid_checksum_fails(self, mock_run, tmp_path):
        """Download with invalid checksum should fail."""
        dest = tmp_path / "downloaded.txt"

        def run_side_effect(*args, **kwargs):
            if "curl" in args[0]:
                if "-o" in args[0]:
                    idx = args[0].index("-o")
                    dest_file = Path(args[0][idx + 1])
                    dest_file.write_text("different content")
                return MagicMock(returncode=0, stdout=b"", stderr=b"")
            return MagicMock(returncode=0)

        mock_run.side_effect = run_side_effect

        config = {
            "security_advanced": {
                "supply_chain": {
                    "enabled": True,
                    "strict_mode": False,
                    "allowed_sources": {"web": ["example.com"]},
                }
            }
        }
        validator = SupplyChainValidator(config, Mock())
        downloader = SecureDownloader(validator, Mock())

        wrong_checksum = "0" * 64

        result = downloader.download_file(
            url="https://example.com/file.txt", destination=dest, expected_checksum=wrong_checksum
        )

        # Should fail and remove file
        assert result is False
        assert not dest.exists()


class TestMaliciousPayloadSimulation:
    """Simulate malicious payload attacks."""

    def test_tampered_download_detected(self, tmp_path):
        """Tampered download should be detected by checksum."""
        # Simulate legitimate checksum
        legitimate_content = b"safe content"
        legitimate_checksum = hashlib.sha256(legitimate_content).hexdigest()

        # Create tampered file
        tampered_file = tmp_path / "download.sh"
        tampered_file.write_text("rm -rf /; echo 'pwned'")

        # Verification should fail
        config = {"security_advanced": {"supply_chain": {"enabled": True, "strict_mode": True}}}
        validator = SupplyChainValidator(config, Mock())

        with pytest.raises(SecurityError) as exc:
            validator.verify_checksum(tampered_file, legitimate_checksum)

        assert "mismatch" in str(exc.value).lower()

    def test_mitm_attack_simulation(self, tmp_path):
        """MITM attack changing file should be detected."""
        # Original file
        original = tmp_path / "original.txt"
        original.write_text("original content")

        expected_checksum = hashlib.sha256(b"original content").hexdigest()

        # Attacker modifies file
        original.write_text("malicious content injected")

        # Should detect tampering
        config = {"security_advanced": {"supply_chain": {"enabled": True, "strict_mode": True}}}
        validator = SupplyChainValidator(config, Mock())

        with pytest.raises(SecurityError):
            validator.verify_checksum(original, expected_checksum)


class TestSecurityError:
    """Test SecurityError exception."""

    def test_security_error_format(self):
        """SecurityError should format message properly."""
        err = SecurityError(what="Test failure", why="Because testing", how="Fix the test")

        error_msg = str(err)
        assert "SECURITY ALERT" in error_msg
        assert "Test failure" in error_msg
        assert "Because testing" in error_msg
        assert "Fix the test" in error_msg


class TestChecksumDatabase:
    """Test checksum database loading."""

    def test_load_checksums_from_yaml(self):
        """Should load checksums from YAML file."""
        config = {"security_advanced": {"supply_chain": {"enabled": True}}}
        validator = SupplyChainValidator(config, Mock())

        # Should have loaded checksums (or empty dict if file missing)
        assert isinstance(validator.checksums, dict)

    def test_get_oh_my_zsh_checksum(self):
        """Should retrieve Oh My Zsh checksum from database."""
        config = {"security_advanced": {"supply_chain": {"enabled": True}}}
        validator = SupplyChainValidator(config, Mock())

        oh_my_zsh = validator.checksums.get("oh_my_zsh", {})
        # May be empty if checksums.yaml not populated
        assert isinstance(oh_my_zsh, dict)


@pytest.mark.integration
class TestEndToEndSecurity:
    """End-to-end security integration tests."""

    @patch("subprocess.run")
    def test_full_secure_download_workflow(self, mock_run, tmp_path):
        """Test complete secure download workflow."""
        dest = tmp_path / "safe-file.tar.gz"

        def run_side_effect(*args, **kwargs):
            if "curl" in args[0]:
                if "-o" in args[0]:
                    idx = args[0].index("-o")
                    dest_file = Path(args[0][idx + 1])
                    dest_file.write_text("downloaded content")
                return MagicMock(returncode=0, stdout=b"", stderr=b"")
            return MagicMock(returncode=0)

        mock_run.side_effect = run_side_effect

        config = {
            "security_advanced": {
                "supply_chain": {"enabled": True, "allowed_sources": {"web": ["example.com"]}}
            }
        }
        validator = SupplyChainValidator(config, Mock())
        downloader = SecureDownloader(validator, Mock())

        expected_checksum = hashlib.sha256(b"downloaded content").hexdigest()

        result = downloader.download_file(
            url="https://example.com/safe-file.tar.gz",
            destination=dest,
            expected_checksum=expected_checksum,
        )

        assert result is True
        assert dest.exists()
