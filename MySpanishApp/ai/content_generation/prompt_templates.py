"""
Prompt Templates for Content Generation
Structured templates for different types of Spanish learning content
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum


class ContentType(Enum):
    """Types of content that can be generated"""
    VOCABULARY = "vocabulary"
    GRAMMAR = "grammar"
    CONVERSATION = "conversation"
    EXERCISE = "exercise"
    STORY = "story"
    EXPLANATION = "explanation"
    HINT = "hint"
    CORRECTION = "correction"


class DifficultyLevel(Enum):
    """Difficulty levels for content"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class UserLevel(Enum):
    """User proficiency levels"""
    BEGINNER = "beginner"
    ELEMENTARY = "elementary"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    NATIVE = "native"


@dataclass
class PromptTemplate:
    """Template for generating prompts"""
    template: str
    required_fields: List[str]
    optional_fields: List[str] = None
    examples: List[str] = None


class PromptTemplates:
    """Collection of prompt templates for Spanish learning content"""
    
    def __init__(self):
        self.templates = {
            ContentType.VOCABULARY: {
                'word_explanation': PromptTemplate(
                    template="""Create a comprehensive vocabulary lesson for the Spanish word "{word}".

Include:
1. Word: {word}
2. English translation(s)
3. Part of speech
4. Pronunciation guide (phonetic)
5. 3 example sentences in Spanish with English translations
6. Common collocations or phrases
7. Cultural context or usage notes
8. Memory aids or mnemonics
9. Related words (synonyms, antonyms, word family)
10. Regional variations if applicable

Level: {user_level}
Difficulty: {difficulty_level}

Format as structured JSON with clear sections.""",
                    required_fields=['word', 'user_level', 'difficulty_level'],
                    examples=[
                        "Create vocabulary lesson for 'casa' (house)",
                        "Create vocabulary lesson for 'subjuntivo' (subjunctive)"
                    ]
                ),
                
                'thematic_vocabulary': PromptTemplate(
                    template="""Create a thematic vocabulary set for "{theme}" in Spanish.

Requirements:
- Include 15-20 words related to {theme}
- Provide English translations
- Group into logical subcategories
- Include pronunciation guides
- Add 2-3 example sentences using multiple words from the set
- Suggest memory techniques for the theme
- Include cultural context where relevant

Level: {user_level}
Difficulty: {difficulty_level}
Theme: {theme}

Format as structured JSON with clear categorization.""",
                    required_fields=['theme', 'user_level', 'difficulty_level'],
                    examples=[
                        "Food and dining vocabulary",
                        "Business and workplace terms"
                    ]
                )
            },
            
            ContentType.GRAMMAR: {
                'concept_explanation': PromptTemplate(
                    template="""Explain the Spanish grammar concept: "{concept}"

Structure your explanation as follows:
1. Clear definition and purpose
2. Formation rules with patterns
3. 5+ examples with English translations
4. Common mistakes to avoid
5. Usage guidelines and context
6. Practice exercises (3 different types)
7. Memory aids or tricks
8. Related grammar concepts
9. Cultural or regional notes if applicable

Level: {user_level}
Difficulty: {difficulty_level}
Focus on practical application and clear examples.

Format as structured content with examples highlighted.""",
                    required_fields=['concept', 'user_level', 'difficulty_level'],
                    examples=[
                        "Subjunctive mood in Spanish",
                        "Ser vs Estar usage"
                    ]
                ),
                
                'error_correction': PromptTemplate(
                    template="""Analyze and correct this Spanish sentence: "{incorrect_sentence}"

Provide:
1. Corrected sentence
2. Explanation of the error(s)
3. Grammar rule that applies
4. Why the original was incorrect
5. Alternative correct ways to express the same idea
6. Tips to avoid this error in the future
7. Related examples showing correct usage

Context: {context}
User Level: {user_level}

Be encouraging and educational in your explanation.""",
                    required_fields=['incorrect_sentence', 'user_level'],
                    optional_fields=['context'],
                    examples=[
                        "Yo soy teniendo hambre (I am being hungry)",
                        "Ella dijió que vendrá (She sayed she will come)"
                    ]
                )
            },
            
            ContentType.CONVERSATION: {
                'dialogue_practice': PromptTemplate(
                    template="""Create a natural Spanish conversation for the scenario: "{scenario}"

Requirements:
- 8-12 exchanges between 2-3 speakers
- Natural, colloquial Spanish appropriate for {user_level} level
- Include cultural context and authentic expressions
- Highlight key vocabulary and phrases
- Provide English translations for dialogue
- Add pronunciation notes for difficult words
- Include conversation tips and cultural notes
- Suggest follow-up practice activities

Scenario: {scenario}
Setting: {setting}
Level: {user_level}
Focus: {conversation_focus}

Make it engaging and practical for real-world use.""",
                    required_fields=['scenario', 'user_level'],
                    optional_fields=['setting', 'conversation_focus'],
                    examples=[
                        "Ordering food at a restaurant",
                        "Making friends at university"
                    ]
                ),
                
                'conversation_practice': PromptTemplate(
                    template="""You are a Spanish conversation partner. Engage in a natural conversation about "{topic}".

Guidelines:
- Adapt your Spanish to {user_level} level
- Ask follow-up questions to encourage dialogue
- Gently correct errors when they occur
- Introduce new vocabulary naturally
- Be encouraging and patient
- Include cultural insights when relevant
- Suggest alternative expressions
- Keep the conversation flowing naturally

Topic: {topic}
Level: {user_level}
Focus: Practical communication skills

Start the conversation with an engaging opener.""",
                    required_fields=['topic', 'user_level'],
                    examples=[
                        "Travel experiences and plans",
                        "Hobbies and interests"
                    ]
                )
            },
            
            ContentType.EXERCISE: {
                'fill_in_blanks': PromptTemplate(
                    template="""Create a fill-in-the-blank exercise focusing on "{grammar_point}".

Requirements:
- 10 sentences with strategic blanks
- Multiple choice options for each blank (4 options)
- Mix of difficulty within the exercise
- Clear context for each sentence
- Answer key with explanations
- Tips for choosing correct answers
- Common mistakes section

Grammar Focus: {grammar_point}
Level: {user_level}
Context: {context_theme}

Ensure exercises test understanding, not just memorization.""",
                    required_fields=['grammar_point', 'user_level'],
                    optional_fields=['context_theme'],
                    examples=[
                        "Subjunctive vs Indicative",
                        "Past tense selection"
                    ]
                ),
                
                'translation_exercise': PromptTemplate(
                    template="""Create a translation exercise from {source_language} to {target_language}.

Include:
- 8 sentences of varying complexity
- Focus on {learning_objective}
- Cultural context where relevant
- Multiple acceptable translations when possible
- Detailed answer explanations
- Common translation pitfalls to avoid
- Tips for natural expression

Level: {user_level}
Theme: {theme}

Balance literal accuracy with natural expression.""",
                    required_fields=['source_language', 'target_language', 'learning_objective', 'user_level'],
                    optional_fields=['theme'],
                    examples=[
                        "English to Spanish - idiomatic expressions",
                        "Spanish to English - formal register"
                    ]
                )
            },
            
            ContentType.HINT: {
                'contextual_hint': PromptTemplate(
                    template="""Provide a helpful hint for understanding "{target_concept}" in Spanish.

The user is struggling with: {user_struggle}
Current context: {context}
User level: {user_level}

Provide:
1. A gentle, encouraging hint (not the full answer)
2. A memory trick or association
3. A simplified example
4. Connection to something they already know
5. Next step suggestion

Keep it supportive and just enough to help them progress.""",
                    required_fields=['target_concept', 'user_struggle', 'user_level'],
                    optional_fields=['context'],
                    examples=[
                        "Hint for choosing between ser and estar",
                        "Hint for subjunctive trigger recognition"
                    ]
                ),
                
                'pronunciation_hint': PromptTemplate(
                    template="""Provide pronunciation guidance for "{word_or_phrase}" in Spanish.

Include:
1. Phonetic breakdown (IPA if helpful)
2. Syllable stress indication
3. Sound comparison to English sounds
4. Common pronunciation mistakes to avoid
5. Memory aids for difficult sounds
6. Recording suggestion or practice tip
7. Regional variation notes if relevant

Word/Phrase: {word_or_phrase}
User level: {user_level}
Native language: {native_language}

Focus on practical pronunciation tips.""",
                    required_fields=['word_or_phrase', 'user_level'],
                    optional_fields=['native_language'],
                    examples=[
                        "Pronunciation of 'rr' in 'perro'",
                        "Stress patterns in Spanish words"
                    ]
                )
            },
            
            ContentType.STORY: {
                'level_appropriate_story': PromptTemplate(
                    template="""Write an engaging Spanish story for {user_level} level learners.

Requirements:
- 200-400 words depending on level
- Incorporate vocabulary theme: {vocabulary_theme}
- Include target grammar: {target_grammar}
- Natural, engaging plot
- Cultural elements
- Comprehension questions (5)
- Vocabulary glossary for key terms
- Discussion questions for deeper engagement

Theme: {vocabulary_theme}
Grammar focus: {target_grammar}
Level: {user_level}

Make it culturally authentic and educationally valuable.""",
                    required_fields=['user_level', 'vocabulary_theme', 'target_grammar'],
                    examples=[
                        "Story about family traditions",
                        "Adventure story using past tenses"
                    ]
                )
            },
            
            ContentType.EXPLANATION: {
                'cultural_explanation': PromptTemplate(
                    template="""Explain the cultural concept "{cultural_concept}" in Spanish-speaking countries.

Include:
1. Clear definition and significance
2. Historical or social context
3. How it varies across different Spanish-speaking countries
4. Related vocabulary and expressions
5. Practical examples or scenarios
6. How it affects language use
7. Tips for cultural sensitivity
8. Comparison with user's culture if helpful

Concept: {cultural_concept}
Target countries: {target_countries}
User level: {user_level}

Make it informative and culturally sensitive.""",
                    required_fields=['cultural_concept', 'user_level'],
                    optional_fields=['target_countries'],
                    examples=[
                        "The concept of 'sobremesa'",
                        "Formal vs informal address systems"
                    ]
                )
            }
        }
    
    def get_template(self, content_type: ContentType, template_name: str) -> PromptTemplate:
        """Get a specific template"""
        return self.templates.get(content_type, {}).get(template_name)
    
    def get_all_templates_for_type(self, content_type: ContentType) -> Dict[str, PromptTemplate]:
        """Get all templates for a content type"""
        return self.templates.get(content_type, {})
    
    def list_templates(self) -> Dict[str, List[str]]:
        """List all available templates by type"""
        return {
            content_type.value: list(templates.keys())
            for content_type, templates in self.templates.items()
        }
    
    def build_prompt(self, 
                     content_type: ContentType, 
                     template_name: str, 
                     **kwargs) -> str:
        """Build a prompt from template with provided parameters"""
        template = self.get_template(content_type, template_name)
        if not template:
            raise ValueError(f"Template {template_name} not found for {content_type.value}")
        
        # Check required fields
        missing_fields = [field for field in template.required_fields if field not in kwargs]
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")
        
        # Fill in optional fields with defaults
        if template.optional_fields:
            for field in template.optional_fields:
                if field not in kwargs:
                    kwargs[field] = ""
        
        return template.template.format(**kwargs)
    
    def get_template_requirements(self, 
                                 content_type: ContentType, 
                                 template_name: str) -> Dict[str, List[str]]:
        """Get field requirements for a template"""
        template = self.get_template(content_type, template_name)
        if not template:
            return {}
        
        return {
            'required': template.required_fields,
            'optional': template.optional_fields or [],
            'examples': template.examples or []
        }
    
    def suggest_templates(self, user_needs: str, user_level: UserLevel) -> List[Dict[str, str]]:
        """Suggest appropriate templates based on user needs"""
        suggestions = []
        
        # Simple keyword matching for suggestions
        keywords_to_templates = {
            'vocabulary': [(ContentType.VOCABULARY, 'word_explanation'), (ContentType.VOCABULARY, 'thematic_vocabulary')],
            'grammar': [(ContentType.GRAMMAR, 'concept_explanation'), (ContentType.EXERCISE, 'fill_in_blanks')],
            'conversation': [(ContentType.CONVERSATION, 'dialogue_practice'), (ContentType.CONVERSATION, 'conversation_practice')],
            'practice': [(ContentType.EXERCISE, 'fill_in_blanks'), (ContentType.EXERCISE, 'translation_exercise')],
            'story': [(ContentType.STORY, 'level_appropriate_story')],
            'culture': [(ContentType.EXPLANATION, 'cultural_explanation')],
            'pronunciation': [(ContentType.HINT, 'pronunciation_hint')],
            'help': [(ContentType.HINT, 'contextual_hint')]
        }
        
        user_needs_lower = user_needs.lower()
        for keyword, template_list in keywords_to_templates.items():
            if keyword in user_needs_lower:
                for content_type, template_name in template_list:
                    suggestions.append({
                        'content_type': content_type.value,
                        'template_name': template_name,
                        'description': self.get_template(content_type, template_name).template.split('\n')[0],
                        'match_reason': f"Matched keyword: {keyword}"
                    })
        
        return suggestions[:5]  # Return top 5 suggestions