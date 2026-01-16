# tests/manual/test_parallel_executor_practical.py
import logging
import time
from unittest.mock import Mock

from configurator.core.execution.base import ExecutionContext
from configurator.core.execution.parallel import ParallelExecutor

# Configure logging
logging.basicConfig(level=logging.INFO)


def test_parallel_speedup():
    print("\n🚀 Testing Parallel Execution Speedup...")

    # Create parallel executor
    executor = ParallelExecutor(max_workers=3)

    # Create 5 mock modules
    modules = []
    print("   Creating 5 modules with 0.5s sleep each...")
    for i in range(5):
        mod = Mock()
        mod.validate.return_value = True
        mod.configure.side_effect = lambda: time.sleep(0.5) or True  # Simulate work
        mod.verify.return_value = True
        modules.append(mod)

    contexts = [ExecutionContext(f"module_{i}", modules[i], {}) for i in range(5)]

    # Execute
    print("   Executing...")
    start = time.time()
    results = executor.execute(contexts)
    duration = time.time() - start

    # Verify
    assert len(results) == 5, "Should execute all 5 modules"
    assert all(r.success for r in results.values()), "All should succeed"

    # Sequential would be 5 * 0.5 = 2.5s
    # Parallel (3 workers) should be around 1.0s (2 rounds)
    print(f"   Duration: {duration:.2f}s")

    if duration < 2.0:
        print(f"✅ Executed 5 modules in {duration:.2f}s (parallel speedup confirmed)")
    else:
        print(f"⚠️  Execution took {duration:.2f}s (slower than expected)")


if __name__ == "__main__":
    test_parallel_speedup()
