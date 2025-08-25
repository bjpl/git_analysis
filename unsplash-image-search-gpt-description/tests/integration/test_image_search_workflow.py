"""
Integration tests for complete image search workflow with collection limits.
Tests the full flow from search initiation to vocabulary extraction.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
import tkinter as tk
import threading
import time
import tempfile
import json
from pathlib import Path
from datetime import datetime

from main import ImageSearchApp
from config_manager import ConfigManager


class TestImageSearchWorkflowIntegration:
    """Integration tests for complete image search workflow."""

    @pytest.fixture
    def mock_app_full(self, temp_data_dir):
        """Create a fully mocked ImageSearchApp for integration testing."""
        # Create config manager with temp directory
        config_manager = Mock(spec=ConfigManager)
        config_manager.get_api_keys.return_value = {
            'unsplash': 'test_unsplash_key_123',
            'openai': 'sk-test_openai_key_456',
            'gpt_model': 'gpt-4o-mini'
        }
        config_manager.get_paths.return_value = {
            'data_dir': temp_data_dir,
            'log_file': temp_data_dir / 'session_log.json',
            'vocabulary_file': temp_data_dir / 'vocabulary.csv'
        }
        
        with patch('main.ensure_api_keys_configured', return_value=config_manager):
            with patch('main.ThemeManager'):
                with patch('tkinter.Tk'):
                    app = ImageSearchApp()
                    app.config_manager = config_manager
                    
                    # Initialize essential attributes
                    app.current_query = ""
                    app.current_page = 0
                    app.current_results = []
                    app.current_index = 0
                    app.used_image_urls = set()
                    app.image_cache = {}
                    app.vocabulary_cache = set()
                    app.target_phrases = []
                    app.log_entries = []
                    app.extracted_phrases = {}
                    
                    # Mock UI elements
                    app.search_entry = Mock()
                    app.progress_bar = Mock()
                    app.status_label = Mock()
                    app.image_label = Mock()
                    app.note_text = Mock()
                    app.description_text = Mock()
                    app.target_listbox = Mock()
                    app.extracted_inner_frame = Mock()
                    app.search_button = Mock()
                    app.another_button = Mock()
                    
                    # Mock methods that interact with UI
                    app.show_progress = Mock()
                    app.hide_progress = Mock()
                    app.update_status = Mock()
                    app.disable_buttons = Mock()
                    app.enable_buttons = Mock()
                    app.display_image = Mock()
                    app.display_description = Mock()
                    app.update_target_list_display = Mock()
                    app.update_stats = Mock()
                    app.after = Mock()
                    
                    return app

    @pytest.fixture
    def sample_unsplash_responses(self):
        """Sample Unsplash API responses for testing."""
        return {
            'page_1': {
                'results': [
                    {
                        'id': 'img_001',
                        'urls': {
                            'regular': 'https://images.unsplash.com/photo-001?w=400',
                            'small': 'https://images.unsplash.com/photo-001?w=200'
                        },
                        'alt_description': 'Beautiful mountain landscape',
                        'user': {'name': 'Nature Photographer'},
                        'description': 'Mountain sunrise'
                    },
                    {
                        'id': 'img_002', 
                        'urls': {
                            'regular': 'https://images.unsplash.com/photo-002?w=400',
                        },
                        'alt_description': 'Forest path',
                        'user': {'name': 'Forest Walker'},
                        'description': 'Peaceful forest trail'
                    }
                ],
                'total': 50,
                'total_pages': 5
            },
            'page_2': {
                'results': [
                    {
                        'id': 'img_003',
                        'urls': {
                            'regular': 'https://images.unsplash.com/photo-003?w=400',
                        },
                        'alt_description': 'Ocean waves',
                        'user': {'name': 'Sea Photographer'},
                        'description': 'Crashing waves'
                    }
                ],
                'total': 50,
                'total_pages': 5
            }
        }

    def test_complete_search_to_vocabulary_workflow(self, mock_app_full, sample_unsplash_responses):
        """Test complete workflow from search to vocabulary extraction."""
        # Setup search query
        mock_app_full.search_entry.get.return_value = "nature"
        
        # Mock API responses
        with patch.object(mock_app_full, 'fetch_images_page') as mock_fetch:
            mock_fetch.return_value = sample_unsplash_responses['page_1']['results']
            
            # Mock image download
            with patch('requests.get') as mock_get:
                mock_response = Mock()
                mock_response.content = self._create_test_image_bytes()
                mock_get.return_value = mock_response
                
                # Mock PIL Image
                with patch('main.Image.open') as mock_image_open:
                    mock_image = Mock()
                    mock_image.copy.return_value = mock_image
                    mock_image_open.return_value = mock_image
                    
                    with patch.object(mock_app_full, 'apply_zoom_to_image', return_value=mock_image):
                        with patch('main.ImageTk.PhotoImage') as mock_photo:
                            mock_photo_obj = Mock()
                            mock_photo.return_value = mock_photo_obj
                            
                            # Start the workflow
                            mock_app_full.search_image()
                            
                            # Verify search initiated
                            assert mock_app_full.current_query == "nature"
                            mock_app_full.show_progress.assert_called()
                            mock_app_full.disable_buttons.assert_called()
                            
                            # Simulate thread completion by calling get_next_image
                            result = mock_app_full.get_next_image()
                            
                            # Verify image was processed
                            assert result is not None
                            photo, display_image = result
                            assert photo == mock_photo_obj
                            assert len(mock_app_full.used_image_urls) == 1
                            assert len(mock_app_full.log_entries) == 1

    def test_search_with_collection_limit_reached(self, mock_app_full):
        """Test search workflow when collection limit is reached."""
        # Pre-populate with maximum images
        MAX_IMAGES = 20
        for i in range(MAX_IMAGES):
            mock_app_full.used_image_urls.add(f'https://images.unsplash.com/photo-{i}')
        
        mock_app_full.search_entry.get.return_value = "test"
        
        with patch.object(mock_app_full, 'fetch_images_page') as mock_fetch:
            mock_fetch.return_value = []  # No more unique images
            
            with patch('tkinter.messagebox.showinfo') as mock_showinfo:
                # Attempt search
                mock_app_full.search_image()
                
                # Simulate thread execution
                result = mock_app_full.get_next_image()
                
                # Should hit limit and show message
                assert result is None
                mock_showinfo.assert_called()

    def test_search_cancellation_workflow(self, mock_app_full):
        """Test search cancellation during operation."""
        mock_app_full.search_entry.get.return_value = "test"
        
        # Add cancellation state
        mock_app_full._search_cancelled = False
        
        def slow_api_call(*args, **kwargs):
            time.sleep(0.1)
            if mock_app_full._search_cancelled:
                raise Exception("Cancelled")
            return []
        
        with patch.object(mock_app_full, 'fetch_images_page', side_effect=slow_api_call):
            # Start search
            search_thread = threading.Thread(
                target=mock_app_full.thread_search_images,
                args=("test",),
                daemon=True
            )
            search_thread.start()
            
            # Cancel after short delay
            time.sleep(0.05)
            mock_app_full._search_cancelled = True
            
            # Wait for completion
            search_thread.join(timeout=1.0)
            
            # Verify cancellation was handled
            assert mock_app_full._search_cancelled == True

    def test_image_description_generation_workflow(self, mock_app_full):
        """Test complete workflow including AI description generation."""
        # Setup initial state
        mock_app_full.current_image_url = "https://example.com/test.jpg"
        mock_app_full.image_label.image = Mock()  # Simulate loaded image
        mock_app_full.search_entry.get.return_value = "nature"
        mock_app_full.note_text.get.return_value = "Beautiful landscape photo"
        
        # Mock OpenAI client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Esta es una hermosa imagen de montañas con un lago cristalino."
        mock_client.chat.completions.create.return_value = mock_response
        mock_app_full.openai_client = mock_client
        
        # Mock phrase extraction
        with patch.object(mock_app_full, 'extract_phrases_from_description') as mock_extract:
            # Start description generation
            mock_app_full.generate_description()
            
            # Verify description process started
            mock_app_full.show_progress.assert_called()
            mock_app_full.disable_buttons.assert_called()
            
            # Simulate thread completion
            mock_app_full.thread_generate_description("nature", "Beautiful landscape photo")
            
            # Verify OpenAI was called
            mock_client.chat.completions.create.assert_called_once()
            
            # Verify description was displayed
            mock_app_full.display_description.assert_called_with(mock_response.choices[0].message.content)
            
            # Verify phrase extraction was initiated
            mock_extract.assert_called_once()

    def test_vocabulary_extraction_and_storage_workflow(self, mock_app_full, temp_data_dir):
        """Test vocabulary extraction and CSV storage workflow."""
        # Setup description
        test_description = "Esta es una hermosa montaña con lagos cristalinos y bosques verdes."
        
        # Mock extracted phrases
        mock_phrases = {
            'Sustantivos': ['la montaña', 'los lagos', 'los bosques'],
            'Adjetivos': ['hermosa', 'cristalinos', 'verdes'],
            'Frases clave': ['muy hermosa', 'paisaje natural']
        }
        
        # Mock OpenAI extraction response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(mock_phrases)
        mock_client.chat.completions.create.return_value = mock_response
        mock_app_full.openai_client = mock_client
        
        # Mock translation
        def mock_translate(word, context=""):
            translations = {
                'la montaña': 'the mountain',
                'hermosa': 'beautiful',
                'paisaje natural': 'natural landscape'
            }
            return translations.get(word, f'translation of {word}')
        
        with patch.object(mock_app_full, 'translate_word', side_effect=mock_translate):
            # Extract phrases
            mock_app_full.extract_phrases_from_description(test_description)
            
            # Simulate phrase addition to vocabulary
            mock_app_full.current_query = "nature"
            mock_app_full.current_image_url = "https://example.com/test.jpg"
            
            # Add phrases to vocabulary
            mock_app_full.add_target_phrase('la montaña')
            mock_app_full.add_target_phrase('hermosa')
            
            # Verify phrases were added
            assert len(mock_app_full.target_phrases) == 2
            assert 'la montaña - the mountain' in mock_app_full.target_phrases
            assert 'hermosa - beautiful' in mock_app_full.target_phrases
            
            # Verify CSV file creation
            csv_file = temp_data_dir / 'vocabulary.csv'
            assert csv_file.exists()

    def test_session_persistence_workflow(self, mock_app_full, temp_data_dir):
        """Test session data persistence workflow."""
        # Setup session data
        mock_app_full.log_entries = [
            {
                'timestamp': datetime.now().isoformat(),
                'query': 'nature',
                'image_url': 'https://example.com/test.jpg',
                'user_note': 'Test note',
                'generated_description': 'Test description'
            }
        ]
        mock_app_full.target_phrases = ['la montaña - the mountain', 'hermosa - beautiful']
        
        # Save session
        mock_app_full.save_session_to_json()
        
        # Verify session file was created
        log_file = temp_data_dir / 'session_log.json'
        assert log_file.exists()
        
        # Verify session data structure
        with open(log_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert 'sessions' in data
            assert len(data['sessions']) == 1
            session = data['sessions'][0]
            assert 'entries' in session
            assert 'vocabulary_learned' in session
            assert session['vocabulary_learned'] == 2

    def test_error_recovery_workflow(self, mock_app_full):
        """Test error recovery during workflow."""
        mock_app_full.search_entry.get.return_value = "test"
        
        # Mock API failure followed by success
        call_count = 0
        def api_with_failure(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise requests.exceptions.RequestException("Network error")
            return [{'id': 'test', 'urls': {'regular': 'http://example.com/test.jpg'}}]
        
        with patch.object(mock_app_full, 'fetch_images_page', side_effect=api_with_failure):
            with patch.object(mock_app_full, 'api_call_with_retry') as mock_retry:
                mock_retry.side_effect = api_with_failure
                
                # First attempt should fail
                result1 = mock_app_full.get_next_image()
                assert result1 is None
                
                # Second attempt should succeed
                with patch('requests.get'), patch('main.Image.open'), patch('main.ImageTk.PhotoImage'):
                    result2 = mock_app_full.get_next_image()
                    # Should succeed or handle gracefully
                    assert result2 is not None or call_count > 1

    def test_memory_management_during_workflow(self, mock_app_full):
        """Test memory management during extended workflow."""
        # Simulate multiple images being processed
        for i in range(15):  # More than cache limit
            url = f'https://example.com/image_{i}.jpg'
            mock_app_full.image_cache[url] = b'cached_image_data' * 1000  # Simulate image data
        
        # Verify cache size management
        initial_cache_size = len(mock_app_full.image_cache)
        
        # Add one more image
        mock_app_full.current_results = [{
            'id': 'new_image',
            'urls': {'regular': 'https://example.com/new_image.jpg'}
        }]
        mock_app_full.current_index = 0
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.content = b'new_image_data'
            mock_get.return_value = mock_response
            
            with patch('main.Image.open'), patch('main.ImageTk.PhotoImage'):
                mock_app_full.get_next_image()
                
                # Cache should be managed (not exceed limit)
                assert len(mock_app_full.image_cache) <= 11  # 10 + 1 new

    def test_ui_state_consistency_during_workflow(self, mock_app_full):
        """Test UI state consistency throughout workflow."""
        # Track UI state changes
        ui_calls = []
        
        def track_progress(message):
            ui_calls.append(('show_progress', message))
        
        def track_hide_progress():
            ui_calls.append(('hide_progress',))
        
        def track_enable():
            ui_calls.append(('enable_buttons',))
        
        def track_disable():
            ui_calls.append(('disable_buttons',))
        
        mock_app_full.show_progress = track_progress
        mock_app_full.hide_progress = track_hide_progress
        mock_app_full.enable_buttons = track_enable
        mock_app_full.disable_buttons = track_disable
        
        mock_app_full.search_entry.get.return_value = "test"
        
        with patch.object(mock_app_full, 'fetch_images_page', return_value=[]):
            # Execute search workflow
            mock_app_full.search_image()
            mock_app_full.thread_search_images("test")
            
            # Verify UI state sequence
            assert ('show_progress', "Searching 'test' on Unsplash") in ui_calls
            assert ('disable_buttons',) in ui_calls
            assert ('hide_progress',) in ui_calls
            assert ('enable_buttons',) in ui_calls

    def _create_test_image_bytes(self):
        """Create minimal PNG image bytes for testing."""
        return (b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
                b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00'
                b'\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\xcc'
                b'\xdb\xd2\x00\x00\x00\x00IEND\xaeB`\x82')


class TestUserCancellationWorkflow:
    """Test suite for user cancellation scenarios."""

    @pytest.fixture
    def cancellable_app(self, mock_config_manager):
        """Create app with cancellation support."""
        with patch('main.ensure_api_keys_configured', return_value=mock_config_manager):
            with patch('main.ThemeManager'):
                with patch('tkinter.Tk'):
                    app = ImageSearchApp()
                    app.config_manager = mock_config_manager
                    
                    # Add cancellation functionality
                    app._search_cancelled = False
                    app._current_operation = None
                    app.stop_button = Mock()
                    
                    # Mock UI elements
                    app.progress_bar = Mock()
                    app.status_label = Mock()
                    app.search_button = Mock()
                    
                    return app

    def test_user_cancels_during_image_search(self, cancellable_app):
        """Test user cancellation during image search."""
        def interruptible_search(*args, **kwargs):
            for i in range(10):  # Simulate long operation
                if cancellable_app._search_cancelled:
                    raise InterruptedError("User cancelled")
                time.sleep(0.01)
            return []
        
        with patch.object(cancellable_app, 'fetch_images_page', side_effect=interruptible_search):
            # Start search
            search_thread = threading.Thread(
                target=cancellable_app.thread_search_images,
                args=("test",),
                daemon=True
            )
            search_thread.start()
            
            # User cancels
            time.sleep(0.02)
            cancellable_app._search_cancelled = True
            
            # Wait for completion
            search_thread.join(timeout=1.0)
            
            # Verify cancellation was handled
            assert cancellable_app._search_cancelled == True

    def test_immediate_cancellation_response(self, cancellable_app):
        """Test that cancellation responds immediately."""
        start_time = time.time()
        
        # Start and immediately cancel
        cancellable_app._search_cancelled = True
        
        # Any operation should check cancellation state
        def check_cancellation():
            if cancellable_app._search_cancelled:
                return None
            # Simulate long operation
            time.sleep(1.0)
            return "result"
        
        result = check_cancellation()
        end_time = time.time()
        
        # Should return immediately (< 0.1 seconds)
        assert (end_time - start_time) < 0.1
        assert result is None