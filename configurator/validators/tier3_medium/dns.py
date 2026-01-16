"""
DNS resolution validator - Tier 3 Medium Priority.

Validates that DNS resolution is working correctly.
"""

import socket

from configurator.validators.base import (
    BaseValidator,
    ValidationResult,
    ValidationSeverity,
)


class DNSValidator(BaseValidator):
    """Validate DNS resolution."""

    name = "DNS Resolution"
    severity = ValidationSeverity.MEDIUM
    auto_fix_available = False

    TEST_DOMAINS = [
        "debian.org",
        "ubuntu.com",
        "github.com",
    ]

    def validate(self) -> ValidationResult:
        """
        Check if DNS resolution is working.

        Returns:
            ValidationResult indicating if DNS is functional
        """
        successful_lookups = []
        failed_lookups = []

        for domain in self.TEST_DOMAINS:
            try:
                socket.gethostbyname(domain)
                successful_lookups.append(domain)
            except socket.gaierror:
                failed_lookups.append(domain)
            except Exception as e:
                self.logger.debug(f"DNS lookup for {domain} failed: {e}")
                failed_lookups.append(domain)

        # If at least one domain resolves, consider it passing
        passed = len(successful_lookups) > 0

        if passed:
            return ValidationResult(
                validator_name=self.name,
                severity=self.severity,
                passed=True,
                message="DNS resolution working",
                details=(
                    f"Successfully resolved {len(successful_lookups)}/"
                    f"{len(self.TEST_DOMAINS)} domains"
                ),
                current_value=f"{len(successful_lookups)} domains resolved",
                required_value="At least 1 domain resolved",
            )
        else:
            return ValidationResult(
                validator_name=self.name,
                severity=self.severity,
                passed=False,
                message="DNS resolution issues",
                details=f"Unable to resolve any test domains: {', '.join(self.TEST_DOMAINS)}",
                current_value="0 domains resolved",
                required_value="At least 1 domain resolved",
                fix_suggestion=(
                    "Check DNS configuration:\n"
                    "  1. Verify /etc/resolv.conf has nameservers\n"
                    "  2. Test with: dig debian.org\n"
                    "  3. Try switching DNS: echo 'nameserver 8.8.8.8' | sudo tee /etc/resolv.conf"
                ),
            )
