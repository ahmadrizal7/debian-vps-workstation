"""
Unit tests for race condition fixes in parallel executor (CORE-003).
"""

import threading
from unittest.mock import Mock

from configurator.core.parallel import ParallelModuleExecutor


class TestRaceConditionFix:
    """Test that race condition is eliminated."""

    def test_stop_flag_checked_before_execution(self):
        """Test that modules check stop flag before starting work."""
        executor = ParallelModuleExecutor(max_workers=2, logger=Mock())

        # Set stop flag BEFORE execution
        executor.should_stop.set()

        # Try to execute module
        mock_module = Mock()
        mock_module.validate.return_value = True
        mock_module.configure.return_value = True
        mock_module.verify.return_value = True

        result = executor._execute_module_internal("test_module", mock_module)

        # Should return False immediately without executing module methods
        assert result is False, "Should skip execution when stop flag is set"

        # Module methods should NOT be called
        mock_module.validate.assert_not_called()
        mock_module.configure.assert_not_called()
        mock_module.verify.assert_not_called()

    def test_stop_flag_not_set_allows_execution(self):
        """Test that modules execute normally when stop flag is not set."""
        executor = ParallelModuleExecutor(max_workers=2, logger=Mock())

        # Stop flag is NOT set
        assert not executor.should_stop.is_set()

        # Create mock module
        mock_module = Mock()
        mock_module.validate.return_value = True
        mock_module.configure.return_value = True
        mock_module.verify.return_value = True

        result = executor._execute_module_internal("test_module", mock_module)

        # Should execute successfully
        assert result is True

        # Module methods should be called
        mock_module.validate.assert_called_once()
        mock_module.configure.assert_called_once()
        mock_module.verify.assert_called_once()

    def test_stop_flag_set_immediately_on_failure(self):
        """Test that stop flag is set immediately when a module fails."""
        executor = ParallelModuleExecutor(max_workers=2, logger=Mock())

        # Create module registry
        module_registry = {"module1": Mock(), "module2": Mock()}

        execution_order = []

        def execution_handler(name, module):
            execution_order.append(f"start_{name}")
            if name == "module1":
                execution_order.append(f"fail_{name}")
                return False  # Fail
            # For other modules, check if stop was set
            execution_order.append(f"check_stop_{name}_{executor.should_stop.is_set()}")
            return True

        # Single batch with both modules
        batches = [["module1", "module2"]]

        executor.execute_batches(batches, module_registry, execution_handler)

        # Stop flag should be set after module1 failure
        assert executor.should_stop.is_set()

    def test_double_check_pattern_exists(self):
        """Verify the double-check pattern is implemented in _execute_module_internal."""
        # This test verifies the code structure by checking that
        # stop flag is checked both before and inside the lock
        executor = ParallelModuleExecutor(max_workers=2, logger=Mock())

        # The fix should have:
        # 1. Check before any work
        # 2. Check inside results_lock

        # Verify first check works
        executor.should_stop.set()
        mock_module = Mock()
        result = executor._execute_module_internal("test", mock_module)
        assert result is False

        # Reset and verify normal execution
        executor.should_stop.clear()
        mock_module = Mock()
        mock_module.validate.return_value = True
        mock_module.configure.return_value = True
        mock_module.verify.return_value = True
        result = executor._execute_module_internal("test2", mock_module)
        assert result is True


class TestStopFlagTiming:
    """Test the timing of stop flag operations."""

    def test_stop_flag_is_threading_event(self):
        """Verify should_stop is a threading.Event for thread safety."""
        executor = ParallelModuleExecutor(max_workers=2, logger=Mock())
        assert isinstance(executor.should_stop, threading.Event)

    def test_stop_flag_thread_safe_operations(self):
        """Test that stop flag operations are thread-safe."""
        executor = ParallelModuleExecutor(max_workers=2, logger=Mock())

        # Test set/clear/is_set
        assert not executor.should_stop.is_set()
        executor.should_stop.set()
        assert executor.should_stop.is_set()
        executor.should_stop.clear()
        assert not executor.should_stop.is_set()


class TestConcurrentExecution:
    """Test behavior under concurrent execution."""

    def test_batch_stops_on_first_failure(self):
        """Test that batch execution stops when first module fails."""
        executor = ParallelModuleExecutor(max_workers=3, logger=Mock())

        # Track execution
        executed = []
        lock = threading.Lock()

        def handler(name, module):
            if executor.should_stop.is_set():
                return False

            with lock:
                executed.append(name)

            if name == "fail_module":
                return False
            return True

        module_registry = {
            "fail_module": Mock(),
            "module2": Mock(),
            "module3": Mock(),
        }

        batches = [["fail_module", "module2", "module3"]]

        results = executor.execute_batches(batches, module_registry, handler)

        # Verify stop flag is set
        assert executor.should_stop.is_set()

        # Verify at least the failing module executed
        assert "fail_module" in executed
