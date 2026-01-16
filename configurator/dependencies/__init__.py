"""
Declarative dependency management for modules.

Provides decorators and models for defining module dependencies, conflicts,
and execution order declaratively.

Exports:
    ModuleDependency: Dependency configuration dataclass
    ConflictRule: Conflict rule dataclass
    DependencyRegistry: Global registry for dependencies
    module: Decorator for defining module metadata
    depends_on: Shorthand decorator for dependencies
    conflicts_with: Shorthand decorator for conflicts
"""

from configurator.dependencies.decorators import conflicts_with, depends_on, module
from configurator.dependencies.models import ConflictRule, ModuleDependency
from configurator.dependencies.registry import DependencyRegistry

__all__ = [
    "ModuleDependency",
    "ConflictRule",
    "DependencyRegistry",
    "module",
    "depends_on",
    "conflicts_with",
]
