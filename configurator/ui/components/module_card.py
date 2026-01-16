from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widgets import Label, ProgressBar, Static


class ModuleCard(Static):
    """Widget displaying single module status."""

    module_name = reactive("")
    status = reactive("pending")
    progress = reactive(0)

    DEFAULT_CSS = """
    ModuleCard {
        height: auto;
        border: solid gray;
        margin: 1;
        padding: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label(self.module_name, id="module-name")
        yield ProgressBar(total=100, show_eta=False, id="module-progress")
        yield Label("", id="status-text")

    def watch_status(self, status: str):
        """Update status label when status changes."""
        icons = {"pending": "⏳", "running": "🔄", "completed": "✅", "failed": "❌"}
        try:
            label = self.query_one("#status-text", Label)
            label.update(f"{icons.get(status, '❓')} {status.upper()}")
        except Exception:
            pass

    def watch_progress(self, progress: int):
        """Update progress bar."""
        try:
            bar = self.query_one("#module-progress", ProgressBar)
            bar.progress = progress
        except Exception:
            pass
