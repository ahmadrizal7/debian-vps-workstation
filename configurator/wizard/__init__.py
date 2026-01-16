from typing import TYPE_CHECKING, Any, Dict, Optional

from configurator.wizard.config_wizard import run_wizard

if TYPE_CHECKING:
    from logging import Logger

    from rich.console import Console


class InteractiveWizard:
    """
    Adapter for the TUI Wizard to be used by the CLI.
    """

    def __init__(self, console: Optional["Console"] = None, logger: Optional["Logger"] = None):
        self.console = console
        self.logger = logger

    def run(self) -> Optional[Dict[str, Any]]:
        """
        Run the interactive wizard.

        Returns:
            Dict with configuration overrides and profile selection,
            or None if cancelled.
        """
        # Run the TUI app
        return run_wizard()
