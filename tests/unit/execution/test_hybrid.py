from unittest.mock import Mock

from configurator.core.execution.base import ExecutionContext
from configurator.core.execution.hybrid import HybridExecutor


def test_hybrid_executor_routes_to_pipeline():
    """Test HybridExecutor routes force_sequential to pipeline."""
    executor = HybridExecutor(max_workers=2)

    mod = Mock()
    mod.force_sequential = True
    mod.validate.return_value = True
    mod.configure.return_value = True
    mod.verify.return_value = True

    contexts = [ExecutionContext("desktop", mod, {})]

    results = executor.execute(contexts)

    assert results["desktop"].success is True


def test_hybrid_executor_routes_to_parallel():
    """Test HybridExecutor routes independent modules to parallel."""
    executor = HybridExecutor(max_workers=2)

    mod1 = Mock()
    mod1.validate.return_value = True
    mod1.configure.return_value = True
    mod1.verify.return_value = True

    mod2 = Mock()
    mod2.validate.return_value = True
    mod2.configure.return_value = True
    mod2.verify.return_value = True

    contexts = [ExecutionContext("docker", mod1, {}), ExecutionContext("python", mod2, {})]

    results = executor.execute(contexts)

    assert results["docker"].success is True
    assert results["python"].success is True


def test_hybrid_executor_mixed_routing():
    """Test HybridExecutor handles mixed pipeline + parallel."""
    executor = HybridExecutor(max_workers=2)

    # Pipeline module
    desktop = Mock()
    desktop.force_sequential = True
    desktop.validate.return_value = True
    desktop.configure.return_value = True
    desktop.verify.return_value = True

    # Parallel modules
    docker = Mock()
    docker.validate.return_value = True
    docker.configure.return_value = True
    docker.verify.return_value = True

    python = Mock()
    python.validate.return_value = True
    python.configure.return_value = True
    python.verify.return_value = True

    contexts = [
        ExecutionContext("desktop", desktop, {}),
        ExecutionContext("docker", docker, {}),
        ExecutionContext("python", python, {}),
    ]

    results = executor.execute(contexts)

    assert len(results) == 3
    assert all(r.success for r in results.values())
