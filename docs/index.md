# Debian VPS Workstation Configurator

Transform your fresh Debian 13 VPS into a fully-featured remote development workstation in minutes.

[![Tests](https://github.com/ahmadrizal7/debian-vps-workstation/actions/workflows/tests.yml/badge.svg)](https://github.com/ahmadrizal7/debian-vps-workstation/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

## 🚀 Features

- **Remote Desktop**: XFCE via XRDP (Microsoft Remote Desktop compatible)
- **Developer Tools**: Python, Node.js, Docker, Git, VS Code, and more
- **Security Hardening**: UFW firewall, Fail2ban, SSH key setup
- **Templates**: "Beginner", "Fullstack", and custom profiles
- **Modular**: Install only what you need
- **Interactive**: Easy-to-use wizard interface

## 🏁 Quick Start

```bash
# SSH into your VPS
ssh root@your-vps-ip

# Run the quick install script
curl -sSL https://raw.githubusercontent.com/ahmadrizal7/debian-vps-workstation/main/quick-install.sh | bash

# Run the wizard
vps-configurator wizard
```

[Get Started Now →](user-guide/getting-started.md){ .md-button .md-button--primary }

## 📚 Documentation

- [User Guide](user-guide/getting-started.md) - Installation and usage instructions
- [CLI Reference](user-guide/cli-reference.md) - Command line options
- [Developer Guide](developer-guide/architecture.md) - Architecture and contributing
- [FAQ](user-guide/faq.md) - Common questions and answers

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](developer-guide/architecture.md) for details.

## 📄 License

This project is licensed under the MIT License.
