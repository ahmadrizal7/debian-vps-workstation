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
    
    name = "PHP"
    description = "Install PHP development environment"
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
        
        # Build package list
        packages = [f"php{version}"]
        for ext in extensions:
            packages.append(f"php{version}-{ext}")
        
        self.logger.info(f"Installing PHP {version} with extensions...")
        
        # Note: Debian 13 may have php8.2 or php8.3 in repos
        # Try without version suffix if versioned packages fail
        result = self.run(f"apt-cache show php{version}", check=False)
        
        if not result.success:
            # Fall back to default php packages
            packages = ["php", "php-cli", "php-common"]
            for ext in extensions:
                packages.append(f"php-{ext}")
        
        self.install_packages(packages)
        
        self.logger.info(f"✓ PHP installed")
    
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
