"""
Recommended RAM validator - Tier 3 Medium Priority.

Validates that the system has recommended RAM (8GB) for optimal performance.
"""

import psutil

from configurator.validators.base import (
    BaseValidator,
    ValidationResult,
    ValidationSeverity,
)


class RecommendedRAMValidator(BaseValidator):
    """Validate recommended RAM for optimal performance."""

    name = "Recommended RAM"
    severity = ValidationSeverity.MEDIUM
    auto_fix_available = False

    RECOMMENDED_RAM_GB = 8

    def validate(self) -> ValidationResult:
        """
        Check if system has recommended RAM.

        Returns:
            ValidationResult indicating if RAM meets recommendations
        """
        total_ram_bytes = psutil.virtual_memory().total
        total_ram_gb = total_ram_bytes / (1024**3)

        passed = total_ram_gb >= self.RECOMMENDED_RAM_GB

        if passed:
            return ValidationResult(
                validator_name=self.name,
                severity=self.severity,
                passed=True,
                message="RAM meets recommended specifications",
                details=f"System has {total_ram_gb:.1f}GB RAM",
                current_value=f"{total_ram_gb:.1f}GB",
                required_value=f"{self.RECOMMENDED_RAM_GB}GB recommended",
            )
        else:
            return ValidationResult(
                validator_name=self.name,
                severity=self.severity,
                passed=False,
                message="RAM below recommended amount",
                details=(
                    f"System has {total_ram_gb:.1f}GB RAM, recommended {self.RECOMMENDED_RAM_GB}GB"
                ),
                current_value=f"{total_ram_gb:.1f}GB",
                required_value=f"{self.RECOMMENDED_RAM_GB}GB recommended",
                fix_suggestion=(
                    f"For optimal performance, consider upgrading to "
                    f"{self.RECOMMENDED_RAM_GB}GB RAM. "
                    "Installation will proceed but may be slower with limited modules."
                ),
            )
