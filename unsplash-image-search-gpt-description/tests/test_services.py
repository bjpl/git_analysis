"""
Test suite for the service layer.
Tests all service classes for proper functionality.
"""

import asyncio
import pytest
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path
import tempfile
import json

from src.services import (
    BaseService,
    ServiceError,
    UnsplashClient,
    OpenAIClient,
    TranslationService,
)
from src.services.openai_service import ImageAnalysisRequest, TextRequest, TokenUsage
from src.services.translation_service import TranslationRequest
from src.services.service_manager import ServiceManager, ServiceConfig


class TestBaseService:
    """Test the base service class."""
    
    class MockService(BaseService):
        """Mock service for testing."""
        def _get_auth_headers(self):
            return {'Authorization': f'Bearer {self.api_key}'}
    
    @pytest.fixture
    async def service(self):
        """Create mock service instance."""
        service = self.MockService(
            name="test",
            base_url="https://api.test.com",
            api_key="test-key",
        )
        yield service
        await service.close()
    
    @pytest.mark.asyncio
    async def test_initialization(self, service):
        """Test service initialization."""
        assert service.name == "test"
        assert service.base_url == "https://api.test.com"
        assert service.api_key == "test-key"
        assert service.enable_caching is True
    
    @pytest.mark.asyncio
    async def test_cache_key_generation(self, service):
        """Test cache key generation."""
        key1 = service._get_cache_key("GET", "/test")
        key2 = service._get_cache_key("GET", "/test", {"param": "value"})
        key3 = service._get_cache_key("POST", "/test")
        
        assert key1 != key2
        assert key1 != key3
        assert isinstance(key1, str)
    
    @pytest.mark.asyncio
    async def test_circuit_breaker(self, service):
        """Test circuit breaker functionality."""
        # Initially should allow requests
        assert service._can_execute() is True
        
        # Simulate failures
        for _ in range(5):  # Default threshold
            service._on_failure(Exception("test error"))
        
        # Should now be in open state
        assert service._can_execute() is False


class TestUnsplashClient:
    """Test the Unsplash client."""
    
    @pytest.fixture
    def client(self):
        """Create Unsplash client instance."""
        return UnsplashClient(
            access_key="test-access-key",
            requests_per_hour=5,  # Low limit for testing
        )
    
    def test_initialization(self, client):
        """Test client initialization."""
        assert client.name == "unsplash"
        assert client.api_key == "test-access-key"
        assert client.requests_per_hour == 5
        assert client._demo_account is True
    
    def test_rate_limit_check(self, client):
        """Test rate limiting."""
        # Should pass initially
        client._check_rate_limit()
        
        # Add requests up to limit
        for _ in range(4):
            client._check_rate_limit()
        
        # Should raise error on exceeding limit
        with pytest.raises(Exception):  # RateLimitError
            client._check_rate_limit()
    
    @pytest.mark.asyncio
    async def test_parse_image_metadata(self, client):
        """Test image metadata parsing."""
        sample_data = {
            'id': 'test-id',
            'description': 'Test image',
            'alt_description': 'Alt description',
            'urls': {'regular': 'https://example.com/image.jpg'},
            'width': 1920,
            'height': 1080,
            'user': {
                'name': 'Test User',
                'links': {'html': 'https://example.com/user'}
            },
            'links': {'download': 'https://example.com/download'},
            'tags': [{'title': 'nature'}, {'title': 'landscape'}],
            'color': '#ffffff',
            'created_at': '2024-01-01T00:00:00Z',
            'likes': 100
        }
        
        metadata = client._parse_image_metadata(sample_data)
        
        assert metadata.id == 'test-id'
        assert metadata.description == 'Test image'
        assert metadata.width == 1920
        assert metadata.height == 1080
        assert metadata.photographer == 'Test User'
        assert len(metadata.tags) == 2
        assert metadata.likes == 100


class TestOpenAIClient:
    """Test the OpenAI client."""
    
    @pytest.fixture
    def client(self):
        """Create OpenAI client instance."""
        with patch('src.services.openai_service.AsyncOpenAI'):
            return OpenAIClient(
                api_key="test-api-key",
                default_model="gpt-4-vision-preview",
            )
    
    def test_initialization(self, client):
        """Test client initialization."""
        assert client.name == "openai"
        assert client.api_key == "test-api-key"
        assert client.default_model == "gpt-4-vision-preview"
        assert client.total_tokens_used == 0
        assert client.total_cost == 0.0
    
    def test_token_usage_creation(self, client):
        """Test token usage object creation."""
        usage_data = {
            'prompt_tokens': 100,
            'completion_tokens': 50,
            'total_tokens': 150
        }
        
        usage = client._create_token_usage(usage_data)
        
        assert usage.prompt_tokens == 100
        assert usage.completion_tokens == 50
        assert usage.total_tokens == 150
        assert usage.input_tokens == 100
        assert usage.output_tokens == 50
    
    def test_cost_calculation(self, client):
        """Test cost calculation."""
        token_usage = TokenUsage(
            prompt_tokens=1000,
            completion_tokens=500,
            total_tokens=1500
        )
        
        cost = client._calculate_cost("gpt-4-vision-preview", token_usage)
        
        assert cost.input_cost == 0.01  # 1000/1000 * 0.01
        assert cost.output_cost == 0.015  # 500/1000 * 0.03
        assert cost.total_cost == 0.025
        assert cost.currency == 'USD'
    
    def test_usage_statistics(self, client):
        """Test usage statistics tracking."""
        # Simulate some usage
        client.total_tokens_used = 1500
        client.total_cost = 0.025
        client.requests_made = 2
        
        stats = client.get_usage_statistics()
        
        assert stats['total_tokens_used'] == 1500
        assert stats['total_cost'] == 0.025
        assert stats['requests_made'] == 2
        assert stats['average_tokens_per_request'] == 750
        assert stats['average_cost_per_request'] == 0.0125


class TestTranslationService:
    """Test the translation service."""
    
    @pytest.fixture
    def mock_openai_client(self):
        """Create mock OpenAI client."""
        client = Mock(spec=OpenAIClient)
        client.process_text = AsyncMock()
        return client
    
    @pytest.fixture
    async def service(self, mock_openai_client):
        """Create translation service instance."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_file = Path(temp_dir) / "test_cache.json"
            service = TranslationService(
                openai_client=mock_openai_client,
                cache_file=cache_file,
            )
            yield service
            await service.close()
    
    def test_initialization(self, service):
        """Test service initialization."""
        assert service.name == "translation"
        assert service.default_model == "gpt-4-turbo"
        assert service.cache is not None
    
    def test_should_skip_translation(self, service):
        """Test translation skipping logic."""
        # Should skip common words
        assert service._should_skip_translation("el", "Spanish") is True
        assert service._should_skip_translation("the", "English") is True
        assert service._should_skip_translation("a", "Spanish") is True
        
        # Should not skip meaningful words
        assert service._should_skip_translation("casa", "Spanish") is False
        assert service._should_skip_translation("beautiful", "English") is False
    
    def test_confidence_estimation(self, service):
        """Test translation confidence estimation."""
        request = TranslationRequest(
            text="casa",
            context="La casa es grande",
            category="noun"
        )
        
        # Good translation
        confidence = service._estimate_confidence(request, "house")
        assert confidence > 0.8
        
        # Bad translation (same as original)
        confidence = service._estimate_confidence(request, "casa")
        assert confidence < 0.5
    
    def test_clean_translation(self, service):
        """Test translation cleaning."""
        # Remove quotes
        assert service._clean_translation('"house"') == 'house'
        
        # Remove prefixes
        assert service._clean_translation('Translation: house') == 'house'
        
        # Remove extra whitespace
        assert service._clean_translation('  house  ') == 'house'
    
    @pytest.mark.asyncio
    async def test_translate_with_cache(self, service, mock_openai_client):
        """Test translation with caching."""
        request = TranslationRequest(text="casa")
        
        # Mock OpenAI response
        mock_result = Mock()
        mock_result.content = "house"
        mock_openai_client.process_text.return_value = mock_result
        
        # First call should hit OpenAI
        result1 = await service.translate(request)
        assert result1.translated == "house"
        assert result1.from_cache is False
        
        # Second call should use cache
        result2 = await service.translate(request)
        assert result2.translated == "house"
        assert result2.from_cache is True
        
        # Should only call OpenAI once
        assert mock_openai_client.process_text.call_count == 1


class TestServiceManager:
    """Test the service manager."""
    
    @pytest.fixture
    def config(self):
        """Create service configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield ServiceConfig(
                unsplash_access_key="test-unsplash-key",
                openai_api_key="test-openai-key",
                data_dir=Path(temp_dir),
            )
    
    @pytest.fixture
    async def manager(self, config):
        """Create service manager instance."""
        with patch('src.services.service_manager.UnsplashClient'), \
             patch('src.services.service_manager.OpenAIClient'), \
             patch('src.services.service_manager.TranslationService'):
            
            manager = ServiceManager(config)
            yield manager
            await manager.stop_services()
    
    def test_initialization(self, manager, config):
        """Test manager initialization."""
        assert manager.config == config
        assert manager._initialized is False
        assert manager._services_started is False
    
    @pytest.mark.asyncio
    async def test_service_lifecycle(self, manager):
        """Test service lifecycle management."""
        # Initialize services
        await manager.initialize()
        assert manager._initialized is True
        assert manager.unsplash is not None
        assert manager.openai is not None
        assert manager.translation is not None
        
        # Start services
        await manager.start_services()
        assert manager._services_started is True
        
        # Stop services
        await manager.stop_services()
        assert manager._services_started is False
    
    @pytest.mark.asyncio
    async def test_context_manager(self, manager):
        """Test async context manager."""
        async with manager as mgr:
            assert mgr._services_started is True
        
        assert manager._services_started is False


if __name__ == "__main__":
    # Run basic tests
    pytest.main([__file__, "-v"])