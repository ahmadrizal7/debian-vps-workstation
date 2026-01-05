"""
Utility functions for the configurator.
"""

from configurator.utils.command import CommandResult, run_command, run_command_with_output
from configurator.utils.file import backup_file, ensure_dir, restore_file, write_file
from configurator.utils.network import check_internet, download_file, get_public_ip
from configurator.utils.system import (
    get_architecture,
    get_disk_free_gb,
    get_os_info,
    get_ram_gb,
    is_root,
    is_systemd,
)

__all__ = [
    # Command utilities
    "run_command",
    "run_command_with_output",
    "CommandResult",
    # File utilities
    "backup_file",
    "restore_file",
    "write_file",
    "ensure_dir",
    # Network utilities
    "check_internet",
    "download_file",
    "get_public_ip",
    # System utilities
    "get_os_info",
    "get_architecture",
    "get_ram_gb",
    "get_disk_free_gb",
    "is_root",
    "is_systemd",
]
