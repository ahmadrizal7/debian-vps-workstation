"""Helper utilities for RBAC permission parsing and matching."""

from __future__ import annotations

import re
from typing import Iterable, List

WILDCARD = "*"


def normalize_permission_string(permission: str) -> str:
    """Normalize permission strings by stripping whitespace and collapsing separators."""
    return permission.replace(" ", "").strip()


def wildcard_match(pattern: str, value: str) -> bool:
    """Match a value against a wildcard pattern.

    Supports `*` to represent any characters. Uses anchored regex.
    """
    if pattern == WILDCARD:
        return True
    if pattern == value:
        return True

    regex_pattern = re.escape(pattern).replace(re.escape(WILDCARD), ".*")
    return bool(re.fullmatch(regex_pattern, value))


def flatten_permissions(permission_sets: Iterable[Iterable[str]]) -> List[str]:
    """Flatten a list of permission iterables into a single list."""
    flattened: List[str] = []
    for permissions in permission_sets:
        flattened.extend(permissions)
    return flattened
