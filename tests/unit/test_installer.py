from unittest.mock import MagicMock

from configurator.config import ConfigManager
from configurator.core.container import Container
from configurator.core.installer import Installer


class MockModule:
    name = "mock_module"
    priority = 10

    def __init__(self, config=None, **kwargs):
        self.config = config or {}

    def validate(self):
        return True

    def configure(self):
        return True

    def verify(self):
        return True


def test_installer_uses_container():
    # Setup
    config = MagicMock(spec=ConfigManager)
    config.get_enabled_modules.return_value = ["mock_module"]

    def config_get_side_effect(key, default=None):
        if key == "performance.max_workers":
            return 4
        return default or {}

    config.get.side_effect = config_get_side_effect

    container = Container()

    # Register a mock module
    mock_module_instance = MagicMock(wraps=MockModule())
    container.factory("mock_module", lambda c, config: mock_module_instance)

    installer = Installer(config=config, container=container)

    # Mock internal components to avoid complex setup
    installer.validator_orchestrator = MagicMock()
    installer.validator_orchestrator.run_validation.return_value = (True, [])
    installer.plugin_manager.load_plugins = MagicMock()

    # Execute
    result = installer.install(skip_validation=True)

    # Verify
    assert result is True
    # Verify container was used
    assert container.has("mock_module")
    # Verify module methods were called
    mock_module_instance.validate.assert_called_once()
    mock_module_instance.configure.assert_called_once()
    mock_module_instance.verify.assert_called_once()


def test_installer_verify_uses_container():
    # Setup
    config = MagicMock(spec=ConfigManager)
    config.get_enabled_modules.return_value = ["mock_module"]
    config.get.return_value = {}

    container = Container()
    mock_module_instance = MagicMock(wraps=MockModule())
    container.factory("mock_module", lambda c, config: mock_module_instance)

    installer = Installer(config=config, container=container)

    # Execute
    result = installer.verify()

    # Verify
    assert result is True
    mock_module_instance.verify.assert_called_once()
