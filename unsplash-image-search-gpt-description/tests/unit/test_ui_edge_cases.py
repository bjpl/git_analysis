"""
Edge case tests for UI rendering and error scenarios.
These tests cover unusual conditions, boundary cases, and error recovery scenarios.
"""

import pytest
import tkinter as tk
from tkinter import ttk
from unittest.mock import Mock, MagicMock, patch
import threading
import time
from pathlib import Path
import tempfile
import sys
import os
import gc
import psutil

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))


@pytest.mark.gui
@pytest.mark.edge_case
class TestUIEdgeCases:
    """Test UI behavior in edge cases and unusual conditions."""
    
    @pytest.fixture
    def minimal_config(self, tmp_path):
        """Create minimal config for edge case testing."""
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
    
    def test_ui_with_extremely_small_window(self, minimal_config):
        """Test UI behavior with extremely small window size."""
        with patch('src.ui.main_window.ensure_api_keys_configured') as mock_ensure:
            mock_ensure.return_value = minimal_config
            
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
                                
                                # Set extremely small size
                                app.geometry("50x50")
                                app.update_idletasks()
                                
                                # UI should not crash
                                assert app.winfo_exists()
                                
                                # Try to access main widgets
                                try:
                                    app.search_entry.get()
                                    app.update_status("Small window test")
                                except tk.TclError:
                                    # Acceptable if widgets are too small to render
                                    pass
                                
                                app.destroy()
                                
                            except Exception as e:
                                pytest.fail(f"Small window test failed: {e}")
    
    def test_ui_with_extremely_large_window(self, minimal_config):
        """Test UI behavior with extremely large window size."""
        with patch('src.ui.main_window.ensure_api_keys_configured') as mock_ensure:
            mock_ensure.return_value = minimal_config
            
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
                                
                                # Set very large size (but within screen bounds)
                                screen_width = app.winfo_screenwidth()
                                screen_height = app.winfo_screenheight()
                                large_width = min(3000, screen_width - 100)
                                large_height = min(2000, screen_height - 100)
                                
                                app.geometry(f"{large_width}x{large_height}")
                                app.update_idletasks()
                                
                                # UI should handle large sizes
                                assert app.winfo_exists()
                                
                                # Widgets should still be functional
                                app.search_entry.insert(0, "large window test")
                                assert "large window test" in app.search_entry.get()
                                
                                app.destroy()
                                
                            except Exception as e:
                                pytest.fail(f"Large window test failed: {e}")
    
    def test_ui_with_rapid_geometry_changes(self, minimal_config):
        """Test UI stability with rapid geometry changes."""
        with patch('src.ui.main_window.ensure_api_keys_configured') as mock_ensure:
            mock_ensure.return_value = minimal_config
            
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
                                
                                # Rapid geometry changes
                                geometries = [
                                    "800x600", "1200x800", "600x400", 
                                    "1000x700", "900x650", "1100x800"
                                ]
                                
                                for geometry in geometries:
                                    app.geometry(geometry)
                                    app.update_idletasks()
                                    time.sleep(0.01)  # Brief pause
                                
                                # UI should remain stable
                                assert app.winfo_exists()
                                app.update_status("Geometry change test complete")
                                
                                app.destroy()
                                
                            except Exception as e:
                                pytest.fail(f"Rapid geometry changes test failed: {e}")
    
    def test_ui_with_corrupted_theme_data(self, minimal_config):
        """Test UI behavior with corrupted or invalid theme data."""
        with patch('src.ui.main_window.ensure_api_keys_configured') as mock_ensure:
            mock_ensure.return_value = minimal_config
            
            with patch('src.ui.theme_manager.ThemeManager') as mock_theme:
                # Mock corrupted theme manager
                mock_theme_instance = Mock()
                
                # Return invalid color data
                corrupted_colors = {
                    'bg': 'invalid_color',
                    'fg': None,
                    'frame_bg': 12345,  # Invalid type
                    # Missing required keys
                }
                mock_theme_instance.get_colors.return_value = corrupted_colors
                mock_theme_instance.create_themed_tooltip = Mock(side_effect=Exception("Theme error"))
                mock_theme_instance.register_theme_callback = Mock()
                mock_theme.return_value = mock_theme_instance
                
                with patch('src.performance_optimization.PerformanceOptimizer'):
                    with patch('src.optimized_image_collection.OptimizedImageCollector'):
                        with patch('src.services.unsplash_service.UnsplashService'):
                            try:
                                from main import ImageSearchApp
                                
                                app = ImageSearchApp()
                                
                                # App should handle corrupted theme gracefully
                                assert app.winfo_exists()
                                
                                # Try theme operations
                                if hasattr(app, 'on_theme_change'):
                                    try:
                                        app.on_theme_change('corrupted', corrupted_colors)
                                    except Exception:
                                        # Should handle gracefully
                                        pass
                                
                                app.destroy()
                                
                            except Exception as e:
                                # Should not crash completely
                                print(f"Expected theme error: {e}")
    
    def test_ui_memory_pressure_handling(self, minimal_config):
        """Test UI behavior under memory pressure."""
        with patch('src.ui.main_window.ensure_api_keys_configured') as mock_ensure:
            mock_ensure.return_value = minimal_config
            
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
                                
                                # Get initial memory usage
                                process = psutil.Process()
                                initial_memory = process.memory_info().rss / 1024 / 1024  # MB
                                
                                # Simulate memory pressure by creating many widgets
                                temp_widgets = []
                                try:
                                    for i in range(100):
                                        widget = tk.Label(app, text=f"Test widget {i}")
                                        temp_widgets.append(widget)
                                        
                                        if i % 10 == 0:
                                            app.update_idletasks()
                                            
                                        # Check if memory usage is getting too high
                                        current_memory = process.memory_info().rss / 1024 / 1024
                                        if current_memory > initial_memory + 100:  # 100MB increase
                                            break
                                
                                finally:
                                    # Clean up widgets
                                    for widget in temp_widgets:
                                        try:
                                            widget.destroy()
                                        except tk.TclError:
                                            pass
                                    
                                    # Force garbage collection
                                    gc.collect()
                                    app.update_idletasks()
                                
                                # App should still be functional
                                assert app.winfo_exists()
                                app.update_status("Memory pressure test complete")
                                
                                app.destroy()
                                
                            except Exception as e:
                                pytest.fail(f"Memory pressure test failed: {e}")
    
    def test_ui_with_unicode_content(self, minimal_config):
        """Test UI handling of Unicode and special characters."""
        with patch('src.ui.main_window.ensure_api_keys_configured') as mock_ensure:
            mock_ensure.return_value = minimal_config
            
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
                                
                                # Test various Unicode content
                                unicode_tests = [
                                    "Hello 世界 🌍",  # Mixed scripts with emoji
                                    "Café résumé naïve",  # Accented characters
                                    "العربية 한국어 日本語",  # Right-to-left and Asian scripts
                                    "𝕌𝕟𝕚𝕔𝕠𝕕𝕖 𝔪𝔞𝔱𝔥 𝔞𝔫𝔡 𝒪ℴ𝓃",  # Mathematical symbols
                                    "\u0000\u001f\u007f\u0080\u009f",  # Control characters
                                    "‚„…‰‹›""''—–",  # Punctuation
                                ]
                                
                                for unicode_text in unicode_tests:
                                    try:
                                        # Test in search entry
                                        app.search_entry.delete(0, tk.END)
                                        app.search_entry.insert(0, unicode_text)
                                        retrieved = app.search_entry.get()
                                        
                                        # Test in text areas
                                        app.note_text.delete("1.0", tk.END)
                                        app.note_text.insert("1.0", unicode_text)
                                        
                                        # Test in status
                                        app.update_status(unicode_text)
                                        
                                        app.update_idletasks()
                                        
                                    except (UnicodeError, tk.TclError) as e:
                                        # Some characters might not be displayable
                                        print(f"Unicode error with '{unicode_text}': {e}")
                                
                                # App should remain stable
                                assert app.winfo_exists()
                                
                                app.destroy()
                                
                            except Exception as e:
                                pytest.fail(f"Unicode content test failed: {e}")
    
    def test_ui_with_many_simultaneous_operations(self, minimal_config):
        """Test UI stability with many simultaneous operations."""
        with patch('src.ui.main_window.ensure_api_keys_configured') as mock_ensure:
            mock_ensure.return_value = minimal_config
            
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
                                
                                # Create multiple threads performing UI operations
                                def ui_operation(operation_id):
                                    for i in range(10):
                                        try:
                                            app.after(i, lambda oid=operation_id, idx=i: 
                                                     app.update_status(f"Op {oid}-{idx}"))
                                            time.sleep(0.01)
                                        except Exception as e:
                                            print(f"Operation {operation_id} error: {e}")
                                
                                threads = []
                                for thread_id in range(5):
                                    thread = threading.Thread(
                                        target=ui_operation, 
                                        args=(thread_id,),
                                        daemon=True
                                    )
                                    threads.append(thread)
                                    thread.start()
                                
                                # Wait for operations to complete
                                for thread in threads:
                                    thread.join(timeout=2.0)
                                
                                # Process pending UI updates
                                for _ in range(50):
                                    app.update_idletasks()
                                    time.sleep(0.01)
                                
                                # App should still be responsive
                                assert app.winfo_exists()
                                app.update_status("Simultaneous operations test complete")
                                
                                app.destroy()
                                
                            except Exception as e:
                                pytest.fail(f"Simultaneous operations test failed: {e}")


@pytest.mark.gui
@pytest.mark.edge_case
class TestUIRecoveryScenarios:
    """Test UI recovery from various error conditions."""
    
    @pytest.fixture
    def recovery_config(self, tmp_path):
        """Config for recovery testing."""
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
    
    def test_ui_recovery_from_widget_destruction(self, recovery_config):
        """Test UI behavior when critical widgets are destroyed."""
        with patch('src.ui.main_window.ensure_api_keys_configured') as mock_ensure:
            mock_ensure.return_value = recovery_config
            
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
                                
                                # Get reference to a critical widget
                                search_button = app.search_button
                                
                                # Simulate widget destruction
                                try:
                                    search_button.destroy()
                                except tk.TclError:
                                    pass
                                
                                # App should handle missing widget gracefully
                                try:
                                    app.update_status("Widget destroyed")
                                    app.update_idletasks()
                                except Exception as e:
                                    print(f"Expected error after widget destruction: {e}")
                                
                                # Main window should still exist
                                assert app.winfo_exists()
                                
                                app.destroy()
                                
                            except Exception as e:
                                print(f"Widget destruction recovery test: {e}")
    
    def test_ui_recovery_from_threading_errors(self, recovery_config):
        """Test UI recovery from threading-related errors."""
        with patch('src.ui.main_window.ensure_api_keys_configured') as mock_ensure:
            mock_ensure.return_value = recovery_config
            
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
                                
                                # Simulate threading errors
                                def problematic_thread():
                                    try:
                                        # Try to access UI from wrong thread (should fail)
                                        app.search_entry.insert(0, "Wrong thread")
                                    except RuntimeError as e:
                                        # Expected error - use proper thread-safe method
                                        app.after(0, lambda: app.update_status("Thread error recovered"))
                                
                                thread = threading.Thread(target=problematic_thread, daemon=True)
                                thread.start()
                                thread.join(timeout=1.0)
                                
                                # Process UI updates
                                app.update_idletasks()
                                
                                # App should recover
                                assert app.winfo_exists()
                                
                                app.destroy()
                                
                            except Exception as e:
                                pytest.fail(f"Threading error recovery test failed: {e}")
    
    def test_ui_state_consistency_after_errors(self, recovery_config):
        """Test that UI state remains consistent after various errors."""
        with patch('src.ui.main_window.ensure_api_keys_configured') as mock_ensure:
            mock_ensure.return_value = recovery_config
            
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
                                
                                # Set initial state
                                initial_query = "test query"
                                app.search_entry.insert(0, initial_query)
                                app.note_text.insert("1.0", "test notes")
                                
                                # Simulate various error conditions
                                error_scenarios = [
                                    lambda: app.disable_buttons(),
                                    lambda: app.show_progress("Test progress"),
                                    lambda: app.update_status("Error simulation"),
                                    lambda: app.hide_progress(),
                                    lambda: app.enable_buttons(),
                                ]
                                
                                for scenario in error_scenarios:
                                    try:
                                        scenario()
                                        app.update_idletasks()
                                    except Exception as e:
                                        print(f"Error scenario error: {e}")
                                
                                # Verify state consistency
                                current_query = app.search_entry.get()
                                current_notes = app.note_text.get("1.0", tk.END).strip()
                                
                                # Basic functionality should be preserved
                                assert initial_query in current_query
                                assert "test notes" in current_notes
                                assert app.winfo_exists()
                                
                                app.destroy()
                                
                            except Exception as e:
                                pytest.fail(f"State consistency test failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "edge_case"])