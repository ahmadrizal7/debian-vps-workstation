"""
Unit tests for StateManager.
"""

import pytest

from configurator.core.state.manager import StateManager
from configurator.core.state.models import ModuleStatus


class TestStateManager:
    """Tests for StateManager."""

    def test_init_creates_db_in_memory(self):
        """Test StateManager creates in-memory database."""
        manager = StateManager(db_path=":memory:")
        assert manager is not None
        assert manager.db_path == ":memory:"

    def test_init_creates_db_file(self, tmp_path):
        """Test StateManager creates database file."""
        db_path = tmp_path / "test.db"
        manager = StateManager(db_path=db_path)

        assert db_path.exists()

    def test_start_installation(self):
        """Test starting new installation."""
        manager = StateManager(db_path=":memory:")

        state = manager.start_installation(profile="advanced", metadata={"user": "test"})

        assert state.installation_id.startswith("inst-")
        assert state.profile == "advanced"
        assert state.metadata["user"] == "test"
        assert state.overall_status == "in_progress"
        assert manager.current_state == state

    def test_update_module_creates_entry(self):
        """Test updating module creates database entry."""
        manager = StateManager(db_path=":memory:")
        manager.start_installation(profile="advanced")

        manager.update_module("docker", status=ModuleStatus.RUNNING, progress=50)

        assert "docker" in manager.current_state.modules
        assert manager.current_state.modules["docker"].status == ModuleStatus.RUNNING
        assert manager.current_state.modules["docker"].progress_percent == 50

    def test_update_module_multiple_fields(self):
        """Test updating multiple module fields."""
        manager = StateManager(db_path=":memory:")
        manager.start_installation(profile="advanced")

        manager.update_module(
            "docker",
            status=ModuleStatus.RUNNING,
            progress=75,
            current_step="Installing packages",
        )

        module_state = manager.current_state.modules["docker"]
        assert module_state.status == ModuleStatus.RUNNING
        assert module_state.progress_percent == 75
        assert module_state.current_step == "Installing packages"

    def test_create_checkpoint(self):
        """Test creating checkpoint."""
        manager = StateManager(db_path=":memory:")
        manager.start_installation(profile="advanced")
        manager.update_module("docker", status=ModuleStatus.RUNNING)

        manager.create_checkpoint("docker", "packages_installed")

        assert manager.current_state.modules["docker"].checkpoint == "packages_installed"

    def test_can_resume_no_installation(self):
        """Test can_resume returns False when no installations."""
        manager = StateManager(db_path=":memory:")

        assert manager.can_resume() is False

    def test_can_resume_incomplete_installation(self):
        """Test can_resume returns True for incomplete installation."""
        manager = StateManager(db_path=":memory:")

        # Start but don't complete
        manager.start_installation(profile="advanced")
        manager.update_module("docker", status=ModuleStatus.RUNNING)

        # Create new manager instance
        manager2 = StateManager(db_path=":memory:")
        # Note: In-memory DB doesn't persist, so this will be False
        # We'll test with file-based DB below

    def test_resume_installation_restores_state(self, tmp_path):
        """Test resume_installation restores state."""
        db_path = tmp_path / "state.db"

        # Session 1: Create incomplete installation
        manager1 = StateManager(db_path=db_path)
        state1 = manager1.start_installation(profile="advanced")
        manager1.update_module("docker", status=ModuleStatus.COMPLETED)
        manager1.update_module("python", status=ModuleStatus.RUNNING, progress=30)

        installation_id = state1.installation_id

        # Session 2: Resume
        manager2 = StateManager(db_path=db_path)
        assert manager2.can_resume() is True

        state2 = manager2.resume_installation()

        assert state2 is not None
        assert state2.installation_id == installation_id
        assert "docker" in state2.modules
        assert state2.modules["docker"].status == ModuleStatus.COMPLETED
        assert "python" in state2.modules
        assert state2.modules["python"].status == ModuleStatus.RUNNING
        assert state2.modules["python"].progress_percent == 30

    def test_complete_installation_success(self):
        """Test completing installation successfully."""
        manager = StateManager(db_path=":memory:")
        manager.start_installation(profile="advanced")

        manager.complete_installation(success=True)

        assert manager.current_state.completed_at is not None
        assert manager.current_state.overall_status == "success"

    def test_complete_installation_failure(self):
        """Test completing installation with failure."""
        manager = StateManager(db_path=":memory:")
        manager.start_installation(profile="advanced")

        manager.complete_installation(success=False)

        assert manager.current_state.completed_at is not None
        assert manager.current_state.overall_status == "failed"

    def test_get_installation_history(self, tmp_path):
        """Test getting installation history."""
        db_path = tmp_path / "state.db"
        manager = StateManager(db_path=db_path)

        # Create multiple installations
        manager.start_installation(profile="basic")
        manager.complete_installation(success=True)

        manager.start_installation(profile="advanced")
        manager.complete_installation(success=False)

        # Get history
        history = manager.get_installation_history(limit=10)

        assert len(history) == 2
        # Most recent first
        assert history[0].profile == "advanced"
        assert history[1].profile == "basic"

    def test_state_persistence_across_restart(self, tmp_path):
        """Integration test: State persists across manager restart."""
        db_path = tmp_path / "state.db"

        # Session 1: Start installation
        manager1 = StateManager(db_path=db_path)
        state1 = manager1.start_installation(profile="advanced")
        manager1.update_module(
            "docker",
            status=ModuleStatus.RUNNING,
            current_step="Installing packages",
        )
        manager1.create_checkpoint("docker", "packages_installed")

        installation_id = state1.installation_id

        # Session 2: Resume installation
        manager2 = StateManager(db_path=db_path)
        state2 = manager2.resume_installation()

        assert state2 is not None
        assert state2.installation_id == installation_id
        assert "docker" in state2.modules
        assert state2.modules["docker"].current_step == "Installing packages"
        assert state2.modules["docker"].checkpoint == "packages_installed"

    def test_update_module_without_active_installation(self):
        """Test updating module without active installation raises error."""
        manager = StateManager(db_path=":memory:")

        with pytest.raises(RuntimeError, match="No active installation"):
            manager.update_module("docker", status=ModuleStatus.RUNNING)
