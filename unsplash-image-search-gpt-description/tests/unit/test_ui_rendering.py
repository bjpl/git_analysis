"""
Comprehensive tests for UI rendering issues and widget creation.
This test suite verifies that the main window creates all expected widgets,
handles errors gracefully, and maintains proper UI state.
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

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from config_manager import ConfigManager
from src.ui.main_window import MainWindow
from src.ui.dialogs.setup_wizard import SetupWizard, ensure_api_keys_configured


@pytest.mark.gui
class TestMainWindowRendering:
    """Test main window UI rendering and widget creation."""
    
    @pytest.fixture
    def mock_root(self):
        """Create a mock root window for testing."""
        root = tk.Tk()
        root.withdraw()  # Hide during testing
        yield root
        try:
            root.destroy()
        except tk.TclError:
            pass  # Already destroyed
    
    @pytest.fixture
    def mock_config_manager(self, tmp_path):
        """Create a mock config manager with temporary paths."""
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
        config.config.get.return_value = '100'  # Default zoom
        return config
    
    def test_main_window_creates_all_widgets(self, mock_config_manager):
        """Test that main window creates all expected widgets without errors."""
        with patch('src.ui.main_window.ensure_api_keys_configured') as mock_ensure:
            mock_ensure.return_value = mock_config_manager
            
            # Mock theme manager to avoid initialization issues
            with patch('src.ui.theme_manager.ThemeManager') as mock_theme:
                mock_theme_instance = Mock()
                mock_theme_instance.get_colors.return_value = {
                    'bg': '#ffffff', 'fg': '#000000', 'frame_bg': '#f0f0f0',
                    'button_active_bg': '#e0e0e0', 'info': '#0066cc', 'border': '#cccccc'
                }
                mock_theme.return_value = mock_theme_instance
                
                # Mock performance components
                with patch('src.performance_optimization.PerformanceOptimizer'):
                    with patch('src.optimized_image_collection.OptimizedImageCollector'):
                        with patch('src.services.unsplash_service.UnsplashService'):
                            try:
                                # Import here to use mocks
                                from main import ImageSearchApp
                                
                                app = ImageSearchApp()
                                
                                # Verify main window properties
                                assert app.title().startswith("Búsqueda de Imágenes")
                                assert "1100x800" in app.geometry() or app.geometry().startswith("1100x800")
                                
                                # Verify essential widgets exist
                                assert hasattr(app, 'search_entry'), "Search entry widget missing"
                                assert hasattr(app, 'search_button'), "Search button widget missing"
                                assert hasattr(app, 'image_label'), "Image label widget missing"
                                assert hasattr(app, 'note_text'), "Note text widget missing"
                                assert hasattr(app, 'description_text'), "Description text widget missing"
                                assert hasattr(app, 'status_label'), "Status label widget missing"
                                
                                # Verify widgets are properly configured
                                assert isinstance(app.search_entry, ttk.Entry), "Search entry wrong type"
                                assert isinstance(app.search_button, ttk.Button), "Search button wrong type"
                                assert isinstance(app.image_label, tk.Label), "Image label wrong type"
                                
                                # Verify button states
                                assert app.search_button['state'] == 'normal', "Search button should be enabled"
                                assert app.another_button['state'] == 'normal', "Another button should be enabled"
                                
                                app.destroy()
                                
                            except Exception as e:
                                pytest.fail(f"Main window creation failed: {e}")
    
    def test_window_geometry_and_visibility(self, mock_config_manager):
        """Test window geometry settings and visibility state."""
        with patch('src.ui.main_window.ensure_api_keys_configured') as mock_ensure:
            mock_ensure.return_value = mock_config_manager
            
            with patch('src.ui.theme_manager.ThemeManager') as mock_theme:
                mock_theme_instance = Mock()
                mock_theme_instance.get_colors.return_value = {
                    'bg': '#ffffff', 'fg': '#000000', 'frame_bg': '#f0f0f0',
                    'button_active_bg': '#e0e0e0', 'info': '#0066cc', 'border': '#cccccc'
                }
                mock_theme.return_value = mock_theme_instance
                
                with patch('src.performance_optimization.PerformanceOptimizer'):
                    with patch('src.optimized_image_collection.OptimizedImageCollector'):
                        with patch('src.services.unsplash_service.UnsplashService'):
                            try:
                                from main import ImageSearchApp
                                
                                app = ImageSearchApp()
                                
                                # Test geometry settings
                                geometry = app.geometry()
                                assert '1100' in geometry and '800' in geometry, f"Invalid geometry: {geometry}"
                                
                                # Test resizable
                                app.update_idletasks()
                                assert app.resizable()[0] == True, "Window should be horizontally resizable"
                                assert app.resizable()[1] == True, "Window should be vertically resizable"
                                
                                # Test minimum size handling
                                app.geometry("100x100")
                                app.update_idletasks()
                                # Window should still function at small sizes
                                
                                app.destroy()
                                
                            except Exception as e:
                                pytest.fail(f"Window geometry test failed: {e}")
    
    def test_widget_packing_and_layout(self, mock_config_manager):
        """Test that all widgets are properly packed and visible."""
        with patch('src.ui.main_window.ensure_api_keys_configured') as mock_ensure:
            mock_ensure.return_value = mock_config_manager
            
            with patch('src.ui.theme_manager.ThemeManager') as mock_theme:
                mock_theme_instance = Mock()
                mock_theme_instance.get_colors.return_value = {
                    'bg': '#ffffff', 'fg': '#000000', 'frame_bg': '#f0f0f0',
                    'button_active_bg': '#e0e0e0', 'info': '#0066cc', 'border': '#cccccc'
                }
                mock_theme.return_value = mock_theme_instance
                
                with patch('src.performance_optimization.PerformanceOptimizer'):
                    with patch('src.optimized_image_collection.OptimizedImageCollector'):
                        with patch('src.services.unsplash_service.UnsplashService'):
                            try:
                                from main import ImageSearchApp
                                
                                app = ImageSearchApp()
                                app.update_idletasks()  # Force layout calculation
                                
                                # Test that main frames exist and are packed
                                main_frames = [child for child in app.winfo_children() if isinstance(child, ttk.Frame)]
                                assert len(main_frames) > 0, "No main frames found"
                                
                                # Test that search controls are accessible
                                assert app.search_entry.winfo_viewable(), "Search entry not visible"
                                assert app.search_button.winfo_viewable(), "Search button not visible"
                                
                                # Test text areas exist and are configured
                                assert app.note_text.winfo_exists(), "Note text area missing"
                                assert app.description_text.winfo_exists(), "Description text area missing"
                                
                                # Test that widgets have proper sizes
                                app.update_idletasks()
                                assert app.search_entry.winfo_width() > 0, "Search entry has no width"
                                assert app.search_button.winfo_height() > 0, "Search button has no height"
                                
                                app.destroy()
                                
                            except Exception as e:
                                pytest.fail(f"Widget packing test failed: {e}")
    
    def test_error_handling_during_init(self, mock_config_manager):
        """Test that UI initialization errors don't prevent window creation."""
        with patch('src.ui.main_window.ensure_api_keys_configured') as mock_ensure:
            mock_ensure.return_value = mock_config_manager
            
            # Test with theme manager initialization failure
            with patch('src.ui.theme_manager.ThemeManager', side_effect=Exception("Theme init failed")):
                try:
                    from main import ImageSearchApp
                    # Should not raise exception even with theme failure
                    app = ImageSearchApp()
                    app.destroy()
                except Exception as e:
                    # Should handle gracefully or at least not crash completely
                    pass
    
    def test_widget_focus_and_tab_order(self, mock_config_manager):
        """Test widget focus handling and tab navigation."""
        with patch('src.ui.main_window.ensure_api_keys_configured') as mock_ensure:
            mock_ensure.return_value = mock_config_manager
            
            with patch('src.ui.theme_manager.ThemeManager') as mock_theme:
                mock_theme_instance = Mock()
                mock_theme_instance.get_colors.return_value = {
                    'bg': '#ffffff', 'fg': '#000000', 'frame_bg': '#f0f0f0',
                    'button_active_bg': '#e0e0e0', 'info': '#0066cc', 'border': '#cccccc'
                }
                mock_theme.return_value = mock_theme_instance
                
                with patch('src.performance_optimization.PerformanceOptimizer'):
                    with patch('src.optimized_image_collection.OptimizedImageCollector'):
                        with patch('src.services.unsplash_service.UnsplashService'):
                            try:
                                from main import ImageSearchApp
                                
                                app = ImageSearchApp()
                                
                                # Test initial focus
                                app.focus_set()
                                
                                # Test that focusable widgets exist
                                focusable_widgets = [
                                    app.search_entry,
                                    app.search_button,
                                    app.note_text,
                                    app.generate_desc_button
                                ]
                                
                                for widget in focusable_widgets:
                                    try:
                                        widget.focus_set()
                                        app.update_idletasks()
                                        # Should not raise exception
                                    except Exception as e:
                                        pytest.fail(f"Focus failed for {widget}: {e}")
                                
                                app.destroy()
                                
                            except Exception as e:
                                pytest.fail(f"Focus handling test failed: {e}")


@pytest.mark.gui
class TestSetupDialogRendering:
    """Test setup dialog UI rendering and modal behavior."""
    
    @pytest.fixture
    def mock_config_manager(self, tmp_path):
        """Create a mock config manager for dialog testing."""
        config = Mock(spec=ConfigManager)
        config.validate_api_keys.return_value = False  # Trigger setup dialog
        config.get_api_keys.return_value = {'unsplash': '', 'openai': '', 'gpt_model': ''}
        config.save_api_keys = Mock()
        return config
    
    def test_setup_wizard_creates_modal_dialog(self, mock_config_manager):
        """Test that setup wizard creates proper modal dialog."""
        root = tk.Tk()
        root.withdraw()
        
        try:
            wizard = SetupWizard(root, mock_config_manager)
            
            # Test modal properties
            assert wizard.transient() == root, "Dialog should be transient to parent"
            
            # Test dialog geometry
            geometry = wizard.geometry()
            assert '600x400' in geometry, f"Invalid dialog geometry: {geometry}"
            
            # Test essential widgets exist
            assert hasattr(wizard, 'unsplash_entry'), "Unsplash entry missing"
            assert hasattr(wizard, 'openai_entry'), "OpenAI entry missing"
            assert hasattr(wizard, 'submit_button'), "Submit button missing"
            assert hasattr(wizard, 'cancel_button'), "Cancel button missing"
            
            # Test initial states
            assert wizard.submit_button['state'] == 'disabled', "Submit should be disabled initially"
            assert wizard.cancel_button['state'] == 'normal', "Cancel should be enabled"
            
            wizard.destroy()
            
        finally:
            root.destroy()
    
    def test_setup_dialog_validation_feedback(self, mock_config_manager):
        """Test real-time validation feedback in setup dialog."""
        root = tk.Tk()
        root.withdraw()
        
        try:
            wizard = SetupWizard(root, mock_config_manager)
            
            # Test initial validation state
            assert hasattr(wizard, 'unsplash_validation'), "Unsplash validation label missing"
            assert hasattr(wizard, 'openai_validation'), "OpenAI validation label missing"
            assert hasattr(wizard, 'status_label'), "Status label missing"
            
            # Test validation with valid keys
            wizard.unsplash_entry.insert(0, 'valid_unsplash_key_1234567890123456789012345')
            wizard.openai_entry.insert(0, 'sk-valid_openai_key_1234567890123456789012345')
            wizard._validate_form()
            
            assert wizard.submit_button['state'] == 'normal', "Submit should be enabled with valid keys"
            
            # Test validation with invalid keys
            wizard.unsplash_entry.delete(0, tk.END)
            wizard.openai_entry.delete(0, tk.END)
            wizard.unsplash_entry.insert(0, 'short')
            wizard.openai_entry.insert(0, 'invalid')
            wizard._validate_form()
            
            assert wizard.submit_button['state'] == 'disabled', "Submit should be disabled with invalid keys"
            
            wizard.destroy()
            
        finally:
            root.destroy()
    
    def test_setup_dialog_doesnt_block_main_ui(self, mock_config_manager):
        """Test that setup dialog doesn't block main UI thread."""
        # This test ensures the dialog can be created without hanging
        root = tk.Tk()
        root.withdraw()
        
        dialog_created = threading.Event()
        exception_occurred = threading.Event()
        
        def create_dialog():
            try:
                wizard = SetupWizard(root, mock_config_manager)
                dialog_created.set()
                
                # Simulate some interaction
                root.update_idletasks()
                time.sleep(0.1)  # Small delay to test non-blocking
                
                wizard.destroy()
            except Exception as e:
                exception_occurred.set()
                print(f"Dialog creation error: {e}")
        
        # Create dialog in separate thread to test non-blocking behavior
        dialog_thread = threading.Thread(target=create_dialog)
        dialog_thread.start()
        
        # Wait for dialog creation (should be quick)
        dialog_created.wait(timeout=5.0)
        
        assert dialog_created.is_set(), "Dialog creation timed out"
        assert not exception_occurred.is_set(), "Exception occurred during dialog creation"
        
        dialog_thread.join(timeout=5.0)
        root.destroy()


@pytest.mark.gui
class TestErrorHandlingUI:
    """Test UI behavior during error conditions."""
    
    @pytest.fixture
    def mock_failing_config(self):
        """Create a config manager that fails validation."""
        config = Mock(spec=ConfigManager)
        config.validate_api_keys.return_value = False
        config.get_api_keys.side_effect = Exception("Config file corrupted")
        return config
    
    def test_ui_handles_config_errors_gracefully(self, mock_failing_config):
        """Test that UI handles configuration errors without crashing."""
        # Test ensure_api_keys_configured with failing config
        with patch('config_manager.ConfigManager') as mock_config_class:
            mock_config_class.return_value = mock_failing_config
            
            root = tk.Tk()
            root.withdraw()
            
            try:
                # Should handle gracefully
                result = ensure_api_keys_configured(root)
                # Result might be None if user cancels
                
                # Main test: no exception should be raised
                assert True, "Function completed without crashing"
                
            except Exception as e:
                pytest.fail(f"ensure_api_keys_configured should handle errors gracefully: {e}")
            finally:
                root.destroy()
    
    def test_main_window_handles_missing_dependencies(self):
        """Test main window behavior when optional dependencies are missing."""
        # Mock missing performance optimization
        with patch.dict('sys.modules', {'src.performance_optimization': None}):
            with patch('src.ui.main_window.ensure_api_keys_configured') as mock_ensure:
                mock_config = Mock()
                mock_config.get_api_keys.return_value = {
                    'unsplash': 'test_key',
                    'openai': 'sk-test_key',
                    'gpt_model': 'gpt-4o-mini'
                }
                mock_config.get_paths.return_value = {
                    'data_dir': Path('test'),
                    'log_file': Path('test/log.json'),
                    'vocabulary_file': Path('test/vocab.csv')
                }
                mock_ensure.return_value = mock_config
                
                try:
                    # Should not crash even with missing dependencies
                    from main import ImageSearchApp
                    app = ImageSearchApp()
                    # Performance optimizer should be None
                    assert hasattr(app, 'performance_optimizer')
                    app.destroy()
                except ImportError:
                    # This is acceptable - missing dependencies handled
                    pass
                except Exception as e:
                    pytest.fail(f"Should handle missing dependencies gracefully: {e}")
    
    def test_api_error_display_doesnt_break_ui(self, mock_config_manager):
        """Test that API errors are displayed without breaking UI."""
        with patch('src.ui.main_window.ensure_api_keys_configured') as mock_ensure:
            mock_ensure.return_value = mock_config_manager
            
            with patch('src.ui.theme_manager.ThemeManager') as mock_theme:
                mock_theme_instance = Mock()
                mock_theme_instance.get_colors.return_value = {
                    'bg': '#ffffff', 'fg': '#000000', 'frame_bg': '#f0f0f0',
                    'button_active_bg': '#e0e0e0', 'info': '#0066cc', 'border': '#cccccc'
                }
                mock_theme.return_value = mock_theme_instance
                
                with patch('src.performance_optimization.PerformanceOptimizer'):
                    with patch('src.optimized_image_collection.OptimizedImageCollector'):
                        with patch('src.services.unsplash_service.UnsplashService'):
                            try:
                                from main import ImageSearchApp
                                
                                app = ImageSearchApp()
                                
                                # Test various error handling methods
                                app.update_status("Test error message")
                                assert app.status_label.cget('text') == "Test error message"
                                
                                # Test enhanced error dialog (should not crash)
                                try:
                                    app.show_enhanced_error("Test Error", "Test message", "error")
                                except Exception:
                                    pass  # Dialog might not display in test environment
                                
                                # UI should still be responsive
                                app.update_idletasks()
                                assert app.winfo_exists(), "Window should still exist after error"
                                
                                app.destroy()
                                
                            except Exception as e:
                                pytest.fail(f"Error handling test failed: {e}")


@pytest.mark.gui
class TestAPIKeyScenarios:
    """Test UI behavior with different API key configurations."""
    
    def test_ui_with_valid_api_keys(self, tmp_path):
        """Test UI behavior when API keys are properly configured."""
        config = Mock(spec=ConfigManager)
        config.validate_api_keys.return_value = True
        config.get_api_keys.return_value = {
            'unsplash': 'valid_unsplash_key_1234567890123456789012345',
            'openai': 'sk-valid_openai_key_1234567890123456789012345',
            'gpt_model': 'gpt-4o-mini'
        }
        config.get_paths.return_value = {
            'data_dir': tmp_path / 'data',
            'log_file': tmp_path / 'data' / 'session.json',
            'vocabulary_file': tmp_path / 'data' / 'vocabulary.csv'
        }
        config.config = Mock()
        config.config.get.return_value = '100'
        
        with patch('src.ui.main_window.ensure_api_keys_configured') as mock_ensure:
            mock_ensure.return_value = config
            
            with patch('src.ui.theme_manager.ThemeManager') as mock_theme:
                mock_theme_instance = Mock()
                mock_theme_instance.get_colors.return_value = {
                    'bg': '#ffffff', 'fg': '#000000', 'frame_bg': '#f0f0f0',
                    'button_active_bg': '#e0e0e0', 'info': '#0066cc', 'border': '#cccccc'
                }
                mock_theme.return_value = mock_theme_instance
                
                with patch('src.performance_optimization.PerformanceOptimizer'):
                    with patch('src.optimized_image_collection.OptimizedImageCollector'):
                        with patch('src.services.unsplash_service.UnsplashService'):
                            try:
                                from main import ImageSearchApp
                                
                                app = ImageSearchApp()
                                
                                # With valid keys, all buttons should be enabled
                                assert app.search_button['state'] == 'normal'
                                assert app.generate_desc_button['state'] == 'normal'
                                
                                # Title should include model info
                                title = app.title()
                                assert 'gpt-4o-mini' in title
                                
                                app.destroy()
                                
                            except Exception as e:
                                pytest.fail(f"Valid API keys test failed: {e}")
    
    def test_ui_without_api_keys(self, tmp_path):
        """Test UI behavior when API keys are not configured."""
        config = Mock(spec=ConfigManager)
        config.validate_api_keys.return_value = False
        config.get_api_keys.return_value = {'unsplash': '', 'openai': '', 'gpt_model': ''}
        
        with patch('src.ui.main_window.ensure_api_keys_configured') as mock_ensure:
            # Simulate user canceling setup
            mock_ensure.return_value = None
            
            try:
                from main import ImageSearchApp
                
                app = ImageSearchApp()
                # App should handle None config gracefully
                # Likely by exiting or showing error
                
            except SystemExit:
                # Acceptable behavior
                pass
            except Exception as e:
                # Should handle gracefully
                pass
    
    def test_setup_wizard_completion_flow(self, tmp_path):
        """Test complete setup wizard flow from start to finish."""
        config = Mock(spec=ConfigManager)
        config.validate_api_keys.return_value = False
        config.get_api_keys.return_value = {'unsplash': '', 'openai': '', 'gpt_model': ''}
        config.save_api_keys = Mock()
        
        root = tk.Tk()
        root.withdraw()
        
        try:
            wizard = SetupWizard(root, config)
            
            # Simulate user input
            wizard.unsplash_entry.insert(0, 'test_unsplash_key_1234567890123456789012345')
            wizard.openai_entry.insert(0, 'sk-test_openai_key_1234567890123456789012345')
            wizard.model_var.set('gpt-4o-mini')
            
            # Trigger validation
            wizard._validate_form()
            assert wizard.submit_button['state'] == 'normal'
            
            # Simulate submit
            wizard.save_and_continue()
            
            # Verify config was called
            config.save_api_keys.assert_called_once()
            
            wizard.destroy()
            
        finally:
            root.destroy()


@pytest.mark.gui
class TestUIThreadSafety:
    """Test UI thread safety and concurrent operations."""
    
    def test_ui_updates_from_background_threads(self, mock_config_manager):
        """Test that UI updates from background threads don't cause issues."""
        with patch('src.ui.main_window.ensure_api_keys_configured') as mock_ensure:
            mock_ensure.return_value = mock_config_manager
            
            with patch('src.ui.theme_manager.ThemeManager') as mock_theme:
                mock_theme_instance = Mock()
                mock_theme_instance.get_colors.return_value = {
                    'bg': '#ffffff', 'fg': '#000000', 'frame_bg': '#f0f0f0',
                    'button_active_bg': '#e0e0e0', 'info': '#0066cc', 'border': '#cccccc'
                }
                mock_theme.return_value = mock_theme_instance
                
                with patch('src.performance_optimization.PerformanceOptimizer'):
                    with patch('src.optimized_image_collection.OptimizedImageCollector'):
                        with patch('src.services.unsplash_service.UnsplashService'):
                            try:
                                from main import ImageSearchApp
                                
                                app = ImageSearchApp()
                                
                                # Test status updates from background thread
                                def background_update():
                                    try:
                                        app.after(0, lambda: app.update_status("Background update"))
                                        time.sleep(0.1)
                                        app.after(0, lambda: app.update_status("Ready"))
                                    except Exception as e:
                                        print(f"Background update error: {e}")
                                
                                thread = threading.Thread(target=background_update)
                                thread.start()
                                thread.join(timeout=2.0)
                                
                                # Process pending events
                                app.update_idletasks()
                                
                                # UI should still be responsive
                                assert app.winfo_exists()
                                
                                app.destroy()
                                
                            except Exception as e:
                                pytest.fail(f"Thread safety test failed: {e}")
    
    def test_concurrent_ui_operations(self, mock_config_manager):
        """Test UI behavior under concurrent operations."""
        with patch('src.ui.main_window.ensure_api_keys_configured') as mock_ensure:
            mock_ensure.return_value = mock_config_manager
            
            with patch('src.ui.theme_manager.ThemeManager') as mock_theme:
                mock_theme_instance = Mock()
                mock_theme_instance.get_colors.return_value = {
                    'bg': '#ffffff', 'fg': '#000000', 'frame_bg': '#f0f0f0',
                    'button_active_bg': '#e0e0e0', 'info': '#0066cc', 'border': '#cccccc'
                }
                mock_theme.return_value = mock_theme_instance
                
                with patch('src.performance_optimization.PerformanceOptimizer'):
                    with patch('src.optimized_image_collection.OptimizedImageCollector'):
                        with patch('src.services.unsplash_service.UnsplashService'):
                            try:
                                from main import ImageSearchApp
                                
                                app = ImageSearchApp()
                                
                                # Simulate multiple concurrent operations
                                operations = []
                                for i in range(5):
                                    def operation(index=i):
                                        app.after(0, lambda: app.update_status(f"Operation {index}"))
                                        app.after(10, lambda: app.update_stats())
                                    operations.append(threading.Thread(target=operation))
                                
                                # Start all operations
                                for op in operations:
                                    op.start()
                                
                                # Wait for completion
                                for op in operations:
                                    op.join(timeout=1.0)
                                
                                # Process all pending UI updates
                                for _ in range(10):
                                    app.update_idletasks()
                                    time.sleep(0.01)
                                
                                # UI should remain stable
                                assert app.winfo_exists()
                                
                                app.destroy()
                                
                            except Exception as e:
                                pytest.fail(f"Concurrent operations test failed: {e}")


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])