from pathlib import Path
from typing import List

from configurator.dependencies.registry import DependencyRegistry


class MermaidExporter:
    """
    Export dependency graph as Mermaid diagram.
    """

    def __init__(self, modules: List[str]):
        self.modules = modules

    def export_flowchart(self) -> str:
        """
        Export as Mermaid flowchart.
        """
        lines = []
        lines.append("```mermaid")
        lines.append("flowchart TD")
        lines.append("")

        # Define nodes
        for module_name in self.modules:
            dependency = DependencyRegistry.get(module_name)
            display_name = module_name.replace("_", " ").title()

            # Add styling based on type
            if dependency and dependency.force_sequential:
                lines.append(f"    {module_name}[{display_name}]::: sequential")
            else:
                lines.append(f"    {module_name}[{display_name}]")

        lines.append("")

        # Define edges (dependencies)
        for module_name in self.modules:
            dependency = DependencyRegistry.get(module_name)
            if dependency and dependency.depends_on:
                for dep in dependency.depends_on:
                    # Only show edge if dependency is also in scope
                    if dep in self.modules:
                        lines.append(f"    {module_name} --> {dep}")
                    # Optionally show external dependencies differently?
                    # For now only internal

        lines.append("")

        # Add styling classes
        lines.append("    classDef sequential fill:#f9f,stroke:#333,stroke-width:2px")

        lines.append("```")

        return "\n".join(lines)

    def export_graph(self) -> str:
        """Export as Mermaid graph (alternative style)."""
        lines = []
        lines.append("```mermaid")
        lines.append("graph LR")
        lines.append("")

        for module_name in self.modules:
            dependency = DependencyRegistry.get(module_name)
            if dependency and dependency.depends_on:
                for dep in dependency.depends_on:
                    if dep in self.modules:
                        lines.append(f"    {dep} --> {module_name}")

        lines.append("```")

        return "\n".join(lines)

    def save_to_file(self, path: Path):
        """Save diagram to file."""
        content = self.export_flowchart()
        path.write_text(content)
