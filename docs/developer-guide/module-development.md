# Module Development Guide

Learn how to create custom modules for Debian VPS Workstation Configurator.

## Overview

Modules are the building blocks of the configurator. Each module is a Python class that handles the installation, configuration, and verification of a specific tool or component.

## Architecture

All modules inherit from `ConfigurationModule` and implements three key methods:

1. `validate()`: Checks if the module can be installed.
2. `configure()`: Performs the installation and configuration.
3. `verify()`: Checks if the installation was successful.

## Step-by-Step: Creating a Module

Let's create a module to install `Redis`.

### 1. Create the Module File

Create `configurator/modules/redis.py`:

```python
from configurator.modules.base import ConfigurationModule
from configurator.dependencies.decorators import module
from configurator.utils.system import system_command, package_installed

@module(
    name="redis",
    description="Redis In-Memory Data Store",
    priority=60,
    depends_on=["system"]
)
class RedisModule(ConfigurationModule):

    def validate(self) -> bool:
        """Check if Redis is already installed or can be installed."""
        if package_installed("redis-server"):
            self.logger.info("Redis is already installed.")
            # We return True so we can proceed to configure/verify mainly,
            # or you can return False if you want to skip re-install logic.
            # Usually we return True and handle idempotency in configure.
        return True

    def configure(self) -> bool:
        """Install and configure Redis."""
        self.logger.info("Installing Redis...")

        # 1. Install package
        if not system_command(["apt-get", "install", "-y", "redis-server"]):
            self.logger.error("Failed to install redis-server")
            return False

        # 2. Configure (example: enable systemd)
        system_command(["systemctl", "enable", "redis-server"])
        system_command(["systemctl", "start", "redis-server"])

        return True

    def verify(self) -> bool:
        """Verify Redis is running."""
        # Check service status
        if not system_command(["systemctl", "is-active", "--quiet", "redis-server"]):
            self.logger.error("Redis service is not active")
            return False

        # Check functionality
        output = system_command(["redis-cli", "ping"], capture_output=True)
        if "PONG" not in output:
            self.logger.error("Redis did not respond to ping")
            return False

        return True
```

### 2. Register the Module

The `@module` decorator automatically registers the class if the file is imported.
Ensure the file is imported in `configurator/modules/__init__.py` or dynamically loaded.

### 3. Test the Module

Create a test file `tests/unit/modules/test_redis.py`:

```python
import pytest
from unittest.mock import patch, MagicMock
from configurator.modules.redis import RedisModule

@pytest.fixture
def module():
    return RedisModule()

def test_validate(module):
    with patch("configurator.modules.redis.package_installed", return_value=False):
        assert module.validate() is True

def test_configure(module):
    with patch("configurator.modules.redis.system_command", return_value=True) as mock_cmd:
        assert module.configure() is True
        assert mock_cmd.call_count >= 2

def test_verify_success(module):
    with patch("configurator.modules.redis.system_command") as mock_cmd:
        # Mock service check True, ping output PONG
        def side_effect(cmd, **kwargs):
            if "is-active" in cmd: return True
            if "ping" in cmd: return "PONG"
            return False

        mock_cmd.side_effect = side_effect
        mock_cmd.side_effect = None # Reset if needed, or use proper mock
        # Simpler approach:
        mock_cmd.return_value = "PONG" # for verify call if simplified

        # Real mock setup
        # ...
```

### 4. Use the Module

Run it via CLI:

```bash
vps-configurator install --module redis
```

## Best Practices

- **Idempotency**: `configure()` should be safe to run multiple times. Check if work is needed before doing it.
- **Error Handling**: Catch exceptions and log errors. Return `False` on failure.
- **Verification**: `verify()` should actually test the functionality, not just check files.
- **Dependencies**: Declare dependencies via `depends_on`.
- **Logging**: Use `self.logger` for all output.

## Advanced Features

### Configuration Parameters

Access user config via `self.config`:

```python
def configure(self):
    port = self.config.get("redis.port", 6379)
    # Use port in config file...
```

### User Interaction

If interactive mode is allowed:

```python
from configurator.ui.prompts import Confirm

if Confirm.ask("Bind to all interfaces?"):
    # Configure 0.0.0.0
```

_Note: Always provide a default for non-interactive mode._

## Contributing

Submit your module via Pull Request! See [Contributing Guide](../contributing.md).
