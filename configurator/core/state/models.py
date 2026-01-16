"""
State models for installation tracking.

Defines data structures for tracking module and installation state.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ModuleStatus(Enum):
    """Module execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ROLLED_BACK = "rolled_back"


@dataclass
class ModuleState:
    """
    State of a single module during installation.

    Tracks execution progress, timing, and rollback information.
    """

    name: str
    status: ModuleStatus = ModuleStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    progress_percent: int = 0
    current_step: str = ""
    error_message: Optional[str] = None
    checkpoint: Optional[str] = None
    rollback_actions: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize to dictionary.

        Returns:
            Dictionary representation of module state
        """
        return {
            "name": self.name,
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
            "progress_percent": self.progress_percent,
            "current_step": self.current_step,
            "error_message": self.error_message,
            "checkpoint": self.checkpoint,
            "rollback_actions": self.rollback_actions,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModuleState":
        """
        Deserialize from dictionary.

        Args:
            data: Dictionary representation

        Returns:
            ModuleState instance
        """
        return cls(
            name=data["name"],
            status=ModuleStatus(data["status"]),
            started_at=(
                datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None
            ),
            completed_at=(
                datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None
            ),
            duration_seconds=data.get("duration_seconds"),
            progress_percent=data.get("progress_percent", 0),
            current_step=data.get("current_step", ""),
            error_message=data.get("error_message"),
            checkpoint=data.get("checkpoint"),
            rollback_actions=data.get("rollback_actions", []),
        )

    def mark_started(self) -> None:
        """Mark module as started."""
        self.status = ModuleStatus.RUNNING
        self.started_at = datetime.now()

    def mark_completed(self) -> None:
        """Mark module as completed successfully."""
        self.status = ModuleStatus.COMPLETED
        self.completed_at = datetime.now()
        self.progress_percent = 100

        if self.started_at:
            delta = self.completed_at - self.started_at
            self.duration_seconds = delta.total_seconds()

    def mark_failed(self, error: str) -> None:
        """
        Mark module as failed.

        Args:
            error: Error message
        """
        self.status = ModuleStatus.FAILED
        self.completed_at = datetime.now()
        self.error_message = error

        if self.started_at:
            delta = self.completed_at - self.started_at
            self.duration_seconds = delta.total_seconds()


@dataclass
class InstallationState:
    """
    Overall installation state.

    Tracks multiple modules and overall installation progress.
    """

    installation_id: str
    started_at: datetime
    profile: str
    modules: Dict[str, ModuleState] = field(default_factory=dict)
    completed_at: Optional[datetime] = None
    overall_status: str = "in_progress"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize to dictionary.

        Returns:
            Dictionary representation of installation state
        """
        return {
            "installation_id": self.installation_id,
            "started_at": self.started_at.isoformat(),
            "profile": self.profile,
            "modules": {name: state.to_dict() for name, state in self.modules.items()},
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "overall_status": self.overall_status,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InstallationState":
        """
        Deserialize from dictionary.

        Args:
            data: Dictionary representation

        Returns:
            InstallationState instance
        """
        modules = {
            name: ModuleState.from_dict(module_data)
            for name, module_data in data.get("modules", {}).items()
        }

        return cls(
            installation_id=data["installation_id"],
            started_at=datetime.fromisoformat(data["started_at"]),
            profile=data["profile"],
            modules=modules,
            completed_at=(
                datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None
            ),
            overall_status=data.get("overall_status", "in_progress"),
            metadata=data.get("metadata", {}),
        )

    def get_progress_percent(self) -> int:
        """
        Calculate overall installation progress.

        Returns:
            Progress percentage (0-100)
        """
        if not self.modules:
            return 0

        total_progress = sum(m.progress_percent for m in self.modules.values())
        return int(total_progress / len(self.modules))

    def is_complete(self) -> bool:
        """
        Check if installation is complete.

        Returns:
            True if all modules completed or skipped
        """
        if not self.modules:
            return False

        return all(
            m.status in (ModuleStatus.COMPLETED, ModuleStatus.SKIPPED)
            for m in self.modules.values()
        )

    def has_failures(self) -> bool:
        """
        Check if any modules failed.

        Returns:
            True if any module has failed status
        """
        return any(m.status == ModuleStatus.FAILED for m in self.modules.values())
