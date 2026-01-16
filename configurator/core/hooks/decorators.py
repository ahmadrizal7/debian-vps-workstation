from functools import wraps
from typing import Callable, List, Union

from .events import HookEvent, HookPriority


def hook(events: Union[HookEvent, List[HookEvent]], priority: HookPriority = HookPriority.NORMAL):
    """
    Decorator to register a function as a hook.

    Args:
        events: Single event or list of events to trigger hook
        priority: Execution priority
    """

    def decorator(func: Callable):
        if not hasattr(func, "_hook_events"):
            func._hook_events = []

        _events = events if isinstance(events, list) else [events]
        for event in _events:
            if event not in func._hook_events:
                func._hook_events.append(event)

        func._hook_priority = priority

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Copy attributes to wrapper
        wrapper._hook_events = func._hook_events
        wrapper._hook_priority = func._hook_priority

        return wrapper

    return decorator
