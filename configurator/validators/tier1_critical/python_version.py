"""
Python version validator - Tier 1 Critical.

Validates that Python version is 3.11 or higher.
"""

import sys

from configurator.validators.base import (
    BaseValidator,
    ValidationResult,
    ValidationSeverity,
)


class PythonVersionValidator(BaseValidator):
    """Validate Python version."""

    name = "Python Version"
    severity = ValidationSeverity.CRITICAL
    auto_fix_available = False

    MINIMUM_VERSION = (3, 11)

    def validate(self) -> ValidationResult:
        """
        Check if Python version meets minimum requirements.

        Returns:
            ValidationResult indicating if Python version is sufficient
        """
        current_version = sys.version_info[:2]
        current_version_str = f"{current_version[0]}.{current_version[1]}"
        required_version_str = f"{self.MINIMUM_VERSION[0]}.{self.MINIMUM_VERSION[1]}"

        if current_version >= self.MINIMUM_VERSION:
            return ValidationResult(
                validator_name=self.name,
                severity=self.severity,
                passed=True,
                message="Python version sufficient",
                details=f"Running Python {current_version_str}",
                current_value=f"Python {current_version_str}",
                required_value=f"Python {required_version_str}+",
            )
        else:
            return ValidationResult(
                validator_name=self.name,
                severity=self.severity,
                passed=False,
                message="Python version too old",
                details=f"Running Python {current_version_str}, need {required_version_str}+",
                current_value=f"Python {current_version_str}",
                required_value=f"Python {required_version_str}+",
                fix_suggestion=(
                    f"Install Python {required_version_str} or higher:\n"
                    "  sudo apt update && sudo apt install python3.11 python3.11-venv"
                ),
            )
