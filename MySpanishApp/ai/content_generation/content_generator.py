"""
Content Generator for Spanish Learning
Combines OpenAI client with prompt templates for intelligent content creation
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import logging

from .openai_client import OpenAIClient, GenerationRequest, GenerationResponse
from .prompt_templates import PromptTemplates, ContentType, UserLevel, DifficultyLevel


class ContentGenerator:
    """High-level content generator for Spanish learning materials"""
    
    def __init__(self, openai_client: OpenAIClient = None):
        """
        Initialize content generator
        
        Args:
            openai_client: OpenAI client instance
        """
        self.openai_client = openai_client or OpenAIClient()
        self.prompt_templates = PromptTemplates()
        self.logger = logging.getLogger(__name__)
        
        # Content generation history
        self.generation_history: List[Dict] = []
        
    async def generate_vocabulary_lesson(self, 
                                       word: str,
                                       user_level: str = "intermediate",
                                       difficulty: str = "medium",
                                       context: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate comprehensive vocabulary lesson"""
        prompt = self.prompt_templates.build_prompt(
            ContentType.VOCABULARY,
            'word_explanation',
            word=word,
            user_level=user_level,
            difficulty_level=difficulty
        )
        
        request = GenerationRequest(
            prompt=prompt,
            content_type="vocabulary",
            difficulty_level=difficulty,
            user_level=user_level,
            max_tokens=800,
            temperature=0.7,
            context=context
        )
        
        response = await self.openai_client.generate_content(request)
        return self._parse_vocabulary_response(response, word)
    
    async def generate_grammar_explanation(self,
                                         concept: str,
                                         user_level: str = "intermediate",
                                         difficulty: str = "medium",
                                         user_context: Optional[str] = None) -> Dict[str, Any]:
        """Generate grammar concept explanation"""
        prompt = self.prompt_templates.build_prompt(
            ContentType.GRAMMAR,
            'concept_explanation',
            concept=concept,
            user_level=user_level,
            difficulty_level=difficulty
        )
        
        if user_context:
            prompt += f"\n\nUser Context: {user_context}"
        
        request = GenerationRequest(
            prompt=prompt,
            content_type="grammar",
            difficulty_level=difficulty,
            user_level=user_level,
            max_tokens=1000,
            temperature=0.6
        )
        
        response = await self.openai_client.generate_content(request)
        return self._parse_grammar_response(response, concept)
    
    async def generate_conversation_practice(self,
                                           scenario: str,
                                           user_level: str = "intermediate",
                                           setting: str = "",
                                           focus: str = "practical communication") -> Dict[str, Any]:
        """Generate conversation practice dialogue"""
        prompt = self.prompt_templates.build_prompt(
            ContentType.CONVERSATION,
            'dialogue_practice',
            scenario=scenario,
            user_level=user_level,
            setting=setting,
            conversation_focus=focus
        )
        
        request = GenerationRequest(
            prompt=prompt,
            content_type="conversation",
            difficulty_level="medium",
            user_level=user_level,
            max_tokens=1200,
            temperature=0.8
        )
        
        response = await self.openai_client.generate_content(request)
        return self._parse_conversation_response(response, scenario)
    
    async def generate_exercise(self,
                              exercise_type: str,
                              grammar_point: str,
                              user_level: str = "intermediate",
                              difficulty: str = "medium",
                              context_theme: str = "") -> Dict[str, Any]:
        """Generate practice exercise"""
        if exercise_type == "fill_in_blanks":
            template_name = 'fill_in_blanks'
        elif exercise_type == "translation":
            template_name = 'translation_exercise'
        else:
            template_name = 'fill_in_blanks'  # Default
        
        if template_name == 'fill_in_blanks':
            prompt = self.prompt_templates.build_prompt(
                ContentType.EXERCISE,
                template_name,
                grammar_point=grammar_point,
                user_level=user_level,
                context_theme=context_theme
            )
        else:
            prompt = self.prompt_templates.build_prompt(
                ContentType.EXERCISE,
                template_name,
                source_language="English",
                target_language="Spanish",
                learning_objective=grammar_point,
                user_level=user_level,
                theme=context_theme
            )
        
        request = GenerationRequest(
            prompt=prompt,
            content_type="exercise",
            difficulty_level=difficulty,
            user_level=user_level,
            max_tokens=1000,
            temperature=0.6
        )
        
        response = await self.openai_client.generate_content(request)
        return self._parse_exercise_response(response, exercise_type, grammar_point)
    
    async def generate_contextual_hint(self,
                                     target_concept: str,
                                     user_struggle: str,
                                     user_level: str = "intermediate",
                                     context: str = "") -> Dict[str, Any]:
        """Generate contextual hint for learning difficulty"""
        prompt = self.prompt_templates.build_prompt(
            ContentType.HINT,
            'contextual_hint',
            target_concept=target_concept,
            user_struggle=user_struggle,
            user_level=user_level,
            context=context
        )
        
        request = GenerationRequest(
            prompt=prompt,
            content_type="hint",
            difficulty_level="easy",
            user_level=user_level,
            max_tokens=300,
            temperature=0.7
        )
        
        response = await self.openai_client.generate_content(request)
        return self._parse_hint_response(response, target_concept)
    
    async def generate_error_correction(self,
                                      incorrect_sentence: str,
                                      user_level: str = "intermediate",
                                      context: str = "") -> Dict[str, Any]:
        """Generate error correction and explanation"""
        prompt = self.prompt_templates.build_prompt(
            ContentType.GRAMMAR,
            'error_correction',
            incorrect_sentence=incorrect_sentence,
            user_level=user_level,
            context=context
        )
        
        request = GenerationRequest(
            prompt=prompt,
            content_type="correction",
            difficulty_level="medium",
            user_level=user_level,
            max_tokens=600,
            temperature=0.6
        )
        
        response = await self.openai_client.generate_content(request)
        return self._parse_correction_response(response, incorrect_sentence)
    
    async def generate_story(self,
                           vocabulary_theme: str,
                           target_grammar: str,
                           user_level: str = "intermediate",
                           length: str = "medium") -> Dict[str, Any]:
        """Generate educational story"""
        prompt = self.prompt_templates.build_prompt(
            ContentType.STORY,
            'level_appropriate_story',
            user_level=user_level,
            vocabulary_theme=vocabulary_theme,
            target_grammar=target_grammar
        )
        
        max_tokens = {
            'short': 400,
            'medium': 600,
            'long': 800
        }.get(length, 600)
        
        request = GenerationRequest(
            prompt=prompt,
            content_type="story",
            difficulty_level="medium",
            user_level=user_level,
            max_tokens=max_tokens,
            temperature=0.8
        )
        
        response = await self.openai_client.generate_content(request)
        return self._parse_story_response(response, vocabulary_theme, target_grammar)
    
    async def batch_generate_content(self, 
                                   content_requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate multiple pieces of content in batch"""
        generation_requests = []
        
        for req in content_requests:
            content_type = req.get('type')
            method_map = {
                'vocabulary': self.generate_vocabulary_lesson,
                'grammar': self.generate_grammar_explanation,
                'conversation': self.generate_conversation_practice,
                'exercise': self.generate_exercise,
                'hint': self.generate_contextual_hint,
                'correction': self.generate_error_correction,
                'story': self.generate_story
            }
            
            if content_type in method_map:
                # Extract parameters for each method
                params = {k: v for k, v in req.items() if k != 'type'}
                generation_requests.append(method_map[content_type](**params))
        
        # Execute all requests concurrently
        results = await asyncio.gather(*generation_requests, return_exceptions=True)
        
        # Log any errors but return successful results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Content generation failed for request {i}: {str(result)}")
                processed_results.append({
                    'error': str(result),
                    'request_index': i
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    def _parse_vocabulary_response(self, response: GenerationResponse, word: str) -> Dict[str, Any]:
        """Parse vocabulary lesson response"""
        try:
            # Try to parse as JSON first
            content = json.loads(response.content)
        except json.JSONDecodeError:
            # Fallback to structured text parsing
            content = self._parse_structured_text(response.content)
        
        return {
            'type': 'vocabulary',
            'word': word,
            'content': content,
            'metadata': {
                'request_id': response.request_id,
                'timestamp': response.timestamp,
                'tokens_used': response.tokens_used,
                'cached': response.cached
            }
        }
    
    def _parse_grammar_response(self, response: GenerationResponse, concept: str) -> Dict[str, Any]:
        """Parse grammar explanation response"""
        try:
            content = json.loads(response.content)
        except json.JSONDecodeError:
            content = self._parse_structured_text(response.content)
        
        return {
            'type': 'grammar',
            'concept': concept,
            'content': content,
            'metadata': {
                'request_id': response.request_id,
                'timestamp': response.timestamp,
                'tokens_used': response.tokens_used,
                'cached': response.cached
            }
        }
    
    def _parse_conversation_response(self, response: GenerationResponse, scenario: str) -> Dict[str, Any]:
        """Parse conversation practice response"""
        try:
            content = json.loads(response.content)
        except json.JSONDecodeError:
            content = self._parse_structured_text(response.content)
        
        return {
            'type': 'conversation',
            'scenario': scenario,
            'content': content,
            'metadata': {
                'request_id': response.request_id,
                'timestamp': response.timestamp,
                'tokens_used': response.tokens_used,
                'cached': response.cached
            }
        }
    
    def _parse_exercise_response(self, response: GenerationResponse, exercise_type: str, grammar_point: str) -> Dict[str, Any]:
        """Parse exercise response"""
        try:
            content = json.loads(response.content)
        except json.JSONDecodeError:
            content = self._parse_structured_text(response.content)
        
        return {
            'type': 'exercise',
            'exercise_type': exercise_type,
            'grammar_point': grammar_point,
            'content': content,
            'metadata': {
                'request_id': response.request_id,
                'timestamp': response.timestamp,
                'tokens_used': response.tokens_used,
                'cached': response.cached
            }
        }
    
    def _parse_hint_response(self, response: GenerationResponse, target_concept: str) -> Dict[str, Any]:
        """Parse hint response"""
        return {
            'type': 'hint',
            'target_concept': target_concept,
            'content': response.content,
            'metadata': {
                'request_id': response.request_id,
                'timestamp': response.timestamp,
                'tokens_used': response.tokens_used,
                'cached': response.cached
            }
        }
    
    def _parse_correction_response(self, response: GenerationResponse, incorrect_sentence: str) -> Dict[str, Any]:
        """Parse error correction response"""
        try:
            content = json.loads(response.content)
        except json.JSONDecodeError:
            content = self._parse_structured_text(response.content)
        
        return {
            'type': 'correction',
            'original_sentence': incorrect_sentence,
            'content': content,
            'metadata': {
                'request_id': response.request_id,
                'timestamp': response.timestamp,
                'tokens_used': response.tokens_used,
                'cached': response.cached
            }
        }
    
    def _parse_story_response(self, response: GenerationResponse, vocabulary_theme: str, target_grammar: str) -> Dict[str, Any]:
        """Parse story response"""
        try:
            content = json.loads(response.content)
        except json.JSONDecodeError:
            content = self._parse_structured_text(response.content)
        
        return {
            'type': 'story',
            'vocabulary_theme': vocabulary_theme,
            'target_grammar': target_grammar,
            'content': content,
            'metadata': {
                'request_id': response.request_id,
                'timestamp': response.timestamp,
                'tokens_used': response.tokens_used,
                'cached': response.cached
            }
        }
    
    def _parse_structured_text(self, text: str) -> Dict[str, Any]:
        """Parse structured text when JSON parsing fails"""
        # Simple fallback parsing for structured text
        sections = {}
        current_section = "content"
        current_content = []
        
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Look for section headers (numbers, bullets, etc.)
            if (line.startswith(('1.', '2.', '3.', '4.', '5.')) or
                line.startswith(('•', '-', '*')) or
                line.endswith(':') and len(line.split()) <= 4):
                
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content)
                
                # Start new section
                current_section = line.rstrip(':').lower().replace(' ', '_')
                current_content = []
            else:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections if sections else {'content': text}
    
    def get_generation_history(self, limit: int = 10) -> List[Dict]:
        """Get recent generation history"""
        return self.generation_history[-limit:]
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """Get content generation statistics"""
        return {
            'openai_stats': self.openai_client.get_usage_stats(),
            'generation_history_count': len(self.generation_history),
            'template_count': sum(len(templates) for templates in self.prompt_templates.templates.values())
        }