"""
SSH Audit Logging.

This module provides audit logging for SSH key operations,
integrating with the core audit system.
"""

import json
import logging
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional


class SSHAuditEvent(Enum):
    """SSH-related audit event types."""

    KEY_GENERATED = "ssh_key_generated"
    KEY_DEPLOYED = "ssh_key_deployed"
    KEY_ROTATED = "ssh_key_rotated"
    KEY_REVOKED = "ssh_key_revoked"
    KEY_IMPORTED = "ssh_key_imported"
    SSH_HARDENED = "ssh_hardened"
    PASSWORD_AUTH_DISABLED = "ssh_password_auth_disabled"
    PASSWORD_AUTH_ENABLED = "ssh_password_auth_enabled"
    ROOT_LOGIN_DISABLED = "ssh_root_login_disabled"
    STALE_KEY_DETECTED = "ssh_stale_key_detected"
    EXPIRING_KEY_DETECTED = "ssh_expiring_key_detected"


class SSHAuditLogger:
    """
    Audit logger for SSH key operations.

    Logs key lifecycle events for security auditing and compliance.

    Usage:
        logger = SSHAuditLogger()

        # Log key generation
        logger.log_key_generated(
            user="johndoe",
            key_id="johndoe-laptop",
            key_type="ed25519"
        )
    """

    DEFAULT_LOG_PATH = Path("/var/log/debian-vps-configurator/ssh-audit.log")

    def __init__(self, log_path: Optional[Path] = None, logger: Optional[logging.Logger] = None):
        """
        Initialize SSHAuditLogger.

        Args:
            log_path: Custom path for SSH audit log
            logger: Optional logger instance
        """
        self.log_path = log_path or self.DEFAULT_LOG_PATH
        self.logger = logger or logging.getLogger(__name__)
        self._ensure_log_dir()

    def _ensure_log_dir(self) -> None:
        """Ensure log directory exists."""
        try:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            self.logger.warning(f"Cannot create log directory: {self.log_path.parent}")

    def _write_log(self, event_type: SSHAuditEvent, details: Dict[str, Any]) -> None:
        """
        Write audit log entry.

        Args:
            event_type: Type of audit event
            details: Event details
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type.value,
            **details,
        }

        try:
            with open(self.log_path, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except (PermissionError, OSError) as e:
            self.logger.warning(f"Cannot write to SSH audit log: {e}")

        # Also log via standard logger
        self.logger.info(f"SSH Audit: {event_type.value} - {details}")

    def log_key_generated(
        self,
        user: str,
        key_id: str,
        key_type: str,
        fingerprint: str = "",
        expires_at: Optional[str] = None,
    ) -> None:
        """Log key generation event."""
        self._write_log(
            SSHAuditEvent.KEY_GENERATED,
            {
                "user": user,
                "key_id": key_id,
                "key_type": key_type,
                "fingerprint": fingerprint,
                "expires_at": expires_at,
            },
        )

    def log_key_deployed(
        self,
        user: str,
        key_id: str,
    ) -> None:
        """Log key deployment event."""
        self._write_log(
            SSHAuditEvent.KEY_DEPLOYED,
            {
                "user": user,
                "key_id": key_id,
            },
        )

    def log_key_rotated(
        self,
        user: str,
        old_key_id: str,
        new_key_id: str,
        grace_period_days: int,
    ) -> None:
        """Log key rotation event."""
        self._write_log(
            SSHAuditEvent.KEY_ROTATED,
            {
                "user": user,
                "old_key_id": old_key_id,
                "new_key_id": new_key_id,
                "grace_period_days": grace_period_days,
            },
        )

    def log_key_revoked(
        self,
        user: str,
        key_id: str,
        reason: str = "",
    ) -> None:
        """Log key revocation event."""
        self._write_log(
            SSHAuditEvent.KEY_REVOKED,
            {
                "user": user,
                "key_id": key_id,
                "reason": reason,
            },
        )

    def log_key_imported(
        self,
        user: str,
        key_id: str,
        fingerprint: str = "",
    ) -> None:
        """Log key import event."""
        self._write_log(
            SSHAuditEvent.KEY_IMPORTED,
            {
                "user": user,
                "key_id": key_id,
                "fingerprint": fingerprint,
            },
        )

    def log_ssh_hardened(
        self,
        settings_applied: Dict[str, str],
    ) -> None:
        """Log SSH hardening event."""
        self._write_log(
            SSHAuditEvent.SSH_HARDENED,
            {
                "settings_applied": settings_applied,
            },
        )

    def log_password_auth_changed(
        self,
        enabled: bool,
    ) -> None:
        """Log password authentication change."""
        event = (
            SSHAuditEvent.PASSWORD_AUTH_ENABLED if enabled else SSHAuditEvent.PASSWORD_AUTH_DISABLED
        )
        self._write_log(
            event,
            {
                "password_auth_enabled": enabled,
            },
        )

    def log_stale_key_detected(
        self,
        user: str,
        key_id: str,
        days_inactive: int,
    ) -> None:
        """Log stale key detection."""
        self._write_log(
            SSHAuditEvent.STALE_KEY_DETECTED,
            {
                "user": user,
                "key_id": key_id,
                "days_inactive": days_inactive,
            },
        )

    def log_expiring_key_detected(
        self,
        user: str,
        key_id: str,
        days_until_expiry: int,
    ) -> None:
        """Log expiring key detection."""
        self._write_log(
            SSHAuditEvent.EXPIRING_KEY_DETECTED,
            {
                "user": user,
                "key_id": key_id,
                "days_until_expiry": days_until_expiry,
            },
        )
