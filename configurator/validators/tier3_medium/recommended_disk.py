"""
Recommended disk space validator - Tier 3 Medium Priority.

Validates that the system has recommended disk space (40GB) for optimal use.
"""

import shutil

from configurator.validators.base import (
    BaseValidator,
    ValidationResult,
    ValidationSeverity,
)


class RecommendedDiskValidator(BaseValidator):
    """Validate recommended disk space for optimal use."""

    name = "Recommended Disk Space"
    severity = ValidationSeverity.MEDIUM
    auto_fix_available = False

    RECOMMENDED_DISK_GB = 40

    def validate(self) -> ValidationResult:
        """
        Check if system has recommended disk space.

        Returns:
            ValidationResult indicating if disk space meets recommendations
        """
        try:
            stat = shutil.disk_usage("/")
            free_gb = stat.free / (1024**3)
        except Exception as e:
            self.logger.error(f"Failed to check disk space: {e}")
            return ValidationResult(
                validator_name=self.name,
                severity=self.severity,
                passed=False,
                message="Unable to check disk space",
                details=str(e),
            )

        passed = free_gb >= self.RECOMMENDED_DISK_GB

        if passed:
            return ValidationResult(
                validator_name=self.name,
                severity=self.severity,
                passed=True,
                message="Disk space meets recommended specifications",
                details=f"{free_gb:.1f}GB free space available",
                current_value=f"{free_gb:.1f}GB free",
                required_value=f"{self.RECOMMENDED_DISK_GB}GB recommended",
            )
        else:
            return ValidationResult(
                validator_name=self.name,
                severity=self.severity,
                passed=False,
                message="Disk space below recommended amount",
                details=f"Only {free_gb:.1f}GB free, recommended {self.RECOMMENDED_DISK_GB}GB",
                current_value=f"{free_gb:.1f}GB free",
                required_value=f"{self.RECOMMENDED_DISK_GB}GB recommended",
                fix_suggestion=(
                    f"For optimal use, consider upgrading storage to have "
                    f"{self.RECOMMENDED_DISK_GB}GB free. "
                    "Installation will proceed but disk space may become tight "
                    "with all modules."
                ),
            )
