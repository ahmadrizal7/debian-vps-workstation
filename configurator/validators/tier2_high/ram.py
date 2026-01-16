"""
RAM validator - Tier 2 High Priority.

Validates that the system has minimum RAM requirements (4GB).
"""

import psutil

from configurator.validators.base import (
    BaseValidator,
    ValidationResult,
    ValidationSeverity,
)


class RAMValidator(BaseValidator):
    """Validate minimum RAM requirement."""

    name = "Minimum RAM"
    severity = ValidationSeverity.HIGH
    auto_fix_available = False

    MINIMUM_RAM_GB = 4

    def validate(self) -> ValidationResult:
        """
        Check if system has minimum RAM.

        Returns:
            ValidationResult indicating if RAM is sufficient
        """
        total_ram_bytes = psutil.virtual_memory().total
        total_ram_gb = total_ram_bytes / (1024**3)

        passed = total_ram_gb >= self.MINIMUM_RAM_GB

        if passed:
            return ValidationResult(
                validator_name=self.name,
                severity=self.severity,
                passed=True,
                message="RAM requirement met",
                details=f"System has {total_ram_gb:.1f}GB RAM",
                current_value=f"{total_ram_gb:.1f}GB",
                required_value=f"{self.MINIMUM_RAM_GB}GB minimum",
            )
        else:
            return ValidationResult(
                validator_name=self.name,
                severity=self.severity,
                passed=False,
                message="Insufficient RAM",
                details=f"System has {total_ram_gb:.1f}GB RAM, need {self.MINIMUM_RAM_GB}GB",
                current_value=f"{total_ram_gb:.1f}GB",
                required_value=f"{self.MINIMUM_RAM_GB}GB minimum",
                fix_suggestion=(
                    "Upgrade VPS plan to increase RAM. "
                    "Installation may fail or run slowly with insufficient memory."
                ),
            )
