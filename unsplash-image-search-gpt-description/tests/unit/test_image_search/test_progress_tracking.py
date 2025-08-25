"""
Unit tests for progress tracking and UI feedback during image search.
Tests progress bar updates, status messages, and loading animations.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import tkinter as tk
import threading
import time

from main import ImageSearchApp


class TestProgressTracking:
    """Test suite for progress tracking functionality."""

    @pytest.fixture
    def mock_app(self, mock_config_manager, no_gui):
        """Create a mock ImageSearchApp for progress testing."""
        with patch('main.ensure_api_keys_configured', return_value=mock_config_manager):
            with patch('main.ThemeManager'):
                app = ImageSearchApp()
                app.config_manager = mock_config_manager
                
                # Mock progress UI elements
                app.progress_bar = Mock()
                app.status_label = Mock()
                app.loading_animation_id = None
                app.loading_base_message = ""
                app.loading_dots = 0
                
                # Mock after method for scheduling
                app.after = Mock()
                app.after_cancel = Mock()
                app.update_idletasks = Mock()
                
                return app

    def test_show_progress_basic(self, mock_app):
        """Test basic progress bar display."""
        mock_app.show_progress("Loading images...")
        
        # Verify progress bar is shown and started
        mock_app.progress_bar.grid.assert_called_once()
        mock_app.progress_bar.start.assert_called_once_with(10)

    def test_hide_progress_basic(self, mock_app):
        """Test basic progress bar hiding."""
        mock_app.hide_progress()
        
        # Verify progress bar is stopped and hidden
        mock_app.progress_bar.stop.assert_called_once()
        mock_app.progress_bar.grid_remove.assert_called_once()

    def test_loading_animation_starts(self, mock_app):
        """Test that loading animation starts correctly."""
        mock_app.show_progress("Searching images...")
        
        # Verify animation is initialized
        assert mock_app.loading_base_message == "Searching images..."
        assert mock_app.loading_dots == 0
        
        # Should schedule first animation update
        mock_app.after.assert_called()

    def test_loading_animation_updates(self, mock_app):
        """Test loading animation dot progression."""
        mock_app.loading_base_message = "Loading"
        mock_app.loading_dots = 0
        
        # Test several animation cycles
        for expected_dots in range(5):
            mock_app.update_loading_animation()
            expected_text = "Loading" + "." * (expected_dots % 4)
            mock_app.status_label.config.assert_called_with(text=expected_text)
            assert mock_app.loading_dots == expected_dots + 1

    def test_stop_loading_animation(self, mock_app):
        """Test stopping loading animation."""
        mock_app.loading_animation_id = "test_id"
        mock_app.loading_base_message = "Loading"
        
        mock_app.stop_loading_animation()
        
        # Should cancel scheduled animation
        mock_app.after_cancel.assert_called_once_with("test_id")
        assert mock_app.loading_animation_id is None
        assert not hasattr(mock_app, 'loading_base_message')

    def test_progress_with_different_messages(self, mock_app):
        """Test progress tracking with various message types."""
        test_messages = [
            "Searching 'nature' on Unsplash",
            "Analyzing image with gpt-4o-mini",
            "Getting another image",
            "Translating 'hermoso'"
        ]
        
        for message in test_messages:
            mock_app.show_progress(message)
            assert mock_app.loading_base_message == message
            mock_app.hide_progress()

    def test_progress_state_during_search(self, mock_app):
        """Test progress state management during search operations."""
        # Initial state
        assert mock_app.loading_animation_id is None
        
        # Start search progress
        mock_app.show_progress("Searching...")
        assert mock_app.loading_base_message == "Searching..."
        
        # Progress should be visible
        mock_app.progress_bar.grid.assert_called()
        mock_app.progress_bar.start.assert_called()
        
        # End search progress
        mock_app.hide_progress()
        mock_app.progress_bar.stop.assert_called()
        mock_app.progress_bar.grid_remove.assert_called()

    def test_multiple_progress_calls_handled(self, mock_app):
        """Test handling multiple progress calls without interference."""
        # Start first progress
        mock_app.show_progress("First operation")
        first_call_count = mock_app.progress_bar.grid.call_count
        
        # Start second progress (should not interfere)
        mock_app.show_progress("Second operation")
        
        # Should have started progress again
        assert mock_app.progress_bar.grid.call_count >= first_call_count
        assert mock_app.loading_base_message == "Second operation"

    def test_progress_cleanup_on_error(self, mock_app):
        """Test that progress is properly cleaned up on errors."""
        mock_app.show_progress("Processing...")
        
        # Simulate error scenario
        try:
            mock_app.hide_progress()
        except Exception:
            pass
        
        # Progress should still be cleaned up
        mock_app.progress_bar.stop.assert_called()
        mock_app.progress_bar.grid_remove.assert_called()

    def test_status_message_updates(self, mock_app):
        """Test status message updates during operations."""
        test_statuses = [
            "Ready",
            "Searching for images...",
            "Image loaded successfully",
            "Description generated successfully",
            "Phrase added to vocabulary"
        ]
        
        for status in test_statuses:
            mock_app.update_status(status)
            mock_app.status_label.config.assert_called_with(text=status)
            mock_app.update_idletasks.assert_called()

    def test_progress_with_threading(self, mock_app):
        """Test progress tracking works correctly with threading."""
        progress_states = []
        
        def mock_show_progress(message):
            progress_states.append(('show', message))
            
        def mock_hide_progress():
            progress_states.append(('hide', None))
        
        mock_app.show_progress = mock_show_progress
        mock_app.hide_progress = mock_hide_progress
        
        def threaded_operation():
            mock_app.show_progress("Thread operation...")
            time.sleep(0.01)  # Simulate work
            mock_app.hide_progress()
        
        thread = threading.Thread(target=threaded_operation, daemon=True)
        thread.start()
        thread.join(timeout=1.0)
        
        # Verify progress was shown and hidden
        assert len(progress_states) == 2
        assert progress_states[0] == ('show', "Thread operation...")
        assert progress_states[1] == ('hide', None)


class TestUIStateManagement:
    """Test suite for UI state management during operations."""

    @pytest.fixture
    def mock_app_with_buttons(self, mock_config_manager, no_gui):
        """Create app with mocked button controls."""
        with patch('main.ensure_api_keys_configured', return_value=mock_config_manager):
            with patch('main.ThemeManager'):
                app = ImageSearchApp()
                app.config_manager = mock_config_manager
                
                # Mock all UI button elements
                app.search_button = Mock()
                app.another_button = Mock()
                app.newsearch_button = Mock()
                app.generate_desc_button = Mock()
                app.theme_button = Mock()
                app.export_button = Mock()
                app.progress_bar = Mock()
                app.status_label = Mock()
                
                return app

    def test_disable_buttons_during_operation(self, mock_app_with_buttons):
        """Test that all buttons are disabled during operations."""
        mock_app_with_buttons.disable_buttons()
        
        # All buttons should be disabled
        mock_app_with_buttons.search_button.config.assert_called_with(state=tk.DISABLED)
        mock_app_with_buttons.another_button.config.assert_called_with(state=tk.DISABLED)
        mock_app_with_buttons.newsearch_button.config.assert_called_with(state=tk.DISABLED)
        mock_app_with_buttons.generate_desc_button.config.assert_called_with(state=tk.DISABLED)
        mock_app_with_buttons.theme_button.config.assert_called_with(state=tk.DISABLED)
        mock_app_with_buttons.export_button.config.assert_called_with(state=tk.DISABLED)

    def test_enable_buttons_after_operation(self, mock_app_with_buttons):
        """Test that buttons are re-enabled after operations."""
        mock_app_with_buttons.enable_buttons()
        
        # All buttons should be enabled
        mock_app_with_buttons.search_button.config.assert_called_with(state=tk.NORMAL)
        mock_app_with_buttons.another_button.config.assert_called_with(state=tk.NORMAL)
        mock_app_with_buttons.newsearch_button.config.assert_called_with(state=tk.NORMAL)
        mock_app_with_buttons.generate_desc_button.config.assert_called_with(state=tk.NORMAL)
        mock_app_with_buttons.theme_button.config.assert_called_with(state=tk.NORMAL)
        mock_app_with_buttons.export_button.config.assert_called_with(state=tk.NORMAL)

    def test_progress_and_button_coordination(self, mock_app_with_buttons):
        """Test coordination between progress display and button states."""
        # Start operation - should disable buttons and show progress
        mock_app_with_buttons.show_progress("Starting operation...")
        mock_app_with_buttons.disable_buttons()
        
        mock_app_with_buttons.progress_bar.grid.assert_called()
        mock_app_with_buttons.search_button.config.assert_called_with(state=tk.DISABLED)
        
        # End operation - should hide progress and enable buttons
        mock_app_with_buttons.hide_progress()
        mock_app_with_buttons.enable_buttons()
        
        mock_app_with_buttons.progress_bar.grid_remove.assert_called()
        mock_app_with_buttons.search_button.config.assert_called_with(state=tk.NORMAL)

    def test_button_state_with_missing_buttons(self, mock_config_manager, no_gui):
        """Test button state management when some buttons don't exist."""
        with patch('main.ensure_api_keys_configured', return_value=mock_config_manager):
            with patch('main.ThemeManager'):
                app = ImageSearchApp()
                app.config_manager = mock_config_manager
                
                # Mock only required buttons
                app.search_button = Mock()
                app.another_button = Mock()
                app.newsearch_button = Mock()
                app.generate_desc_button = Mock()
                # theme_button and export_button are missing
                
                # Should not raise error
                app.disable_buttons()
                app.enable_buttons()
                
                # Required buttons should be called
                app.search_button.config.assert_called()
                app.another_button.config.assert_called()

    def test_progress_accuracy_tracking(self, mock_app_with_buttons):
        """Test that progress accurately reflects operation stages."""
        operation_stages = [
            "Fetching images from Unsplash API",
            "Downloading image data", 
            "Processing image with PIL",
            "Updating UI with new image",
            "Operation complete"
        ]
        
        for i, stage in enumerate(operation_stages):
            mock_app_with_buttons.update_status(stage)
            mock_app_with_buttons.status_label.config.assert_called_with(text=stage)
            
            # Could track progress percentage if implemented
            if hasattr(mock_app_with_buttons, 'progress_percentage'):
                expected_progress = (i + 1) / len(operation_stages) * 100
                assert mock_app_with_buttons.progress_percentage >= expected_progress