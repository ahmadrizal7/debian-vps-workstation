"""Integration tests for user lifecycle management."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from configurator.users.lifecycle_manager import LifecycleEvent, UserLifecycleManager, UserStatus


@pytest.fixture
def temp_dirs():
    """Create temporary directories for testing."""
    temp_dir = tempfile.mkdtemp()
    registry_file = Path(temp_dir) / "registry.json"
    archive_dir = Path(temp_dir) / "archives"
    audit_log = Path(temp_dir) / "audit.log"

    yield {
        "temp_dir": temp_dir,
        "registry_file": registry_file,
        "archive_dir": archive_dir,
        "audit_log": audit_log,
    }

    # Cleanup
    import shutil

    shutil.rmtree(temp_dir, ignore_errors=True)


def test_complete_user_lifecycle(temp_dirs):
    """Test complete user lifecycle from creation to offboarding."""
    lifecycle = UserLifecycleManager(
        registry_file=temp_dirs["registry_file"],
        archive_dir=temp_dirs["archive_dir"],
        audit_log=temp_dirs["audit_log"],
        dry_run=True,
    )

    with patch("subprocess.run"):
        with patch("pwd.getpwnam") as mock_getpwnam:
            mock_pwd = MagicMock()
            mock_pwd.pw_uid = 1001
            mock_pwd.pw_gid = 1001
            mock_pwd.pw_dir = "/home/johndoe"
            mock_getpwnam.return_value = mock_pwd

            # Step 1: Create user
            profile = lifecycle.create_user(
                username="johndoe",
                full_name="John Doe",
                email="johndoe@example.com",
                role="developer",
                created_by="admin",
                department="Engineering",
                manager="janedoe",
            )

            assert profile.username == "johndoe"
            assert profile.status == UserStatus.ACTIVE
            assert profile.department == "Engineering"
            assert profile.manager == "janedoe"

            # Step 2: Update role
            lifecycle.update_user_role("johndoe", "devops", "admin")
            profile = lifecycle.get_user_profile("johndoe")
            assert profile.role == "devops"

            # Step 3: Suspend user
            lifecycle.suspend_user("johndoe", "Policy violation", "admin")
            profile = lifecycle.get_user_profile("johndoe")
            assert profile.status == UserStatus.SUSPENDED

            # Step 4: Reactivate user
            lifecycle.reactivate_user("johndoe", "admin")
            profile = lifecycle.get_user_profile("johndoe")
            assert profile.status == UserStatus.ACTIVE

            # Step 5: Offboard user
            lifecycle.offboard_user(
                username="johndoe",
                reason="Employment ended",
                offboarded_by="admin",
                archive_data=False,
            )

            profile = lifecycle.get_user_profile("johndoe")
            assert profile.status == UserStatus.OFFBOARDED
            assert profile.offboarding_reason == "Employment ended"


def test_user_lifecycle_with_rbac_integration(temp_dirs):
    """Test user lifecycle with RBAC integration."""
    lifecycle = UserLifecycleManager(
        registry_file=temp_dirs["registry_file"],
        archive_dir=temp_dirs["archive_dir"],
        audit_log=temp_dirs["audit_log"],
        dry_run=False,  # Disable dry_run for RBAC calls
    )

    # Mock RBAC manager
    mock_rbac = MagicMock()
    mock_rbac.get_role.return_value = MagicMock(system_groups=["developers", "docker"])
    mock_rbac.assignments = {}
    lifecycle.rbac_manager = mock_rbac

    with patch("subprocess.run"):
        with patch("subprocess.Popen") as mock_popen:
            mock_proc = MagicMock()
            mock_proc.communicate.return_value = ("", "")
            mock_popen.return_value = mock_proc

            with patch("pwd.getpwnam") as mock_getpwnam:
                mock_pwd = MagicMock()
                mock_pwd.pw_uid = 1001
                mock_pwd.pw_gid = 1001
                mock_pwd.pw_dir = "/home/testuser"
                mock_getpwnam.return_value = mock_pwd

                with patch("os.chown"):
                    with patch("grp.getgrnam"):  # Mock group lookup
                        with patch(
                            "pathlib.Path.exists", return_value=False
                        ):  # Mock sudoers file check
                            # Create user with RBAC role
                            profile = lifecycle.create_user(
                                username="testuser",
                                full_name="Test User",
                                email="test@example.com",
                                role="developer",
                            )

                            # Verify RBAC integration
                            mock_rbac.assign_role.assert_called_once()

                            # Change role
                            lifecycle.update_user_role("testuser", "devops", "admin")

                            # Offboard and verify RBAC cleanup
                            lifecycle.offboard_user("testuser", "Test", "admin", archive_data=False)

                            # Verify assignment was removed
                            assert "testuser" not in lifecycle.rbac_manager.assignments


def test_multiple_users_management(temp_dirs):
    """Test managing multiple users simultaneously."""
    lifecycle = UserLifecycleManager(
        registry_file=temp_dirs["registry_file"],
        archive_dir=temp_dirs["archive_dir"],
        audit_log=temp_dirs["audit_log"],
        dry_run=True,
    )

    with patch("subprocess.run"):
        with patch("pwd.getpwnam") as mock_getpwnam:
            mock_pwd = MagicMock()

            # Create 5 users
            for i in range(5):
                mock_pwd.pw_uid = 1000 + i
                mock_pwd.pw_gid = 1000 + i
                mock_pwd.pw_dir = f"/home/user{i}"

                lifecycle.create_user(
                    username=f"user{i}",
                    full_name=f"User {i}",
                    email=f"user{i}@example.com",
                    role="developer" if i % 2 == 0 else "viewer",
                )

            # List all users
            users = lifecycle.list_users()
            assert len(users) == 5

            # Suspend some users
            lifecycle.suspend_user("user0", "Test", "admin")
            lifecycle.suspend_user("user2", "Test", "admin")

            # List suspended users
            suspended = lifecycle.list_users(status=UserStatus.SUSPENDED)
            assert len(suspended) == 2

            # List active users
            active = lifecycle.list_users(status=UserStatus.ACTIVE)
            assert len(active) == 3


def test_audit_trail_completeness(temp_dirs):
    """Test that all lifecycle events are logged."""
    lifecycle = UserLifecycleManager(
        registry_file=temp_dirs["registry_file"],
        archive_dir=temp_dirs["archive_dir"],
        audit_log=temp_dirs["audit_log"],
        dry_run=True,
    )

    with patch("subprocess.run"):
        with patch("pwd.getpwnam") as mock_getpwnam:
            mock_pwd = MagicMock()
            mock_pwd.pw_uid = 1001
            mock_pwd.pw_gid = 1001
            mock_pwd.pw_dir = "/home/testuser"
            mock_getpwnam.return_value = mock_pwd

            # Perform various lifecycle operations
            lifecycle.create_user(
                username="testuser",
                full_name="Test User",
                email="test@example.com",
                role="developer",
            )

            lifecycle.update_user_role("testuser", "devops", "admin")
            lifecycle.suspend_user("testuser", "Test", "admin")
            lifecycle.reactivate_user("testuser", "admin")
            lifecycle.offboard_user("testuser", "Test", "admin", archive_data=False)

            # Read audit log
            with open(temp_dirs["audit_log"], "r") as f:
                lines = f.readlines()

            # Verify all events logged
            events = [json.loads(line)["event"] for line in lines]

            assert LifecycleEvent.CREATED.value in events
            assert LifecycleEvent.ROLE_CHANGED.value in events
            assert LifecycleEvent.SUSPENDED.value in events
            assert LifecycleEvent.REACTIVATED.value in events
            assert LifecycleEvent.OFFBOARDED.value in events


def test_registry_persistence_across_instances(temp_dirs):
    """Test that registry persists across manager instances."""
    # Create first instance and add user
    lifecycle1 = UserLifecycleManager(
        registry_file=temp_dirs["registry_file"],
        archive_dir=temp_dirs["archive_dir"],
        audit_log=temp_dirs["audit_log"],
        dry_run=True,
    )

    with patch("subprocess.run"):
        with patch("pwd.getpwnam") as mock_getpwnam:
            mock_pwd = MagicMock()
            mock_pwd.pw_uid = 1001
            mock_pwd.pw_gid = 1001
            mock_pwd.pw_dir = "/home/testuser"
            mock_getpwnam.return_value = mock_pwd

            lifecycle1.create_user(
                username="testuser",
                full_name="Test User",
                email="test@example.com",
                role="developer",
            )

    # Create second instance and verify user exists
    lifecycle2 = UserLifecycleManager(
        registry_file=temp_dirs["registry_file"],
        archive_dir=temp_dirs["archive_dir"],
        audit_log=temp_dirs["audit_log"],
        dry_run=True,
    )

    profile = lifecycle2.get_user_profile("testuser")
    assert profile is not None
    assert profile.username == "testuser"
    assert profile.full_name == "Test User"


def test_user_with_all_optional_features(temp_dirs):
    """Test user creation with all optional features enabled."""
    lifecycle = UserLifecycleManager(
        registry_file=temp_dirs["registry_file"],
        archive_dir=temp_dirs["archive_dir"],
        audit_log=temp_dirs["audit_log"],
        dry_run=True,
    )

    with patch("subprocess.run"):
        with patch("pwd.getpwnam") as mock_getpwnam:
            mock_pwd = MagicMock()
            mock_pwd.pw_uid = 1001
            mock_pwd.pw_gid = 1001
            mock_pwd.pw_dir = "/home/testuser"
            mock_getpwnam.return_value = mock_pwd

            profile = lifecycle.create_user(
                username="testuser",
                full_name="Test User",
                email="test@example.com",
                role="developer",
                department="Engineering",
                manager="boss",
                shell="/bin/zsh",
                enable_ssh_key=True,
                enable_2fa=True,
                generate_temp_password=True,
            )

            assert profile.username == "testuser"
            assert profile.department == "Engineering"
            assert profile.manager == "boss"
            assert profile.shell == "/bin/zsh"
            assert profile.ssh_keys_enabled is True
            assert profile.mfa_enabled is True
            assert profile.status == UserStatus.PENDING  # Pending due to 2FA


def test_user_status_transitions(temp_dirs):
    """Test valid user status transitions."""
    lifecycle = UserLifecycleManager(
        registry_file=temp_dirs["registry_file"],
        archive_dir=temp_dirs["archive_dir"],
        audit_log=temp_dirs["audit_log"],
        dry_run=True,
    )

    with patch("subprocess.run"):
        with patch("pwd.getpwnam") as mock_getpwnam:
            mock_pwd = MagicMock()
            mock_pwd.pw_uid = 1001
            mock_pwd.pw_gid = 1001
            mock_pwd.pw_dir = "/home/testuser"
            mock_getpwnam.return_value = mock_pwd

            # Create user (ACTIVE)
            profile = lifecycle.create_user(
                username="testuser",
                full_name="Test User",
                email="test@example.com",
                role="developer",
            )
            assert profile.status == UserStatus.ACTIVE

            # Suspend (ACTIVE -> SUSPENDED)
            lifecycle.suspend_user("testuser", "Test", "admin")
            profile = lifecycle.get_user_profile("testuser")
            assert profile.status == UserStatus.SUSPENDED

            # Reactivate (SUSPENDED -> ACTIVE)
            lifecycle.reactivate_user("testuser", "admin")
            profile = lifecycle.get_user_profile("testuser")
            assert profile.status == UserStatus.ACTIVE

            # Offboard (ACTIVE -> OFFBOARDED)
            lifecycle.offboard_user("testuser", "Test", "admin", archive_data=False)
            profile = lifecycle.get_user_profile("testuser")
            assert profile.status == UserStatus.OFFBOARDED
