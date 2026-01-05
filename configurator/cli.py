"""
Command-line interface for the configurator.

Provides commands:
- install: Run installation
- wizard: Interactive setup wizard
- verify: Verify installation
- rollback: Rollback changes
"""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console

from configurator import __version__
from configurator.config import ConfigManager
from configurator.core.installer import Installer
from configurator.core.reporter import ProgressReporter
from configurator.logger import setup_logger


console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="Debian VPS Configurator")
@click.option(
    "--verbose", "-v",
    is_flag=True,
    help="Enable verbose output",
)
@click.option(
    "--quiet", "-q",
    is_flag=True,
    help="Suppress all but error messages",
)
@click.pass_context
def main(ctx: click.Context, verbose: bool, quiet: bool):
    """
    Debian 13 VPS Workstation Configurator
    
    Transform your Debian 13 VPS into a fully-featured
    remote desktop coding workstation.
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["quiet"] = quiet
    
    # Setup logging
    logger = setup_logger(verbose=verbose, quiet=quiet)
    ctx.obj["logger"] = logger


@main.command()
@click.option(
    "--profile", "-p",
    type=click.Choice(["beginner", "intermediate", "advanced"]),
    default=None,
    help="Installation profile to use",
)
@click.option(
    "--config", "-c",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Path to custom configuration file",
)
@click.option(
    "--non-interactive", "-y",
    is_flag=True,
    help="Run without prompts (use with --profile or --config)",
)
@click.option(
    "--skip-validation",
    is_flag=True,
    help="Skip system validation checks",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be done without making changes",
)
@click.pass_context
def install(
    ctx: click.Context,
    profile: Optional[str],
    config: Optional[Path],
    non_interactive: bool,
    skip_validation: bool,
    dry_run: bool,
):
    """
    Install and configure the workstation.
    
    Examples:
    
      # Interactive wizard (recommended for beginners)
      vps-configurator wizard
      
      # Quick install with beginner profile
      vps-configurator install --profile beginner -y
      
      # Install with custom config
      vps-configurator install --config myconfig.yaml -y
    """
    logger = ctx.obj["logger"]
    
    # If no profile or config specified, suggest using wizard
    if not profile and not config and not non_interactive:
        console.print(
            "\n[yellow]Tip: Use 'vps-configurator wizard' for interactive setup![/yellow]\n"
        )
        
        # Ask which profile to use
        console.print("Available profiles:")
        for name, info in ConfigManager.get_profiles().items():
            console.print(f"  • {info['name']}")
            console.print(f"    {info['description']}")
        
        profile = click.prompt(
            "\nSelect profile",
            type=click.Choice(["beginner", "intermediate", "advanced"]),
            default="beginner",
        )
    
    # Load configuration
    try:
        config_manager = ConfigManager(
            config_file=config,
            profile=profile,
        )
        
        # Set non-interactive mode
        if non_interactive:
            config_manager.set("interactive", False)
        
        # Validate configuration
        config_manager.validate()
        
    except Exception as e:
        logger.error(str(e))
        sys.exit(1)
    
    # Create installer and run
    reporter = ProgressReporter(console)
    installer = Installer(
        config=config_manager,
        logger=logger,
        reporter=reporter,
    )
    
    if dry_run:
        console.print("[yellow]DRY RUN MODE - No changes will be made[/yellow]\n")
    
    # Run installation
    success = installer.install(
        skip_validation=skip_validation,
        dry_run=dry_run,
    )
    
    sys.exit(0 if success else 1)


@main.command()
@click.pass_context
def wizard(ctx: click.Context):
    """
    Run the interactive setup wizard.
    
    Guides you through the configuration process
    with beginner-friendly prompts.
    """
    from configurator.wizard import InteractiveWizard
    
    logger = ctx.obj["logger"]
    
    try:
        wizard_instance = InteractiveWizard(console=console, logger=logger)
        config = wizard_instance.run()
        
        if config is None:
            console.print("[yellow]Setup cancelled.[/yellow]")
            sys.exit(0)
        
        # Create config manager with wizard results
        config_manager = ConfigManager(profile=config.get("profile"))
        
        # Override with wizard selections
        for key, value in config.items():
            if key != "profile":
                config_manager.set(key, value)
        
        # Run installation
        reporter = ProgressReporter(console)
        installer = Installer(
            config=config_manager,
            logger=logger,
            reporter=reporter,
        )
        
        success = installer.install()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Setup cancelled.[/yellow]")
        sys.exit(0)
    except Exception as e:
        logger.exception("Wizard failed")
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@main.command()
@click.option(
    "--profile", "-p",
    type=click.Choice(["beginner", "intermediate", "advanced"]),
    default=None,
    help="Profile that was used for installation",
)
@click.option(
    "--config", "-c",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Path to configuration file used for installation",
)
@click.pass_context
def verify(
    ctx: click.Context,
    profile: Optional[str],
    config: Optional[Path],
):
    """
    Verify the installation.
    
    Checks that all installed components are working correctly.
    """
    logger = ctx.obj["logger"]
    
    # Load configuration
    config_manager = ConfigManager(
        config_file=config,
        profile=profile or "beginner",
    )
    
    # Create installer and verify
    reporter = ProgressReporter(console)
    installer = Installer(
        config=config_manager,
        logger=logger,
        reporter=reporter,
    )
    
    success = installer.verify()
    
    if success:
        console.print("\n[green]✓ All components verified successfully![/green]")
    else:
        console.print("\n[yellow]⚠ Some components have issues. Check the output above.[/yellow]")
    
    sys.exit(0 if success else 1)


@main.command()
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be rolled back without making changes",
)
@click.option(
    "--force", "-f",
    is_flag=True,
    help="Skip confirmation prompt",
)
@click.pass_context
def rollback(
    ctx: click.Context,
    dry_run: bool,
    force: bool,
):
    """
    Rollback installation changes.
    
    Undoes changes made during the installation process.
    Use with caution!
    """
    logger = ctx.obj["logger"]
    
    if not force:
        console.print(
            "[yellow]WARNING: This will attempt to undo installation changes.[/yellow]"
        )
        confirm = click.confirm("Are you sure you want to continue?")
        if not confirm:
            console.print("Rollback cancelled.")
            sys.exit(0)
    
    # Create installer and rollback
    config_manager = ConfigManager()
    reporter = ProgressReporter(console)
    installer = Installer(
        config=config_manager,
        logger=logger,
        reporter=reporter,
    )
    
    if dry_run:
        console.print("[yellow]DRY RUN MODE - No changes will be made[/yellow]\n")
    
    success = installer.rollback()
    
    if success:
        console.print("\n[green]✓ Rollback completed successfully![/green]")
    else:
        console.print("\n[red]✗ Rollback encountered errors. Check the output above.[/red]")
    
    sys.exit(0 if success else 1)


@main.command()
def profiles():
    """
    List available installation profiles.
    """
    console.print("\n[bold]Available Installation Profiles[/bold]\n")
    
    for name, info in ConfigManager.get_profiles().items():
        console.print(f"  [cyan]{name}[/cyan]")
        console.print(f"    {info['name']}")
        console.print(f"    {info['description']}")
        console.print()


if __name__ == "__main__":
    main()
