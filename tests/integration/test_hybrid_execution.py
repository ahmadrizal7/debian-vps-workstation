# tests/integration/test_hybrid_execution.py
from unittest.mock import MagicMock, Mock

import pytest

from configurator.core.execution.base import ExecutionContext
from configurator.core.execution.hybrid import HybridExecutor


@pytest.fixture
def mock_module():
    mod = Mock()
    mod.validate.return_value = True
    mod.configure.return_value = True
    mod.verify.return_value = True
    return mod


def test_hybrid_execution_end_to_end(mock_module):
    """Test full workflow with mixed modules."""
    executor = HybridExecutor(max_workers=3)

    # 1. Parallel compatible module
    mod_parallel = Mock()
    mod_parallel.validate.return_value = True
    mod_parallel.configure.return_value = True
    mod_parallel.verify.return_value = True
    mod_parallel.force_sequential = False

    # 2. Sequential forced module
    mod_sequential = Mock()
    mod_sequential.validate.return_value = True
    mod_sequential.configure.return_value = True
    mod_sequential.verify.return_value = True
    mod_sequential.force_sequential = True

    contexts = [
        ExecutionContext("parallel_1", mod_parallel, {}),
        ExecutionContext("sequential_1", mod_sequential, {}),
    ]

    results = executor.execute(contexts)

    assert len(results) == 2
    assert results["parallel_1"].success
    assert results["sequential_1"].success
    assert results["parallel_1"].module_name == "parallel_1"


def test_hybrid_routing_logic():
    """Verify modules are routed correctly internally."""
    executor = HybridExecutor()
    executor.parallel_executor = MagicMock()
    executor.pipeline_executor = MagicMock()

    mod_p = Mock(force_sequential=False, large_module=False)
    mod_s = Mock(force_sequential=True)

    contexts = [
        ExecutionContext("p", mod_p, {}),
        ExecutionContext("s", mod_s, {}),
    ]

    executor.execute(contexts)

    # Check parallel executor called with 'p'
    parallel_call_args = executor.parallel_executor.execute.call_args[0][0]
    assert len(parallel_call_args) == 1
    assert parallel_call_args[0].module_name == "p"

    # Check pipeline executor called with 's'
    pipeline_call_args = executor.pipeline_executor.execute.call_args[0][0]
    assert len(pipeline_call_args) == 1
    assert pipeline_call_args[0].module_name == "s"
