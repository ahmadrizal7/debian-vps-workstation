"""
Integration tests for rollback scenarios.

Tests:
- Rollback after partial installation failure
- Rollback preserves system state
- Rollback order is correct (LIFO)
- Rollback continuation on individual action failure
"""

import threading
from unittest.mock import Mock, patch

import pytest

from configurator.core.rollback import RollbackManager


@pytest.mark.integration
class TestRollbackLIFOOrder:
    """Test that rollback actions execute in LIFO (Last-In-First-Out) order."""

    def test_rollback_executes_in_reverse_order(self):
        """Test that rollback actions execute in reverse registration order."""
        logger = Mock()
        rollback_mgr = RollbackManager(logger=logger)

        # Track execution order
        execution_order = []

        # Register actions
        rollback_mgr.add_command("action_1", "First action")
        rollback_mgr.add_command("action_2", "Second action")
        rollback_mgr.add_command("action_3", "Third action")

        with patch("configurator.core.rollback.run_command") as mock_run:

            def track_execution(cmd, check=False):
                execution_order.append(cmd)
                return Mock(success=True, returncode=0)

            mock_run.side_effect = track_execution

            rollback_mgr.rollback()

        # Verify LIFO order (last registered executes first)
        assert len(execution_order) == 3
        assert execution_order[0] == "action_3", "Last action should execute first"
        assert execution_order[1] == "action_2", "Second action should execute second"
        assert execution_order[2] == "action_1", "First action should execute last"

    def test_rollback_actions_cleared_after_execution(self):
        """Test that rollback actions are cleared after successful rollback."""
        logger = Mock()
        rollback_mgr = RollbackManager(logger=logger)

        rollback_mgr.add_command("test_action", "Test")

        with patch("configurator.core.rollback.run_command", return_value=Mock(success=True)):
            rollback_mgr.rollback()

        # Actions should be cleared
        assert len(rollback_mgr.actions) == 0


@pytest.mark.integration
class TestRollbackContinuation:
    """Test that rollback continues even when individual actions fail."""

    def test_rollback_continues_on_failure(self):
        """Test that rollback continues executing remaining actions on failure."""
        logger = Mock()
        rollback_mgr = RollbackManager(logger=logger)

        execution_order = []

        rollback_mgr.add_command("action_1", "First")
        rollback_mgr.add_command("action_fail", "Failing action")
        rollback_mgr.add_command("action_3", "Third")

        with patch("configurator.core.rollback.run_command") as mock_run:

            def run_with_failure(cmd, check=False):
                execution_order.append(cmd)
                if cmd == "action_fail":
                    raise Exception("Simulated failure")
                return Mock(success=True, returncode=0)

            mock_run.side_effect = run_with_failure

            # Rollback should not raise exception
            rollback_mgr.rollback()

        # All actions should have been attempted
        assert "action_1" in execution_order
        assert "action_fail" in execution_order
        assert "action_3" in execution_order

    def test_rollback_logs_failures(self):
        """Test that rollback logs failures properly."""
        logger = Mock()
        rollback_mgr = RollbackManager(logger=logger)

        rollback_mgr.add_command("failing_action", "This will fail")

        with patch("configurator.core.rollback.run_command") as mock_run:
            mock_run.side_effect = Exception("Test failure")

            rollback_mgr.rollback()

        # Should log error for failed action
        error_calls = [str(c) for c in logger.error.call_args_list]
        assert len(error_calls) > 0


@pytest.mark.integration
class TestRollbackWithFiles:
    """Test rollback with file operations."""

    def test_file_rollback_action_created(self):
        """Test that file restore rollback actions are properly created."""
        logger = Mock()
        rollback_mgr = RollbackManager(logger=logger)

        # Add file restore action
        rollback_mgr.add_file_restore(
            backup_path="/etc/xrdp/xrdp.ini.bak",
            original_path="/etc/xrdp/xrdp.ini",
            description="Restore xrdp.ini",
        )

        assert len(rollback_mgr.actions) == 1
        action = rollback_mgr.actions[0]
        assert action.action_type == "file_restore"
        assert "xrdp.ini" in action.data["original_path"]

    def test_command_rollback_action_created(self):
        """Test that command rollback actions are properly created."""
        logger = Mock()
        rollback_mgr = RollbackManager(logger=logger)

        # Add command action
        rollback_mgr.add_command("rm -rf /usr/share/themes/Nordic", "Remove Nordic theme")

        assert len(rollback_mgr.actions) == 1
        action = rollback_mgr.actions[0]
        assert action.action_type == "command"
        assert "rm -rf" in action.data["command"]
        assert "Nordic" in action.data["command"]


@pytest.mark.integration
class TestRollbackSummary:
    """Test rollback summary functionality."""

    def test_get_summary_returns_action_count(self):
        """Test that get_summary returns action count information."""
        logger = Mock()
        rollback_mgr = RollbackManager(logger=logger)

        rollback_mgr.add_command("action1", "First description")
        rollback_mgr.add_command("action2", "Second description")

        summary = rollback_mgr.get_summary()

        # Should contain count information
        assert "2" in summary or "command" in summary

    def test_empty_rollback_summary(self):
        """Test summary when no actions are registered."""
        logger = Mock()
        rollback_mgr = RollbackManager(logger=logger)

        summary = rollback_mgr.get_summary()

        # Should return indication of no actions
        assert "no" in summary.lower() or "0" in summary


@pytest.mark.integration
class TestRollbackThreadSafety:
    """Test rollback thread safety."""

    def test_concurrent_add_actions(self):
        """Test that adding actions concurrently works."""
        logger = Mock()
        rollback_mgr = RollbackManager(logger=logger)

        # Patch _save_state to avoid file system operations
        with patch.object(rollback_mgr, "_save_state"):

            def add_actions(prefix, count):
                for i in range(count):
                    rollback_mgr.add_command(f"{prefix}_action_{i}", f"{prefix} action {i}")

            threads = []
            for i in range(5):
                t = threading.Thread(target=add_actions, args=(f"thread{i}", 10))
                threads.append(t)
                t.start()

            for t in threads:
                t.join()

        # Should have all 50 actions
        assert len(rollback_mgr.actions) == 50


@pytest.mark.integration
class TestRollbackActionTypes:
    """Test different rollback action types."""

    def test_package_remove_action(self):
        """Test package removal rollback action."""
        logger = Mock()
        rollback_mgr = RollbackManager(logger=logger)

        rollback_mgr.add_package_remove(["nginx", "apache2"], "Remove web servers")

        assert len(rollback_mgr.actions) == 1
        action = rollback_mgr.actions[0]
        assert action.action_type == "package_remove"
        assert "nginx" in action.data["packages"]
        assert "apache2" in action.data["packages"]

    def test_service_stop_action(self):
        """Test service stop rollback action."""
        logger = Mock()
        rollback_mgr = RollbackManager(logger=logger)

        rollback_mgr.add_service_stop("xrdp", "Stop XRDP service")

        assert len(rollback_mgr.actions) == 1
        action = rollback_mgr.actions[0]
        assert action.action_type == "service_stop"
        assert action.data["service"] == "xrdp"
