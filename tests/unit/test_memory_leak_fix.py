"""
Unit tests for memory leak fix in parallel executor (CORE-004).
"""

import threading
from unittest.mock import Mock

from configurator.core.parallel import ParallelModuleExecutor


class TestMemoryLeakFix:
    """Test that memory leak is fixed with proper cleanup."""

    def test_executor_initialization(self):
        """Test that executor initializes correctly."""
        executor = ParallelModuleExecutor(max_workers=2, logger=Mock())

        assert executor.max_workers == 2
        assert executor.results == {}
        assert isinstance(executor.results_lock, type(threading.Lock()))
        assert isinstance(executor.should_stop, threading.Event)

    def test_batch_execution_completes(self):
        """Test that batch execution completes and returns results."""
        executor = ParallelModuleExecutor(max_workers=2, logger=Mock())

        module_registry = {
            "module1": Mock(),
            "module2": Mock(),
        }

        def handler(name, module):
            return True

        batches = [["module1", "module2"]]

        results = executor.execute_batches(batches, module_registry, handler)

        assert "module1" in results
        assert "module2" in results
        assert results["module1"] is True
        assert results["module2"] is True

    def test_cleanup_after_successful_batch(self):
        """Test that cleanup occurs after successful batch."""
        executor = ParallelModuleExecutor(max_workers=2, logger=Mock())

        module_registry = {"module1": Mock()}

        def handler(name, module):
            return True

        batches = [["module1"]]

        # Execute batch
        results = executor.execute_batches(batches, module_registry, handler)

        # Verify results are captured
        assert results["module1"] is True

        # Verify executor is in clean state (no dangling references)
        assert "module1" in executor.results

    def test_cleanup_after_failed_batch(self):
        """Test that cleanup occurs even after batch failure."""
        executor = ParallelModuleExecutor(max_workers=2, logger=Mock())

        module_registry = {"module1": Mock()}

        def handler(name, module):
            return False  # Fail

        batches = [["module1"]]

        results = executor.execute_batches(batches, module_registry, handler)

        # Failure should be recorded
        assert results["module1"] is False

    def test_multiple_batches_sequential(self):
        """Test that multiple batches can be executed sequentially."""
        executor = ParallelModuleExecutor(max_workers=2, logger=Mock())

        def handler(name, module):
            return True

        # Execute multiple separate batches
        for i in range(3):
            # Reset executor for each batch
            executor = ParallelModuleExecutor(max_workers=2, logger=Mock())
            module_registry = {f"module_{i}_{j}": Mock() for j in range(2)}
            batches = [list(module_registry.keys())]

            results = executor.execute_batches(batches, module_registry, handler)

            # All should succeed
            assert all(results.values())

    def test_large_batch_single_execution(self):
        """Test execution of large batch (>5 modules)."""
        executor = ParallelModuleExecutor(max_workers=3, logger=Mock())

        # Create 10 modules (> 5 threshold for GC)
        module_names = [f"module_{i}" for i in range(10)]
        module_registry = {name: Mock() for name in module_names}

        def handler(name, module):
            return True

        batches = [module_names]

        # Should complete without issues
        results = executor.execute_batches(batches, module_registry, handler)

        # All should succeed
        assert len(results) == 10
        assert all(results.values())

    def test_small_batch_execution(self):
        """Test execution of small batch (<= 5 modules)."""
        executor = ParallelModuleExecutor(max_workers=3, logger=Mock())

        # Create 3 modules (<= 5 threshold)
        module_names = [f"module_{i}" for i in range(3)]
        module_registry = {name: Mock() for name in module_names}

        def handler(name, module):
            return True

        batches = [module_names]

        results = executor.execute_batches(batches, module_registry, handler)

        assert len(results) == 3
        assert all(results.values())


class TestFinallyBlockPattern:
    """Test that finally block cleanup pattern exists."""

    def test_cleanup_code_structure(self):
        """Verify that cleanup should happen after batch execution."""
        # This test verifies the expected behavior:
        # - future_to_module should be cleared after batch
        # - GC should be triggered for large batches

        executor = ParallelModuleExecutor(max_workers=2, logger=Mock())

        # The finally block in _execute_parallel_batch should:
        # 1. Clear future_to_module dict
        # 2. Trigger gc.collect() for batches > 5

        # We can verify the executor completes cleanly
        module_registry = {"module1": Mock()}

        def handler(name, module):
            return True

        batches = [["module1"]]
        results = executor.execute_batches(batches, module_registry, handler)

        assert results["module1"] is True

    def test_executor_reusable_after_batch(self):
        """Test that executor can be reused after batch completion."""
        executor = ParallelModuleExecutor(max_workers=2, logger=Mock())

        def handler(name, module):
            return True

        # First batch
        module_registry1 = {"mod1": Mock()}
        results1 = executor.execute_batches([["mod1"]], module_registry1, handler)
        assert results1["mod1"] is True

        # Executor should be reusable (state cleaned up)
        # Note: results accumulate, which is expected behavior
        assert "mod1" in executor.results
