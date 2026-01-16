"""
Debian VPS Workstation Configurator

Transform Debian 13 VPS into a fully-featured remote desktop coding workstation.
"""

from configurator.config import ConfigManager
from configurator.logger import setup_logger

from .__version__ import __author__, __license__, __version__

__all__ = [
    "__version__",
    "__author__",
    "__license__",
    "ConfigManager",
    "setup_logger",
]
