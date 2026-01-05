"""
Installation modules for the configurator.
"""

from configurator.modules.base import ConfigurationModule
from configurator.modules.caddy import CaddyModule
from configurator.modules.cursor import CursorModule

# Additional modules
from configurator.modules.databases import DatabasesModule
from configurator.modules.desktop import DesktopModule
from configurator.modules.devops import DevOpsModule
from configurator.modules.docker import DockerModule
from configurator.modules.git import GitModule

# Phase 6 modules
from configurator.modules.golang import GolangModule
from configurator.modules.java import JavaModule
from configurator.modules.neovim import NeovimModule
from configurator.modules.netdata import NetdataModule
from configurator.modules.nodejs import NodeJSModule
from configurator.modules.php import PHPModule
from configurator.modules.python import PythonModule
from configurator.modules.rust import RustModule
from configurator.modules.security import SecurityModule
from configurator.modules.system import SystemModule
from configurator.modules.utilities import UtilitiesModule
from configurator.modules.vscode import VSCodeModule
from configurator.modules.wireguard import WireGuardModule

__all__ = [
    "ConfigurationModule",
    # Core modules
    "SystemModule",
    "SecurityModule",
    "DesktopModule",
    # Languages
    "PythonModule",
    "NodeJSModule",
    "GolangModule",
    "RustModule",
    "JavaModule",
    "PHPModule",
    # Tools
    "DockerModule",
    "GitModule",
    "DatabasesModule",
    "DevOpsModule",
    "UtilitiesModule",
    # Editors
    "VSCodeModule",
    "CursorModule",
    "NeovimModule",
    # Networking
    "WireGuardModule",
    "CaddyModule",
    # Monitoring
    "NetdataModule",
]
