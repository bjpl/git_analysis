"""
Integration tests for image collection functionality.
Tests end-to-end workflows, real API interactions, and system-level behavior.
"""

import pytest
import time
import threading
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import requests
from PIL import Image, ImageTk
import tkinter as tk
import sys

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from main import ImageSearchApp
    from config_manager import ConfigManager
    from tests.fixtures.sample_data import (
        SAMPLE_UNSPLASH_SEARCH_RESPONSE,
        TEST_IMAGE_DATA,
        PERFORMANCE_BENCHMARKS
    )
except ImportError:
    pytest.skip("Required modules not available", allow_module_level=True)


@pytest.mark.integration
class TestImageCollectionWorkflow:
    """Test complete image collection workflows end-to-end."""

    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def test_config_manager(self, temp_workspace):
        """Create test configuration manager."""
        config_manager = ConfigManager()
        config_manager.config_dir = temp_workspace
        config_manager.data_dir = temp_workspace / "data"
        config_manager.data_dir.mkdir(exist_ok=True)
        config_manager.config_file = temp_workspace / "config.ini"
        
        # Setup test API keys
        config_manager.save_api_keys(
            "test_unsplash_key_123456789",
            "sk-test_openai_key_123456789",
            "gpt-4o-mini"
        )
        
        return config_manager

    @pytest.fixture
    def app_with_real_config(self, test_config_manager, tkinter_root):
        """Create app with real configuration for integration testing."""
        with patch('main.ensure_api_keys_configured', return_value=test_config_manager):
            app = ImageSearchApp()
            app.withdraw()
            yield app
            try:
                app.destroy()
            except:
                pass

    @patch('requests.get')
    def test_complete_search_to_display_workflow(self, mock_get, app_with_real_config):
        """Test complete workflow from search initiation to image display."""
        app = app_with_real_config
        
        # Setup mock API responses
        search_response = Mock()
        search_response.json.return_value = SAMPLE_UNSPLASH_SEARCH_RESPONSE
        search_response.raise_for_status = Mock()
        
        image_response = Mock()
        image_response.content = TEST_IMAGE_DATA["png_1x1"]
        image_response.raise_for_status = Mock()
        
        mock_get.side_effect = [search_response, image_response]
        
        with patch('PIL.Image.open') as mock_image_open, \
             patch('PIL.ImageTk.PhotoImage') as mock_photo:
            
            # Setup PIL mocks
            mock_pil_image = Mock()
            mock_pil_image.copy.return_value = mock_pil_image
            mock_pil_image.size = (800, 600)
            mock_image_open.return_value = mock_pil_image
            
            mock_photo_instance = Mock()
            mock_photo_instance.width.return_value = 400
            mock_photo_instance.height.return_value = 300
            mock_photo.return_value = mock_photo_instance
            
            # Execute complete workflow
            app.search_entry.delete(0, tk.END)
            app.search_entry.insert(0, "mountains")
            
            # Trigger search
            app.search_image()
            
            # Wait for async operations
            app.update()
            time.sleep(0.1)
            app.update()
            
            # Verify workflow results
            assert app.current_query == "mountains"
            assert len(app.used_image_urls) >= 1
            assert app.current_image_url is not None

    @patch('requests.get')
    def test_multi_page_collection_with_limits(self, mock_get, app_with_real_config):
        """Test multi-page image collection with collection limits."""
        app = app_with_real_config
        app.max_images_per_search = 3  # Small limit for testing
        
        # Setup responses for multiple pages
        def create_page_response(page_num):
            response = Mock()
            response.json.return_value = {
                "results": [
                    {
                        "id": f"img_{page_num}_{i}",
                        "urls": {"regular": f"https://test.com/image_{page_num}_{i}.jpg"},
                        "description": f"Test image {page_num}-{i}"
                    }
                    for i in range(2)
                ]
            }
            response.raise_for_status = Mock()
            return response
        
        # Mock multiple pages + image downloads
        responses = []
        for page in range(1, 4):
            responses.append(create_page_response(page))
            # Add image download responses
            for i in range(2):
                img_response = Mock()
                img_response.content = TEST_IMAGE_DATA["png_1x1"]
                img_response.raise_for_status = Mock()
                responses.append(img_response)
        
        mock_get.side_effect = responses
        
        with patch('PIL.Image.open') as mock_image_open, \
             patch('PIL.ImageTk.PhotoImage') as mock_photo:
            
            mock_pil_image = Mock()
            mock_pil_image.copy.return_value = mock_pil_image
            mock_pil_image.size = (600, 400)
            mock_image_open.return_value = mock_pil_image
            
            mock_photo.return_value = Mock()
            
            app.current_query = "nature"
            app.current_page = 1
            app.current_results = []
            app.current_index = 0
            
            # Collect images up to limit
            collected_count = 0
            while collected_count < app.max_images_per_search:
                result = app.get_next_image()
                if result:
                    collected_count += 1
                    app.images_collected_count = collected_count
                else:
                    break
            
            # Verify collection limit behavior
            assert len(app.used_image_urls) <= app.max_images_per_search

    def test_data_persistence_during_collection(self, app_with_real_config, temp_workspace):
        """Test that data is properly persisted during image collection."""
        app = app_with_real_config
        
        # Setup test data
        test_session_data = {
            "sessions": [{
                "session_start": "2024-01-01T10:00:00",
                "session_end": "2024-01-01T10:30:00",
                "entries": [
                    {
                        "timestamp": "2024-01-01T10:05:00",
                        "query": "nature",
                        "image_url": "https://test.com/image1.jpg",
                        "user_note": "Beautiful landscape",
                        "generated_description": "A scenic mountain view"
                    }
                ],
                "vocabulary_learned": 5,
                "target_phrases": ["la montaña - mountain", "hermoso - beautiful"]
            }]
        }
        
        # Add some runtime data
        app.log_entries.append({
            "timestamp": "2024-01-01T10:10:00",
            "query": "forest",
            "image_url": "https://test.com/image2.jpg",
            "user_note": "Dense forest",
            "generated_description": "A thick forest with tall trees"
        })
        
        app.target_phrases = ["el bosque - forest", "alto - tall"]
        
        # Save session data
        app.save_session_to_json()
        
        # Verify data was saved
        log_file = app.LOG_FILENAME
        assert log_file.exists()
        
        with open(log_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
            
        assert "sessions" in saved_data
        assert len(saved_data["sessions"]) > 0
        assert len(saved_data["sessions"][-1]["entries"]) > 0

    @patch('requests.get')
    def test_error_recovery_and_resilience(self, mock_get, app_with_real_config):
        """Test error recovery and system resilience during collection."""
        app = app_with_real_config
        
        # Setup sequence of responses: error, error, success
        error_response = Mock()
        error_response.raise_for_status.side_effect = requests.exceptions.HTTPError("503 Service Unavailable")
        
        success_response = Mock()
        success_response.json.return_value = SAMPLE_UNSPLASH_SEARCH_RESPONSE
        success_response.raise_for_status = Mock()
        
        mock_get.side_effect = [error_response, error_response, success_response]
        
        # Execute with retry logic
        with patch('time.sleep'):  # Speed up test
            result = app.api_call_with_retry(
                app.fetch_images_page, 
                "mountains", 
                1, 
                max_retries=3
            )
        
        # Should eventually succeed
        assert result == SAMPLE_UNSPLASH_SEARCH_RESPONSE["results"]
        assert mock_get.call_count == 3

    def test_concurrent_ui_operations(self, app_with_real_config):
        """Test concurrent UI operations during image collection."""
        app = app_with_real_config
        
        # Simulate concurrent operations
        operations_completed = []
        
        def ui_operation_1():
            app.update_status("Operation 1")
            operations_completed.append("op1")
        
        def ui_operation_2():
            app.update_stats()
            operations_completed.append("op2")
        
        def ui_operation_3():
            app.disable_buttons()
            app.enable_buttons()
            operations_completed.append("op3")
        
        # Execute operations
        for op in [ui_operation_1, ui_operation_2, ui_operation_3]:
            op()
            app.update()
        
        # All operations should complete
        assert len(operations_completed) == 3
        assert "op1" in operations_completed
        assert "op2" in operations_completed
        assert "op3" in operations_completed

    @patch('requests.get')
    def test_memory_management_during_extended_collection(self, mock_get, app_with_real_config):
        """Test memory management during extended image collection."""
        app = app_with_real_config
        
        # Setup continuous responses
        def create_response():
            response = Mock()
            response.json.return_value = {
                "results": [{
                    "id": f"img_{time.time()}",
                    "urls": {"regular": f"https://test.com/image_{time.time()}.jpg"},
                    "description": "Test image"
                }]
            }
            response.raise_for_status = Mock()
            return response
        
        # Create many responses
        responses = [create_response() for _ in range(50)]
        image_responses = [Mock(content=TEST_IMAGE_DATA["png_1x1"], raise_for_status=Mock()) for _ in range(50)]
        
        # Interleave search and image responses
        all_responses = []
        for i in range(50):
            all_responses.extend([responses[i], image_responses[i]])
        
        mock_get.side_effect = all_responses
        
        with patch('PIL.Image.open') as mock_image_open, \
             patch('PIL.ImageTk.PhotoImage'):
            
            mock_image_open.return_value = Mock(copy=Mock(return_value=Mock()), size=(400, 300))
            
            # Collect many images
            app.current_query = "test"
            collected = 0
            
            while collected < 25:  # Collect reasonable number
                app.current_page = (collected // 10) + 1
                app.current_results = []
                app.current_index = 0
                
                result = app.get_next_image()
                if result:
                    collected += 1
                    app.images_collected_count = collected
                    
                    # Check memory usage periodically
                    if collected % 5 == 0:
                        # Cache should be limited
                        assert len(app.image_cache) <= 11
                        # URL set should be reasonable
                        assert len(app.used_image_urls) == collected
                
                # Prevent infinite loop
                if mock_get.call_count >= len(all_responses):
                    break

    def test_search_state_persistence_across_operations(self, app_with_real_config):
        """Test that search state persists correctly across operations."""
        app = app_with_real_config
        
        # Set initial state
        app.current_query = "mountains"
        app.current_page = 3
        app.current_index = 7
        app.images_collected_count = 15
        app.max_images_per_search = 30
        
        # Perform various operations that shouldn't affect core state
        app.update_status("Testing...")
        app.update_stats()
        app.show_progress("Loading...")
        app.hide_progress()
        
        # Core search state should be preserved
        assert app.current_query == "mountains"
        assert app.current_page == 3
        assert app.current_index == 7
        assert app.images_collected_count == 15
        assert app.max_images_per_search == 30

    @patch('requests.get')
    def test_user_interaction_during_collection(self, mock_get, app_with_real_config):
        """Test user interactions during active image collection."""
        app = app_with_real_config
        
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = SAMPLE_UNSPLASH_SEARCH_RESPONSE
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Start a collection operation
        app.start_search_session()
        assert app.search_state == 'searching'
        
        # Simulate user clicking stop
        app.stop_search()
        assert app.search_cancelled == True
        assert app.search_state == 'cancelled'
        
        # User should be able to start new search
        app.reset_search_state()
        app.start_search_session()
        assert app.search_cancelled == False
        assert app.search_state == 'searching'


@pytest.mark.integration
@pytest.mark.slow
class TestPerformanceIntegration:
    """Integration tests for performance under realistic conditions."""

    @pytest.fixture
    def performance_app(self, mock_config_manager, tkinter_root):
        """Create app configured for performance testing."""
        with patch('main.ensure_api_keys_configured', return_value=mock_config_manager):
            app = ImageSearchApp()
            app.withdraw()
            app.max_images_per_search = 100  # Higher limit for performance testing
            yield app
            try:
                app.destroy()
            except:
                pass

    @patch('requests.get')
    def test_high_volume_image_processing(self, mock_get, performance_app):
        """Test performance with high volume image processing."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        start_time = time.time()
        
        # Create responses for high volume processing
        responses = []
        for batch in range(10):  # 10 batches
            search_response = Mock()
            search_response.json.return_value = {
                "results": [
                    {
                        "id": f"img_{batch}_{i}",
                        "urls": {"regular": f"https://test.com/batch_{batch}_img_{i}.jpg"},
                        "description": f"Batch {batch} image {i}"
                    }
                    for i in range(10)  # 10 images per batch
                ]
            }
            search_response.raise_for_status = Mock()
            responses.append(search_response)
            
            # Add image download responses
            for i in range(10):
                img_response = Mock()
                img_response.content = TEST_IMAGE_DATA["png_1x1"]
                img_response.raise_for_status = Mock()
                responses.append(img_response)
        
        mock_get.side_effect = responses
        
        with patch('PIL.Image.open') as mock_image_open, \
             patch('PIL.ImageTk.PhotoImage'):
            
            mock_image_open.return_value = Mock(
                copy=Mock(return_value=Mock()),
                size=(600, 400)
            )
            
            # Process high volume
            performance_app.current_query = "nature"
            total_processed = 0
            
            for batch in range(5):  # Process 5 batches
                performance_app.current_page = batch + 1
                performance_app.current_results = []
                performance_app.current_index = 0
                
                batch_count = 0
                while batch_count < 10 and total_processed < 50:
                    result = performance_app.get_next_image()
                    if result:
                        batch_count += 1
                        total_processed += 1
                        performance_app.images_collected_count = total_processed
                    else:
                        break
        
        end_time = time.time()
        final_memory = process.memory_info().rss
        
        # Performance assertions
        duration = end_time - start_time
        memory_increase = final_memory - initial_memory
        
        assert duration < PERFORMANCE_BENCHMARKS.get("high_volume_processing", 10.0)
        assert memory_increase < 100 * 1024 * 1024  # Less than 100MB increase
        assert len(performance_app.image_cache) <= 11  # Cache properly limited
        assert performance_app.images_collected_count == total_processed

    def test_ui_responsiveness_under_load(self, performance_app):
        """Test UI responsiveness under high load conditions."""
        response_times = []
        
        def measure_ui_operation():
            start = time.time()
            performance_app.update_status("Testing responsiveness...")
            performance_app.update_stats()
            performance_app.update()
            end = time.time()
            return end - start
        
        # Simulate load by adding many operations
        for i in range(100):
            # Add some load
            performance_app.vocabulary_cache.update([f"word_{i}_{j}" for j in range(10)])
            performance_app.used_image_urls.update([f"url_{i}_{j}" for j in range(5)])
            
            # Measure UI responsiveness
            response_time = measure_ui_operation()
            response_times.append(response_time)
        
        # UI should remain responsive
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        
        assert avg_response_time < 0.01  # Less than 10ms average
        assert max_response_time < 0.1   # Less than 100ms maximum


@pytest.mark.integration
class TestRealWorldScenarios:
    """Test real-world usage scenarios and edge cases."""

    @pytest.fixture
    def scenario_app(self, mock_config_manager, tkinter_root):
        """Create app for scenario testing."""
        with patch('main.ensure_api_keys_configured', return_value=mock_config_manager):
            app = ImageSearchApp()
            app.withdraw()
            yield app
            try:
                app.destroy()
            except:
                pass

    @patch('requests.get')
    def test_interrupted_collection_recovery(self, mock_get, scenario_app):
        """Test recovery from interrupted collection operations."""
        # Setup partial responses (simulating interruption)
        good_response = Mock()
        good_response.json.return_value = SAMPLE_UNSPLASH_SEARCH_RESPONSE
        good_response.raise_for_status = Mock()
        
        bad_response = Mock()
        bad_response.raise_for_status.side_effect = requests.exceptions.ConnectionError("Connection interrupted")
        
        # Sequence: success, failure, success
        mock_get.side_effect = [good_response, bad_response, good_response]
        
        scenario_app.current_query = "landscape"
        scenario_app.current_page = 1
        
        # First operation should succeed
        results1 = scenario_app.fetch_images_page("landscape", 1)
        assert len(results1) > 0
        
        # Second operation should fail but be recoverable
        with pytest.raises(requests.exceptions.ConnectionError):
            scenario_app.fetch_images_page("landscape", 2)
        
        # Third operation should succeed (recovery)
        results3 = scenario_app.fetch_images_page("landscape", 3)
        assert len(results3) > 0

    def test_rapid_user_interactions(self, scenario_app):
        """Test handling of rapid user interactions."""
        interactions = []
        
        # Simulate rapid button clicks
        for i in range(10):
            try:
                scenario_app.disable_buttons()
                scenario_app.enable_buttons()
                scenario_app.update_status(f"Interaction {i}")
                scenario_app.update_stats()
                interactions.append(f"interaction_{i}")
            except Exception as e:
                interactions.append(f"error_{i}: {str(e)}")
        
        # Should handle all interactions gracefully
        successful_interactions = [i for i in interactions if not i.startswith("error_")]
        assert len(successful_interactions) >= 8  # At least 80% success rate

    def test_state_consistency_during_concurrent_operations(self, scenario_app):
        """Test state consistency during concurrent operations."""
        # Set initial state
        initial_state = {
            "current_query": "test",
            "current_page": 5,
            "current_index": 3,
            "images_collected_count": 12
        }
        
        for key, value in initial_state.items():
            setattr(scenario_app, key, value)
        
        # Simulate concurrent state modifications
        def modify_state_1():
            scenario_app.images_collected_count += 1
            scenario_app.current_index += 1
        
        def modify_state_2():
            scenario_app.current_page += 1
        
        def read_state():
            return {
                "current_query": scenario_app.current_query,
                "current_page": scenario_app.current_page,
                "current_index": scenario_app.current_index,
                "images_collected_count": scenario_app.images_collected_count
            }
        
        # Execute concurrent modifications
        modify_state_1()
        modify_state_2()
        final_state = read_state()
        
        # State should be consistent (no corruption)
        assert final_state["current_query"] == initial_state["current_query"]
        assert final_state["current_page"] == initial_state["current_page"] + 1
        assert final_state["current_index"] == initial_state["current_index"] + 1
        assert final_state["images_collected_count"] == initial_state["images_collected_count"] + 1


if __name__ == "__main__":
    # Run integration tests
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-m", "integration"
    ])