from unittest.mock import Mock

from configurator.core.execution.base import ExecutionContext
from configurator.core.execution.parallel import ParallelExecutor


def test_parallel_executor_can_handle_multiple():
    """Test ParallelExecutor can handle multiple modules."""
    executor = ParallelExecutor(max_workers=2)

    mod1 = Mock()
    mod1.force_sequential = False
    mod2 = Mock()
    mod2.force_sequential = False

    contexts = [ExecutionContext("mod1", mod1, {}), ExecutionContext("mod2", mod2, {})]

    assert executor.can_handle(contexts) is True


def test_parallel_executor_rejects_single():
    """Test ParallelExecutor rejects single module."""
    executor = ParallelExecutor()
    contexts = [ExecutionContext("mod1", Mock(), {})]

    assert executor.can_handle(contexts) is False


def test_parallel_executor_rejects_sequential():
    """Test ParallelExecutor rejects force_sequential modules."""
    executor = ParallelExecutor()

    mod1 = Mock()
    mod1.force_sequential = True

    contexts = [ExecutionContext("mod1", mod1, {}), ExecutionContext("mod2", Mock(), {})]

    assert executor.can_handle(contexts) is False


def test_parallel_executor_executes_modules():
    """Test ParallelExecutor executes modules successfully."""
    executor = ParallelExecutor(max_workers=2)

    # Create mock modules
    mod1 = Mock()
    mod1.validate.return_value = True
    mod1.configure.return_value = True
    mod1.verify.return_value = True

    mod2 = Mock()
    mod2.validate.return_value = True
    mod2.configure.return_value = True
    mod2.verify.return_value = True

    contexts = [ExecutionContext("mod1", mod1, {}), ExecutionContext("mod2", mod2, {})]

    results = executor.execute(contexts)

    assert len(results) == 2
    assert results["mod1"].success is True
    assert results["mod2"].success is True

    # Verify methods called
    mod1.validate.assert_called_once()
    mod1.configure.assert_called_once()
    mod1.verify.assert_called_once()

    # Verify mod2 methods called
    mod2.validate.assert_called_once()
    mod2.configure.assert_called_once()
    mod2.verify.assert_called_once()


def test_parallel_executor_callback_called():
    """Test ParallelExecutor calls progress callback."""
    executor = ParallelExecutor()

    callback = Mock()

    mod = Mock()
    mod.validate.return_value = True
    mod.configure.return_value = True
    mod.verify.return_value = True

    contexts = [ExecutionContext("test", mod, {})]

    executor.execute(contexts, callback=callback)

    # Verify callback called with events
    calls = [call[0] for call in callback.call_args_list]
    events = [call[1] for call in calls]

    assert "started" in events
    assert "validating" in events
    assert "configuring" in events
    assert "verifying" in events
    assert "completed" in events


def test_parallel_executor_handles_failure():
    """Test ParallelExecutor handles module failure."""
    executor = ParallelExecutor()

    mod = Mock()
    mod.validate.return_value = False  # Fail validation

    contexts = [ExecutionContext("failing", mod, {})]

    results = executor.execute(contexts)

    assert results["failing"].success is False
    assert results["failing"].error is not None
