"""
Generate CLI and API documentation.
"""

import importlib
import inspect
import os
import sys
from pathlib import Path

import click

# Add project root to path so we can import configurator
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from configurator.cli import main as cli


def generate_api_docs(output_dir: Path):
    """Generate API reference documentation."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Core Components to document
    components = [
        ("configurator.core.installer", "Installer"),
        # ("configurator.core.execution.hybrid", "HybridExecutor"), # Might not be importable if deps missing
        ("configurator.core.state.manager", "StateManager"),
        # ("configurator.validators.orchestrator", "ValidationOrchestrator"),
        ("configurator.profiles.manager", "ProfileManager"),
        ("configurator.modules.base", "ConfigurationModule"),
    ]

    # Generate index
    index_lines = ["# API Reference", "", "## Core Components", ""]

    for module_name, class_name in components:
        try:
            mod = importlib.import_module(module_name)
            cls = getattr(mod, class_name)

            doc_file = output_dir / f"{class_name}.md"
            doc_content = _generate_class_doc(cls, module_name)
            doc_file.write_text(doc_content)

            index_lines.append(f"- [{class_name}]({class_name}.md)")
            print(f"✅ Generated API doc: {doc_file}")

        except (ImportError, AttributeError) as e:
            print(f"⚠️ Failed to document {module_name}.{class_name}: {e}")

    # Write index
    (output_dir / "index.md").write_text("\n".join(index_lines))


def _generate_class_doc(cls, module_name):
    """Generate markdown doc for a class."""
    lines = []
    lines.append(f"# {cls.__name__}")
    lines.append("")
    lines.append(f"**Module:** `{module_name}`")
    lines.append("")

    # Docstring
    if cls.__doc__:
        lines.append(inspect.getdoc(cls))
    lines.append("")

    # Methods
    lines.append("## Methods")
    lines.append("")

    for name, member in inspect.getmembers(cls):
        if name.startswith("_") and name != "__init__":
            continue

        if inspect.isfunction(member):
            sig = str(inspect.signature(member))
            lines.append(f"### `{name}{sig}`")
            lines.append("")
            if member.__doc__:
                lines.append(inspect.getdoc(member))
            lines.append("")
            lines.append("---")
            lines.append("")

    return "\n".join(lines)


def generate_cli_docs(output_file: Path):
    """Generate markdown documentation for all CLI commands."""

    lines = []

    # Header
    lines.append("# CLI Command Reference")
    lines.append("")
    lines.append("Complete reference for all `vps-configurator` commands.")
    lines.append("")

    # Global options
    lines.append("## Global Options")
    lines.append("")
    lines.append("These options are available for all commands:")
    lines.append("")
    lines.append("| Option | Description |")
    lines.append("|--------|-------------|")
    lines.append("| `--verbose, -v` | Enable verbose output |")
    lines.append("| `--quiet, -q` | Suppress output |")
    lines.append("| `--config PATH` | Use custom config file |")
    lines.append("| `--version` | Show version and exit |")
    lines.append("| `--help` | Show help message |")
    lines.append("")

    # Commands
    lines.append("## Commands")
    lines.append("")

    # Iterate through all commands
    for command_name in sorted(cli.commands.keys()):
        command = cli.commands[command_name]

        # Command header
        lines.append(f"### `vps-configurator {command_name}`")
        lines.append("")

        # Description
        if command.help:
            lines.append(command.help)
            lines.append("")

        # Syntax
        lines.append("**Syntax:**")
        lines.append("```bash")

        # Build syntax string
        syntax = f"vps-configurator {command_name}"

        # Add options
        for param in command.params:
            if isinstance(param, click.Option):
                param_str = (
                    f"[{param.name.upper()}]" if not param.required else f"{param.name.upper()}"
                )
                syntax += f" {param_str}"

        lines.append(syntax)
        lines.append("```")
        lines.append("")

        # Options table
        if command.params:
            lines.append("**Options:**")
            lines.append("")
            lines.append("| Option | Type | Description | Default |")
            lines.append("|--------|------|-------------|---------|")

            for param in command.params:
                if isinstance(param, click.Option):
                    opts = ", ".join([f"`{opt}`" for opt in param.opts])
                    param_type = param.type.name if hasattr(param.type, "name") else "string"
                    description = param.help or ""
                    default = f"`{param.default}`" if param.default is not None else "-"

                    lines.append(f"| {opts} | {param_type} | {description} | {default} |")

            lines.append("")

        # Examples
        lines.append("**Examples:**")
        lines.append("")
        lines.append("```bash")

        # Add common usage examples
        if command_name == "install":
            lines.append("# Interactive wizard")
            lines.append("vps-configurator install --wizard")
            lines.append("")
            lines.append("# Use beginner profile")
            lines.append("vps-configurator install --profile beginner")
            lines.append("")
            lines.append("# Dry run (preview without installing)")
            lines.append("vps-configurator install --profile advanced --dry-run")

        elif command_name == "wizard":
            lines.append("# Launch interactive wizard")
            lines.append("vps-configurator wizard")

        elif command_name == "verify":
            lines.append("# Verify all installed modules")
            lines.append("vps-configurator verify")
            lines.append("")
            lines.append("# Verify specific module")
            lines.append("vps-configurator verify --module docker")

        elif command_name == "visualize":
            lines.append("# Visualize default profile")
            lines.append("vps-configurator visualize")
            lines.append("")
            lines.append("# Export to Mermaid file")
            lines.append(
                "vps-configurator visualize --profile fullstack --format mermaid-file -o graph.mmd"
            )

        elif command_name == "profiles":
            lines.append("# List available profiles")
            lines.append("vps-configurator profiles")
            lines.append("")
            lines.append("# Inspect a profile")
            lines.append("vps-configurator profiles inspect beginner")

        lines.append("```")
        lines.append("")

        # Related commands
        lines.append("**See also:**")
        related = get_related_commands(command_name)
        for rel in related:
            lines.append(f"- [`{rel}`](#vps-configurator-{rel})")
        lines.append("")

        lines.append("---")
        lines.append("")

    # Exit codes
    lines.append("## Exit Codes")
    lines.append("")
    lines.append("| Code | Meaning |")
    lines.append("|------|---------|")
    lines.append("| 0 | Success |")
    lines.append("| 1 | General error |")
    lines.append("| 2 | Invalid usage |")
    lines.append("| 3 | Validation failed |")
    lines.append("| 4 | Installation failed |")
    lines.append("| 130 | Interrupted by user (Ctrl+C) |")
    lines.append("")

    # Environment variables
    lines.append("## Environment Variables")
    lines.append("")
    lines.append("| Variable | Description | Default |")
    lines.append("|----------|-------------|---------|")
    lines.append("| `VPS_CONFIG_FILE` | Default config file path | `config/default.yaml` |")
    lines.append("| `VPS_LOG_LEVEL` | Log level (DEBUG, INFO, WARNING, ERROR) | `INFO` |")
    lines.append("| `VPS_NO_COLOR` | Disable colored output | `false` |")
    lines.append("")

    # Write to file
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text("\n".join(lines))
    print(f"✅ Generated CLI reference: {output_file}")


def get_related_commands(command_name: str) -> list:
    """Get related commands for cross-referencing."""
    relations = {
        "install": ["wizard", "verify", "profiles", "visualize"],
        "wizard": ["install", "profiles"],
        "verify": ["install", "visualize"],
        "profiles": ["install", "visualize"],
        "visualize": ["install", "profiles"],
        "checklist": ["install", "verify"],
    }
    return relations.get(command_name, [])


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--api-reference":
        generate_api_docs(Path("docs/api-reference"))
    else:
        output = Path("docs/user-guide/cli-reference.md")
        generate_cli_docs(output)
