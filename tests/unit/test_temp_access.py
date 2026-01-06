"""Unit tests for temporary access management."""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from configurator.users.temp_access import (
    AccessStatus,
    AccessType,
    ExtensionRequest,
    ExtensionStatus,
    TempAccess,
    TempAccessManager,
)


@pytest.fixture
def temp_paths():
    """Create temporary paths for testing."""
    temp_dir = tempfile.mkdtemp()
    registry = Path(temp_dir) / "registry.json"
    extensions = Path(temp_dir) / "extensions.json"
    audit_log = Path(temp_dir) / "audit.log"

    yield {
        "registry": registry,
        "extensions": extensions,
        "audit_log": audit_log,
    }

    # Cleanup
    import shutil

    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_access_manager(temp_paths):
    """Create temp access manager with temp paths."""
    return TempAccessManager(
        registry_file=temp_paths["registry"],
        extensions_file=temp_paths["extensions"],
        audit_log=temp_paths["audit_log"],
    )


def test_temp_access_manager_initialization(temp_access_manager):
    """Test temp access manager initialization."""
    assert temp_access_manager is not None
    assert len(temp_access_manager.access_grants) == 0
    assert len(temp_access_manager.extensions) == 0


def test_grant_temp_access(temp_access_manager):
    """Test granting temporary access."""
    access = temp_access_manager.grant_temp_access(
        username="contractor-john",
        full_name="John Contractor",
        email="john@contractor.com",
        role="developer",
        duration_days=30,
        reason="Q1 project",
        skip_user_creation=True,
    )

    assert access is not None
    assert access.username == "contractor-john"
    assert access.role == "developer"
    assert access.status == AccessStatus.ACTIVE
    assert access.access_type == AccessType.TEMPORARY
    assert access.days_remaining() > 0


def test_grant_temp_access_with_custom_type(temp_access_manager):
    """Test granting emergency access."""
    access = temp_access_manager.grant_temp_access(
        username="emergency-admin",
        full_name="Emergency Admin",
        email="emergency@company.com",
        role="admin",
        duration_days=1,
        reason="Production incident",
        access_type=AccessType.EMERGENCY,
        skip_user_creation=True,
    )

    assert access.access_type == AccessType.EMERGENCY


def test_access_expiration_check(temp_access_manager):
    """Test checking if access is expired."""
    # Create expired access
    access = TempAccess(
        access_id="TEST-001",
        username="testuser",
        access_type=AccessType.TEMPORARY,
        granted_at=datetime.now() - timedelta(days=31),
        expires_at=datetime.now() - timedelta(days=1),
        role="developer",
        reason="Test",
    )

    assert access.is_expired()
    assert access.days_remaining() == 0


def test_access_not_expired(temp_access_manager):
    """Test access that is not expired."""
    access = temp_access_manager.grant_temp_access(
        username="activeuser",
        full_name="Active User",
        email="active@company.com",
        role="developer",
        duration_days=30,
        reason="Active project",
        skip_user_creation=True,
    )

    assert not access.is_expired()
    assert access.days_remaining() > 0


def test_check_expired_access(temp_access_manager):
    """Test checking for expired access."""
    # Create access that will expire
    access = temp_access_manager.grant_temp_access(
        username="expireduser",
        full_name="Expired User",
        email="expired@company.com",
        role="developer",
        duration_days=30,
        reason="Test",
        skip_user_creation=True,
    )

    # Manually set expiration to past
    access.expires_at = datetime.now() - timedelta(days=1)
    temp_access_manager._save_access_registry()

    # Check expired
    expired = temp_access_manager.check_expired_access()

    assert len(expired) == 1
    assert expired[0].username == "expireduser"
    assert expired[0].status == AccessStatus.EXPIRED


def test_revoke_access(temp_access_manager):
    """Test revoking temporary access."""
    access = temp_access_manager.grant_temp_access(
        username="revokeuser",
        full_name="Revoke User",
        email="revoke@company.com",
        role="developer",
        duration_days=30,
        reason="Test",
        skip_user_creation=True,
    )

    success = temp_access_manager.revoke_access(
        username="revokeuser",
        reason="Access no longer needed",
        revoked_by="admin",
        skip_system=True,
    )

    assert success
    assert access.status == AccessStatus.REVOKED
    assert access.revoked_at is not None
    assert access.revoked_by == "admin"


def test_revoke_nonexistent_access(temp_access_manager):
    """Test revoking non-existent access."""
    success = temp_access_manager.revoke_access(
        username="nonexistent",
        skip_system=True,
    )

    assert not success


def test_request_extension(temp_access_manager):
    """Test requesting access extension."""
    # Grant access first
    temp_access_manager.grant_temp_access(
        username="extenduser",
        full_name="Extend User",
        email="extend@company.com",
        role="developer",
        duration_days=30,
        reason="Initial project",
        skip_user_creation=True,
    )

    # Request extension
    extension = temp_access_manager.request_extension(
        username="extenduser",
        additional_days=14,
        reason="Project extended",
        requested_by="manager",
    )

    assert extension is not None
    assert extension.username == "extenduser"
    assert extension.additional_days == 14
    assert extension.status == ExtensionStatus.PENDING


def test_request_extension_for_nonexistent_user(temp_access_manager):
    """Test requesting extension for non-existent user."""
    with pytest.raises(ValueError, match="No temporary access found"):
        temp_access_manager.request_extension(
            username="nonexistent",
            additional_days=14,
            reason="Test",
            requested_by="manager",
        )


def test_approve_extension(temp_access_manager):
    """Test approving extension request."""
    # Grant access
    access = temp_access_manager.grant_temp_access(
        username="approveuser",
        full_name="Approve User",
        email="approve@company.com",
        role="developer",
        duration_days=30,
        reason="Initial project",
        skip_user_creation=True,
    )

    original_expiration = access.expires_at

    # Request extension
    extension = temp_access_manager.request_extension(
        username="approveuser",
        additional_days=14,
        reason="Project extended",
        requested_by="manager",
    )

    # Approve extension
    success = temp_access_manager.approve_extension(
        request_id=extension.request_id,
        approved_by="security-team",
    )

    assert success
    assert extension.status == ExtensionStatus.APPROVED
    assert extension.approved_by == "security-team"
    assert access.expires_at > original_expiration
    assert access.extended_count == 1


def test_get_expiring_soon(temp_access_manager):
    """Test getting access expiring soon."""
    # Create access expiring in 5 days
    access = temp_access_manager.grant_temp_access(
        username="expiringsoon",
        full_name="Expiring User",
        email="expiring@company.com",
        role="developer",
        duration_days=5,
        reason="Short project",
        skip_user_creation=True,
    )

    expiring = temp_access_manager.get_expiring_soon(days=7)

    assert len(expiring) == 1
    assert expiring[0].username == "expiringsoon"


def test_get_access(temp_access_manager):
    """Test getting access by username."""
    temp_access_manager.grant_temp_access(
        username="getuser",
        full_name="Get User",
        email="get@company.com",
        role="developer",
        duration_days=30,
        reason="Test",
        skip_user_creation=True,
    )

    access = temp_access_manager.get_access("getuser")

    assert access is not None
    assert access.username == "getuser"


def test_get_nonexistent_access(temp_access_manager):
    """Test getting non-existent access."""
    access = temp_access_manager.get_access("nonexistent")

    assert access is None


def test_list_access(temp_access_manager):
    """Test listing all access grants."""
    temp_access_manager.grant_temp_access(
        username="user1",
        full_name="User One",
        email="user1@company.com",
        role="developer",
        duration_days=30,
        reason="Project 1",
        skip_user_creation=True,
    )

    temp_access_manager.grant_temp_access(
        username="user2",
        full_name="User Two",
        email="user2@company.com",
        role="developer",
        duration_days=30,
        reason="Project 2",
        skip_user_creation=True,
    )

    all_access = temp_access_manager.list_access()

    assert len(all_access) == 2


def test_list_access_by_status(temp_access_manager):
    """Test listing access by status."""
    # Grant and revoke one
    temp_access_manager.grant_temp_access(
        username="activeuser",
        full_name="Active User",
        email="active@company.com",
        role="developer",
        duration_days=30,
        reason="Active",
        skip_user_creation=True,
    )

    temp_access_manager.grant_temp_access(
        username="revokeduser",
        full_name="Revoked User",
        email="revoked@company.com",
        role="developer",
        duration_days=30,
        reason="Revoked",
        skip_user_creation=True,
    )

    temp_access_manager.revoke_access("revokeduser", skip_system=True)

    # List active
    active = temp_access_manager.list_access(status=AccessStatus.ACTIVE)
    assert len(active) == 1

    # List revoked
    revoked = temp_access_manager.list_access(status=AccessStatus.REVOKED)
    assert len(revoked) == 1


def test_get_pending_extensions(temp_access_manager):
    """Test getting pending extension requests."""
    # Grant access and request extension
    temp_access_manager.grant_temp_access(
        username="pendinguser",
        full_name="Pending User",
        email="pending@company.com",
        role="developer",
        duration_days=30,
        reason="Test",
        skip_user_creation=True,
    )

    temp_access_manager.request_extension(
        username="pendinguser",
        additional_days=14,
        reason="Need more time",
        requested_by="manager",
    )

    pending = temp_access_manager.get_pending_extensions()

    assert len(pending) == 1
    assert pending[0].username == "pendinguser"


def test_access_persistence(temp_access_manager, temp_paths):
    """Test access persists to registry."""
    temp_access_manager.grant_temp_access(
        username="persistuser",
        full_name="Persist User",
        email="persist@company.com",
        role="developer",
        duration_days=30,
        reason="Test persistence",
        skip_user_creation=True,
    )

    # Create new manager instance
    new_manager = TempAccessManager(
        registry_file=temp_paths["registry"],
        extensions_file=temp_paths["extensions"],
        audit_log=temp_paths["audit_log"],
    )

    # Should load from registry
    access = new_manager.get_access("persistuser")

    assert access is not None
    assert access.username == "persistuser"


def test_temp_access_dataclass():
    """Test TempAccess dataclass."""
    access = TempAccess(
        access_id="TEST-001",
        username="testuser",
        access_type=AccessType.TEMPORARY,
        granted_at=datetime(2026, 1, 6),
        expires_at=datetime(2026, 2, 5),
        role="developer",
        reason="Test project",
    )

    data = access.to_dict()

    assert data["username"] == "testuser"
    assert data["access_type"] == "temporary"
    assert data["role"] == "developer"


def test_extension_request_dataclass():
    """Test ExtensionRequest dataclass."""
    extension = ExtensionRequest(
        request_id="EXT-001",
        access_id="TEMP-001",
        username="testuser",
        additional_days=14,
        reason="Project extended",
        requested_by="manager",
        requested_at=datetime(2026, 1, 20),
    )

    data = extension.to_dict()

    assert data["username"] == "testuser"
    assert data["additional_days"] == 14
    assert data["status"] == "pending"


def test_audit_log_created(temp_access_manager, temp_paths):
    """Test audit log is created."""
    temp_access_manager.grant_temp_access(
        username="audituser",
        full_name="Audit User",
        email="audit@company.com",
        role="developer",
        duration_days=30,
        reason="Test audit",
        skip_user_creation=True,
    )

    assert temp_paths["audit_log"].exists()

    # Check content
    with open(temp_paths["audit_log"], "r") as f:
        content = f.read()

    assert "grant_access" in content
    assert "audituser" in content


def test_needs_reminder(temp_access_manager):
    """Test reminder check."""
    # Create access expiring in 5 days
    access = TempAccess(
        access_id="TEST-001",
        username="reminderuser",
        access_type=AccessType.TEMPORARY,
        granted_at=datetime.now() - timedelta(days=25),
        expires_at=datetime.now() + timedelta(days=5),
        role="developer",
        reason="Test",
        notify_before_days=7,
    )

    assert access.needs_reminder()


def test_no_reminder_needed(temp_access_manager):
    """Test no reminder needed."""
    # Create access expiring in 20 days
    access = TempAccess(
        access_id="TEST-001",
        username="noreminder",
        access_type=AccessType.TEMPORARY,
        granted_at=datetime.now(),
        expires_at=datetime.now() + timedelta(days=20),
        role="developer",
        reason="Test",
        notify_before_days=7,
    )

    assert not access.needs_reminder()
