from unittest.mock import MagicMock, Mock

from configurator.core.reporter.rich_reporter import RichProgressReporter


def test_rich_reporter_creation():
    reporter = RichProgressReporter()
    assert reporter is not None


def test_rich_reporter_start():
    console = MagicMock()
    console.__enter__.return_value = console
    console.__exit__.return_value = None

    reporter = RichProgressReporter(console=console)
    # Mock progress.start to avoid rich internal logic which is hard to mock perfectly
    reporter.progress.start = Mock()

    reporter.start("Test")
    assert console.print.called
    reporter.progress.start.assert_called_once()


def test_rich_reporter_update():
    console = Mock()
    reporter = RichProgressReporter(console=console)
    # Must add a task first
    reporter.start_phase("Test Phase")
    reporter.update("message", True)
    # Verification is tricky without mocking logic inside Rich,
    # but we ensure no exceptions.


def test_rich_reporter_summary():
    console = Mock()
    reporter = RichProgressReporter(console=console)
    reporter.show_summary({"mod1": True, "mod2": False})
    # Should print a table
    assert console.print.called
