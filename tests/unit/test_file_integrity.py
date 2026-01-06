import os
import time
from unittest.mock import MagicMock, patch

import pytest

from configurator.core.file_integrity import FileIntegrityMonitor


@pytest.fixture
def fim(tmp_path):
    db_path = tmp_path / "fim.json"

    # Create some monitored files
    file1 = tmp_path / "test.conf"
    file1.write_text("content1")

    file2 = tmp_path / "other.conf"
    file2.write_text("content2")

    with patch("os.chmod"):  # Mock chmod
        # Mocking audit logger to avoid real logging during tests
        with patch("configurator.core.file_integrity.AuditLogger") as MockAudit:
            MockAudit.return_value.log_event = MagicMock()

            monitor = FileIntegrityMonitor(
                db_path=db_path, monitored_files=[str(file1), str(file2)]
            )
            yield monitor, file1, file2


def test_initialize(fim):
    monitor, f1, f2 = fim
    monitor.initialize()

    assert monitor.db_path.exists()
    assert str(f1) in monitor.baseline
    assert str(f2) in monitor.baseline

    # Check stored hash matches actual hash
    assert monitor.baseline[str(f1)].sha256 == monitor._calculate_hash(f1)


def test_check_clean(fim):
    monitor, _, _ = fim
    monitor.initialize()

    violations = monitor.check()
    assert len(violations) == 0


def test_detect_content_change(fim):
    monitor, f1, _ = fim
    monitor.initialize()

    # Wait a tiny bit to ensure mtime change if OS has low resolution
    time.sleep(0.01)

    # Modify file
    f1.write_text("new content")

    violations = monitor.check()
    assert len(violations) == 1
    assert violations[0]["path"] == str(f1)
    assert "content_modified" in violations[0]["changes"]
    assert violations[0]["severity"] == "high"


def test_detect_deletion(fim):
    monitor, f1, _ = fim
    monitor.initialize()

    # Delete file
    try:
        os.remove(f1)
    except OSError:
        pass

    violations = monitor.check()
    assert len(violations) == 1
    assert violations[0]["type"] == "file_deleted"


def test_update_baseline(fim):
    monitor, f1, _ = fim
    monitor.initialize()

    # Modify
    f1.write_text("modified")

    # Verify modification detected
    assert len(monitor.check()) == 1

    # Update baseline
    monitor.update_baseline(str(f1))

    # Verify no violation now
    assert len(monitor.check()) == 0


def test_persistence(tmp_path):
    db_path = tmp_path / "fim.json"
    f1 = tmp_path / "f1"
    f1.write_text("data")

    with patch("os.chmod"):
        with patch("configurator.core.file_integrity.AuditLogger"):
            m1 = FileIntegrityMonitor(db_path=db_path, monitored_files=[str(f1)])
            m1.initialize()

            m2 = FileIntegrityMonitor(db_path=db_path, monitored_files=[str(f1)])
            assert str(f1) in m2.baseline
