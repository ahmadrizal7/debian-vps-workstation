"""
Base validator interface and result model.

Provides the abstract base class and result structures for all validation checks.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ValidationSeverity(Enum):
    """Validation result severity levels."""

    CRITICAL = "critical"  # Must pass to continue
    HIGH = "high"  # Required but can prompt user
    MEDIUM = "medium"  # Warning only
    INFO = "info"  # Informational


@dataclass
class ValidationResult:
    """Result of a single validation check."""

    validator_name: str
    severity: ValidationSeverity
    passed: bool
    message: str
    details: Optional[str] = None
    fix_suggestion: Optional[str] = None
    auto_fixable: bool = False
    current_value: Optional[str] = None
    required_value: Optional[str] = None

    @property
    def icon(self) -> str:
        """
        Get status icon based on result.

        Returns:
            Icon emoji: ✅ (passed), ❌ (critical fail), ⚠️ (high/medium fail), ℹ️ (info)
        """
        if self.passed:
            return "✅"

        if self.severity == ValidationSeverity.CRITICAL:
            return "❌"
        elif self.severity == ValidationSeverity.HIGH:
            return "⚠️"
        elif self.severity == ValidationSeverity.MEDIUM:
            return "⚠️"
        else:  # INFO
            return "ℹ️"


class BaseValidator(ABC):
    """
    Abstract base class for all validators.

    All validators must inherit from this class and implement the validate() method.
    Validators can optionally implement auto_fix() if they support automatic remediation.
    """

    name: str = "Unknown Validator"
    severity: ValidationSeverity = ValidationSeverity.HIGH
    auto_fix_available: bool = False

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize validator.

        Args:
            logger: Optional logger instance. If not provided, creates one from class name.
        """
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def validate(self) -> ValidationResult:
        """
        Perform validation check.

        This method must be implemented by all subclasses.

        Returns:
            ValidationResult with details about the validation outcome
        """
        pass

    def auto_fix(self) -> bool:
        """
        Attempt to automatically fix the validation issue.

        This method should be overridden by subclasses that support auto-fixing.

        Returns:
            True if fix was successful, False otherwise

        Raises:
            NotImplementedError: If auto-fix is not implemented for this validator
        """
        raise NotImplementedError(f"Auto-fix not implemented for {self.__class__.__name__}")

    def get_user_prompt(self, result: ValidationResult) -> str:
        """
        Get user-friendly prompt for failed validation.

        Args:
            result: The validation result to format

        Returns:
            Formatted string with icon, message, and optional fix suggestion
        """
        lines = [
            f"{result.icon} {result.message}",
        ]

        if result.details:
            lines.append(f"   Details: {result.details}")

        if result.current_value:
            lines.append(f"   Current: {result.current_value}")

        if result.required_value:
            lines.append(f"   Required: {result.required_value}")

        if result.fix_suggestion:
            lines.append(f"\n   💡 Fix: {result.fix_suggestion}")

        return "\n".join(lines)
