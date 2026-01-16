import pytest

from configurator.ui.tui_dashboard import InstallationDashboard


@pytest.mark.asyncio
async def test_dashboard_creation():
    app = InstallationDashboard()
    assert app is not None
    # Running textual app tests requires headless environment and more setup.
    # We just verify it instantiates and has methods.
    assert hasattr(app, "add_module")
    assert hasattr(app, "update_module")
