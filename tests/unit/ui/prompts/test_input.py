import unittest
from unittest.mock import MagicMock

from configurator.ui.prompts.input_text import InputPrompt
from configurator.ui.prompts.number import NumberPrompt
from configurator.ui.prompts.password import PasswordPrompt


class TestInputPrompts(unittest.TestCase):
    def setUp(self):
        self.console = MagicMock()

    def test_input_simple(self):
        self.console.input.return_value = "hello"
        prompt = InputPrompt("Enter text", console=self.console)
        result = prompt.prompt()
        self.assertEqual(result.value, "hello")

    def test_input_default(self):
        self.console.input.return_value = ""
        prompt = InputPrompt("Enter text", default="world", console=self.console)
        result = prompt.prompt()
        self.assertEqual(result.value, "world")

    def test_password_prompt(self):
        # We simulate the confirmation flow
        # PasswordPrompt calls input() twice if confirm=True
        self.console.input.side_effect = ["secret", "secret"]
        prompt = PasswordPrompt("Password", confirm=True, console=self.console)
        result = prompt.prompt()
        self.assertEqual(result.value, "secret")

    def test_number_prompt_valid(self):
        self.console.input.return_value = "42"
        prompt = NumberPrompt("Enter number", console=self.console)
        result = prompt.prompt()
        self.assertEqual(result.value, 42)

    def test_number_prompt_range(self):
        # First input invalid (too low), second valid
        self.console.input.side_effect = ["5", "15"]
        prompt = NumberPrompt("Enter number", min_value=10, console=self.console)
        result = prompt.prompt()
        self.assertEqual(result.value, 15)
