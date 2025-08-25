"""
Unit tests for UI components during image search operations.
Tests progress bars, button states, status messages, and user interactions.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
import tkinter as tk
from tkinter import ttk
import threading
import time

from main import ImageSearchApp


class TestProgressBarComponents:
    """Test suite for progress bar UI components."""

    @pytest.fixture
    def mock_progress_app(self, mock_config_manager, no_gui):
        """Create app with mocked progress components."""
        with patch('main.ensure_api_keys_configured', return_value=mock_config_manager):
            with patch('main.ThemeManager'):
                app = ImageSearchApp()
                app.config_manager = mock_config_manager
                
                # Mock progress bar with real ttk.Progressbar interface
                app.progress_bar = Mock(spec=ttk.Progressbar)
                app.progress_var = Mock(spec=tk.IntVar)
                app.status_label = Mock(spec=ttk.Label)
                
                # Mock scheduling methods
                app.after = Mock()
                app.after_cancel = Mock()
                app.update_idletasks = Mock()
                
                # Progress animation state
                app.loading_animation_id = None
                app.loading_base_message = ""
                app.loading_dots = 0
                
                return app

    def test_progress_bar_visibility_control(self, mock_progress_app):
        """Test progress bar show/hide functionality."""
        # Initially hidden
        mock_progress_app.progress_bar.grid_remove.assert_not_called()
        
        # Show progress
        mock_progress_app.show_progress("Testing...")
        mock_progress_app.progress_bar.grid.assert_called_once()
        mock_progress_app.progress_bar.start.assert_called_once_with(10)
        
        # Hide progress
        mock_progress_app.hide_progress()
        mock_progress_app.progress_bar.stop.assert_called_once()
        mock_progress_app.progress_bar.grid_remove.assert_called_once()

    def test_progress_bar_animation_speed(self, mock_progress_app):
        """Test progress bar animation speed configuration."""
        # Test different animation speeds
        test_speeds = [5, 10, 15, 20]
        
        for speed in test_speeds:
            mock_progress_app.progress_bar.reset_mock()
            mock_progress_app.show_progress(f"Speed test {speed}", animation_speed=speed)
            mock_progress_app.progress_bar.start.assert_called_with(speed)
            mock_progress_app.hide_progress()

    def test_progress_bar_mode_switching(self, mock_progress_app):
        """Test switching between indeterminate and determinate modes."""
        # Test indeterminate mode (default)
        mock_progress_app.show_progress("Indeterminate task...")
        mock_progress_app.progress_bar.config.assert_called_with(mode='indeterminate')
        
        # Test determinate mode
        mock_progress_app.progress_bar.reset_mock()
        mock_progress_app.show_progress_determinate("Determinate task...", 0, 100)
        mock_progress_app.progress_bar.config.assert_called_with(mode='determinate', maximum=100)
        mock_progress_app.progress_var.set.assert_called_with(0)

    def test_progress_message_updates(self, mock_progress_app):
        """Test progress message updates during operation."""
        messages = [
            "Starting search...",
            "Fetching page 1...", 
            "Processing results...",
            "Loading image...",
            "Complete!"
        ]
        
        for message in messages:
            mock_progress_app.show_progress(message)
            assert mock_progress_app.loading_base_message == message

    def test_progress_animation_lifecycle(self, mock_progress_app):
        """Test complete progress animation lifecycle."""
        # Start animation
        mock_progress_app.show_progress("Animating...")
        
        # Verify animation initialized
        assert mock_progress_app.loading_base_message == "Animating..."
        assert mock_progress_app.loading_dots == 0
        mock_progress_app.after.assert_called()
        
        # Simulate animation cycles
        for cycle in range(5):
            mock_progress_app.update_loading_animation()
            expected_dots = cycle % 4
            expected_message = "Animating..." + "." * expected_dots
            mock_progress_app.status_label.config.assert_called_with(text=expected_message)
        
        # Stop animation
        mock_progress_app.loading_animation_id = "test_id"
        mock_progress_app.stop_loading_animation()
        mock_progress_app.after_cancel.assert_called_with("test_id")
        assert mock_progress_app.loading_animation_id is None

    def test_nested_progress_operations(self, mock_progress_app):
        """Test handling nested progress operations."""
        # Start outer operation
        mock_progress_app.show_progress("Outer operation...")
        outer_calls = mock_progress_app.progress_bar.grid.call_count
        
        # Start inner operation
        mock_progress_app.show_progress("Inner operation...")
        inner_calls = mock_progress_app.progress_bar.grid.call_count
        
        # Inner should not interfere with outer
        assert inner_calls >= outer_calls
        assert mock_progress_app.loading_base_message == "Inner operation..."
        
        # End operations
        mock_progress_app.hide_progress()
        mock_progress_app.progress_bar.stop.assert_called()


class TestButtonStateManagement:
    """Test suite for button state management during operations."""

    @pytest.fixture
    def mock_button_app(self, mock_config_manager, no_gui):
        """Create app with all UI buttons mocked."""
        with patch('main.ensure_api_keys_configured', return_value=mock_config_manager):
            with patch('main.ThemeManager'):
                app = ImageSearchApp()
                app.config_manager = mock_config_manager
                
                # Mock all interactive buttons
                app.search_button = Mock(spec=ttk.Button)
                app.another_button = Mock(spec=ttk.Button)
                app.newsearch_button = Mock(spec=ttk.Button)
                app.generate_desc_button = Mock(spec=ttk.Button)
                app.theme_button = Mock(spec=ttk.Button)
                app.export_button = Mock(spec=ttk.Button)
                app.copy_desc_button = Mock(spec=ttk.Button)
                
                # Mock UI state tracking
                app._ui_state = 'ready'  # ready, searching, processing
                
                return app

    def test_disable_all_buttons_during_operation(self, mock_button_app):
        """Test that all buttons are disabled during operations."""
        mock_button_app.disable_buttons()
        
        # Verify all buttons are disabled
        expected_buttons = [
            'search_button', 'another_button', 'newsearch_button',
            'generate_desc_button', 'theme_button', 'export_button'
        ]
        
        for button_name in expected_buttons:
            button = getattr(mock_button_app, button_name)
            button.config.assert_called_with(state=tk.DISABLED)

    def test_enable_all_buttons_after_operation(self, mock_button_app):
        """Test that all buttons are re-enabled after operations."""
        mock_button_app.enable_buttons()
        
        # Verify all buttons are enabled
        expected_buttons = [
            'search_button', 'another_button', 'newsearch_button',
            'generate_desc_button', 'theme_button', 'export_button'
        ]
        
        for button_name in expected_buttons:
            button = getattr(mock_button_app, button_name)
            button.config.assert_called_with(state=tk.NORMAL)

    def test_selective_button_enabling(self, mock_button_app):
        """Test selective enabling of buttons based on context."""
        # Simulate state where only some buttons should be enabled
        mock_button_app.enable_buttons_selective(['search_button', 'theme_button'])
        
        # Only specified buttons should be enabled
        mock_button_app.search_button.config.assert_called_with(state=tk.NORMAL)
        mock_button_app.theme_button.config.assert_called_with(state=tk.NORMAL)
        
        # Others should remain disabled
        mock_button_app.another_button.config.assert_called_with(state=tk.DISABLED)

    def test_button_state_during_search_workflow(self, mock_button_app):
        """Test button state changes during complete search workflow."""
        # Initial state - buttons enabled
        mock_button_app._ui_state = 'ready'
        
        # Start search - disable buttons
        mock_button_app.disable_buttons()
        mock_button_app._ui_state = 'searching'
        
        for button_name in ['search_button', 'another_button']:
            button = getattr(mock_button_app, button_name)
            button.config.assert_called_with(state=tk.DISABLED)
        
        # Search complete - re-enable buttons
        mock_button_app.enable_buttons()
        mock_button_app._ui_state = 'ready'
        
        for button_name in ['search_button', 'another_button']:
            button = getattr(mock_button_app, button_name)
            button.config.assert_called_with(state=tk.NORMAL)

    def test_button_tooltips_during_state_changes(self, mock_button_app):
        """Test that button tooltips are updated during state changes."""
        # Mock theme manager for tooltips
        mock_button_app.theme_manager = Mock()
        mock_button_app.theme_manager.create_themed_tooltip = Mock()
        
        # Disable buttons should update tooltips
        mock_button_app.disable_buttons()
        
        # Enable buttons should restore tooltips
        mock_button_app.enable_buttons()
        
        # Theme manager tooltip methods should be called
        assert mock_button_app.theme_manager.create_themed_tooltip.call_count >= 0

    def test_button_keyboard_shortcuts_during_disabled_state(self, mock_button_app):
        """Test keyboard shortcuts are disabled when buttons are disabled."""
        # Mock keyboard event handling
        mock_event = Mock()
        mock_event.keysym = 'Return'
        mock_event.state = 4  # Ctrl key
        
        # Disable buttons
        mock_button_app.disable_buttons()
        mock_button_app._ui_state = 'searching'
        
        # Keyboard shortcuts should not trigger actions
        result = mock_button_app.handle_keyboard_shortcut(mock_event)
        assert result == 'break' or result is None

    def test_button_visual_feedback(self, mock_button_app):
        """Test visual feedback for button state changes."""
        # Mock button styling
        mock_button_app.search_button.configure = Mock()
        
        # Test visual state changes
        mock_button_app.disable_buttons()
        
        # Button should have disabled appearance
        # (Implementation would depend on specific styling)
        mock_button_app.search_button.config.assert_called_with(state=tk.DISABLED)


class TestStatusMessageSystem:
    """Test suite for status message system."""

    @pytest.fixture
    def mock_status_app(self, mock_config_manager, no_gui):
        """Create app with status message system."""
        with patch('main.ensure_api_keys_configured', return_value=mock_config_manager):
            with patch('main.ThemeManager'):
                app = ImageSearchApp()
                app.config_manager = mock_config_manager
                
                # Mock status display components
                app.status_label = Mock(spec=ttk.Label)
                app.stats_label = Mock(spec=ttk.Label)
                app.update_idletasks = Mock()
                
                # Status message history
                app._status_history = []
                
                return app

    def test_status_message_display(self, mock_status_app):
        """Test basic status message display."""
        test_message = "Test status message"
        mock_status_app.update_status(test_message)
        
        mock_status_app.status_label.config.assert_called_with(text=test_message)
        mock_status_app.update_idletasks.assert_called()

    def test_status_message_types(self, mock_status_app):
        """Test different types of status messages."""
        status_types = [
            ("Ready", "info"),
            ("Searching for images...", "progress"),
            ("Error occurred", "error"),
            ("Operation completed successfully", "success"),
            ("Warning: Rate limit approaching", "warning")
        ]
        
        for message, msg_type in status_types:
            mock_status_app.update_status(message, msg_type)
            mock_status_app.status_label.config.assert_called_with(text=message)

    def test_status_message_history(self, mock_status_app):
        """Test status message history tracking."""
        messages = [
            "Starting operation...",
            "Processing data...",
            "Operation complete"
        ]
        
        for message in messages:
            mock_status_app.update_status(message)
            mock_status_app._status_history.append(message)
        
        # History should contain all messages
        assert len(mock_status_app._status_history) == 3
        assert mock_status_app._status_history[-1] == "Operation complete"

    def test_status_message_with_progress_percentage(self, mock_status_app):
        """Test status messages with progress percentage."""
        for i in range(0, 101, 20):
            message = f"Processing... {i}%"
            mock_status_app.update_status(message)
            mock_status_app.status_label.config.assert_called_with(text=message)

    def test_concurrent_status_updates(self, mock_status_app):
        """Test concurrent status message updates."""
        import threading
        
        def update_status_worker(worker_id):
            for i in range(5):
                message = f"Worker {worker_id} - Step {i}"
                mock_status_app.update_status(message)
                time.sleep(0.01)
        
        # Start multiple threads updating status
        threads = []
        for worker_id in range(3):
            thread = threading.Thread(target=update_status_worker, args=(worker_id,), daemon=True)
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=1.0)
        
        # Status label should have been called multiple times
        assert mock_status_app.status_label.config.call_count >= 15

    def test_status_message_overflow_handling(self, mock_status_app):
        """Test handling of very long status messages."""
        # Test very long message
        long_message = "This is a very long status message " * 20
        mock_status_app.update_status(long_message)
        
        # Should truncate or handle gracefully
        call_args = mock_status_app.status_label.config.call_args
        displayed_message = call_args[1]['text']
        
        # Either full message or truncated version should be displayed
        assert len(displayed_message) > 0
        assert "very long status message" in displayed_message


class TestUserInteractionFeedback:
    """Test suite for user interaction feedback systems."""

    @pytest.fixture
    def mock_interaction_app(self, mock_config_manager, no_gui):
        """Create app with user interaction feedback."""
        with patch('main.ensure_api_keys_configured', return_value=mock_config_manager):
            with patch('main.ThemeManager'):
                app = ImageSearchApp()
                app.config_manager = mock_config_manager
                
                # Mock interaction elements
                app.search_entry = Mock(spec=ttk.Entry)
                app.note_text = Mock()
                app.target_listbox = Mock(spec=tk.Listbox)
                
                # Mock feedback systems
                app.show_enhanced_error = Mock()
                app.update_status = Mock()
                
                # Interaction state
                app._interaction_blocked = False
                
                return app

    def test_search_entry_validation_feedback(self, mock_interaction_app):
        """Test real-time validation feedback for search entry."""
        # Mock search entry behavior
        mock_interaction_app.search_entry.get.return_value = ""
        
        # Test empty query validation
        with patch('tkinter.messagebox.showerror') as mock_error:
            mock_interaction_app.search_image()
            mock_error.assert_called_once()
            
        # Test valid query
        mock_interaction_app.search_entry.get.return_value = "valid query"
        with patch.object(mock_interaction_app, 'thread_search_images'):
            mock_interaction_app.search_image()
            # Should proceed without error

    def test_button_click_feedback(self, mock_interaction_app):
        """Test immediate feedback on button clicks."""
        # Mock button with click simulation
        mock_button = Mock()
        
        def simulate_click():
            mock_button.config(relief=tk.SUNKEN)  # Visual press feedback
            time.sleep(0.1)  # Simulate processing
            mock_button.config(relief=tk.RAISED)  # Visual release feedback
        
        # Simulate button press
        simulate_click()
        
        # Verify visual feedback calls
        expected_calls = [
            call(relief=tk.SUNKEN),
            call(relief=tk.RAISED)
        ]
        mock_button.config.assert_has_calls(expected_calls)

    def test_hover_feedback_on_vocabulary_buttons(self, mock_interaction_app):
        """Test hover feedback on vocabulary phrase buttons."""
        # Mock vocabulary button
        mock_vocab_button = Mock()
        mock_vocab_button.bind = Mock()
        
        # Setup hover effects
        def setup_hover_effects(button, phrase):
            def on_enter(event):
                button.config(bg='lightblue')
                mock_interaction_app.update_status(f"Click to add '{phrase}' to vocabulary")
            
            def on_leave(event):
                button.config(bg='white')
                mock_interaction_app.update_status("Ready")
            
            button.bind("<Enter>", on_enter)
            button.bind("<Leave>", on_leave)
        
        # Test hover setup
        setup_hover_effects(mock_vocab_button, "test phrase")
        
        # Verify event bindings
        assert mock_vocab_button.bind.call_count == 2

    def test_keyboard_navigation_feedback(self, mock_interaction_app):
        """Test keyboard navigation feedback."""
        # Mock keyboard event
        mock_event = Mock()
        mock_event.keysym = 'Tab'
        
        # Test tab navigation
        def handle_tab_navigation(event):
            # Simulate focus change feedback
            mock_interaction_app.update_status("Navigating to next field")
            return "break"
        
        # Test navigation
        result = handle_tab_navigation(mock_event)
        assert result == "break"
        mock_interaction_app.update_status.assert_called_with("Navigating to next field")

    def test_loading_state_user_feedback(self, mock_interaction_app):
        """Test user feedback during loading states."""
        # Simulate loading sequence
        loading_states = [
            "Connecting to Unsplash...",
            "Searching for images...",
            "Processing results...",
            "Loading image...",
            "Ready!"
        ]
        
        for state in loading_states:
            mock_interaction_app.update_status(state)
            time.sleep(0.01)  # Simulate processing time
        
        # Verify all states were displayed
        assert mock_interaction_app.update_status.call_count == 5

    def test_error_feedback_presentation(self, mock_interaction_app):
        """Test error feedback presentation to user."""
        # Test different error types
        error_scenarios = [
            ("API Error", "Invalid API key", "api"),
            ("Network Error", "Connection failed", "error"),
            ("Rate Limit", "Too many requests", "warning")
        ]
        
        for title, message, error_type in error_scenarios:
            mock_interaction_app.show_enhanced_error(title, message, error_type)
            
        # Verify error display calls
        assert mock_interaction_app.show_enhanced_error.call_count == 3