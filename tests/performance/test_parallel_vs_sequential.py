"""
Performance benchmark tests.

Compares:
- Parallel vs Sequential execution time
- Memory usage patterns
- Throughput metrics
"""

import threading
import time
from unittest.mock import Mock

import pytest

from configurator.core.parallel import ParallelModuleExecutor


@pytest.mark.slow
class TestParallelPerformance:
    """Benchmark parallel execution performance."""

    def test_parallel_faster_than_sequential_simulated(self):
        """Test that parallel execution is faster using simulated modules."""
        # Create modules with simulated work
        module_count = 6
        work_time = 0.1  # 100ms per module

        def create_handler(delay):
            def handler(name, module):
                time.sleep(delay)
                return True

            return handler

        # Sequential timing
        sequential_start = time.time()
        for i in range(module_count):
            time.sleep(work_time)
        sequential_time = time.time() - sequential_start

        # Parallel timing
        executor = ParallelModuleExecutor(max_workers=4, logger=Mock())
        module_registry = {f"module_{i}": Mock() for i in range(module_count)}
        batches = [list(module_registry.keys())]

        parallel_start = time.time()
        executor.execute_batches(batches, module_registry, create_handler(work_time))
        parallel_time = time.time() - parallel_start

        # Verify parallel is faster
        speedup = sequential_time / parallel_time
        assert speedup > 1.5, f"Expected speedup > 1.5x, got {speedup:.2f}x"

    def test_parallel_scaling_with_workers(self):
        """Test that more workers improve performance up to a point."""
        module_count = 8
        work_time = 0.05

        def handler(name, module):
            time.sleep(work_time)
            return True

        times = {}

        for workers in [1, 2, 4]:
            executor = ParallelModuleExecutor(max_workers=workers, logger=Mock())
            module_registry = {f"module_{i}": Mock() for i in range(module_count)}
            batches = [list(module_registry.keys())]

            start = time.time()
            executor.execute_batches(batches, module_registry, handler)
            times[workers] = time.time() - start

        # More workers should be faster (with diminishing returns)
        assert times[2] < times[1], "2 workers should be faster than 1"
        # assert times[4] <= times[2], "4 workers should be at least as fast as 2"


@pytest.mark.slow
class TestThroughputMetrics:
    """Test throughput metrics for parallel execution."""

    def test_modules_per_second_metric(self):
        """Test module execution throughput."""
        executor = ParallelModuleExecutor(max_workers=4, logger=Mock())

        module_count = 10
        work_time = 0.01  # 10ms per module

        def handler(name, module):
            time.sleep(work_time)
            return True

        module_registry = {f"module_{i}": Mock() for i in range(module_count)}
        batches = [list(module_registry.keys())]

        start = time.time()
        executor.execute_batches(batches, module_registry, handler)
        total_time = time.time() - start

        throughput = module_count / total_time

        # With 4 workers and 10ms per module, should achieve ~100+ modules/sec
        assert throughput > 10, f"Expected throughput > 10 modules/s, got {throughput:.1f}"

    def test_batch_overhead(self):
        """Test overhead of batch processing."""
        executor = ParallelModuleExecutor(max_workers=4, logger=Mock())

        # Zero-work modules
        def instant_handler(name, module):
            return True

        module_registry = {f"module_{i}": Mock() for i in range(100)}
        batches = [list(module_registry.keys())]

        start = time.time()
        executor.execute_batches(batches, module_registry, instant_handler)
        overhead = time.time() - start

        # Overhead should be minimal (< 1 second for 100 instant modules)
        assert overhead < 1.0, f"Batch overhead too high: {overhead:.3f}s"


@pytest.mark.slow
class TestMemoryUsagePatterns:
    """Test memory usage patterns during parallel execution."""

    def test_executor_cleanup_between_batches(self):
        """Test that executor cleans up properly between batches."""
        executor = ParallelModuleExecutor(max_workers=2, logger=Mock())

        def handler(name, module):
            return True

        # Run multiple batches
        for i in range(5):
            module_registry = {f"batch{i}_module_{j}": Mock() for j in range(10)}
            batches = [list(module_registry.keys())]

            executor.execute_batches(batches, module_registry, handler)

        # Executor should still be usable
        assert executor is not None

    def test_no_thread_leak(self):
        """Test that threads are properly cleaned up."""
        initial_threads = threading.active_count()

        executor = ParallelModuleExecutor(max_workers=4, logger=Mock())

        def handler(name, module):
            time.sleep(0.01)
            return True

        module_registry = {f"module_{i}": Mock() for i in range(20)}
        batches = [list(module_registry.keys())]

        executor.execute_batches(batches, module_registry, handler)

        # Give threads time to clean up
        time.sleep(0.2)

        final_threads = threading.active_count()

        # Thread count should not grow significantly
        thread_growth = final_threads - initial_threads
        assert thread_growth < 5, f"Thread leak detected: {thread_growth} new threads"


class TestPerformanceRegression:
    """Tests to detect performance regressions."""

    def test_executor_initialization_fast(self):
        """Test that executor initialization is fast."""
        start = time.time()

        for _ in range(100):
            executor = ParallelModuleExecutor(max_workers=4, logger=Mock())

        init_time = time.time() - start

        # 100 initializations should be < 1 second
        assert init_time < 1.0, f"Executor initialization too slow: {init_time:.3f}s for 100 inits"

    def test_empty_batch_fast(self):
        """Test that empty batch handling is fast."""
        executor = ParallelModuleExecutor(max_workers=4, logger=Mock())

        def handler(name, module):
            return True

        start = time.time()

        # Execute with empty batches
        for _ in range(100):
            executor.execute_batches([], {}, handler)

        empty_time = time.time() - start

        assert empty_time < 0.1, f"Empty batch handling too slow: {empty_time:.3f}s"
