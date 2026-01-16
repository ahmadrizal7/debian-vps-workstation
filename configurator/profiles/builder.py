import logging
from typing import Any, Dict, List, Optional

from configurator.dependencies.registry import DependencyRegistry
from configurator.exceptions import ProfileError
from configurator.profiles.manager import Profile
from configurator.profiles.validator import ProfileValidator
from configurator.ux.suggestions import SuggestionEngine


class ProfileBuilder:
    """
    Interactive profile builder with smart suggestions.

    Features:
    - Step-by-step module selection
    - Automatic dependency resolution
    - Conflict detection
    - Smart suggestions
    - Validation
    """

    def __init__(
        self,
        name: str,
        display_name: Optional[str] = None,
        category: str = "custom",
        logger: Optional[logging.Logger] = None,
    ):
        self.name = name
        self.display_name = display_name or name
        self.category = category
        self.logger = logger or logging.getLogger(__name__)

        self.enabled_modules: List[str] = []
        self.module_config: Dict[str, Any] = {}
        self.system_config: Dict[str, Any] = {}
        self.description: str = ""
        self.tags: List[str] = []

        self.validator = ProfileValidator()
        self.suggestion_engine = SuggestionEngine()

    def add_module(self, module_name: str) -> "ProfileBuilder":
        """
        Add module to profile.

        Automatically adds dependencies.

        Args:
            module_name: Module to add

        Returns:
            Self for chaining
        """
        if module_name in self.enabled_modules:
            self.logger.info(f"Module '{module_name}' already enabled")
            return self

        # Add module
        self.enabled_modules.append(module_name)

        # Add dependencies
        dependency = DependencyRegistry.get(module_name)
        if dependency:
            for dep in dependency.depends_on:
                if dep not in self.enabled_modules:
                    self.logger.info(f"Auto-adding dependency: {dep} (required by {module_name})")
                    self.add_module(dep)  # Recursive add to handle transitive deps

        self.logger.info(f"Added module: {module_name}")

        return self

    def remove_module(self, module_name: str) -> "ProfileBuilder":
        """Remove module from profile."""
        if module_name not in self.enabled_modules:
            self.logger.warning(f"Module '{module_name}' not in profile")
            return self

        # Check if any other modules depend on this
        dependents = []
        for other_module in self.enabled_modules:
            if other_module == module_name:
                continue

            dep = DependencyRegistry.get(other_module)
            if dep and module_name in dep.depends_on:
                dependents.append(other_module)

        if dependents:
            self.logger.warning(
                f"Cannot remove '{module_name}': required by {', '.join(dependents)}"
            )
            return self

        self.enabled_modules.remove(module_name)

        # Remove config if exists
        if module_name in self.module_config:
            del self.module_config[module_name]

        self.logger.info(f"Removed module: {module_name}")

        return self

    def configure_module(self, module_name: str, config: Dict[str, Any]) -> "ProfileBuilder":
        """Set configuration for a module."""
        if module_name not in self.enabled_modules:
            self.logger.warning(f"Module '{module_name}' not enabled. Adding it first.")
            self.add_module(module_name)

        self.module_config[module_name] = config
        self.logger.info(f"Configured module: {module_name}")

        return self

    def set_system_config(self, config: Dict[str, Any]) -> "ProfileBuilder":
        """Set system configuration."""
        self.system_config.update(config)
        return self

    def set_description(self, description: str) -> "ProfileBuilder":
        """Set profile description."""
        self.description = description
        return self

    def add_tag(self, tag: str) -> "ProfileBuilder":
        """Add tag to profile."""
        if tag not in self.tags:
            self.tags.append(tag)
        return self

    def get_suggestions(self) -> List[str]:
        """
        Get smart module suggestions based on current selection.

        Returns:
            List of suggested module names
        """
        return self.suggestion_engine.suggest_modules(self.enabled_modules)

    def build(self) -> Profile:
        """
        Build and validate the profile.

        Returns:
            Validated Profile instance

        Raises:
            ProfileError: If validation fails
        """
        profile = Profile(
            name=self.name,
            display_name=self.display_name,
            description=self.description,
            category=self.category,
            enabled_modules=self.enabled_modules,
            module_config=self.module_config,
            system_config=self.system_config,
            tags=self.tags,
        )

        # Validate
        errors = self.validator.validate(profile)
        if errors:
            raise ProfileError(
                what=f"Profile '{self.name}' validation failed",
                why=f"Errors: {', '.join(errors)}",
                how="Fix the validation errors and try again",
            )

        return profile
