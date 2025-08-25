"""
Tests for Content Generation System
Tests OpenAI client, prompt templates, and content generator
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
import sys
import os

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai.content_generation.openai_client import OpenAIClient, GenerationRequest, GenerationResponse, TokenBucket
from ai.content_generation.prompt_templates import PromptTemplates, ContentType, UserLevel, DifficultyLevel
from ai.content_generation.content_generator import ContentGenerator


class TestTokenBucket:
    """Test token bucket rate limiting"""
    
    def test_token_bucket_initialization(self):
        """Test token bucket initialization"""
        bucket = TokenBucket(capacity=10, refill_rate=5)
        assert bucket.capacity == 10
        assert bucket.tokens == 10
        assert bucket.refill_rate == 5
    
    def test_token_consumption(self):
        """Test token consumption"""
        bucket = TokenBucket(capacity=10, refill_rate=5)
        
        # Should be able to consume tokens initially
        assert bucket.consume(3) == True
        assert bucket.tokens == 7
        
        # Should fail when not enough tokens
        assert bucket.consume(10) == False
        assert bucket.tokens == 7  # Unchanged
        
        # Should succeed with remaining tokens
        assert bucket.consume(7) == True
        assert bucket.tokens == 0
    
    def test_token_refill(self):
        """Test token refilling over time"""
        import time
        bucket = TokenBucket(capacity=10, refill_rate=10)  # 10 tokens per second
        
        # Consume all tokens
        bucket.consume(10)
        assert bucket.tokens == 0
        
        # Wait and check refill (simulated by calling _refill directly)
        bucket.last_refill -= 1  # Simulate 1 second passed
        bucket._refill()
        
        assert bucket.tokens > 0


class TestPromptTemplates:
    """Test prompt template system"""
    
    def setup_method(self):
        """Setup test environment"""
        self.templates = PromptTemplates()
    
    def test_template_loading(self):
        """Test that templates are loaded correctly"""
        vocab_templates = self.templates.get_all_templates_for_type(ContentType.VOCABULARY)
        assert len(vocab_templates) > 0
        assert 'word_explanation' in vocab_templates
        assert 'thematic_vocabulary' in vocab_templates
        
        grammar_templates = self.templates.get_all_templates_for_type(ContentType.GRAMMAR)
        assert len(grammar_templates) > 0
        assert 'concept_explanation' in grammar_templates
    
    def test_template_retrieval(self):
        """Test getting specific templates"""
        template = self.templates.get_template(ContentType.VOCABULARY, 'word_explanation')
        assert template is not None
        assert hasattr(template, 'template')
        assert hasattr(template, 'required_fields')
        assert 'word' in template.required_fields
        assert 'user_level' in template.required_fields
    
    def test_prompt_building(self):
        """Test building prompts from templates"""
        prompt = self.templates.build_prompt(
            ContentType.VOCABULARY,
            'word_explanation',
            word='casa',
            user_level='intermediate',
            difficulty_level='medium'
        )
        
        assert 'casa' in prompt
        assert 'intermediate' in prompt
        assert 'medium' in prompt
        assert len(prompt) > 100  # Should be substantial
    
    def test_missing_required_fields(self):
        """Test error handling for missing required fields"""
        with pytest.raises(ValueError, match="Missing required fields"):
            self.templates.build_prompt(
                ContentType.VOCABULARY,
                'word_explanation',
                word='casa'  # Missing user_level and difficulty_level
            )
    
    def test_optional_fields(self):
        """Test handling of optional fields"""
        # This should work with optional fields missing
        prompt = self.templates.build_prompt(
            ContentType.GRAMMAR,
            'error_correction',
            incorrect_sentence='Yo es estudiante',
            user_level='beginner'
            # context is optional
        )
        
        assert 'Yo es estudiante' in prompt
        assert 'beginner' in prompt
    
    def test_template_requirements(self):
        """Test getting template requirements"""
        requirements = self.templates.get_template_requirements(
            ContentType.VOCABULARY, 'word_explanation'
        )
        
        assert 'required' in requirements
        assert 'optional' in requirements
        assert 'word' in requirements['required']
        assert isinstance(requirements['required'], list)
        assert isinstance(requirements['optional'], list)
    
    def test_template_suggestions(self):
        """Test template suggestions based on user needs"""
        suggestions = self.templates.suggest_templates('I need help with vocabulary', UserLevel.INTERMEDIATE)
        
        assert len(suggestions) > 0
        assert any('vocabulary' in s['content_type'] for s in suggestions)
        assert all('match_reason' in s for s in suggestions)
    
    def test_template_listing(self):
        """Test listing all available templates"""
        all_templates = self.templates.list_templates()
        
        assert isinstance(all_templates, dict)
        assert ContentType.VOCABULARY.value in all_templates
        assert ContentType.GRAMMAR.value in all_templates
        assert len(all_templates[ContentType.VOCABULARY.value]) > 0


class TestOpenAIClient:
    """Test OpenAI client (with mocked responses)"""
    
    def setup_method(self):
        """Setup test environment with mock"""
        # Skip if OpenAI not available
        try:
            self.client = OpenAIClient(api_key="test_key")
        except (ImportError, ValueError):
            pytest.skip("OpenAI library not available or no API key")
    
    @patch('ai.content_generation.openai_client.OpenAI')
    def test_client_initialization(self, mock_openai):
        """Test client initialization"""
        client = OpenAIClient(api_key="test_key")
        assert client.api_key == "test_key"
        assert client.model == "gpt-4"
        assert client.max_retries == 3
        assert isinstance(client.rate_limiter, TokenBucket)
    
    def test_cache_key_generation(self):
        """Test cache key generation"""
        if not hasattr(self, 'client'):
            pytest.skip("OpenAI client not available")
        
        request1 = GenerationRequest(
            prompt="Test prompt",
            content_type="vocabulary",
            difficulty_level="medium",
            user_level="intermediate"
        )
        
        request2 = GenerationRequest(
            prompt="Test prompt",
            content_type="vocabulary", 
            difficulty_level="medium",
            user_level="intermediate"
        )
        
        request3 = GenerationRequest(
            prompt="Different prompt",
            content_type="vocabulary",
            difficulty_level="medium",
            user_level="intermediate"
        )
        
        key1 = self.client._generate_cache_key(request1)
        key2 = self.client._generate_cache_key(request2)
        key3 = self.client._generate_cache_key(request3)
        
        assert key1 == key2  # Same requests should have same key
        assert key1 != key3  # Different requests should have different keys
    
    def test_system_message_building(self):
        """Test system message construction"""
        if not hasattr(self, 'client'):
            pytest.skip("OpenAI client not available")
        
        request = GenerationRequest(
            prompt="Test prompt",
            content_type="vocabulary",
            difficulty_level="medium",
            user_level="intermediate"
        )
        
        system_message = self.client._build_system_message(request)
        
        assert 'Spanish language teacher' in system_message
        assert 'intermediate' in system_message.lower()
        assert 'vocabulary' in system_message.lower()
        assert 'medium' in system_message.lower()
    
    def test_cost_estimation(self):
        """Test token cost estimation"""
        if not hasattr(self, 'client'):
            pytest.skip("OpenAI client not available")
        
        cost = self.client._estimate_cost(1000)
        assert cost > 0
        assert isinstance(cost, float)
        
        # Larger token count should cost more
        cost_large = self.client._estimate_cost(2000)
        assert cost_large > cost
    
    def test_usage_stats(self):
        """Test usage statistics tracking"""
        if not hasattr(self, 'client'):
            pytest.skip("OpenAI client not available")
        
        stats = self.client.get_usage_stats()
        
        assert 'total_requests' in stats
        assert 'failed_requests' in stats
        assert 'success_rate' in stats
        assert 'total_tokens_used' in stats
        assert 'cache_size' in stats
        
        # All should be numbers
        assert isinstance(stats['total_requests'], int)
        assert isinstance(stats['success_rate'], float)
    
    @patch('ai.content_generation.openai_client.OpenAI')
    @patch('asyncio.to_thread')
    async def test_mock_api_call(self, mock_to_thread, mock_openai):
        """Test API call with mocked response"""
        # Mock the OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response content"
        mock_response.usage.total_tokens = 100
        
        mock_to_thread.return_value = mock_response
        
        client = OpenAIClient(api_key="test_key")
        
        request = GenerationRequest(
            prompt="Test prompt",
            content_type="vocabulary",
            difficulty_level="medium",
            user_level="intermediate"
        )
        
        response = await client.generate_content(request)
        
        assert isinstance(response, GenerationResponse)
        assert response.content == "Test response content"
        assert response.tokens_used == 100
        assert response.cost_estimate > 0


class TestContentGenerator:
    """Test content generator"""
    
    def setup_method(self):
        """Setup test environment with mock client"""
        # Create mock OpenAI client
        mock_client = Mock(spec=OpenAIClient)
        mock_response = GenerationResponse(
            content="Mock generated content",
            request_id="test_123",
            timestamp=datetime.now(),
            tokens_used=50,
            cost_estimate=0.05,
            cached=False
        )
        mock_client.generate_content = AsyncMock(return_value=mock_response)
        
        self.generator = ContentGenerator(openai_client=mock_client)
    
    async def test_vocabulary_lesson_generation(self):
        """Test vocabulary lesson generation"""
        result = await self.generator.generate_vocabulary_lesson(
            word="casa",
            user_level="intermediate",
            difficulty="medium"
        )
        
        assert result['type'] == 'vocabulary'
        assert result['word'] == 'casa'
        assert 'content' in result
        assert 'metadata' in result
        assert result['metadata']['tokens_used'] == 50
    
    async def test_grammar_explanation_generation(self):
        """Test grammar explanation generation"""
        result = await self.generator.generate_grammar_explanation(
            concept="subjunctive mood",
            user_level="advanced",
            difficulty="hard"
        )
        
        assert result['type'] == 'grammar'
        assert result['concept'] == "subjunctive mood"
        assert 'content' in result
        assert 'metadata' in result
    
    async def test_conversation_practice_generation(self):
        """Test conversation practice generation"""
        result = await self.generator.generate_conversation_practice(
            scenario="ordering food at restaurant",
            user_level="intermediate",
            setting="casual restaurant"
        )
        
        assert result['type'] == 'conversation'
        assert result['scenario'] == "ordering food at restaurant"
        assert 'content' in result
    
    async def test_exercise_generation(self):
        """Test exercise generation"""
        result = await self.generator.generate_exercise(
            exercise_type="fill_in_blanks",
            grammar_point="ser vs estar",
            user_level="intermediate"
        )
        
        assert result['type'] == 'exercise'
        assert result['exercise_type'] == "fill_in_blanks"
        assert result['grammar_point'] == "ser vs estar"
        assert 'content' in result
    
    async def test_hint_generation(self):
        """Test contextual hint generation"""
        result = await self.generator.generate_contextual_hint(
            target_concept="subjunctive triggers",
            user_struggle="can't identify when to use subjunctive",
            user_level="intermediate"
        )
        
        assert result['type'] == 'hint'
        assert result['target_concept'] == "subjunctive triggers"
        assert 'content' in result
    
    async def test_error_correction_generation(self):
        """Test error correction generation"""
        result = await self.generator.generate_error_correction(
            incorrect_sentence="Yo soy teniendo hambre",
            user_level="beginner"
        )
        
        assert result['type'] == 'correction'
        assert result['original_sentence'] == "Yo soy teniendo hambre"
        assert 'content' in result
    
    async def test_story_generation(self):
        """Test story generation"""
        result = await self.generator.generate_story(
            vocabulary_theme="family",
            target_grammar="past tense",
            user_level="intermediate"
        )
        
        assert result['type'] == 'story'
        assert result['vocabulary_theme'] == "family"
        assert result['target_grammar'] == "past tense"
        assert 'content' in result
    
    async def test_batch_content_generation(self):
        """Test batch content generation"""
        content_requests = [
            {
                'type': 'vocabulary',
                'word': 'casa',
                'user_level': 'intermediate'
            },
            {
                'type': 'grammar',
                'concept': 'present tense',
                'user_level': 'beginner'
            },
            {
                'type': 'hint',
                'target_concept': 'gender agreement',
                'user_struggle': 'forgets adjective agreement',
                'user_level': 'elementary'
            }
        ]
        
        results = await self.generator.batch_generate_content(content_requests)
        
        assert len(results) == 3
        assert results[0]['type'] == 'vocabulary'
        assert results[1]['type'] == 'grammar'
        assert results[2]['type'] == 'hint'
    
    def test_structured_text_parsing(self):
        """Test parsing of structured text responses"""
        sample_text = '''
1. Word: casa
2. Translation: house
3. Examples:
   - Mi casa es grande
   - Voy a casa
4. Tips: Remember casa is feminine
        '''
        
        parsed = self.generator._parse_structured_text(sample_text)
        
        assert isinstance(parsed, dict)
        assert len(parsed) > 1
        # Should have extracted sections based on numbering
    
    def test_usage_statistics(self):
        """Test usage statistics collection"""
        stats = self.generator.get_usage_statistics()
        
        assert 'openai_stats' in stats
        assert 'generation_history_count' in stats
        assert 'template_count' in stats
        
        assert isinstance(stats['template_count'], int)
        assert stats['template_count'] > 0


class TestIntegration:
    """Integration tests for content generation system"""
    
    def setup_method(self):
        """Setup integrated system"""
        self.templates = PromptTemplates()
        
        # Mock OpenAI client for integration tests
        mock_client = Mock(spec=OpenAIClient)
        mock_response = GenerationResponse(
            content='{"word": "casa", "translation": "house", "examples": ["Mi casa", "Tu casa"]}',
            request_id="test_integration",
            timestamp=datetime.now(),
            tokens_used=75,
            cost_estimate=0.075,
            cached=False
        )
        mock_client.generate_content = AsyncMock(return_value=mock_response)
        
        self.generator = ContentGenerator(openai_client=mock_client)
    
    async def test_template_to_generation_flow(self):
        """Test complete flow from template to generated content"""
        # First, build a prompt using templates
        prompt = self.templates.build_prompt(
            ContentType.VOCABULARY,
            'word_explanation',
            word='perro',
            user_level='beginner',
            difficulty_level='easy'
        )
        
        assert 'perro' in prompt
        assert len(prompt) > 50
        
        # Then use generator to create content
        result = await self.generator.generate_vocabulary_lesson(
            word="perro",
            user_level="beginner",
            difficulty="easy"
        )
        
        assert result['type'] == 'vocabulary'
        assert result['word'] == 'perro'
        
        # Content should be parsed (mock returns JSON)
        content = result['content']
        assert isinstance(content, dict)
    
    def test_template_coverage(self):
        """Test that generator covers all main template types"""
        all_templates = self.templates.list_templates()
        
        # Check that we have generation methods for main content types
        generator_methods = [
            'generate_vocabulary_lesson',
            'generate_grammar_explanation', 
            'generate_conversation_practice',
            'generate_exercise',
            'generate_contextual_hint',
            'generate_story'
        ]
        
        for method_name in generator_methods:
            assert hasattr(self.generator, method_name)
            method = getattr(self.generator, method_name)
            assert callable(method)


if __name__ == "__main__":
    # Run async tests with asyncio
    def run_async_tests():
        async def async_test_runner():
            # Create test instances
            test_client = TestOpenAIClient()
            test_client.setup_method()
            
            test_generator = TestContentGenerator()
            test_generator.setup_method()
            
            test_integration = TestIntegration()
            test_integration.setup_method()
            
            # Run async tests
            if hasattr(test_client, 'client'):
                await test_client.test_mock_api_call()
            
            await test_generator.test_vocabulary_lesson_generation()
            await test_generator.test_batch_content_generation()
            
            await test_integration.test_template_to_generation_flow()
            
            print("All async tests completed successfully!")
        
        asyncio.run(async_test_runner())
    
    # Run regular pytest for sync tests, then async tests
    pytest.main([__file__, "-v", "-k", "not test_mock_api_call"])
    run_async_tests()