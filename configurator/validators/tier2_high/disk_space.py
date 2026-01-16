"""
Disk space validator - Tier 2 High Priority.

Validates that the system has minimum disk space (20GB free).
"""

import shutil

from configurator.validators.base import (
    BaseValidator,
    ValidationResult,
    ValidationSeverity,
)


class DiskSpaceValidator(BaseValidator):
    """Validate minimum disk space requirement."""

    name = "Minimum Disk Space"
    severity = ValidationSeverity.HIGH
    auto_fix_available = False

    MINIMUM_DISK_GB = 20

    def validate(self) -> ValidationResult:
        """
        Check if system has minimum free disk space.

        Returns:
            ValidationResult indicating if disk space is sufficient
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
                fix_suggestion="Verify disk access and permissions",
            )

        passed = free_gb >= self.MINIMUM_DISK_GB

        if passed:
            return ValidationResult(
                validator_name=self.name,
                severity=self.severity,
                passed=True,
                message="Disk space requirement met",
                details=f"{free_gb:.1f}GB free space available",
                current_value=f"{free_gb:.1f}GB free",
                required_value=f"{self.MINIMUM_DISK_GB}GB minimum",
            )
        else:
            return ValidationResult(
                validator_name=self.name,
                severity=self.severity,
                passed=False,
                message="Insufficient disk space",
                details=f"Only {free_gb:.1f}GB free, need {self.MINIMUM_DISK_GB}GB",
                current_value=f"{free_gb:.1f}GB free",
                required_value=f"{self.MINIMUM_DISK_GB}GB minimum",
                fix_suggestion=(
                    "Free up disk space or upgrade VPS storage. "
                    "Installation will fail without sufficient disk space."
                ),
            )
