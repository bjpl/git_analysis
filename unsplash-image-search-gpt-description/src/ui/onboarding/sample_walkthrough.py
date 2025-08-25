"""
Sample walkthrough system that demonstrates the app with a curated image
Shows users exactly how the application works with step-by-step guidance
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Dict, Any
import base64
from pathlib import Path
import json
import time
from PIL import Image, ImageTk
from io import BytesIO


class SampleWalkthrough:
    """
    Guides users through a complete workflow with a sample image
    Demonstrates search, description generation, and vocabulary extraction
    """
    
    def __init__(self, parent: tk.Tk, theme_manager, config_manager,
                 on_completion: Callable = None, on_skip: Callable = None):
        self.parent = parent
        self.theme_manager = theme_manager
        self.config_manager = config_manager
        self.on_completion = on_completion
        self.on_skip = on_skip
        
        self.walkthrough_window = None
        self.current_step = 0
        self.total_steps = 7
        self.is_running = False
        
        # Sample data for demonstration
        self.sample_data = {
            'query': 'mercado de comida',
            'image_url': 'sample_market_image.jpg',  # Placeholder - would use embedded sample
            'description': '''En esta vibrante imagen podemos observar un colorido mercado de comida callejera. 
Los vendedores exhiben una gran variedad de frutas tropicales frescas como mangos amarillos, 
piñas maduras y plátanos verdes. Las mesas de madera están cubiertas con manteles de colores 
brillantes - rojo, azul y verde - creando un ambiente festivo y acogedor. 
            
Los clientes locales caminan entre los puestos, examinando cuidadosamente la mercancía. 
Una señora mayor usa un delantal floreado mientras atiende a los compradores. 
El sol tropical ilumina toda la escena, creando sombras suaves bajo los toldos de tela.''',
            'extracted_vocabulary': {
                'Sustantivos': ['el mercado', 'la comida', 'las frutas', 'los mangos', 'las piñas', 'los plátanos', 'las mesas', 'los manteles', 'los puestos', 'la señora'],
                'Adjetivos': ['vibrante', 'colorido', 'tropicales', 'frescas', 'amarillos', 'maduras', 'verdes', 'brillantes', 'festivo', 'acogedor'],
                'Verbos': ['observar', 'exhibir', 'cubrir', 'caminar', 'examinar', 'atender', 'iluminar'],
                'Frases clave': ['mercado de comida', 'frutas tropicales', 'ambiente festivo', 'delantal floreado', 'sombras suaves']
            }
        }
        
        # Step definitions
        self.steps = [
            {
                'title': 'Welcome to the Sample Walkthrough',
                'content': 'Let\\'s see how the app works with a real example!',
                'action': 'show_intro',
                'button_text': 'Start Demo'
            },
            {
                'title': 'Step 1: Search for Images',
                'content': 'We\\'ll search for "mercado de comida" (food market)',
                'action': 'demo_search',
                'button_text': 'Search Images'
            },
            {
                'title': 'Step 2: Image Appears',
                'content': 'Here\\'s a beautiful food market image from Unsplash',
                'action': 'show_image',
                'button_text': 'View Image'
            },
            {
                'title': 'Step 3: Add Notes (Optional)',
                'content': 'You can add your own observations about the image',
                'action': 'demo_notes',
                'button_text': 'Add Notes'
            },
            {
                'title': 'Step 4: Generate Description',
                'content': 'The AI analyzes the image and creates a Spanish description',
                'action': 'generate_description',
                'button_text': 'Generate Description'
            },
            {
                'title': 'Step 5: Extract Vocabulary',
                'content': 'The AI automatically finds useful vocabulary words',
                'action': 'extract_vocabulary',
                'button_text': 'Extract Words'
            },
            {
                'title': 'Step 6: Build Your Vocabulary List',
                'content': 'Click words to add them to your learning list',
                'action': 'demo_vocabulary_selection',
                'button_text': 'Select Words'
            },
            {
                'title': 'Complete! You\\'re Ready to Learn',
                'content': 'Now you know how to use the app to build your Spanish vocabulary',
                'action': 'show_completion',
                'button_text': 'Finish'
            }
        ]
    
    def start(self):
        """Start the sample walkthrough"""
        if self.walkthrough_window:
            self.walkthrough_window.lift()
            return
        
        self.is_running = True
        self.current_step = 0
        self._create_walkthrough_window()
        self._show_current_step()
    
    def stop(self):
        """Stop the walkthrough"""
        self.is_running = False
        if self.walkthrough_window:
            self.walkthrough_window.destroy()
            self.walkthrough_window = None
    
    def _create_walkthrough_window(self):
        """Create the walkthrough window"""
        colors = self.theme_manager.get_colors()
        
        # Create window
        self.walkthrough_window = tk.Toplevel(self.parent)
        self.walkthrough_window.title("Sample Walkthrough - See How It Works")
        self.walkthrough_window.geometry("800x700")
        self.walkthrough_window.configure(bg=colors['bg'])
        self.walkthrough_window.resizable(True, True)
        self.walkthrough_window.transient(self.parent)
        self.walkthrough_window.grab_set()
        
        # Center window
        self.walkthrough_window.update_idletasks()
        x = (self.walkthrough_window.winfo_screenwidth() // 2) - 400
        y = (self.walkthrough_window.winfo_screenheight() // 2) - 350
        self.walkthrough_window.geometry(f"+{x}+{y}")
        
        # Handle window close
        self.walkthrough_window.protocol("WM_DELETE_WINDOW", self._on_window_close)
        
        # Create UI components
        self._create_header()
        self._create_demo_area()
        self._create_controls()
    
    def _create_header(self):
        """Create walkthrough header"""
        colors = self.theme_manager.get_colors()
        
        header_frame = tk.Frame(self.walkthrough_window, bg=colors['bg'])
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        # Icon and title
        title_frame = tk.Frame(header_frame, bg=colors['bg'])
        title_frame.pack()
        
        icon_label = tk.Label(
            title_frame,
            text="🎬",
            font=('TkDefaultFont', 24),
            bg=colors['bg'],
            fg=colors['info']
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.title_label = tk.Label(
            title_frame,
            text="Sample Walkthrough",
            font=('TkDefaultFont', 16, 'bold'),
            bg=colors['bg'],
            fg=colors['fg']
        )
        self.title_label.pack(side=tk.LEFT)
        
        # Progress bar
        progress_frame = tk.Frame(header_frame, bg=colors['bg'])
        progress_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='determinate',
            length=400
        )
        self.progress_bar.pack()
        
        # Step indicator
        self.step_label = tk.Label(
            progress_frame,
            text="Step 1 of 8",
            font=('TkDefaultFont', 9),
            bg=colors['bg'],
            fg=colors['disabled_fg']
        )
        self.step_label.pack(pady=(5, 0))
    
    def _create_demo_area(self):
        """Create the main demo area that simulates the app"""
        colors = self.theme_manager.get_colors()
        
        # Demo container
        demo_frame = tk.LabelFrame(
            self.walkthrough_window,
            text="App Simulation",
            font=('TkDefaultFont', 10, 'bold'),
            bg=colors['frame_bg'],
            fg=colors['fg']
        )
        demo_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Search area (top)
        search_frame = tk.Frame(demo_frame, bg=colors['frame_bg'])
        search_frame.pack(fill=tk.X, padx=15, pady=10)
        
        tk.Label(
            search_frame,
            text="Search Query:",
            font=('TkDefaultFont', 10),
            bg=colors['frame_bg'],
            fg=colors['fg']
        ).pack(side=tk.LEFT)
        
        self.demo_search_entry = tk.Entry(
            search_frame,
            font=('TkDefaultFont', 10),
            width=30,
            state=tk.DISABLED
        )
        self.demo_search_entry.pack(side=tk.LEFT, padx=(10, 5))
        
        self.demo_search_button = tk.Button(
            search_frame,
            text="Search",
            font=('TkDefaultFont', 9),
            bg=colors['button_bg'],
            fg=colors['button_fg'],
            relief=tk.FLAT,
            state=tk.DISABLED
        )
        self.demo_search_button.pack(side=tk.LEFT)
        
        # Content area - split between image and text
        content_frame = tk.Frame(demo_frame, bg=colors['frame_bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Left side - Image preview
        image_frame = tk.LabelFrame(
            content_frame,
            text="Image Preview",
            font=('TkDefaultFont', 9),
            bg=colors['frame_bg'],
            fg=colors['fg']
        )
        image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.demo_image_label = tk.Label(
            image_frame,
            text="No image loaded",
            font=('TkDefaultFont', 10),
            bg=colors['text_bg'],
            fg=colors['disabled_fg'],
            width=30,
            height=15,
            relief=tk.SUNKEN
        )
        self.demo_image_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Right side - Text areas
        text_frame = tk.Frame(content_frame, bg=colors['frame_bg'])
        text_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Notes area
        notes_frame = tk.LabelFrame(
            text_frame,
            text="Your Notes",
            font=('TkDefaultFont', 9),
            bg=colors['frame_bg'],
            fg=colors['fg']
        )
        notes_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.demo_notes_text = tk.Text(
            notes_frame,
            height=4,
            font=('TkDefaultFont', 9),
            bg=colors['text_bg'],
            fg=colors['text_fg'],
            state=tk.DISABLED
        )
        self.demo_notes_text.pack(fill=tk.X, padx=10, pady=5)
        
        # Generate button
        self.demo_generate_button = tk.Button(
            notes_frame,
            text="Generate Description",
            font=('TkDefaultFont', 9),
            bg=colors['info'],
            fg=colors['select_fg'],
            relief=tk.FLAT,
            state=tk.DISABLED
        )
        self.demo_generate_button.pack(pady=5)
        
        # Description area
        desc_frame = tk.LabelFrame(
            text_frame,
            text="AI Description",
            font=('TkDefaultFont', 9),
            bg=colors['frame_bg'],
            fg=colors['fg']
        )
        desc_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        self.demo_description_text = tk.Text(
            desc_frame,
            height=8,
            font=('TkDefaultFont', 9),
            bg=colors['text_bg'],
            fg=colors['text_fg'],
            state=tk.DISABLED,
            wrap=tk.WORD
        )
        self.demo_description_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Vocabulary area (bottom)
        vocab_frame = tk.Frame(demo_frame, bg=colors['frame_bg'])
        vocab_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        # Extracted vocabulary (left)
        extracted_frame = tk.LabelFrame(
            vocab_frame,
            text="Extracted Vocabulary",
            font=('TkDefaultFont', 9),
            bg=colors['frame_bg'],
            fg=colors['fg']
        )
        extracted_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.demo_vocab_frame = tk.Frame(extracted_frame, bg=colors['frame_bg'])
        self.demo_vocab_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Selected vocabulary (right)
        selected_frame = tk.LabelFrame(
            vocab_frame,
            text="Your Vocabulary List",
            font=('TkDefaultFont', 9),
            bg=colors['frame_bg'],
            fg=colors['fg']
        )
        selected_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        
        self.demo_selected_listbox = tk.Listbox(
            selected_frame,
            height=6,
            width=25,
            font=('TkDefaultFont', 9),
            bg=colors['entry_bg'],
            fg=colors['entry_fg']
        )
        self.demo_selected_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    def _create_controls(self):
        """Create walkthrough controls"""
        colors = self.theme_manager.get_colors()
        
        controls_frame = tk.Frame(self.walkthrough_window, bg=colors['bg'])
        controls_frame.pack(fill=tk.X, padx=20, pady=(10, 20))
        
        # Instruction area
        self.instruction_frame = tk.LabelFrame(
            controls_frame,
            text="Instructions",
            font=('TkDefaultFont', 10, 'bold'),
            bg=colors['frame_bg'],
            fg=colors['info']
        )
        self.instruction_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.instruction_label = tk.Label(
            self.instruction_frame,
            text="Click 'Start Demo' to begin the walkthrough",
            font=('TkDefaultFont', 11),
            bg=colors['frame_bg'],
            fg=colors['fg'],
            wraplength=600,
            justify=tk.LEFT
        )
        self.instruction_label.pack(fill=tk.X, padx=15, pady=10)
        
        # Navigation buttons
        nav_frame = tk.Frame(controls_frame, bg=colors['bg'])
        nav_frame.pack(fill=tk.X)
        
        # Skip button
        self.skip_button = tk.Button(
            nav_frame,
            text="Skip Walkthrough",
            command=self._skip_walkthrough,
            font=('TkDefaultFont', 10),
            bg=colors['button_bg'],
            fg=colors['disabled_fg'],
            relief=tk.FLAT,
            padx=20
        )
        self.skip_button.pack(side=tk.LEFT)
        
        # Right navigation
        right_nav = tk.Frame(nav_frame, bg=colors['bg'])
        right_nav.pack(side=tk.RIGHT)
        
        # Back button
        self.back_button = tk.Button(
            right_nav,
            text="← Back",
            command=self._previous_step,
            font=('TkDefaultFont', 10),
            bg=colors['button_bg'],
            fg=colors['button_fg'],
            relief=tk.FLAT,
            padx=20,
            state=tk.DISABLED
        )
        self.back_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Action button (changes based on step)
        self.action_button = tk.Button(
            right_nav,
            text="Start Demo",
            command=self._handle_action,
            font=('TkDefaultFont', 10, 'bold'),
            bg=colors['select_bg'],
            fg=colors['select_fg'],
            relief=tk.FLAT,
            padx=20
        )
        self.action_button.pack(side=tk.LEFT)
    
    def _show_current_step(self):
        """Display the current walkthrough step"""
        if self.current_step >= len(self.steps):
            self._complete_walkthrough()
            return
        
        step = self.steps[self.current_step]
        colors = self.theme_manager.get_colors()
        
        # Update progress
        progress = (self.current_step / (len(self.steps) - 1)) * 100
        self.progress_bar.configure(value=progress)
        self.step_label.configure(text=f"Step {self.current_step + 1} of {len(self.steps)}")
        
        # Update instruction
        self.instruction_label.configure(
            text=f"{step['title']}\\n\\n{step['content']}"
        )
        
        # Update action button
        self.action_button.configure(text=step['button_text'])
        
        # Update navigation
        self.back_button.configure(
            state=tk.NORMAL if self.current_step > 0 else tk.DISABLED
        )
        
        # Perform step action
        action_method = getattr(self, f"_{step['action']}", None)
        if action_method:
            action_method()
    
    def _show_intro(self):
        """Show introduction step"""
        colors = self.theme_manager.get_colors()
        
        # Reset demo interface
        self.demo_search_entry.configure(state=tk.NORMAL)
        self.demo_search_entry.delete(0, tk.END)
        self.demo_search_entry.configure(state=tk.DISABLED)
        
        self.demo_image_label.configure(
            text="Sample walkthrough will demonstrate\\nall app features step by step",
            fg=colors['info']
        )
        
        # Clear all text areas
        for text_widget in [self.demo_notes_text, self.demo_description_text]:
            text_widget.configure(state=tk.NORMAL)
            text_widget.delete('1.0', tk.END)
            text_widget.configure(state=tk.DISABLED)
        
        # Clear vocabulary
        for widget in self.demo_vocab_frame.winfo_children():
            widget.destroy()
        
        self.demo_selected_listbox.delete(0, tk.END)
    
    def _demo_search(self):
        """Demonstrate the search functionality"""
        # Enable search entry and show query
        self.demo_search_entry.configure(state=tk.NORMAL)
        self.demo_search_entry.delete(0, tk.END)
        self.demo_search_entry.insert(0, self.sample_data['query'])
        self.demo_search_entry.configure(state=tk.DISABLED)
        
        # Enable search button visually
        colors = self.theme_manager.get_colors()
        self.demo_search_button.configure(
            bg=colors['select_bg'],
            fg=colors['select_fg']
        )
    
    def _show_image(self):
        """Show the sample image"""
        colors = self.theme_manager.get_colors()
        
        # Create a placeholder image (in real implementation, you'd load actual image)
        self.demo_image_label.configure(
            text="🖼️\\n\\nBeautiful food market image\\nwith colorful fruits and vendors\\n\\n(Sample Image Loaded)",
            fg=colors['success'],
            font=('TkDefaultFont', 10)
        )
        
        # Enable the image area
        self.demo_image_label.configure(bg=colors['bg'])
    
    def _demo_notes(self):
        """Demonstrate adding notes"""
        sample_note = "I can see lots of tropical fruits and colorful market stalls. The vendors look friendly and the atmosphere seems lively."
        
        self.demo_notes_text.configure(state=tk.NORMAL)
        self.demo_notes_text.delete('1.0', tk.END)
        
        # Simulate typing
        self._type_text(self.demo_notes_text, sample_note, delay=30)
        
        # Enable generate button
        colors = self.theme_manager.get_colors()
        self.demo_generate_button.configure(
            bg=colors['success'],
            state=tk.NORMAL
        )
    
    def _generate_description(self):
        """Demonstrate AI description generation"""
        colors = self.theme_manager.get_colors()
        
        # Show loading state
        self.demo_generate_button.configure(text="Generating...")
        self.demo_description_text.configure(state=tk.NORMAL)
        self.demo_description_text.delete('1.0', tk.END)
        self.demo_description_text.insert('1.0', "Analyzing image with AI...")
        self.demo_description_text.configure(state=tk.DISABLED)
        
        # Simulate processing delay then show description
        self.walkthrough_window.after(1500, self._show_generated_description)
    
    def _show_generated_description(self):
        """Show the generated description"""
        colors = self.theme_manager.get_colors()
        
        self.demo_description_text.configure(state=tk.NORMAL)
        self.demo_description_text.delete('1.0', tk.END)
        
        # Type out the description
        self._type_text(
            self.demo_description_text, 
            self.sample_data['description'], 
            delay=20,
            callback=lambda: self.demo_generate_button.configure(text="Generate Description")
        )
    
    def _extract_vocabulary(self):
        """Demonstrate vocabulary extraction"""
        colors = self.theme_manager.get_colors()
        
        # Clear existing vocabulary widgets
        for widget in self.demo_vocab_frame.winfo_children():
            widget.destroy()
        
        vocab_data = self.sample_data['extracted_vocabulary']
        
        # Create vocabulary categories with buttons
        for category, words in vocab_data.items():
            if not words:
                continue
            
            # Category label
            cat_label = tk.Label(
                self.demo_vocab_frame,
                text=f"{category}:",
                font=('TkDefaultFont', 9, 'bold'),
                bg=colors['frame_bg'],
                fg=colors['fg']
            )
            cat_label.pack(anchor=tk.W, pady=(5, 2))
            
            # Words frame
            words_frame = tk.Frame(self.demo_vocab_frame, bg=colors['frame_bg'])
            words_frame.pack(fill=tk.X, padx=10)
            
            # Create clickable word buttons
            for i, word in enumerate(words[:6]):  # Show first 6 words
                if i % 3 == 0:  # New row every 3 words
                    row_frame = tk.Frame(words_frame, bg=colors['frame_bg'])
                    row_frame.pack(fill=tk.X, pady=1)
                
                word_button = tk.Button(
                    row_frame,
                    text=word,
                    font=('TkDefaultFont', 8),
                    bg=colors['info'],
                    fg=colors['select_fg'],
                    relief=tk.FLAT,
                    padx=8,
                    pady=2,
                    command=lambda w=word: self._demo_add_word(w)
                )
                word_button.pack(side=tk.LEFT, padx=2)
    
    def _demo_vocabulary_selection(self):
        """Demonstrate vocabulary selection"""
        # Add some sample words to the vocabulary list
        sample_selections = [
            "el mercado - the market",
            "las frutas - the fruits",
            "colorido - colorful",
            "examinar - to examine"
        ]
        
        for word in sample_selections:
            self.demo_selected_listbox.insert(tk.END, word)
        
        # Highlight the list
        colors = self.theme_manager.get_colors()
        self.demo_selected_listbox.configure(
            highlightbackground=colors['success'],
            highlightthickness=2
        )
    
    def _show_completion(self):
        """Show completion message"""
        colors = self.theme_manager.get_colors()
        
        self.instruction_label.configure(
            text="🎉 Walkthrough Complete!\\n\\nYou've seen how to:\\n" +
                 "✅ Search for images\\n" +
                 "✅ Generate AI descriptions\\n" +
                 "✅ Extract vocabulary\\n" +
                 "✅ Build your learning list\\n\\n" +
                 "Now you're ready to start learning Spanish!",
            fg=colors['success']
        )
        
        self.action_button.configure(text="Finish & Continue")
    
    def _demo_add_word(self, word):
        """Add a word to the demo vocabulary list"""
        # Simple translation simulation
        translations = {
            'el mercado': 'the market',
            'la comida': 'the food', 
            'las frutas': 'the fruits',
            'colorido': 'colorful',
            'vibrante': 'vibrant',
            'examinar': 'to examine',
            'atender': 'to serve/attend'
        }
        
        translation = translations.get(word, 'translation')
        combined = f"{word} - {translation}"
        
        # Add to list if not already there
        current_items = [self.demo_selected_listbox.get(i) for i in range(self.demo_selected_listbox.size())]
        if combined not in current_items:
            self.demo_selected_listbox.insert(tk.END, combined)
    
    def _type_text(self, text_widget, text, delay=50, callback=None):
        """Simulate typing text into a widget"""
        text_widget.configure(state=tk.NORMAL)
        
        def type_char(index=0):
            if index < len(text):
                text_widget.insert(tk.END, text[index])
                text_widget.see(tk.END)
                text_widget.update_idletasks()
                self.walkthrough_window.after(delay, lambda: type_char(index + 1))
            else:
                text_widget.configure(state=tk.DISABLED)
                if callback:
                    callback()
        
        type_char()
    
    def _handle_action(self):
        """Handle the action button click"""
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self._show_current_step()
        else:
            self._complete_walkthrough()
    
    def _previous_step(self):
        """Go to previous step"""
        if self.current_step > 0:
            self.current_step -= 1
            self._show_current_step()
    
    def _skip_walkthrough(self):
        """Skip the walkthrough"""
        from ..theme_manager import ThemedMessageBox
        
        result = ThemedMessageBox.ask_yes_no(
            self.walkthrough_window,
            "Skip Walkthrough",
            "Are you sure you want to skip the demonstration?\\n\\n" +
            "The walkthrough shows you exactly how to use the app.",
            self.theme_manager
        )
        
        if result:
            self.stop()
            if self.on_skip:
                self.on_skip()
    
    def _complete_walkthrough(self):
        """Complete the walkthrough"""
        self.stop()
        if self.on_completion:
            self.on_completion()
    
    def _on_window_close(self):
        """Handle window close"""
        self._skip_walkthrough()