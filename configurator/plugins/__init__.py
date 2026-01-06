"""
Plugin system for extensible module loading.

Allows users to add custom modules without modifying the core codebase.
"""

from configurator.plugins.base import PluginBase, PluginInfo
from configurator.plugins.loader import PluginLoader, PluginManager

__all__ = [
    "PluginBase",
    "PluginInfo",
    "PluginLoader",
    "PluginManager",
]
