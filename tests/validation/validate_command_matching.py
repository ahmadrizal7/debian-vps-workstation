#!/usr/bin/env python3
"""Test command pattern matching with wildcards"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from configurator.rbac.sudo_manager import PasswordRequirement, SudoCommandRule


def test_command_matching():
    """Test command pattern matching with wildcards"""

    print("Command Pattern Matching Test")
    print("=" * 60)

    # Test 1: Exact match
    print("\n1. Testing exact match...")
    rule = SudoCommandRule(
        command_pattern="systemctl restart myapp",
        password_required=PasswordRequirement.NONE,
    )

    if rule.matches_command("systemctl restart myapp"):
        print("  ✅ Exact match works")
    else:
        print("  ❌ Exact match failed")
        return False

    if not rule.matches_command("systemctl restart otherapp"):
        print("  ✅ Different command correctly rejected")
    else:
        print("  ❌ Should not match different command")
        return False

    # Test 2: Wildcard match (*)
    print("\n2. Testing wildcard match (systemctl restart *)...")
    rule = SudoCommandRule(
        command_pattern="systemctl restart *",
        password_required=PasswordRequirement.NONE,
    )

    test_commands = [
        ("systemctl restart myapp", True),
        ("systemctl restart nginx", True),
        ("systemctl restart anything", True),
        ("systemctl stop myapp", False),
        ("systemctl restart", False),
    ]

    for command, should_match in test_commands:
        matches = rule.matches_command(command)
        if matches == should_match:
            status = "✅" if should_match else "✅ (correctly rejected)"
            print(f"    {status} {command}")
        else:
            print(f"    ❌ {command} - expected {should_match}, got {matches}")
            return False

    # Test 3: Mid-pattern wildcard
    print("\n3. Testing mid-pattern wildcard (docker logs *)...")
    rule = SudoCommandRule(
        command_pattern="docker logs *",
        password_required=PasswordRequirement.NONE,
    )

    if rule.matches_command("docker logs container123"):
        print("  ✅ Mid-pattern wildcard works")
    else:
        print("  ❌ Mid-pattern wildcard failed")
        return False

    # Test 4: Full wildcard
    print("\n4. Testing full wildcard (*)...")
    rule = SudoCommandRule(
        command_pattern="*",
        password_required=PasswordRequirement.REQUIRED,
    )

    if rule.matches_command("any command here"):
        print("  ✅ Full wildcard works")
    else:
        print("  ❌ Full wildcard failed")
        return False

    # Test 5: Multiple wildcards
    print("\n5. Testing multiple wildcards (systemctl * *)...")
    rule = SudoCommandRule(
        command_pattern="systemctl * *",
        password_required=PasswordRequirement.NONE,
    )

    if rule.matches_command("systemctl restart nginx"):
        print("  ✅ Multiple wildcards work")
    else:
        print("  ❌ Multiple wildcards failed")
        return False

    print("\n" + "=" * 60)
    print("✅ Command pattern matching validated")
    return True


if __name__ == "__main__":
    result = test_command_matching()

    print("\n" + "=" * 60)
    print("FINAL RESULT")
    print("=" * 60)
    print(f"Command Matching: {'✅ PASS' if result else '❌ FAIL'}")

    sys.exit(0 if result else 1)
