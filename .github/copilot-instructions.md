# GitHub Copilot Instructions

## Priority Guidelines

When generating code for this repository:

1. **Version Compatibility**: Always respect Python 3.12+ and the exact versions of frameworks/libraries in pyproject.toml
2. **Context Files**: Prioritize patterns from .github/copilot directory and exemplars.md
3. **Codebase Patterns**: Scan existing modules for established patterns before generating new code
4. **Architectural Consistency**: Maintain Modular Plugin Architecture with strict layer boundaries
5. **Code Quality**: Prioritize maintainability, performance, security, and testability equally

## Technology Version Detection

**Language Version:**

- Python 3.12+ (minimum)
- Use only features available in Python 3.12
- Type hints required for all public APIs
- Dataclasses preferred over traditional classes for data structures

**Framework Versions:**

```toml
# From pyproject.toml - NEVER exceed these versions
click = "^8.1.0"          # CLI framework
rich = "^13.0.0"          # Terminal output
textual = "^0.40.0"       # TUI framework
pyyaml = "^6.0"           # YAML parsing
paramiko = "^3.3.0"       # SSH operations
cryptography = "^41.0.0"  # Encryption
psutil = "^5.9.0"         # System metrics
networkx = "^3.1"         # Dependency graphs
pytest = "^7.4.0"         # Testing
ruff = "^0.1.0"           # Linting
mypy = "^1.5.0"           # Type checking
```

**Never Use:**

- Python 3.13+ features (match statement, PEP 695 syntax)
- async/await (project uses ThreadPoolExecutor)
- Features beyond library versions specified above

## Context Files

Reference these files in priority order:

1. **exemplars.md**: Gold-standard code examples (9 patterns documented)
2. **Project_Architecture_Blueprint.md**: Complete architecture reference
3. **.github/copilot-instructions.md**: This file
4. **CONTRIBUTING.md**: Contribution guidelines
5. **.cursor/rules/\*.mdc**: Code quality rules

## Codebase Scanning Instructions

**Before generating ANY code:**

1. **For new modules**: Scan `configurator/modules/` for similar implementations
2. **For core components**: Reference `configurator/core/` patterns
3. **For utilities**: Check `configurator/utils/` for existing helpers
4. **For tests**: Match structure from `tests/unit/` or `tests/integration/`

**Pattern Priority:**

- Prioritize patterns from `exemplars.md`
- Then patterns from most recent files (git log)
- Then most tested files (highest coverage)
- Never introduce patterns not in codebase

## Code Quality Standards

### Maintainability

**Naming Conventions** (from actual codebase):

```python
# Classes: PascalCase
class ConfigurationModule(ABC): ...
class DockerModule(ConfigurationModule): ...

# Functions/Methods: snake_case
def install_packages_resilient(self, packages: List[str]) -> bool: ...
def validate_username(self, username: str) -> bool: ...

# Constants: UPPER_SNAKE_CASE
_APT_LOCK = threading.Lock()
ROLLBACK_STATE_FILE = Path("/var/lib/...")

# Private: Leading underscore
def _add_docker_repository(self): ...
def _format_message(self) -> str: ...

# Module-level: snake_case
rollback_manager = RollbackManager()
```

**Function Length**: Maximum ~50 lines (from codebase analysis)
**Class Length**: Maximum ~700 lines (base.py is 662 lines)
**Single Responsibility**: Each method does ONE thing

### Performance

**Patterns from codebase:**

1. **Lazy Loading** (startup optimization):

```python
# configurator/cli.py pattern
ConfigManager = LazyLoader("configurator.config", "ConfigManager")
Installer = LazyLoader("configurator.core.installer", "Installer")
# Import happens on first access, not at module load
```

2. **Parallel Execution** (45min → 15min):

```python
# Use ThreadPoolExecutor for independent operations
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(module.configure) for module in batch]
    for future in as_completed(futures):
        result = future.result()
```

3. **Caching** (50-90% bandwidth savings):

```python
# Package cache pattern
if self.package_cache_manager:
    self.package_cache_manager.cache_package(package_path)
```

4. **Thread Safety** (APT operations):

```python
# ALWAYS use lock for APT
with self._APT_LOCK:
    result = self.run("apt-get install ...")
```

### Security

**Input Validation** (ALWAYS validate):

```python
# configurator/security/input_validator.py pattern
class InputValidator:
    def validate_username(self, username: str) -> bool:
        if not re.match(r'^[a-z][a-z0-9_-]{2,31}$', username):
            raise ValidationError("Invalid username format")
        return True

    def validate_path(self, path: str) -> bool:
        # Check dangerous characters
        for char in self.DANGEROUS_CHARS:
            if char in path:
                raise ValidationError(f"Path contains dangerous: {char}")
        return True
```

**Supply Chain Security**:

```python
# Always verify checksums and signatures
validator = SupplyChainValidator(config, logger)
validator.verify_apt_key_fingerprint(key_path, expected_fingerprint)
validator.verify_download(url, expected_sha256)
```

**Never:**

- Use subprocess.run directly (use self.run())
- Concatenate strings for shell commands
- Trust external input without validation

### Testability

**Dependency Injection** (all modules):

```python
class DockerModule(ConfigurationModule):
    def __init__(
        self,
        config: Dict[str, Any],
        logger: Optional[logging.Logger] = None,
        rollback_manager: Optional[RollbackManager] = None,
        dry_run_manager: Optional[DryRunManager] = None,
        circuit_breaker_manager: Optional[CircuitBreakerManager] = None,
        package_cache_manager: Optional[PackageCacheManager] = None,
    ):
        # All dependencies injected - testable
        self.config = config
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        # ...
```

**Mock at Boundaries**:

```python
# tests/unit/test_docker.py pattern
@pytest.fixture
def mock_subprocess(monkeypatch):
    def fake_run(cmd, **kwargs):
        return CommandResult(command=cmd, return_code=0, stdout="", stderr="")
    monkeypatch.setattr('configurator.utils.command.subprocess.run', fake_run)
```

## Documentation Requirements

**Comprehensive Documentation Required:**

1. **Module Docstrings** (Google style):

```python
"""
Docker module for container development.

Handles:
- Docker Engine installation
- Docker Compose plugin
- Docker daemon configuration
- User permissions
"""
```

2. **Class Docstrings**:

```python
class ConfigurationModule(ABC):
    """
    Abstract base class for all configuration modules.

    Provides the interface that all modules must implement.
    """
```

3. **Method Docstrings** (include Args, Returns, Raises, Example):

```python
def install_packages_resilient(self, packages: List[str]) -> bool:
    """
    Install packages with network resilience.

    This method includes:
    - Circuit breaker protection
    - Automatic retry with exponential backoff
    - Proper timeout handling
    - Rollback registration

    Args:
        packages: List of package names to install

    Returns:
        True if all packages installed successfully

    Raises:
        ModuleExecutionError: If installation fails after retries

    Example:
        >>> self.install_packages_resilient(["docker-ce", "docker-compose"])
        True
    """
```

4. **Type Hints** (mandatory):

```python
def get(self, key: str, default: Any = None) -> Any:
    """Get config value using dot notation."""
```

## Testing Approach

### Unit Testing

**Structure** (from tests/unit/test_config.py):

```python
class TestConfigManager:
    """Tests for ConfigManager."""

    def test_default_values(self):
        """Test that default values are loaded correctly."""
        config = ConfigManager()
        assert config.get("system.hostname") == "dev-workstation"

    def test_invalid_profile(self):
        """Test that invalid profile raises error."""
        with pytest.raises(ConfigurationError):
            ConfigManager(profile="nonexistent")
```

**Naming Convention:**

- Test files: `test_*.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<what_it_tests>`

**Fixtures** (reusable):

```python
@pytest.fixture
def temp_config_file(tmp_path):
    config = tmp_path / "config.yaml"
    config.write_text("system:\n  hostname: test-server")
    return config
```

### Integration Testing

**Mark slow tests**:

```python
@pytest.mark.integration
@pytest.mark.slow
def test_docker_install_real(self):
    """Integration test - requires Debian system"""
    module = DockerModule(config=real_config)
    assert module.configure() == True
```

### End-to-End Testing

**Validation tests** (tests/validation/):

- Run on real Debian 13 system
- Verify actual package installation
- 400+ validation checks

## Python-Specific Guidelines

### Module Organization

**Import Order** (enforced by ruff):

```python
# 1. Standard library
import logging
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

# 2. Third-party
import click
from rich.console import Console

# 3. Local
from configurator.core.installer import Installer
from configurator.exceptions import ModuleExecutionError
```

**Relative Imports** (within package):

```python
# Use relative imports within same package
from .base import ConfigurationModule
from ..utils.command import run_command
```

### Type Hints

**Always use** (enforced by mypy):

```python
def configure(self) -> bool:
    """Return type required"""

def get(self, key: str, default: Any = None) -> Any:
    """Param types and return type required"""

def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
    """All params typed"""
```

### Error Handling

**Use Custom Exceptions** (from configurator/exceptions.py):

```python
raise ModuleExecutionError(
    what="Failed to install Docker",
    why="Package repository not available",
    how="1. Check network: ping deb.debian.org\n"
        "2. Check firewall: sudo ufw status\n"
        "3. Try again: vps-configurator install --module docker"
)
```

**Exception Hierarchy:**

```python
ConfiguratorError (base)
├── PrerequisiteError      # System not ready
├── ConfigurationError     # Invalid config
├── ModuleExecutionError   # Module failed
└── ValidationError        # Input invalid
```

### Async/Threading

**Use ThreadPoolExecutor** (NOT async/await):

```python
# Pattern from configurator/core/parallel.py
with ThreadPoolExecutor(max_workers=max_workers) as executor:
    futures = {executor.submit(self._execute_module, mod): mod for mod in batch}

    for future in as_completed(futures):
        module = futures[future]
        try:
            result = future.result(timeout=module_timeout)
        except Exception as e:
            # Handle error
```

**Thread Safety**:

```python
# Global lock for shared resources
_APT_LOCK = threading.Lock()

# Always use lock
with self._APT_LOCK:
    self.run("apt-get install ...")
```

### OOP Patterns

**Abstract Base Classes**:

```python
from abc import ABC, abstractmethod

class ConfigurationModule(ABC):
    @abstractmethod
    def validate(self) -> bool:
        """Subclasses MUST implement"""

    def install_packages(self, packages: List[str]):
        """Default implementation - can override"""
```

**Dataclasses** (for data structures):

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class User:
    username: str
    status: UserStatus
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        return {...}
```

**Composition over Inheritance**:

```python
class Installer:
    def __init__(self):
        # Compose services
        self.rollback_manager = RollbackManager()
        self.validator = SystemValidator()
        self.hooks_manager = HooksManager()
```

## Version Control Guidelines

**Semantic Versioning**:

- Major.Minor.Patch (e.g., 2.0.0)
- Breaking changes → Major bump
- New features → Minor bump
- Bug fixes → Patch bump

**Commit Messages** (conventional commits):

```
feat(docker): add custom registry support
fix(xrdp): correct audio configuration
docs(readme): add troubleshooting section
test(config): add profile validation tests
refactor(parallel): optimize batch scheduling
```

## Architecture-Specific Guidelines

### Module Development Pattern

**ALWAYS follow this template**:

```python
"""
<Module Name> module for <purpose>.

Handles:
- <Responsibility 1>
- <Responsibility 2>
- <Responsibility 3>
"""

from configurator.modules.base import ConfigurationModule

class <Name>Module(ConfigurationModule):
    """
    <One-line description>.

    <Detailed description if needed>.
    """

    name = "<Display Name>"
    description = "<Brief description>"
    depends_on = ["system", "security"]  # Dependencies
    priority = 50  # Execution order (10-90)
    mandatory = False  # Stop install on failure?

    def validate(self) -> bool:
        """Validate prerequisites."""
        # Check if already installed
        # Check disk space
        # Check dependencies
        return True

    def configure(self) -> bool:
        """Execute installation/configuration."""
        self.logger.info(f"Installing {self.name}...")

        # Step 1: Install packages
        self._install_packages()

        # Step 2: Configure
        self._configure_service()

        # Step 3: Start service
        self._start_service()

        self.logger.info(f"✓ {self.name} installed")
        return True

    def verify(self) -> bool:
        """Verify installation."""
        # Check service running
        # Check command available
        # Run test command
        return True

    # Helper methods (private)
    def _install_packages(self):
        """Install required packages."""
        self.install_packages_resilient(["package-name"])

    def _configure_service(self):
        """Configure the service."""
        # Write config files with rollback
        pass

    def _start_service(self):
        """Start and enable service."""
        self.enable_service("service-name")
```

### Core Component Pattern

**For orchestration components**:

```python
class ComponentName:
    """Brief description."""

    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize with dependencies."""
        self.logger = logger or logging.getLogger(__name__)

    def main_method(self) -> bool:
        """Public method with clear return."""
        try:
            self._validate()
            self._execute()
            return True
        except Exception as e:
            self.logger.error(f"Failed: {e}")
            return False

    def _validate(self):
        """Private validation."""
        pass

    def _execute(self):
        """Private execution."""
        pass
```

### Utility Function Pattern

**For utils/**:

```python
"""
Brief module description.

Functions:
- function1: Description
- function2: Description
"""

import logging

logger = logging.getLogger(__name__)

def utility_function(param: str, optional: int = 0) -> bool:
    """
    Brief description.

    Args:
        param: Description
        optional: Description with default

    Returns:
        Success status

    Raises:
        ValueError: If param invalid

    Example:
        >>> utility_function("test", 5)
        True
    """
    try:
        # Implementation
        return True
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
```

## General Best Practices

### Error Handling

**Always include beginner-friendly messages**:

```python
raise ModuleExecutionError(
    what="What happened (plain English)",
    why="Why it happened (explanation)",
    how="How to fix:\n1. Step 1\n2. Step 2\n3. Step 3"
)
```

### Logging

**Use appropriate levels**:

```python
self.logger.debug("Detailed diagnostic info")
self.logger.info("Normal operation messages")
self.logger.warning("Something unexpected but handled")
self.logger.error("Error occurred, operation failed")
```

**Structured logging** (when available):

```python
self.structured_logger.info(
    "module_started",
    extra={"module": "docker", "priority": 50}
)
```

### Command Execution

**NEVER use subprocess directly**:

```python
# ❌ WRONG
subprocess.run(["apt-get", "install", "docker-ce"])

# ✅ CORRECT
self.run("apt-get install docker-ce")
# Handles: dry-run, logging, rollback registration
```

### Rollback Registration

**ALWAYS register for state changes**:

```python
# After installing package
self.rollback_manager.add_package_remove(["docker-ce"])

# After starting service
self.rollback_manager.add_service_stop("docker")

# After creating file
self.rollback_manager.add_file_restore(backup_path, original_path)

# After running command
self.run("systemctl start docker",
         rollback_command="systemctl stop docker")
```

### Configuration Access

**Use dot notation**:

```python
# ✅ CORRECT
hostname = self.get_config("system.hostname", default="dev-workstation")
enabled = self.get_config("languages.python.enabled", default=True)

# ❌ WRONG
hostname = self.config["system"]["hostname"]  # KeyError if missing
```

## Project-Specific Guidance

### Critical Rules

1. **Module Isolation**: Modules CANNOT import other modules directly
2. **Layer Boundaries**: Core CANNOT import modules (circular dependency prevention)
3. **APT Lock**: ALL apt operations MUST use `with self._APT_LOCK:`
4. **Dry-Run Support**: ALL state-changing operations MUST check `if self.dry_run:`
5. **Rollback Registration**: ALL state changes MUST register rollback actions
6. **Error Messages**: ALL exceptions MUST use WHAT/WHY/HOW format

### Prohibited Patterns

**NEVER do these:**

```python
# ❌ Direct module imports
from configurator.modules.docker import DockerModule

# ❌ Direct subprocess
subprocess.run(["apt-get", "install", "package"])

# ❌ Bare exceptions
try:
    something()
except:  # Don't catch bare Exception
    pass

# ❌ String concatenation for commands
cmd = "apt-get install " + package_name  # Injection risk!

# ❌ Sync when should be parallel
for module in modules:
    module.configure()  # Should use ThreadPoolExecutor

# ❌ Missing type hints
def configure():  # Missing return type
    pass
```

### Encouraged Patterns

**ALWAYS do these:**

```python
# ✅ Dependency injection
module = container.get('docker_module')

# ✅ Use self.run()
self.run("apt-get install docker-ce")

# ✅ Specific exceptions
try:
    configure()
except ModuleExecutionError as e:
    logger.error(f"Configuration failed: {e}")

# ✅ Parameterized commands
packages = shlex.quote(" ".join(packages))
self.run(f"apt-get install {packages}")

# ✅ Parallel execution
with ThreadPoolExecutor() as executor:
    futures = [executor.submit(m.configure) for m in batch]

# ✅ Complete type hints
def configure(self) -> bool:
    pass
```

## When in Doubt

**Priority order for decisions:**

1. Check `exemplars.md` for gold-standard examples
2. Find similar code in the same layer
3. Consult `Project_Architecture_Blueprint.md`
4. Follow Python best practices (PEP 8, PEP 257)
5. Ask via GitHub Discussion

**Golden Rule**: Consistency with existing codebase > External best practices

---

**Last Updated:** January 16, 2026
**Version:** 2.0
**Applies to:** debian-vps-workstation v2.0+
