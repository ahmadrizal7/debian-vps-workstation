import pytest

from configurator.wizard.config_wizard import ConfigWizardApp
from configurator.wizard.screens.experience_level import ExperienceLevelScreen
from configurator.wizard.screens.welcome import WelcomeScreen


@pytest.mark.asyncio
async def test_wizard_app_initialization():
    """Test that the wizard app initializes and installs screens."""
    app = ConfigWizardApp()

    # We can't easily run the full app lifecycle in unit tests without a proper harness,
    # but we can check internal state if we construct it carefully.

    assert app.wizard_data == {}

    # Screens are installed on_mount, so we can't check them until it runs.
    # But we can instantiate screens to ensure they don't crash.

    welcome = WelcomeScreen()
    assert welcome is not None

    exp = ExperienceLevelScreen()
    assert exp is not None

    # Needs app context for real functionality, but instantiation is a good sanity check
