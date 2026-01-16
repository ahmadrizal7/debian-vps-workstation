import psutil
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Label, ProgressBar, Static


class ResourceGauge(Static):
    """Widget displaying system resources."""

    DEFAULT_CSS = """
    ResourceGauge {
        height: auto;
        border: solid blue;
        margin: 1;
        padding: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("CPU Usage")
            yield ProgressBar(total=100, show_eta=False, id="cpu-bar")
            yield Label("RAM Usage")
            yield ProgressBar(total=100, show_eta=False, id="ram-bar")

    def on_mount(self) -> None:
        self.set_interval(2.0, self.update_resources)

    def update_resources(self) -> None:
        try:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent

            self.query_one("#cpu-bar", ProgressBar).progress = cpu
            self.query_one("#ram-bar", ProgressBar).progress = ram
        except Exception:
            pass
