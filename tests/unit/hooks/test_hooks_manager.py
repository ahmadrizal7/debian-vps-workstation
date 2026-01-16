"""Tests for HooksManager."""

from unittest.mock import Mock

from configurator.core.hooks.decorators import hook
from configurator.core.hooks.events import HookContext, HookEvent, HookPriority
from configurator.core.hooks.manager import HooksManager


class TestHooksManager:
    """Tests for HooksManager."""

    def test_hooks_manager_creation(self):
        """Test HooksManager can be created."""
        manager = HooksManager()
        assert manager is not None
        assert len(manager.hooks) == len(HookEvent)

    def test_register_hook(self):
        """Test registering a hook."""
        manager = HooksManager()

        def test_hook(context):
            pass

        manager.register(HookEvent.BEFORE_INSTALLATION, test_hook)

        hooks = manager.hooks[HookEvent.BEFORE_INSTALLATION]
        assert len(hooks) == 1
        assert hooks[0][1] == test_hook

    def test_register_hook_with_priority(self):
        """Test registering hook with custom priority."""
        manager = HooksManager()

        def test_hook(context):
            pass

        manager.register(HookEvent.BEFORE_INSTALLATION, test_hook, priority=HookPriority.HIGH)

        hooks = manager.hooks[HookEvent.BEFORE_INSTALLATION]
        assert hooks[0][0] == HookPriority.HIGH.value

    def test_hooks_sorted_by_priority(self):
        """Test hooks are sorted by priority."""
        manager = HooksManager()

        def hook1(context):
            pass

        def hook2(context):
            pass

        def hook3(context):
            pass

        # Register in reverse priority order
        manager.register(HookEvent.BEFORE_INSTALLATION, hook1, HookPriority.LOW)
        manager.register(HookEvent.BEFORE_INSTALLATION, hook2, HookPriority.HIGH)
        manager.register(HookEvent.BEFORE_INSTALLATION, hook3, HookPriority.NORMAL)

        hooks = manager.hooks[HookEvent.BEFORE_INSTALLATION]

        # Should be sorted: HIGH (25), NORMAL (50), LOW (75)
        assert hooks[0][1] == hook2  # HIGH
        assert hooks[1][1] == hook3  # NORMAL
        assert hooks[2][1] == hook1  # LOW

    def test_register_from_decorator(self):
        """Test registering hook decorated with @hook."""
        manager = HooksManager()

        @hook(HookEvent.BEFORE_INSTALLATION, priority=HookPriority.HIGH)
        def test_hook(context):
            pass

        manager.register_from_decorator(test_hook)

        hooks = manager.hooks[HookEvent.BEFORE_INSTALLATION]
        assert len(hooks) == 1
        assert hooks[0][1] == test_hook
        assert hooks[0][0] == HookPriority.HIGH.value

    def test_execute_hooks(self):
        """Test executing hooks for an event."""
        manager = HooksManager()

        mock_func = Mock()
        manager.register(HookEvent.BEFORE_INSTALLATION, mock_func)

        context = HookContext(event=HookEvent.BEFORE_INSTALLATION)
        manager.execute(HookEvent.BEFORE_INSTALLATION, context)

        mock_func.assert_called_once_with(context)

    def test_execute_multiple_hooks(self):
        """Test executing multiple hooks in priority order."""
        manager = HooksManager()

        call_order = []

        def hook1(context):
            call_order.append("low")

        def hook2(context):
            call_order.append("high")

        manager.register(HookEvent.BEFORE_INSTALLATION, hook1, HookPriority.LOW)
        manager.register(HookEvent.BEFORE_INSTALLATION, hook2, HookPriority.HIGH)

        manager.execute(HookEvent.BEFORE_INSTALLATION)

        # High priority should execute first
        assert call_order == ["high", "low"]

    def test_execute_hooks_with_kwargs(self):
        """Test execute creates context from kwargs."""
        manager = HooksManager()

        captured_context = None

        def test_hook(context):
            nonlocal captured_context
            captured_context = context

        manager.register(HookEvent.BEFORE_MODULE_CONFIGURE, test_hook)

        manager.execute(HookEvent.BEFORE_MODULE_CONFIGURE, module_name="docker", duration=120)

        assert captured_context is not None
        assert captured_context.data["module_name"] == "docker"
        assert captured_context.data["duration"] == 120

    def test_hook_failure_doesnt_crash(self):
        """Test hook failure doesn't stop other hooks."""
        manager = HooksManager()

        def failing_hook(context):
            raise RuntimeError("Test error")

        successful_mock = Mock()

        manager.register(HookEvent.BEFORE_INSTALLATION, failing_hook, HookPriority.HIGH)
        manager.register(HookEvent.BEFORE_INSTALLATION, successful_mock, HookPriority.LOW)

        # Should not raise exception
        manager.execute(HookEvent.BEFORE_INSTALLATION)

        # Successful hook should still execute
        successful_mock.assert_called_once()

    def test_execute_no_hooks(self):
        """Test executing event with no hooks registered."""
        manager = HooksManager()

        # Should not raise exception
        manager.execute(HookEvent.BEFORE_INSTALLATION)
