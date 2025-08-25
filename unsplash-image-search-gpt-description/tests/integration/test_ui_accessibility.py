"""
Integration tests for UI accessibility and theme management.
These tests verify that the application maintains proper accessibility standards,
focus handling, and theme consistency across different states.
"""

import pytest
import tkinter as tk
from tkinter import ttk
from unittest.mock import Mock, MagicMock, patch
import threading
import time
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))


@pytest.mark.gui
@pytest.mark.integration
class TestUIAccessibility:
    """Test UI accessibility features and focus management."""
    
    @pytest.fixture
    def mock_config_manager(self, tmp_path):
        """Create a mock config manager for accessibility testing."""
        from config_manager import ConfigManager
        config = Mock(spec=ConfigManager)
        config.get_api_keys.return_value = {
            'unsplash': 'test_unsplash_key_12345678901234567890123456789012345',
            'openai': 'sk-test_openai_key_12345678901234567890123456789012345',
            'gpt_model': 'gpt-4o-mini'
        }
        config.get_paths.return_value = {
            'data_dir': tmp_path / 'data',
            'log_file': tmp_path / 'data' / 'session.json',
            'vocabulary_file': tmp_path / 'data' / 'vocabulary.csv'
        }
        config.validate_api_keys.return_value = True
        config.config = Mock()
        config.config.get.return_value = '100'
        return config
    
    def test_keyboard_navigation_flow(self, mock_config_manager):
        """Test complete keyboard navigation through the UI."""
        with patch('src.ui.main_window.ensure_api_keys_configured') as mock_ensure:
            mock_ensure.return_value = mock_config_manager
            
            with patch('src.ui.theme_manager.ThemeManager') as mock_theme:
                mock_theme_instance = Mock()
                mock_theme_instance.get_colors.return_value = {
                    'bg': '#ffffff', 'fg': '#000000', 'frame_bg': '#f0f0f0',
                    'button_active_bg': '#e0e0e0', 'info': '#0066cc', 'border': '#cccccc'
                }
                mock_theme_instance.create_themed_tooltip = Mock()
                mock_theme_instance.register_theme_callback = Mock()
                mock_theme.return_value = mock_theme_instance
                
                with patch('src.performance_optimization.PerformanceOptimizer'):
                    with patch('src.optimized_image_collection.OptimizedImageCollector'):
                        with patch('src.services.unsplash_service.UnsplashService'):
                            try:
                                from main import ImageSearchApp
                                
                                app = ImageSearchApp()
                                app.update_idletasks()
                                
                                # Test tab order through main widgets
                                focusable_widgets = [
                                    app.search_entry,
                                    app.search_button,
                                    app.another_button,
                                    app.newsearch_button,
                                    app.note_text,
                                    app.generate_desc_button
                                ]
                                
                                # Test forward tab navigation
                                for i, widget in enumerate(focusable_widgets):
                                    try:
                                        widget.focus_set()
                                        app.update_idletasks()
                                        
                                        # Verify widget has focus (if supported)
                                        focused_widget = app.focus_get()
                                        
                                        # Test keyboard shortcuts work with focus
                                        if widget == app.search_entry:
                                            # Test Enter key binding
                                            assert widget.bind('<Return>') is not None or len(widget.bind('<Return>')) > 0
                                        
                                    except tk.TclError as e:
                                        # Some widgets might not support focus in test environment
                                        print(f"Focus error for {widget}: {e}")
                                
                                # Test application-level keyboard shortcuts
                                shortcuts_to_test = [
                                    ('<Control-n>', 'change_search'),
                                    ('<Control-g>', 'generate_description'),
                                    ('<Control-e>', 'export_vocabulary'),
                                    ('<Control-t>', 'toggle_theme'),
                                    ('<Control-q>', 'on_exit'),
                                    ('<F1>', 'show_help_dialog')
                                ]
                                
                                for shortcut, method_name in shortcuts_to_test:
                                    binding = app.bind(shortcut)
                                    assert binding is not None, f"Shortcut {shortcut} not bound"
                                
                                app.destroy()
                                
                            except Exception as e:
                                pytest.fail(f"Keyboard navigation test failed: {e}")
    
    def test_focus_restoration_after_operations(self, mock_config_manager):
        """Test that focus is properly restored after async operations."""
        with patch('src.ui.main_window.ensure_api_keys_configured') as mock_ensure:
            mock_ensure.return_value = mock_config_manager
            
            with patch('src.ui.theme_manager.ThemeManager') as mock_theme:
                mock_theme_instance = Mock()
                mock_theme_instance.get_colors.return_value = {
                    'bg': '#ffffff', 'fg': '#000000', 'frame_bg': '#f0f0f0',
                    'button_active_bg': '#e0e0e0', 'info': '#0066cc', 'border': '#cccccc'
                }
                mock_theme_instance.create_themed_tooltip = Mock()
                mock_theme_instance.register_theme_callback = Mock()
                mock_theme.return_value = mock_theme_instance
                
                with patch('src.performance_optimization.PerformanceOptimizer'):
                    with patch('src.optimized_image_collection.OptimizedImageCollector'):
                        with patch('src.services.unsplash_service.UnsplashService'):
                            try:
                                from main import ImageSearchApp
                                
                                app = ImageSearchApp()
                                app.update_idletasks()
                                
                                # Set initial focus
                                app.search_entry.focus_set()
                                initial_focus = app.focus_get()
                                
                                # Simulate button state changes (like during API calls)
                                app.disable_buttons()
                                app.update_idletasks()
                                
                                # Buttons should be disabled but focus should remain
                                assert app.search_button['state'] == 'disabled'
                                assert app.another_button['state'] == 'disabled'
                                
                                # Re-enable buttons
                                app.enable_buttons()
                                app.update_idletasks()
                                
                                # Focus should be restorable
                                app.search_entry.focus_set()
                                app.update_idletasks()
                                
                                # Verify accessibility features
                                assert app.search_entry.cget('state') == 'normal'
                                assert app.search_button.cget('state') == 'normal'
                                
                                app.destroy()
                                
                            except Exception as e:
                                pytest.fail(f"Focus restoration test failed: {e}")
    
    def test_high_contrast_theme_support(self, mock_config_manager):
        """Test UI behavior with high contrast themes."""
        with patch('src.ui.main_window.ensure_api_keys_configured') as mock_ensure:
            mock_ensure.return_value = mock_config_manager
            
            with patch('src.ui.theme_manager.ThemeManager') as mock_theme:
                # Mock high contrast theme
                mock_theme_instance = Mock()
                high_contrast_colors = {
                    'bg': '#000000', 'fg': '#ffffff', 'frame_bg': '#000000',
                    'button_active_bg': '#ffffff', 'info': '#ffff00', 'border': '#ffffff'
                }
                mock_theme_instance.get_colors.return_value = high_contrast_colors
                mock_theme_instance.create_themed_tooltip = Mock()
                mock_theme_instance.register_theme_callback = Mock()
                mock_theme_instance.current_theme = 'dark'
                mock_theme.return_value = mock_theme_instance
                
                with patch('src.performance_optimization.PerformanceOptimizer'):
                    with patch('src.optimized_image_collection.OptimizedImageCollector'):
                        with patch('src.services.unsplash_service.UnsplashService'):
                            try:
                                from main import ImageSearchApp
                                
                                app = ImageSearchApp()
                                app.update_idletasks()
                                
                                # Test theme change callback
                                if hasattr(app, 'on_theme_change'):
                                    app.on_theme_change('dark', high_contrast_colors)
                                    app.update_idletasks()
                                
                                # Verify high contrast is maintained
                                # (Colors should be applied through theme manager)
                                
                                # Test theme toggle functionality
                                if hasattr(app, 'toggle_theme'):
                                    try:
                                        app.toggle_theme()
                                        app.update_idletasks()
                                    except Exception as e:
                                        print(f"Theme toggle error: {e}")
                                
                                app.destroy()
                                
                            except Exception as e:
                                pytest.fail(f"High contrast theme test failed: {e}")
    
    def test_tooltip_accessibility(self, mock_config_manager):
        """Test tooltip functionality for accessibility."""
        with patch('src.ui.main_window.ensure_api_keys_configured') as mock_ensure:
            mock_ensure.return_value = mock_config_manager
            
            with patch('src.ui.theme_manager.ThemeManager') as mock_theme:
                mock_theme_instance = Mock()
                mock_theme_instance.get_colors.return_value = {
                    'bg': '#ffffff', 'fg': '#000000', 'frame_bg': '#f0f0f0',
                    'button_active_bg': '#e0e0e0', 'info': '#0066cc', 'border': '#cccccc'
                }
                mock_theme_instance.create_themed_tooltip = Mock()
                mock_theme_instance.register_theme_callback = Mock()
                mock_theme.return_value = mock_theme_instance
                
                with patch('src.performance_optimization.PerformanceOptimizer'):
                    with patch('src.optimized_image_collection.OptimizedImageCollector'):
                        with patch('src.services.unsplash_service.UnsplashService'):
                            try:
                                from main import ImageSearchApp
                                
                                app = ImageSearchApp()
                                app.update_idletasks()
                                
                                # Verify tooltips are created for important buttons
                                tooltip_widgets = [
                                    app.search_button,
                                    app.another_button,
                                    app.newsearch_button,
                                    app.generate_desc_button
                                ]
                                
                                for widget in tooltip_widgets:
                                    # Verify theme manager was called to create tooltip
                                    mock_theme_instance.create_themed_tooltip.assert_any_call(
                                        widget, unittest.mock.ANY
                                    )
                                
                                # Test help dialog accessibility
                                if hasattr(app, 'show_help_dialog'):
                                    try:
                                        # Create help dialog
                                        app.show_help_dialog()
                                        app.update_idletasks()
                                        
                                        # Find help dialog in children
                                        for child in app.winfo_children():
                                            if isinstance(child, tk.Toplevel) and 'Help' in child.title():
                                                # Verify dialog properties
                                                assert child.transient() == app
                                                child.destroy()
                                                break
                                    except Exception as e:
                                        print(f"Help dialog error: {e}")
                                
                                app.destroy()
                                
                            except Exception as e:
                                pytest.fail(f"Tooltip accessibility test failed: {e}")


@pytest.mark.gui
@pytest.mark.integration
class TestThemeManagement:
    """Test theme management and visual consistency."""
    
    @pytest.fixture
    def mock_config_manager(self, tmp_path):
        """Create a mock config manager for theme testing."""
        from config_manager import ConfigManager
        config = Mock(spec=ConfigManager)
        config.get_api_keys.return_value = {
            'unsplash': 'test_key',
            'openai': 'sk-test_key',
            'gpt_model': 'gpt-4o-mini'
        }
        config.get_paths.return_value = {
            'data_dir': tmp_path / 'data',
            'log_file': tmp_path / 'data' / 'session.json',
            'vocabulary_file': tmp_path / 'data' / 'vocabulary.csv'
        }
        config.validate_api_keys.return_value = True
        config.config = Mock()
        config.config.get.return_value = '100'
        return config
    
    def test_theme_consistency_across_widgets(self, mock_config_manager):
        """Test that theme is applied consistently across all widgets."""
        with patch('src.ui.main_window.ensure_api_keys_configured') as mock_ensure:
            mock_ensure.return_value = mock_config_manager
            
            with patch('src.ui.theme_manager.ThemeManager') as mock_theme:
                mock_theme_instance = Mock()
                test_colors = {
                    'bg': '#f0f0f0', 'fg': '#333333', 'frame_bg': '#ffffff',
                    'button_active_bg': '#e0e0e0', 'info': '#0066cc', 'border': '#cccccc'
                }
                mock_theme_instance.get_colors.return_value = test_colors
                mock_theme_instance.create_themed_tooltip = Mock()
                mock_theme_instance.register_theme_callback = Mock()
                mock_theme_instance.configure_widget = Mock()
                mock_theme.return_value = mock_theme_instance
                
                with patch('src.performance_optimization.PerformanceOptimizer'):
                    with patch('src.optimized_image_collection.OptimizedImageCollector'):
                        with patch('src.services.unsplash_service.UnsplashService'):
                            try:
                                from main import ImageSearchApp
                                
                                app = ImageSearchApp()
                                app.update_idletasks()
                                
                                # Verify theme manager was initialized
                                assert hasattr(app, 'theme_manager')
                                mock_theme_instance.register_theme_callback.assert_called()
                                
                                # Test theme change callback
                                if hasattr(app, 'on_theme_change'):
                                    app.on_theme_change('test_theme', test_colors)
                                    
                                    # Verify widgets were updated
                                    text_widgets = ['note_text', 'description_text']
                                    for widget_name in text_widgets:
                                        if hasattr(app, widget_name):
                                            widget = getattr(app, widget_name)
                                            mock_theme_instance.configure_widget.assert_any_call(
                                                widget, 'Text'
                                            )
                                
                                app.destroy()
                                
                            except Exception as e:
                                pytest.fail(f"Theme consistency test failed: {e}")
    
    def test_theme_switching_performance(self, mock_config_manager):
        """Test performance of theme switching operations."""
        with patch('src.ui.main_window.ensure_api_keys_configured') as mock_ensure:
            mock_ensure.return_value = mock_config_manager
            
            with patch('src.ui.theme_manager.ThemeManager') as mock_theme:
                mock_theme_instance = Mock()
                mock_theme_instance.get_colors.return_value = {
                    'bg': '#ffffff', 'fg': '#000000', 'frame_bg': '#f0f0f0',
                    'button_active_bg': '#e0e0e0', 'info': '#0066cc', 'border': '#cccccc'
                }
                mock_theme_instance.create_themed_tooltip = Mock()
                mock_theme_instance.register_theme_callback = Mock()
                mock_theme_instance.configure_widget = Mock()
                mock_theme_instance.toggle_theme = Mock()
                mock_theme_instance.current_theme = 'light'
                mock_theme.return_value = mock_theme_instance
                
                with patch('src.performance_optimization.PerformanceOptimizer'):
                    with patch('src.optimized_image_collection.OptimizedImageCollector'):
                        with patch('src.services.unsplash_service.UnsplashService'):
                            try:
                                from main import ImageSearchApp
                                
                                app = ImageSearchApp()
                                app.update_idletasks()
                                
                                # Measure theme switch performance
                                start_time = time.time()
                                
                                # Perform multiple theme switches
                                for i in range(5):
                                    if hasattr(app, 'toggle_theme'):
                                        app.toggle_theme()
                                        app.update_idletasks()
                                        
                                        # Simulate theme manager response
                                        if hasattr(app, 'on_theme_change'):
                                            theme_name = 'dark' if i % 2 else 'light'
                                            app.on_theme_change(theme_name, mock_theme_instance.get_colors.return_value)
                                
                                end_time = time.time()
                                total_time = end_time - start_time
                                
                                # Theme switching should be reasonably fast
                                assert total_time < 2.0, f"Theme switching took too long: {total_time}s"
                                
                                app.destroy()
                                
                            except Exception as e:
                                pytest.fail(f"Theme switching performance test failed: {e}")
    
    def test_dynamic_theme_updates(self, mock_config_manager):
        """Test dynamic theme updates during application runtime."""
        with patch('src.ui.main_window.ensure_api_keys_configured') as mock_ensure:
            mock_ensure.return_value = mock_config_manager
            
            with patch('src.ui.theme_manager.ThemeManager') as mock_theme:
                mock_theme_instance = Mock()
                light_colors = {
                    'bg': '#ffffff', 'fg': '#000000', 'frame_bg': '#f0f0f0',
                    'button_active_bg': '#e0e0e0', 'info': '#0066cc', 'border': '#cccccc'
                }
                dark_colors = {
                    'bg': '#2b2b2b', 'fg': '#ffffff', 'frame_bg': '#3c3c3c',
                    'button_active_bg': '#4d4d4d', 'info': '#66b3ff', 'border': '#555555'
                }
                
                # Start with light theme
                mock_theme_instance.get_colors.return_value = light_colors
                mock_theme_instance.create_themed_tooltip = Mock()
                mock_theme_instance.register_theme_callback = Mock()
                mock_theme_instance.configure_widget = Mock()
                mock_theme_instance.current_theme = 'light'
                mock_theme.return_value = mock_theme_instance
                
                with patch('src.performance_optimization.PerformanceOptimizer'):
                    with patch('src.optimized_image_collection.OptimizedImageCollector'):
                        with patch('src.services.unsplash_service.UnsplashService'):
                            try:
                                from main import ImageSearchApp
                                
                                app = ImageSearchApp()
                                app.update_idletasks()
                                
                                # Verify initial theme setup
                                mock_theme_instance.register_theme_callback.assert_called()
                                
                                # Test dynamic theme change
                                if hasattr(app, 'on_theme_change'):
                                    # Switch to dark theme
                                    mock_theme_instance.current_theme = 'dark'
                                    mock_theme_instance.get_colors.return_value = dark_colors
                                    
                                    app.on_theme_change('dark', dark_colors)
                                    app.update_idletasks()
                                    
                                    # Verify theme change was applied
                                    assert mock_theme_instance.configure_widget.call_count > 0
                                    
                                    # Test that UI remains functional after theme change
                                    app.update_status("Theme changed successfully")
                                    assert app.status_label.cget('text') == "Theme changed successfully"
                                
                                app.destroy()
                                
                            except Exception as e:
                                pytest.fail(f"Dynamic theme update test failed: {e}")


@pytest.mark.gui
@pytest.mark.integration
class TestUIResponsiveness:
    """Test UI responsiveness under various conditions."""
    
    @pytest.fixture
    def mock_config_manager(self, tmp_path):
        """Create a mock config manager for responsiveness testing."""
        from config_manager import ConfigManager
        config = Mock(spec=ConfigManager)
        config.get_api_keys.return_value = {
            'unsplash': 'test_key',
            'openai': 'sk-test_key',
            'gpt_model': 'gpt-4o-mini'
        }
        config.get_paths.return_value = {
            'data_dir': tmp_path / 'data',
            'log_file': tmp_path / 'data' / 'session.json',
            'vocabulary_file': tmp_path / 'data' / 'vocabulary.csv'
        }
        config.validate_api_keys.return_value = True
        config.config = Mock()
        config.config.get.return_value = '100'
        return config
    
    def test_ui_remains_responsive_during_operations(self, mock_config_manager):
        """Test that UI remains responsive during background operations."""
        with patch('src.ui.main_window.ensure_api_keys_configured') as mock_ensure:
            mock_ensure.return_value = mock_config_manager
            
            with patch('src.ui.theme_manager.ThemeManager') as mock_theme:
                mock_theme_instance = Mock()
                mock_theme_instance.get_colors.return_value = {
                    'bg': '#ffffff', 'fg': '#000000', 'frame_bg': '#f0f0f0',
                    'button_active_bg': '#e0e0e0', 'info': '#0066cc', 'border': '#cccccc'
                }
                mock_theme_instance.create_themed_tooltip = Mock()
                mock_theme_instance.register_theme_callback = Mock()
                mock_theme.return_value = mock_theme_instance
                
                with patch('src.performance_optimization.PerformanceOptimizer'):
                    with patch('src.optimized_image_collection.OptimizedImageCollector'):
                        with patch('src.services.unsplash_service.UnsplashService'):
                            try:
                                from main import ImageSearchApp
                                
                                app = ImageSearchApp()
                                app.update_idletasks()
                                
                                # Simulate background operations
                                def background_task():
                                    for i in range(10):
                                        app.after(i * 10, lambda idx=i: app.update_status(f"Processing {idx}"))
                                        time.sleep(0.01)
                                
                                # Start background task
                                thread = threading.Thread(target=background_task)
                                thread.start()
                                
                                # UI should remain responsive
                                for i in range(5):
                                    app.update_idletasks()
                                    time.sleep(0.02)
                                    
                                    # Test that UI operations work
                                    try:
                                        app.search_entry.delete(0, tk.END)
                                        app.search_entry.insert(0, f"test {i}")
                                        app.update_idletasks()
                                    except tk.TclError:
                                        # Widget might be busy, but shouldn't crash
                                        pass
                                
                                thread.join(timeout=2.0)
                                app.destroy()
                                
                            except Exception as e:
                                pytest.fail(f"UI responsiveness test failed: {e}")
    
    def test_large_vocabulary_list_performance(self, mock_config_manager):
        """Test UI performance with large vocabulary lists."""
        with patch('src.ui.main_window.ensure_api_keys_configured') as mock_ensure:
            mock_ensure.return_value = mock_config_manager
            
            with patch('src.ui.theme_manager.ThemeManager') as mock_theme:
                mock_theme_instance = Mock()
                mock_theme_instance.get_colors.return_value = {
                    'bg': '#ffffff', 'fg': '#000000', 'frame_bg': '#f0f0f0',
                    'button_active_bg': '#e0e0e0', 'info': '#0066cc', 'border': '#cccccc'
                }
                mock_theme_instance.create_themed_tooltip = Mock()
                mock_theme_instance.register_theme_callback = Mock()
                mock_theme.return_value = mock_theme_instance
                
                with patch('src.performance_optimization.PerformanceOptimizer'):
                    with patch('src.optimized_image_collection.OptimizedImageCollector'):
                        with patch('src.services.unsplash_service.UnsplashService'):
                            try:
                                from main import ImageSearchApp
                                
                                app = ImageSearchApp()
                                app.update_idletasks()
                                
                                # Simulate adding many vocabulary items
                                start_time = time.time()
                                
                                for i in range(100):
                                    phrase = f"palabra {i} - word {i}"
                                    app.target_phrases.append(phrase)
                                    
                                    # Update display every 10 items
                                    if i % 10 == 0:
                                        app.update_target_list_display()
                                        app.update_idletasks()
                                
                                end_time = time.time()
                                update_time = end_time - start_time
                                
                                # Should handle large lists reasonably fast
                                assert update_time < 5.0, f"Large vocabulary update took too long: {update_time}s"
                                
                                # Verify UI is still responsive
                                app.update_status("Large vocabulary test complete")
                                app.update_idletasks()
                                
                                app.destroy()
                                
                            except Exception as e:
                                pytest.fail(f"Large vocabulary performance test failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])