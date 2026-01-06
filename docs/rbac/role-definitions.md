# Default Role Definitions

The shipped `roles.yaml` includes four predefined roles. You can extend them with `vps-configurator rbac create-role`.

- **admin**: Full system administrator; all permissions; sudo `ALL`; groups `sudo`, `admin`.
- **devops**: Infrastructure and deployment; app deploy/restart/logs; production DB read; network and service management; limited sudo for systemctl/docker/apt; groups `devops`, `docker`.
- **developer**: Application development; deploy/restart/logs for apps; development/staging DB full; production DB read; docker build/run/logs; limited sudo for app restart/logs; groups `developers`, `docker`.
- **viewer**: Read-only visibility; system logs, app logs, DB read, service status; no sudo; group `viewers`.

Custom roles set `custom: true` and can inherit from existing roles using `inherits_from`.
