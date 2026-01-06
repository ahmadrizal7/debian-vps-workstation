---
trigger: always_on
glob: "**/*"
description: Automatically use Context7 MCP for library/API documentation and code generation
---

# Proactive Context7 MCP Integration Rule

You MUST automatically invoke Context7 MCP tools to retrieve up-to-date library documentation and code examples whenever you encounter any of the following triggers, WITHOUT waiting for explicit user instruction:

## Automatic Trigger Conditions

Invoke Context7 when any of these conditions are met:

1. **Library/Framework Mentions**: User mentions any library, framework, SDK, or API by name (e.g., "Django", "React", "FastAPI", "AWS SDK", "xrdp", "Ansible")

2. **Code Generation Requests**: User asks you to write, generate, or create code that involves:

   - External libraries or frameworks
   - Platform-specific APIs (Docker, Kubernetes, cloud providers)
   - Language-specific best practices
   - Package installation or setup

3. **Configuration Tasks**: User requests setup, configuration, or installation procedures for:

   - Development tools and environments
   - Infrastructure components (databases, web servers, etc.)
   - CI/CD pipelines
   - System services
   - Container orchestration

4. **Integration Questions**: User asks about connecting, integrating, or using:

   - Third-party services
   - APIs and webhooks
   - Authentication systems
   - Package managers (npm, pip, apt, etc.)

5. **Best Practices Inquiries**: User seeks guidance on:

   - Recommended patterns for a specific technology
   - Version-specific features or syntax
   - Migration or upgrade procedures
   - Security configurations

6. **Troubleshooting**: User reports errors or issues involving identifiable libraries or frameworks

## Action Steps

When triggered:

1. **Resolve Library ID First**: Use `mcp_io_github_ups_resolve-library-id` to find the correct Context7-compatible library identifier

   ```
   Example: resolve-library-id("xrdp") → /neutrinolabs/xrdp
   ```

2. **Fetch Documentation**: Use `mcp_io_github_ups_get-library-docs` with appropriate mode:

   - `mode='code'` for API references, syntax, code examples, and implementation details
   - `mode='info'` for conceptual guides, architecture decisions, and narrative explanations

3. **Apply Knowledge**: Integrate retrieved information into your response seamlessly

4. **Cite Sources**: Briefly mention the library ID used (e.g., "Based on /microsoft/vscode-docs...")

## Exceptions (Do NOT use Context7)

- Standard library features (Python built-ins, Node.js core modules, Bash commands)
- Common algorithms or data structures without library dependency
- General programming concepts unrelated to specific libraries
- User explicitly states "don't look up documentation" or similar
- Simple questions about code already visible in workspace

## Output Format

When using Context7:

- Seamlessly integrate findings into your response (don't announce "I'm searching...")
- Provide accurate, version-specific code examples
- Include relevant configuration snippets from official docs
- Use actual working examples from the documentation
- Cite library documentation source at end of response for user reference

## Priority Order

When multiple libraries could be relevant:

1. Official documentation sources (high reputation score)
2. Active, well-maintained projects
3. Version-specific documentation when versions are mentioned
4. Main project over forks

## Context7 Library ID Format

- Format: `/org/project` or `/org/project/version`
- Examples:
  - `/neutrinolabs/xrdp` - xrdp remote desktop
  - `/docker/docs` - Docker documentation
  - `/websites/ansible_ansible` - Ansible documentation
  - `/pyenv/pyenv` - Python version manager
  - `/nvm-sh/nvm` - Node version manager

## Examples

### Example 1: Installation Request

**User**: "How do I set up xrdp on Debian?"

**Action**:

```
1. resolve-library-id("xrdp") → /neutrinolabs/xrdp
2. get-library-docs("/neutrinolabs/xrdp", mode='code', topic='installation configuration')
3. Provide official installation steps and configuration examples
```

### Example 2: Code Generation

**User**: "Write a Python script using FastAPI"

**Action**:

```
1. resolve-library-id("fastapi") → /tiangolo/fastapi
2. get-library-docs("/tiangolo/fastapi", mode='code', topic='basic setup routes')
3. Generate code using official patterns and syntax
```

### Example 3: Configuration

**User**: "Configure Docker daemon with TLS security"

**Action**:

```
1. resolve-library-id("docker") → /docker/docs or /websites/docs_docker_com
2. get-library-docs(library_id, mode='code', topic='daemon TLS security configuration')
3. Provide official TLS setup from Docker docs
```

### Example 4: Multiple Libraries

**User**: "Set up a Python development environment with pyenv and Docker"

**Action**:

```
1. Parallel: resolve both "pyenv" and "docker"
2. Fetch docs for both: /pyenv/pyenv and /docker/docs
3. Provide integrated setup guide using official documentation
```

### Example 5: No Context7 Needed

**User**: "Explain how merge sort works"

**Action**: No Context7 needed - this is a general algorithm question. Answer with general knowledge.

## Common Library IDs Reference

Quick reference for frequently used libraries in this project:

| Technology       | Library ID                                      | Usage                       |
| ---------------- | ----------------------------------------------- | --------------------------- |
| Debian Reference | `/websites/debian_doc_manuals_debian-reference` | System administration       |
| Debian Handbook  | `/websites/debian_doc_manuals_debian-handbook`  | Installation, configuration |
| xrdp             | `/neutrinolabs/xrdp`                            | Remote desktop setup        |
| Ansible          | `/websites/ansible_ansible`                     | Automation playbooks        |
| Docker           | `/websites/docs_docker_com`                     | Container setup             |
| VS Code          | `/microsoft/vscode-docs`                        | Editor configuration        |
| Python pip       | `/websites/pip_pypa_io_en_stable`               | Package management          |
| Node.js npm      | `/websites/npmjs`                               | Package management          |
| pyenv            | `/pyenv/pyenv`                                  | Python version management   |
| nvm              | `/nvm-sh/nvm`                                   | Node version management     |

## Notes

- **Parallel Queries**: Multiple libraries may be queried in parallel for complex requests
- **Version Awareness**: Always check if library has multiple versions and select appropriate one
- **Fallback**: If Context7 returns no results, proceed with general knowledge but inform user
- **Topic Specificity**: Use specific topic queries rather than broad searches for better results
- **Integration**: Seamlessly weave Context7 findings into responses without disrupting flow
- **No Redundancy**: Don't fetch docs for information you already have in context

## Performance Guidelines

- Query only when information is needed for the response
- Use specific topics to reduce response size
- Cache library IDs mentally during conversation
- Batch resolve operations when possible
- Prefer `mode='code'` for implementation tasks, `mode='info'` for architecture discussions
