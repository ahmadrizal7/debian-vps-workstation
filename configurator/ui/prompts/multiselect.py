from typing import List, Optional

from rich.console import Console
from rich.table import Table

from configurator.ui.prompts.base import PromptBase, PromptResult


class MultiSelectPrompt(PromptBase):
    """Prompt for selecting multiple options from a list."""

    def __init__(
        self,
        message: str,
        choices: List[str],
        defaults: Optional[List[str]] = None,
        console: Optional[Console] = None,
    ):
        super().__init__(message, None, console)
        self.choices = choices
        self.defaults = set(defaults) if defaults else set()

    def prompt(self) -> PromptResult:
        """
        Display the prompt and get user input.
        Returns a list of selected strings.
        """
        current_selection = self.defaults.copy()

        # We'll use a simple comma-separated input for now as a fallback if not full interactive
        # For a better experience, we might want to use a TUI widget, but keeping it simple for CLI first

        self.console.print(f"\n[bold]{self.message}[/bold] (comma-separated numbers, e.g. 1,3)")

        table = Table(show_header=False, box=None)
        table.add_column("Index", style="cyan", justify="right")
        table.add_column("Selection", justify="center")
        table.add_column("Option")

        for idx, choice in enumerate(self.choices, 1):
            selected = "✓" if choice in current_selection else " "
            style = "green" if choice in current_selection else ""
            table.add_row(str(idx), f"[{selected}]", choice, style=style)

        self.console.print(table)

        while True:
            try:
                response = self.console.input(
                    "\n[bold cyan]Select (enter to confirm): [/bold cyan]"
                )

                if not response.strip():
                    return PromptResult(value=list(current_selection))

                # Parse selection
                parts = [p.strip() for p in response.split(",")]

                # If valid numbers, toggle them. If "all", select all. If "none", clear.
                if "all" in parts:
                    current_selection = set(self.choices)
                elif "none" in parts:
                    current_selection = set()
                else:
                    # Toggle logic or overwrite logic?
                    # Standard CLI usually implies "enter what you want".
                    # But if we want it to be "toggle", we need a loop.
                    # To keep it simple conforming to standard CLI without TUI loop:
                    # We will treat the input as the *final* selection indices.

                    new_selection = set()
                    for part in parts:
                        if not part:
                            continue
                        try:
                            idx = int(part)
                            if 1 <= idx <= len(self.choices):
                                new_selection.add(self.choices[idx - 1])
                            else:
                                self.console.print(f"[red]Invalid index: {idx}[/red]")
                        except ValueError:
                            # Try string match
                            if part in self.choices:
                                new_selection.add(part)
                            else:
                                self.console.print(f"[red]Invalid option: {part}[/red]")

                    if new_selection:
                        current_selection = new_selection
                        return PromptResult(value=list(current_selection))

            except KeyboardInterrupt:
                return PromptResult(value=[], cancelled=True)
