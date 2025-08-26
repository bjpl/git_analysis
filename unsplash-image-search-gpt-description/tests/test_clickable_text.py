"""
Test suite for ClickableText component.

Tests the functionality of word detection, clicking, and vocabulary integration.
"""

import unittest
import tkinter as tk
from tkinter import ttk
import tempfile
import os
from pathlib import Path
import sys

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from src.ui.components.clickable_text import ClickableText
    from src.models.vocabulary import VocabularyManager, VocabularyEntry
    from src.ui.theme_manager import ThemeManager
except ImportError:
    # Fallback for different path structures
    try:
        from ui.components.clickable_text import ClickableText
        from models.vocabulary import VocabularyManager, VocabularyEntry
        from ui.theme_manager import ThemeManager
    except ImportError as e:
        print(f"Could not import required modules: {e}")
        sys.exit(1)


class MockOpenAIService:
    """Mock OpenAI service for testing."""
    
    def __init__(self):
        self.model = "gpt-4o-mini"
        self.client = self
    
    def chat_completions_create(self, **kwargs):
        """Mock chat completions method."""
        # Return a mock response
        class MockResponse:
            def __init__(self):
                self.choices = [MockChoice()]
        
        class MockChoice:
            def __init__(self):
                self.message = MockMessage()
        
        class MockMessage:
            def __init__(self):
                # Simple translation logic for testing
                messages = kwargs.get('messages', [])
                if messages:
                    content = messages[0].get('content', '')
                    if 'playa' in content.lower():
                        self.content = "beach"
                    elif 'agua' in content.lower():
                        self.content = "water"
                    elif 'hermoso' in content.lower():
                        self.content = "beautiful"
                    else:
                        self.content = "translated_word"
        
        return MockResponse()
    
    # Make it work with the expected interface
    class ChatCompletions:
        def __init__(self, parent):
            self.parent = parent
        
        def create(self, **kwargs):
            return self.parent.chat_completions_create(**kwargs)
    
    def __init__(self):
        self.model = "gpt-4o-mini"
        self.chat = self.ChatCompletions(self)


class MockConfigManager:
    """Mock config manager for testing."""
    
    def __init__(self):
        self.config = {}


class TestClickableText(unittest.TestCase):
    """Test cases for ClickableText component."""
    
    def setUp(self):
        """Set up test environment."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during tests
        
        # Create temporary CSV file for testing
        self.temp_dir = tempfile.mkdtemp()
        self.vocab_file = Path(self.temp_dir) / "test_vocabulary.csv"
        
        # Initialize managers
        self.vocab_manager = VocabularyManager(self.vocab_file)
        self.openai_service = MockOpenAIService()
        self.theme_manager = ThemeManager(MockConfigManager())
        self.theme_manager.initialize(self.root)
        
        # Create ClickableText widget
        self.clickable_text = ClickableText(
            self.root,
            vocabulary_manager=self.vocab_manager,
            openai_service=self.openai_service,
            theme_manager=self.theme_manager,
            current_search_query="test query",
            current_image_url="http://test.com/image.jpg"
        )
    
    def tearDown(self):
        """Clean up after tests."""
        try:
            self.clickable_text.destroy()
            self.root.destroy()
            # Clean up temp files
            if os.path.exists(self.vocab_file):
                os.remove(self.vocab_file)
            os.rmdir(self.temp_dir)
        except:
            pass
    
    def test_initialization(self):
        """Test that ClickableText initializes properly."""
        self.assertIsInstance(self.clickable_text, ClickableText)
        self.assertEqual(self.clickable_text.current_search_query, "test query")
        self.assertEqual(self.clickable_text.current_image_url, "http://test.com/image.jpg")
        self.assertTrue(self.clickable_text.is_clickable)
    
    def test_spanish_word_detection(self):
        """Test detection of Spanish words."""
        # Test basic Spanish word detection
        self.assertTrue(self.clickable_text._is_likely_spanish_word("playa"))
        self.assertTrue(self.clickable_text._is_likely_spanish_word("hermoso"))
        self.assertTrue(self.clickable_text._is_likely_spanish_word("descripción"))
        
        # Test filtering of common words
        self.assertFalse(self.clickable_text._is_likely_spanish_word("el"))
        self.assertFalse(self.clickable_text._is_likely_spanish_word("la"))
        self.assertFalse(self.clickable_text._is_likely_spanish_word("de"))
        
        # Test English words
        self.assertFalse(self.clickable_text._is_likely_spanish_word("the"))
        self.assertFalse(self.clickable_text._is_likely_spanish_word("and"))
    
    def test_text_insertion_and_tagging(self):
        """Test that text insertion creates proper tags."""
        spanish_text = "Esta es una playa hermosa con agua cristalina."
        
        # Insert text
        self.clickable_text.insert(tk.END, spanish_text)
        self.clickable_text._make_text_clickable()
        
        # Check that content was inserted
        content = self.clickable_text.get("1.0", tk.END).strip()
        self.assertEqual(content, spanish_text)
        
        # Check that clickable tags were created
        ranges = self.clickable_text.tag_ranges(self.clickable_text.click_tag)
        self.assertTrue(len(ranges) > 0)  # Should have some tagged ranges
    
    def test_word_bounds_detection(self):
        """Test word boundary detection."""
        test_text = "Esta es una playa hermosa."
        self.clickable_text.insert(tk.END, test_text)
        
        # Test getting word at different positions
        word_at_start = self.clickable_text._get_word_at_index("1.0")
        self.assertEqual(word_at_start, "Esta")
        
        # Test word bounds
        start, end = self.clickable_text._get_word_bounds("1.0")
        word = self.clickable_text.get(start, end)
        self.assertTrue(word.strip() in ["Esta", "Es"])  # Depending on exact position
    
    def test_context_extraction(self):
        """Test context extraction around clicked words."""
        test_text = "Esta es una playa hermosa con agua cristalina y arena blanca."
        self.clickable_text.insert(tk.END, test_text)
        
        # Get context for a word in the middle
        context = self.clickable_text._get_word_context("1.12", "1.17")  # "playa"
        self.assertIsInstance(context, str)
        self.assertTrue(len(context) > 0)
    
    def test_clickable_state_toggle(self):
        """Test enabling/disabling clickable functionality."""
        # Initially should be clickable
        self.assertTrue(self.clickable_text.is_clickable)
        
        # Disable clicking
        self.clickable_text.set_clickable(False)
        self.assertFalse(self.clickable_text.is_clickable)
        
        # Enable clicking
        self.clickable_text.set_clickable(True)
        self.assertTrue(self.clickable_text.is_clickable)
    
    def test_context_update(self):
        """Test updating context information."""
        new_query = "new search query"
        new_url = "http://example.com/new_image.jpg"
        
        self.clickable_text.update_context(new_query, new_url)
        
        self.assertEqual(self.clickable_text.current_search_query, new_query)
        self.assertEqual(self.clickable_text.current_image_url, new_url)
    
    def test_vocabulary_entry_creation(self):
        """Test that vocabulary entries can be created properly."""
        # This tests the integration with VocabularyManager
        initial_count = self.vocab_manager.get_vocabulary_count()
        
        # Create a test vocabulary entry
        entry = VocabularyEntry(
            spanish="playa",
            english="beach",
            search_query="test query",
            image_url="http://test.com/image.jpg",
            context="una playa hermosa"
        )
        
        success = self.vocab_manager.add_vocabulary_entry(entry)
        self.assertTrue(success)
        
        new_count = self.vocab_manager.get_vocabulary_count()
        self.assertEqual(new_count, initial_count + 1)
    
    def test_theme_integration(self):
        """Test theme manager integration."""
        # Test that theme colors are applied
        colors = self.clickable_text._get_theme_colors()
        self.assertIsInstance(colors, dict)
        self.assertIn('bg', colors)
        self.assertIn('fg', colors)
        
        # Test theme change
        current_theme = self.theme_manager.current_theme
        self.theme_manager.toggle_theme()
        new_theme = self.theme_manager.current_theme
        self.assertNotEqual(current_theme, new_theme)
    
    def test_clear_functionality(self):
        """Test clearing text and cleanup."""
        # Add some text
        self.clickable_text.insert(tk.END, "Test text content")
        self.assertNotEqual(self.clickable_text.get("1.0", tk.END).strip(), "")
        
        # Clear it
        self.clickable_text.clear()
        self.assertEqual(self.clickable_text.get("1.0", tk.END).strip(), "")


class TestVocabularyIntegration(unittest.TestCase):
    """Test vocabulary integration functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.vocab_file = Path(self.temp_dir) / "test_vocab.csv"
        self.vocab_manager = VocabularyManager(self.vocab_file)
    
    def tearDown(self):
        """Clean up after tests."""
        if os.path.exists(self.vocab_file):
            os.remove(self.vocab_file)
        os.rmdir(self.temp_dir)
    
    def test_vocabulary_file_creation(self):
        """Test that vocabulary file is created with proper headers."""
        self.assertTrue(self.vocab_file.exists())
        
        # Check file contents
        with open(self.vocab_file, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            expected_headers = "Spanish,English,Date,Search Query,Image URL,Context"
            self.assertEqual(first_line, expected_headers)
    
    def test_duplicate_detection(self):
        """Test duplicate word detection."""
        # Add a word
        entry1 = VocabularyEntry("playa", "beach")
        success1 = self.vocab_manager.add_vocabulary_entry(entry1)
        self.assertTrue(success1)
        
        # Try to add the same word again
        entry2 = VocabularyEntry("playa", "shore")
        success2 = self.vocab_manager.add_vocabulary_entry(entry2)
        self.assertFalse(success2)  # Should fail due to duplicate
        
        # Verify only one entry exists
        self.assertEqual(self.vocab_manager.get_vocabulary_count(), 1)
    
    def test_entry_retrieval(self):
        """Test retrieving vocabulary entries."""
        # Add some entries
        entries = [
            VocabularyEntry("agua", "water"),
            VocabularyEntry("fuego", "fire"),
            VocabularyEntry("tierra", "earth")
        ]
        
        for entry in entries:
            self.vocab_manager.add_vocabulary_entry(entry)
        
        # Retrieve all entries
        all_entries = self.vocab_manager.get_all_entries()
        self.assertEqual(len(all_entries), 3)
        
        # Check that we can find our entries
        spanish_words = [entry.spanish for entry in all_entries]
        self.assertIn("agua", spanish_words)
        self.assertIn("fuego", spanish_words)
        self.assertIn("tierra", spanish_words)


def run_visual_test():
    """Run a visual test of the ClickableText component."""
    print("Starting visual test...")
    
    root = tk.Tk()
    root.title("ClickableText Visual Test")
    root.geometry("600x500")
    
    # Create temporary vocabulary file
    temp_dir = tempfile.mkdtemp()
    vocab_file = Path(temp_dir) / "test_vocabulary.csv"
    
    try:
        # Initialize managers
        vocab_manager = VocabularyManager(vocab_file)
        openai_service = MockOpenAIService()
        theme_manager = ThemeManager(MockConfigManager())
        theme_manager.initialize(root)
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Instructions
        instructions = tk.Label(
            main_frame,
            text="Visual Test - Click on Spanish words below to test functionality",
            font=('Arial', 12, 'bold')
        )
        instructions.pack(pady=(0, 10))
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        def toggle_theme():
            theme_manager.toggle_theme()
        
        def show_vocab():
            count = vocab_manager.get_vocabulary_count()
            print(f"Vocabulary count: {count}")
        
        ttk.Button(button_frame, text="Toggle Theme", command=toggle_theme).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Show Vocab Count", command=show_vocab).pack(side=tk.LEFT)
        
        # ClickableText widget
        text_frame = ttk.LabelFrame(main_frame, text="Clickable Spanish Text", padding="10")
        text_frame.pack(fill=tk.BOTH, expand=True)
        text_frame.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)
        
        clickable_text = ClickableText(
            text_frame,
            vocabulary_manager=vocab_manager,
            openai_service=openai_service,
            theme_manager=theme_manager,
            current_search_query="visual test",
            current_image_url="http://example.com/test.jpg",
            wrap=tk.WORD,
            font=("TkDefaultFont", 12)
        )
        clickable_text.grid(row=0, column=0, sticky="nsew")
        
        # Add sample Spanish text
        sample_text = """Esta es una imagen hermosa de una playa tropical con agua cristalina. 
Las palmeras proporcionan sombra natural para los visitantes. El cielo está 
despejado con nubes blancas que flotan lentamente. Las olas rompen suavemente 
contra la arena dorada, creando un ambiente muy tranquilo y relajante.

Los turistas pueden disfrutar de actividades como nadar, bucear, o simplemente 
descansar bajo el sol. La temperatura del agua es perfecta durante todo el año. 
Este paraíso tropical ofrece una experiencia unforgettable para todos los 
que buscan paz y belleza natural."""
        
        clickable_text.insert(tk.END, sample_text)
        
        # Status label
        status_label = tk.Label(
            main_frame,
            text="Click on Spanish words to translate and add to vocabulary",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_label.pack(fill=tk.X, pady=(10, 0))
        
        print("Visual test window opened. Try clicking on Spanish words.")
        print("Close the window to end the test.")
        
        root.mainloop()
        
    finally:
        # Cleanup
        try:
            if os.path.exists(vocab_file):
                os.remove(vocab_file)
            os.rmdir(temp_dir)
        except:
            pass


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test ClickableText component')
    parser.add_argument('--visual', action='store_true', help='Run visual test')
    parser.add_argument('--unit', action='store_true', help='Run unit tests')
    args = parser.parse_args()
    
    if args.visual:
        run_visual_test()
    elif args.unit or (not args.visual and not args.unit):
        # Run unit tests by default
        unittest.main(argv=[''], exit=False, verbosity=2)
        
        if not args.unit:
            # If no specific test was requested, offer to run visual test
            response = input("\nWould you like to run the visual test? (y/n): ")
            if response.lower().startswith('y'):
                run_visual_test()