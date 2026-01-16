"""
Network connectivity validator - Tier 2 High Priority.

Validates that the system has internet connectivity.
"""

import socket
from typing import List, Tuple

from configurator.validators.base import (
    BaseValidator,
    ValidationResult,
    ValidationSeverity,
)


class NetworkValidator(BaseValidator):
    """Validate internet connectivity."""

    name = "Internet Connectivity"
    severity = ValidationSeverity.HIGH
    auto_fix_available = False

    # Test connectivity to multiple reliable hosts
    TEST_HOSTS: List[Tuple[str, int]] = [
        ("deb.debian.org", 80),
        ("archive.ubuntu.com", 80),
        ("8.8.8.8", 53),  # Google DNS
    ]

    TIMEOUT_SECONDS = 5

    def validate(self) -> ValidationResult:
        """
        Check if system has internet connectivity.

        Returns:
            ValidationResult indicating if internet is accessible
        """
        successful_hosts = []
        failed_hosts = []

        for host, port in self.TEST_HOSTS:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.TIMEOUT_SECONDS)
                result = sock.connect_ex((host, port))
                sock.close()

                if result == 0:
                    successful_hosts.append(host)
                else:
                    failed_hosts.append(host)
            except Exception as e:
                self.logger.debug(f"Connection to {host}:{port} failed: {e}")
                failed_hosts.append(host)

        # If at least one host is reachable, consider it passing
        passed = len(successful_hosts) > 0

        if passed:
            return ValidationResult(
                validator_name=self.name,
                severity=self.severity,
                passed=True,
                message="Internet connectivity available",
                details=f"Successfully connected to {len(successful_hosts)} host(s)",
                current_value=f"{len(successful_hosts)}/{len(self.TEST_HOSTS)} hosts reachable",
                required_value="At least 1 host reachable",
            )
        else:
            return ValidationResult(
                validator_name=self.name,
                severity=self.severity,
                passed=False,
                message="No internet connectivity",
                details=(
                    f"Unable to reach any test hosts: {', '.join([h for h, _ in self.TEST_HOSTS])}"
                ),
                current_value="0 hosts reachable",
                required_value="At least 1 host reachable",
                fix_suggestion=(
                    "Check network configuration:\n"
                    "  1. Verify network interface: ip addr show\n"
                    "  2. Check gateway: ip route show\n"
                    "  3. Test DNS: ping 8.8.8.8\n"
                    "  4. Check firewall: sudo ufw status"
                ),
            )
