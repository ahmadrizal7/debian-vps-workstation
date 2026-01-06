#!/usr/bin/env python3
"""Validate RBAC file structure"""

import sys
from pathlib import Path


def validate_structure():
    print("RBAC File Structure Validation")
    print("=" * 60)

    base = Path("/home/racoon/AgentMemorh/debian-vps-workstation")

    files = {
        "configurator/rbac/__init__.py": False,
        "configurator/rbac/rbac_manager.py": False,
        "configurator/rbac/roles.yaml": False,
        "configurator/rbac/permissions.py": False,
        "tests/unit/test_rbac.py": False,
        "tests/integration/test_rbac_integration.py": False,
    }

    for file, _ in files.items():
        path = base / file
        files[file] = path.exists()
        status = "✅" if files[file] else "❌"
        print(f"{status} {file}")

    passed = sum(files.values())
    total = len(files)

    print(f"\n{passed}/{total} files exist")
    return passed == total


if __name__ == "__main__":
    sys.exit(0 if validate_structure() else 1)
