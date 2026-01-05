"""
File operation utilities with backup support.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

from configurator.exceptions import ModuleExecutionError

# Default backup directory
BACKUP_DIR = Path("/var/backups/debian-vps-configurator")


def ensure_dir(path: Union[str, Path], mode: int = 0o755) -> Path:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path
        mode: Directory permissions

    Returns:
        Path object for the directory
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True, mode=mode)
    return path


def backup_file(
    path: Union[str, Path],
    backup_dir: Optional[Path] = None,
    suffix: Optional[str] = None,
) -> Optional[Path]:
    """
    Create a backup of a file.

    Args:
        path: File to backup
        backup_dir: Directory to store backup (default: /var/backups/debian-vps-configurator)
        suffix: Optional suffix for backup filename

    Returns:
        Path to backup file, or None if original doesn't exist
    """
    path = Path(path)

    if not path.exists():
        return None

    # Determine backup location
    backup_dir = backup_dir or BACKUP_DIR
    ensure_dir(backup_dir)

    # Generate backup filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = suffix or timestamp
    backup_name = f"{path.name}.{suffix}.bak"
    backup_path = backup_dir / backup_name

    # Create backup
    try:
        shutil.copy2(path, backup_path)
        return backup_path
    except Exception as e:
        raise ModuleExecutionError(
            what=f"Failed to backup file: {path}",
            why=str(e),
            how="Check file permissions and available disk space",
        )


def restore_file(
    backup_path: Union[str, Path],
    original_path: Union[str, Path],
) -> bool:
    """
    Restore a file from backup.

    Args:
        backup_path: Path to backup file
        original_path: Path to restore to

    Returns:
        True if restoration was successful
    """
    backup_path = Path(backup_path)
    original_path = Path(original_path)

    if not backup_path.exists():
        raise ModuleExecutionError(
            what=f"Backup file not found: {backup_path}",
            why="The backup file does not exist",
            how="Check if the backup was created successfully",
        )

    try:
        shutil.copy2(backup_path, original_path)
        return True
    except Exception as e:
        raise ModuleExecutionError(
            what=f"Failed to restore file: {original_path}",
            why=str(e),
            how="Check file permissions and available disk space",
        )


def write_file(
    path: Union[str, Path],
    content: str,
    backup: bool = True,
    mode: int = 0o644,
    owner: Optional[str] = None,
    group: Optional[str] = None,
) -> Path:
    """
    Write content to a file with optional backup.

    Args:
        path: File path
        content: Content to write
        backup: Create backup if file exists
        mode: File permissions
        owner: File owner (username)
        group: File group (groupname)

    Returns:
        Path to the written file
    """
    path = Path(path)

    # Create parent directories
    ensure_dir(path.parent)

    # Backup existing file
    if backup and path.exists():
        backup_file(path)

    # Write content
    try:
        path.write_text(content, encoding="utf-8")
        os.chmod(path, mode)

        # Set ownership if specified
        if owner or group:
            import grp
            import pwd

            uid = pwd.getpwnam(owner).pw_uid if owner else -1
            gid = grp.getgrnam(group).gr_gid if group else -1
            os.chown(path, uid, gid)

        return path
    except Exception as e:
        raise ModuleExecutionError(
            what=f"Failed to write file: {path}",
            why=str(e),
            how="Check file permissions and available disk space",
        )


def read_file(path: Union[str, Path]) -> str:
    """
    Read file content.

    Args:
        path: File path

    Returns:
        File content as string
    """
    path = Path(path)

    if not path.exists():
        raise ModuleExecutionError(
            what=f"File not found: {path}",
            why="The file does not exist",
            how="Check if the file path is correct",
        )

    try:
        return path.read_text(encoding="utf-8")
    except Exception as e:
        raise ModuleExecutionError(
            what=f"Failed to read file: {path}",
            why=str(e),
            how="Check file permissions",
        )


def append_to_file(
    path: Union[str, Path],
    content: str,
    create: bool = True,
) -> Path:
    """
    Append content to a file.

    Args:
        path: File path
        content: Content to append
        create: Create file if it doesn't exist

    Returns:
        Path to the file
    """
    path = Path(path)

    if not path.exists() and not create:
        raise ModuleExecutionError(
            what=f"File not found: {path}",
            why="The file does not exist and create=False",
            how="Set create=True or create the file first",
        )

    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(content)
        return path
    except Exception as e:
        raise ModuleExecutionError(
            what=f"Failed to append to file: {path}",
            why=str(e),
            how="Check file permissions",
        )


def file_contains(path: Union[str, Path], pattern: str) -> bool:
    """
    Check if a file contains a pattern.

    Args:
        path: File path
        pattern: String pattern to search for

    Returns:
        True if pattern is found
    """
    path = Path(path)

    if not path.exists():
        return False

    content = path.read_text(encoding="utf-8")
    return pattern in content


def replace_in_file(
    path: Union[str, Path],
    old: str,
    new: str,
    backup: bool = True,
) -> bool:
    """
    Replace text in a file.

    Args:
        path: File path
        old: Text to replace
        new: Replacement text
        backup: Create backup before modifying

    Returns:
        True if replacement was made
    """
    path = Path(path)

    if not path.exists():
        raise ModuleExecutionError(
            what=f"File not found: {path}",
            why="The file does not exist",
            how="Check if the file path is correct",
        )

    content = path.read_text(encoding="utf-8")

    if old not in content:
        return False

    new_content = content.replace(old, new)
    write_file(path, new_content, backup=backup)

    return True
