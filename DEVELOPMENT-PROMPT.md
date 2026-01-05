# 🚀 COMPLETE DEVELOPMENT PROMPT - DEBIAN 13 VPS CONFIGURATOR

````markdown
# ═══════════════════════════════════════════════════════════════════

# DEBIAN 13 VPS REMOTE DESKTOP CODING WORKSTATION CONFIGURATOR

# COMPREHENSIVE DEVELOPMENT PROMPT - PRODUCTION READY

# ═══════════════════════════════════════════════════════════════════

## PROJECT OVERVIEW

You are tasked with developing a **production-ready, beginner-friendly** automated
configuration system for fresh Debian 13 (Trixie) VPS servers that transforms them
into fully-featured remote desktop coding workstations.

**Project Name:** Debian VPS Workstation Configurator
**Target Users:** Beginner to Advanced Linux users (Primary: Beginners)
**Budget Constraint:** 100% Free/Open Source Tools Only
**Timeline:** 4 weeks (MVP in 2 weeks)
**License:** MIT License

## ═══════════════════════════════════════════════════════════════════

## SECTION 1: CORE REQUIREMENTS & CONSTRAINTS

## ═══════════════════════════════════════════════════════════════════

### 1.1 USER PROFILE (CRITICAL)

**Primary User:**

- Linux Experience: BEGINNER (just learning)
- Use Case: Personal staging environment (production-like)
- Scale: 1-3 servers (DigitalOcean)
- Access Level: Root/sudo access available
- Target Audience: Public (various skill levels)

**CRITICAL DESIGN PRINCIPLE:**

> "Make it simple by default, powerful for those who need it"
> NEVER sacrifice security for simplicity
> ALWAYS provide clear, actionable error messages

### 1.2 HARDWARE SPECIFICATIONS

**Target Server:**

- CPU: 4 vCPU (minimum 2 vCPU)
- RAM: 8GB (minimum 4GB)
- Disk: 100GB SSD (minimum 40GB)
- Network: Minimum 10 Mbps
- Platform: DigitalOcean (primary), portable to other providers

**Resource Philosophy:**

- Balanced performance and efficiency
- Installation time: Not critical (quality over speed)
- Target install time: < 2 hours for full stack

### 1.3 OPERATING SYSTEM

**Base System:**

- OS: Debian 13 (Trixie) ONLY
- Architecture: x86_64/amd64 (primary), arm64 (documented)
- Init System: systemd (mandatory)
- Package Manager: APT

**Validation Requirements:**

```bash
# Pre-flight checks MUST verify:
- Debian version == 13 (Trixie)
- Architecture == x86_64
- systemd is running
- Internet connectivity
- Root/sudo access
- Sufficient disk space (>20GB free)
- Sufficient RAM (>2GB)
```
````

### 1.4 BUDGET CONSTRAINTS

**MANDATORY: 100% FREE/OPEN SOURCE TOOLS**

❌ FORBIDDEN:

- Paid software licenses
- Cloud services requiring payment
- Enterprise-only features
- Trial-based tools

✅ ALLOWED:

- Open source tools (MIT, Apache, GPL, BSD)
- Free tier cloud services (documented as optional)
- Community editions
- Self-hosted alternatives

## ═══════════════════════════════════════════════════════════════════

## SECTION 2: TECHNICAL ARCHITECTURE

## ═══════════════════════════════════════════════════════════════════

### 2.1 LANGUAGE & FRAMEWORK

**Primary Language:** Python 3.11+ (Debian 13 default)

**Why Python:**

- Beginner-readable code
- Excellent for system automation
- Rich library ecosystem for SSH, config parsing, etc.
- Easy to debug
- Cross-platform (future Windows support possible)

**Required Python Libraries:**

```python
# requirements.txt
pyyaml>=6.0              # Configuration parsing
click>=8.1. 0             # CLI framework
rich>=13.0.0             # Beautiful terminal output
requests>=2.31.0         # HTTP client
paramiko>=3.3.0          # SSH operations
jinja2>=3.1.0            # Template rendering
pytest>=7.4.0            # Testing
pytest-cov>=4.1.0        # Code coverage
black>=23.0.0            # Code formatting
pylint>=3.0.0            # Linting
mypy>=1.5.0              # Type checking
```

### 2.2 PROJECT STRUCTURE

```
debian-vps-configurator/
├── README.md                           # Quick start guide
├── LICENSE                             # MIT License
├── requirements. txt                    # Python dependencies
├── setup.py                            # Package installation
├── . gitignore                          # Git ignore patterns
├── .github/
│   └── workflows/
│       ├── tests.yml                   # CI/CD with GitHub Actions
│       └── release.yml                 # Automated releases
│
├── configurator/                       # Main package
│   ├── __init__.py
│   ├── __main__.py                     # Entry point:  python -m configurator
│   ├── cli.py                          # CLI interface (Click)
│   ├── wizard.py                       # Interactive wizard
│   ├── config. py                       # Configuration management
│   ├── logger.py                       # Logging system
│   ├── exceptions.py                   # Custom exceptions
│   │
│   ├── core/                           # Core functionality
│   │   ├── __init__. py
│   │   ├── validator.py                # System validation
│   │   ├── installer.py                # Installation orchestrator
│   │   ├── rollback.py                 # Rollback manager
│   │   ├── reporter.py                 # Progress reporter
│   │   └── notifier.py                 # Notification system
│   │
│   ├── modules/                        # Installation modules
│   │   ├── __init__.py
│   │   ├── base.py                     # Base module class
│   │   ├── system.py                   # System optimization
│   │   ├── security.py                 # Security hardening
│   │   ├── firewall.py                 # UFW firewall
│   │   ├── fail2ban.py                 # Fail2ban setup
│   │   ├── desktop.py                  # xrdp + XFCE4
│   │   ├── python.py                   # Python development
│   │   ├── nodejs.py                   # Node.js development
│   │   ├── golang.py                   # Go development
│   │   ├── rust.py                     # Rust development
│   │   ├── java.py                     # Java development
│   │   ├── php.py                      # PHP development
│   │   ├── docker.py                   # Docker + Compose
│   │   ├── vscode.py                   # VS Code installation
│   │   ├── cursor.py                   # Cursor IDE installation
│   │   ├── neovim.py                   # Neovim installation
│   │   ├── git.py                      # Git + GitHub CLI
│   │   ├── databases.py                # Database clients
│   │   ├── devops.py                   # DevOps tools
│   │   ├── networking.py               # WireGuard, Caddy
│   │   ├── monitoring.py               # Netdata
│   │   ├── utilities.py                # CLI utilities
│   │   └── rbac.py                     # Multi-user RBAC
│   │
│   ├── utils/                          # Utility functions
│   │   ├── __init__.py
│   │   ├── command.py                  # Command execution
│   │   ├── file.py                     # File operations
│   │   ├── network.py                  # Network utilities
│   │   ├── system.py                   # System information
│   │   └── validation.py               # Input validation
│   │
│   └── templates/                      # Configuration templates
│       ├── xrdp.ini. j2
│       ├── caddy.conf.j2
│       ├── wireguard.conf.j2
│       └── fail2ban-jail.conf.j2
│
├── config/                             # Configuration files
│   ├── default.yaml                    # Default configuration
│   ├── profiles/                       # Pre-defined profiles
│   │   ├── beginner.yaml               # Beginner-friendly
│   │   ├── intermediate.yaml           # Intermediate users
│   │   ├── advanced.yaml               # Advanced/Full stack
│   │   ├── backend-dev.yaml            # Backend developer
│   │   ├── frontend-dev.yaml           # Frontend developer
│   │   ├── fullstack-dev.yaml          # Full-stack developer
│   │   ├── data-science.yaml           # Data science
│   │   └── devops.yaml                 # DevOps engineer
│   └── examples/                       # Example configurations
│       ├── minimal.yaml
│       ├── python-only.yaml
│       ├── nodejs-only.yaml
│       └── custom-tools.yaml
│
├── scripts/                            # Utility scripts
│   ├── bootstrap.sh                    # Initial bootstrap
│   ├── verify.sh                       # Post-install verification
│   ├── install.sh                      # One-line installer
│   └── uninstall.sh                    # Uninstaller
│
├── tests/                              # Test suite
│   ├── __init__.py
│   ├── conftest.py                     # Pytest configuration
│   ├── unit/                           # Unit tests
│   │   ├── test_validator.py
│   │   ├── test_modules.py
│   │   ├── test_config.py
│   │   └── test_utils.py
│   ├── integration/                    # Integration tests
│   │   ├── test_full_install.py
│   │   ├── test_rollback.py
│   │   └── test_profiles.py
│   └── fixtures/                       # Test fixtures
│       ├── configs/
│       └── mocks/
│
├── docs/                               # Documentation
│   ├── README.md                       # Documentation index
│   ├── quickstart/
│   │   ├── 5-minute-guide.md
│   │   ├── video-tutorial.md
│   │   └── screenshots/
│   ├── installation/
│   │   ├── requirements.md
│   │   ├── step-by-step.md
│   │   ├── digitalocean. md
│   │   └── troubleshooting.md
│   ├── configuration/
│   │   ├── overview.md
│   │   ├── profiles.md
│   │   ├── security.md
│   │   └── customization.md
│   ├── examples/
│   │   └── *.yaml (example configs)
│   ├── advanced/
│   │   ├── plugins.md
│   │   ├── hooks.md
│   │   └── api.md
│   ├── reference/
│   │   ├── cli-commands.md
│   │   ├── configuration-options.md
│   │   └── glossary.md
│   └── community/
│       ├── faq.md
│       ├── contributing.md
│       └── support.md
│
└── examples/                           # Example use cases
    ├── databases/
    │   ├── postgres-docker-compose.yml
    │   ├── mysql-docker-compose.yml
    │   └── redis-docker-compose.yml
    ├── networking/
    │   ├── wireguard-setup.sh
    │   └── caddy-examples/
    └── hooks/
        ├── pre-install-example.sh
        └── post-install-example.sh
```

### 2.3 ARCHITECTURE PATTERN: MODULAR + PROGRESSIVE DISCLOSURE

**Core Principle:**

```
BEGINNER sees:   Simple wizard with safe defaults
INTERMEDIATE sees: Some customization options
ADVANCED sees:  Full control with plugins/hooks
```

**Implementation:**

```python
# Base Module Interface
class ConfigurationModule(ABC):
    """Base class for all configuration modules"""

    def __init__(self, config: Dict[str, Any], logger: Logger):
        self.config = config
        self.logger = logger
        self.rollback_commands:  List[str] = []
        self.state:  Dict[str, Any] = {}

    @abstractmethod
    def validate(self) -> bool:
        """
        Validate prerequisites before installation
        Returns:  True if ready to install, False otherwise
        Raises: PrerequisiteError with helpful message
        """
        pass

    @abstractmethod
    def configure(self) -> bool:
        """
        Execute configuration/installation
        Returns: True if successful
        Raises: ModuleExecutionError with helpful message
        """
        pass

    @abstractmethod
    def verify(self) -> bool:
        """
        Verify installation was successful
        Returns: True if verified
        """
        pass

    def rollback(self) -> bool:
        """
        Rollback changes made by this module
        Returns: True if rollback successful
        """
        for cmd in reversed(self.rollback_commands):
            self._execute_command(cmd, check=False)
        return True

    def _execute_command(self, cmd: str, check: bool = True) -> subprocess.CompletedProcess:
        """Execute shell command with error handling"""
        pass
```

### 2.4 PROGRESSIVE DISCLOSURE WIZARD

```python
class WizardInterface:
    """
    Three-tier wizard system based on user experience level
    """

    PROFILES = {
        'beginner':  {
            'name': '🟢 Quick Setup (Recommended for Beginners)',
            'description': 'Safe defaults, minimal questions, ~30 minutes',
            'features': ['xrdp', 'python', 'nodejs', 'docker', 'vscode', 'git'],
            'questions': 3,  # Only hostname, timezone, password
            'advanced_features': []
        },
        'intermediate':  {
            'name': '🟡 Standard Setup',
            'description': 'Balanced configuration, ~45 minutes',
            'features':  ['All beginner', 'cursor', 'neovim', 'wireguard', 'caddy'],
            'questions': 8,
            'advanced_features':  ['vpn', 'reverse_proxy']
        },
        'advanced':  {
            'name': '🔴 Advanced Setup',
            'description': 'Full control, all features, ~60 minutes',
            'features':  'all',
            'questions': 20,
            'advanced_features':  ['plugins', 'hooks', 'rbac', 'custom_tools']
        }
    }

    def run(self):
        """
        Main wizard flow:
        1. Welcome + Select profile
        2. Profile-specific questions
        3. Show installation plan
        4. Confirm and install
        5. Verification
        6. Final instructions
        """
        pass
```

## ═══════════════════════════════════════════════════════════════════

## SECTION 3: DETAILED MODULE SPECIFICATIONS

## ═══════════════════════════════════════════════════════════════════

### 3.1 SYSTEM MODULE (Priority: CRITICAL)

**Responsibilities:**

- System validation
- Package repository optimization
- Hostname configuration
- Timezone configuration
- Locale configuration
- Swap configuration
- Kernel parameter tuning
- Performance optimization

**Implementation Requirements:**

```python
class SystemModule(ConfigurationModule):
    """System optimization and configuration"""

    def validate(self):
        """
        Pre-flight checks:
        - Verify Debian 13 (check /etc/os-release)
        - Check architecture (x86_64)
        - Verify systemd
        - Check internet connectivity
        - Verify sudo/root access
        - Check disk space (>20GB free)
        - Check RAM (>2GB)
        """

        # Check Debian version
        with open('/etc/os-release') as f:
            content = f.read()
            if 'VERSION_ID="13"' not in content:
                raise PrerequisiteError(
                    what="Unsupported Debian version",
                    why="This tool is designed for Debian 13 (Trixie) only",
                    how="""
                    Your system:  {current_version}
                    Required:  Debian 13 (Trixie)

                    Please use a fresh Debian 13 VPS.
                    """,
                    docs_link="https://docs.yourproject.com/requirements"
                )

        # Additional checks...
        return True

    def configure(self):
        """
        Configure system:
        1. Update package lists
        2. Install essential packages
        3. Configure hostname
        4. Configure timezone
        5. Configure locale
        6. Create swap if needed
        7.  Tune kernel parameters
        8.  Optimize APT
        """

        # 1. Update package lists
        self. logger.info("📦 Updating package lists...")
        self._run_apt_update()

        # 2. Install essentials
        essential_packages = [
            'curl', 'wget', 'git', 'vim', 'htop',
            'build-essential', 'software-properties-common',
            'apt-transport-https', 'ca-certificates', 'gnupg'
        ]
        self._install_packages(essential_packages)

        # 3. Hostname
        self._configure_hostname()

        # 4. Timezone
        self._configure_timezone()

        # 5. Locale
        self._configure_locale()

        # 6. Swap
        self._configure_swap()

        # 7. Kernel tuning
        self._tune_kernel_parameters()

        return True

    def _configure_hostname(self):
        """Configure system hostname"""
        hostname = self.config.get('system', {}).get('hostname', 'dev-workstation')

        if self.config.get('interactive'):
            print(f"\nCurrent hostname: {self._get_current_hostname()}")
            new_hostname = input(f"Enter hostname [{hostname}]: ").strip()
            if new_hostname:
                hostname = new_hostname

        # Validate
        if not re.match(r'^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$', hostname):
            raise ConfigurationError(f"Invalid hostname: {hostname}")

        # Set hostname
        subprocess.run(['hostnamectl', 'set-hostname', hostname], check=True)

        # Update /etc/hosts
        self._update_etc_hosts(hostname)

        self.logger.info(f"✅ Hostname:  {hostname}")
        self.rollback_commands.append(f"hostnamectl set-hostname old-hostname")

    def _tune_kernel_parameters(self):
        """Apply kernel tuning for development workstation"""

        sysctl_config = """
# Debian VPS Workstation - Kernel Tuning
# Generated by debian-vps-configurator

# Memory Management
vm.swappiness = 10
vm.dirty_ratio = 15
vm.dirty_background_ratio = 5

# File System
fs.file-max = 100000
fs.inotify. max_user_watches = 524288

# Network Performance
net.core.netdev_max_backlog = 5000
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.ipv4.tcp_rmem = 4096 87380 134217728
net.ipv4.tcp_wmem = 4096 65536 134217728

# TCP Optimization
net.ipv4.tcp_fastopen = 3
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_fin_timeout = 30
net. ipv4.tcp_keepalive_time = 1200

# BBR Congestion Control
net.core.default_qdisc = fq
net.ipv4.tcp_congestion_control = bbr
"""

        with open('/etc/sysctl.d/99-vps-workstation.conf', 'w') as f:
            f.write(sysctl_config)

        subprocess.run(['sysctl', '-p', '/etc/sysctl. d/99-vps-workstation.conf'],
                      check=True, capture_output=True)

        self.logger.info("✅ Kernel parameters tuned")
```

### 3.2 SECURITY MODULE (Priority: CRITICAL)

**MANDATORY - CANNOT BE DISABLED**

**Responsibilities:**

- UFW firewall setup (MANDATORY)
- Fail2ban installation
- SSH hardening
- Automatic security updates
- Audit logging
- Security best practices

**Implementation Requirements:**

```python
class SecurityModule(ConfigurationModule):
    """
    Security hardening - MANDATORY for all installations
    User cannot skip or disable this module
    """

    def validate(self):
        """Check security prerequisites"""

        # Warn if conflicting security tools installed
        conflicting = []
        if self._command_exists('iptables-save'):
            result = subprocess.run(['iptables-save'], capture_output=True)
            if result.stdout.strip():
                conflicting. append('iptables rules')

        if conflicting:
            self.logger.warning(f"""
            ⚠️  Existing security configuration detected:  {', '.join(conflicting)}

            For best results, we recommend starting with a clean system.
            Existing rules will be backed up to /var/backups/security-backup/
            """)

            if self.config.get('interactive'):
                confirm = input("Backup and proceed? (yes/no): ")
                if confirm.lower() != 'yes':
                    raise PrerequisiteError("User cancelled security setup")

        return True

    def configure(self):
        """
        Security hardening sequence:
        1. Setup UFW firewall (MANDATORY)
        2. Install and configure fail2ban
        3. Harden SSH configuration
        4. Enable automatic security updates
        5. Configure audit logging
        """

        self.logger.info("""
╔════════════════════════════════════════════════════════╗
║         🔒 SECURITY HARDENING (MANDATORY)              ║
╚════════════════════════════════════════════════════════╝

Your server will be protected with:
  ✓ UFW Firewall (blocks unauthorized access)
  ✓ Fail2ban (prevents brute force attacks)
  ✓ SSH Hardening (secure remote access)
  ✓ Automatic Updates (security patches)

This is MANDATORY and cannot be skipped.
        """)

        if self.config.get('interactive'):
            input("Press Enter to continue...")

        # 1. UFW Firewall
        self._setup_ufw_firewall()

        # 2. Fail2ban
        self._setup_fail2ban()

        # 3. SSH Hardening
        self._harden_ssh()

        # 4. Automatic Updates
        self._enable_automatic_updates()

        # 5. Audit Logging
        self._setup_audit_logging()

        return True

    def _setup_ufw_firewall(self):
        """Setup UFW firewall - MANDATORY"""

        self.logger.info("🔥 Setting up UFW firewall...")

        # Install UFW
        self._install_packages(['ufw'])

        # Reset to clean state
        subprocess.run(['ufw', '--force', 'reset'], check=True)

        # Default policies
        subprocess.run(['ufw', 'default', 'deny', 'incoming'], check=True)
        subprocess.run(['ufw', 'default', 'allow', 'outgoing'], check=True)

        # Allow SSH with rate limiting
        subprocess.run(['ufw', 'limit', '22/tcp', 'comment', 'SSH'], check=True)

        # Allow RDP for xrdp
        subprocess.run(['ufw', 'allow', '3389/tcp', 'comment', 'RDP'], check=True)

        # Enable UFW
        subprocess.run(['ufw', '--force', 'enable'], check=True)

        # Verify
        result = subprocess.run(['ufw', 'status'], capture_output=True, text=True)
        if 'Status: active' not in result.stdout:
            raise ModuleExecutionError("UFW failed to activate")

        self.logger.info("✅ Firewall active and configured")
        self.logger.info("\n📋 Active Rules:")
        subprocess.run(['ufw', 'status', 'numbered'])

        self.rollback_commands.append("ufw disable")
```

### 3.3 DESKTOP MODULE (xrdp + XFCE4) (Priority: HIGH)

**Responsibilities:**

- Install xrdp server
- Install XFCE4 desktop environment
- Configure SSL certificates
- Optimize for remote access
- Configure session management

**Implementation Requirements:**

```python
class DesktopModule(ConfigurationModule):
    """Install and configure xrdp + XFCE4 remote desktop"""

    def validate(self):
        """Check prerequisites for desktop installation"""

        # Check if X11 is already installed
        if os.path.exists('/usr/bin/X'):
            self.logger.warning("X11 already installed, will configure for xrdp")

        # Check available disk space (desktop needs ~2GB)
        free_gb = self._get_free_disk_space_gb()
        if free_gb < 5:
            raise PrerequisiteError(
                what="Insufficient disk space",
                why=f"Only {free_gb}GB free, need at least 5GB",
                how="Free up disk space or use a larger VPS"
            )

        return True

    def configure(self):
        """
        Install xrdp + XFCE4:
        1. Install xrdp and xorgxrdp
        2. Install XFCE4 desktop environment
        3. Generate SSL certificates
        4. Configure xrdp
        5. Configure XFCE4 for remote use
        6. Setup session management
        7. Enable and start services
        """

        self.logger.info("🖥️  Installing Remote Desktop (xrdp + XFCE4)...")

        # 1. Install xrdp
        self._install_packages(['xrdp', 'xorgxrdp'])

        # 2. Install XFCE4 (lightweight desktop)
        self.logger.info("📦 Installing XFCE4 (this may take a few minutes)...")
        self._install_packages([
            'xfce4',
            'xfce4-goodies',
            'xfce4-terminal',
            'thunar',
            'firefox-esr'  # Web browser
        ])

        # 3. Generate SSL certificates
        self._setup_ssl_certificates()

        # 4. Configure xrdp
        self._configure_xrdp()

        # 5. Optimize XFCE4
        self._optimize_xfce4()

        # 6. Configure session
        self._configure_session()

        # 7. Start services
        subprocess.run(['systemctl', 'enable', 'xrdp'], check=True)
        subprocess.run(['systemctl', 'start', 'xrdp'], check=True)

        self.logger.info("✅ Remote Desktop installed and running")

        return True

    def _configure_xrdp(self):
        """Configure xrdp for optimal performance"""

        xrdp_config = """
[Globals]
bitmap_cache=yes
bitmap_compression=yes
bulk_compression=yes
max_bpp=24
new_cursors=yes
use_compression=yes

[Xorg]
name=Xorg
lib=libxup.so
username=ask
password=ask
ip=127.0.0.1
port=-1
code=20
"""

        # Backup original
        if os.path.exists('/etc/xrdp/xrdp. ini'):
            shutil.copy('/etc/xrdp/xrdp.ini', '/etc/xrdp/xrdp.ini.backup')

        with open('/etc/xrdp/xrdp.ini', 'w') as f:
            f.write(xrdp_config)

        self.rollback_commands.append("mv /etc/xrdp/xrdp.ini.backup /etc/xrdp/xrdp.ini")
```

### 3.4 PROGRAMMING LANGUAGE MODULES

**3.4.1 Python Module**

```python
class PythonModule(ConfigurationModule):
    """Setup Python development environment"""

    def configure(self):
        """
        Python setup:
        1. Use Debian 13 system Python (3.11)
        2. Install python3-venv, pip, dev tools
        3. Install common development packages
        4. Configure pip
        """

        self.logger. info("🐍 Setting up Python development environment...")

        # System Python + essentials
        packages = [
            'python3',
            'python3-pip',
            'python3-venv',
            'python3-dev',
            'build-essential',
            'libssl-dev',
            'libffi-dev',
            'python3-setuptools'
        ]

        self._install_packages(packages)

        # Upgrade pip
        subprocess.run([
            'python3', '-m', 'pip', 'install', '--upgrade', 'pip'
        ], check=True)

        # Install common dev tools globally
        dev_tools = [
            'black',          # Code formatter
            'pylint',         # Linter
            'mypy',           # Type checker
            'pytest',         # Testing
            'ipython',        # Better REPL
            'virtualenv',     # Alternative to venv
            'wheel'           # Package building
        ]

        subprocess.run([
            'pip3', 'install', '--user'
        ] + dev_tools, check=True)

        # Create example virtual environment
        example_venv = '/root/example-venv'
        subprocess.run([
            'python3', '-m', 'venv', example_venv
        ], check=True)

        self.logger.info(f"""
✅ Python development environment ready!

Python version: {self._get_python_version()}

Example usage:
  # Create virtual environment
  python3 -m venv myproject
  source myproject/bin/activate

  # Install packages
  pip install requests flask django

  # Code formatting
  black mycode.py

  # Type checking
  mypy mycode. py
        """)

        return True
```

**3.4.2 Node.js Module (with nvm)**

```python
class NodeJSModule(ConfigurationModule):
    """Setup Node.js development environment with nvm"""

    def configure(self):
        """
        Node.js setup with nvm:
        1. Install nvm (Node Version Manager)
        2. Install Node.js LTS (v20)
        3. Install npm, yarn, pnpm
        4. Install global development tools
        """

        self.logger. info("🟢 Setting up Node.js with nvm...")

        # 1. Install nvm
        nvm_install_script = "https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh"
        subprocess.run([
            'curl', '-o-', nvm_install_script
        ], stdout=subprocess.PIPE, check=True)

        # Source nvm
        nvm_dir = os.path.expanduser('~/. nvm')
        os.environ['NVM_DIR'] = nvm_dir

        # 2. Install Node.js LTS
        self. logger.info("📦 Installing Node.js v20 (LTS)...")
        subprocess.run([
            'bash', '-c',
            'source ~/. nvm/nvm.sh && nvm install 20 && nvm use 20'
        ], check=True)

        # 3. Install package managers
        subprocess.run([
            'bash', '-c',
            'source ~/. nvm/nvm.sh && npm install -g yarn pnpm'
        ], check=True)

        # 4. Install global dev tools
        global_tools = [
            'typescript',
            'ts-node',
            'nodemon',
            'eslint',
            'prettier',
            'webpack',
            'vite',
            '@vue/cli',
            'create-react-app'
        ]

        subprocess.run([
            'bash', '-c',
            f"source ~/.nvm/nvm. sh && npm install -g {' '.join(global_tools)}"
        ], check=True)

        self.logger.info("""
✅ Node.js development environment ready!

Node.js version: v20 (LTS)
Package managers:  npm, yarn, pnpm

Example usage:
  # Switch Node versions
  nvm install 18
  nvm use 18

  # Create new project
  npm init -y

  # Install dependencies
  npm install express
  yarn add react
  pnpm add vue
        """)

        return True
```

### 3.5 DOCKER MODULE

```python
class DockerModule(ConfigurationModule):
    """Install Docker + Docker Compose"""

    def configure(self):
        """
        Docker installation:
        1. Add Docker's official GPG key
        2. Add Docker apt repository
        3. Install Docker Engine + Compose
        4. Configure Docker daemon
        5. Add user to docker group
        6. Verify installation
        """

        self.logger.info("🐳 Installing Docker...")

        # 1. Add Docker GPG key
        subprocess.run([
            'install', '-m', '0755', '-d', '/etc/apt/keyrings'
        ], check=True)

        subprocess.run([
            'curl', '-fsSL',
            'https://download.docker.com/linux/debian/gpg',
            '-o', '/etc/apt/keyrings/docker.asc'
        ], check=True)

        subprocess.run([
            'chmod', 'a+r', '/etc/apt/keyrings/docker.asc'
        ], check=True)

        # 2. Add repository
        repo_line = (
            f'deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.asc] '
            f'https://download.docker.com/linux/debian '
            f'trixie stable'
        )

        with open('/etc/apt/sources. list.d/docker.list', 'w') as f:
            f.write(repo_line + '\n')

        # 3. Install Docker
        self._run_apt_update()
        self._install_packages([
            'docker-ce',
            'docker-ce-cli',
            'containerd.io',
            'docker-buildx-plugin',
            'docker-compose-plugin'
        ])

        # 4. Configure daemon
        daemon_config = {
            "log-driver": "json-file",
            "log-opts": {
                "max-size": "10m",
                "max-file": "3"
            },
            "storage-driver": "overlay2"
        }

        with open('/etc/docker/daemon.json', 'w') as f:
            json.dump(daemon_config, f, indent=2)

        # 5. Add user to docker group
        subprocess.run(['usermod', '-aG', 'docker', 'root'], check=True)

        # 6. Start Docker
        subprocess.run(['systemctl', 'enable', 'docker'], check=True)
        subprocess.run(['systemctl', 'start', 'docker'], check=True)

        # 7. Verify
        result = subprocess.run(['docker', 'run', 'hello-world'],
                              capture_output=True, text=True)
        if 'Hello from Docker!' not in result.stdout:
            raise ModuleExecutionError("Docker verification failed")

        self. logger.info("""
✅ Docker installed and verified!

Usage:
  docker ps
  docker run nginx
  docker compose up -d

Example:  Run PostgreSQL
  docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=dev postgres: 16
        """)

        return True
```

### 3.6 EDITOR MODULES

**3.6.1 VS Code Module**

```python
class VSCodeModule(ConfigurationModule):
    """Install VS Code from official Microsoft repository"""

    def configure(self):
        """
        VS Code installation:
        1. Add Microsoft GPG key
        2. Add VS Code repository
        3. Install code package
        4. Install recommended extensions
        """

        self.logger.info("💻 Installing Visual Studio Code...")

        # 1. Add Microsoft GPG key
        subprocess.run([
            'wget', '-qO-',
            'https://packages.microsoft.com/keys/microsoft.asc',
            '|', 'gpg', '--dearmor',
            '>', '/etc/apt/keyrings/packages.microsoft.gpg'
        ], shell=True, check=True)

        # 2. Add repository
        repo_line = (
            'deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/packages.microsoft.gpg] '
            'https://packages.microsoft.com/repos/code stable main'
        )

        with open('/etc/apt/sources.list.d/vscode.list', 'w') as f:
            f.write(repo_line + '\n')

        # 3. Install
        self._run_apt_update()
        self._install_packages(['code'])

        # 4. Install extensions
        extensions = [
            'ms-python.python',
            'dbaeumer.vscode-eslint',
            'esbenp.prettier-vscode',
            'golang.go',
            'rust-lang.rust-analyzer',
            'ms-vscode.cpptools',
            'redhat.java',
            'bmewburn.vscode-intelephense-client'
        ]

        for ext in extensions:
            try:
                subprocess.run(['code', '--install-extension', ext],
                             check=True, timeout=60)
                self.logger.info(f"  ✓ Installed:  {ext}")
            except Exception as e:
                self.logger.warning(f"  ⚠ Failed to install {ext}: {e}")

        self.logger.info("✅ VS Code installed with extensions")

        return True
```

**3.6.2 Cursor IDE Module**

```python
class CursorModule(ConfigurationModule):
    """Install Cursor IDE with multi-strategy fallback"""

    STRATEGIES = [
        {
            'name': 'Official Download Page',
            'url': 'https://cursor.sh/download',
            'method': 'parse_html'
        },
        {
            'name': 'Direct Download Link',
            'url': 'https://downloader.cursor.sh/linux/appImage/x64',
            'method': 'direct'
        },
        {
            'name': 'GitHub Releases',
            'url': 'https://api.github.com/repos/getcursor/cursor/releases/latest',
            'method': 'github_api'
        }
    ]

    def configure(self):
        """
        Try multiple strategies to install Cursor:
        1. Parse official download page
        2. Direct download link
        3. GitHub releases API
        """

        self.logger.info("⚡ Installing Cursor IDE...")

        for strategy in self.STRATEGIES:
            try:
                self. logger.info(f"  Trying:  {strategy['name']}")

                if strategy['method'] == 'parse_html':
                    url = self._parse_download_page(strategy['url'])
                elif strategy['method'] == 'github_api':
                    url = self._get_github_latest(strategy['url'])
                else:
                    url = strategy['url']

                if self._download_and_install_deb(url):
                    self.logger.info("✅ Cursor IDE installed")
                    return True

            except Exception as e:
                self.logger.debug(f"Strategy failed: {e}")
                continue

        # All strategies failed
        self.logger. warning("""
⚠️  Could not install Cursor IDE automatically.

Manual installation:
1. Visit:  https://cursor.sh
2. Download the . deb file
3. Install: sudo dpkg -i cursor_*.deb
        """)

        return False  # Non-critical, don't fail entire installation
```

## ═══════════════════════════════════════════════════════════════════

## SECTION 4: ERROR HANDLING & USER EXPERIENCE

## ═══════════════════════════════════════════════════════════════════

### 4.1 BEGINNER-FRIENDLY ERROR MESSAGES

**MANDATORY STRUCTURE:**

```python
class BeginnerFriendlyError(Exception):
    """
    Every error MUST have:
    - what: What happened (plain English)
    - why: Why it happened (explanation)
    - how: How to fix (actionable steps)
    - docs_link: Link to relevant documentation
    """

    def __init__(self, what:  str, why: str, how:  str, docs_link: str = None):
        self.what = what
        self.why = why
        self.how = how
        self.docs_link = docs_link

        message = f"""
╔════════════════════════════════════════════════════════╗
║                  ❌ ERROR OCCURRED                      ║
╚════════════════════════════════════════════════════════╝

WHAT HAPPENED:
{what}

WHY IT HAPPENED:
{why}

HOW TO FIX:
{how}
"""
        if docs_link:
            message += f"\n📖 More help: {docs_link}\n"

        message += """
════════════════════════════════════════════════════════

Need more help?
- View logs: tail -f /var/log/debian-vps-configurator/install.log
- Community:  https://github.com/yourrepo/discussions
- Report bug: https://github.com/yourrepo/issues
        """

        super().__init__(message)

# Example usage:
raise BeginnerFriendlyError(
    what="Package 'docker-ce' could not be installed",
    why="The package was not found in the system repositories",
    how="""
Try these steps:
1. Update package list:
   sudo apt-get update

2. Check internet connection:
   ping -c 3 google.com

3. Verify repository was added correctly:
   cat /etc/apt/sources.list. d/docker.list

4. If problem persists, run with --verbose flag for detailed logs
    """,
    docs_link="https://docs.yourproject.com/troubleshooting/docker"
)
```

### 4.2 PROGRESS REPORTING

```python
class ProgressReporter:
    """Beautiful progress reporting using Rich library"""

    def __init__(self):
        from rich.console import Console
        from rich.progress import Progress, SpinnerColumn, TextColumn

        self.console = Console()
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True
        )

    def start_phase(self, phase_name: str, total_steps: int):
        """Start a new installation phase"""
        self.console.print(f"\n[bold blue]▶ {phase_name}[/bold blue]")
        self.current_phase = phase_name
        self. total_steps = total_steps
        self.current_step = 0

    def update(self, message: str):
        """Update current step"""
        self.current_step += 1
        percentage = (self.current_step / self.total_steps) * 100
        self.console.print(
            f"  [{self.current_step}/{self. total_steps}] ({percentage:.0f}%) {message}"
        )

    def complete_phase(self, success: bool = True):
        """Mark phase as complete"""
        if success:
            self.console. print(f"[bold green]✓ {self.current_phase} complete[/bold green]")
        else:
            self.console.print(f"[bold red]✗ {self.current_phase} failed[/bold red]")

    def show_summary(self, results: Dict[str, bool]):
        """Show installation summary"""
        from rich.table import Table

        table = Table(title="Installation Summary")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")

        for component, success in results.items():
            status = "✅ Installed" if success else "❌ Failed"
            table.add_row(component, status)

        self.console.print(table)
```

### 4.3 INTERACTIVE WIZARD

```python
class InteractiveWizard:
    """Interactive wizard for beginners"""

    def run(self) -> Dict[str, Any]:
        """
        Run wizard and return configuration
        """
        from rich.prompt import Prompt, Confirm
        from rich.console import Console

        console = Console()
        config = {}

        # Welcome
        console.print("""
╔════════════════════════════════════════════════════════╗
║   Debian 13 VPS Workstation Configurator              ║
║   Transform your VPS into a coding powerhouse!         ║
╚════════════════════════════════════════════════════════╝

This wizard will guide you through the setup process.
It should take about 5 minutes to answer all questions,
then 30-60 minutes for the actual installation.
        """, style="bold cyan")

        # Step 1: Experience level
        console.print("\n[bold]Step 1: Select Your Experience Level[/bold]\n")
        console.print("1. 🟢 Beginner - Quick setup with safe defaults (Recommended)")
        console.print("   → Perfect if you're new to Linux")
        console.print("   → Installs:  Remote Desktop, Python, Node.js, Docker, VS Code")
        console.print("   → Takes: ~30 minutes\n")

        console. print("2. 🟡 Intermediate - More control and features")
        console.print("   → For users comfortable with Linux basics")
        console.print("   → Adds: Multiple editors, VPN, reverse proxy")
        console.print("   → Takes: ~45 minutes\n")

        console.print("3. 🔴 Advanced - Full control, all features")
        console.print("   → For system administrators and power users")
        console.print("   → Adds: Plugins, hooks, RBAC, custom tools")
        console.print("   → Takes: ~60 minutes\n")

        level = Prompt.ask(
            "Select your level",
            choices=["1", "2", "3"],
            default="1"
        )

        profile_map = {'1': 'beginner', '2': 'intermediate', '3': 'advanced'}
        config['profile'] = profile_map[level]

        # Profile-specific questions
        if config['profile'] == 'beginner':
            return self._beginner_wizard(console, config)
        elif config['profile'] == 'intermediate':
            return self._intermediate_wizard(console, config)
        else:
            return self._advanced_wizard(console, config)

    def _beginner_wizard(self, console, config):
        """Minimal questions for beginners"""

        console.print("\n[bold]Step 2: Basic Configuration[/bold]\n")

        # Hostname
        config['system'] = {}
        config['system']['hostname'] = Prompt.ask(
            "Enter a hostname for your server",
            default="dev-workstation"
        )

        # Timezone
        console.print("\nCommon timezones:")
        console.print("  1. Asia/Jakarta")
        console.print("  2. UTC")
        console.print("  3. America/New_York")
        console.print("  4. Europe/London")

        tz_choice = Prompt.ask("Select timezone", choices=["1", "2", "3", "4"], default="1")
        tz_map = {
            '1': 'Asia/Jakarta',
            '2': 'UTC',
            '3': 'America/New_York',
            '4': 'Europe/London'
        }
        config['system']['timezone'] = tz_map[tz_choice]

        # Show what will be installed
        console.print("\n[bold]Installation Plan[/bold]\n")
        console.print("The following will be installed:")
        console.print("  ✓ Security:  Firewall, fail2ban, automatic updates")
        console.print("  ✓ Remote Desktop: xrdp + XFCE4")
        console.print("  ✓ Languages: Python 3.11, Node.js 20")
        console.print("  ✓ Tools: Docker, Git, VS Code")
        console.print("  ✓ Monitoring: Netdata")
        console.print("\nEstimated time: 30 minutes")

        # Confirm
        if not Confirm.ask("\nReady to start installation?"):
            console.print("[red]Installation cancelled.[/red]")
            sys.exit(0)

        return config
```

## ═══════════════════════════════════════════════════════════════════

## SECTION 5: TESTING REQUIREMENTS

## ═══════════════════════════════════════════════════════════════════

### 5.1 UNIT TESTING (Priority: HIGH)

**Coverage Target:**

- MVP (Week 1-2): 60% coverage
- Enhancement (Week 3): 75% coverage
- Release (Week 4): 80% coverage

**Test Structure:**

```python
# tests/unit/test_validator.py
import pytest
from configurator.core.validator import SystemValidator

class TestSystemValidator:
    """Unit tests for system validation"""

    def test_debian_version_detection(self, tmp_path):
        """Test Debian 13 detection"""
        # Create mock /etc/os-release
        os_release = tmp_path / "os-release"
        os_release.write_text('VERSION_ID="13"\nID="debian"\n')

        validator = SystemValidator(os_release_path=os_release)
        assert validator.validate_os() == True

    def test_insufficient_ram_detection(self, monkeypatch):
        """Test RAM validation"""
        def mock_get_ram():
            return 1  # 1GB RAM (insufficient)

        monkeypatch.setattr('configurator. utils.system.get_ram_gb', mock_get_ram)

        validator = SystemValidator()
        assert validator.validate_resources() == False

    def test_internet_connectivity(self, monkeypatch):
        """Test internet connection check"""
        def mock_ping(host):
            return True

        monkeypatch.setattr('configurator.utils.network.ping', mock_ping)

        validator = SystemValidator()
        assert validator.validate_network() == True

# tests/unit/test_modules.py
class TestFirewallModule:
    """Unit tests for firewall module"""

    def test_ufw_installation(self, mock_apt):
        """Test UFW package installation"""
        module = FirewallModule(config={}, logger=Mock())
        module.configure()

        mock_apt.assert_called_with(['ufw'])

    def test_firewall_rules_applied(self, mock_subprocess):
        """Test firewall rules are correctly applied"""
        module = FirewallModule(config={}, logger=Mock())
        module.configure()

        # Verify SSH rule
        mock_subprocess.assert_any_call(['ufw', 'limit', '22/tcp'])
        # Verify RDP rule
        mock_subprocess. assert_any_call(['ufw', 'allow', '3389/tcp'])
```

### 5.2 INTEGRATION TESTING (Priority: MEDIUM)

**Test on Real VPS:**

```python
# tests/integration/test_full_install.py
import pytest
from fabric import Connection

@pytest.mark.integration
@pytest.mark.slow
class TestFullInstallation:
    """Integration tests on real DigitalOcean droplet"""

    @pytest.fixture(scope='class')
    def vps(self):
        """Create and destroy test VPS"""
        # Create DigitalOcean droplet
        droplet = create_test_droplet(
            name='test-debian-configurator',
            image='debian-13-x64',
            size='s-2vcpu-4gb'
        )

        yield droplet

        # Cleanup
        droplet.destroy()

    def test_beginner_profile_installation(self, vps):
        """Test full beginner profile installation"""

        # Upload configurator
        conn = Connection(vps.ip_address, user='root')
        conn.put('dist/configurator.tar.gz', '/tmp/')

        # Extract and install
        conn.run('cd /tmp && tar xzf configurator.tar.gz')
        conn.run('cd /tmp/configurator && pip3 install -r requirements.txt')

        # Run installation
        result = conn.run(
            'cd /tmp/configurator && python3 -m configurator install --profile beginner --non-interactive',
            warn=True
        )

        assert result.return_code == 0, f"Installation failed: {result. stderr}"

        # Verify services are running
        assert self._check_service(conn, 'xrdp')
        assert self._check_service(conn, 'docker')
        assert self._check_service(conn, 'fail2ban')
        assert self._check_service(conn, 'ufw')

        # Verify tools are installed
        assert self._check_command(conn, 'python3')
        assert self._check_command(conn, 'node')
        assert self._check_command(conn, 'docker')
        assert self._check_command(conn, 'code')

    def _check_service(self, conn, service_name):
        """Check if service is active"""
        result = conn.run(f'systemctl is-active {service_name}', warn=True)
        return result.return_code == 0

    def _check_command(self, conn, command):
        """Check if command exists"""
        result = conn.run(f'which {command}', warn=True)
        return result.return_code == 0
```

### 5.3 CI/CD PIPELINE (GitHub Actions)

```yaml
# .github/workflows/tests.yml
name: Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  unit-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run linting
        run: |
          black --check configurator/
          pylint configurator/
          mypy configurator/

      - name: Run unit tests
        run: |
          pytest tests/unit/ -v --cov=configurator --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml

  integration-tests:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run integration tests
        env:
          DIGITALOCEAN_TOKEN: ${{ secrets.DIGITALOCEAN_TOKEN }}
        run: |
          pytest tests/integration/ -v --slow
```

## ═══════════════════════════════════════════════════════════════════

## SECTION 6: DOCUMENTATION REQUIREMENTS

## ═══════════════════════════════════════════════════════════════════

### 6.1 ESSENTIAL DOCUMENTATION (Week 1-2)

**README.md:**

````markdown
# Debian 13 VPS Workstation Configurator

One-command setup to transform your Debian 13 VPS into a fully-featured
remote desktop coding workstation.

## ✨ Features

- 🖥️ **Remote Desktop**: xrdp + XFCE4 (Windows RDP compatible)
- 🐍 **Full Stack Development**: Python, Node.js, Go, Rust, Java, PHP
- 🐳 **Containerization**: Docker + Docker Compose
- 💻 **Modern Editors**: VS Code, Cursor IDE, Neovim
- 🔒 **Security First**: Firewall, fail2ban, automatic updates
- 📊 **Monitoring**: Netdata real-time monitoring
- 🚀 **DevOps Tools**: Git, Ansible, Terraform, kubectl

## 🚀 Quick Start

```bash
# One-line installation (interactive)
curl -fsSL https://get.debian-vps-configurator.com | sudo bash

# Or download and run
wget https://github.com/youruser/debian-vps-configurator/releases/latest/download/install.sh
sudo bash install.sh
```
````

## 📋 Requirements

- Fresh Debian 13 (Trixie) VPS
- Minimum: 2 vCPU, 4GB RAM, 20GB disk
- Recommended: 4 vCPU, 8GB RAM, 40GB disk
- Root or sudo access
- Internet connection

## 📖 Documentation

- [5-Minute Quick Start](docs/quickstart/5-minute-guide.md)
- [Step-by-Step Installation](docs/installation/step-by-step.md)
- [Configuration Guide](docs/configuration/overview.md)
- [Troubleshooting](docs/installation/troubleshooting.md)
- [FAQ](docs/community/faq.md)

## 💬 Support

- [Community Discussions](https://github.com/youruser/repo/discussions)
- [Report Issues](https://github.com/youruser/repo/issues)
- [Documentation](https://docs.yourproject.com)

## 📜 License

MIT License - see [LICENSE](LICENSE)

````

**INSTALLATION. md:**
```markdown
# Installation Guide

## Method 1: One-Line Install (Recommended)

```bash
curl -fsSL https://get.debian-vps-configurator.com | sudo bash
````

This will:

1. Download the latest version
2. Verify checksum
3. Run interactive wizard
4. Install everything

## Method 2: Manual Install

### Step 1: Download

```bash
wget https://github.com/youruser/debian-vps-configurator/releases/latest/download/configurator.tar.gz
tar xzf configurator.tar.gz
cd debian-vps-configurator
```

### Step 2: Install Dependencies

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip
pip3 install -r requirements.txt
```

### Step 3: Run Wizard

```bash
sudo python3 -m configurator wizard
```

## Installation Profiles

### Beginner (Recommended)

Safe defaults, minimal questions, ~30 minutes

```bash
sudo python3 -m configurator install --profile beginner
```

### Intermediate

More control, additional features, ~45 minutes

```bash
sudo python3 -m configurator install --profile intermediate
```

### Advanced

Full control, all features, ~60 minutes

```bash
sudo python3 -m configurator install --profile advanced
```

## Non-Interactive Installation

```bash
# Use predefined config
sudo python3 -m configurator install --config myconfig.yaml --non-interactive

# Use profile without questions
sudo python3 -m configurator install --profile beginner --non-interactive
```

## Verification

```bash
sudo python3 -m configurator verify
```

## Troubleshooting

See [Troubleshooting Guide](troubleshooting.md)

```

### 6.2 COMPREHENSIVE DOCUMENTATION (Week 3-4)

- CONFIGURATION.md: All configuration options
- ARCHITECTURE.md: System architecture
- SECURITY.md: Security features and best practices
- ADVANCED.md: Plugins, hooks, RBAC
- API.md: Plugin API reference
- CONTRIBUTING.md: Contribution guidelines

## ═══════════════════════════════════════════════════════════════════
## SECTION 7: DELIVERABLES & TIMELINE
## ═══════════════════════════════════════════════════════════════════

### 7.1 WEEK 1-2: MVP (Minimum Viable Product)

**Deliverables:**
- ✅ Core system validation
- ✅ Security hardening (UFW, fail2ban, SSH, updates)
- ✅ Remote desktop (xrdp + XFCE4)
- ✅ Python development environment
- ✅ Node.js development environment (nvm)
- ✅ Docker + Docker Compose
- ✅ Git + GitHub CLI
- ✅ VS Code installation
- ✅ Basic CLI (install, verify, rollback)
- ✅ Interactive wizard (beginner profile)
- ✅ Essential documentation (README)
```
