Sempurna!  Saya sudah menganalisis repository **yunaamelia/debian-vps-workstation**. Implementasi Anda sudah sangat baik dan mengikuti development prompt dengan tepat. Sekarang saya akan membuat **prompt penambahan fitur** yang dikategorikan berdasarkan prioritas.
# 🚀 ENHANCEMENT PROMPTS - PRIORITIZED

## ═══════════════════════════════════════════════════════════════════
## PRIORITY 1 (CRITICAL) - Core Functionality Gaps
## ═══════════════════════════════════════════════════════════════════

### **PROMPT 1.1: Implement Dependency Injection Container**

**File**: `configurator/core/container.py`

```markdown
# FEATURE:  Dependency Injection Container

## OBJECTIVE
Create a proper DI container to manage dependencies between modules and make testing easier.

## REQUIREMENTS

1. **Container Implementation**
   - Singleton services (logger, config, reporter)
   - Factory services (modules created on-demand)
   - Automatic dependency resolution
   - Lazy loading support

2. **Service Registration**
   ```python
   from configurator.core.container import Container

   container = Container()

   # Register singleton
   container.singleton('logger', lambda: setup_logger())
   container.singleton('config', lambda: ConfigManager())

   # Register factory
   container. factory('SystemModule', lambda c: SystemModule(
       config=c.get('config'),
       logger=c.get('logger')
   ))

   # Auto-wire dependencies
   module = container.make('SystemModule')
   ```

3. **Integration Points**
   - Update `Installer` to use container
   - Update all modules to support DI
   - Add container to CLI context

4. **Testing Benefits**
   - Easy mocking with container. mock('service', mock_object)
   - Clean test setup with test containers
   - Isolated unit tests

## IMPLEMENTATION STEPS

1. Create `configurator/core/container.py`
2. Implement Container class with:
   - `singleton(name, factory)`
   - `factory(name, factory)`
   - `get(name)`
   - `make(name)`
   - `has(name)`
   - `mock(name, instance)` for testing
3. Update `Installer.__init__` to use container
4. Create `tests/unit/test_container.py`

## ACCEPTANCE CRITERIA
- [ ] Container can register and resolve services
- [ ] Circular dependencies are detected
- [ ] Mock services for testing work
- [ ] All modules use DI (no hard-coded dependencies)
- [ ] Unit tests pass with 80%+ coverage

## FILES TO CREATE/MODIFY
- CREATE: `configurator/core/container.py`
- MODIFY: `configurator/core/installer.py`
- MODIFY: `configurator/modules/base.py`
- CREATE: `tests/unit/test_container.py`
```

---

### **PROMPT 1.2: Add Configuration Validation with Pydantic**

**File**: `configurator/config_schema.py`

```markdown
# FEATURE: Configuration Schema Validation with Pydantic

## OBJECTIVE
Add strict configuration validation using Pydantic to prevent runtime errors from invalid configs.

## REQUIREMENTS

1. **Schema Models**
   ```python
   from pydantic import BaseModel, Field, validator

   class FirewallConfig(BaseModel):
       enabled: bool = True
       allowed_ports: List[int] = Field(default=[22, 3389])
       ssh_rate_limit: bool = True

       @validator('allowed_ports')
       def validate_ports(cls, v):
           for port in v:
               if not (1 <= port <= 65535):
                   raise ValueError(f"Invalid port: {port}")
           return v

   class SecurityConfig(BaseModel):
       ufw:  FirewallConfig
       fail2ban:  Fail2banConfig
       ssh:  SSHConfig
       auto_updates: bool = True

   class AppConfig(BaseModel):
       profile:  Literal["beginner", "intermediate", "advanced"]
       system:  SystemConfig
       security: SecurityConfig
       # ... etc
   ```

2. **Validation Features**
   - Type checking (str, int, bool, List, Dict)
   - Range validation (Field(ge=1, le=100))
   - Custom validators (@validator decorator)
   - Cross-field validation (@root_validator)
   - Clear error messages with field paths

3. **Integration**
   - Update `ConfigManager.load()` to validate with Pydantic
   - Catch ValidationError and show user-friendly messages
   - Support environment variable overrides with Pydantic

4. **Error Reporting**
   ```python
   try:
       config = AppConfig(**raw_config)
   except ValidationError as e:
       for error in e.errors():
           location = " -> ".join(str(loc) for loc in error['loc'])
           print(f"  {location}: {error['msg']}")
   ```

## IMPLEMENTATION STEPS

1. Add pydantic to requirements. txt
2. Create `configurator/config_schema.py` with all config models
3. Update `ConfigManager.load()` to use Pydantic validation
4. Add comprehensive error messages
5. Create `tests/unit/test_config_schema.py`
6. Add example invalid configs to test error messages

## ACCEPTANCE CRITERIA
- [ ] All config fields have Pydantic models
- [ ] Invalid configs show clear error messages
- [ ] Port ranges, paths, and values are validated
- [ ] Profile consistency is enforced
- [ ] Unit tests cover all validators
- [ ] Documentation updated with schema

## FILES TO CREATE/MODIFY
- CREATE: `configurator/config_schema.py`
- MODIFY: `configurator/config.py` (integrate Pydantic)
- CREATE: `tests/unit/test_config_schema.py`
- CREATE: `tests/fixtures/invalid_configs/` (test cases)
```

---

### **PROMPT 1.3: Add Retry Logic with Exponential Backoff**

**File**: `configurator/utils/retry.py`

```markdown
# FEATURE: Retry Decorator with Exponential Backoff

## OBJECTIVE
Handle transient failures (network issues, apt locks) with intelligent retry logic.

## REQUIREMENTS

1. **Retry Decorator**
   ```python
   from configurator.utils.retry import retry_with_backoff

   @retry_with_backoff(
       max_attempts=3,
       base_delay=2. 0,
       max_delay=60.0,
       exceptions=(requests.RequestException, subprocess.CalledProcessError)
   )
   def download_file(url):
       response = requests.get(url, timeout=10)
       response.raise_for_status()
       return response.content
   ```

2. **Features**
   - Exponential backoff:  delay = base_delay * (2 ** attempt)
   - Maximum delay cap
   - Configurable exception types
   - Logging of retry attempts
   - Jitter to prevent thundering herd

3. **Use Cases**
   - Package installation (apt-get lock conflicts)
   - File downloads (network timeouts)
   - Service starts (systemd startup delays)
   - API calls (rate limiting)

4. **Integration Points**
   - Update `install_packages()` in base.py
   - Update `download_file()` in cursor.py
   - Update network operations

## IMPLEMENTATION STEPS

1. Create `configurator/utils/retry.py`
2. Implement `retry_with_backoff` decorator
3. Add jitter calculation
4. Update all network/package operations to use decorator
5. Create `tests/unit/test_retry.py`
6. Test with simulated failures

## ACCEPTANCE CRITERIA
- [ ] Decorator works with sync and async functions
- [ ] Exponential backoff with jitter implemented
- [ ] Logs show retry attempts
- [ ] Max attempts and delay respected
- [ ] Specific exceptions can be targeted
- [ ] Unit tests simulate failures and verify retries

## FILES TO CREATE/MODIFY
- CREATE: `configurator/utils/retry.py`
- MODIFY: `configurator/modules/base.py` (add to install_packages)
- MODIFY: `configurator/modules/cursor.py` (add to download)
- CREATE: `tests/unit/test_retry.py`
```

---

## ═══════════════════════════════════════════════════════════════════
## PRIORITY 2 (HIGH) - Security & Monitoring Enhancements
## ═══════════════════════════════════════════════════════════════════

### **PROMPT 2.1: Implement Secrets Manager**

**File**: `configurator/core/secrets.py`

```markdown
# FEATURE: Secure Secrets Management

## OBJECTIVE
Provide encrypted storage for sensitive data (passwords, API keys, certificates).

## REQUIREMENTS

1. **Encryption**
   - Use Fernet (symmetric encryption from cryptography library)
   - Derive key from master password using PBKDF2
   - Store encrypted secrets in JSON file
   - Secure file permissions (0600)

2. **API**
   ```python
   from configurator.core.secrets import SecretsManager

   secrets = SecretsManager()

   # Store
   secrets.store('db_password', 'my_secret_pass')
   secrets.store('api_key', 'sk-abc123')

   # Retrieve
   password = secrets.retrieve('db_password')

   # List all keys
   keys = secrets.list_keys()

   # Delete
   secrets.delete('old_key')
   ```

3. **Master Password**
   - Environment variable: `DVPS_MASTER_PASSWORD`
   - Auto-generate and save to `/root/.dvps_master_password` if not set
   - Never log or display master password

4. **Integration**
   - Use in RBAC module for user passwords
   - Use in database modules for connection strings
   - Use in VPN modules for keys
   - Document in security guide

## IMPLEMENTATION STEPS

1. Add cryptography to requirements.txt
2. Create `configurator/core/secrets.py`
3. Implement SecretsManager class
4. Add CLI command:  `vps-configurator secrets set/get/list/delete`
5. Update RBAC module to use secrets
6. Create `tests/unit/test_secrets.py`
7. Add to security documentation

## ACCEPTANCE CRITERIA
- [ ] Secrets are encrypted at rest
- [ ] Master password is never logged
- [ ] File permissions are secure (0600)
- [ ] CLI commands work
- [ ] RBAC module uses secrets for passwords
- [ ] Unit tests cover all operations
- [ ] Documentation includes examples

## FILES TO CREATE/MODIFY
- CREATE: `configurator/core/secrets.py`
- MODIFY: `configurator/cli. py` (add secrets commands)
- MODIFY: `configurator/modules/rbac.py` (use secrets)
- CREATE: `tests/unit/test_secrets.py`
- MODIFY: `docs/SECURITY.md` (document secrets)
```

---

### **PROMPT 2.2: Add Security Audit Logging**

**File**: `configurator/core/audit.py`

```markdown
# FEATURE: Immutable Security Audit Log

## OBJECTIVE
Log all security-relevant events for compliance and forensics.

## REQUIREMENTS

1. **Audit Event Types**
   ```python
   class AuditEventType(Enum):
       INSTALL_START = "install_start"
       INSTALL_COMPLETE = "install_complete"
       USER_CREATE = "user_create"
       USER_DELETE = "user_delete"
       PERMISSION_CHANGE = "permission_change"
       FIREWALL_RULE_ADD = "firewall_rule_add"
       FIREWALL_RULE_DELETE = "firewall_rule_delete"
       SSH_CONFIG_CHANGE = "ssh_config_change"
       PACKAGE_INSTALL = "package_install"
       SERVICE_START = "service_start"
       SERVICE_STOP = "service_stop"
       SECURITY_VIOLATION = "security_violation"
   ```

2. **Log Format (JSON Lines)**
   ```json
   {"timestamp":"2026-01-06T12:34:56Z","event_type":"user_create","user":"root","description":"Created user johndoe","details":{"username":"johndoe","role":"developer"},"success":true}
   ```

3. **Features**
   - Append-only log file (immutable)
   - Structured logging (JSON Lines format)
   - Query API for audit log analysis
   - Integration with all security modules

4. **API**
   ```python
   from configurator.core.audit import AuditLogger

   audit = AuditLogger()

   # Log event
   audit.log_event(
       AuditEventType.FIREWALL_RULE_ADD,
       "Added firewall rule for Docker",
       details={'port': 2376, 'protocol': 'tcp'}
   )

   # Query events
   violations = audit.query_events(
       event_type=AuditEventType.SECURITY_VIOLATION,
       start_time=datetime.now() - timedelta(days=7)
   )
   ```

## IMPLEMENTATION STEPS

1. Create `configurator/core/audit.py`
2. Implement AuditLogger class
3. Create `/var/log/debian-vps-configurator/audit.jsonl`
4. Add audit logging to all security modules
5. Add CLI command: `vps-configurator audit query`
6. Create `tests/unit/test_audit.py`
7. Document in SECURITY.md

## ACCEPTANCE CRITERIA
- [ ] All security events are logged
- [ ] Log file is append-only (600 permissions)
- [ ] JSON Lines format for easy parsing
- [ ] Query API works with filters
- [ ] CLI command can query audit log
- [ ] Unit tests verify logging
- [ ] Documentation includes examples

## FILES TO CREATE/MODIFY
- CREATE: `configurator/core/audit.py`
- MODIFY: `configurator/cli.py` (add audit command)
- MODIFY: `configurator/modules/security.py` (add audit logging)
- MODIFY: `configurator/modules/rbac.py` (add audit logging)
- CREATE: `tests/unit/test_audit.py`
- MODIFY: `docs/SECURITY.md`
```

---

### **PROMPT 2.3: Add File Integrity Monitoring**

**File**: `configurator/core/file_integrity.py`

```markdown
# FEATURE: File Integrity Monitoring (FIM)

## OBJECTIVE
Monitor critical system files for unauthorized changes (similar to AIDE/Tripwire).

## REQUIREMENTS

1. **Monitored Files**
   - `/etc/ssh/sshd_config`
   - `/etc/sudoers`
   - `/etc/passwd`, `/etc/shadow`, `/etc/group`
   - `/etc/xrdp/xrdp. ini`
   - `/etc/ufw/user.rules`
   - `/etc/fail2ban/jail.local`
   - User-configurable list

2. **Tracked Attributes**
   - SHA256 hash
   - File size
   - Modification time
   - Permissions (mode)
   - Owner (uid/gid)

3. **Operations**
   ```python
   from configurator.core.file_integrity import FileIntegrityMonitor

   fim = FileIntegrityMonitor()

   # Initialize baseline
   fim.initialize()

   # Check for changes
   violations = fim.check()

   # Update baseline after authorized change
   fim.update_baseline('/etc/ssh/sshd_config')
   ```

4. **Integration**
   - Run check on system startup (systemd service)
   - Run check via cron (daily)
   - Alert on violations (log + optional notification)
   - CLI command: `vps-configurator fim check/init/update`

## IMPLEMENTATION STEPS

1. Create `configurator/core/file_integrity.py`
2. Implement FileIntegrityMonitor class
3. Create database:  `/var/lib/debian-vps-configurator/file-integrity.json`
4. Add CLI commands for FIM
5. Create systemd service for daily checks
6. Create `tests/unit/test_file_integrity.py`
7. Document in SECURITY.md

## ACCEPTANCE CRITERIA
- [ ] Baseline database is created during install
- [ ] Daily checks detect changes
- [ ] Violations are logged to audit log
- [ ] CLI commands work
- [ ] Unit tests verify detection of changes
- [ ] Systemd service runs daily checks
- [ ] Documentation includes usage examples

## FILES TO CREATE/MODIFY
- CREATE: `configurator/core/file_integrity.py`
- MODIFY: `configurator/cli.py` (add fim commands)
- MODIFY: `configurator/modules/system.py` (initialize FIM)
- CREATE: `scripts/file-integrity-check.service` (systemd)
- CREATE: `tests/unit/test_file_integrity.py`
- MODIFY: `docs/SECURITY.md`
```

---

## ═══════════════════════════════════════════════════════════════════
## PRIORITY 3 (MEDIUM) - User Experience & CLI Enhancements
## ═══════════════════════════════════════════════════════════════════

### **PROMPT 3.1: Add Interactive Wizard Mode**

**File**: `configurator/wizard.py`

```markdown
# FEATURE: Full Interactive Wizard with TUI

## OBJECTIVE
Create beginner-friendly interactive wizard with beautiful TUI (Terminal User Interface).

## REQUIREMENTS

1. **Wizard Flow**
   - Welcome screen with animated banner
   - Profile selection (beginner/intermediate/advanced)
   - Progressive disclosure (only show relevant questions)
   - Configuration preview before installation
   - Progress indication during install
   - Summary screen with next steps

2. **TUI Library**
   - Use `textual` library for rich TUI
   - Form inputs, checkboxes, radio buttons
   - Real-time validation
   - Keyboard shortcuts
   - Mouse support

3. **Screens**
   ```python
   from textual.app import App
   from textual.widgets import Header, Footer, Button, Input

   class WizardApp(App):
       async def on_mount(self):
           await self.view.dock(Header(), edge="top")
           await self.view.dock(Footer(), edge="bottom")
           await self.show_welcome_screen()

       async def show_welcome_screen(self):
           # Animated welcome

       async def show_profile_selection(self):
           # Profile selection

       async def show_configuration(self, profile):
           # Configuration questions

       async def show_preview(self, config):
           # Preview before install

       async def run_installation(self, config):
           # Progress screen during install

       async def show_summary(self, results):
           # Summary and next steps
   ```

4. **Integration**
   - Update CLI:  `vps-configurator wizard`
   - Default mode if no arguments provided
   - Save configuration for review
   - Option to resume interrupted installation

## IMPLEMENTATION STEPS

1. Add textual to requirements.txt
2. Create `configurator/wizard.py` with WizardApp
3. Create screens for each step
4. Add real-time configuration validation
5. Update CLI to launch wizard
6. Create `tests/unit/test_wizard.py`
7. Add screenshots to documentation

## ACCEPTANCE CRITERIA
- [ ] Wizard is beautiful and intuitive
- [ ] Beginner profile has <5 questions
- [ ] Advanced profile shows all options
- [ ] Configuration is validated in real-time
- [ ] Preview screen shows what will be installed
- [ ] Progress updates during installation
- [ ] Summary shows connection info
- [ ] Can save/load wizard configuration
- [ ] Tests verify wizard flow
- [ ] Documentation has screenshots

## FILES TO CREATE/MODIFY
- CREATE: `configurator/wizard.py`
- CREATE: `configurator/wizard/` (screens directory)
- MODIFY: `configurator/cli.py` (add wizard command)
- CREATE: `tests/unit/test_wizard.py`
- MODIFY: `docs/quickstart/wizard-guide.md`
```

---

### **PROMPT 3.2: Add Dry-Run Mode with Diff Preview**

**File**: `configurator/core/dryrun.py`

```markdown
# FEATURE: Comprehensive Dry-Run Mode

## OBJECTIVE
Show exactly what would change without making actual changes.

## REQUIREMENTS

1. **Dry-Run Manager**
   ```python
   from configurator.core.dryrun import DryRunManager

   dryrun = DryRunManager()

   # Record planned changes
   dryrun.record_package_install(['docker-ce', 'docker-compose'])
   dryrun.record_file_write('/etc/docker/daemon.json', content)
   dryrun.record_service_start('docker')
   dryrun.record_firewall_rule('allow 2376/tcp')

   # Generate report
   report = dryrun.generate_report()
   ```

2. **Change Types**
   - Packages to install
   - Files to create/modify
   - Services to start/enable
   - Firewall rules to add
   - Users to create
   - Commands to execute

3. **Report Format**
   ```
   DRY-RUN REPORT
   ══════════════════════════════════════════════════════

   PACKAGES TO INSTALL (12):
     + docker-ce (24.0.7)
     + docker-ce-cli (24.0.7)
     + containerd.io (1.6.26)
     ...

   FILES TO CREATE/MODIFY (5):
     CREATE /etc/docker/daemon.json (234 bytes)
       {
         "log-driver": "json-file",
         ...
       }

     MODIFY /etc/ssh/sshd_config
       - PermitRootLogin yes
       + PermitRootLogin no

   SERVICES TO START (3):
     + docker.service (enabled)
     + fail2ban.service (enabled)
     + xrdp.service (enabled)

   FIREWALL RULES TO ADD (2):
     + ufw allow 3389/tcp (xrdp)
     + ufw allow 2376/tcp (docker)

   ESTIMATED TIME:  30 minutes
   ESTIMATED DISK USAGE: 2.3 GB
   ══════════════════════════════════════════════════════

   No changes will be made in dry-run mode.
   To apply these changes, run without --dry-run flag.
   ```

4. **Integration**
   - CLI flag: `--dry-run`
   - Pass DryRunManager to all modules
   - Modules check `if self.dry_run: dryrun.record() else: execute()`
   - Generate report at end

## IMPLEMENTATION STEPS

1. Create `configurator/core/dryrun.py`
2. Implement DryRunManager class
3. Update base. py to support dry-run
4. Update all modules to use dry-run
5. Create beautiful report formatter
6. Create `tests/unit/test_dryrun.py`
7. Update documentation

## ACCEPTANCE CRITERIA
- [ ] All changes are recorded in dry-run mode
- [ ] No actual changes are made
- [ ] Report shows all planned changes
- [ ] File diffs are shown
- [ ] Estimated time and disk usage shown
- [ ] Can save report to file
- [ ] Unit tests verify no changes made
- [ ] Documentation updated

## FILES TO CREATE/MODIFY
- CREATE: `configurator/core/dryrun.py`
- MODIFY: `configurator/modules/base.py` (add dry_run support)
- MODIFY: `configurator/core/installer.py` (integrate dry-run)
- MODIFY: All modules (check dry_run flag)
- CREATE: `tests/unit/test_dryrun. py`
- MODIFY: `docs/CLI-REFERENCE.md`
```
