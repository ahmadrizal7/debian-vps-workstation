import copy
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class HistoryState:
    """Represents a snapshot of the configuration."""

    profile_data: dict
    timestamp: float


class ConfigHistory:
    """
    Manages undo/redo history for configuration changes.
    """

    def __init__(self, max_size: int = 50):
        self.max_size = max_size
        self._undo_stack: List[dict] = []
        self._redo_stack: List[dict] = []

    def save_state(self, state: dict):
        """Save a new state to history."""
        # Deep copy to avoid reference issues
        self._undo_stack.append(copy.deepcopy(state))

        # Clear redo stack when new action is taken
        self._redo_stack.clear()

        # Enforce max size
        if len(self._undo_stack) > self.max_size:
            self._undo_stack.pop(0)

    def undo(self, current_state: dict) -> Optional[dict]:
        """
        Revert to previous state.
        Returns the previous state, or None if undo is not possible.
        """
        if not self.can_undo():
            return None

        # Save current state to redo stack
        self._redo_stack.append(copy.deepcopy(current_state))

        return self._undo_stack.pop()

    def redo(self, current_state: dict) -> Optional[dict]:
        """
        Redo a previously undone action.
        Returns the next state, or None if redo is not possible.
        """
        if not self.can_redo():
            return None

        # Save current state to undo stack
        self._undo_stack.append(copy.deepcopy(current_state))

        return self._redo_stack.pop()

    def can_undo(self) -> bool:
        return len(self._undo_stack) > 0

    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0

    def clear(self):
        self._undo_stack.clear()
        self._redo_stack.clear()
