import unittest

from configurator.ux.autocomplete import Autocomplete
from configurator.ux.filters import ModuleFilter


class TestImports(unittest.TestCase):
    def test_filter_import(self):
        f = ModuleFilter()
        self.assertIsNotNone(f)

    def test_autocomplete_import(self):
        # Already tested in test_search, but ensuring explicit coverage for the re-export file
        ac = Autocomplete([])
        self.assertIsNotNone(ac)
