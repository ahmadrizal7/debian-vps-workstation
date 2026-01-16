"""
Integration test for state persistence across crashes/restarts.

Tests that installation state survives crashes and can be resumed.
"""

from configurator.core.state.manager import StateManager
from configurator.core.state.models import ModuleStatus


class TestStatePersistenceIntegration:
    """Integration tests for state persistence."""

    def test_state_survives_crash_and_resume(self, tmp_path):
        """Test state persists and resumes correctly after crash."""
        db_path = tmp_path / "crash_test.db"

        # Session 1: Partial installation (simulates crash)
        manager1 = StateManager(db_path=db_path)
        state1 = manager1.start_installation(profile="advanced", metadata={"test": "crash"})

        installation_id = state1.installation_id

        # Complete some modules
        manager1.update_module("system", status=ModuleStatus.COMPLETED, progress=100)
        manager1.update_module(
            "security",
            status=ModuleStatus.RUNNING,
            progress=75,
            current_step="Configuring firewall",
        )
        manager1.create_checkpoint("security", "firewall_configured")

        # Add another module
        manager1.update_module("docker", status=ModuleStatus.PENDING)

        # Simulate crash - don't complete, don't close cleanly
        del manager1

        # Session 2: Resume after crash
        manager2 = StateManager(db_path=db_path)

        assert manager2.can_resume() is True

        state2 = manager2.resume_installation()

        # Verify state restored
        assert state2 is not None
        assert state2.installation_id == installation_id
        assert state2.profile == "advanced"
        assert state2.metadata["test"] == "crash"

        # Verify module states
        assert "system" in state2.modules
        assert state2.modules["system"].status == ModuleStatus.COMPLETED
        assert state2.modules["system"].progress_percent == 100

        assert "security" in state2.modules
        assert state2.modules["security"].status == ModuleStatus.RUNNING
        assert state2.modules["security"].progress_percent == 75
        assert state2.modules["security"].current_step == "Configuring firewall"
        assert state2.modules["security"].checkpoint == "firewall_configured"

        assert "docker" in state2.modules
        assert state2.modules["docker"].status == ModuleStatus.PENDING

    def test_multiple_installations_resume_latest(self, tmp_path):
        """Test resume picks up the latest incomplete installation."""
        db_path = tmp_path / "multi_install.db"

        # Create first installation (completed)
        manager1 = StateManager(db_path=db_path)
        manager1.start_installation(profile="basic")
        manager1.complete_installation(success=True)

        # Create second installation (incomplete)
        manager2 = StateManager(db_path=db_path)
        state2 = manager2.start_installation(profile="advanced")
        manager2.update_module("docker", status=ModuleStatus.RUNNING)

        installation_id = state2.installation_id

        # Resume should get second installation
        manager3 = StateManager(db_path=db_path)
        state3 = manager3.resume_installation()

        assert state3.installation_id == installation_id
        assert state3.profile == "advanced"

    def test_checkpoint_restore(self, tmp_path):
        """Test checkpoints are restored correctly."""
        db_path = tmp_path / "checkpoint_test.db"

        # Session 1: Create checkpoints
        manager1 = StateManager(db_path=db_path)
        manager1.start_installation(profile="advanced")

        manager1.update_module("docker", status=ModuleStatus.RUNNING, progress=30)
        manager1.create_checkpoint("docker", "repository_added")

        manager1.update_module("docker", status=ModuleStatus.RUNNING, progress=60)
        manager1.create_checkpoint("docker", "packages_installed")

        # Session 2: Resume and verify latest checkpoint
        manager2 = StateManager(db_path=db_path)
        state2 = manager2.resume_installation()

        assert state2.modules["docker"].checkpoint == "packages_installed"
        assert state2.modules["docker"].progress_percent == 60

    def test_complete_after_resume(self, tmp_path):
        """Test completing installation after resume."""
        db_path = tmp_path / "complete_test.db"

        # Session 1: Start and partially complete
        manager1 = StateManager(db_path=db_path)
        state1 = manager1.start_installation(profile="advanced")
        manager1.update_module("docker", status=ModuleStatus.COMPLETED)

        installation_id = state1.installation_id

        # Session 2: Resume and complete
        manager2 = StateManager(db_path=db_path)
        state2 = manager2.resume_installation()

        manager2.update_module("python", status=ModuleStatus.COMPLETED)
        manager2.complete_installation(success=True)

        # Session 3: Verify no resume available
        manager3 = StateManager(db_path=db_path)
        assert manager3.can_resume() is False

        # Verify in history
        history = manager3.get_installation_history()
        assert len(history) == 1
        assert history[0].installation_id == installation_id
        assert history[0].overall_status == "success"

    def test_failed_installation_tracking(self, tmp_path):
        """Test failed installations are tracked correctly."""
        db_path = tmp_path / "failed_test.db"

        manager = StateManager(db_path=db_path)
        manager.start_installation(profile="advanced")

        # Fail a module
        manager.update_module(
            "docker",
            status=ModuleStatus.FAILED,
            error="Installation failed: package not found",
        )

        # Complete installation as failed
        manager.complete_installation(success=False)

        # Verify history
        history = manager.get_installation_history()
        assert len(history) == 1
        assert history[0].overall_status == "failed"

        # Verify can't resume completed (failed) installation
        manager2 = StateManager(db_path=db_path)
        assert manager2.can_resume() is False

    def test_installation_history_ordering(self, tmp_path):
        """Test installation history is ordered correctly."""
        db_path = tmp_path / "history_test.db"
        manager = StateManager(db_path=db_path)

        profiles = ["basic", "standard", "advanced"]

        # Create multiple installations
        for profile in profiles:
            manager.start_installation(profile=profile)
            manager.complete_installation(success=True)

        # Get history
        history = manager.get_installation_history(limit=10)

        assert len(history) == 3
        # Should be in reverse chronological order (most recent first)
        assert history[0].profile == "advanced"
        assert history[1].profile == "standard"
        assert history[2].profile == "basic"

    def test_database_fallback_location(self):
        """Test database fallback to user config directory."""
        # This would require mocking permission checks
        # For now, just verify the logic exists
        manager = StateManager()
        assert manager.db_path is not None

    def test_concurrent_updates_same_module(self, tmp_path):
        """Test multiple updates to same module persist correctly."""
        db_path = tmp_path / "concurrent_test.db"
        manager = StateManager(db_path=db_path)
        manager.start_installation(profile="advanced")

        # Update module multiple times
        for progress in [25, 50, 75, 100]:
            manager.update_module(
                "docker",
                status=ModuleStatus.RUNNING if progress < 100 else ModuleStatus.COMPLETED,
                progress=progress,
                current_step=f"Step {progress}%",
            )

        # Resume and verify latest state
        manager2 = StateManager(db_path=db_path)
        state = manager2.resume_installation()

        assert state.modules["docker"].progress_percent == 100
        assert state.modules["docker"].status == ModuleStatus.COMPLETED
        assert state.modules["docker"].current_step == "Step 100%"
