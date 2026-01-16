"""Tests for hook decorators."""

from configurator.core.hooks.decorators import hook
from configurator.core.hooks.events import HookEvent, HookPriority


class TestHookDecorator:
    """Tests for @hook decorator."""

    def test_hook_decorator_single_event(self):
        """Test @hook decorator with single event."""

        @hook(HookEvent.BEFORE_INSTALLATION)
        def test_func(context):
            pass

        assert hasattr(test_func, "_hook_events")
        assert HookEvent.BEFORE_INSTALLATION in test_func._hook_events

    def test_hook_decorator_multiple_events(self):
        """Test @hook decorator with multiple events."""

        @hook([HookEvent.BEFORE_INSTALLATION, HookEvent.AFTER_INSTALLATION])
        def test_func(context):
            pass

        assert len(test_func._hook_events) == 2
        assert HookEvent.BEFORE_INSTALLATION in test_func._hook_events
        assert HookEvent.AFTER_INSTALLATION in test_func._hook_events

    def test_hook_decorator_with_priority(self):
        """Test @hook decorator with custom priority."""

        @hook(HookEvent.BEFORE_INSTALLATION, priority=HookPriority.HIGH)
        def test_func(context):
            pass

        assert test_func._hook_priority == HookPriority.HIGH

    def test_hook_decorator_default_priority(self):
        """Test @hook decorator uses default priority."""

        @hook(HookEvent.BEFORE_INSTALLATION)
        def test_func(context):
            pass

        assert test_func._hook_priority == HookPriority.NORMAL

    def test_hook_decorator_preserves_function(self):
        """Test @hook decorator preserves function."""

        @hook(HookEvent.BEFORE_INSTALLATION)
        def test_func(context):
            return "test"

        assert test_func({}) == "test"
        assert test_func.__name__ == "test_func"

    def test_multiple_decorators(self):
        """Test multiple @hook decorators on same function."""

        @hook(HookEvent.BEFORE_INSTALLATION)
        @hook(HookEvent.AFTER_INSTALLATION)
        def test_func(context):
            pass

        # Both events should be registered
        assert HookEvent.BEFORE_INSTALLATION in test_func._hook_events
        assert HookEvent.AFTER_INSTALLATION in test_func._hook_events
