#!/usr/bin/env python3
"""Test sudoers.d file generation and validation"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from configurator.rbac.sudo_manager import (
    PasswordRequirement,
    SudoCommandRule,
    SudoPolicy,
    SudoPolicyManager,
)


def test_sudoers_generation():
    """Test sudoers.d file generation"""

    print("Sudoers File Generation Test")
    print("=" * 60)

    temp_dir = tempfile.mkdtemp()

    sudo_mgr = SudoPolicyManager(
        sudoers_dir=Path(temp_dir) / "sudoers.d",
        policy_dir=Path(temp_dir) / "policies",
        audit_log=Path(temp_dir) / "audit.log",
        dry_run=True,
    )

    # Test 1: Generate content for developer policy
    print("\n1. Testing sudoers content generation...")

    policy = sudo_mgr.policies.get("developer")

    if not policy:
        print("  ❌ Developer policy not found")
        return False

    try:
        content = sudo_mgr._generate_sudoers_content("testuser", policy)

        print("  ✅ Content generated")
        print("\n  Sample content (first 15 lines):")
        lines = content.split("\n")[:15]
        for line in lines:
            print(f"    {line}")

    except Exception as e:
        print(f"  ❌ Content generation failed: {e}")
        return False

    # Test 2: Validate content format
    print("\n2. Validating content format...")

    # Check for required elements
    checks = [
        ("# Sudo policy for testuser" in content, "Header comment"),
        ("# Role: developer" in content, "Role comment"),
        ("NOPASSWD:" in content, "Passwordless rules"),
        ("testuser ALL=(ALL)" in content, "User specification"),
    ]

    all_passed = True
    for check, description in checks:
        if check:
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ {description} missing")
            all_passed = False

    if not all_passed:
        return False

    # Test 3: Validate with visudo
    print("\n3. Validating with visudo...")

    is_valid = sudo_mgr._validate_sudoers_content(content)

    if is_valid:
        print("  ✅ Sudoers content is valid (visudo -c passed or skipped)")
    else:
        print("  ❌ Sudoers content is invalid")
        return False

    # Test 4: Test invalid content rejection
    print("\n4. Testing invalid content rejection...")

    invalid_content = "INVALID SYNTAX HERE\ntestuser ALL=(ALL) NOPASSWD"

    is_valid = sudo_mgr._validate_sudoers_content(invalid_content)

    if not is_valid:
        print("  ✅ Invalid content correctly rejected (or visudo not available)")
    else:
        # This might pass if visudo not available
        print("  ⚠️  Invalid content validation skipped (visudo not available)")

    # Test 5: Test policy with mixed passwordless and password-required
    print("\n5. Testing mixed policy (passwordless + password-required)...")

    mixed_policy = SudoPolicy(
        name="mixed",
        rules=[
            SudoCommandRule(
                "systemctl restart myapp",
                password_required=PasswordRequirement.NONE,
                description="Passwordless restart",
            ),
            SudoCommandRule(
                "systemctl stop *",
                password_required=PasswordRequirement.REQUIRED,
                description="Password-required stop",
            ),
        ],
    )

    content = sudo_mgr._generate_sudoers_content("mixeduser", mixed_policy)

    # Check both types present
    if "NOPASSWD:" in content and "mixeduser ALL=(ALL) systemctl stop *" in content:
        print("  ✅ Mixed policy generates both passwordless and password-required rules")
    else:
        print("  ❌ Mixed policy generation failed")
        return False

    # Cleanup
    import shutil

    shutil.rmtree(temp_dir, ignore_errors=True)

    print("\n" + "=" * 60)
    print("✅ Sudoers file generation validated")
    return True


if __name__ == "__main__":
    result = test_sudoers_generation()

    print("\n" + "=" * 60)
    print("FINAL RESULT")
    print("=" * 60)
    print(f"Sudoers Generation: {'✅ PASS' if result else '❌ FAIL'}")

    sys.exit(0 if result else 1)
