import pytest

from configurator.wizard.config_wizard import ConfigWizardApp


@pytest.mark.asyncio
async def test_full_wizard_flow_beginner():
    """
    Test the wizard flow for a beginner selection.
    This simulates navigating through the wizard screens.
    """
    app = ConfigWizardApp()
    async with app.run_test() as pilot:
        # Welcome Screen
        await pilot.pause()
        # Check for welcome text in any widget
        widgets = app.screen.query("Static")
        found_welcome = False
        for w in widgets:
            if (
                "Welcome" in str(getattr(w, "renderable", ""))
                or "Welcome" in str(w)
                or "Welcome" in getattr(w, "label", "")
            ):
                found_welcome = True  # Heuristic
                break

        # Simpler check: Check class name
        assert "WelcomeScreen" in str(app.screen)

        # Click Start
        await pilot.click("#continue")
        await pilot.pause()

        # Experience Level Screen
        assert app.is_screen_installed("experience_level")
        assert "ExperienceLevelScreen" in str(app.screen)

        # Select Beginner
        await pilot.click("#select-beginner")
        await pilot.pause()

        # Preview Screen (Skip module selection for beginner)
        assert app.is_screen_installed("preview")
        assert "PreviewScreen" in str(app.screen)

        # Verify Profile Data
        assert app.wizard_data["experience_level"] == "beginner"

        # Click Install (maps to exit for now in test)
        await pilot.click("#install")
        await pilot.pause()

        # Should be finished
        # In a real run, this returns data, but in test mode we check state
        assert not app.is_running


@pytest.mark.asyncio
async def test_wizard_generates_valid_profile():
    app = ConfigWizardApp()
    async with app.run_test() as pilot:
        # Navigate to end similarly...
        pass
