from datetime import datetime
from unittest.mock import Mock

import pytest

from configurator.core.execution.base import ExecutionContext, ExecutionResult, ExecutorInterface


def test_execution_context_creation():
    """Test ExecutionContext dataclass."""
    module = Mock()
    context = ExecutionContext(
        module_name="docker", module_instance=module, config={"enabled": True}
    )

    assert context.module_name == "docker"
    assert context.dry_run is False
    assert context.priority == 50


def test_execution_result_status_icon():
    """Test ExecutionResult status icon."""
    result = ExecutionResult(
        module_name="docker",
        success=True,
        started_at=datetime.now(),
        completed_at=datetime.now(),
        duration_seconds=10.5,
    )

    assert result.status_icon == "✅"

    result_fail = ExecutionResult(
        module_name="docker",
        success=False,
        started_at=datetime.now(),
        completed_at=datetime.now(),
        duration_seconds=10.5,
    )
    assert result_fail.status_icon == "❌"


def test_executor_interface_is_abstract():
    """Test ExecutorInterface cannot be instantiated."""
    with pytest.raises(TypeError):
        ExecutorInterface()
