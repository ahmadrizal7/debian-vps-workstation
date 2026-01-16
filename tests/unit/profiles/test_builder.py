from configurator.profiles.builder import ProfileBuilder


def test_builder_add_module_with_dependencies():
    """Test adding module adds dependencies."""
    builder = ProfileBuilder("test")

    # Adding desktop should add system and security (based on registry defaults)
    builder.add_module("desktop")

    assert "desktop" in builder.enabled_modules
    assert "system" in builder.enabled_modules
    assert "security" in builder.enabled_modules


def test_builder_remove_module_dependency_check():
    """Test removing a module that is required by another."""
    builder = ProfileBuilder("test")
    builder.add_module("desktop")

    # Try to remove system (desktop depends on it)
    builder.remove_module("system")

    # Should still be there if logic prevents it
    # Note: The implementation in builder.py logs a warning and returns, protecting the removal.
    assert "system" in builder.enabled_modules


def test_builder_configure_module():
    """Test configuring a module."""
    builder = ProfileBuilder("test")
    builder.configure_module("python", {"version": "3.11"})

    assert "python" in builder.enabled_modules  # Auto-added
    assert builder.module_config["python"]["version"] == "3.11"


def test_builder_build():
    """Test building profile."""
    builder = ProfileBuilder("test")
    builder.add_module("system")

    profile = builder.build()

    assert profile.name == "test"
    assert "system" in profile.enabled_modules
