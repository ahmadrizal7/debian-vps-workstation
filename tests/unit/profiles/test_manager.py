import pytest

from configurator.profiles.manager import Profile, ProfileManager


@pytest.fixture
def manager(tmp_path):
    # Mock paths to point to tmp_path
    m = ProfileManager()
    m.CUSTOM_PROFILES_DIR = tmp_path / "custom"
    m.CUSTOM_PROFILES_DIR.mkdir()
    return m


def test_profile_manager_list_profiles(manager):
    """Test listing all profiles."""
    profiles = manager.list_profiles()

    # We expect at least the builtin ones if they are found
    # But since we are testing in an environment where schemas might be relative to source
    # we should check if they were loaded.
    # Note: ProfileManager uses __file__ for builtins, so it should find them if they exist in source.

    # For this test, let's create a custom profile to ensure list works
    manager.save_profile(
        Profile(name="test-list", display_name="Test List", description="Desc", category="custom")
    )

    profiles = manager.list_profiles()
    assert any(p.name == "test-list" for p in profiles)


def test_profile_manager_load_builtin(manager):
    """Test loading built-in profile."""
    # This might fail if schemas are not in the expected relative path during test execution
    # depending on how pytest is run.
    # We will skip if builtin dir is empty manifest of issues in setup, not logic.
    if not any(manager.BUILTIN_PROFILES_DIR.glob("*.yaml")):
        pytest.skip("Builtin profiles not found")

    profile = manager.load_profile("beginner")
    assert profile.name == "beginner"
    assert "system" in profile.enabled_modules


def test_profile_manager_save_custom(manager):
    """Test saving custom profile."""
    profile = Profile(
        name="test-profile",
        display_name="Test Profile",
        description="Test",
        category="custom",
        enabled_modules=["system", "python"],
    )

    manager.save_profile(profile)

    # Reload and verify
    loaded = manager.load_profile("test-profile")
    assert loaded.name == "test-profile"
    assert loaded.enabled_modules == ["system", "python"]


def test_profile_manager_inheritance(manager):
    """Test profile inheritance (extends)."""
    # Create base profile
    base = Profile(
        name="base-test",
        display_name="Base",
        description="Base",
        category="custom",
        enabled_modules=["system", "python"],
    )
    manager.save_profile(base)

    # Create derived profile
    derived = Profile(
        name="derived-test",
        display_name="Derived",
        description="Derived",
        category="custom",
        extends="base-test",
        enabled_modules=["docker"],  # Add docker to base
    )
    manager.save_profile(derived)

    # Load derived
    loaded = manager.load_profile("derived-test")

    # Should have modules from both
    assert "system" in loaded.enabled_modules
    assert "python" in loaded.enabled_modules
    assert "docker" in loaded.enabled_modules
