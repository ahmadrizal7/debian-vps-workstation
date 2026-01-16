"""
Unit tests for DependencyRegistry.
"""

import pytest

from configurator.dependencies.models import ModuleDependency
from configurator.dependencies.registry import DependencyRegistry


class TestDependencyRegistry:
    """Tests for DependencyRegistry."""

    def setup_method(self):
        """Clear registry before each test."""
        DependencyRegistry.clear()

    def test_register(self):
        """Test registering a dependency."""
        dep = ModuleDependency(module_name="test", depends_on=["foo"])

        DependencyRegistry.register(dep)

        assert DependencyRegistry.get("test") == dep

    def test_get_nonexistent(self):
        """Test getting non-existent dependency returns None."""
        result = DependencyRegistry.get("nonexistent")
        assert result is None

    def test_get_all(self):
        """Test getting all dependencies."""
        dep1 = ModuleDependency(module_name="test1")
        dep2 = ModuleDependency(module_name="test2")

        DependencyRegistry.register(dep1)
        DependencyRegistry.register(dep2)

        all_deps = DependencyRegistry.get_all()

        assert len(all_deps) == 2
        assert dep1 in all_deps
        assert dep2 in all_deps

    def test_detect_conflicts(self):
        """Test detecting conflicts."""
        dep1 = ModuleDependency(module_name="docker", conflicts_with=["podman"])
        dep2 = ModuleDependency(module_name="podman")

        DependencyRegistry.register(dep1)
        DependencyRegistry.register(dep2)

        conflicts = DependencyRegistry.detect_conflicts(["docker", "podman"])

        assert len(conflicts) == 1
        assert conflicts[0].module_a == "docker"
        assert conflicts[0].module_b == "podman"

    def test_detect_conflicts_no_conflict(self):
        """Test no conflicts detected when modules don't conflict."""
        dep1 = ModuleDependency(module_name="docker")
        dep2 = ModuleDependency(module_name="python")

        DependencyRegistry.register(dep1)
        DependencyRegistry.register(dep2)

        conflicts = DependencyRegistry.detect_conflicts(["docker", "python"])

        assert len(conflicts) == 0

    def test_resolve_order_simple(self):
        """Test simple dependency resolution."""
        dep1 = ModuleDependency(module_name="system", priority=10)
        dep2 = ModuleDependency(module_name="docker", depends_on=["system"], priority=50)

        DependencyRegistry.register(dep1)
        DependencyRegistry.register(dep2)

        order = DependencyRegistry.resolve_order(["system", "docker"])

        # system must come before docker
        assert order.index("system") < order.index("docker")

    def test_resolve_order_priority(self):
        """Test dependency resolution respects priority."""
        # Both have no dependencies, lower priority number should come first
        dep1 = ModuleDependency(module_name="first", priority=20)
        dep2 = ModuleDependency(module_name="second", priority=80)

        DependencyRegistry.register(dep1)
        DependencyRegistry.register(dep2)

        order = DependencyRegistry.resolve_order(["first", "second"])

        assert order.index("first") < order.index("second")

    def test_resolve_order_complex(self):
        """Test complex dependency chain."""
        deps = [
            ModuleDependency(module_name="system", priority=10),
            ModuleDependency(module_name="security", depends_on=["system"], priority=20),
            ModuleDependency(module_name="docker", depends_on=["system", "security"], priority=50),
        ]

        for dep in deps:
            DependencyRegistry.register(dep)

        order = DependencyRegistry.resolve_order(["system", "security", "docker"])

        # Verify dependencies are respected
        assert order.index("system") < order.index("security")
        assert order.index("system") < order.index("docker")
        assert order.index("security") < order.index("docker")

    def test_resolve_order_circular_dependency(self):
        """Test circular dependency raises error."""
        dep1 = ModuleDependency(module_name="a", depends_on=["b"])
        dep2 = ModuleDependency(module_name="b", depends_on=["a"])

        DependencyRegistry.register(dep1)
        DependencyRegistry.register(dep2)

        with pytest.raises(ValueError, match="Circular dependency"):
            DependencyRegistry.resolve_order(["a", "b"])

    def test_validate_dependencies_success(self):
        """Test validation passes when all dependencies satisfied."""
        dep1 = ModuleDependency(module_name="system")
        dep2 = ModuleDependency(module_name="docker", depends_on=["system"])

        DependencyRegistry.register(dep1)
        DependencyRegistry.register(dep2)

        errors = DependencyRegistry.validate_dependencies(["system", "docker"])

        assert len(errors) == 0

    def test_validate_dependencies_missing(self):
        """Test validation fails when dependencies missing."""
        dep = ModuleDependency(module_name="docker", depends_on=["system"])

        DependencyRegistry.register(dep)

        errors = DependencyRegistry.validate_dependencies(["docker"])

        assert len(errors) == 1
        assert "docker" in errors[0]
        assert "system" in errors[0]

    def test_clear(self):
        """Test clearing registry."""
        dep = ModuleDependency(module_name="test")
        DependencyRegistry.register(dep)

        assert len(DependencyRegistry.get_all()) == 1

        DependencyRegistry.clear()

        assert len(DependencyRegistry.get_all()) == 0
