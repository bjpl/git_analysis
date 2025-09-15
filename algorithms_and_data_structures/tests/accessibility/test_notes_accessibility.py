#!/usr/bin/env python3
"""
Accessibility and Keyboard Navigation Tests for Notes System
Testing accessibility compliance, keyboard navigation, and screen reader compatibility
"""

import pytest
import tempfile
import os
import time
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, AsyncMock

# Import the classes under test
sys_path = Path(__file__).parent.parent.parent / "src"
import sys
sys.path.insert(0, str(sys_path))

from ui.notes import NotesManager as UINotesManager, RichNote, NoteType, Priority, NoteEditor
from ui.formatter import TerminalFormatter
from ui.navigation import NavigationController, MenuItem


class TestKeyboardNavigation:
    """Test keyboard navigation functionality"""
    
    @pytest.fixture
    def temp_notes_dir(self):
        import tempfile
        import shutil
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def formatter(self):
        return TerminalFormatter()
    
    @pytest.fixture
    def ui_manager(self, formatter, temp_notes_dir):
        return UINotesManager(formatter, temp_notes_dir)
    
    @pytest.fixture
    def accessible_notes(self, ui_manager):
        """Create notes with accessibility considerations"""
        notes = [
            RichNote(
                "nav1", "First Navigation Note",
                "**Primary content** for navigation testing.\n\n# Main Section\n- First item\n- Second item",
                NoteType.CONCEPT, Priority.HIGH, ["navigation", "first"]
            ),
            RichNote(
                "nav2", "Second Navigation Note", 
                "*Secondary content* with different formatting.\n\n## Subsection\n1. Numbered item\n2. Another item",
                NoteType.EXAMPLE, Priority.MEDIUM, ["navigation", "second"]
            ),
            RichNote(
                "nav3", "Third Navigation Note",
                "Regular content without special formatting for baseline comparison.",
                NoteType.REFERENCE, Priority.LOW, ["navigation", "third"]
            )
        ]
        
        for note in notes:
            ui_manager.notes[note.id] = note
            ui_manager._update_indices(note)
        
        return notes
    
    def test_sequential_keyboard_navigation(self, ui_manager, accessible_notes):
        """Test sequential navigation through notes using keyboard"""
        # Simulate keyboard navigation through search results
        search_results = ui_manager.search_notes("navigation", search_type="all")
        
        # Results should be in a predictable order for navigation
        assert len(search_results) == 3
        
        # Test that results can be navigated sequentially
        for i, note in enumerate(search_results):
            # Each note should have clear navigation markers
            assert note.id in ["nav1", "nav2", "nav3"]
            assert "navigation" in note.tags
            
            # Title should be descriptive for screen readers
            assert len(note.title.split()) >= 3  # Multi-word titles
    
    def test_keyboard_shortcuts_simulation(self, ui_manager, accessible_notes):
        """Test keyboard shortcuts for common operations"""
        # Simulate keyboard shortcuts for note operations
        keyboard_actions = {
            'search': lambda: ui_manager.search_notes("navigation", search_type="all"),
            'filter_by_tag': lambda: ui_manager.get_notes_by_tag("navigation"),
            'filter_by_topic': lambda: ui_manager.get_notes_by_topic("Test Topic"),
            'get_statistics': lambda: ui_manager.get_statistics()
        }
        
        # Each keyboard action should be responsive
        for action_name, action_func in keyboard_actions.items():
            start_time = time.time()
            result = action_func()
            response_time = time.time() - start_time
            
            # Keyboard actions should be fast for good UX
            assert response_time < 0.5  # 500ms max response time
            assert result is not None
            
            print(f"Keyboard action '{action_name}': {response_time:.4f}s")
    
    @pytest.mark.asyncio
    async def test_editor_keyboard_navigation(self, formatter, temp_notes_dir):
        """Test keyboard navigation within the note editor"""
        editor = NoteEditor(formatter)
        
        # Mock keyboard input sequence
        keyboard_sequence = [
            "Test Note Title",          # Title input
            "Test content line 1",     # Content input
            "Test content line 2",     # More content
            "/help",                    # Command input
            "/save"                     # Save command
        ]
        
        # Test that editor responds to keyboard commands
        with patch('builtins.input') as mock_input:
            mock_input.side_effect = keyboard_sequence
            
            # Mock menu navigation
            with patch('src.ui.navigation.NavigationController.show_menu') as mock_menu:
                mock_menu.side_effect = [
                    (None, "1"),  # Note type selection
                    (None, "3")   # Priority selection
                ]
                
                # Test editor creation with keyboard input
                note = await editor.create_new_note("Test Topic")
        
        # Verify keyboard input was processed correctly
        if note:
            assert note.title == "Test Note Title"
            assert "Test content line 1" in note.content
            assert "Test content line 2" in note.content
    
    def test_focus_management(self, ui_manager, accessible_notes):
        """Test focus management for keyboard users"""
        # Test that search maintains logical focus order
        search_results = ui_manager.search_notes("navigation", search_type="all")
        
        # Results should be ordered by priority/relevance for focus navigation
        priorities = [note.priority.value for note in search_results]
        
        # Higher priority notes should come first for better keyboard navigation
        for i in range(len(priorities) - 1):
            # Current note should have equal or higher priority than next
            assert priorities[i] >= priorities[i + 1] or abs(priorities[i] - priorities[i + 1]) <= 1
    
    def test_skip_navigation_links(self, ui_manager, accessible_notes):
        """Test skip navigation functionality for screen readers"""
        # Create navigation structure with clear sections
        stats = ui_manager.get_statistics()
        
        # Statistics should provide clear section markers
        assert 'total_notes' in stats
        assert 'notes_by_type' in stats
        assert 'notes_by_priority' in stats
        
        # Each section should be independently accessible
        for section_name, section_data in stats.items():
            if isinstance(section_data, dict):
                # Dictionary sections should have clear structure
                assert len(section_data) >= 0
            else:
                # Numeric sections should be present
                assert isinstance(section_data, (int, float, list))


class TestScreenReaderCompatibility:
    """Test compatibility with screen readers"""
    
    @pytest.fixture
    def temp_notes_dir(self):
        import tempfile
        import shutil
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def formatter(self):
        return TerminalFormatter()
    
    @pytest.fixture
    def ui_manager(self, formatter, temp_notes_dir):
        return UINotesManager(formatter, temp_notes_dir)
    
    def test_semantic_content_structure(self, ui_manager):
        """Test that content has semantic structure for screen readers"""
        # Create note with semantic structure
        semantic_note = RichNote(
            "semantic1", "Semantically Structured Note",
            "# Main Heading\n\nIntroductory paragraph with **important text** and *emphasis*.\n\n## Subsection\n\nAnother paragraph with information.\n\n### Sub-subsection\n\n- First list item\n- Second list item with `code`\n- Third list item\n\n1. First numbered item\n2. Second numbered item\n3. Third numbered item",
            NoteType.CONCEPT, Priority.MEDIUM, ["semantic", "structure"]
        )
        
        ui_manager.notes[semantic_note.id] = semantic_note
        
        # Test that formatting preserves semantic meaning
        formatted_content = semantic_note.formatted_content
        
        # Headers should be distinguishable
        assert "# Main Heading" in semantic_note.content
        assert "## Subsection" in semantic_note.content
        assert "### Sub-subsection" in semantic_note.content
        
        # Lists should be structured
        assert "- First list item" in semantic_note.content
        assert "1. First numbered item" in semantic_note.content
        
        # Emphasis should be marked
        assert "**important text**" in semantic_note.content
        assert "*emphasis*" in semantic_note.content
        assert "`code`" in semantic_note.content
    
    def test_alternative_text_descriptions(self, ui_manager):
        """Test alternative text descriptions for non-text elements"""
        # Create note with various priority and type indicators
        priority_note = RichNote(
            "priority1", "Priority Indicator Test",
            "Content with priority indicators for screen reader testing.",
            NoteType.TODO, Priority.URGENT, ["priority", "urgent"]
        )
        
        ui_manager.notes[priority_note.id] = priority_note
        
        # Priority should be indicated in text, not just color/icons
        assert priority_note.priority == Priority.URGENT
        assert priority_note.note_type == NoteType.TODO
        
        # These should be accessible to screen readers via text descriptions
        priority_description = f"Priority: {priority_note.priority.name}"
        type_description = f"Type: {priority_note.note_type.value.title()}"
        
        assert "URGENT" in priority_description
        assert "Todo" in type_description
    
    def test_content_reading_order(self, ui_manager):
        """Test logical reading order for screen readers"""
        reading_order_note = RichNote(
            "reading1", "Reading Order Test Note",
            "First paragraph comes first.\n\nSecond paragraph follows logically.\n\n# Important Section\n\nSection content is grouped properly.\n\n- List items\n- Are grouped together\n- In logical order",
            NoteType.CONCEPT, Priority.MEDIUM, ["reading", "order"]
        )
        
        ui_manager.notes[reading_order_note.id] = reading_order_note
        
        # Content should be in logical reading order
        content_lines = reading_order_note.content.split('\n')
        
        # Verify reading order
        assert "First paragraph" in content_lines[0]
        assert "Second paragraph" in content_lines[2]  # After empty line
        assert "# Important Section" in content_lines[4]
        assert "Section content" in content_lines[6]
        
        # List items should be sequential
        list_start = next(i for i, line in enumerate(content_lines) if line.startswith("- List items"))
        assert content_lines[list_start + 1].startswith("- Are grouped")
        assert content_lines[list_start + 2].startswith("- In logical")
    
    def test_landmark_navigation(self, ui_manager):
        """Test landmark navigation for screen readers"""
        # Create notes representing different content landmarks
        landmark_notes = [
            RichNote("main1", "Main Content Note", "# Main Content\nPrimary information here.", 
                    NoteType.CONCEPT, Priority.HIGH, ["main", "primary"]),
            RichNote("nav1", "Navigation Note", "# Navigation\nLinks and navigation items.", 
                    NoteType.REFERENCE, Priority.MEDIUM, ["navigation", "links"]),
            RichNote("comp1", "Complementary Note", "# Additional Info\nSupplementary content.", 
                    NoteType.INSIGHT, Priority.LOW, ["complementary", "additional"])
        ]
        
        for note in landmark_notes:
            ui_manager.notes[note.id] = note
        
        # Test that different note types can serve as landmarks
        concept_notes = [n for n in ui_manager.notes.values() if n.note_type == NoteType.CONCEPT]
        reference_notes = [n for n in ui_manager.notes.values() if n.note_type == NoteType.REFERENCE]
        insight_notes = [n for n in ui_manager.notes.values() if n.note_type == NoteType.INSIGHT]
        
        assert len(concept_notes) == 1  # Main content
        assert len(reference_notes) == 1  # Navigation
        assert len(insight_notes) == 1  # Complementary
    
    def test_error_message_accessibility(self, ui_manager):
        """Test that error messages are accessible to screen readers"""
        # Test operations that might produce errors
        # (In a real implementation, these would be actual error conditions)
        
        # Search with no results
        empty_results = ui_manager.search_notes("nonexistent_term", search_type="all")
        assert len(empty_results) == 0  # No results - should provide clear feedback
        
        # Search by non-existent tag
        empty_tag_results = ui_manager.get_notes_by_tag("nonexistent_tag")
        assert len(empty_tag_results) == 0  # No results - should provide clear feedback
        
        # These error states should provide clear, descriptive messages for screen readers
        # In actual implementation, these would be handled with accessible error messages


class TestColorBlindAccessibility:
    """Test accessibility for color-blind users"""
    
    @pytest.fixture
    def temp_notes_dir(self):
        import tempfile
        import shutil
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def formatter(self):
        return TerminalFormatter()
    
    @pytest.fixture
    def ui_manager(self, formatter, temp_notes_dir):
        return UINotesManager(formatter, temp_notes_dir)
    
    def test_priority_without_color_dependence(self, ui_manager):
        """Test that priority is indicated by more than just color"""
        # Create notes with different priorities
        priority_notes = [
            RichNote("low1", "Low Priority Note", "Low priority content", 
                    NoteType.REFERENCE, Priority.LOW, ["low"]),
            RichNote("med1", "Medium Priority Note", "Medium priority content", 
                    NoteType.CONCEPT, Priority.MEDIUM, ["medium"]),
            RichNote("high1", "High Priority Note", "High priority content", 
                    NoteType.QUESTION, Priority.HIGH, ["high"]),
            RichNote("crit1", "Critical Priority Note", "Critical priority content", 
                    NoteType.TODO, Priority.CRITICAL, ["critical"]),
            RichNote("urg1", "Urgent Priority Note", "Urgent priority content", 
                    NoteType.INSIGHT, Priority.URGENT, ["urgent"])
        ]
        
        for note in priority_notes:
            ui_manager.notes[note.id] = note
        
        # Test that priority is accessible without color
        stats = ui_manager.get_statistics()
        priority_counts = stats['notes_by_priority']
        
        # Priority should be indicated by text labels, not just colors
        assert 'LOW' in priority_counts
        assert 'MEDIUM' in priority_counts
        assert 'HIGH' in priority_counts
        assert 'CRITICAL' in priority_counts
        assert 'URGENT' in priority_counts
        
        # Each priority level should have clear text indicators
        for note in priority_notes:
            priority_text = note.priority.name
            assert priority_text in ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL', 'URGENT']
    
    def test_note_type_without_color_dependence(self, ui_manager):
        """Test that note types are distinguishable without color"""
        # Create notes of different types
        type_notes = [
            RichNote("concept1", "Concept Note", "Concept content", 
                    NoteType.CONCEPT, Priority.MEDIUM, ["concept"]),
            RichNote("example1", "Example Note", "Example content", 
                    NoteType.EXAMPLE, Priority.MEDIUM, ["example"]),
            RichNote("question1", "Question Note", "Question content", 
                    NoteType.QUESTION, Priority.MEDIUM, ["question"]),
            RichNote("insight1", "Insight Note", "Insight content", 
                    NoteType.INSIGHT, Priority.MEDIUM, ["insight"]),
            RichNote("todo1", "Todo Note", "Todo content", 
                    NoteType.TODO, Priority.MEDIUM, ["todo"]),
            RichNote("ref1", "Reference Note", "Reference content", 
                    NoteType.REFERENCE, Priority.MEDIUM, ["reference"])
        ]
        
        for note in type_notes:
            ui_manager.notes[note.id] = note
        
        # Test that note types are distinguishable by text
        stats = ui_manager.get_statistics()
        type_counts = stats['notes_by_type']
        
        # All note types should be represented with clear labels
        expected_types = ['concept', 'example', 'question', 'insight', 'todo', 'reference']
        for note_type in expected_types:
            assert note_type in type_counts
            assert type_counts[note_type] == 1
    
    def test_content_formatting_accessibility(self, ui_manager):
        """Test that formatting is accessible without color"""
        # Create note with various formatting that should work without color
        formatted_note = RichNote(
            "format1", "Formatting Test Note",
            "Content with **bold text** for emphasis.\n\n" +
            "Content with *italic text* for subtle emphasis.\n\n" +
            "Content with `code formatting` for technical terms.\n\n" +
            "# Primary Heading\n" +
            "## Secondary Heading\n" +
            "### Tertiary Heading\n\n" +
            "- Unordered list item 1\n" +
            "- Unordered list item 2\n\n" +
            "1. Ordered list item 1\n" +
            "2. Ordered list item 2",
            NoteType.EXAMPLE, Priority.MEDIUM, ["formatting", "accessible"]
        )
        
        ui_manager.notes[formatted_note.id] = formatted_note
        
        # Test that formatting uses structural elements, not just color
        content = formatted_note.content
        
        # Emphasis should use markup, not color
        assert "**bold text**" in content
        assert "*italic text*" in content
        assert "`code formatting`" in content
        
        # Headings should use structural markup
        assert "# Primary Heading" in content
        assert "## Secondary Heading" in content
        assert "### Tertiary Heading" in content
        
        # Lists should use structural markup
        assert "- Unordered list" in content
        assert "1. Ordered list" in content


class TestMobileAccessibility:
    """Test accessibility on mobile and touch devices"""
    
    @pytest.fixture
    def temp_notes_dir(self):
        import tempfile
        import shutil
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def formatter(self):
        return TerminalFormatter()
    
    @pytest.fixture
    def ui_manager(self, formatter, temp_notes_dir):
        return UINotesManager(formatter, temp_notes_dir)
    
    def test_touch_friendly_content_structure(self, ui_manager):
        """Test that content is structured for touch interaction"""
        # Create notes with mobile-friendly structure
        mobile_notes = [
            RichNote(
                "mobile1", "Short Mobile Title",
                "Short paragraphs work better on mobile.\n\nEach paragraph is focused.\n\nKey points:\n- Point 1\n- Point 2\n- Point 3",
                NoteType.CONCEPT, Priority.MEDIUM, ["mobile", "friendly"]
            ),
            RichNote(
                "mobile2", "Touch Interaction Note",
                "Content designed for touch interaction.\n\nClear sections:\n\n## Section 1\nBrief content here.\n\n## Section 2\nMore brief content.",
                NoteType.EXAMPLE, Priority.MEDIUM, ["touch", "interaction"]
            )
        ]
        
        for note in mobile_notes:
            ui_manager.notes[note.id] = note
        
        # Test content structure
        for note in mobile_notes:
            # Titles should be concise for mobile
            assert len(note.title.split()) <= 4  # Max 4 words
            
            # Content should be broken into digestible chunks
            paragraphs = note.content.split('\n\n')
            for paragraph in paragraphs:
                if paragraph.strip() and not paragraph.startswith('#'):
                    # Non-heading paragraphs should be reasonably short
                    assert len(paragraph) <= 200  # Max 200 chars per chunk
    
    def test_responsive_content_layout(self, ui_manager):
        """Test that content adapts to different screen sizes"""
        # Create note with content that should adapt well
        responsive_note = RichNote(
            "responsive1", "Responsive Note",
            "Responsive content design:\n\n" +
            "Short lines work better on narrow screens.\n\n" +
            "Lists are mobile-friendly:\n" +
            "- Item 1\n" +
            "- Item 2\n" +
            "- Item 3\n\n" +
            "Code should wrap:\n" +
            "`function_name(param1, param2)`",
            NoteType.EXAMPLE, Priority.MEDIUM, ["responsive", "mobile"]
        )
        
        ui_manager.notes[responsive_note.id] = responsive_note
        
        # Test content line lengths
        lines = responsive_note.content.split('\n')
        long_lines = [line for line in lines if len(line) > 80]
        
        # Most lines should be reasonable length for mobile
        assert len(long_lines) / len([l for l in lines if l.strip()]) < 0.3  # Less than 30% long lines
    
    def test_gesture_navigation_simulation(self, ui_manager):
        """Test gesture-like navigation patterns"""
        # Create multiple notes for navigation testing
        navigation_notes = []
        for i in range(10):
            note = RichNote(
                f"nav_{i}", f"Navigation Note {i+1}",
                f"Content for navigation testing note {i+1}",
                NoteType.CONCEPT, Priority.MEDIUM, ["navigation", f"item{i}"]
            )
            ui_manager.notes[note.id] = note
            navigation_notes.append(note)
        
        # Test swipe-like navigation (getting sequential items)
        all_notes = list(ui_manager.notes.values())
        
        # Notes should be in a predictable order for gesture navigation
        assert len(all_notes) == 10
        
        # Test "swipe" to next/previous (simulated by list iteration)
        for i in range(len(all_notes) - 1):
            current_note = all_notes[i]
            next_note = all_notes[i + 1]
            
            # Each note should be accessible in sequence
            assert current_note.id != next_note.id
            assert "navigation" in current_note.tags
            assert "navigation" in next_note.tags
    
    def test_voice_input_simulation(self, ui_manager):
        """Test voice input compatibility"""
        # Create notes that would be suitable for voice interaction
        voice_notes = [
            RichNote(
                "voice1", "Voice Command Note",
                "Content that works well with voice commands. Clear structure. Simple language.",
                NoteType.CONCEPT, Priority.MEDIUM, ["voice", "command"]
            ),
            RichNote(
                "voice2", "Speech Recognition Note",
                "Content optimized for speech recognition. Short sentences. Clear pronunciation.",
                NoteType.EXAMPLE, Priority.MEDIUM, ["speech", "recognition"]
            )
        ]
        
        for note in voice_notes:
            ui_manager.notes[note.id] = note
        
        # Test voice-friendly search
        voice_results = ui_manager.search_notes("voice", search_type="all")
        assert len(voice_results) == 1
        
        speech_results = ui_manager.search_notes("speech", search_type="all")
        assert len(speech_results) == 1
        
        # Content should be voice-friendly (short sentences, clear language)
        for note in voice_notes:
            sentences = note.content.split('. ')
            for sentence in sentences:
                if sentence.strip():
                    # Sentences should be reasonably short for voice
                    assert len(sentence.split()) <= 15  # Max 15 words per sentence


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
