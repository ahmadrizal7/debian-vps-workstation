# RBAC Overview

This module introduces a role-based access control (RBAC) layer for Debian VPS Configurator. It centralizes permission management, supports predefined and custom roles, and can optionally enforce system-level changes (groups and sudoers) when run with sufficient privileges.

## Key Concepts

- **Permissions**: `scope:resource:action` strings with wildcard support.
- **Roles**: Collections of permissions plus optional sudo rules and system groups.
- **Assignments**: Bind a role to a user with optional expiry and reason.

## File Layout

- Roles: `/etc/debian-vps-configurator/rbac/roles.yaml` (overridable).
- Assignments: `/etc/debian-vps-configurator/rbac/assignments.json` (overridable).
- Audit log: `/var/log/rbac-audit.log` (best effort).

## CLI

- `vps-configurator rbac list-roles`
- `vps-configurator rbac assign-role --user alice --role developer`
- `vps-configurator rbac check-permission --user alice --permission app:demo:deploy`
- `vps-configurator rbac create-role --name data-analyst --permission db:analytics:read`

System mutations (sudoers, group membership) are skipped automatically when `--dry-run` is used or when not running as root.
