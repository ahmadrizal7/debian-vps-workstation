#!/bin/bash
#####################################################################
# Server-Side Deployment Script with Circuit Breaker
#
# This script should be run ON THE REMOTE SERVER after transferring
# the codebase. It sets up the environment and runs the installation
# through the circuit breaker monitor.
#
# Usage:
#   1. Transfer this script and the codebase to the server
#   2. Run: bash deploy_on_server.sh
#####################################################################

set -euo pipefail

REPO_DIR="${1:-/root/debian-vps-workstation}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================="
echo "Server-Side Deployment Script"
echo "=========================================="
echo "Repository: $REPO_DIR"
echo ""

# Check if we're in the right directory or repo exists
if [ ! -d "$REPO_DIR" ]; then
    echo "❌ Repository directory not found: $REPO_DIR"
    echo "Please ensure the codebase has been transferred to the server."
    exit 1
fi

cd "$REPO_DIR" || exit 1

# Ensure circuit breaker script exists
MONITOR_SCRIPT="$REPO_DIR/tools/monitor_install_with_checkpoint.py"
if [ ! -f "$MONITOR_SCRIPT" ]; then
    echo "❌ Circuit breaker script not found: $MONITOR_SCRIPT"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

# Create venv if missing
if [ ! -d ".venv" ]; then
    echo "--- Creating virtual environment ---"
    python3 -m venv .venv
fi

# Activate venv and install dependencies
echo "--- Installing/Updating dependencies ---"
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -e .

# Clear any apt locks
echo "--- Clearing apt locks ---"
sudo killall apt apt-get dpkg 2>/dev/null || true
sudo rm -f /var/lib/apt/lists/lock /var/cache/apt/archives/lock /var/lib/dpkg/lock*
sudo dpkg --configure -a 2>/dev/null || true

# Run installation through circuit breaker
echo ""
echo "=========================================="
echo "Starting Installation with Circuit Breaker"
echo "=========================================="
echo "MONITORING MODE: Will halt on ERROR, WARNING, SKIP, or TIMEOUT"
echo ""

INSTALL_CMD="cd $REPO_DIR && .venv/bin/python3 -m configurator --verbose install --profile advanced --no-parallel"
MONITOR_CMD="python3 $MONITOR_SCRIPT \"$INSTALL_CMD\""

if eval "$MONITOR_CMD"; then
    echo ""
    echo "✅ Installation completed successfully!"
    exit 0
else
    echo ""
    echo "❌ Installation failed or was halted by circuit breaker"
    echo ""
    echo "Check the logs:"
    echo "  - Monitor log: /tmp/monitor_install.log"
    echo "  - Checkpoint: /tmp/vps-checkpoint-*"
    exit 1
fi
