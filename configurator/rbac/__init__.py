"""Role-Based Access Control utilities for Debian VPS Configurator.

Exposes the main RBACManager along with supporting classes and enums.
"""

from .rbac_manager import (
    Permission,
    PermissionAction,
    PermissionScope,
    RBACManager,
    Role,
    RoleAssignment,
    SudoAccess,
)

__all__ = [
    "Permission",
    "PermissionAction",
    "PermissionScope",
    "RBACManager",
    "Role",
    "RoleAssignment",
    "SudoAccess",
]
