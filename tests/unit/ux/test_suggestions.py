import unittest

from configurator.ux.suggestions import SuggestionEngine


class TestSuggestions(unittest.TestCase):
    def setUp(self):
        self.engine = SuggestionEngine()

    def test_suggest_modules_dev_tools(self):
        # Python should suggest vscode and git
        suggestions = self.engine.suggest_modules(["python"])
        self.assertIn("vscode", suggestions)
        self.assertIn("git", suggestions)

        # If vscode present, don't suggest it
        suggestions = self.engine.suggest_modules(["python", "vscode"])
        self.assertNotIn("vscode", suggestions)
        self.assertIn("git", suggestions)

    def test_suggest_modules_docker(self):
        suggestions = self.engine.suggest_modules(["docker"])
        self.assertIn("devops", suggestions)

    def test_suggest_modules_desktop(self):
        # Desktop suggests cursor if vscode not present
        suggestions = self.engine.suggest_modules(["desktop"])
        self.assertIn("cursor", suggestions)

        # If vscode present, cursor optional/not suggested by this logic
        suggestions = self.engine.suggest_modules(["desktop", "vscode"])
        self.assertNotIn("cursor", suggestions)

    def test_suggest_config(self):
        conf = self.engine.suggest_config("python")
        self.assertTrue(conf["install_poetry"])

        conf = self.engine.suggest_config("unknown")
        self.assertEqual(conf, {})

    def test_popular_combinations(self):
        combos = self.engine.get_popular_combinations()
        self.assertTrue(len(combos) > 0)
        self.assertIn(["python", "vscode", "git"], combos)
