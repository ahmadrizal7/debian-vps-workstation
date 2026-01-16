import pytest

from configurator.core.reporter.base import ReporterInterface


def test_reporter_interface_is_abstract():
    with pytest.raises(TypeError):
        ReporterInterface()
