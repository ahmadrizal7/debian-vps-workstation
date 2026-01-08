"""
PHP module for PHP development environment.

Handles:
- PHP installation
- Composer package manager
- Common extensions
"""

from configurator.modules.base import ConfigurationModule


class PHPModule(ConfigurationModule):
    """
    PHP development environment module.
    """

    name = "PHP Development"
    description = "PHP environment with Composer"
    depends_on = ["system"]
    priority = 45
    mandatory = False

    # Common PHP extensions
    PHP_EXTENSIONS = [
        "cli",
        "common",
        "curl",
        "mbstring",
        "xml",
        "zip",
        "gd",
        "mysql",
        "pgsql",
        "sqlite3",
        "redis",
        "intl",
    ]

    def validate(self) -> bool:
        """Validate PHP prerequisites."""
        # Check if PHP is already installed
        if self.command_exists("php"):
            result = self.run("php --version | head -1", check=False)
            self.logger.info(f"  Found existing PHP: {result.stdout.strip()}")

        return True

    def configure(self) -> bool:
        """Install and configure PHP."""
        self.logger.info("Installing PHP...")

        # 1. Install PHP
        self._install_php()

        # 2. Install Composer
        self._install_composer()

        self.logger.info("✓ PHP development environment ready")
        return True

    def verify(self) -> bool:
        """Verify PHP installation."""
        checks_passed = True

        # Check php
        result = self.run("php --version | head -1", check=False)
        if result.success:
            self.logger.info(f"✓ {result.stdout.strip()}")
        else:
            self.logger.error("PHP not found!")
            checks_passed = False

        # Check composer
        result = self.run("composer --version 2>/dev/null | head -1", check=False)
        if result.success:
            self.logger.info(f"✓ {result.stdout.strip()}")
        else:
            self.logger.warning("Composer not found")

        return checks_passed

    def _install_php(self):
        """Install PHP and extensions."""
        version = self.get_config("version", "8.2")
        extensions = self.get_config("extensions", self.PHP_EXTENSIONS)

        # Strategy: Prefer generic 'php' packages on Debian 13 (Trixie)
        # as they map to the correct stable version (e.g. 8.2 or 8.3).
        # Hardcoding versions causes failures and trips the circuit breaker.

        # We will try generic first.
        self.logger.info("Attempting installation with generic PHP packages...")
        packages = ["php", "php-cli", "php-common"]
        for ext in extensions:
            packages.append(f"php-{ext}")

        try:
            self.install_packages(packages)
            self.logger.info("✓ PHP installed (generic packages)")
            return
        except Exception as e:
            self.logger.warning(f"Generic PHP installation failed: {e}")
            # Reset breaker? We can't easily.
            # But maybe specific version works?
            # If generic failed, apt might be broken, but let's try specific as fallback.

        self.logger.info(f"Falling back to specific version php{version}...")
        packages = [f"php{version}"]
        for ext in extensions:
            packages.append(f"php{version}-{ext}")

        self.install_packages(packages)
        self.logger.info(f"✓ PHP {version} installed")

    def _install_composer(self):
        """Install Composer package manager."""
        self.logger.info("Installing Composer...")

        # Download installer
        self.run(
            "curl -sS https://getcomposer.org/installer -o /tmp/composer-setup.php",
            check=True,
        )

        # Verify installer (optional but recommended)
        # Install globally
        self.run(
            "php /tmp/composer-setup.php --install-dir=/usr/local/bin --filename=composer",
            check=True,
        )

        # Cleanup
        self.run("rm /tmp/composer-setup.php", check=False)

        self.logger.info("✓ Composer installed")
