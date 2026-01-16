from unittest.mock import Mock

from configurator.core.execution.base import ExecutionContext
from configurator.core.execution.pipeline import PipelineExecutor


def test_pipeline_executor_can_handle_single():
    """Test PipelineExecutor handles single force_sequential module."""
    executor = PipelineExecutor()

    mod = Mock()
    mod.force_sequential = True

    contexts = [ExecutionContext("desktop", mod, {})]

    assert executor.can_handle(contexts) is True


def test_pipeline_executor_rejects_multiple():
    """Test PipelineExecutor rejects multiple modules."""
    executor = PipelineExecutor()

    contexts = [ExecutionContext("mod1", Mock(), {}), ExecutionContext("mod2", Mock(), {})]

    assert executor.can_handle(contexts) is False


def test_pipeline_executor_executes_stages():
    """Test PipelineExecutor executes all stages."""
    executor = PipelineExecutor()

    mod = Mock()
    mod.validate.return_value = True
    mod.configure.return_value = True
    mod.verify.return_value = True

    contexts = [ExecutionContext("test", mod, {})]

    callback = Mock()
    results = executor.execute(contexts, callback=callback)

    assert results["test"].success is True

    # Verify all stages called
    events = [call[0][1] for call in callback.call_args_list]
    assert "validating" in events
    assert "configuring" in events
    assert "verifying" in events


def test_pipeline_executor_with_hooks():
    """Test PipelineExecutor calls pre/post hooks if present."""
    executor = PipelineExecutor()

    mod = Mock()
    mod.validate.return_value = True
    mod.pre_configure.return_value = True
    mod.configure.return_value = True
    mod.post_configure.return_value = True
    mod.verify.return_value = True

    contexts = [ExecutionContext("test", mod, {})]

    callback = Mock()
    results = executor.execute(contexts, callback=callback)

    assert results["test"].success is True

    # Verify hooks called
    mod.pre_configure.assert_called_once()
    mod.post_configure.assert_called_once()
