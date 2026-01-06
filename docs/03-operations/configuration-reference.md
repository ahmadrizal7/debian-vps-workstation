# CONFIGURATION REFERENCE

**Debian VPS Configurator - Complete Configuration Guide**
**All Configuration Options Explained with Examples**
**Date:** January 6, 2026

---

## 🎯 OVERVIEW

This reference guide documents **every configuration option** available in Debian VPS Configurator with detailed explanations, valid values, defaults, and examples.

**Configuration File Location:**

- Primary: `/etc/debian-vps-configurator/config.yaml`
- Environment: `/opt/vps-configurator/.env`
- User overrides: `~/.vps-configurator/config.yaml`

**Configuration Priority (highest to lowest):**

1. Command-line arguments (`--option value`)
2. Environment variables (`VPS_CONFIG_OPTION=value`)
3. User config (`~/.vps-configurator/config.yaml`)
4. System config (`/etc/debian-vps-configurator/config.yaml`)
5. Built-in defaults

---

## 📋 TABLE OF CONTENTS

1. [General Settings](#general-settings)
2. [Logging Configuration](#logging-configuration)
3. [Performance Settings](#performance-settings)
4. [CIS Benchmark Scanner](#cis-benchmark)
5. [Vulnerability Scanner](#vulnerability-scanner)
6. [SSL/TLS Certificates](#ssl-certificates)
7. [SSH Key Management](#ssh-keys)
8. [MFA/2FA Settings](#mfa-settings)
9. [RBAC Settings](#rbac-settings)
10. [User Lifecycle](#user-lifecycle)
11. [Activity Monitoring](#activity-monitoring)
12. [Team Management](#team-management)
13. [Temporary Access](#temporary-access)
14. [Backup Settings](#backup-settings)
15. [Notifications](#notifications)

---

## 🔧 CORE CONFIGURATION

### General Settings

**Section:** `general`

```yaml
general:
  # Environment type
  # Valid values: development, staging, production
  # Default: production
  # Impact: Affects safety checks, logging verbosity, error handling
  environment: production

  # Server hostname
  # Valid values: Any valid hostname/FQDN
  # Default: System hostname
  # Impact: Used in emails, reports, certificates
  hostname: vps.company.com

  # Administrator email
  # Valid values: Valid email address
  # Default: root@localhost
  # Impact: Receives critical alerts, certificate notifications
  admin_email: admin@company.com

  # Timezone for scheduled tasks
  # Valid values: Any valid TZ database name
  # Default: System timezone
  # Impact: Affects cron jobs, log timestamps, reports
  # Examples: America/New_York, Europe/London, Asia/Tokyo
  timezone: UTC

  # Enable verbose output
  # Valid values: true, false
  # Default: false
  # Impact: More detailed CLI output
  verbose: false

  # Enable colored output
  # Valid values: true, false
  # Default: true
  # Impact: Terminal output colors
  color_output: true

  # Default language
  # Valid values: en, es, fr, de, ja (if translations available)
  # Default: en
  # Impact: CLI messages, reports, emails
  language: en
```

**Example - Development Configuration:**

```yaml
general:
  environment: development
  hostname: dev.local
  admin_email: dev-team@company.com
  timezone: America/Los_Angeles
  verbose: true
  color_output: true
```

**Example - Production Configuration:**

```yaml
general:
  environment: production
  hostname: vps.company.com
  admin_email: ops@company.com
  timezone: UTC
  verbose: false
  color_output: false # For automated scripts
```

---

### Logging Configuration

**Section:** `logging`

```yaml
logging:
  # Log level
  # Valid values: DEBUG, INFO, WARNING, ERROR, CRITICAL
  # Default: INFO
  # Impact: Amount of detail in logs
  # Recommendations:
  #   - DEBUG: Development/troubleshooting only (very verbose)
  #   - INFO: Production (balanced detail)
  #   - WARNING: Production (minimal logging)
  #   - ERROR: Only log errors
  level: INFO

  # Main log file path
  # Valid values: Absolute file path
  # Default: /var/log/vps-configurator/main.log
  # Impact: Where logs are written
  file: /var/log/vps-configurator/main.log

  # Maximum log file size in MB
  # Valid values: Integer > 0
  # Default: 100
  # Impact: When log rotation triggers
  max_size_mb: 100

  # Number of backup log files to keep
  # Valid values: Integer >= 0
  # Default: 10
  # Impact: Disk space used by logs
  backup_count: 10

  # Log format string
  # Valid values: Python logging format string
  # Default: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  # Variables: %(asctime)s, %(name)s, %(levelname)s, %(message)s,
  #            %(filename)s, %(lineno)d, %(funcName)s
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

  # Date format for timestamps
  # Valid values: Python strftime format
  # Default: "%Y-%m-%d %H:%M:%S"
  date_format: "%Y-%m-%d %H:%M:%S"

  # Enable console logging (in addition to file)
  # Valid values: true, false
  # Default: true
  # Impact: Whether logs appear in terminal
  console_output: true

  # Console log level (can differ from file)
  # Valid values: DEBUG, INFO, WARNING, ERROR, CRITICAL
  # Default: Same as 'level'
  # Impact: Console verbosity
  console_level: WARNING

  # Enable structured logging (JSON format)
  # Valid values: true, false
  # Default: false
  # Impact: Log parsing, integration with log aggregators
  structured: false

  # Separate log files for different components
  # Valid values: true, false
  # Default: false
  # Impact: Creates security.log, audit.log, etc.
  separate_files: true

  # Specific log files when separate_files is true
  security_log: /var/log/vps-configurator/security.log
  audit_log: /var/log/vps-configurator/audit.log
  backup_log: /var/log/vps-configurator/backup.log

  # Log sensitive data (passwords, keys)
  # Valid values: true, false
  # Default: false
  # SECURITY WARNING: Never enable in production!
  log_sensitive_data: false
```

**Example - Development Logging:**

```yaml
logging:
  level: DEBUG
  console_output: true
  console_level: DEBUG
  format: "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s"
  structured: false
```

**Example - Production Logging:**

```yaml
logging:
  level: INFO
  file: /var/log/vps-configurator/main.log
  max_size_mb: 100
  backup_count: 30
  console_output: false
  structured: true # For log aggregators like ELK
  separate_files: true
  log_sensitive_data: false
```

---

### Performance Settings

**Section:** `performance`

```yaml
performance:
  # Parallel execution settings
  parallel_execution:
    # Enable parallel task execution
    # Valid values: true, false
    # Default: true
    # Impact: Significant performance boost
    enabled: true

    # Maximum worker threads/processes
    # Valid values: 1-16 (depends on CPU cores)
    # Default: 4
    # Impact: CPU usage, memory usage, speed
    # Recommendation: Set to number of CPU cores
    max_workers: 4

    # Worker type
    # Valid values: thread, process
    # Default: thread
    # Impact:
    #   - thread: Lower overhead, shared memory
    #   - process: Better for CPU-intensive tasks
    worker_type: thread

    # Task timeout in seconds
    # Valid values: Integer > 0
    # Default: 300 (5 minutes)
    # Impact: When tasks are killed
    task_timeout: 300

  # Caching settings
  cache:
    # Enable caching
    # Valid values: true, false
    # Default: true
    # Impact: Speed vs memory usage
    enabled: true

    # Cache directory
    # Valid values: Absolute directory path
    # Default: /var/cache/vps-configurator
    cache_directory: /var/cache/vps-configurator

    # Maximum cache size in GB
    # Valid values: Integer > 0
    # Default: 10
    # Impact: Disk space usage
    max_size_gb: 10

    # Cache TTL (time-to-live) in seconds
    # Valid values: Integer > 0
    # Default: 3600 (1 hour)
    # Impact: Cache freshness vs hit rate
    ttl_seconds: 3600

    # Cache packages
    # Valid values: true, false
    # Default: true
    # Impact: Bandwidth savings
    cache_packages: true

    # Cache scan results
    # Valid values: true, false
    # Default: true
    # Impact: Scan speed on repeated runs
    cache_scan_results: true

  # Lazy loading settings
  lazy_loading:
    # Enable lazy loading of modules
    # Valid values: true, false
    # Default: true
    # Impact: Startup time, memory usage
    enabled: true

    # Modules to preload (skip lazy loading)
    # Valid values: List of module names
    # Default: []
    # Impact: Startup time vs first-use latency
    preload_modules:
      - core
      - rbac

  # Circuit breaker settings
  circuit_breaker:
    # Enable circuit breaker pattern
    # Valid values: true, false
    # Default: true
    # Impact: Resilience to failures
    enabled: true

    # Failure threshold before opening circuit
    # Valid values: Integer > 0
    # Default: 5
    # Impact: Sensitivity to failures
    failure_threshold: 5

    # Success threshold to close circuit
    # Valid values: Integer > 0
    # Default: 2
    # Impact: Recovery speed
    success_threshold: 2

    # Timeout before trying half-open (seconds)
    # Valid values: Integer > 0
    # Default: 60
    # Impact: Recovery attempt frequency
    timeout: 60

  # Database connection pool
  database_pool:
    # Minimum connections
    # Valid values: Integer >= 0
    # Default: 1
    min_size: 1

    # Maximum connections
    # Valid values: Integer > 0
    # Default: 10
    # Impact: Concurrent database access
    max_size: 10

    # Connection timeout (seconds)
    # Valid values: Integer > 0
    # Default: 30
    timeout: 30
```

---

## 🔒 SECURITY CONFIGURATION

### CIS Benchmark Scanner

**Section:** `security.cis_benchmark`

```yaml
security:
  cis_benchmark:
    # Enable CIS benchmark scanning
    # Valid values: true, false
    # Default: true
    enabled: true

    # CIS benchmark profile
    # Valid values: level1-server, level2-server, level1-workstation
    # Default: level1-server
    # Impact: Number and strictness of checks
    # Recommendations:
    #   - level1-server: Basic hardening (recommended for most)
    #   - level2-server: Stricter (may impact functionality)
    profile: level1-server

    # Auto-remediation mode
    # Valid values: true, false
    # Default: false
    # CAUTION: Review changes before enabling
    auto_remediate: false

    # Require approval for remediation
    # Valid values: true, false
    # Default: true
    # Impact: Manual review vs automation
    require_approval: true

    # Scan schedule (cron format)
    # Valid values: Valid cron expression or empty string
    # Default: "0 2 * * 0" (Sunday 2 AM)
    # Impact: Automated scanning frequency
    scan_schedule: "0 2 * * 0"

    # Scan timeout (seconds)
    # Valid values: Integer > 0
    # Default: 1800 (30 minutes)
    scan_timeout: 1800

    # Excluded checks (by check ID)
    # Valid values: List of check IDs
    # Default: []
    # Impact: Skip specific checks
    # Use when a check is not applicable
    excluded_checks:
      - "1.1.1.1" # Example: cramfs check
      - "5.2.8" # Example: SSH root login (if needed)

    # Compliance threshold (percentage)
    # Valid values: 0-100
    # Default: 90
    # Impact: When to alert/fail
    compliance_threshold: 90

    # Generate report after scan
    # Valid values: true, false
    # Default: true
    generate_report: true

    # Report format
    # Valid values: pdf, html, json, text
    # Default: pdf
    report_format: pdf

    # Report destination
    # Valid values: Absolute file path
    # Default: /var/reports/cis-scan-{date}.pdf
    report_path: /var/reports/cis-scan-{date}.pdf

    # Email report
    # Valid values: true, false
    # Default: false
    email_report: true

    # Alert on failed checks
    # Valid values: true, false
    # Default: true
    alert_on_failure: true
```

---

### Vulnerability Scanner

**Section:** `security.vulnerability_scanner`

```yaml
security:
  vulnerability_scanner:
    # Enable vulnerability scanning
    # Valid values: true, false
    # Default: true
    enabled: true

    # CVE database source
    # Valid values: nvd, debian, ubuntu, custom
    # Default: nvd
    # Impact: CVE coverage and accuracy
    database_source: nvd

    # Auto-update CVE database
    # Valid values: true, false
    # Default: true
    # Impact: Database freshness
    auto_update_db: true

    # Database update schedule
    db_update_schedule: "0 4 * * *"

    # Scan schedule
    scan_schedule: "0 3 * * *"

    # Scan timeout (seconds)
    scan_timeout: 3600

    # Scan types
    scan_types:
      packages: true
      ports: true
      exploits: false

    # Severity levels to report
    severity_levels:
      - critical
      - high
      - medium

    # Alert thresholds
    alert_thresholds:
      critical: 1
      high: 5
      medium: 20

    # Auto-patch mode
    # Valid values: none, security-only, all
    # Default: none
    auto_patch: none

    # Require reboot after patching
    # Valid values: prompt, auto, never
    # Default: prompt
    reboot_policy: prompt

    # Generate vulnerability report
    generate_report: true

    # Report format
    report_format: pdf
```

---

### SSL/TLS Certificates

**Section:** `security.ssl_certificates`

```yaml
security:
  ssl_certificates:
    enabled: true
    provider: letsencrypt

    letsencrypt:
      email: admin@company.com
      server: production
      challenge_type: http-01
      key_type: ecdsa256

    auto_renew:
      enabled: true
      renew_days_before: 30
      check_schedule: "0 0 * * *"
      reload_services:
        - nginx
        - apache2

    monitoring:
      alert_expiry_days: 14
      check_frequency_hours: 24

    ocsp_stapling: true

    cert_directory: /etc/letsencrypt/live
    archive_directory: /etc/letsencrypt/archive
```

---

### SSH Key Management

**Section:** `security.ssh_keys`

```yaml
security:
  ssh_keys:
    enabled: true
    default_key_type: ed25519
    rsa_key_size: 4096

    rotation:
      enabled: true
      rotation_days: 90
      grace_period_days: 7
      check_schedule: "0 6 * * 1"
      notify_users: true
      notify_days_before: 7

    validation:
      reject_weak_keys: true
      min_key_strength: 2048
      reject_weak_algorithms: true
      blacklisted_algorithms:
        - dsa
        - rsa1024

    deployment:
      auto_deploy: true
      file_permissions: "0600"
      directory_permissions: "0700"

    audit:
      log_operations: true
      audit_log: /var/log/vps-configurator/ssh-keys.log
```

---

### MFA/2FA Settings

**Section:** `security.mfa`

```yaml
security:
  mfa:
    enabled: true

    # MFA enforcement policy
    # Valid values: optional, required, role-based
    # Default: required
    enforcement: required

    required_roles:
      - admin
      - devops

    totp:
      period: 30
      digits: 6
      algorithm: SHA1
      drift_tolerance: 1

    backup_codes:
      enabled: true
      count: 10
      length: 8

    lockout:
      enabled: true
      max_attempts: 5
      lockout_duration: 30
      auto_unlock: true

    qr_code:
      qr_size: 300
      error_correction: M

    audit:
      log_operations: true
      log_failed_attempts: true
      alert_on_failures: true
```

---

## 👥 USER MANAGEMENT CONFIGURATION

### RBAC Settings

**Section:** `rbac`

```yaml
rbac:
  enabled: true

  # Default deny policy (whitelist approach)
  default_deny: true

  roles_file: /etc/debian-vps-configurator/rbac/roles.yaml
  permission_format: scope:resource:action
  role_inheritance: false

  audit_checks: true

  cache_checks: true
  cache_ttl: 300

  sudo:
    enabled: true
    validate_before_apply: true
    sudoers_directory: /etc/sudoers.d
    audit_enabled: true
    audit_log: /var/log/sudo-audit.log
```

---

### User Lifecycle

**Section:** `users.lifecycle`

```yaml
users:
  lifecycle:
    enabled: true

    provisioning:
      auto_generate_ssh_key: true
      auto_enroll_2fa: false
      welcome_email: true
      welcome_email_template: /etc/debian-vps-configurator/templates/welcome.txt
      require_password_change: true
      default_shell: /bin/bash
      home_directory_template: /etc/skel

    offboarding:
      archive_data: true
      archive_directory: /var/backups/users
      compress_archives: true
      archive_retention_days: 2555
      delete_immediately: false
      grace_period_days: 30
      send_report: true
      notify_user: true

    audit:
      log_all_events: true
      audit_log: /var/log/user-lifecycle-audit.log
```

---

### Activity Monitoring

**Section:** `users.activity_monitoring`

```yaml
users:
  activity_monitoring:
    enabled: true
    database: /var/lib/debian-vps-configurator/activity/activity.db
    retention_days: 2555

    tracking:
      ssh_sessions: true
      command_execution: true
      file_access: true
      sudo_commands: true
      permission_changes: true
      failed_auth: true

    anomaly_detection:
      enabled: true
      baseline_days: 30
      alert_threshold: 70

      anomaly_types:
        unusual_time: true
        new_location: true
        unusual_commands: true
        bulk_downloads: true
        permission_escalation: true
        failed_auth_spike: true

      auto_response:
        enabled: false
        actions:
          high: alert
          critical: suspend

    reporting:
      enabled: true
      schedule: "0 7 * * 0"
      format: pdf
      email_reports: true
```

---

### Team Management

**Section:** `users.teams`

```yaml
users:
  teams:
    enabled: true
    shared_directories: /var/projects
    default_permissions: "2775"

    default_quotas:
      disk_gb: 50
      docker_containers: 10
      max_files: null

    team_permissions:
      inherit_from_roles: true
      allow_team_specific: true

    lifecycle:
      auto_setup_directory: true
      initialize_templates: true
      template_directory: /etc/debian-vps-configurator/templates/team
      notify_on_changes: true

    audit:
      log_operations: true
      audit_log: /var/log/team-audit.log
```

---

### Temporary Access

**Section:** `users.temp_access`

```yaml
users:
  temp_access:
    enabled: true
    default_duration_days: 30
    max_duration_days: 90
    default_reminder_days: 7

    extensions:
      enabled: true
      require_approval: true
      max_extensions: 2
      max_extension_days: 30

    expiration:
      enabled: true
      check_schedule: "0 5 * * *"
      grace_period_hours: 0
      auto_revoke: true
      archive_expired: true

    reminders:
      enabled: true
      reminder_days: [7, 3, 1]
      methods:
        - email

    emergency:
      enabled: true
      max_duration_hours: 4
      require_incident_id: true
      enhanced_logging: true
      require_review: true

    audit:
      log_operations: true
      audit_log: /var/log/temp-access-audit.log
```

---

## 🔗 INTEGRATION CONFIGURATION

### Backup Settings

**Section:** `backup`

```yaml
backup:
  enabled: true
  directory: /opt/vps-configurator/backups
  schedule: "0 1 * * *"

  retention:
    daily: 7
    weekly: 4
    monthly: 12

  compress: true
  compression_level: 6

  encryption:
    enabled: false
    method: gpg
    gpg_recipient: backup@company.com

  include:
    - /etc/debian-vps-configurator
    - /var/lib/debian-vps-configurator
    - /var/log/vps-configurator

  exclude:
    - "*.tmp"
    - "*.cache"

  remote:
    enabled: false
    type: s3
    s3:
      bucket: my-backups
      region: us-east-1
    auto_upload: true
    keep_local: true

  notifications:
    on_success: false
    on_failure: true
```

---

### Notifications

**Section:** `notifications`

```yaml
notifications:
  email:
    enabled: true
    smtp_host: smtp.gmail.com
    smtp_port: 587
    smtp_security: starttls
    smtp_user: alerts@company.com
    from_address: vps-configurator@company.com
    reply_to: admin@company.com

    recipients:
      admin: admin@company.com
      security: security@company.com
      alerts: alerts@company.com

  slack:
    enabled: false
    webhook_url: "https://hooks.slack.com/services/..."
    channel: "#alerts"
    username: "VPS Configurator"
    notify_on:
      - critical
      - error

  discord:
    enabled: false
    webhook_url: "https://discord.com/api/webhooks/..."
    username: "VPS Bot"

  webhook:
    enabled: false
    url: "https://monitoring.company.com/api/alert"
    method: "POST"
    headers:
      Authorization: "Bearer token"
```

---

### Database Configuration

**Section:** `database`

```yaml
database:
  # Database type
  # Valid values: sqlite, postgresql
  # Default: sqlite
  type: sqlite

  sqlite:
    path: /var/lib/debian-vps-configurator/main.db
    journal_mode: WAL
    backup_on_startup: true

  postgresql:
    host: localhost
    port: 5432
    database: vps_config
    user: vps_admin
    # Password should be set via DB_PASSWORD env var
    ssl_mode: require
    connection_pool_size: 5

  migrations:
    auto_migrate: true
    backup_before_migrate: true
    migration_table: schema_migrations
```

---

### Maintenance Settings

**Section:** `maintenance`

```yaml
maintenance:
  enabled: true

  # Maintenance windows
  windows:
    # Daily low-traffic window
    daily:
      enabled: true
      start_time: "03:00"
      duration_minutes: 60
      tasks:
        - log_rotation
        - db_backup
        - temp_file_cleanup

    # Weekly deep maintenance
    weekly:
      enabled: true
      day_of_week: "Sunday"
      start_time: "04:00"
      duration_minutes: 120
      tasks:
        - full_scan
        - package_updates
        - cert_renewal

  # Reboot behavior
  reboot:
    allowed_in_window: true
    notify_before_reboot: true
    notification_lead_time_minutes: 15
    require_confirmation: false # Auto-reboot during window
```

---

## 🔧 ENVIRONMENT VARIABLES REFERENCE

`environment_variables`

These variables override settings in `config.yaml` and provide secrets.

### Core Overrides

| Variable          | Config Option         | Description                 |
| ----------------- | --------------------- | --------------------------- |
| `VPS_ENV`         | `general.environment` | Environment type (dev/prod) |
| `VPS_HOSTNAME`    | `general.hostname`    | Server hostname             |
| `VPS_LOG_LEVEL`   | `logging.level`       | Log verbosity               |
| `VPS_ADMIN_EMAIL` | `general.admin_email` | Admin email address         |

### Secrets (Do not set in config.yaml)

| Variable                | Description                               |
| ----------------------- | ----------------------------------------- |
| `SMTP_PASSWORD`         | Password for SMTP email sending           |
| `DB_PASSWORD`           | PostgreSQL password                       |
| `AWS_ACCESS_KEY_ID`     | S3 Access Key for backups                 |
| `AWS_SECRET_ACCESS_KEY` | S3 Secret Key for backups                 |
| `SLACK_WEBHOOK_URL`     | Override Slack webhook URL                |
| `DISCORD_WEBHOOK_URL`   | Override Discord webhook URL              |
| `ENCRYPTION_KEY`        | Master key for encrypting secrets at rest |

### Feature Toggles

| Variable                    | Description                         |
| --------------------------- | ----------------------------------- |
| `VPS_DISABLE_SECURITY_SCAN` | Set to "true" to skip boot scans    |
| `VPS_DISABLE_AUTO_UPDATE`   | Set to "true" to block auto-updates |
| `VPS_FORCE_COLOR`           | Force ANSI color output ("true")    |
| `VPS_NO_COLOR`              | Disable ANSI color output ("true")  |

---

**END OF CONFIGURATION REFERENCE**

🔧 **Use this reference to fine-tune your installation!**
