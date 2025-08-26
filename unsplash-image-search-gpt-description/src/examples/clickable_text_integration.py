"""
Example integration of ClickableText component with the existing main application.

This file shows how to modify main.py to use the new ClickableText component
instead of the regular ScrolledText widget for the description area.
"""

import tkinter as tk
from tkinter import scrolledtext
from pathlib import Path
import sys

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from ui.components.clickable_text import ClickableText
    from ui.theme_manager import ThemeManager
    from models.vocabulary import VocabularyManager
    from services.openai_service import OpenAIService
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all required modules are available")


class ClickableTextDemo:
    """
    Demo application showing how to integrate ClickableText with existing app structure.
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Clickable Text Integration Demo")
        self.root.geometry("800x600")
        
        # Initialize managers (mock versions for demo)
        self.setup_managers()
        
        # Create UI
        self.create_ui()
        
        # Load sample content
        self.load_sample_content()
    
    def setup_managers(self):
        """Setup the required managers for the demo."""
        
        # Mock config manager
        class MockConfigManager:
            def __init__(self):
                self.config_dir = Path('.')
                self.data_dir = Path('./data')
                self.data_dir.mkdir(exist_ok=True)
            
            def get_paths(self):
                return {
                    'data_dir': self.data_dir,
                    'vocabulary_file': self.data_dir / 'vocabulary.csv'
                }
        
        config_manager = MockConfigManager()
        
        # Initialize vocabulary manager
        paths = config_manager.get_paths()
        self.vocabulary_manager = VocabularyManager(paths['vocabulary_file'])
        
        # Initialize theme manager
        self.theme_manager = ThemeManager(config_manager)
        self.theme_manager.initialize(self.root)
        
        # Mock OpenAI service (replace with real API key for actual translation)
        class MockOpenAIService:
            def __init__(self):
                self.client = None
                self.model = "gpt-4o-mini"
            
            # This would be the actual OpenAI service in real app
            # self.openai_service = OpenAIService(api_key="your-api-key-here")
        
        self.openai_service = MockOpenAIService()
        
        # Current context (would come from actual image search in real app)
        self.current_query = "tropical beach"
        self.current_image_url = "https://example.com/beach.jpg"
    
    def create_ui(self):
        """Create the demo UI."""
        
        # Main container
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="ClickableText Integration Demo",
            font=('Arial', 16, 'bold')
        )
        title_label.pack(pady=(0, 10))
        
        # Instructions
        instructions = tk.Label(
            main_frame,
            text="Click on Spanish words in the text below to translate and add to vocabulary",
            font=('Arial', 10),
            fg='gray'
        )
        instructions.pack(pady=(0, 10))
        
        # Control buttons
        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Button(
            control_frame,
            text="Toggle Theme",
            command=self.toggle_theme
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            control_frame,
            text="Load New Content",
            command=self.load_sample_content
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            control_frame,
            text="Toggle Clickable",
            command=self.toggle_clickable
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            control_frame,
            text="Show Vocabulary Count",
            command=self.show_vocab_count
        ).pack(side=tk.LEFT)
        
        # Create content area with both regular and clickable text widgets for comparison
        content_frame = tk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Regular ScrolledText (left side)
        regular_frame = tk.LabelFrame(content_frame, text="Regular ScrolledText", padding="10")
        regular_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        regular_frame.rowconfigure(0, weight=1)
        regular_frame.columnconfigure(0, weight=1)
        
        self.regular_text = scrolledtext.ScrolledText(
            regular_frame,
            wrap=tk.WORD,
            font=("TkDefaultFont", 12)
        )
        self.regular_text.grid(row=0, column=0, sticky="nsew")
        
        # ClickableText (right side)
        clickable_frame = tk.LabelFrame(content_frame, text="ClickableText Component", padding="10")
        clickable_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        clickable_frame.rowconfigure(0, weight=1)
        clickable_frame.columnconfigure(0, weight=1)
        
        self.clickable_text = ClickableText(
            clickable_frame,
            vocabulary_manager=self.vocabulary_manager,
            openai_service=self.openai_service,
            theme_manager=self.theme_manager,
            current_search_query=self.current_query,
            current_image_url=self.current_image_url,
            wrap=tk.WORD,
            font=("TkDefaultFont", 12)
        )
        self.clickable_text.grid(row=0, column=0, sticky="nsew")
        
        # Status bar
        self.status_label = tk.Label(
            main_frame,
            text="Ready - Click on Spanish words to translate and add to vocabulary",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_label.pack(fill=tk.X, pady=(10, 0))
    
    def load_sample_content(self):
        """Load sample Spanish content into both text widgets."""
        
        sample_texts = [
            """Esta imagen muestra una hermosa playa tropical con aguas cristalinas. 
La arena es blanca y fina, perfecta para caminar descalzo. Los árboles de coco 
proporcionan sombra natural para los visitantes. El cielo está despejado con 
algunas nubes blancas que flotan lentamente. Las olas rompen suavemente contra 
la orilla, creando un sonido relajante.""",
            
            """En esta fotografía vemos un paisaje montañoso espectacular. Las montañas 
se extienden hacia el horizonte, creando una vista impresionante. Los picos están 
cubiertos de nieve durante todo el año. El valle verde contrasta beautifully con 
las rocas grises de las cimas. Algunos senderos serpenteantes permiten a los 
excursionistas explorar esta región natural.""",
            
            """La ciudad nocturna cobra vida con miles de luces brillantes. Los rascacielos 
iluminados crean un skyline impresionante contra el cielo oscuro. Las calles están 
llenas de tráfico y peatones que caminan por las aceras. Los restaurantes y cafés 
permanecen abiertos hasta altas horas de la noche. La energía urbana es palpable 
en cada esquina de esta metrópolis moderna."""
        ]
        
        import random
        selected_text = random.choice(sample_texts)
        
        # Clear both text widgets
        self.regular_text.delete("1.0", tk.END)
        self.clickable_text.clear()
        
        # Insert the same text into both
        self.regular_text.insert(tk.END, selected_text)
        self.clickable_text.insert(tk.END, selected_text)
        
        self.status_label.config(text="New content loaded - Try clicking words in the right panel")
    
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        self.theme_manager.toggle_theme()
        current_theme = self.theme_manager.current_theme
        self.status_label.config(text=f"Theme changed to: {current_theme}")
    
    def toggle_clickable(self):
        """Toggle clickable functionality on/off."""
        current_state = self.clickable_text.is_clickable
        self.clickable_text.set_clickable(not current_state)
        new_state = "enabled" if not current_state else "disabled"
        self.status_label.config(text=f"Clickable functionality {new_state}")
    
    def show_vocab_count(self):
        """Show current vocabulary count."""
        count = self.vocabulary_manager.get_vocabulary_count()
        self.status_label.config(text=f"Vocabulary entries: {count}")
        
        # Show a sample of recent entries if any
        if count > 0:
            entries = self.vocabulary_manager.get_all_entries()
            recent = entries[-3:] if entries else []
            if recent:
                recent_words = [f"'{entry.spanish}' = '{entry.english}'" for entry in recent]
                print(f"Recent vocabulary entries:")
                for word in recent_words:
                    print(f"  {word}")
    
    def run(self):
        """Run the demo application."""
        self.root.mainloop()


def show_integration_instructions():
    """
    Show step-by-step integration instructions for existing main.py
    """
    
    instructions = """
    
    INTEGRATION INSTRUCTIONS FOR MAIN.PY
    ====================================
    
    1. Import the ClickableText component:
       
       Add this import near the top of main.py:
       ```python
       from src.ui.components.clickable_text import ClickableText
       ```
    
    2. Initialize vocabulary manager in __init__:
       
       Add this in ImageSearchApp.__init__ after setting up config_manager:
       ```python
       # Initialize vocabulary manager
       if hasattr(self, 'CSV_TARGET_WORDS'):
           self.vocabulary_manager = VocabularyManager(self.CSV_TARGET_WORDS)
       else:
           # Fallback for incomplete initialization
           self.vocabulary_manager = None
       ```
    
    3. Replace description_text widget in create_placeholder_widgets():
       
       Replace this code:
       ```python
       self.description_text = scrolledtext.ScrolledText(
           desc_frame, 
           wrap=tk.WORD, 
           state=tk.DISABLED,
           font=("TkDefaultFont", 12)
       )
       ```
       
       With this:
       ```python
       self.description_text = ClickableText(
           desc_frame,
           vocabulary_manager=self.vocabulary_manager,
           openai_service=None,  # Will be set later when API is ready
           theme_manager=self.theme_manager,
           current_search_query="",
           current_image_url="",
           wrap=tk.WORD,
           state=tk.DISABLED,
           font=("TkDefaultFont", 12)
       )
       ```
    
    4. Update description display method:
       
       Modify display_description() method:
       ```python
       def display_description(self, text):
           \"\"\"Display generated description.\"\"\"
           self.description_text.config(state=tk.NORMAL)
           self.description_text.delete("1.0", tk.END)
           
           # Update context for vocabulary entries
           self.description_text.update_context(
               search_query=self.current_query,
               image_url=self.current_image_url
           )
           
           # Update OpenAI service reference
           if hasattr(self, 'openai_client') and self.openai_client:
               # Create OpenAI service wrapper if needed
               if not hasattr(self, 'openai_service_wrapper'):
                   class OpenAIServiceWrapper:
                       def __init__(self, client, model):
                           self.client = client
                           self.model = model
                   
                   self.openai_service_wrapper = OpenAIServiceWrapper(
                       self.openai_client, 
                       self.GPT_MODEL
                   )
               
               # Update the clickable text's OpenAI service
               self.description_text.openai_service = self.openai_service_wrapper
           
           self.description_text.insert(tk.END, text)
           self.description_text.config(state=tk.DISABLED)
           self.copy_desc_button.config(state=tk.NORMAL)
           self.update_status("Description generated successfully - Click words to add to vocabulary")
       ```
    
    5. Initialize theme manager if not already done:
       
       Add this in complete_initialization():
       ```python
       # Initialize theme manager if not already done
       if not hasattr(self, 'theme_manager'):
           self.theme_manager = ThemeManager(self.config_manager)
           self.theme_manager.initialize(self)
       ```
    
    6. Optional - Add vocabulary stats to UI:
       
       You can add a vocabulary count display to the status bar:
       ```python
       def update_vocab_stats(self):
           if self.vocabulary_manager:
               count = self.vocabulary_manager.get_vocabulary_count()
               vocab_text = f"Vocabulary: {count} words"
               # Update your stats label or create a new one
               if hasattr(self, 'vocab_stats_label'):
                   self.vocab_stats_label.config(text=vocab_text)
       ```
    
    IMPORTANT NOTES:
    - The ClickableText component is fully backward compatible with ScrolledText
    - Word clicking only works when OpenAI service is properly configured
    - The component respects the existing theme system
    - Vocabulary is automatically saved to CSV file
    - Pop-up confirmations appear when words are successfully added
    
    TESTING:
    1. Run the application normally
    2. Generate a description in Spanish
    3. Try clicking on Spanish words in the description
    4. Check data/vocabulary.csv for new entries
    """
    
    print(instructions)


if __name__ == "__main__":
    print("ClickableText Integration Demo")
    print("=" * 50)
    
    # Show integration instructions
    show_integration_instructions()
    
    print("\nStarting demo application...")
    print("Note: For full functionality, configure OpenAI API key")
    
    # Run demo
    try:
        demo = ClickableTextDemo()
        demo.run()
    except Exception as e:
        print(f"Demo failed to start: {e}")
        print("This is expected if required dependencies are not available")