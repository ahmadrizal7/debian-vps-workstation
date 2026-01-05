"""
Base class for all configuration modules.

Provides the interface that all modules must implement.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from configurator.core.rollback import RollbackManager
from configurator.exceptions import ModuleExecutionError
from configurator.utils.command import run_command, CommandResult


class ConfigurationModule(ABC):
    """
    Abstract base class for all configuration modules.
    
    Each module must implement:
    - validate(): Check prerequisites before installation
    - configure(): Execute the installation/configuration
    - verify(): Verify the installation was successful
    
    The rollback() method is provided with a default implementation
    that executes commands registered during configure().
    """
    
    # Module metadata - override in subclasses
    name: str = "Base Module"
    description: str = "Base configuration module"
    priority: int = 100  # Lower = higher priority
    mandatory: bool = False  # If True, installation stops on failure
    
    def __init__(
        self,
        config: Dict[str, Any],
        logger: Optional[logging.Logger] = None,
        rollback_manager: Optional[RollbackManager] = None,
    ):
        """
        Initialize the module.
        
        Args:
            config: Module-specific configuration
            logger: Logger instance
            rollback_manager: Rollback manager for tracking changes
        """
        self.config = config
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.rollback_manager = rollback_manager or RollbackManager()
        
        # State tracking
        self.state: Dict[str, Any] = {}
        self.installed_packages: List[str] = []
        self.started_services: List[str] = []
    
    @abstractmethod
    def validate(self) -> bool:
        """
        Validate prerequisites before installation.
        
        Check that all requirements are met before attempting installation.
        This might include checking for existing installations, available
        disk space, network connectivity, etc.
        
        Returns:
            True if ready to install, False otherwise
            
        Raises:
            PrerequisiteError with helpful message if validation fails
        """
        pass
    
    @abstractmethod
    def configure(self) -> bool:
        """
        Execute configuration/installation.
        
        This is the main method that performs the actual work.
        Should register rollback actions for any changes made.
        
        Returns:
            True if successful
            
        Raises:
            ModuleExecutionError with helpful message on failure
        """
        pass
    
    @abstractmethod
    def verify(self) -> bool:
        """
        Verify installation was successful.
        
        Check that everything is working correctly after installation.
        This might include checking service status, running test commands,
        verifying file permissions, etc.
        
        Returns:
            True if verified successfully
        """
        pass
    
    def rollback(self) -> bool:
        """
        Rollback changes made by this module.
        
        Default implementation uses the rollback manager.
        Override if custom rollback logic is needed.
        
        Returns:
            True if rollback was successful
        """
        return self.rollback_manager.rollback()
    
    # Utility methods for subclasses
    
    def run(
        self,
        command: str,
        check: bool = True,
        rollback_command: Optional[str] = None,
        description: str = "",
    ) -> CommandResult:
        """
        Run a shell command with optional rollback registration.
        
        Args:
            command: Command to run
            check: Raise exception on non-zero exit code
            rollback_command: Command to undo this action
            description: Description for logging
            
        Returns:
            CommandResult with return code, stdout, stderr
        """
        self.logger.debug(f"Running: {command}")
        
        result = run_command(command, check=check)
        
        if rollback_command and result.success:
            self.rollback_manager.add_command(
                rollback_command,
                description=description or f"Undo: {command}",
            )
        
        return result
    
    def install_packages(
        self,
        packages: List[str],
        update_cache: bool = True,
    ) -> bool:
        """
        Install APT packages.
        
        Args:
            packages: List of package names
            update_cache: Run apt-get update first
            
        Returns:
            True if installation was successful
        """
        if not packages:
            return True
        
        self.logger.info(f"Installing packages: {', '.join(packages)}")
        
        if update_cache:
            self.run("apt-get update", check=False)
        
        # Install packages
        packages_str = " ".join(packages)
        result = self.run(
            f"DEBIAN_FRONTEND=noninteractive apt-get install -y {packages_str}",
            check=True,
        )
        
        if result.success:
            self.installed_packages.extend(packages)
            self.rollback_manager.add_package_remove(
                packages,
                description=f"Remove packages: {', '.join(packages)}",
            )
        
        return result.success
    
    def enable_service(self, service: str, start: bool = True) -> bool:
        """
        Enable and optionally start a systemd service.
        
        Args:
            service: Service name
            start: Also start the service
            
        Returns:
            True if successful
        """
        self.logger.info(f"Enabling service: {service}")
        
        self.run(f"systemctl enable {service}", check=True)
        
        if start:
            self.run(f"systemctl start {service}", check=True)
            self.started_services.append(service)
            self.rollback_manager.add_service_stop(service)
        
        return True
    
    def restart_service(self, service: str) -> bool:
        """
        Restart a systemd service.
        
        Args:
            service: Service name
            
        Returns:
            True if successful
        """
        self.logger.info(f"Restarting service: {service}")
        result = self.run(f"systemctl restart {service}", check=False)
        return result.success
    
    def is_service_active(self, service: str) -> bool:
        """
        Check if a systemd service is running.
        
        Args:
            service: Service name
            
        Returns:
            True if service is active
        """
        result = self.run(f"systemctl is-active {service}", check=False)
        return result.stdout.strip() == "active"
    
    def command_exists(self, command: str) -> bool:
        """
        Check if a command exists.
        
        Args:
            command: Command name
            
        Returns:
            True if command exists
        """
        result = self.run(f"which {command}", check=False)
        return result.success
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            default: Default value if not found
            
        Returns:
            Configuration value
        """
        keys = key.split(".")
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
