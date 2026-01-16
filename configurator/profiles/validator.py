from typing import Any, List


class ProfileValidator:
    """Validator for configuration profiles."""

    def validate(self, profile: Any) -> List[str]:
        """
        Validate a Profile object.

        Args:
            profile: Profile object to validate

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        # Validate name
        if not profile.name or not isinstance(profile.name, str):
            errors.append("Profile name is required and must be a string")
        elif not profile.name.strip():
            errors.append("Profile name cannot be empty")

        # Validate category
        if not profile.category or not isinstance(profile.category, str):
            errors.append("Profile category is required")

        # Validate enabled_modules
        if not isinstance(profile.enabled_modules, list):
            errors.append("enabled_modules must be a list")

        # Validate module_config
        if not isinstance(profile.module_config, dict):
            errors.append("module_config must be a dictionary")

        # Validate system_config
        if not isinstance(profile.system_config, dict):
            errors.append("system_config must be a dictionary")

        return errors
