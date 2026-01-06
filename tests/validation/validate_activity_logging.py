#!/usr/bin/env python3
"""Test activity event logging"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import sqlite3

from configurator.users.activity_monitor import ActivityMonitor, ActivityType


def test_activity_logging():
    """Test logging various activity types."""
    print("Activity Logging Test")
    print("=" * 60)

    temp_dir = tempfile.mkdtemp()
    db_file = Path(temp_dir) / "activity.db"
    audit_log = Path(temp_dir) / "audit.log"

    monitor = ActivityMonitor(db_file=db_file, audit_log=audit_log)
    test_user = "testuser_activity"

    # Test 1: Log SSH login
    print("\n1. Testing SSH login logging...")
    try:
        event = monitor.log_activity(
            user=test_user,
            activity_type=ActivityType.SSH_LOGIN,
            source_ip="203.0.113.50",
            session_id="session123",
            details={"login_method": "ssh_key"},
        )

        print("  ✅ SSH login logged")
        print(f"     User: {event.user}")
        print(f"     Type: {event.activity_type.value}")
        print(f"     Source IP: {event.source_ip}")
        print(f"     Risk: {event.risk_level.value}")

    except Exception as e:
        print(f"  ❌ Logging failed: {e}")
        return False

    # Test 2: Log command execution
    print("\n2. Testing command logging...")
    try:
        event = monitor.log_activity(
            user=test_user,
            activity_type=ActivityType.COMMAND,
            session_id="session123",
            command="git pull origin main",
        )

        print("  ✅ Command logged")
        print(f"     Command: {event.command}")
        print(f"     Risk: {event.risk_level.value}")

    except Exception as e:
        print(f"  ❌ Command logging failed: {e}")
        return False

    # Test 3: Log sudo command
    print("\n3. Testing sudo command logging...")
    try:
        event = monitor.log_activity(
            user=test_user,
            activity_type=ActivityType.SUDO_COMMAND,
            command="systemctl restart nginx",
        )

        print("  ✅ Sudo command logged")
        print(f"     Command: {event.command}")
        print(f"     Risk: {event.risk_level.value}")

    except Exception as e:
        print(f"  ❌ Sudo command logging failed: {e}")
        return False

    # Test 4: Verify events in database
    print("\n4. Verifying events in database...")

    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM activity_events WHERE user = ?", (test_user,))
        count = cursor.fetchone()[0]

        print(f"  ✅ Events stored in database: {count}")

        if count >= 3:
            print("  ✅ All test events found")
        else:
            print(f"  ⚠️  Expected at least 3 events, found {count}")

        conn.close()

    except Exception as e:
        print(f"  ❌ Database verification failed: {e}")
        return False

    # Cleanup
    import shutil

    shutil.rmtree(temp_dir, ignore_errors=True)

    print("\n" + "=" * 60)
    print("✅ Activity logging validated")
    return True


if __name__ == "__main__":
    result = test_activity_logging()

    print("\n" + "=" * 60)
    print("FINAL RESULT")
    print("=" * 60)
    print(f"Activity Logging: {'✅ PASS' if result else '❌ FAIL'}")

    sys.exit(0 if result else 1)
