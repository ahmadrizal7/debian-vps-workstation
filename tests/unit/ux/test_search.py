import unittest

from configurator.ux.search import Autocomplete, ModuleSearch


class TestSearch(unittest.TestCase):
    def test_search_list(self):
        ms = ModuleSearch()
        modules = ["python-dev", "python-pip", "docker", "system"]
        results = ms.search_in_list("py", modules)
        self.assertIn("python-dev", results)
        self.assertIn("python-pip", results)
        self.assertNotIn("docker", results)

    def test_search_fuzzy(self):
        ms = ModuleSearch()
        modules = ["kubernetes", "docker"]
        # 'kubernets' typo
        results = ms.search_in_list("kubernets", modules)
        self.assertIn("kubernetes", results)


class TestAutocomplete(unittest.TestCase):
    def test_complete(self):
        ac = Autocomplete(["apple", "apricot", "banana"])
        res = ac.complete("app")
        self.assertEqual(res, ["apple"])
        res = ac.complete("ba")
        self.assertEqual(res, ["banana"])
