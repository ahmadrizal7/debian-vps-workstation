"""
Validation orchestrator for tiered validation system.

Coordinates running validators across all tiers and displays results.
"""

import logging
from typing import Dict, List, Optional, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from configurator.validators.base import (
    BaseValidator,
    ValidationResult,
    ValidationSeverity,
)


class ValidationOrchestrator:
    """
    Orchestrates validation across multiple tiers.

    Tier 1 (Critical): Must pass for installation to proceed
    Tier 2 (High): Important but can be overridden by user
    Tier 3 (Medium): Warnings only, installation continues
    """

    def __init__(
        self,
        console: Optional[Console] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize validation orchestrator.

        Args:
            console: Rich console for output (creates new if not provided)
            logger: Logger instance (creates new if not provided)
        """
        self.console = console or Console()
        self.logger = logger or logging.getLogger(__name__)
        self.validators: Dict[int, List[BaseValidator]] = {1: [], 2: [], 3: []}

    def register_validator(self, tier: int, validator: BaseValidator) -> None:
        """
        Register a validator in a specific tier.

        Args:
            tier: Tier number (1=critical, 2=high, 3=medium)
            validator: Validator instance to register

        Raises:
            ValueError: If tier is not 1, 2, or 3
        """
        if tier not in {1, 2, 3}:
            raise ValueError(f"Invalid tier: {tier}. Must be 1, 2, or 3.")

        self.validators[tier].append(validator)
        self.logger.debug(f"Registered {validator.name} in tier {tier}")

    def run_validation(
        self,
        interactive: bool = True,
        auto_fix: bool = False,
    ) -> Tuple[bool, List[ValidationResult]]:
        """
        Run tiered validation process.

        Args:
            interactive: If True, prompt user for failures; if False, fail immediately
            auto_fix: If True, attempt automatic fixes for failures

        Returns:
            Tuple of (overall_passed, all_results)
        """
        self._display_header()

        all_results: List[ValidationResult] = []

        # Tier 1: Critical (must pass)
        tier1_results = self._run_tier(1, "Critical", interactive, auto_fix)
        all_results.extend(tier1_results)

        # Check if any critical validation failed
        critical_failures = [r for r in tier1_results if not r.passed]
        if critical_failures:
            self._display_results_table(all_results)
            self._display_critical_failure_summary(critical_failures)
            return False, all_results

        # Tier 2: High (can prompt user)
        tier2_results = self._run_tier(2, "High Priority", interactive, auto_fix)
        all_results.extend(tier2_results)

        # Tier 3: Medium (warnings only)
        tier3_results = self._run_tier(3, "Recommended", interactive, auto_fix)
        all_results.extend(tier3_results)

        # Display results
        self._display_results_table(all_results)

        # Determine overall pass/fail
        # Critical must pass, high can be overridden in interactive mode
        critical_passed = all(r.passed for r in tier1_results)
        high_failures = [r for r in tier2_results if not r.passed]

        if not critical_passed:
            overall_passed = False
        elif high_failures and not interactive:
            overall_passed = False
        else:
            overall_passed = True

        self._display_summary(all_results, overall_passed)

        return overall_passed, all_results

    def _run_tier(
        self,
        tier: int,
        tier_name: str,
        interactive: bool,
        auto_fix: bool,
    ) -> List[ValidationResult]:
        """
        Run validators in a specific tier.

        Args:
            tier: Tier number
            tier_name: Display name for tier
            interactive: Whether to prompt for failures
            auto_fix: Whether to attempt auto-fixes

        Returns:
            List of validation results for this tier
        """
        validators = self.validators[tier]
        if not validators:
            return []

        self.console.print(f"\n[bold cyan]Running {tier_name} Validations...[/bold cyan]")

        results: List[ValidationResult] = []

        for validator in validators:
            self.logger.debug(f"Running validator: {validator.name}")

            try:
                result = validator.validate()
                results.append(result)

                # Display immediate feedback
                if result.passed:
                    self.console.print(f"  {result.icon} {validator.name}")
                else:
                    self.console.print(f"  {result.icon} {validator.name}")

                    # Attempt auto-fix if enabled and available
                    if auto_fix and validator.auto_fix_available:
                        self.console.print("    [yellow]Attempting auto-fix...[/yellow]")
                        try:
                            if validator.auto_fix():
                                # Re-validate
                                result = validator.validate()
                                results[-1] = result  # Update result
                                if result.passed:
                                    self.console.print("    [green]✓ Auto-fix successful[/green]")
                        except Exception as e:
                            self.console.print(f"    [red]✗ Auto-fix failed: {e}[/red]")

            except Exception as e:
                self.logger.error(f"Validator {validator.name} raised exception: {e}")
                # Create failure result
                results.append(
                    ValidationResult(
                        validator_name=validator.name,
                        severity=validator.severity,
                        passed=False,
                        message=f"Validation error: {str(e)}",
                        details=str(e),
                    )
                )

        return results

    def _display_header(self) -> None:
        """Display validation header."""
        self.console.print()
        self.console.print(
            Panel(
                "[bold white]System Validation[/bold white]\n"
                "Checking system requirements before installation",
                border_style="cyan",
            )
        )

    def _display_results_table(self, results: List[ValidationResult]) -> None:
        """
        Display validation results in a Rich table.

        Args:
            results: List of validation results to display
        """
        if not results:
            return

        table = Table(title="Validation Results", show_header=True, header_style="bold")
        table.add_column("Status", style="bold", width=6)
        table.add_column("Validation", style="cyan")
        table.add_column("Severity", style="yellow")
        table.add_column("Details")

        for result in results:
            status_style = "green" if result.passed else "red"

            severity_str = result.severity.value.upper()
            if result.severity == ValidationSeverity.CRITICAL:
                severity_color = "red"
            elif result.severity == ValidationSeverity.HIGH:
                severity_color = "yellow"
            else:
                severity_color = "blue"

            details = result.message
            if result.current_value:
                details += f"\n{result.current_value}"

            table.add_row(
                f"[{status_style}]{result.icon}[/{status_style}]",
                result.validator_name,
                f"[{severity_color}]{severity_str}[/{severity_color}]",
                details,
            )

        self.console.print()
        self.console.print(table)

    def _display_critical_failure_summary(self, failures: List[ValidationResult]) -> None:
        """
        Display summary of critical failures.

        Args:
            failures: List of failed critical validations
        """
        self.console.print()
        self.console.print(
            Panel(
                "[bold red]❌ Critical Validation Failures[/bold red]\n\n"
                "The following critical requirements are not met:\n\n"
                + "\n\n".join(
                    f"[yellow]• {f.validator_name}:[/yellow]\n  "
                    f"{f.message}\n  {f.fix_suggestion or ''}"
                    for f in failures
                ),
                border_style="red",
                title="Installation Cannot Continue",
            )
        )

    def _display_summary(self, results: List[ValidationResult], overall_passed: bool) -> None:
        """
        Display validation summary.

        Args:
            results: All validation results
            overall_passed: Whether validation passed overall
        """
        total = len(results)
        passed_count = sum(1 for r in results if r.passed)
        failed_count = total - passed_count

        critical_failed = sum(
            1 for r in results if not r.passed and r.severity == ValidationSeverity.CRITICAL
        )
        high_failed = sum(
            1 for r in results if not r.passed and r.severity == ValidationSeverity.HIGH
        )
        medium_failed = sum(
            1 for r in results if not r.passed and r.severity == ValidationSeverity.MEDIUM
        )

        summary = Text()
        summary.append(f"Total Checks: {total}\n", style="bold")
        summary.append(f"Passed: {passed_count}\n", style="green")
        if failed_count > 0:
            summary.append(f"Failed: {failed_count}\n", style="red")
            if critical_failed > 0:
                summary.append(f"  - Critical: {critical_failed}\n", style="red")
            if high_failed > 0:
                summary.append(f"  - High: {high_failed}\n", style="yellow")
            if medium_failed > 0:
                summary.append(f"  - Medium: {medium_failed}\n", style="blue")

        if overall_passed:
            panel_style = "green"
            title = "✓ Validation Passed"
        else:
            panel_style = "red"
            title = "✗ Validation Failed"

        self.console.print()
        self.console.print(Panel(summary, border_style=panel_style, title=title))
