#!/usr/bin/env python3
"""Test permission parsing and matching"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from configurator.rbac.rbac_manager import Permission


def test_permission_parsing():
    print("Permission Parsing Test")
    print("=" * 60)

    # Test 1: Basic permission
    print("\n1. Testing basic permission (app:myapp:deploy)...")
    try:
        perm = Permission("app:myapp:deploy")

        assert perm.scope == "app", f"Wrong scope: {perm.scope}"
        assert perm.resource == "myapp", f"Wrong resource: {perm.resource}"
        assert perm.action == "deploy", f"Wrong action: {perm.action}"

        print("  ✅ Basic permission parsed correctly")
        print(f"     Scope: {perm.scope}")
        print(f"     Resource: {perm.resource}")
        print(f"     Action: {perm.action}")
    except Exception as e:
        print(f"  ❌ Parsing failed: {e}")
        return False

    # Test 2: Wildcard permission
    print("\n2. Testing wildcard permission (app:*:read)...")
    try:
        perm = Permission("app:*:read")

        assert perm.scope == "app"
        assert perm.resource == "*"
        assert perm.action == "read"

        print("  ✅ Wildcard permission parsed correctly")
    except Exception as e:
        print(f"  ❌ Parsing failed: {e}")
        return False

    # Test 3: Scope-only permission
    print("\n3. Testing scope-only permission (system:*)...")
    try:
        perm = Permission("system:*")

        assert perm.scope == "system"
        assert perm.resource == "*"
        assert perm.action == "*"

        print("  ✅ Scope-only permission parsed correctly")
    except Exception as e:
        print(f"  ❌ Parsing failed: {e}")
        return False

    # Test 4: Invalid permission format
    print("\n4. Testing invalid permission format...")
    try:
        perm = Permission("invalid")
        print("  ❌ Should have raised ValueError")
        return False
    except ValueError:
        print("  ✅ Invalid format rejected correctly")

    print("\n" + "=" * 60)
    print("✅ Permission parsing validated")
    return True


def test_permission_matching():
    print("\n\nPermission Matching Test")
    print("=" * 60)

    # Test 1: Exact match
    print("\n1. Testing exact match...")
    granted = Permission("app:myapp:deploy")
    required = Permission("app:myapp:deploy")

    if granted.matches(required):
        print("  ✅ Exact match works")
    else:
        print("  ❌ Exact match failed")
        return False

    # Test 2: Wildcard resource match
    print("\n2. Testing wildcard resource (app:*:deploy)...")
    granted = Permission("app:*:deploy")
    required = Permission("app:myapp:deploy")

    if granted.matches(required):
        print("  ✅ Wildcard resource match works")
    else:
        print("  ❌ Wildcard resource match failed")
        return False

    # Test 3: Wildcard action match
    print("\n3. Testing wildcard action (app:myapp:*)...")
    granted = Permission("app:myapp:*")
    required = Permission("app:myapp:deploy")

    if granted.matches(required):
        print("  ✅ Wildcard action match works")
    else:
        print("  ❌ Wildcard action match failed")
        return False

    # Test 4: Full wildcard (system:*)
    print("\n4. Testing full wildcard (system:*)...")
    granted = Permission("system:*")
    required = Permission("system:infrastructure:restart")

    if granted.matches(required):
        print("  ✅ Full wildcard match works")
    else:
        print("  ❌ Full wildcard match failed")
        return False

    # Test 5: No match (different scope)
    print("\n5. Testing no match (different scope)...")
    granted = Permission("app:myapp:deploy")
    required = Permission("db:production:read")

    if not granted.matches(required):
        print("  ✅ Different scope correctly rejected")
    else:
        print("  ❌ Should not match different scope")
        return False

    # Test 6: No match (different action)
    print("\n6. Testing no match (different action)...")
    granted = Permission("app:myapp:read")
    required = Permission("app:myapp:write")

    if not granted.matches(required):
        print("  ✅ Different action correctly rejected")
    else:
        print("  ❌ Should not match different action")
        return False

    print("\n" + "=" * 60)
    print("✅ Permission matching validated")
    return True


if __name__ == "__main__":
    result1 = test_permission_parsing()
    result2 = test_permission_matching()
    sys.exit(0 if (result1 and result2) else 1)
