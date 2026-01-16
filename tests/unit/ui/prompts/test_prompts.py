from unittest.mock import patch

from configurator.ui.prompts.confirm import ConfirmPrompt
from configurator.ui.prompts.select import SelectPrompt


def test_confirm_prompt_yes():
    """Test confirm prompt with 'y'."""
    with patch("builtins.input", return_value="y"):
        prompt = ConfirmPrompt("Continue?")
        result = prompt.prompt()
        assert result.value is True


def test_confirm_prompt_no():
    """Test confirm prompt with 'n'."""
    with patch("builtins.input", return_value="n"):
        prompt = ConfirmPrompt("Continue?")
        result = prompt.prompt()
        assert result.value is False


def test_confirm_prompt_default():
    """Test confirm prompt default."""
    with patch("builtins.input", return_value=""):
        prompt = ConfirmPrompt("Reset?", default=True)
        result = prompt.prompt()
        assert result.value is True


def test_select_prompt():
    """Test select prompt."""
    choices = ["A", "B", "C"]

    # Mock rich.prompt.Prompt.ask because SelectPrompt uses it
    with patch("rich.prompt.Prompt.ask", return_value="2"):
        prompt = SelectPrompt("Choose", choices)
        result = prompt.prompt()
        assert result.value == "B"
