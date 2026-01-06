import pytest

from configurator.rbac.rbac_manager import RBACManager


@pytest.mark.integration
@pytest.mark.parametrize("role_name", ["admin", "devops", "developer", "viewer"])
def test_default_roles_exist(role_name):
    manager = RBACManager(dry_run=True)
    assert manager.get_role(role_name) is not None
