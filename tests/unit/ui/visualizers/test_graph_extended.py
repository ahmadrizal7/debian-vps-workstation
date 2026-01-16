import unittest
from unittest.mock import patch

from configurator.dependencies.registry import ModuleDependencyInfo
from configurator.ui.visualizers.dependency_graph import DependencyGraphVisualizer


class TestGraphAdditional(unittest.TestCase):
    def setUp(self):
        self.patcher = patch("configurator.dependencies.registry.DependencyRegistry.get")
        self.mock_get = self.patcher.start()
        # Default mock behavior
        self.mock_get.return_value = ModuleDependencyInfo("test_mod")

    def tearDown(self):
        self.patcher.stop()

    def test_render_flat(self):
        viz = DependencyGraphVisualizer(["mod1", "mod2"])

        def side_effect(name):
            if name == "mod1":
                return ModuleDependencyInfo("mod1", depends_on=["sys"])
            if name == "mod2":
                return ModuleDependencyInfo("mod2", conflicts_with=["bad"])
            return None

        self.mock_get.side_effect = side_effect

        output = viz.render_flat()
        self.assertIn("mod1", output)
        self.assertIn("requires: sys", output)
        self.assertIn("mod2", output)
        self.assertIn("conflicts with: bad", output)

    def test_estimate_time_display(self):
        # Force a large time to test formatting
        # We need to reach _estimate_time logic
        # Mock batches via patching get_execution_batches is hard without refactor,
        # but we can test helper directly if we access it,
        # or just construct a graph that yields specific results.

        # Accessing private method for coverage is acceptable in unit tests
        viz = DependencyGraphVisualizer([])
        # 10 batches of 10 items each = 10*3 + 100*2 = 30 + 200 = 230 mins > 60
        batches = [["a"] * 10] * 10
        time_str = viz._estimate_time(batches)
        self.assertIn("h", time_str)  # Should be hours
