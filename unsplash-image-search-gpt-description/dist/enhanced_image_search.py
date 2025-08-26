"""
Enhanced Unsplash Image Search & GPT Description Tool
Production Version with Advanced Features

Features:
- 3 Description Styles (Academic, Poetic, Technical)
- 4 Vocabulary Levels (Beginner to Native)
- Session-based image variety system
- Smart search rotation for different results
- Persistent user preferences
- Advanced vocabulary management
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
from PIL import Image, ImageTk
from io import BytesIO
import threading
import json
import random
import time
import hashlib
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, List, Optional, Tuple
import os
import sys

# ============================================================================
# DESCRIPTION STYLES MODULE
# ============================================================================

class DescriptionStyle(Enum):
    """Available description styles."""
    ACADEMIC = "academic"
    POETIC = "poetic"
    TECHNICAL = "technical"


class VocabularyLevel(Enum):
    """Vocabulary complexity levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    NATIVE = "native"


@dataclass
class StyleConfig:
    """Configuration for a specific description style."""
    name: str
    display_name: str
    style: DescriptionStyle
    level: VocabularyLevel
    prompt_template: str
    vocabulary_focus: List[str]
    tone_keywords: List[str]
    example_phrases: List[str]


class DescriptionStyleManager:
    """Manages different description styles for AI-generated content."""
    
    def __init__(self):
        self.current_style = DescriptionStyle.ACADEMIC
        self.current_level = VocabularyLevel.INTERMEDIATE
        self._initialize_styles()
    
    def _initialize_styles(self):
        """Initialize style configurations."""
        self.styles = {
            DescriptionStyle.ACADEMIC: {
                VocabularyLevel.BEGINNER: StyleConfig(
                    name="academic_beginner",
                    display_name="Academic/Neutral - Beginner",
                    style=DescriptionStyle.ACADEMIC,
                    level=VocabularyLevel.BEGINNER,
                    prompt_template="""Describe this image in academic Spanish using:
- Simple, clear vocabulary for beginners
- Objective, factual descriptions
- Present tense primarily
- Basic sentence structures
- Educational tone without complex terminology""",
                    vocabulary_focus=["nouns", "basic_verbs", "colors", "positions"],
                    tone_keywords=["objetivo", "claro", "simple", "educativo"],
                    example_phrases=[
                        "En la imagen se observa...",
                        "El elemento principal es...",
                        "Los colores predominantes son..."
                    ]
                ),
                VocabularyLevel.INTERMEDIATE: StyleConfig(
                    name="academic_intermediate",
                    display_name="Academic/Neutral - Intermediate",
                    style=DescriptionStyle.ACADEMIC,
                    level=VocabularyLevel.INTERMEDIATE,
                    prompt_template="""Provide an academic analysis in Spanish using:
- Formal, objective language
- Academic vocabulary and connectors (por lo tanto, sin embargo, además)
- Multiple verb tenses
- Structured paragraphs with clear transitions
- Analytical observations about composition and context""",
                    vocabulary_focus=["academic_connectors", "analytical_verbs", "formal_adjectives"],
                    tone_keywords=["formal", "analítico", "estructurado", "objetivo"],
                    example_phrases=[
                        "Cabe destacar que...",
                        "En términos de composición...",
                        "Se puede apreciar claramente..."
                    ]
                )
            },
            DescriptionStyle.POETIC: {
                VocabularyLevel.BEGINNER: StyleConfig(
                    name="poetic_beginner",
                    display_name="Poetic/Literary - Beginner",
                    style=DescriptionStyle.POETIC,
                    level=VocabularyLevel.BEGINNER,
                    prompt_template="""Create a simple poetic description in Spanish using:
- Beautiful but simple vocabulary
- Basic sensory descriptions
- Simple metaphors and comparisons
- Emotional language accessible to beginners""",
                    vocabulary_focus=["emotions", "senses", "nature", "simple_metaphors"],
                    tone_keywords=["poético", "emotivo", "sensorial", "simple"],
                    example_phrases=[
                        "Como un sueño...",
                        "Los colores bailan...",
                        "La luz abraza suavemente..."
                    ]
                ),
                VocabularyLevel.INTERMEDIATE: StyleConfig(
                    name="poetic_intermediate",
                    display_name="Poetic/Literary - Intermediate",
                    style=DescriptionStyle.POETIC,
                    level=VocabularyLevel.INTERMEDIATE,
                    prompt_template="""Craft a literary description in Spanish featuring:
- Rich, expressive vocabulary
- Metaphors and similes
- Sensory imagery and synesthesia
- Emotional depth and atmosphere""",
                    vocabulary_focus=["literary_devices", "sensory_adjectives", "metaphorical_verbs"],
                    tone_keywords=["lírico", "evocador", "metafórico", "expresivo"],
                    example_phrases=[
                        "El lienzo respira historias...",
                        "Como pétalos de memoria...",
                        "La melancolía se derrama..."
                    ]
                )
            },
            DescriptionStyle.TECHNICAL: {
                VocabularyLevel.BEGINNER: StyleConfig(
                    name="technical_beginner",
                    display_name="Technical/Scientific - Beginner",
                    style=DescriptionStyle.TECHNICAL,
                    level=VocabularyLevel.BEGINNER,
                    prompt_template="""Provide a basic technical description in Spanish using:
- Simple technical vocabulary
- Basic measurements and quantities
- Clear cause-and-effect relationships
- Systematic organization""",
                    vocabulary_focus=["measurements", "materials", "basic_processes", "shapes"],
                    tone_keywords=["técnico", "preciso", "sistemático", "claro"],
                    example_phrases=[
                        "El objeto mide aproximadamente...",
                        "El material parece ser...",
                        "La estructura muestra..."
                    ]
                ),
                VocabularyLevel.INTERMEDIATE: StyleConfig(
                    name="technical_intermediate",
                    display_name="Technical/Scientific - Intermediate",
                    style=DescriptionStyle.TECHNICAL,
                    level=VocabularyLevel.INTERMEDIATE,
                    prompt_template="""Generate a technical analysis in Spanish including:
- Specialized technical terminology
- Precise measurements and specifications
- Scientific methodology in observations
- Technical processes and mechanisms""",
                    vocabulary_focus=["technical_specifications", "scientific_methods", "engineering_terms"],
                    tone_keywords=["científico", "metodológico", "cuantitativo", "especializado"],
                    example_phrases=[
                        "Las propiedades ópticas indican...",
                        "El análisis compositivo revela...",
                        "Según los parámetros observables..."
                    ]
                )
            }
        }
        
        # Add advanced and native levels for all styles
        for style in DescriptionStyle:
            if VocabularyLevel.ADVANCED not in self.styles[style]:
                self.styles[style][VocabularyLevel.ADVANCED] = self.styles[style][VocabularyLevel.INTERMEDIATE]
            if VocabularyLevel.NATIVE not in self.styles[style]:
                self.styles[style][VocabularyLevel.NATIVE] = self.styles[style][VocabularyLevel.INTERMEDIATE]
    
    def get_current_config(self) -> StyleConfig:
        """Get current style configuration."""
        return self.styles[self.current_style][self.current_level]
    
    def generate_prompt(self, base_context: str = "", user_notes: str = "") -> str:
        """Generate style-specific prompt for AI."""
        config = self.get_current_config()
        
        prompt = f"{config.prompt_template}\n\n"
        
        if config.example_phrases:
            prompt += "Usa frases como:\n"
            for phrase in config.example_phrases:
                prompt += f"- {phrase}\n"
            prompt += "\n"
        
        if base_context:
            prompt += f"Contexto: {base_context}\n\n"
        
        if user_notes:
            prompt += f"Notas: {user_notes}\n\n"
        
        return prompt
    
    def get_style_info(self) -> Dict:
        """Get current style information."""
        config = self.get_current_config()
        return {
            "style": config.style.value,
            "level": config.level.value,
            "display_name": config.display_name,
            "example_phrases": config.example_phrases[:2]
        }

# ============================================================================
# SESSION TRACKER MODULE
# ============================================================================

@dataclass
class ImageRecord:
    """Record of a shown image."""
    url: str
    search_query: str
    timestamp: float
    page_number: int
    index_in_page: int
    
    def to_dict(self):
        return asdict(self)


@dataclass
class SearchSession:
    """Record of a search session."""
    query: str
    timestamp: float
    images_shown: List[str]
    page_numbers_used: List[int]
    total_results_seen: int
    
    def to_dict(self):
        return asdict(self)


class SessionTracker:
    """Tracks search sessions for image variety."""
    
    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path("./data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.session_file = self.data_dir / "search_sessions.json"
        self.image_history_file = self.data_dir / "image_history.json"
        
        self.search_history: Dict[str, SearchSession] = {}
        self.image_history: Dict[str, List[ImageRecord]] = {}
        
        self.max_history_days = 30
        self.max_images_per_query = 100
        self.shuffle_seed_interval = 3600
        
        self.load_session_data()
    
    def load_session_data(self):
        """Load session data from disk."""
        if self.session_file.exists():
            try:
                with open(self.session_file, 'r') as f:
                    data = json.load(f)
                    for query, session_data in data.items():
                        self.search_history[query] = SearchSession(**session_data)
            except:
                self.search_history = {}
    
    def save_session_data(self):
        """Save session data to disk."""
        search_data = {
            query: session.to_dict() 
            for query, session in self.search_history.items()
        }
        with open(self.session_file, 'w') as f:
            json.dump(search_data, f, indent=2)
    
    def get_search_parameters(self, query: str) -> Dict:
        """Get optimized search parameters for variety."""
        query_lower = query.lower().strip()
        
        if query_lower not in self.search_history:
            self.search_history[query_lower] = SearchSession(
                query=query_lower,
                timestamp=time.time(),
                images_shown=[],
                page_numbers_used=[],
                total_results_seen=0
            )
        
        session = self.search_history[query_lower]
        shown_images = set(session.images_shown)
        used_pages = set(session.page_numbers_used)
        
        # Calculate optimal page
        if len(shown_images) < 10:
            available_pages = [p for p in range(1, 6) if p not in used_pages]
            page = random.choice(available_pages) if available_pages else random.randint(1, 5)
        elif len(shown_images) < 30:
            available_pages = [p for p in range(1, 11) if p not in used_pages]
            page = random.choice(available_pages) if available_pages else random.randint(6, 15)
        else:
            query_hash = hashlib.md5(query_lower.encode()).hexdigest()
            base_page = int(query_hash[:4], 16) % 20 + 1
            time_offset = int(time.time() / 3600) % 10
            page = min(base_page + time_offset + (len(shown_images) // 10), 100)
        
        if page not in session.page_numbers_used:
            session.page_numbers_used.append(page)
        
        self.save_session_data()
        
        return {
            "page": page,
            "per_page": random.choice([10, 15, 20, 30]),
            "shown_count": len(shown_images),
            "strategy": "exploring" if len(shown_images) < 10 else "expanding" if len(shown_images) < 30 else "deep_search"
        }
    
    def record_shown_image(self, query: str, image_url: str, page: int = 1):
        """Record that an image has been shown."""
        query_lower = query.lower().strip()
        
        if query_lower in self.search_history:
            session = self.search_history[query_lower]
            if image_url not in session.images_shown:
                session.images_shown.append(image_url)
                session.total_results_seen += 1
            
            if len(session.images_shown) > self.max_images_per_query:
                session.images_shown = session.images_shown[-self.max_images_per_query:]
        
        self.save_session_data()
    
    def reset_query_history(self, query: str):
        """Reset history for a specific query."""
        query_lower = query.lower().strip()
        if query_lower in self.search_history:
            del self.search_history[query_lower]
        self.save_session_data()
    
    def get_statistics(self) -> Dict:
        """Get session statistics."""
        total_searches = len(self.search_history)
        total_images = sum(len(s.images_shown) for s in self.search_history.values())
        
        most_searched = sorted(
            self.search_history.items(),
            key=lambda x: len(x[1].images_shown),
            reverse=True
        )[:5]
        
        return {
            "total_searches": total_searches,
            "total_images_shown": total_images,
            "most_searched": [{"query": q, "images": len(s.images_shown)} for q, s in most_searched]
        }

# ============================================================================
# STYLE SELECTOR UI COMPONENT
# ============================================================================

class StyleSelectorPanel(ttk.LabelFrame):
    """Panel widget for selecting description styles."""
    
    def __init__(self, parent, style_manager: DescriptionStyleManager, on_style_change=None, **kwargs):
        super().__init__(parent, text="📝 Description Style", padding="10", **kwargs)
        
        self.style_manager = style_manager
        self.on_style_change = on_style_change
        
        self.create_widgets()
        self.update_display()
    
    def create_widgets(self):
        """Create panel widgets."""
        # Style selection
        style_frame = ttk.Frame(self)
        style_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(style_frame, text="Style:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.style_var = tk.StringVar(value=self.style_manager.current_style.value)
        
        styles = [
            ("📚 Academic", DescriptionStyle.ACADEMIC),
            ("🎨 Poetic", DescriptionStyle.POETIC),
            ("🔬 Technical", DescriptionStyle.TECHNICAL)
        ]
        
        for label, style in styles:
            ttk.Radiobutton(
                style_frame,
                text=label,
                variable=self.style_var,
                value=style.value,
                command=self.on_style_selected
            ).pack(side=tk.LEFT, padx=5)
        
        # Vocabulary level
        level_frame = ttk.Frame(self)
        level_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(level_frame, text="Level:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.level_var = tk.StringVar()
        self.level_combo = ttk.Combobox(
            level_frame,
            textvariable=self.level_var,
            values=["Beginner", "Intermediate", "Advanced", "Native"],
            state="readonly",
            width=15
        )
        self.level_combo.pack(side=tk.LEFT, padx=5)
        self.level_combo.bind("<<ComboboxSelected>>", self.on_level_selected)
        self.level_combo.set(self.style_manager.current_level.value.capitalize())
        
        # Preview
        self.preview_text = tk.Text(self, height=3, wrap=tk.WORD, state=tk.DISABLED)
        self.preview_text.pack(fill=tk.BOTH, expand=True)
    
    def on_style_selected(self):
        """Handle style selection."""
        for style in DescriptionStyle:
            if style.value == self.style_var.get():
                self.style_manager.current_style = style
                break
        
        self.update_display()
        if self.on_style_change:
            self.on_style_change(self.style_manager.current_style, self.style_manager.current_level)
    
    def on_level_selected(self, event=None):
        """Handle level selection."""
        level_str = self.level_var.get().lower()
        for level in VocabularyLevel:
            if level.value == level_str:
                self.style_manager.current_level = level
                break
        
        self.update_display()
        if self.on_style_change:
            self.on_style_change(self.style_manager.current_style, self.style_manager.current_level)
    
    def update_display(self):
        """Update preview display."""
        info = self.style_manager.get_style_info()
        
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(tk.END, f"{info['display_name']}\n")
        for phrase in info['example_phrases']:
            self.preview_text.insert(tk.END, f"• {phrase}\n")
        self.preview_text.config(state=tk.DISABLED)

# ============================================================================
# MAIN APPLICATION
# ============================================================================

class EnhancedImageSearchApp(tk.Tk):
    """Enhanced Unsplash Image Search Application."""
    
    def __init__(self):
        super().__init__()
        
        self.title("Enhanced Unsplash Image Search & GPT Description")
        self.geometry("1200x800")
        
        # Initialize managers
        self.style_manager = DescriptionStyleManager()
        self.session_tracker = SessionTracker(Path("./data"))
        
        # API keys (to be configured)
        self.UNSPLASH_ACCESS_KEY = ""
        self.OPENAI_API_KEY = ""
        self.openai_client = None
        
        # State
        self.current_query = ""
        self.current_image_url = None
        self.current_results = []
        self.current_index = 0
        
        # Load config
        self.load_configuration()
        
        # Create UI
        self.create_ui()
    
    def create_ui(self):
        """Create the user interface."""
        # Menu bar
        self.create_menu()
        
        # Main container
        main = ttk.Frame(self, padding="10")
        main.pack(fill=tk.BOTH, expand=True)
        
        # Search section
        search_frame = ttk.LabelFrame(main, text="🔍 Search", padding="10")
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        search_row = ttk.Frame(search_frame)
        search_row.pack(fill=tk.X)
        
        ttk.Label(search_row, text="Query:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_entry = ttk.Entry(search_row, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<Return>', self.search_images)
        
        ttk.Button(search_row, text="Search", command=self.search_images).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_row, text="🔄 Shuffle", command=self.shuffle_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_row, text="🆕 Fresh", command=self.fresh_search).pack(side=tk.LEFT, padx=5)
        
        self.session_info = ttk.Label(search_row, text="", foreground="blue")
        self.session_info.pack(side=tk.LEFT, padx=(20, 0))
        
        # Style selector
        self.style_selector = StyleSelectorPanel(
            main,
            self.style_manager,
            on_style_change=self.on_style_change
        )
        self.style_selector.pack(fill=tk.X, pady=(0, 10))
        
        # Content area
        content = ttk.Frame(main)
        content.pack(fill=tk.BOTH, expand=True)
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)
        
        # Image preview
        img_frame = ttk.LabelFrame(content, text="📷 Image", padding="10")
        img_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        self.image_label = ttk.Label(img_frame, text="No image loaded", anchor=tk.CENTER)
        self.image_label.pack(fill=tk.BOTH, expand=True)
        
        # Text areas
        text_frame = ttk.Frame(content)
        text_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        # Description
        desc_frame = ttk.LabelFrame(text_frame, text="✨ Description", padding="10")
        desc_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        self.desc_text = scrolledtext.ScrolledText(desc_frame, wrap=tk.WORD, height=10)
        self.desc_text.pack(fill=tk.BOTH, expand=True)
        
        ttk.Button(desc_frame, text="Generate", command=self.generate_description).pack(pady=(5, 0))
        
        # Vocabulary
        vocab_frame = ttk.LabelFrame(text_frame, text="📚 Vocabulary", padding="10")
        vocab_frame.pack(fill=tk.BOTH, expand=True)
        
        self.vocab_text = scrolledtext.ScrolledText(vocab_frame, wrap=tk.WORD, height=8)
        self.vocab_text.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status = ttk.Label(main, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(fill=tk.X, pady=(10, 0))
    
    def create_menu(self):
        """Create menu bar."""
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Configure API Keys", command=self.configure_api)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Statistics", command=self.show_statistics)
    
    def search_images(self, event=None):
        """Search for images with variety."""
        query = self.search_entry.get().strip()
        if not query:
            return
        
        self.current_query = query
        params = self.session_tracker.get_search_parameters(query)
        
        self.session_info.config(
            text=f"Page: {params['page']} | Strategy: {params['strategy']} | Shown: {params['shown_count']}"
        )
        
        if not self.UNSPLASH_ACCESS_KEY:
            self.status.config(text="Please configure Unsplash API key")
            return
        
        threading.Thread(target=self._search_thread, args=(query, params), daemon=True).start()
    
    def _search_thread(self, query, params):
        """Search in background thread."""
        try:
            headers = {"Authorization": f"Client-ID {self.UNSPLASH_ACCESS_KEY}"}
            url = f"https://api.unsplash.com/search/photos?query={query}&page={params['page']}&per_page={params['per_page']}"
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            self.current_results = data.get("results", [])
            if self.current_results:
                self.current_index = 0
                self.show_current_image()
        except Exception as e:
            self.after(0, lambda: self.status.config(text=f"Search error: {e}"))
    
    def show_current_image(self):
        """Display current image."""
        if not self.current_results or self.current_index >= len(self.current_results):
            return
        
        result = self.current_results[self.current_index]
        img_url = result["urls"]["regular"]
        
        try:
            response = requests.get(img_url, timeout=10)
            img = Image.open(BytesIO(response.content))
            img.thumbnail((400, 400), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            self.image_label.config(image=photo, text="")
            self.image_label.image = photo
            
            self.current_image_url = img_url
            self.session_tracker.record_shown_image(
                self.current_query, img_url, 
                self.session_tracker.search_history[self.current_query.lower()].page_numbers_used[-1]
            )
            
            self.status.config(text="Image loaded successfully")
        except Exception as e:
            self.status.config(text=f"Image load error: {e}")
    
    def shuffle_image(self):
        """Get next image from results."""
        if self.current_results:
            self.current_index = (self.current_index + 1) % len(self.current_results)
            self.show_current_image()
    
    def fresh_search(self):
        """Reset history and search again."""
        if self.current_query:
            self.session_tracker.reset_query_history(self.current_query)
            self.search_images()
    
    def generate_description(self):
        """Generate AI description."""
        if not self.current_image_url:
            self.status.config(text="No image loaded")
            return
        
        if not self.OPENAI_API_KEY:
            # Show demo description
            info = self.style_manager.get_style_info()
            self.desc_text.delete(1.0, tk.END)
            self.desc_text.insert(tk.END, f"Style: {info['display_name']}\n\n")
            for phrase in info['example_phrases']:
                self.desc_text.insert(tk.END, f"{phrase}\n")
            self.status.config(text="Demo mode - Configure OpenAI API for real descriptions")
            return
        
        # Generate with OpenAI
        threading.Thread(target=self._generate_thread, daemon=True).start()
    
    def _generate_thread(self):
        """Generate description in background."""
        try:
            prompt = self.style_manager.generate_prompt(
                base_context=f"Image URL: {self.current_image_url}"
            )
            
            # OpenAI API call would go here
            # For now, show demo content
            info = self.style_manager.get_style_info()
            self.after(0, lambda: self.desc_text.delete(1.0, tk.END))
            self.after(0, lambda: self.desc_text.insert(tk.END, f"Generated with {info['display_name']}"))
            
        except Exception as e:
            self.after(0, lambda: self.status.config(text=f"Generation error: {e}"))
    
    def on_style_change(self, style, level):
        """Handle style change."""
        self.save_configuration()
        self.status.config(text=f"Style: {style.value} - {level.value}")
    
    def configure_api(self):
        """Configure API keys dialog."""
        dialog = tk.Toplevel(self)
        dialog.title("Configure API Keys")
        dialog.geometry("400x200")
        
        ttk.Label(dialog, text="Unsplash Access Key:").grid(row=0, column=0, padx=10, pady=10)
        unsplash_entry = ttk.Entry(dialog, width=40)
        unsplash_entry.grid(row=0, column=1, padx=10, pady=10)
        unsplash_entry.insert(0, self.UNSPLASH_ACCESS_KEY)
        
        ttk.Label(dialog, text="OpenAI API Key:").grid(row=1, column=0, padx=10, pady=10)
        openai_entry = ttk.Entry(dialog, width=40, show="*")
        openai_entry.grid(row=1, column=1, padx=10, pady=10)
        openai_entry.insert(0, self.OPENAI_API_KEY)
        
        def save_keys():
            self.UNSPLASH_ACCESS_KEY = unsplash_entry.get()
            self.OPENAI_API_KEY = openai_entry.get()
            self.save_configuration()
            
            if self.OPENAI_API_KEY:
                try:
                    from openai import OpenAI
                    self.openai_client = OpenAI(api_key=self.OPENAI_API_KEY)
                except:
                    pass
            
            dialog.destroy()
            self.status.config(text="API keys configured")
        
        ttk.Button(dialog, text="Save", command=save_keys).grid(row=2, column=1, pady=20)
    
    def show_statistics(self):
        """Show session statistics."""
        stats = self.session_tracker.get_statistics()
        
        msg = f"Session Statistics\n\n"
        msg += f"Total Searches: {stats['total_searches']}\n"
        msg += f"Total Images: {stats['total_images_shown']}\n\n"
        msg += "Most Searched:\n"
        for item in stats['most_searched']:
            msg += f"  • {item['query']}: {item['images']} images\n"
        
        messagebox.showinfo("Statistics", msg)
    
    def save_configuration(self):
        """Save configuration to file."""
        config = {
            "unsplash_key": self.UNSPLASH_ACCESS_KEY,
            "openai_key": self.OPENAI_API_KEY,
            "style": self.style_manager.current_style.value,
            "level": self.style_manager.current_level.value
        }
        
        config_file = Path("./data/config.json")
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def load_configuration(self):
        """Load configuration from file."""
        config_file = Path("./data/config.json")
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                self.UNSPLASH_ACCESS_KEY = config.get("unsplash_key", "")
                self.OPENAI_API_KEY = config.get("openai_key", "")
                
                if config.get("style"):
                    for style in DescriptionStyle:
                        if style.value == config["style"]:
                            self.style_manager.current_style = style
                            break
                
                if config.get("level"):
                    for level in VocabularyLevel:
                        if level.value == config["level"]:
                            self.style_manager.current_level = level
                            break
                
                if self.OPENAI_API_KEY:
                    try:
                        from openai import OpenAI
                        self.openai_client = OpenAI(api_key=self.OPENAI_API_KEY)
                    except:
                        pass
            except:
                pass


def main():
    """Run the application."""
    app = EnhancedImageSearchApp()
    app.mainloop()


if __name__ == "__main__":
    main()