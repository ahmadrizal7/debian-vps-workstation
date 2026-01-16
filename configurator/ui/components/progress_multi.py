from textual.app import ComposeResult
from textual.widgets import Label, ProgressBar, Static


class OverallProgress(Static):
    """Widget for overall installation progress."""

    DEFAULT_CSS = """
    OverallProgress {
        height: auto;
        border: solid yellow;
        margin: 1;
        padding: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label("Overall Progress", id="overall-label")
        yield ProgressBar(total=100, show_eta=True, id="overall-bar")

    def update_progress(self, percent: int) -> None:
        try:
            bar = self.query_one("#overall-bar", ProgressBar)
            bar.progress = percent
        except Exception:
            pass
