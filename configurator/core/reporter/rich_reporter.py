from datetime import datetime
from typing import Dict, Optional

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.table import Table

from configurator.core.reporter.base import ReporterInterface


class RichProgressReporter(ReporterInterface):
    """
    Enhanced progress reporter using Rich library.

    Features:
    - Multi-line progress bars
    - Spinner animations
    - Time elapsed/remaining
    - Status messages
    - Tips and facts
    """

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.start_time: Optional[datetime] = None
        self.current_phase: Optional[str] = None
        self.results: Dict[str, bool] = {}

        # Create Rich Progress instance
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            TextColumn("[dim]{task.fields[status]}[/dim]"),
            console=self.console,
        )

        self.overall_task: Optional[TaskID] = None
        self.module_task: Optional[TaskID] = None

    def start(self, title: str = "Installation"):
        """Display startup banner."""
        self.start_time = datetime.now()

        banner = f"""
╔{"═" * 58}╗
║   🚀 {title: ^50} ║
║   Transform your VPS into a coding powerhouse! {" " * 10}║
╚{"═" * 58}╝
        """.strip()

        self.console.print(Panel(banner, style="bold cyan"))
        self.console.print()
        self.progress.start()

    def start_phase(self, name: str, total_steps: int = 0):
        """Start new installation phase."""
        self.current_phase = name

        # Add task to progress if not exists or reuse??
        # Usually we want a fresh task for a phase or update the current one.
        # Let's say module_task represents the current running module/phase.

        if self.module_task is not None:
            # Stop/Hide previous task? Or just update it?
            # If we are reusing the line, update it.
            self.progress.update(
                self.module_task,
                description=f"[bold]{name}[/bold]",
                completed=0,
                total=total_steps or 100,
                status="Starting...",
            )
        else:
            self.module_task = self.progress.add_task(
                f"[bold]{name}[/bold]", total=total_steps or 100, status="Starting..."
            )

    def update(self, message: str, success: bool = True):
        """Update current progress with message."""
        if self.module_task:
            status_icon = "✅" if success else "❌"
            if not success:
                self.progress.update(self.module_task, status=f"{status_icon} {message}")
            else:
                self.progress.update(self.module_task, status=message)

    def update_progress(
        self, percent: int, current: Optional[int] = None, total: Optional[int] = None
    ):
        """Update progress percentage."""
        if self.module_task is not None:
            if current is not None and total is not None:
                self.progress.update(self.module_task, completed=current, total=total)
            else:
                # If using percent (0-100), map to total (assuming 100)
                # If total was set to something else, this might be tricky.
                # Assuming simple % update.
                self.progress.update(self.module_task, completed=percent, total=100)

    def complete_phase(self, success: bool = True):
        """Mark current phase as complete."""
        if self.module_task is not None:
            icon = "✅" if success else "❌"
            msg = "Done" if success else "Failed"
            self.progress.update(self.module_task, completed=100, status=f"{icon} {msg}")

    def show_summary(self, results: Dict[str, bool]):
        """Display installation summary."""
        # Stop progress display
        self.progress.stop()

        table = Table(title="Installation Summary")
        table.add_column("Module", style="cyan")
        table.add_column("Status", justify="center")

        for module, success in results.items():
            status = "[green]SUCCESS[/green]" if success else "[red]FAILED[/red]"
            table.add_row(module, status)

        self.console.print(table)

    def error(self, message: str):
        self.console.print(f"[bold red]ERROR:[/bold red] {message}")

    def warning(self, message: str):
        self.console.print(f"[bold yellow]WARNING:[/bold yellow] {message}")

    def info(self, message: str):
        self.console.print(f"[blue]INFO:[/blue] {message}")

    def show_next_steps(self, reboot_required: bool = False, rdp_port: int = 3389, **kwargs):
        """Display next steps after installation."""
        self.console.print("\n[bold cyan]Next Steps:[/bold cyan]")
        if reboot_required:
            self.console.print(
                "  • [bold yellow]Reboot your system[/bold yellow] to apply all changes."
            )
            self.console.print("    Run: [bold]sudo reboot[/bold]")

        self.console.print(
            "  • [green]Verify[/green] installation with: [bold]vps-configurator verify[/bold]"
        )
        self.console.print(
            "  • [green]Monitor[/green] system with: [bold]vps-configurator dashboard[/bold]"
        )
        self.console.print(f"  • Connect via RDP on port: [bold]{rdp_port}[/bold]")
