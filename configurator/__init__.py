"""
Debian VPS Workstation Configurator

Transform Debian 13 VPS into a fully-featured remote desktop coding workstation.
"""

__version__ = "2.0.0"
__author__ = "VPS Configurator Team"
__license__ = "MIT"

from configurator.config import ConfigManager
from configurator.logger import setup_logger

__all__ = [
    "__version__",
    "ConfigManager",
    "setup_logger",
]
