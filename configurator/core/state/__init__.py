"""
Installation state management with persistence.

Provides models and managers for tracking installation state across restarts,
enabling resume capability and rollback management.

Exports:
    ModuleStatus: Enum for module execution states
    ModuleState: State of a single module
    InstallationState: Overall installation state
    StateManager: SQLite-backed state persistence
"""

from configurator.core.state.manager import StateManager
from configurator.core.state.models import (
    InstallationState,
    ModuleState,
    ModuleStatus,
)

__all__ = [
    "ModuleStatus",
    "ModuleState",
    "InstallationState",
    "StateManager",
]
