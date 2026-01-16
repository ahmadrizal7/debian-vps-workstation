"""
Operating system version validator - Tier 1 Critical.

Validates that the system is running a supported OS version.
"""

from configurator.utils.system import get_os_info
from configurator.validators.base import (
    BaseValidator,
    ValidationResult,
    ValidationSeverity,
)


class OSVersionValidator(BaseValidator):
    """Validate operating system version."""

    name = "Operating System Version"
    severity = ValidationSeverity.CRITICAL
    auto_fix_available = False

    SUPPORTED_OS = {
        "debian": ["13"],
        "ubuntu": ["22.04", "24.04"],
    }

    def validate(self) -> ValidationResult:
        """
        Check if OS is supported.

        Returns:
            ValidationResult indicating if OS version is supported
        """
        os_info = get_os_info()
        if hasattr(os_info.name, "lower"):
            os_name = os_info.name.lower()
        else:
            os_name = str(os_info.name).lower()

        # Check if OS type is supported
        if os_name not in self.SUPPORTED_OS:
            return ValidationResult(
                validator_name=self.name,
                severity=self.severity,
                passed=False,
                message="Unsupported operating system",
                details=f"Detected: {os_info.pretty_name}",
                current_value=os_name,
                required_value=f"One of: {', '.join(self.SUPPORTED_OS.keys())}",
                fix_suggestion=(
                    "This installer requires Debian 13 (Trixie) or Ubuntu 22.04/24.04. "
                    "Please use a VPS with a supported operating system."
                ),
            )

        # Check if version is supported for this OS
        supported_versions = self.SUPPORTED_OS[os_name]
        if os_info.version_id not in supported_versions:
            return ValidationResult(
                validator_name=self.name,
                severity=self.severity,
                passed=False,
                message=f"Unsupported {os_info.name} version",
                details=f"Detected: {os_info.pretty_name}",
                current_value=f"{os_info.name} {os_info.version_id}",
                required_value=f"{os_info.name} {' or '.join(supported_versions)}",
                fix_suggestion=(
                    f"Upgrade to {os_info.name} {' or '.join(supported_versions)}, "
                    "or provision a new VPS with a supported version."
                ),
            )

        # All checks passed
        return ValidationResult(
            validator_name=self.name,
            severity=self.severity,
            passed=True,
            message="Operating system supported",
            details=f"Running {os_info.pretty_name}",
            current_value=f"{os_info.name} {os_info.version_id}",
            required_value=f"{os_info.name} {' or '.join(supported_versions)}",
        )
