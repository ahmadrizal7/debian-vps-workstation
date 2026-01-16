"""
Unit tests for state models.
"""

from datetime import datetime

from configurator.core.state.models import (
    InstallationState,
    ModuleState,
    ModuleStatus,
)


class TestModuleStatus:
    """Tests for ModuleStatus enum."""

    def test_all_statuses_exist(self):
        """Test all module statuses are defined."""
        assert ModuleStatus.PENDING.value == "pending"
        assert ModuleStatus.RUNNING.value == "running"
        assert ModuleStatus.COMPLETED.value == "completed"
        assert ModuleStatus.FAILED.value == "failed"
        assert ModuleStatus.SKIPPED.value == "skipped"
        assert ModuleStatus.ROLLED_BACK.value == "rolled_back"


class TestModuleState:
    """Tests for ModuleState."""

    def test_init_defaults(self):
        """Test ModuleState initialization with defaults."""
        state = ModuleState(name="test")

        assert state.name == "test"
        assert state.status == ModuleStatus.PENDING
        assert state.started_at is None
        assert state.completed_at is None
        assert state.duration_seconds is None
        assert state.progress_percent == 0
        assert state.current_step == ""
        assert state.error_message is None
        assert state.checkpoint is None
        assert state.rollback_actions == []

    def test_serialization(self):
        """Test ModuleState to_dict() and from_dict()."""
        original = ModuleState(
            name="docker",
            status=ModuleStatus.COMPLETED,
            started_at=datetime(2026, 1, 16, 10, 0, 0),
            completed_at=datetime(2026, 1, 16, 10, 5, 0),
            duration_seconds=300.0,
            progress_percent=100,
            current_step="Finished",
            checkpoint="packages_installed",
        )

        data = original.to_dict()
        restored = ModuleState.from_dict(data)

        assert restored.name == original.name
        assert restored.status == original.status
        assert restored.started_at == original.started_at
        assert restored.completed_at == original.completed_at
        assert restored.duration_seconds == original.duration_seconds
        assert restored.progress_percent == original.progress_percent
        assert restored.current_step == original.current_step
        assert restored.checkpoint == original.checkpoint

    def test_mark_started(self):
        """Test marking module as started."""
        state = ModuleState(name="test")

        state.mark_started()

        assert state.status == ModuleStatus.RUNNING
        assert state.started_at is not None

    def test_mark_completed(self):
        """Test marking module as completed."""
        state = ModuleState(name="test")
        state.mark_started()

        state.mark_completed()

        assert state.status == ModuleStatus.COMPLETED
        assert state.completed_at is not None
        assert state.progress_percent == 100
        assert state.duration_seconds is not None
        assert state.duration_seconds > 0

    def test_mark_failed(self):
        """Test marking module as failed."""
        state = ModuleState(name="test")
        state.mark_started()

        state.mark_failed("Test error")

        assert state.status == ModuleStatus.FAILED
        assert state.completed_at is not None
        assert state.error_message == "Test error"
        assert state.duration_seconds is not None


class TestInstallationState:
    """Tests for InstallationState."""

    def test_init_defaults(self):
        """Test InstallationState initialization."""
        state = InstallationState(
            installation_id="test-123",
            started_at=datetime.now(),
            profile="advanced",
        )

        assert state.installation_id == "test-123"
        assert state.profile == "advanced"
        assert state.modules == {}
        assert state.completed_at is None
        assert state.overall_status == "in_progress"
        assert state.metadata == {}

    def test_serialization(self):
        """Test InstallationState to_dict() and from_dict()."""
        original = InstallationState(
            installation_id="test-123",
            started_at=datetime(2026, 1, 16, 10, 0, 0),
            profile="advanced",
            metadata={"user": "test"},
        )

        original.modules["docker"] = ModuleState(name="docker", status=ModuleStatus.COMPLETED)

        data = original.to_dict()
        restored = InstallationState.from_dict(data)

        assert restored.installation_id == original.installation_id
        assert restored.profile == original.profile
        assert restored.metadata == original.metadata
        assert "docker" in restored.modules
        assert restored.modules["docker"].status == ModuleStatus.COMPLETED

    def test_get_progress_percent_empty(self):
        """Test progress calculation with no modules."""
        state = InstallationState(
            installation_id="test",
            started_at=datetime.now(),
            profile="advanced",
        )

        assert state.get_progress_percent() == 0

    def test_get_progress_percent_partial(self):
        """Test progress calculation with partial completion."""
        state = InstallationState(
            installation_id="test",
            started_at=datetime.now(),
            profile="advanced",
        )

        state.modules["m1"] = ModuleState(name="m1", progress_percent=100)
        state.modules["m2"] = ModuleState(name="m2", progress_percent=50)
        state.modules["m3"] = ModuleState(name="m3", progress_percent=0)

        # Average: (100 + 50 + 0) / 3 = 50
        assert state.get_progress_percent() == 50

    def test_is_complete_false(self):
        """Test is_complete returns False for incomplete installation."""
        state = InstallationState(
            installation_id="test",
            started_at=datetime.now(),
            profile="advanced",
        )

        state.modules["m1"] = ModuleState(name="m1", status=ModuleStatus.COMPLETED)
        state.modules["m2"] = ModuleState(name="m2", status=ModuleStatus.RUNNING)

        assert state.is_complete() is False

    def test_is_complete_true(self):
        """Test is_complete returns True when all modules done."""
        state = InstallationState(
            installation_id="test",
            started_at=datetime.now(),
            profile="advanced",
        )

        state.modules["m1"] = ModuleState(name="m1", status=ModuleStatus.COMPLETED)
        state.modules["m2"] = ModuleState(name="m2", status=ModuleStatus.SKIPPED)

        assert state.is_complete() is True

    def test_has_failures_false(self):
        """Test has_failures returns False when no failures."""
        state = InstallationState(
            installation_id="test",
            started_at=datetime.now(),
            profile="advanced",
        )

        state.modules["m1"] = ModuleState(name="m1", status=ModuleStatus.COMPLETED)

        assert state.has_failures() is False

    def test_has_failures_true(self):
        """Test has_failures returns True when module failed."""
        state = InstallationState(
            installation_id="test",
            started_at=datetime.now(),
            profile="advanced",
        )

        state.modules["m1"] = ModuleState(name="m1", status=ModuleStatus.COMPLETED)
        state.modules["m2"] = ModuleState(name="m2", status=ModuleStatus.FAILED)

        assert state.has_failures() is True
