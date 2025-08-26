"""
Test suite for description styles functionality
Tests the style system, prompt generation, and UI components
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tkinter as tk
import tempfile
import json
import os

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from features.description_styles import (
    DescriptionStyle, VocabularyLevel, DescriptionStyleManager,
    AcademicNeutralStyleHandler, PoeticLiteraryStyleHandler, 
    TechnicalScientificStyleHandler, get_style_manager
)
from ui.components.style_selector import StyleSelectorPanel, show_style_selector_dialog
from features.session_tracker import SessionTracker


class TestDescriptionStyles(unittest.TestCase):
    """Test description style functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.style_manager = DescriptionStyleManager()
    
    def test_style_enum_values(self):
        """Test that style enum has expected values"""
        self.assertEqual(DescriptionStyle.ACADEMIC.value, "academic")
        self.assertEqual(DescriptionStyle.POETIC.value, "poetic")
        self.assertEqual(DescriptionStyle.TECHNICAL.value, "technical")
    
    def test_vocabulary_level_enum_values(self):
        """Test that vocabulary level enum has expected values"""
        self.assertEqual(VocabularyLevel.BEGINNER.value, "beginner")
        self.assertEqual(VocabularyLevel.INTERMEDIATE.value, "intermediate")
        self.assertEqual(VocabularyLevel.ADVANCED.value, "advanced")
        self.assertEqual(VocabularyLevel.NATIVE.value, "native")
    
    def test_style_manager_initialization(self):
        """Test that style manager initializes correctly"""
        self.assertIsNotNone(self.style_manager)
        self.assertEqual(self.style_manager.get_current_style(), DescriptionStyle.ACADEMIC)
        self.assertEqual(self.style_manager.get_current_vocabulary_level(), VocabularyLevel.INTERMEDIATE)
    
    def test_get_available_styles(self):
        """Test getting available styles"""
        styles = self.style_manager.get_available_styles()
        self.assertEqual(len(styles), 3)
        
        style_names = [style['name'] for style in styles]
        self.assertIn('academic', style_names)
        self.assertIn('poetic', style_names)
        self.assertIn('technical', style_names)
    
    def test_set_current_style(self):
        """Test setting current style"""
        self.style_manager.set_current_style(DescriptionStyle.POETIC)
        self.assertEqual(self.style_manager.get_current_style(), DescriptionStyle.POETIC)
        
        self.style_manager.set_current_style(DescriptionStyle.TECHNICAL)
        self.assertEqual(self.style_manager.get_current_style(), DescriptionStyle.TECHNICAL)
    
    def test_set_vocabulary_level(self):
        """Test setting vocabulary level"""
        self.style_manager.set_vocabulary_level(VocabularyLevel.ADVANCED)
        self.assertEqual(self.style_manager.get_current_vocabulary_level(), VocabularyLevel.ADVANCED)
        
        self.style_manager.set_vocabulary_level(VocabularyLevel.BEGINNER)
        self.assertEqual(self.style_manager.get_current_vocabulary_level(), VocabularyLevel.BEGINNER)
    
    def test_invalid_style_raises_error(self):
        """Test that invalid style raises ValueError"""
        with self.assertRaises(ValueError):
            # This would need to be a non-existent style
            pass  # Can't easily test this with enum
    
    def test_export_import_preferences(self):
        """Test exporting and importing style preferences"""
        # Set specific preferences
        self.style_manager.set_current_style(DescriptionStyle.POETIC)
        self.style_manager.set_vocabulary_level(VocabularyLevel.ADVANCED)
        
        # Export preferences
        prefs = self.style_manager.export_style_preferences()
        self.assertEqual(prefs['current_style'], 'poetic')
        self.assertEqual(prefs['current_vocabulary_level'], 'advanced')
        
        # Change preferences
        self.style_manager.set_current_style(DescriptionStyle.ACADEMIC)
        self.style_manager.set_vocabulary_level(VocabularyLevel.BEGINNER)
        
        # Import original preferences
        self.style_manager.import_style_preferences(prefs)
        self.assertEqual(self.style_manager.get_current_style(), DescriptionStyle.POETIC)
        self.assertEqual(self.style_manager.get_current_vocabulary_level(), VocabularyLevel.ADVANCED)


class TestStyleHandlers(unittest.TestCase):
    """Test individual style handlers"""
    
    def setUp(self):
        """Set up test environment"""
        self.style_manager = DescriptionStyleManager()
    
    def test_academic_prompt_generation(self):
        """Test academic style prompt generation"""
        handler = self.style_manager.get_style_handler(DescriptionStyle.ACADEMIC)
        
        # Test basic prompt
        prompt = handler.generate_prompt()
        self.assertIn("académico", prompt.lower())
        self.assertIn("formal", prompt.lower())
        self.assertIn("objetivo", prompt.lower())
        
        # Test with context
        prompt_with_context = handler.generate_prompt(context="Una fotografía de paisaje")
        self.assertIn("Una fotografía de paisaje", prompt_with_context)
        
        # Test with focus areas
        prompt_with_focus = handler.generate_prompt(focus_areas=["colores", "composición"])
        self.assertIn("colores", prompt_with_focus)
        self.assertIn("composición", prompt_with_focus)
    
    def test_poetic_prompt_generation(self):
        """Test poetic style prompt generation"""
        handler = self.style_manager.get_style_handler(DescriptionStyle.POETIC)
        
        prompt = handler.generate_prompt()
        self.assertIn("poético", prompt.lower())
        self.assertIn("metáfor", prompt.lower())
        self.assertIn("expresiv", prompt.lower())
        
        # Test vocabulary level variation
        beginner_prompt = handler.generate_prompt(VocabularyLevel.BEGINNER)
        advanced_prompt = handler.generate_prompt(VocabularyLevel.ADVANCED)
        
        # These should be different
        self.assertNotEqual(beginner_prompt, advanced_prompt)
    
    def test_technical_prompt_generation(self):
        """Test technical style prompt generation"""
        handler = self.style_manager.get_style_handler(DescriptionStyle.TECHNICAL)
        
        prompt = handler.generate_prompt()
        self.assertIn("técnico", prompt.lower())
        self.assertIn("científico", prompt.lower())
        self.assertIn("precis", prompt.lower())
        
        # Test with different vocabulary levels
        for level in VocabularyLevel:
            level_prompt = handler.generate_prompt(level)
            self.assertIsInstance(level_prompt, str)
            self.assertTrue(len(level_prompt) > 100)  # Should be substantial
    
    def test_vocabulary_extraction_prompts(self):
        """Test vocabulary extraction prompts for each style"""
        test_description = "Esta es una imagen hermosa con colores vibrantes."
        
        for style in DescriptionStyle:
            handler = self.style_manager.get_style_handler(style)
            vocab_prompt = handler.get_vocabulary_extraction_prompt(test_description)
            
            # Should contain the description
            self.assertIn(test_description, vocab_prompt)
            
            # Should ask for JSON format
            self.assertIn("JSON", vocab_prompt)
            
            # Should be substantial
            self.assertTrue(len(vocab_prompt) > 200)


class TestStyleSelectorUI(unittest.TestCase):
    """Test style selector UI components"""
    
    def setUp(self):
        """Set up test environment with Tkinter"""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide test window
        
        # Create temporary directory for session tracker
        self.temp_dir = tempfile.mkdtemp()
        self.session_tracker = SessionTracker(Path(self.temp_dir))
    
    def tearDown(self):
        """Clean up test environment"""
        self.root.destroy()
        
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_style_selector_panel_creation(self):
        """Test that StyleSelectorPanel creates without errors"""
        try:
            panel = StyleSelectorPanel(self.root, self.session_tracker)
            self.assertIsNotNone(panel)
            
            # Test initial values
            self.assertIn('academic', panel.style_var.get())
            self.assertTrue(len(panel.vocab_level_var.get()) > 0)
            
        except Exception as e:
            self.fail(f"StyleSelectorPanel creation failed: {e}")
    
    def test_style_selection_methods(self):
        """Test style selection methods"""
        panel = StyleSelectorPanel(self.root, self.session_tracker)
        
        # Test setting academic style
        panel.style_var.set('academic')
        panel.update_style_manager()
        selected_style = panel.get_selected_style()
        self.assertEqual(selected_style, DescriptionStyle.ACADEMIC)
        
        # Test setting poetic style
        panel.style_var.set('poetic')
        panel.update_style_manager()
        selected_style = panel.get_selected_style()
        self.assertEqual(selected_style, DescriptionStyle.POETIC)
        
        # Test setting technical style
        panel.style_var.set('technical')
        panel.update_style_manager()
        selected_style = panel.get_selected_style()
        self.assertEqual(selected_style, DescriptionStyle.TECHNICAL)
    
    def test_vocabulary_level_selection(self):
        """Test vocabulary level selection"""
        panel = StyleSelectorPanel(self.root, self.session_tracker)
        
        # Test different vocabulary levels
        test_cases = [
            ('Principiante - Vocabulario básico y estructuras simples', VocabularyLevel.BEGINNER),
            ('Intermedio - Vocabulario variado con expresiones comunes', VocabularyLevel.INTERMEDIATE),
            ('Avanzado - Vocabulario sofisticado y estructuras complejas', VocabularyLevel.ADVANCED),
            ('Nativo - Vocabulario completo con modismos y expresiones idiomáticas', VocabularyLevel.NATIVE)
        ]
        
        for selection_text, expected_level in test_cases:
            panel.vocab_level_var.set(selection_text)
            panel.update_style_manager()
            selected_level = panel.get_selected_vocabulary_level()
            self.assertEqual(selected_level, expected_level)
    
    def test_callback_functionality(self):
        """Test that callbacks are called correctly"""
        callback_called = False
        callback_args = {}
        
        def test_callback(style, vocabulary_level):
            nonlocal callback_called, callback_args
            callback_called = True
            callback_args = {'style': style, 'vocabulary_level': vocabulary_level}
        
        panel = StyleSelectorPanel(self.root, self.session_tracker, test_callback)
        
        # Trigger a style change
        panel.style_var.set('poetic')
        panel.on_style_selection_change()
        
        # Check that callback was called
        self.assertTrue(callback_called)
        self.assertEqual(callback_args['style'], DescriptionStyle.POETIC)
    
    @patch('tkinter.messagebox.showinfo')
    def test_reset_to_defaults(self, mock_messagebox):
        """Test reset to defaults functionality"""
        panel = StyleSelectorPanel(self.root, self.session_tracker)
        
        # Change from defaults
        panel.style_var.set('technical')
        panel.vocab_level_var.set('Nativo - Vocabulario completo con modismos y expresiones idiomáticas')
        
        # Reset to defaults
        panel.reset_to_defaults()
        
        # Check that defaults are restored
        self.assertEqual(panel.style_var.get(), 'academic')
        self.assertIn('Intermedio', panel.vocab_level_var.get())


class TestSessionTrackerIntegration(unittest.TestCase):
    """Test integration with session tracker"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.session_tracker = SessionTracker(Path(self.temp_dir))
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_save_load_style_preferences(self):
        """Test saving and loading style preferences"""
        # Save preferences
        prefs = {
            'description_style': 'poetic',
            'vocabulary_level': 'advanced'
        }
        self.session_tracker.save_style_preferences(prefs)
        
        # Load preferences
        loaded_prefs = self.session_tracker.load_style_preferences()
        
        self.assertEqual(loaded_prefs['description_style'], 'poetic')
        self.assertEqual(loaded_prefs['vocabulary_level'], 'advanced')
    
    def test_session_stats_with_style_info(self):
        """Test that session stats include style information"""
        # Set style preferences
        self.session_tracker.current_session.description_style = 'technical'
        self.session_tracker.current_session.vocabulary_level = 'native'
        
        # Get session stats
        stats = self.session_tracker.get_session_stats()
        
        self.assertEqual(stats['description_style'], 'technical')
        self.assertEqual(stats['vocabulary_level'], 'native')
    
    def test_style_usage_stats(self):
        """Test style usage statistics"""
        # This would require some test data in the sessions file
        # For now, just test that the method exists and returns expected format
        stats = self.session_tracker.get_style_usage_stats()
        
        self.assertIn('style_usage', stats)
        self.assertIn('vocabulary_level_usage', stats)
        self.assertIn('total_sessions', stats)


class TestIntegrationWithMainApp(unittest.TestCase):
    """Test integration with main application"""
    
    def setUp(self):
        """Set up test environment"""
        self.style_manager = get_style_manager()
    
    def test_global_style_manager(self):
        """Test that global style manager works correctly"""
        # Test that we get the same instance
        manager1 = get_style_manager()
        manager2 = get_style_manager()
        
        # Should be the same object
        self.assertIs(manager1, manager2)
    
    def test_prompt_generation_integration(self):
        """Test full prompt generation workflow"""
        # Set style and vocabulary level
        self.style_manager.set_current_style(DescriptionStyle.POETIC)
        self.style_manager.set_vocabulary_level(VocabularyLevel.ADVANCED)
        
        # Generate prompt
        prompt = self.style_manager.generate_description_prompt(
            context="Una hermosa fotografía de naturaleza",
            focus_areas=["colores", "texturas", "atmósfera"]
        )
        
        # Verify prompt contains expected elements
        self.assertIn("poético", prompt.lower())
        self.assertIn("Una hermosa fotografía de naturaleza", prompt)
        self.assertIn("colores", prompt)
        self.assertIn("texturas", prompt)
        self.assertIn("atmósfera", prompt)
    
    def test_vocabulary_extraction_integration(self):
        """Test vocabulary extraction workflow"""
        test_description = "Esta imagen muestra un paisaje sereno con colores cálidos y texturas suaves."
        
        for style in DescriptionStyle:
            self.style_manager.set_current_style(style)
            vocab_prompt = self.style_manager.get_vocabulary_extraction_prompt(test_description)
            
            # Should contain the description
            self.assertIn(test_description, vocab_prompt)
            
            # Should be style-specific
            if style == DescriptionStyle.ACADEMIC:
                self.assertIn("académic", vocab_prompt.lower())
            elif style == DescriptionStyle.POETIC:
                self.assertIn("poétic", vocab_prompt.lower())
            elif style == DescriptionStyle.TECHNICAL:
                self.assertIn("técnic", vocab_prompt.lower())


if __name__ == '__main__':
    # Create test suite
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestDescriptionStyles,
        TestStyleHandlers,
        TestStyleSelectorUI,
        TestSessionTrackerIntegration,
        TestIntegrationWithMainApp
    ]
    
    for test_class in test_classes:
        tests = test_loader.loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)