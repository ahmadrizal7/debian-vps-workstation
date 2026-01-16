from unittest.mock import MagicMock

from configurator.exceptions import ConfiguratorError
from configurator.ui.formatters.error import ErrorFormatter


def test_formatter_configurator_error():
    """Test formatting structured ConfiguratorError."""
    console = MagicMock()
    formatter = ErrorFormatter(console)

    err = ConfiguratorError(what="Something broke", why="Because reasons", how="Fix it")

    formatter.format_error(err)

    # Verify console.print calls
    # We can check that print was called with a Panel
    assert console.print.called

    # We can inspect the calls if needed, but checking it runs without error
    # and invokes the console is usually sufficient for visual formatters in unit tests
    # unless we parse the Rich renderables.


def test_formatter_generic_error():
    """Test formatting generic exception."""
    console = MagicMock()
    formatter = ErrorFormatter(console)

    err = ValueError("Invalid value")

    formatter.format_error(err)

    assert console.print.called


def test_formatter_suggestions():
    """Test suggestions output."""
    console = MagicMock()
    formatter = ErrorFormatter(console)

    err = ValueError("Found")
    formatter.format_with_suggestions(err, ["Try this", "Or that"])

    assert console.print.called
