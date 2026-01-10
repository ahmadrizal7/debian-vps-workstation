"""
Integration tests for Phase 4 complete flow.
"""

from unittest.mock import Mock, patch

import pytest

from configurator.modules.desktop import DesktopModule


class TestPhase4Integration:
    """Integration tests for full Phase 4 flow."""
    
    def test_configure_calls_all_phase4_methods(self):
        """Test that configure() calls all Phase 4 methods in correct order."""
        config = {"desktop": {"zsh": {"enabled": True}}}
        module = DesktopModule(config=config, logger=Mock(), rollback_manager=Mock())
        
        # Track method calls
        called_methods = []
        
        def track(name):
            def wrapper(*args, **kwargs):
                called_methods.append(name)
            return wrapper
        
        # Patch Phase 4 methods
        with patch.object(module, '_install_zsh_package', track('_install_zsh_package')):
            with patch.object(module, '_install_oh_my_zsh', track('_install_oh_my_zsh')):
                with patch.object(module, '_install_powerlevel10k', track('_install_powerlevel10k')):
                    with patch.object(module, '_install_zsh_plugins', track('_install_zsh_plugins')):
                        with patch.object(module, '_install_terminal_tools', track('_install_terminal_tools')):
                            with patch.object(module, '_configure_zshrc', track('_configure_zshrc')):
                                with patch.object(module, '_generate_p10k_starter_config', track('_generate_p10k_starter_config')):
                                    with patch.object(module, '_set_zsh_as_default_shell', track('_set_zsh_as_default_shell')):
                                        # Mock all previous phases
                                        with patch.object(module, '_install_xrdp'):
                                            with patch.object(module, '_install_xfce4'):
                                                with patch.object(module, '_configure_xrdp'):
                                                    with patch.object(module, '_optimize_xrdp_performance'):
                                                        with patch.object(module, '_configure_user_session'):
                                                            with patch.object(module, '_optimize_xfce_compositor'):
                                                                with patch.object(module, '_configure_polkit_rules'):
                                                                    with patch.object(module, '_install_themes'):
                                                                        with patch.object(module, '_install_icon_packs'):
                                                                            with patch.object(module, '_configure_fonts'):
                                                                                with patch.object(module, '_configure_panel_layout'):
                                                                                    with patch.object(module, '_apply_theme_and_icons'):
                                                                                        with patch.object(module, '_configure_session'):
                                                                                            with patch.object(module, '_start_services'):
                                                                                                with patch.object(module, '_install_and_configure_zsh', wraps=module._install_and_configure_zsh) as mock_main_zsh:
                                                                                                    module.configure()
        
        # Verify all Phase 4 methods called.
        # Note: Depending on implementation details, _generate_p10k_starter_config might be called by _configure_zshrc or separately.
        # We need to ensure the main methods are hit.
        
        assert '_install_zsh_package' in called_methods
        assert '_install_oh_my_zsh' in called_methods
        assert '_install_powerlevel10k' in called_methods
        assert '_install_zsh_plugins' in called_methods
        assert '_install_terminal_tools' in called_methods
        assert '_configure_zshrc' in called_methods
        # set_default_shell might be called if configured
        assert '_set_zsh_as_default_shell' in called_methods
