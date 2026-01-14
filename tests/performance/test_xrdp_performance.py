"""Performance tests for XRDP optimization."""

from unittest.mock import Mock, patch

import pytest

from configurator.modules.desktop import DesktopModule


class TestXRDPPerformance:
    """Performance tests for XRDP."""

    @pytest.fixture
    def module(self):
        return DesktopModule(config={}, logger=Mock(), rollback_manager=Mock())

    def test_xrdp_optimization_completes_quickly(self, module):
        """Test that XRDP optimization doesn't hang."""
        with patch("configurator.utils.file.write_file"):
            with patch.object(module, "install_packages", return_value=True):
                with patch.object(module, "run") as mock_run:
                    mock_run.return_value = Mock(success=True)
                    import time

                    start = time.time()
                    module._optimize_xrdp_performance()
                    duration = time.time() - start
                    # Should complete reasonably fast even with mocking overhead
                    assert duration < 5.0, f"Took {duration}s - too slow"
