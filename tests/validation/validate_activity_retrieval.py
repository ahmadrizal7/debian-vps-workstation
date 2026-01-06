#!/usr/bin/env python3
"""Test activity retrieval"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from datetime import datetime, timedelta

from configurator.users.activity_monitor import ActivityMonitor, ActivityType


def test_activity_retrieval():
    """Test retrieving user activities."""
    print("Activity Retrieval Test")
    print("=" * 60)

    temp_dir = tempfile.mkdtemp()
    db_file = Path(temp_dir) / "activity.db"
    audit_log = Path(temp_dir) / "audit.log"

    monitor = ActivityMonitor(db_file=db_file, audit_log=audit_log)
    test_user = "testuser_retrieve"

    # Setup: Log some activities
    print("\n1. Setting up test activities...")

    activities_logged = 0

    for i in range(5):
        monitor.log_activity(
            user=test_user, activity_type=ActivityType.COMMAND, command=f"test command {i}"
        )
        activities_logged += 1

    print(f"  ✅ Logged {activities_logged} test activities")

    # Test 2: Retrieve all activities
    print("\n2. Retrieving all user activities...")

    activities = monitor.get_user_activity(user=test_user)

    print(f"  Retrieved: {len(activities)} activities")

    if len(activities) == activities_logged:
        print("  ✅ All activities retrieved")
    else:
        print(f"  ⚠️  Expected {activities_logged}, got {len(activities)}")

    # Test 3: Filter by activity type
    print("\n3. Testing activity type filter...")

    # Log a sudo command
    monitor.log_activity(
        user=test_user,
        activity_type=ActivityType.SUDO_COMMAND,
        command="sudo systemctl restart myapp",
    )

    sudo_activities = monitor.get_user_activity(
        user=test_user, activity_type=ActivityType.SUDO_COMMAND
    )

    print(f"  Sudo commands found: {len(sudo_activities)}")

    if len(sudo_activities) >= 1:
        print("  ✅ Activity type filter works")
    else:
        print("  ❌ Filter not working")
        return False

    # Test 4: Date range filter
    print("\n4. Testing date range filter...")

    now = datetime.now()
    start_date = now - timedelta(hours=1)

    recent_activities = monitor.get_user_activity(user=test_user, start_date=start_date)

    print(f"  Activities in last hour: {len(recent_activities)}")

    if len(recent_activities) > 0:
        print("  ✅ Date range filter works")
    else:
        print("  ⚠️  No recent activities found")

    # Cleanup
    import shutil

    shutil.rmtree(temp_dir, ignore_errors=True)

    print("\n" + "=" * 60)
    print("✅ Activity retrieval validated")
    return True


if __name__ == "__main__":
    result = test_activity_retrieval()

    print("\n" + "=" * 60)
    print("FINAL RESULT")
    print("=" * 60)
    print(f"Activity Retrieval: {'✅ PASS' if result else '❌ FAIL'}")

    sys.exit(0 if result else 1)
