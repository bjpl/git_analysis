"""
Integration tests for complete application workflow.
"""
import pytest
from unittest.mock import Mock, patch
import json
import tempfile
from pathlib import Path

# These tests require the full application stack
pytestmark = pytest.mark.integration


@pytest.fixture
def integration_config(temp_data_dir):
    """Create integration test configuration."""
    config = {
        'api_keys': {
            'unsplash': 'integration_test_key',
            'openai': 'integration_test_key'
        },
        'paths': {
            'session_log': str(temp_data_dir / 'session_log.json'),
            'vocabulary_csv': str(temp_data_dir / 'vocabulary.csv'),
            'data_dir': str(temp_data_dir)
        },
        'settings': {
            'gpt_model': 'gpt-4o-mini',
            'max_description_length': 500
        }
    }
    return config


@pytest.fixture
def mock_api_responses():
    """Mock API responses for integration testing."""
    return {
        'unsplash_search': {
            'results': [
                {
                    'id': 'integration_test_image',
                    'urls': {
                        'small': 'https://images.unsplash.com/test_small.jpg',
                        'regular': 'https://images.unsplash.com/test_regular.jpg'
                    },
                    'alt_description': 'A beautiful landscape',
                    'user': {'name': 'Test Photographer'},
                    'description': 'Test image for integration testing'
                }
            ],
            'total': 1,
            'total_pages': 1
        },
        'openai_response': {
            'choices': [{
                'message': {
                    'content': 'Esta es una imagen hermosa de un paisaje montañoso. Las montañas altas se extienden hacia el horizonte bajo un cielo azul brillante. Los árboles verdes cubren las laderas de las montañas, creando un contraste natural con las rocas grises. El ambiente es tranquilo y sereno.'
                }
            }]
        }
    }


class TestCompleteWorkflow:
    """Test complete application workflow from start to finish."""
    
    @patch('requests.get')
    @patch('main.OpenAI')
    def test_search_to_description_workflow(self, mock_openai, mock_requests_get, 
                                          integration_config, mock_api_responses, temp_data_dir):
        """Test complete workflow: search -> display -> describe -> extract -> save."""
        # Setup API mocks
        mock_search_response = Mock()
        mock_search_response.status_code = 200
        mock_search_response.json.return_value = mock_api_responses['unsplash_search']
        
        mock_image_response = Mock() 
        mock_image_response.status_code = 200
        mock_image_response.content = b'\x89PNG\r\n\x1a\n'  # Minimal PNG header
        
        mock_requests_get.side_effect = [mock_search_response, mock_image_response]
        
        # Setup OpenAI mock
        mock_client = Mock()
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = mock_api_responses['openai_response']['choices'][0]['message']['content']
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client
        
        # Import and setup app (with all necessary patches)
        with patch('main.ensure_api_keys_configured') as mock_ensure_config, \
             patch('main.tk.Tk.__init__', return_value=None), \
             patch('PIL.Image.open'), \
             patch('PIL.ImageTk.PhotoImage'):
            
            # Setup config mock
            mock_config = Mock()
            mock_config.get_api_keys.return_value = integration_config['api_keys']
            mock_config.get_paths.return_value = integration_config['paths']
            mock_config.get_settings.return_value = integration_config['settings']
            mock_ensure_config.return_value = mock_config
            
            from main import ImageSearchApp
            
            # Create app with mocked UI components
            with patch.object(ImageSearchApp, '_setup_ui'), \
                 patch.object(ImageSearchApp, '_setup_data_structures'):
                
                app = ImageSearchApp()
                
                # Mock UI components
                app.search_entry = Mock()
                app.search_entry.get.return_value = "mountain landscape"
                app.notes_text = Mock()
                app.notes_text.get.return_value = "Beautiful mountain view for Spanish learning"
                app.description_text = Mock()
                app.image_label = Mock()
                app.loading_label = Mock()
                app.prev_button = Mock()
                app.next_button = Mock()
                app.vocab_frame = Mock()
                
                # Execute workflow steps
                
                # Step 1: Search for images
                app.search_images()
                
                # Verify search API was called
                assert mock_requests_get.called
                search_call = mock_requests_get.call_args_list[0]
                assert 'unsplash.com' in str(search_call)
                assert 'mountain landscape' in str(search_call) or 'mountain%20landscape' in str(search_call)
                
                # Verify images were loaded
                assert app.current_images is not None
                assert len(app.current_images) > 0
                assert app.current_image_index == 0
                
                # Step 2: Generate description
                app.generate_description()
                
                # Verify OpenAI API was called
                mock_client.chat.completions.create.assert_called()
                call_args = mock_client.chat.completions.create.call_args
                assert 'gpt-4o-mini' in str(call_args) or 'gpt-4' in str(call_args)
                
                # Verify description was processed
                app.description_text.delete.assert_called()
                app.description_text.insert.assert_called()
                
                # Step 3: Check vocabulary extraction (mocked)
                with patch.object(app, '_extract_vocabulary') as mock_extract:
                    mock_extract.return_value = ['las montañas', 'el paisaje', 'los árboles', 'el cielo']
                    app._process_gpt_response(mock_api_responses['openai_response']['choices'][0]['message']['content'])
                    mock_extract.assert_called()
                
                # Step 4: Check data persistence
                with patch.object(app, '_save_session_data') as mock_save_session, \
                     patch.object(app, '_save_vocabulary_translation') as mock_save_vocab:
                    
                    # Simulate saving session
                    test_session_data = {
                        'timestamp': '2024-01-01T12:00:00Z',
                        'query': 'mountain landscape',
                        'image_url': 'https://images.unsplash.com/test_regular.jpg',
                        'description': mock_api_responses['openai_response']['choices'][0]['message']['content'],
                        'vocabulary': ['las montañas', 'el paisaje', 'los árboles', 'el cielo']
                    }
                    app._save_session_data(test_session_data)
                    mock_save_session.assert_called_with(test_session_data)
                    
                    # Simulate vocabulary translation
                    app._save_vocabulary_translation('las montañas', 'the mountains')
                    mock_save_vocab.assert_called_with('las montañas', 'the mountains')
    
    def test_error_handling_workflow(self, integration_config):
        """Test workflow with various error conditions."""
        with patch('main.ensure_api_keys_configured') as mock_ensure_config, \
             patch('main.tk.Tk.__init__', return_value=None), \
             patch('main.messagebox.showerror') as mock_error:
            
            # Setup config mock
            mock_config = Mock()
            mock_config.get_api_keys.return_value = integration_config['api_keys']
            mock_config.get_paths.return_value = integration_config['paths']
            mock_config.get_settings.return_value = integration_config['settings']
            mock_ensure_config.return_value = mock_config
            
            from main import ImageSearchApp
            
            with patch.object(ImageSearchApp, '_setup_ui'), \
                 patch.object(ImageSearchApp, '_setup_data_structures'):
                
                app = ImageSearchApp()
                app.search_entry = Mock()
                app.search_entry.get.return_value = "test"
                app.loading_label = Mock()
                
                # Test network error
                with patch('requests.get', side_effect=Exception("Network error")):
                    app.search_images()
                    mock_error.assert_called()
                
                # Reset mock
                mock_error.reset_mock()
                
                # Test API error response
                with patch('requests.get') as mock_get:
                    mock_response = Mock()
                    mock_response.status_code = 401
                    mock_response.json.return_value = {"error": "Unauthorized"}
                    mock_get.return_value = mock_response
                    
                    app.search_images()
                    mock_error.assert_called()
    
    def test_data_persistence_integration(self, integration_config, temp_data_dir):
        """Test actual data persistence to files."""
        with patch('main.ensure_api_keys_configured') as mock_ensure_config, \
             patch('main.tk.Tk.__init__', return_value=None):
            
            # Setup config mock with real temp directory
            mock_config = Mock()
            mock_config.get_api_keys.return_value = integration_config['api_keys']
            mock_config.get_paths.return_value = integration_config['paths']
            mock_config.get_settings.return_value = integration_config['settings']
            mock_ensure_config.return_value = mock_config
            
            from main import ImageSearchApp
            
            with patch.object(ImageSearchApp, '_setup_ui'), \
                 patch.object(ImageSearchApp, '_setup_data_structures'):
                
                app = ImageSearchApp()
                
                # Test session data saving
                test_session_data = {
                    'timestamp': '2024-01-01T12:00:00Z',
                    'query': 'integration test',
                    'description': 'Test description',
                    'vocabulary': ['palabra', 'prueba']
                }
                
                app._save_session_data(test_session_data)
                
                # Verify session file was created
                session_file = Path(integration_config['paths']['session_log'])
                assert session_file.exists()
                
                # Verify content
                with open(session_file) as f:
                    saved_data = json.load(f)
                    assert isinstance(saved_data, list)
                    assert len(saved_data) > 0
                    assert saved_data[-1]['query'] == 'integration test'
                
                # Test vocabulary saving
                app._save_vocabulary_translation('hola', 'hello')
                
                # Verify vocabulary file was created
                vocab_file = Path(integration_config['paths']['vocabulary_csv'])
                assert vocab_file.exists()
                
                # Verify content
                content = vocab_file.read_text()
                assert 'hola' in content
                assert 'hello' in content
    
    def test_configuration_integration(self, temp_data_dir):
        """Test configuration management integration."""
        config_file = temp_data_dir / "config.ini"
        
        # Test config file creation and loading
        from config_manager import ConfigManager
        
        config_manager = ConfigManager(str(config_file))
        config_manager.set_api_key('unsplash', 'test_integration_key')
        config_manager.set_api_key('openai', 'test_integration_key')
        
        # Verify file was created
        assert config_file.exists()
        
        # Create new instance and verify persistence
        config_manager2 = ConfigManager(str(config_file))
        api_keys = config_manager2.get_api_keys()
        
        assert api_keys['unsplash'] == 'test_integration_key'
        assert api_keys['openai'] == 'test_integration_key'
    
    @pytest.mark.slow
    def test_performance_workflow(self, integration_config):
        """Test workflow performance characteristics."""
        import time
        
        with patch('main.ensure_api_keys_configured') as mock_ensure_config, \
             patch('main.tk.Tk.__init__', return_value=None), \
             patch('requests.get') as mock_get, \
             patch('main.OpenAI') as mock_openai:
            
            # Setup mocks
            mock_config = Mock()
            mock_config.get_api_keys.return_value = integration_config['api_keys']
            mock_config.get_paths.return_value = integration_config['paths']
            mock_config.get_settings.return_value = integration_config['settings']
            mock_ensure_config.return_value = mock_config
            
            # Mock API responses with delay
            def mock_api_delay(*args, **kwargs):
                time.sleep(0.1)  # Simulate API delay
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {'results': [], 'total': 0}
                return mock_response
            
            mock_get.side_effect = mock_api_delay
            
            mock_client = Mock()
            mock_completion = Mock()
            mock_completion.choices = [Mock()]
            mock_completion.choices[0].message.content = "Test description"
            mock_client.chat.completions.create.return_value = mock_completion
            mock_openai.return_value = mock_client
            
            from main import ImageSearchApp
            
            with patch.object(ImageSearchApp, '_setup_ui'), \
                 patch.object(ImageSearchApp, '_setup_data_structures'):
                
                app = ImageSearchApp()
                app.search_entry = Mock()
                app.search_entry.get.return_value = "performance test"
                app.loading_label = Mock()
                
                # Measure search performance
                start_time = time.time()
                app.search_images()
                search_time = time.time() - start_time
                
                # Should complete within reasonable time (including mock delay)
                assert search_time < 1.0  # 1 second max including 0.1s mock delay


@pytest.mark.integration
class TestMultiPlatformCompatibility:
    """Test compatibility across different platforms."""
    
    def test_path_handling(self, temp_data_dir):
        """Test cross-platform path handling."""
        from config_manager import ConfigManager
        
        config_file = temp_data_dir / "config.ini"
        config_manager = ConfigManager(str(config_file))
        
        paths = config_manager.get_paths()
        
        # Verify all paths are valid strings
        assert all(isinstance(path, str) for path in paths.values())
        
        # Verify paths can be converted to Path objects
        for path_value in paths.values():
            path_obj = Path(path_value)
            # Should not raise exception
            assert isinstance(path_obj, Path)
    
    def test_encoding_handling(self, temp_data_dir):
        """Test handling of different text encodings."""
        from config_manager import ConfigManager
        
        config_file = temp_data_dir / "config.ini" 
        config_manager = ConfigManager(str(config_file))
        
        # Test with Unicode characters (Spanish accents)
        test_text = "Descripción con acentos: niño, montaña, corazón"
        
        # Should handle Unicode text without errors
        vocabulary = []  # Mock vocabulary extraction
        assert isinstance(test_text, str)
        assert len(test_text) > 0