"""
Example integration of accessibility features with the main application.
Shows how to retrofit existing Tkinter applications with comprehensive accessibility.
"""

import tkinter as tk
from tkinter import ttk
from .core import AccessibilityManager
from .sound_cues import AudioFeedback


class AccessibleMainWindow:
    """
    Example of how to integrate accessibility features into the existing main window.
    This shows the pattern for retrofitting accessibility into existing applications.
    """
    
    def __init__(self, root_window: tk.Tk, config_manager):
        self.root = root_window
        self.config_manager = config_manager
        
        # Initialize accessibility manager first
        self.accessibility_manager = AccessibilityManager(root_window)
        
        # Store reference in root for global access
        root_window._accessibility_manager = self.accessibility_manager
        
        # Initialize audio feedback
        self.audio_feedback = AudioFeedback(self.accessibility_manager.sound_manager)
        
        # Apply initial accessibility setup
        self._setup_accessibility()
    
    def _setup_accessibility(self):
        """Setup basic accessibility for the application."""
        # Set application-level accessibility properties
        app_widget = self.accessibility_manager.make_accessible(
            self.root,
            name="Unsplash Image Search Application",
            description="Search for images on Unsplash and generate AI descriptions",
            role="application"
        )
        
        # Enable global shortcuts
        self._setup_global_shortcuts()
        
        # Setup theme integration
        self._integrate_themes()
    
    def _setup_global_shortcuts(self):
        """Setup application-specific shortcuts."""
        # Add application-specific shortcuts to keyboard navigation
        if hasattr(self.accessibility_manager, 'keyboard_nav'):
            keyboard_nav = self.accessibility_manager.keyboard_nav
            
            # Add custom shortcuts
            keyboard_nav.shortcuts.update({
                'new_search': lambda event: self._handle_new_search(),
                'generate_description': lambda event: self._handle_generate_description(),
                'export_vocabulary': lambda event: self._handle_export_vocabulary(),
                'toggle_theme': lambda event: self._handle_toggle_theme()
            })
            
            # Bind the shortcuts
            self.root.bind_all('<Control-n>', keyboard_nav.shortcuts['new_search'])
            self.root.bind_all('<Control-g>', keyboard_nav.shortcuts['generate_description'])
            self.root.bind_all('<Control-e>', keyboard_nav.shortcuts['export_vocabulary'])
            self.root.bind_all('<Control-t>', keyboard_nav.shortcuts['toggle_theme'])
    
    def _integrate_themes(self):
        """Integrate accessibility themes with existing theme manager."""
        # If the app has an existing theme manager, integrate with it
        if hasattr(self, 'theme_manager'):
            # Register callback for theme changes
            self.accessibility_manager.focus_manager.add_focus_callback(
                self._on_accessibility_focus_change
            )
    
    def make_search_bar_accessible(self, search_bar_widget):
        """Make the search bar accessible."""
        # Get individual components
        search_entry = search_bar_widget.search_entry
        search_button = search_bar_widget.search_button
        another_button = search_bar_widget.another_button
        
        # Make search entry accessible
        search_accessible = self.accessibility_manager.make_accessible(
            search_entry,
            name="Image search query",
            description="Enter keywords to search for images on Unsplash. Press Enter to search.",
            role="textbox"
        )
        
        # Add form validation feedback
        original_get = search_entry.get
        def enhanced_get(*args, **kwargs):
            value = original_get(*args, **kwargs)
            if not value.strip():
                self.audio_feedback.field_warning()
            return value
        search_entry.get = enhanced_get
        
        # Make search button accessible
        search_btn_accessible = self.accessibility_manager.make_accessible(
            search_button,
            name="Search for images",
            description="Search Unsplash for images matching your query",
            role="button"
        )
        
        # Add audio feedback to button
        original_command = search_button.cget('command')
        def enhanced_search():
            self.audio_feedback.button_clicked()
            if original_command:
                original_command()
        search_button.configure(command=enhanced_search)
        
        # Make another image button accessible
        another_accessible = self.accessibility_manager.make_accessible(
            another_button,
            name="Get another image",
            description="Get a different image from the current search results",
            role="button"
        )
        
        return {
            'search_entry': search_accessible,
            'search_button': search_btn_accessible,
            'another_button': another_accessible
        }
    
    def make_image_viewer_accessible(self, image_viewer_widget):
        """Make the image viewer accessible."""
        # Main image display
        image_canvas = image_viewer_widget.image_canvas
        
        image_accessible = self.accessibility_manager.make_accessible(
            image_canvas,
            name="Image preview",
            description="Currently loaded image from Unsplash. Use arrow keys to pan if zoomed.",
            role="img"
        )
        
        # Zoom controls
        if hasattr(image_viewer_widget, 'zoom_controls'):
            zoom_in_btn = image_viewer_widget.zoom_in_btn
            zoom_out_btn = image_viewer_widget.zoom_out_btn
            zoom_reset_btn = image_viewer_widget.zoom_reset_btn
            
            # Make zoom buttons accessible
            self.accessibility_manager.make_accessible(
                zoom_in_btn,
                name="Zoom in",
                description="Increase image size by 10%. Current zoom level will be announced.",
                role="button"
            )
            
            self.accessibility_manager.make_accessible(
                zoom_out_btn,
                name="Zoom out", 
                description="Decrease image size by 10%. Current zoom level will be announced.",
                role="button"
            )
            
            self.accessibility_manager.make_accessible(
                zoom_reset_btn,
                name="Reset zoom",
                description="Reset image to 100% zoom level",
                role="button"
            )
            
            # Add audio feedback for zoom changes
            def announce_zoom_change(new_level):
                self.accessibility_manager.announce(f"Zoom level {int(new_level)}%")
            
            # Hook into zoom change events (if they exist)
            # This would need to be integrated with the actual zoom functionality
        
        return image_accessible
    
    def make_text_areas_accessible(self, text_area_widgets):
        """Make text areas accessible."""
        accessible_widgets = {}
        
        # User notes area
        if 'notes' in text_area_widgets:
            notes_text = text_area_widgets['notes']
            notes_accessible = self.accessibility_manager.make_accessible(
                notes_text,
                name="User notes",
                description="Enter your own notes or description for the image. This context will be used when generating AI descriptions.",
                role="textbox"
            )
            accessible_widgets['notes'] = notes_accessible
        
        # Generated description area
        if 'description' in text_area_widgets:
            desc_text = text_area_widgets['description']
            desc_accessible = self.accessibility_manager.make_accessible(
                desc_text,
                name="AI generated description",
                description="Description of the image generated by GPT. This area is read-only.",
                role="document"
            )
            accessible_widgets['description'] = desc_accessible
        
        # Generate description button
        if 'generate_button' in text_area_widgets:
            generate_btn = text_area_widgets['generate_button']
            generate_accessible = self.accessibility_manager.make_accessible(
                generate_btn,
                name="Generate description",
                description="Generate AI description of the current image using GPT",
                role="button"
            )
            
            # Add audio feedback
            original_command = generate_btn.cget('command')
            def enhanced_generate():
                self.audio_feedback.button_clicked()
                self.accessibility_manager.announce("Generating description with AI...")
                if original_command:
                    result = original_command()
                    # Announce completion (this would need integration with the actual function)
                    self.root.after(1000, lambda: self.accessibility_manager.announce("Description generated"))
                    return result
            generate_btn.configure(command=enhanced_generate)
            
            accessible_widgets['generate_button'] = generate_accessible
        
        return accessible_widgets
    
    def make_vocabulary_lists_accessible(self, vocab_widgets):
        """Make vocabulary lists accessible."""
        accessible_widgets = {}
        
        # Extracted phrases list
        if 'extracted_phrases' in vocab_widgets:
            extracted_list = vocab_widgets['extracted_phrases']
            extracted_accessible = self.accessibility_manager.make_accessible(
                extracted_list,
                name="Extracted phrases",
                description="Spanish words and phrases extracted from the AI description. Click any phrase to add it to your vocabulary.",
                role="list"
            )
            accessible_widgets['extracted_phrases'] = extracted_accessible
        
        # Target vocabulary list
        if 'target_vocabulary' in vocab_widgets:
            target_list = vocab_widgets['target_vocabulary']
            target_accessible = self.accessibility_manager.make_accessible(
                target_list,
                name="Target vocabulary",
                description="Your saved vocabulary words with Spanish to English translations",
                role="list"
            )
            accessible_widgets['target_vocabulary'] = target_accessible
        
        return accessible_widgets
    
    def add_phrase_click_accessibility(self, phrase_buttons):
        """Add accessibility to clickable phrase buttons."""
        for i, button in enumerate(phrase_buttons):
            phrase_text = button.cget('text')
            
            # Make each phrase button accessible
            phrase_accessible = self.accessibility_manager.make_accessible(
                button,
                name=f"Add phrase: {phrase_text}",
                description=f"Click to add '{phrase_text}' to your vocabulary list with translation",
                role="button"
            )
            
            # Add audio feedback
            original_command = button.cget('command')
            def enhanced_add_phrase(phrase=phrase_text, cmd=original_command):
                self.audio_feedback.button_clicked()
                self.accessibility_manager.announce(f"Adding {phrase} to vocabulary")
                if cmd:
                    result = cmd()
                    # Announce completion
                    self.root.after(500, lambda: self.accessibility_manager.announce(f"Added {phrase} to vocabulary"))
                    return result
            
            button.configure(command=enhanced_add_phrase)
    
    def setup_status_announcements(self, status_callback):
        """Setup automatic status announcements."""
        def enhanced_status_callback(message):
            # Call original status update
            if status_callback:
                status_callback(message)
            
            # Announce status changes to screen reader
            if message and message != "Ready":
                priority = "assertive" if "error" in message.lower() else "polite"
                self.accessibility_manager.announce(message, priority)
                
                # Play appropriate sound cue
                if "error" in message.lower():
                    self.audio_feedback.validation_error()
                elif "success" in message.lower() or "completed" in message.lower():
                    self.audio_feedback.action_completed()
                elif "loading" in message.lower() or "searching" in message.lower():
                    self.audio_feedback.information_displayed()
        
        return enhanced_status_callback
    
    def integrate_with_existing_app(self, main_window_instance):
        """
        Complete integration example with existing MainWindow class.
        This shows how to retrofit the entire application.
        """
        # Make main components accessible
        if hasattr(main_window_instance, 'search_bar'):
            self.make_search_bar_accessible(main_window_instance.search_bar)
        
        if hasattr(main_window_instance, 'image_viewer'):
            self.make_image_viewer_accessible(main_window_instance.image_viewer)
        
        # Make text areas accessible
        text_widgets = {}
        if hasattr(main_window_instance, 'note_text'):
            text_widgets['notes'] = main_window_instance.note_text
        if hasattr(main_window_instance, 'description_text'):
            text_widgets['description'] = main_window_instance.description_text
        if hasattr(main_window_instance, 'generate_desc_button'):
            text_widgets['generate_button'] = main_window_instance.generate_desc_button
        
        if text_widgets:
            self.make_text_areas_accessible(text_widgets)
        
        # Make vocabulary widgets accessible
        vocab_widgets = {}
        if hasattr(main_window_instance, 'extracted_phrases'):
            vocab_widgets['extracted_phrases'] = main_window_instance.extracted_phrases
        if hasattr(main_window_instance, 'vocabulary_list'):
            vocab_widgets['target_vocabulary'] = main_window_instance.vocabulary_list
        
        if vocab_widgets:
            self.make_vocabulary_lists_accessible(vocab_widgets)
        
        # Setup status announcements
        if hasattr(main_window_instance, 'update_status'):
            original_update_status = main_window_instance.update_status
            enhanced_update_status = self.setup_status_announcements(original_update_status)
            main_window_instance.update_status = enhanced_update_status
        
        # Setup progress announcements
        if hasattr(main_window_instance, 'show_progress'):
            original_show_progress = main_window_instance.show_progress
            def enhanced_show_progress(message="Loading..."):
                self.accessibility_manager.announce(message)
                return original_show_progress(message)
            main_window_instance.show_progress = enhanced_show_progress
        
        return True
    
    # Event handlers for shortcuts
    def _handle_new_search(self):
        """Handle new search shortcut."""
        self.accessibility_manager.announce("Starting new search")
        # Would trigger the actual new search functionality
    
    def _handle_generate_description(self):
        """Handle generate description shortcut."""
        self.accessibility_manager.announce("Generating description")
        # Would trigger the actual generate description functionality
    
    def _handle_export_vocabulary(self):
        """Handle export vocabulary shortcut."""
        self.accessibility_manager.announce("Opening export dialog")
        # Would trigger the actual export functionality
    
    def _handle_toggle_theme(self):
        """Handle theme toggle shortcut."""
        # This would integrate with existing theme manager
        self.accessibility_manager.announce("Theme toggled")
    
    def _on_accessibility_focus_change(self, event_type, widget):
        """Handle accessibility focus changes."""
        if event_type == 'focus_in':
            # Optionally play focus sound
            if self.accessibility_manager.settings.get('sound_enabled'):
                self.audio_feedback.element_focused()


# Usage example for retrofitting existing application
def retrofit_main_window_accessibility(main_window_instance, config_manager):
    """
    Retrofit an existing MainWindow instance with accessibility features.
    
    Args:
        main_window_instance: Instance of the existing MainWindow class
        config_manager: Configuration manager instance
    
    Returns:
        AccessibleMainWindow: The accessibility integration wrapper
    """
    # Create accessibility wrapper
    accessible_wrapper = AccessibleMainWindow(
        main_window_instance,  # Assuming main_window_instance is the Tk root
        config_manager
    )
    
    # Integrate with existing application
    accessible_wrapper.integrate_with_existing_app(main_window_instance)
    
    return accessible_wrapper


# Example of complete integration
def create_accessible_application():
    """Example of creating a new application with full accessibility."""
    root = tk.Tk()
    
    # Initialize configuration (placeholder)
    config_manager = None  # Would be actual config manager
    
    # Create accessible wrapper
    accessible_app = AccessibleMainWindow(root, config_manager)
    
    # Create your UI components
    # ... create widgets ...
    
    # Make them accessible
    # accessible_app.make_search_bar_accessible(search_bar)
    # accessible_app.make_image_viewer_accessible(image_viewer)
    
    return root, accessible_app