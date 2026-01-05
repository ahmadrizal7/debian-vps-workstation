"""
Interactive setup wizard for beginners.

Provides a friendly, guided configuration experience
with progressive disclosure based on user experience level.
"""

import logging
import sys
from typing import Any, Dict, Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from configurator.config import ConfigManager


class InteractiveWizard:
    """
    Interactive wizard for configuring the workstation.

    Uses progressive disclosure to show appropriate options
    based on user experience level.
    """

    # Common timezones
    TIMEZONES = {
        "1": "Asia/Jakarta",
        "2": "UTC",
        "3": "America/New_York",
        "4": "America/Los_Angeles",
        "5": "Europe/London",
        "6": "Europe/Berlin",
        "7": "Asia/Singapore",
        "8": "Asia/Tokyo",
    }

    def __init__(
        self,
        console: Optional[Console] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize wizard.

        Args:
            console: Rich console instance
            logger: Logger instance
        """
        self.console = console or Console()
        self.logger = logger or logging.getLogger(__name__)
        self.config: Dict[str, Any] = {}

    def run(self) -> Optional[Dict[str, Any]]:
        """
        Run the interactive wizard.

        Returns:
            Configuration dictionary, or None if cancelled
        """
        try:
            # Welcome
            self._show_welcome()

            # Step 1: Select experience level
            profile = self._select_profile()
            self.config["profile"] = profile

            # Step 2: Basic configuration (all profiles)
            self._configure_basic()

            # Step 3: Profile-specific configuration
            if profile == "beginner":
                self._configure_beginner()
            elif profile == "intermediate":
                self._configure_intermediate()
            else:
                self._configure_advanced()

            # Step 4: Show installation plan and confirm
            if not self._confirm_installation():
                return None

            return self.config

        except KeyboardInterrupt:
            self.console.print("\n[yellow]Setup cancelled.[/yellow]")
            return None

    def _show_welcome(self):
        """Display welcome banner."""
        welcome_text = """
[bold cyan]🚀 Debian 13 VPS Workstation Configurator[/bold cyan]

Transform your VPS into a coding powerhouse!

This wizard will guide you through the setup process.
It should take about 5 minutes to answer all questions,
then 30-60 minutes for the actual installation.

[dim]Press Ctrl+C at any time to cancel.[/dim]
        """

        self.console.print(Panel(welcome_text.strip(), border_style="cyan"))
        self.console.print()

    def _select_profile(self) -> str:
        """Let user select their experience level."""
        self.console.print("[bold]Step 1: Select Your Experience Level[/bold]\n")

        # Show profile options
        profiles = ConfigManager.get_profiles()

        self.console.print(
            "1. 🟢 [green]Beginner[/green] - Quick setup with safe defaults (Recommended)"
        )
        self.console.print("   → Perfect if you're new to Linux")
        self.console.print("   → Installs: Remote Desktop, Python, Node.js, Docker, VS Code")
        self.console.print("   → Takes: ~30 minutes\n")

        self.console.print("2. 🟡 [yellow]Intermediate[/yellow] - More control and features")
        self.console.print("   → For users comfortable with Linux basics")
        self.console.print("   → Adds: Go, Cursor IDE, Neovim, Caddy, monitoring")
        self.console.print("   → Takes: ~45 minutes\n")

        self.console.print("3. 🔴 [red]Advanced[/red] - Full control, all features")
        self.console.print("   → For power users and sysadmins")
        self.console.print("   → Adds: All languages, VPN, custom configuration")
        self.console.print("   → Takes: ~60 minutes\n")

        choice = Prompt.ask(
            "Select your level",
            choices=["1", "2", "3"],
            default="1",
        )

        profile_map = {"1": "beginner", "2": "intermediate", "3": "advanced"}
        profile = profile_map[choice]

        self.console.print(f"\n[green]✓ Selected: {profile.capitalize()} profile[/green]\n")

        return profile

    def _configure_basic(self):
        """Configure basic settings (all profiles)."""
        self.console.print("[bold]Step 2: Basic Configuration[/bold]\n")

        # Initialize system config
        self.config["system"] = {}

        # Hostname
        self.config["system"]["hostname"] = Prompt.ask(
            "Enter a hostname for your server",
            default="dev-workstation",
        )

        # Timezone
        self.console.print("\n[bold]Select timezone:[/bold]")
        for key, tz in self.TIMEZONES.items():
            self.console.print(f"  {key}. {tz}")
        self.console.print("  9. Other (enter manually)")

        tz_choice = Prompt.ask(
            "\nSelect timezone",
            choices=list(self.TIMEZONES.keys()) + ["9"],
            default="1",
        )

        if tz_choice == "9":
            self.config["system"]["timezone"] = Prompt.ask("Enter timezone (e.g., America/Chicago)")
        else:
            self.config["system"]["timezone"] = self.TIMEZONES[tz_choice]

        self.console.print(f"\n[green]✓ Hostname: {self.config['system']['hostname']}[/green]")
        self.console.print(f"[green]✓ Timezone: {self.config['system']['timezone']}[/green]\n")

    def _configure_beginner(self):
        """Configure beginner profile (minimal questions)."""
        # Beginner profile uses all defaults
        # Just show what will be installed
        self.console.print("[bold]Step 3: Review Installation[/bold]\n")

        self.console.print("The following will be installed with safe defaults:")
        self.console.print("  ✓ Security: Firewall, fail2ban, automatic updates")
        self.console.print("  ✓ Remote Desktop: xrdp + XFCE4")
        self.console.print("  ✓ Languages: Python 3.11, Node.js 20")
        self.console.print("  ✓ Tools: Docker, Git, VS Code")
        self.console.print("  ✓ Monitoring: Netdata\n")

    def _configure_intermediate(self):
        """Configure intermediate profile."""
        self.console.print("[bold]Step 3: Additional Configuration[/bold]\n")

        # Ask about additional languages
        self.config["languages"] = {}

        if Confirm.ask("Install Go (Golang)?", default=True):
            self.config["languages"]["golang"] = {"enabled": True}

        # Ask about editors
        self.config["tools"] = {"editors": {}}

        if Confirm.ask("Install Cursor IDE (AI-powered)?", default=True):
            self.config["tools"]["editors"]["cursor"] = {"enabled": True}

        if Confirm.ask("Install Neovim?", default=True):
            self.config["tools"]["editors"]["neovim"] = {"enabled": True}

        # Ask about networking
        self.config["networking"] = {}

        if Confirm.ask("Install Caddy (reverse proxy)?", default=True):
            self.config["networking"]["caddy"] = {"enabled": True}

        self.console.print()

    def _configure_advanced(self):
        """Configure advanced profile (full control)."""
        self.console.print("[bold]Step 3: Advanced Configuration[/bold]\n")

        # Languages
        self.console.print("[bold]Programming Languages:[/bold]")
        self.config["languages"] = {}

        for lang in ["golang", "rust", "java", "php"]:
            default = lang in ["golang"]  # Go is popular, default to yes
            if Confirm.ask(f"Install {lang.capitalize()}?", default=default):
                self.config["languages"][lang] = {"enabled": True}

        # Editors
        self.console.print("\n[bold]Code Editors:[/bold]")
        self.config["tools"] = {"editors": {}}

        for editor in ["cursor", "neovim"]:
            if Confirm.ask(f"Install {editor.capitalize()}?", default=True):
                self.config["tools"]["editors"][editor] = {"enabled": True}

        # Networking
        self.console.print("\n[bold]Networking:[/bold]")
        self.config["networking"] = {}

        if Confirm.ask("Install WireGuard VPN?", default=False):
            self.config["networking"]["wireguard"] = {"enabled": True}

        if Confirm.ask("Install Caddy (reverse proxy)?", default=True):
            self.config["networking"]["caddy"] = {"enabled": True}

        # Security options
        self.console.print("\n[bold]Security Options:[/bold]")
        self.config["security"] = {}

        if Confirm.ask("Disable SSH password authentication (keys only)?", default=False):
            self.config["security"]["ssh"] = {"disable_password_auth": True}

        self.console.print()

    def _confirm_installation(self) -> bool:
        """Show installation plan and ask for confirmation."""
        self.console.print("[bold]Step 4: Confirm Installation[/bold]\n")

        # Build summary table
        table = Table(title="Installation Plan", show_header=True)
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")

        # Always installed
        table.add_row("System Configuration", "✓ Will install")
        table.add_row("Security Hardening", "✓ Will install (mandatory)")
        table.add_row("Remote Desktop (xrdp)", "✓ Will install")
        table.add_row("Python", "✓ Will install")
        table.add_row("Node.js", "✓ Will install")
        table.add_row("Docker", "✓ Will install")
        table.add_row("Git", "✓ Will install")
        table.add_row("VS Code", "✓ Will install")

        # Profile-specific
        profile = self.config.get("profile", "beginner")

        if profile in ["intermediate", "advanced"]:
            langs = self.config.get("languages", {})
            if langs.get("golang", {}).get("enabled"):
                table.add_row("Go (Golang)", "✓ Will install")
            if langs.get("rust", {}).get("enabled"):
                table.add_row("Rust", "✓ Will install")
            if langs.get("java", {}).get("enabled"):
                table.add_row("Java", "✓ Will install")
            if langs.get("php", {}).get("enabled"):
                table.add_row("PHP", "✓ Will install")

            editors = self.config.get("tools", {}).get("editors", {})
            if editors.get("cursor", {}).get("enabled"):
                table.add_row("Cursor IDE", "✓ Will install")
            if editors.get("neovim", {}).get("enabled"):
                table.add_row("Neovim", "✓ Will install")

            networking = self.config.get("networking", {})
            if networking.get("wireguard", {}).get("enabled"):
                table.add_row("WireGuard VPN", "✓ Will install")
            if networking.get("caddy", {}).get("enabled"):
                table.add_row("Caddy", "✓ Will install")

        table.add_row("Netdata Monitoring", "✓ Will install")

        self.console.print(table)

        # Estimate time
        times = {"beginner": 30, "intermediate": 45, "advanced": 60}
        estimated_time = times.get(profile, 45)

        self.console.print(f"\n[dim]Estimated installation time: ~{estimated_time} minutes[/dim]")

        self.console.print("\n[yellow]⚠️  This will modify your system configuration.[/yellow]")
        self.console.print(
            "[yellow]   Make sure you have a backup or snapshot of your VPS.[/yellow]\n"
        )

        return Confirm.ask("Ready to start installation?", default=True)
