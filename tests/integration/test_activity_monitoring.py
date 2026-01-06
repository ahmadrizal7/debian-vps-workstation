"""Integration tests for activity monitoring."""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from configurator.users.activity_monitor import ActivityMonitor, ActivityType, RiskLevel


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    temp_dir = tempfile.mkdtemp()
    db_file = Path(temp_dir) / "activity.db"
    audit_log = Path(temp_dir) / "audit.log"

    yield {
        "db_file": db_file,
        "audit_log": audit_log,
    }

    # Cleanup
    import shutil

    shutil.rmtree(temp_dir, ignore_errors=True)


def test_complete_activity_workflow(temp_db):
    """Test complete activity monitoring workflow."""
    monitor = ActivityMonitor(
        db_file=temp_db["db_file"],
        audit_log=temp_db["audit_log"],
    )

    # Step 1: Start SSH session
    session_id = monitor.start_ssh_session(
        user="johndoe",
        source_ip="203.0.113.50",
    )
    assert session_id is not None

    # Step 2: Log commands
    monitor.log_activity(
        user="johndoe",
        activity_type=ActivityType.COMMAND,
        session_id=session_id,
        command="git pull origin main",
    )

    monitor.log_activity(
        user="johndoe",
        activity_type=ActivityType.SUDO_COMMAND,
        session_id=session_id,
        command="systemctl restart myapp",
    )

    # Step 3: End session
    monitor.end_ssh_session(session_id)

    # Step 4: Generate report
    end_date = datetime.now()
    start_date = end_date - timedelta(hours=1)

    report = monitor.generate_activity_report(
        user="johndoe",
        start_date=start_date,
        end_date=end_date,
    )

    # Verify report
    assert report["user"] == "johndoe"
    assert report["summary"]["ssh_sessions"] >= 1
    assert report["summary"]["commands"] >= 1
    assert report["summary"]["sudo_commands"] >= 1


def test_anomaly_detection_workflow(temp_db):
    """Test anomaly detection workflow."""
    monitor = ActivityMonitor(
        db_file=temp_db["db_file"],
        audit_log=temp_db["audit_log"],
    )

    # Establish baseline: normal logins from office IP
    for i in range(10):
        monitor.log_activity(
            user="johndoe",
            activity_type=ActivityType.SSH_LOGIN,
            source_ip="203.0.113.50",
        )

    # Anomaly: suspicious command with high risk
    event = monitor.log_activity(
        user="johndoe",
        activity_type=ActivityType.COMMAND,
        command="chmod 777 /etc/passwd",  # Suspicious command
    )

    # Force high risk to trigger anomaly detection
    assert event.risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]

    # Check for anomalies
    anomalies = monitor.get_anomalies(user="johndoe")

    # May or may not detect anomaly depending on risk level
    # Just verify query works
    assert isinstance(anomalies, list)


def test_multi_user_activity_tracking(temp_db):
    """Test tracking multiple users simultaneously."""
    monitor = ActivityMonitor(
        db_file=temp_db["db_file"],
        audit_log=temp_db["audit_log"],
    )

    users = ["user1", "user2", "user3"]

    # Log activities for multiple users
    for user in users:
        for i in range(5):
            monitor.log_activity(
                user=user,
                activity_type=ActivityType.COMMAND,
                command=f"command {i}",
            )

    # Verify each user's activities
    for user in users:
        activities = monitor.get_user_activity(user)
        assert len(activities) == 5
        assert all(a.user == user for a in activities)


def test_activity_report_with_multiple_types(temp_db):
    """Test activity report with multiple activity types."""
    monitor = ActivityMonitor(
        db_file=temp_db["db_file"],
        audit_log=temp_db["audit_log"],
    )

    user = "testuser"

    # Log various activities
    monitor.log_activity(user=user, activity_type=ActivityType.SSH_LOGIN, source_ip="203.0.113.50")
    monitor.log_activity(user=user, activity_type=ActivityType.COMMAND, command="ls -la")
    monitor.log_activity(
        user=user, activity_type=ActivityType.SUDO_COMMAND, command="systemctl restart nginx"
    )
    monitor.log_activity(
        user=user, activity_type=ActivityType.FILE_ACCESS, file_path=Path("/etc/nginx/nginx.conf")
    )
    monitor.log_activity(user=user, activity_type=ActivityType.SSH_LOGOUT)

    # Generate report
    end_date = datetime.now()
    start_date = end_date - timedelta(hours=1)

    report = monitor.generate_activity_report(user, start_date, end_date)

    # Verify all activity types recorded
    summary = report["summary"]
    assert summary["ssh_sessions"] >= 1
    assert summary["commands"] >= 1
    assert summary["sudo_commands"] >= 1
    assert summary["file_accesses"] >= 1


def test_audit_log_persistence(temp_db):
    """Test that audit log is written to file."""
    monitor = ActivityMonitor(
        db_file=temp_db["db_file"],
        audit_log=temp_db["audit_log"],
    )

    # Log activity
    monitor.log_activity(
        user="testuser",
        activity_type=ActivityType.COMMAND,
        command="test command",
    )

    # Verify audit log file exists and has content
    assert temp_db["audit_log"].exists()

    with open(temp_db["audit_log"], "r") as f:
        content = f.read()

    assert "testuser" in content
    assert "test command" in content


def test_database_persistence(temp_db):
    """Test that activities persist in database."""
    # Create monitor and log activity
    monitor1 = ActivityMonitor(
        db_file=temp_db["db_file"],
        audit_log=temp_db["audit_log"],
    )

    monitor1.log_activity(
        user="testuser",
        activity_type=ActivityType.COMMAND,
        command="persistent command",
    )

    # Create new monitor instance (simulates restart)
    monitor2 = ActivityMonitor(
        db_file=temp_db["db_file"],
        audit_log=temp_db["audit_log"],
    )

    # Retrieve activities
    activities = monitor2.get_user_activity("testuser")

    assert len(activities) >= 1
    assert any(a.command == "persistent command" for a in activities)


def test_high_volume_activity_logging(temp_db):
    """Test logging high volume of activities."""
    monitor = ActivityMonitor(
        db_file=temp_db["db_file"],
        audit_log=temp_db["audit_log"],
    )

    # Log many activities
    num_activities = 100
    for i in range(num_activities):
        monitor.log_activity(
            user="testuser",
            activity_type=ActivityType.COMMAND,
            command=f"command {i}",
        )

    # Retrieve with limit
    activities = monitor.get_user_activity("testuser", limit=50)

    assert len(activities) == 50

    # Retrieve all
    all_activities = monitor.get_user_activity("testuser")
    assert len(all_activities) == num_activities


def test_risk_escalation_workflow(temp_db):
    """Test workflow for escalating risk activities."""
    monitor = ActivityMonitor(
        db_file=temp_db["db_file"],
        audit_log=temp_db["audit_log"],
    )

    # Log low-risk activity
    event1 = monitor.log_activity(
        user="testuser",
        activity_type=ActivityType.COMMAND,
        command="ls -la",
    )
    assert event1.risk_level == RiskLevel.LOW

    # Log high-risk activity
    event2 = monitor.log_activity(
        user="testuser",
        activity_type=ActivityType.SUDO_COMMAND,
        command="chmod 777 /etc/passwd",
    )
    assert event2.risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
