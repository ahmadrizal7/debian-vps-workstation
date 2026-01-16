"""
Root access validator - Tier 1 Critical.

Validates that the script is running with root/sudo privileges.
"""

import os

from configurator.validators.base import (
    BaseValidator,
    ValidationResult,
    ValidationSeverity,
)


class RootAccessValidator(BaseValidator):
    """Validate root/sudo access."""

    name = "Root Access"
    severity = ValidationSeverity.CRITICAL
    auto_fix_available = False

    def validate(self) -> ValidationResult:
        """
        Check if running with root privileges.

        Returns:
            ValidationResult indicating if user has root access
        """
        has_root = os.geteuid() == 0

        if has_root:
            return ValidationResult(
                validator_name=self.name,
                severity=self.severity,
                passed=True,
                message="Root access available",
                details="Running with root/sudo privileges",
                current_value="root (UID 0)",
                required_value="root (UID 0)",
            )
        else:
            return ValidationResult(
                validator_name=self.name,
                severity=self.severity,
                passed=False,
                message="Root access required",
                details="This installer must be run with root/sudo privileges",
                current_value=f"UID {os.geteuid()}",
                required_value="root (UID 0)",
                fix_suggestion="Run with sudo: sudo vps-configurator install",
            )
