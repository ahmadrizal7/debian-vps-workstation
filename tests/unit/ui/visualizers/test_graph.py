from configurator.ui.visualizers.dependency_graph import DependencyGraphVisualizer
from configurator.ui.visualizers.mermaid_exporter import MermaidExporter


def test_ascii_tree_render():
    """Test ASCII tree rendering."""
    modules = ["system", "desktop", "security"]
    # We implicitly rely on DependencyRegistry having these defined

    viz = DependencyGraphVisualizer(modules)
    output = viz.render_tree()

    # Check structure
    assert "Installation Order" in output
    assert "batch" in output  # Batches should be calculated
    assert "system" in output
    assert "desktop" in output


def test_mermaid_export():
    """Test Mermaid diagram export."""
    modules = ["system", "desktop"]

    exporter = MermaidExporter(modules)
    output = exporter.export_flowchart()

    assert "flowchart TD" in output
    assert "system[System]" in output
    # desktop depends on system, so edge should exist
    assert "desktop --> system" in output


def test_mermaid_graph_export():
    """Test Mermaid graph export."""
    modules = ["system", "desktop"]

    exporter = MermaidExporter(modules)
    output = exporter.export_graph()

    assert "graph LR" in output
    # Arrows might be reversed in graph LR semantic vs flowchart
    # Implementation checks: dep --> module_name (system --> desktop)
    assert "system --> desktop" in output
