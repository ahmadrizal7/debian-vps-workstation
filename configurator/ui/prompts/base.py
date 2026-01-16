from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional

from rich.console import Console


@dataclass
class PromptResult:
    """Result from a prompt."""

    value: Any
    cancelled: bool = False
    error: Optional[str] = None


class PromptBase(ABC):
    """Base class for all prompts."""

    def __init__(self, message: str, default: Any = None, console: Optional[Console] = None):
        self.message = message
        self.default = default
        self.console = console or Console()

    @abstractmethod
    def prompt(self) -> PromptResult:
        """Display prompt and get user input."""
        pass

    def validate(self, value: Any) -> bool:
        """Validate user input. Override in subclasses."""
        return True

    def format_error(self, error: str) -> str:
        """Format error message."""
        return f"[red]✗[/red] {error}"
