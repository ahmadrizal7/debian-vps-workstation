# 🚀 Debian 13 VPS Workstation Configurator

Transform your Debian 13 VPS into a fully-featured remote desktop coding workstation with one command.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Debian 13](https://img.shields.io/badge/debian-13%20(Trixie)-red.svg)](https://www.debian.org/)

## ✨ Features

- 🖥️ **Remote Desktop**: xrdp + XFCE4 (Windows RDP compatible)
- 🐍 **Full Stack Development**: Python, Node.js, Go, Rust, Java, PHP
- 🐳 **Containerization**: Docker + Docker Compose
- 💻 **Modern Editors**: VS Code, Cursor IDE, Neovim
- 🔒 **Security First**: UFW Firewall, Fail2ban, SSH hardening, auto-updates
- 📊 **Monitoring**: Netdata real-time monitoring
- 🌐 **Networking**: WireGuard VPN, Caddy reverse proxy
- 🚀 **DevOps Tools**: Git, GitHub CLI

## 🎯 Quick Start

### One-Line Installation (Interactive)

```bash
# Download and run the installer
curl -fsSL https://github.com/youruser/debian-vps-configurator/releases/latest/download/install.sh | sudo bash
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/youruser/debian-vps-configurator.git
cd debian-vps-configurator

# Install dependencies
pip install -r requirements.txt

# Run the interactive wizard
sudo python -m configurator wizard
```

### Quick Install with Profile

```bash
# Beginner profile (recommended)
sudo python -m configurator install --profile beginner -y

# Intermediate profile
sudo python -m configurator install --profile intermediate -y

# Advanced profile (all features)
sudo python -m configurator install --profile advanced -y
```

## 📋 Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| OS | Debian 13 (Trixie) | Debian 13 (Trixie) |
| Architecture | x86_64 | x86_64 |
| CPU | 2 vCPU | 4 vCPU |
| RAM | 4 GB | 8 GB |
| Disk | 20 GB | 40 GB |
| Access | Root or sudo | Root |

## 🎭 Installation Profiles

### 🟢 Beginner (Recommended for new users)
- Quick setup with safe defaults
- ~30 minutes installation time
- Includes: Remote Desktop, Python, Node.js, Docker, VS Code, Git

### 🟡 Intermediate
- Balanced configuration with more features
- ~45 minutes installation time
- Adds: Go, Cursor IDE, Neovim, Caddy, Netdata

### 🔴 Advanced
- Full control with all features
- ~60 minutes installation time
- Adds: All languages, WireGuard VPN, custom configuration

## 💻 Usage

### Commands

```bash
# Interactive wizard (recommended for first-time users)
sudo vps-configurator wizard

# Install with specific profile
sudo vps-configurator install --profile beginner

# Install with custom configuration
sudo vps-configurator install --config myconfig.yaml

# Verify installation
sudo vps-configurator verify

# Rollback changes
sudo vps-configurator rollback

# List available profiles
vps-configurator profiles
```

### Connecting via Remote Desktop

After installation, connect to your VPS using any RDP client:

**Windows:**
1. Open Remote Desktop Connection
2. Enter your server IP and port 3389
3. Login with your Linux credentials

**Mac:**
1. Install Microsoft Remote Desktop from App Store
2. Add a new PC with your server IP
3. Login with your Linux credentials

**Linux:**
```bash
remmina -c rdp://YOUR_SERVER_IP
# or
rdesktop YOUR_SERVER_IP
```

## 🔧 Configuration

Create a custom configuration file in YAML format:

```yaml
# myconfig.yaml
system:
  hostname: my-workstation
  timezone: America/New_York

languages:
  python:
    enabled: true
  nodejs:
    enabled: true
  golang:
    enabled: false

tools:
  docker:
    enabled: true
  editors:
    vscode:
      enabled: true
    cursor:
      enabled: false
```

Then run:
```bash
sudo vps-configurator install --config myconfig.yaml -y
```

## 🔒 Security

This configurator implements security best practices:

- **UFW Firewall**: Only necessary ports are open (SSH, RDP)
- **Fail2ban**: Protects against brute-force attacks
- **SSH Hardening**: Secure configuration, rate limiting
- **Automatic Updates**: Security patches applied automatically

> ⚠️ **Note**: Security module is MANDATORY and cannot be disabled.

## 📖 Documentation

- [Installation Guide](docs/installation/step-by-step.md)
- [Configuration Reference](docs/configuration/overview.md)
- [Troubleshooting](docs/installation/troubleshooting.md)
- [FAQ](docs/community/faq.md)

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) first.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📖 [Documentation](https://github.com/youruser/debian-vps-configurator/wiki)
- 💬 [Discussions](https://github.com/youruser/debian-vps-configurator/discussions)
- 🐛 [Report Issues](https://github.com/youruser/debian-vps-configurator/issues)

---

Made with ❤️ for developers who want a powerful remote coding environment.
