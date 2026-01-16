# tests/integration/test_progress_reporting.py
from configurator.core.reporter.rich_reporter import RichProgressReporter


def test_progress_reporting_full_flow():
    """Simulate a complete installation flow with reporter."""
    import io

    from rich.console import Console

    # Use real console capturing output
    output = io.StringIO()
    console = Console(file=output, force_terminal=True)
    reporter = RichProgressReporter(console=console)

    # 1. Start
    reporter.start("Integration Test")

    # 2. Phase 1
    reporter.start_phase("Phase 1", total_steps=50)
    reporter.update_progress(10, 5, 50)
    reporter.update("Working...")
    reporter.complete_phase(success=True)

    # 3. Phase 2
    reporter.start_phase("Phase 2")
    reporter.complete_phase(success=False)

    from datetime import datetime

    from configurator.core.execution.base import ExecutionResult

    # 4. Summary
    results = {
        "module_a": ExecutionResult(
            module_name="module_a",
            success=True,
            started_at=datetime.now(),
            completed_at=datetime.now(),
            duration_seconds=1.0,
            error=None,
        ),
        "module_b": ExecutionResult(
            module_name="module_b",
            success=False,
            started_at=datetime.now(),
            completed_at=datetime.now(),
            duration_seconds=0.5,
            error=Exception("Failed"),
        ),
    }
    reporter.show_summary(results)

    # Verify console interaction (rough check)
    # Verify console output
    output_str = output.getvalue()
    assert "Integration Test" in output_str
    assert "Phase 1" in output_str
    assert "Installation Summary" in output_str
    assert "module_a" in output_str
    assert "module_b" in output_str
