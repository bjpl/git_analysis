"""
Tests for main application functionality.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import tkinter as tk
import json
from pathlib import Path

# Skip tests if main module is not available
try:
    # We'll mock the imports that might not be available in test environment
    with patch.dict('sys.modules', {
        'tkinter': Mock(),
        'PIL': Mock(),
        'openai': Mock(),
        'requests': Mock()
    }):
        from main import ImageSearchApp
except ImportError:
    pytest.skip("main module not available", allow_module_level=True)


@pytest.mark.unit
class TestImageSearchAppInitialization:
    """Test ImageSearchApp initialization."""
    
    @patch('main.ensure_api_keys_configured')
    @patch('main.tk.Tk.__init__')
    def test_should_initialize_with_valid_config(self, mock_tk_init, mock_ensure_config, mock_config_manager):
        """Test app initialization with valid configuration."""
        mock_tk_init.return_value = None
        mock_ensure_config.return_value = mock_config_manager
        
        # Mock the GUI components
        with patch.object(ImageSearchApp, '_setup_ui'), \
             patch.object(ImageSearchApp, '_setup_data_structures'):
            
            app = ImageSearchApp()
            
            assert app.config_manager == mock_config_manager
            assert hasattr(app, 'UNSPLASH_ACCESS_KEY')
            assert hasattr(app, 'OPENAI_API_KEY')
    
    @patch('main.ensure_api_keys_configured')
    @patch('main.tk.Tk.__init__')
    def test_should_handle_config_failure(self, mock_tk_init, mock_ensure_config):
        """Test app handling configuration failure."""
        mock_tk_init.return_value = None
        mock_ensure_config.return_value = None  # Configuration failed
        
        with patch.object(ImageSearchApp, 'destroy') as mock_destroy:
            app = ImageSearchApp()
            mock_destroy.assert_called_once()


@pytest.mark.unit
class TestImageSearchFunctionality:
    """Test image search functionality."""
    
    def create_mock_app(self, mock_config_manager):
        """Create a mock app for testing."""
        with patch('main.ensure_api_keys_configured', return_value=mock_config_manager), \
             patch('main.tk.Tk.__init__', return_value=None), \
             patch.object(ImageSearchApp, '_setup_ui'), \
             patch.object(ImageSearchApp, '_setup_data_structures'):
            
            app = ImageSearchApp()
            app.search_entry = Mock()
            app.search_entry.get.return_value = "test query"
            app.image_label = Mock()
            app.loading_label = Mock()
            app.prev_button = Mock()
            app.next_button = Mock()
            
            return app
    
    @patch('main.requests.get')
    def test_should_search_images_successfully(self, mock_get, mock_config_manager, mock_api_response):
        """Test successful image search."""
        app = self.create_mock_app(mock_config_manager)
        
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_api_response
        mock_get.return_value = mock_response
        
        # Execute search
        app.search_images()
        
        # Verify API call was made
        mock_get.assert_called()
        call_args = mock_get.call_args
        assert 'unsplash.com' in str(call_args)
    
    @patch('main.requests.get')
    def test_should_handle_api_errors(self, mock_get, mock_config_manager):
        """Test handling API errors."""
        app = self.create_mock_app(mock_config_manager)
        
        # Mock API error
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": "Unauthorized"}
        mock_get.return_value = mock_response
        
        with patch('main.messagebox.showerror') as mock_error:
            app.search_images()
            mock_error.assert_called()
    
    @patch('main.requests.get')
    def test_should_handle_network_errors(self, mock_get, mock_config_manager):
        """Test handling network errors."""
        app = self.create_mock_app(mock_config_manager)
        
        # Mock network error
        mock_get.side_effect = Exception("Network error")
        
        with patch('main.messagebox.showerror') as mock_error:
            app.search_images()
            mock_error.assert_called()


@pytest.mark.unit
class TestGPTDescriptionGeneration:
    """Test GPT description generation functionality."""
    
    def create_mock_app_with_image(self, mock_config_manager):
        """Create a mock app with image data for testing."""
        with patch('main.ensure_api_keys_configured', return_value=mock_config_manager), \
             patch('main.tk.Tk.__init__', return_value=None), \
             patch.object(ImageSearchApp, '_setup_ui'), \
             patch.object(ImageSearchApp, '_setup_data_structures'):
            
            app = ImageSearchApp()
            app.current_images = [{'urls': {'regular': 'https://example.com/image.jpg'}}]
            app.current_image_index = 0
            app.notes_text = Mock()
            app.notes_text.get.return_value = "Test notes"
            app.description_text = Mock()
            app.vocab_frame = Mock()
            
            return app
    
    def test_should_generate_description_successfully(self, mock_config_manager, mock_openai_client):
        """Test successful description generation."""
        app = self.create_mock_app_with_image(mock_config_manager)
        
        with patch('main.OpenAI', return_value=mock_openai_client):
            app.generate_description()
            
            # Verify OpenAI API was called
            mock_openai_client.chat.completions.create.assert_called()
            
            # Verify description was set
            app.description_text.delete.assert_called()
            app.description_text.insert.assert_called()
    
    def test_should_handle_openai_errors(self, mock_config_manager):
        """Test handling OpenAI API errors."""
        app = self.create_mock_app_with_image(mock_config_manager)
        
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        with patch('main.OpenAI', return_value=mock_client), \
             patch('main.messagebox.showerror') as mock_error:
            
            app.generate_description()
            mock_error.assert_called()
    
    def test_should_extract_vocabulary_from_description(self, mock_config_manager):
        """Test vocabulary extraction from generated description."""
        app = self.create_mock_app_with_image(mock_config_manager)
        
        # Mock description with Spanish text
        test_description = "El gato negro está durmiendo en la casa grande."
        
        with patch.object(app, '_extract_vocabulary') as mock_extract:
            mock_extract.return_value = ["el gato", "negro", "está durmiendo", "la casa", "grande"]
            
            app._process_gpt_response(test_description)
            
            mock_extract.assert_called_with(test_description)


@pytest.mark.unit
class TestVocabularyExtraction:
    """Test vocabulary extraction functionality."""
    
    def create_mock_app(self, mock_config_manager):
        """Create a mock app for testing."""
        with patch('main.ensure_api_keys_configured', return_value=mock_config_manager), \
             patch('main.tk.Tk.__init__', return_value=None), \
             patch.object(ImageSearchApp, '_setup_ui'), \
             patch.object(ImageSearchApp, '_setup_data_structures'):
            
            return ImageSearchApp()
    
    def test_should_extract_spanish_vocabulary(self, mock_config_manager):
        """Test extraction of Spanish vocabulary."""
        app = self.create_mock_app(mock_config_manager)
        
        test_text = "El perro grande corre rápidamente por el parque verde."
        vocabulary = app._extract_vocabulary(test_text)
        
        assert isinstance(vocabulary, list)
        assert len(vocabulary) > 0
    
    def test_should_handle_empty_text(self, mock_config_manager):
        """Test handling empty text for vocabulary extraction."""
        app = self.create_mock_app(mock_config_manager)
        
        vocabulary = app._extract_vocabulary("")
        
        assert isinstance(vocabulary, list)
        assert len(vocabulary) == 0
    
    def test_should_remove_duplicates(self, mock_config_manager):
        """Test removal of duplicate vocabulary items."""
        app = self.create_mock_app(mock_config_manager)
        
        test_text = "El gato, el gato negro, el gato grande."
        vocabulary = app._extract_vocabulary(test_text)
        
        # Should not have duplicates
        assert len(vocabulary) == len(set(vocabulary))


@pytest.mark.unit  
class TestDataPersistence:
    """Test data persistence functionality."""
    
    def create_mock_app(self, mock_config_manager, temp_data_dir):
        """Create a mock app with temporary data directory."""
        # Update mock to return temp directory paths
        mock_config_manager.get_paths.return_value = {
            'session_log': str(temp_data_dir / 'session_log.json'),
            'vocabulary_csv': str(temp_data_dir / 'vocabulary.csv'),
            'data_dir': str(temp_data_dir)
        }
        
        with patch('main.ensure_api_keys_configured', return_value=mock_config_manager), \
             patch('main.tk.Tk.__init__', return_value=None), \
             patch.object(ImageSearchApp, '_setup_ui'), \
             patch.object(ImageSearchApp, '_setup_data_structures'):
            
            return ImageSearchApp()
    
    def test_should_save_session_data(self, mock_config_manager, temp_data_dir):
        """Test saving session data to JSON file."""
        app = self.create_mock_app(mock_config_manager, temp_data_dir)
        
        test_data = {
            'query': 'test',
            'description': 'Test description',
            'vocabulary': ['word1', 'word2']
        }
        
        app._save_session_data(test_data)
        
        # Check if file was created
        session_file = temp_data_dir / 'session_log.json'
        assert session_file.exists()
        
        # Check content
        with open(session_file) as f:
            saved_data = json.load(f)
            assert isinstance(saved_data, list)
            assert len(saved_data) > 0
    
    def test_should_save_vocabulary_to_csv(self, mock_config_manager, temp_data_dir):
        """Test saving vocabulary to CSV file."""
        app = self.create_mock_app(mock_config_manager, temp_data_dir)
        
        app._save_vocabulary_translation('hola', 'hello')
        
        # Check if file was created
        vocab_file = temp_data_dir / 'vocabulary.csv'
        assert vocab_file.exists()
        
        # Check content
        content = vocab_file.read_text()
        assert 'hola' in content
        assert 'hello' in content


@pytest.mark.integration
class TestFullWorkflow:
    """Integration tests for complete workflow."""
    
    @patch('main.requests.get')
    @patch('main.OpenAI')
    def test_complete_search_and_describe_workflow(self, mock_openai, mock_get, 
                                                 mock_config_manager, mock_api_response, 
                                                 mock_openai_client, temp_data_dir):
        """Test complete workflow from search to description."""
        # Setup mocks
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_api_response
        mock_get.return_value = mock_response
        mock_openai.return_value = mock_openai_client
        
        # Update config to use temp directory
        mock_config_manager.get_paths.return_value = {
            'session_log': str(temp_data_dir / 'session_log.json'),
            'vocabulary_csv': str(temp_data_dir / 'vocabulary.csv'),
            'data_dir': str(temp_data_dir)
        }
        
        with patch('main.ensure_api_keys_configured', return_value=mock_config_manager), \
             patch('main.tk.Tk.__init__', return_value=None), \
             patch.object(ImageSearchApp, '_setup_ui'), \
             patch.object(ImageSearchApp, '_setup_data_structures'):
            
            app = ImageSearchApp()
            app.search_entry = Mock()
            app.search_entry.get.return_value = "cats"
            app.notes_text = Mock()
            app.notes_text.get.return_value = "Test notes"
            app.description_text = Mock()
            app.image_label = Mock()
            app.loading_label = Mock()
            app.prev_button = Mock()
            app.next_button = Mock()
            app.vocab_frame = Mock()
            
            # Execute workflow
            app.search_images()
            app.generate_description()
            
            # Verify calls were made
            mock_get.assert_called()
            mock_openai_client.chat.completions.create.assert_called()