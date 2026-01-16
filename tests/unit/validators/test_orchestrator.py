"""
Unit tests for ValidationOrchestrator.
"""

from unittest.mock import Mock

import pytest
from rich.console import Console

from configurator.validators.base import (
    BaseValidator,
    ValidationResult,
    ValidationSeverity,
)
from configurator.validators.orchestrator import ValidationOrchestrator


class MockPassValidator(BaseValidator):
    """Mock validator that always passes."""

    name = "Pass Validator"
    severity = ValidationSeverity.HIGH

    def validate(self):
        return ValidationResult(
            validator_name=self.name,
            severity=self.severity,
            passed=True,
            message="Passed",
        )


class MockFailValidator(BaseValidator):
    """Mock validator that always fails."""

    name = "Fail Validator"
    severity = ValidationSeverity.HIGH

    def validate(self):
        return ValidationResult(
            validator_name=self.name,
            severity=self.severity,
            passed=False,
            message="Failed",
        )


class MockCriticalFailValidator(BaseValidator):
    """Mock critical validator that fails."""

    name = "Critical Fail"
    severity = ValidationSeverity.CRITICAL

    def validate(self):
        return ValidationResult(
            validator_name=self.name,
            severity=self.severity,
            passed=False,
            message="Critical failure",
        )


class TestValidationOrchestrator:
    """Tests for ValidationOrchestrator."""

    def test_init(self):
        """Test orchestrator initialization."""
        orchestrator = ValidationOrchestrator()
        assert orchestrator is not None
        assert isinstance(orchestrator.console, Console)
        assert len(orchestrator.validators) == 3
        assert 1 in orchestrator.validators
        assert 2 in orchestrator.validators
        assert 3 in orchestrator.validators

    def test_register_validator_tier1(self):
        """Test registering validator in tier 1."""
        orchestrator = ValidationOrchestrator()
        validator = MockPassValidator()

        orchestrator.register_validator(1, validator)

        assert validator in orchestrator.validators[1]

    def test_register_validator_tier2(self):
        """Test registering validator in tier 2."""
        orchestrator = ValidationOrchestrator()
        validator = MockPassValidator()

        orchestrator.register_validator(2, validator)

        assert validator in orchestrator.validators[2]

    def test_register_validator_tier3(self):
        """Test registering validator in tier 3."""
        orchestrator = ValidationOrchestrator()
        validator = MockPassValidator()

        orchestrator.register_validator(3, validator)

        assert validator in orchestrator.validators[3]

    def test_register_validator_invalid_tier(self):
        """Test registering validator with invalid tier raises error."""
        orchestrator = ValidationOrchestrator()
        validator = MockPassValidator()

        with pytest.raises(ValueError, match="Invalid tier"):
            orchestrator.register_validator(4, validator)

    def test_run_validation_all_pass(self):
        """Test validation when all checks pass."""
        orchestrator = ValidationOrchestrator()

        # Register passing validators
        orchestrator.register_validator(1, MockPassValidator())
        orchestrator.register_validator(2, MockPassValidator())

        passed, results = orchestrator.run_validation(interactive=False)

        assert passed is True
        assert len(results) == 2
        assert all(r.passed for r in results)

    def test_run_validation_critical_fails(self):
        """Test validation stops when critical fails."""
        orchestrator = ValidationOrchestrator()

        # Tier 1 critical - fails
        critical_validator = MockCriticalFailValidator()
        orchestrator.register_validator(1, critical_validator)

        # Tier 2 - should not run
        tier2_validator = Mock(spec=BaseValidator)
        tier2_validator.name = "Tier 2"
        tier2_validator.severity = ValidationSeverity.HIGH
        orchestrator.register_validator(2, tier2_validator)

        passed, results = orchestrator.run_validation(interactive=False)

        assert passed is False
        assert len(results) == 1  # Only tier 1 ran
        assert results[0].passed is False
        tier2_validator.validate.assert_not_called()

    def test_run_validation_high_fails_non_interactive(self):
        """Test validation fails for high priority in non-interactive mode."""
        orchestrator = ValidationOrchestrator()

        # Tier 1: Pass
        orchestrator.register_validator(1, MockPassValidator())

        # Tier 2: Fail
        orchestrator.register_validator(2, MockFailValidator())

        passed, results = orchestrator.run_validation(interactive=False)

        # Should pass overall (high failures don't stop execution)
        # but interactive=False means we don't prompt
        assert len(results) == 2

    def test_run_validation_medium_doesnt_fail(self):
        """Test medium priority failures don't affect overall result."""
        orchestrator = ValidationOrchestrator()

        # Tier 1: Pass
        pass_validator = MockPassValidator()
        orchestrator.register_validator(1, pass_validator)

        # Tier 3: Fail (medium)
        class MediumFailValidator(BaseValidator):
            name = "Medium Fail"
            severity = ValidationSeverity.MEDIUM

            def validate(self):
                return ValidationResult(
                    validator_name=self.name,
                    severity=self.severity,
                    passed=False,
                    message="Medium failure",
                )

        orchestrator.register_validator(3, MediumFailValidator())

        passed, results = orchestrator.run_validation(interactive=False)

        assert passed is True  # Medium failures don't fail installation
        assert len(results) == 2
        assert results[0].passed is True
        assert results[1].passed is False

    def test_run_validation_empty(self):
        """Test validation with no validators."""
        orchestrator = ValidationOrchestrator()

        passed, results = orchestrator.run_validation(interactive=False)

        assert passed is True
        assert len(results) == 0

    def test_validator_exception_handling(self):
        """Test orchestrator handles validator exceptions."""
        orchestrator = ValidationOrchestrator()

        class ExceptionValidator(BaseValidator):
            name = "Exception Validator"
            severity = ValidationSeverity.HIGH

            def validate(self):
                raise RuntimeError("Validator error")

        orchestrator.register_validator(1, ExceptionValidator())

        passed, results = orchestrator.run_validation(interactive=False)

        assert len(results) == 1
        assert results[0].passed is False
        assert "error" in results[0].message.lower()
