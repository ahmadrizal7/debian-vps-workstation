import unittest
from unittest.mock import MagicMock

from configurator.ui.prompts.multiselect import MultiSelectPrompt


class TestMultiSelectPrompt(unittest.TestCase):
    def setUp(self):
        self.console = MagicMock()
        self.choices = ["Apple", "Banana", "Cherry"]

    def test_multiselect_simple_indices(self):
        self.console.input.side_effect = ["1,3", ""]
        prompt = MultiSelectPrompt("Choose fruits", self.choices, console=self.console)
        result = prompt.prompt()
        self.assertEqual(sorted(result.value), ["Apple", "Cherry"])

    def test_multiselect_all(self):
        self.console.input.side_effect = ["all", ""]
        prompt = MultiSelectPrompt("Choose fruits", self.choices, console=self.console)
        result = prompt.prompt()
        self.assertEqual(len(result.value), 3)

    def test_multiselect_none(self):
        self.console.input.side_effect = ["none", ""]
        prompt = MultiSelectPrompt(
            "Choose fruits", self.choices, defaults=["Apple"], console=self.console
        )
        result = prompt.prompt()
        self.assertEqual(len(result.value), 0)

    def test_multiselect_empty_input_uses_defaults(self):
        self.console.input.return_value = ""
        prompt = MultiSelectPrompt(
            "Choose fruits", self.choices, defaults=["Banana"], console=self.console
        )
        result = prompt.prompt()
        self.assertEqual(result.value, ["Banana"])
