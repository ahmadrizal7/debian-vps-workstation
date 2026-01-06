# Permission Model

Permissions use the format `scope:resource:action` with wildcard support (`*`). Examples:

- `app:myapp:deploy` — deploy a specific app.
- `app:*:logs:read` — read logs for any app.
- `db:production:read` — read-only production database access.
- `system:*` — any system-level operation.

## Matching Rules

- Scope, resource, and action are matched independently and may contain `*`.
- A granted permission matches a required permission when all three segments match (with wildcard expansion).

## Common Scopes

- `system`, `app`, `db`, `network`, `user`, `file`, `service`

## Actions

- `read`, `write`, `create`, `delete`, `execute`, or `*` for all actions.

Use multiple permissions to capture complex access needs and role inheritance to compose reusable sets.
