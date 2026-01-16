"""
Tiered validation system for system requirements.

This package provides a comprehensive validation framework with three tiers:
- Tier 1 (Critical): Must pass to continue installation
- Tier 2 (High): Required but can prompt user for confirmation
- Tier 3 (Medium): Warnings only, installation can continue

Exports:
    BaseValidator: Abstract base class for all validators
    ValidationResult: Result of a validation check
    ValidationSeverity: Severity levels for validation results
    ValidationOrchestrator: Orchestrates validation across all tiers
"""

from configurator.validators.base import (
    BaseValidator,
    ValidationResult,
    ValidationSeverity,
)
from configurator.validators.orchestrator import ValidationOrchestrator

__all__ = [
    "BaseValidator",
    "ValidationResult",
    "ValidationSeverity",
    "ValidationOrchestrator",
]
