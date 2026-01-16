"""
Unit tests for dependency decorators.
"""

from configurator.dependencies.decorators import conflicts_with, depends_on, module
from configurator.dependencies.registry import DependencyRegistry


class TestModuleDecorator:
    """Tests for @module decorator."""

    def setup_method(self):
        """Clear registry before each test."""
        DependencyRegistry.clear()

    def test_module_decorator_sets_attributes(self):
        """Test @module decorator sets class attributes."""

        @module(name="test", priority=42, depends_on=["foo"])
        class TestModule:
            pass

        assert TestModule._module_name == "test"
        assert TestModule.priority == 42
        assert TestModule.depends_on == ["foo"]

    def test_module_decorator_default_name(self):
        """Test @module decorator generates default name from class."""

        @module()
        class DockerModule:
            pass

        assert DockerModule._module_name == "docker"

    def test_module_decorator_registers_dependency(self):
        """Test @module decorator registers in DependencyRegistry."""

        @module(name="test", depends_on=["foo"])
        class TestModule:
            pass

        dep = DependencyRegistry.get("test")
        assert dep is not None
        assert dep.module_name == "test"
        assert dep.depends_on == ["foo"]

    def test_module_decorator_all_fields(self):
        """Test @module decorator with all fields."""

        @module(
            name="docker",
            priority=50,
            depends_on=["system"],
            optional_deps=["network"],
            conflicts_with=["podman"],
            force_sequential=True,
        )
        class DockerModule:
            pass

        assert DockerModule._module_name == "docker"
        assert DockerModule.priority == 50
        assert DockerModule.depends_on == ["system"]
        assert DockerModule.optional_deps == ["network"]
        assert DockerModule.conflicts_with == ["podman"]
        assert DockerModule.force_sequential is True

        dep = DependencyRegistry.get("docker")
        assert dep.priority == 50
        assert dep.force_sequential is True


class TestDependsOnDecorator:
    """Tests for @depends_on decorator."""

    def setup_method(self):
        """Clear registry before each test."""
        DependencyRegistry.clear()

    def test_depends_on_decorator(self):
        """Test @depends_on shorthand decorator."""

        @depends_on("system", "security")
        class TestModule:
            pass

        assert TestModule.depends_on == ["system", "security"]
        assert TestModule._module_name == "test"

    def test_depends_on_registers(self):
        """Test @depends_on registers in registry."""

        @depends_on("system")
        class DockerModule:
            pass

        dep = DependencyRegistry.get("docker")
        assert dep is not None
        assert dep.depends_on == ["system"]


class TestConflictsWithDecorator:
    """Tests for @conflicts_with decorator."""

    def setup_method(self):
        """Clear registry before each test."""
        DependencyRegistry.clear()

    def test_conflicts_with_decorator(self):
        """Test @conflicts_with shorthand decorator."""

        @conflicts_with("podman")
        class DockerModule:
            pass

        assert DockerModule.conflicts_with == ["podman"]
        assert DockerModule._module_name == "docker"

    def test_conflicts_with_multiple(self):
        """Test @conflicts_with with multiple conflicts."""

        @conflicts_with("podman", "containerd")
        class DockerModule:
            pass

        assert DockerModule.conflicts_with == ["podman", "containerd"]

    def test_conflicts_with_registers(self):
        """Test @conflicts_with registers in registry."""

        @conflicts_with("podman")
        class DockerModule:
            pass

        dep = DependencyRegistry.get("docker")
        assert dep is not None
        assert dep.conflicts_with == ["podman"]
