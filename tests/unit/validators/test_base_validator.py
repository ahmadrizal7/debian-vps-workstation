"""
Unit tests for base validator infrastructure.
"""

import logging

import pytest

from configurator.validators.base import (
    BaseValidator,
    ValidationResult,
    ValidationSeverity,
)


class TestValidationSeverity:
    """Tests for ValidationSeverity enum."""

    def test_severity_levels_exist(self):
        """Test all severity levels are defined."""
        assert ValidationSeverity.CRITICAL.value == "critical"
        assert ValidationSeverity.HIGH.value == "high"
        assert ValidationSeverity.MEDIUM.value == "medium"
        assert ValidationSeverity.INFO.value == "info"

    def test_severity_count(self):
        """Test exactly 4 severity levels exist."""
        assert len(ValidationSeverity) == 4


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_icon_passed(self):
        """Test icon for passed validation."""
        result = ValidationResult(
            validator_name="Test",
            severity=ValidationSeverity.CRITICAL,
            passed=True,
            message="OK",
        )
        assert result.icon == "✅"

    def test_icon_failed_critical(self):
        """Test icon for failed critical validation."""
        result = ValidationResult(
            validator_name="Test",
            severity=ValidationSeverity.CRITICAL,
            passed=False,
            message="Failed",
        )
        assert result.icon == "❌"

    def test_icon_failed_high(self):
        """Test icon for failed high priority validation."""
        result = ValidationResult(
            validator_name="Test",
            severity=ValidationSeverity.HIGH,
            passed=False,
            message="Failed",
        )
        assert result.icon == "⚠️"

    def test_icon_failed_medium(self):
        """Test icon for failed medium priority validation."""
        result = ValidationResult(
            validator_name="Test",
            severity=ValidationSeverity.MEDIUM,
            passed=False,
            message="Failed",
        )
        assert result.icon == "⚠️"

    def test_icon_info(self):
        """Test icon for info level."""
        result = ValidationResult(
            validator_name="Test",
            severity=ValidationSeverity.INFO,
            passed=False,
            message="Info",
        )
        assert result.icon == "ℹ️"

    def test_all_required_fields(self):
        """Test ValidationResult with all fields."""
        result = ValidationResult(
            validator_name="Test Validator",
            severity=ValidationSeverity.HIGH,
            passed=False,
            message="Test failed",
            details="Detailed information",
            fix_suggestion="How to fix",
            auto_fixable=True,
            current_value="1GB",
            required_value="4GB",
        )

        assert result.validator_name == "Test Validator"
        assert result.severity == ValidationSeverity.HIGH
        assert result.passed is False
        assert result.message == "Test failed"
        assert result.details == "Detailed information"
        assert result.fix_suggestion == "How to fix"
        assert result.auto_fixable is True
        assert result.current_value == "1GB"
        assert result.required_value == "4GB"


class TestBaseValidator:
    """Tests for BaseValidator abstract class."""

    def test_cannot_instantiate_directly(self):
        """Test BaseValidator is abstract and cannot be instantiated."""
        with pytest.raises(TypeError):
            BaseValidator()

    def test_concrete_validator_can_instantiate(self):
        """Test concrete validator can be instantiated."""

        class ConcreteValidator(BaseValidator):
            def validate(self):
                return ValidationResult(
                    validator_name="Concrete",
                    severity=ValidationSeverity.HIGH,
                    passed=True,
                    message="OK",
                )

        validator = ConcreteValidator()
        assert validator is not None
        assert isinstance(validator.logger, logging.Logger)

    def test_auto_fix_not_implemented_by_default(self):
        """Test auto_fix raises NotImplementedError by default."""

        class TestValidator(BaseValidator):
            def validate(self):
                return ValidationResult(
                    validator_name="Test",
                    severity=ValidationSeverity.HIGH,
                    passed=False,
                    message="Failed",
                )

        validator = TestValidator()
        with pytest.raises(NotImplementedError):
            validator.auto_fix()

    def test_get_user_prompt_basic(self):
        """Test get_user_prompt formats basic message."""

        class TestValidator(BaseValidator):
            name = "Test Validator"

            def validate(self):
                pass

        validator = TestValidator()
        result = ValidationResult(
            validator_name="Test",
            severity=ValidationSeverity.HIGH,
            passed=False,
            message="Test failed",
        )

        prompt = validator.get_user_prompt(result)
        assert "⚠️" in prompt
        assert "Test failed" in prompt

    def test_get_user_prompt_with_details(self):
        """Test get_user_prompt includes all details."""

        class TestValidator(BaseValidator):
            def validate(self):
                pass

        validator = TestValidator()
        result = ValidationResult(
            validator_name="Test",
            severity=ValidationSeverity.HIGH,
            passed=False,
            message="Test failed",
            details="More info",
            current_value="1GB",
            required_value="4GB",
            fix_suggestion="Add more RAM",
        )

        prompt = validator.get_user_prompt(result)
        assert "Test failed" in prompt
        assert "More info" in prompt
        assert "1GB" in prompt
        assert "4GB" in prompt
        assert "Add more RAM" in prompt

    def test_custom_logger(self):
        """Test validator can use custom logger."""

        class TestValidator(BaseValidator):
            def validate(self):
                return ValidationResult(
                    validator_name="Test",
                    severity=ValidationSeverity.HIGH,
                    passed=True,
                    message="OK",
                )

        custom_logger = logging.getLogger("custom")
        validator = TestValidator(logger=custom_logger)

        assert validator.logger is custom_logger

    def test_class_attributes(self):
        """Test BaseValidator class attributes."""

        class TestValidator(BaseValidator):
            name = "Test Validator"
            severity = ValidationSeverity.CRITICAL
            auto_fix_available = True

            def validate(self):
                pass

        assert TestValidator.name == "Test Validator"
        assert TestValidator.severity == ValidationSeverity.CRITICAL
        assert TestValidator.auto_fix_available is True
