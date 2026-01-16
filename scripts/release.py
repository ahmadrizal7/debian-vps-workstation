#!/usr/bin/env python3
"""
Release automation script.
Automates the build and release process.
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def log(msg, color=RESET):
    print(f"{color}{msg}{RESET}")


def run_command(cmd, cwd=None, capture=False):
    """Run a shell command."""
    log(f"Running: {' '.join(cmd)}", YELLOW)
    result = subprocess.run(cmd, cwd=cwd, capture_output=capture, text=True, check=False)
    if result.returncode != 0:
        log(f"Error running command: {' '.join(cmd)}", RED)
        if capture:
            log(result.stderr, RED)
        sys.exit(1)
    return result.stdout


def clean_build():
    """Clean build artifacts."""
    log("Cleaning build artifacts...", GREEN)
    for path in ["dist", "build", "debian_vps_configurator.egg-info"]:
        if os.path.exists(path):
            shutil.rmtree(path)
    log("Clean complete.", GREEN)


def run_tests():
    """Run test suite."""
    log("Running tests...", GREEN)
    run_command([sys.executable, "-m", "pytest", "tests/", "-v"])
    log("Tests passed.", GREEN)


def build_package():
    """Build distribution packages."""
    log("Building packages...", GREEN)
    run_command([sys.executable, "-m", "build"])
    log("Build complete.", GREEN)


def verify_version(version):
    """Verify version matches in all files."""
    log(f"Verifying version {version}...", GREEN)

    # 1. Check __version__.py
    version_file = Path("configurator/__version__.py").read_text()
    if f'__version__ = "{version}"' not in version_file:
        log(f"❌ Version in __version__.py does not match {version}", RED)
        sys.exit(1)

    # 2. Check setup.py
    # setup_py = Path("setup.py").read_text()
    # if f'version="{version}"' not in setup_py and f"version='{version}'" not in setup_py:
    #     log("❌ Version in setup.py does not match", RED)
    #     sys.exit(1)

    log("Version verification passed.", GREEN)


def check_changelog(version):
    """Check if version is in changelog."""
    log("Checking changelog...", GREEN)
    changelog = Path("CHANGELOG.md").read_text()
    if f"[{version}]" not in changelog:
        log(f"❌ Version {version} not found in CHANGELOG.md", RED)
        sys.exit(1)
    log("Changelog check passed.", GREEN)


def main():
    parser = argparse.ArgumentParser(description="Release automation")
    parser.add_argument("--version", required=True, help="Version to release (e.g. 2.0.0)")
    parser.add_argument("--skip-tests", action="store_true", help="Skip running tests")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually tag/push")

    args = parser.parse_args()
    version = args.version

    log(f"🚀 Starting release process for v{version}", GREEN)

    # Prerelease checks
    verify_version(version)
    check_changelog(version)

    if not args.skip_tests:
        run_tests()

    clean_build()
    build_package()

    # Check artifacts
    dist = Path("dist")
    files = list(dist.glob("*"))
    if not files:
        log("❌ No artifacts generated!", RED)
        sys.exit(1)

    log(f"✅ Generated {len(files)} artifacts:", GREEN)
    for f in files:
        print(f"  - {f.name}")

    if not args.dry_run:
        log("\nTo complete the release:", YELLOW)
        log(f"1. git tag -a v{version} -m 'Release v{version}'")
        log(f"2. git push origin v{version}")
        log("3. twine upload dist/*")

    log("\n✨ Release preparation complete!", GREEN)


if __name__ == "__main__":
    main()
