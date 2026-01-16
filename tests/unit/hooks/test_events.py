"""Tests for hook events and context."""

from configurator.core.hooks.events import HookContext, HookEvent, HookPriority


class TestHookEvent:
    """Tests for HookEvent enum."""

    def test_hook_event_values(self):
        """Test HookEvent has expected values."""
        assert HookEvent.BEFORE_INSTALLATION.value == "before_installation"
        assert HookEvent.AFTER_INSTALLATION.value == "after_installation"
        assert HookEvent.BEFORE_MODULE_CONFIGURE.value == "before_module_configure"
        assert HookEvent.AFTER_MODULE_CONFIGURE.value == "after_module_configure"

    def test_all_hook_events_exist(self):
        """Test all expected hook events exist."""
        events = [e.value for e in HookEvent]

        # Installation lifecycle
        assert "before_installation" in events
        assert "after_installation" in events

        # Module lifecycle
        assert "before_module_validate" in events
        assert "after_module_validate" in events
        assert "before_module_configure" in events
        assert "after_module_configure" in events

        # Error handling
        assert "on_module_error" in events
        assert "on_installation_error" in events


class TestHookPriority:
    """Tests for HookPriority enum."""

    def test_hook_priority_values(self):
        """Test HookPriority has correct values."""
        assert HookPriority.FIRST.value == 0
        assert HookPriority.HIGH.value == 25
        assert HookPriority.NORMAL.value == 50
        assert HookPriority.LOW.value == 75
        assert HookPriority.LAST.value == 100

    def test_priority_ordering(self):
        """Test priorities are correctly ordered."""
        priorities = [p.value for p in HookPriority]
        assert priorities == sorted(priorities)


class TestHookContext:
    """Tests for HookContext dataclass."""

    def test_hook_context_creation(self):
        """Test HookContext can be created."""
        context = HookContext(event=HookEvent.BEFORE_INSTALLATION)

        assert context.event == HookEvent.BEFORE_INSTALLATION
        assert context.module_name is None
        assert context.data == {}
        assert context.metadata == {}

    def test_hook_context_with_module(self):
        """Test HookContext with module name."""
        context = HookContext(event=HookEvent.BEFORE_MODULE_CONFIGURE, module_name="docker")

        assert context.module_name == "docker"

    def test_hook_context_with_data(self):
        """Test HookContext with custom data."""
        context = HookContext(
            event=HookEvent.AFTER_MODULE_CONFIGURE,
            module_name="python",
            data={"duration": 120.5},
            metadata={"version": "3.12"},
        )

        assert context.data["duration"] == 120.5
        assert context.metadata["version"] == "3.12"

    def test_hook_context_timestamp(self):
        """Test HookContext has timestamp."""
        context = HookContext(event=HookEvent.BEFORE_INSTALLATION)

        assert context.timestamp is not None
