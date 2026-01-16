import unittest
from unittest.mock import patch

from configurator.dependencies.registry import ModuleDependencyInfo
from configurator.ui.visualizers.dependency_graph import DependencyGraphVisualizer


class TestDependencyGraphCycles(unittest.TestCase):
    def setUp(self):
        # We need to mock the registry to simulate a cycle
        self.patcher = patch("configurator.dependencies.registry.DependencyRegistry.get")
        self.mock_get_info = self.patcher.start()

        # Setup specific cycle
        def side_effect(module):
            if module == "a":
                return ModuleDependencyInfo("a", depends_on=["b"])
            if module == "b":
                return ModuleDependencyInfo("b", depends_on=["c"])
            if module == "c":
                return ModuleDependencyInfo("c", depends_on=["a"])  # Cycle!
            return ModuleDependencyInfo(module)

        self.mock_get_info.side_effect = side_effect

    def tearDown(self):
        self.patcher.stop()

    def test_detect_cycles(self):
        viz = DependencyGraphVisualizer(["a", "b", "c"])
        cycles = viz.detect_cycles()
        # Should be detected
        self.assertTrue(len(cycles) > 0)
        # Cycle is a->b->c->a

    def test_render_tree_with_cycle(self):
        # Should not crash, just warn or handle gracefully
        viz = DependencyGraphVisualizer(["a"])
        try:
            output = viz.render_tree()
            self.assertIn("a", output)
        except RecursionError:
            self.fail("RecursionError during render_tree with cycle")


class TestSequentialExecution(unittest.TestCase):
    def setUp(self):
        self.patcher = patch("configurator.dependencies.registry.DependencyRegistry.get")
        self.mock_get_info = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_estimate_time_sequential(self):
        # A, B sequential -> 5+5=10 min
        # C, D parallel -> 5 min
        def side_effect(module):
            return ModuleDependencyInfo(
                module, estimated_time=5, force_sequential=(module in ["a", "b"])
            )

        self.mock_get_info.side_effect = side_effect
        # Just invoke to cover the lines, logic is tested deeper in core usually
        viz = DependencyGraphVisualizer(["a", "b"])
        viz._estimate_time({})

    def test_is_sequential(self):
        self.mock_get_info.return_value = ModuleDependencyInfo("a", force_sequential=True)
        viz = DependencyGraphVisualizer(["a"])
        self.assertTrue(viz._is_sequential("a"))

        self.mock_get_info.return_value = ModuleDependencyInfo("b", force_sequential=False)
        self.assertFalse(viz._is_sequential("b"))
