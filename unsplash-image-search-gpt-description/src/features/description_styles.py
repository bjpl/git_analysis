"""
Description styles module for generating different types of AI descriptions.
Provides three distinct styles: Academic/Neutral, Poetic/Literary, Technical/Scientific
"""

import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class DescriptionStyle(Enum):
    """Enumeration of available description styles."""
    ACADEMIC = "academic"
    POETIC = "poetic"
    TECHNICAL = "technical"


class VocabularyLevel(Enum):
    """Enumeration of vocabulary complexity levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    NATIVE = "native"


@dataclass
class StyleConfig:
    """Configuration for a specific description style."""
    name: str
    display_name: str
    style: DescriptionStyle
    level: VocabularyLevel
    prompt_template: str
    vocabulary_focus: List[str]
    tone_keywords: List[str]
    example_phrases: List[str]


class DescriptionStyleManager:
    """Manages different description styles for AI-generated content."""
    
    def __init__(self):
        """Initialize the description style manager with predefined styles."""
        self.current_style = DescriptionStyle.ACADEMIC
        self.current_level = VocabularyLevel.INTERMEDIATE
        self._initialize_styles()
    
    def _initialize_styles(self):
        """Initialize the style configurations."""
        self.styles = {
            DescriptionStyle.ACADEMIC: {
                VocabularyLevel.BEGINNER: StyleConfig(
                    name="academic_beginner",
                    display_name="Academic/Neutral - Beginner",
                    style=DescriptionStyle.ACADEMIC,
                    level=VocabularyLevel.BEGINNER,
                    prompt_template="""Describe this image in academic Spanish using:
- Simple, clear vocabulary for beginners
- Objective, factual descriptions
- Present tense primarily
- Basic sentence structures
- Educational tone without complex terminology""",
                    vocabulary_focus=["nouns", "basic_verbs", "colors", "positions"],
                    tone_keywords=["objetivo", "claro", "simple", "educativo"],
                    example_phrases=[
                        "En la imagen se observa...",
                        "El elemento principal es...",
                        "Los colores predominantes son..."
                    ]
                ),
                VocabularyLevel.INTERMEDIATE: StyleConfig(
                    name="academic_intermediate",
                    display_name="Academic/Neutral - Intermediate",
                    style=DescriptionStyle.ACADEMIC,
                    level=VocabularyLevel.INTERMEDIATE,
                    prompt_template="""Provide an academic analysis in Spanish using:
- Formal, objective language
- Academic vocabulary and connectors (por lo tanto, sin embargo, además)
- Multiple verb tenses
- Structured paragraphs with clear transitions
- Analytical observations about composition and context""",
                    vocabulary_focus=["academic_connectors", "analytical_verbs", "formal_adjectives"],
                    tone_keywords=["formal", "analítico", "estructurado", "objetivo"],
                    example_phrases=[
                        "Cabe destacar que...",
                        "En términos de composición...",
                        "Se puede apreciar claramente..."
                    ]
                ),
                VocabularyLevel.ADVANCED: StyleConfig(
                    name="academic_advanced",
                    display_name="Academic/Neutral - Advanced",
                    style=DescriptionStyle.ACADEMIC,
                    level=VocabularyLevel.ADVANCED,
                    prompt_template="""Create a sophisticated academic analysis in Spanish featuring:
- Complex academic terminology
- Subjunctive mood where appropriate
- Scholarly discourse markers
- Critical analysis of visual elements
- References to artistic or cultural context""",
                    vocabulary_focus=["scholarly_terms", "subjunctive_constructions", "critical_analysis"],
                    tone_keywords=["erudito", "crítico", "contextual", "sofisticado"],
                    example_phrases=[
                        "Es menester señalar que...",
                        "Desde una perspectiva semiótica...",
                        "La yuxtaposición de elementos sugiere..."
                    ]
                )
            },
            DescriptionStyle.POETIC: {
                VocabularyLevel.BEGINNER: StyleConfig(
                    name="poetic_beginner",
                    display_name="Poetic/Literary - Beginner",
                    style=DescriptionStyle.POETIC,
                    level=VocabularyLevel.BEGINNER,
                    prompt_template="""Create a simple poetic description in Spanish using:
- Beautiful but simple vocabulary
- Basic sensory descriptions (colors, sounds, feelings)
- Simple metaphors and comparisons
- Emotional language accessible to beginners
- Short, melodic sentences""",
                    vocabulary_focus=["emotions", "senses", "nature", "simple_metaphors"],
                    tone_keywords=["poético", "emotivo", "sensorial", "simple"],
                    example_phrases=[
                        "Como un sueño...",
                        "Los colores bailan...",
                        "La luz abraza suavemente..."
                    ]
                ),
                VocabularyLevel.INTERMEDIATE: StyleConfig(
                    name="poetic_intermediate",
                    display_name="Poetic/Literary - Intermediate",
                    style=DescriptionStyle.POETIC,
                    level=VocabularyLevel.INTERMEDIATE,
                    prompt_template="""Craft a literary description in Spanish featuring:
- Rich, expressive vocabulary
- Metaphors and similes
- Sensory imagery and synesthesia
- Emotional depth and atmosphere
- Varied rhythm and sentence structure""",
                    vocabulary_focus=["literary_devices", "sensory_adjectives", "metaphorical_verbs"],
                    tone_keywords=["lírico", "evocador", "metafórico", "expresivo"],
                    example_phrases=[
                        "El lienzo respira historias...",
                        "Como pétalos de memoria...",
                        "La melancolía se derrama..."
                    ]
                ),
                VocabularyLevel.ADVANCED: StyleConfig(
                    name="poetic_advanced",
                    display_name="Poetic/Literary - Advanced",
                    style=DescriptionStyle.POETIC,
                    level=VocabularyLevel.ADVANCED,
                    prompt_template="""Compose an elaborate literary piece in Spanish with:
- Sophisticated poetic devices
- Complex metaphorical systems
- Intertextual references
- Philosophical undertones
- Experimental language and neologisms where fitting""",
                    vocabulary_focus=["literary_allusions", "philosophical_concepts", "avant_garde"],
                    tone_keywords=["transcendente", "filosófico", "vanguardista", "sublime"],
                    example_phrases=[
                        "En el crisol de lo inefable...",
                        "La epifanía cromática trasciende...",
                        "Como un palimpsesto visual..."
                    ]
                )
            },
            DescriptionStyle.TECHNICAL: {
                VocabularyLevel.BEGINNER: StyleConfig(
                    name="technical_beginner",
                    display_name="Technical/Scientific - Beginner",
                    style=DescriptionStyle.TECHNICAL,
                    level=VocabularyLevel.BEGINNER,
                    prompt_template="""Provide a basic technical description in Spanish using:
- Simple technical vocabulary
- Basic measurements and quantities
- Clear cause-and-effect relationships
- Systematic organization
- Introduction to technical terms with explanations""",
                    vocabulary_focus=["measurements", "materials", "basic_processes", "shapes"],
                    tone_keywords=["técnico", "preciso", "sistemático", "claro"],
                    example_phrases=[
                        "El objeto mide aproximadamente...",
                        "El material parece ser...",
                        "La estructura muestra..."
                    ]
                ),
                VocabularyLevel.INTERMEDIATE: StyleConfig(
                    name="technical_intermediate",
                    display_name="Technical/Scientific - Intermediate",
                    style=DescriptionStyle.TECHNICAL,
                    level=VocabularyLevel.INTERMEDIATE,
                    prompt_template="""Generate a technical analysis in Spanish including:
- Specialized technical terminology
- Precise measurements and specifications
- Scientific methodology in observations
- Technical processes and mechanisms
- Data-driven descriptions""",
                    vocabulary_focus=["technical_specifications", "scientific_methods", "engineering_terms"],
                    tone_keywords=["científico", "metodológico", "cuantitativo", "especializado"],
                    example_phrases=[
                        "Las propiedades ópticas indican...",
                        "El análisis compositivo revela...",
                        "Según los parámetros observables..."
                    ]
                ),
                VocabularyLevel.ADVANCED: StyleConfig(
                    name="technical_advanced",
                    display_name="Technical/Scientific - Advanced",
                    style=DescriptionStyle.TECHNICAL,
                    level=VocabularyLevel.ADVANCED,
                    prompt_template="""Produce an expert-level technical analysis in Spanish with:
- Highly specialized scientific terminology
- Quantitative analysis where applicable
- References to scientific principles
- Technical specifications and tolerances
- Interdisciplinary technical connections""",
                    vocabulary_focus=["specialized_jargon", "scientific_principles", "quantitative_analysis"],
                    tone_keywords=["altamente_técnico", "cuantitativo", "interdisciplinario", "especializado"],
                    example_phrases=[
                        "La refracción lumínica sugiere un índice...",
                        "Los vectores compositivos convergen...",
                        "La entropía visual correlaciona con..."
                    ]
                )
            }
        }
    
    def set_style(self, style: DescriptionStyle, level: VocabularyLevel = None):
        """
        Set the current description style and vocabulary level.
        
        Args:
            style: The description style to use
            level: The vocabulary level (optional, keeps current if not provided)
        """
        self.current_style = style
        if level:
            self.current_level = level
    
    def get_current_config(self) -> StyleConfig:
        """Get the current style configuration."""
        return self.styles[self.current_style][self.current_level]
    
    def generate_prompt(self, base_context: str = "", user_notes: str = "") -> str:
        """
        Generate a style-specific prompt for AI description.
        
        Args:
            base_context: Base context about the image
            user_notes: Additional notes from the user
            
        Returns:
            Complete prompt tailored to the selected style
        """
        config = self.get_current_config()
        
        prompt = f"{config.prompt_template}\n\n"
        
        # Add example phrases
        if config.example_phrases:
            prompt += "Usa frases como:\n"
            for phrase in config.example_phrases:
                prompt += f"- {phrase}\n"
            prompt += "\n"
        
        # Add base context
        if base_context:
            prompt += f"Contexto de la imagen: {base_context}\n\n"
        
        # Add user notes
        if user_notes:
            prompt += f"Notas adicionales del usuario: {user_notes}\n\n"
        
        # Add vocabulary focus
        prompt += f"Enfócate en vocabulario relacionado con: {', '.join(config.vocabulary_focus)}\n"
        
        return prompt
    
    def extract_vocabulary_for_style(self, text: str) -> Dict[str, List[str]]:
        """
        Extract vocabulary appropriate for the current style.
        
        Args:
            text: The text to extract vocabulary from
            
        Returns:
            Dictionary of vocabulary categories and words
        """
        config = self.get_current_config()
        vocabulary = {}
        
        if config.style == DescriptionStyle.ACADEMIC:
            vocabulary = {
                "Términos académicos": [],
                "Conectores formales": [],
                "Verbos analíticos": [],
                "Conceptos clave": []
            }
        elif config.style == DescriptionStyle.POETIC:
            vocabulary = {
                "Imágenes poéticas": [],
                "Metáforas": [],
                "Adjetivos sensoriales": [],
                "Expresiones líricas": []
            }
        elif config.style == DescriptionStyle.TECHNICAL:
            vocabulary = {
                "Términos técnicos": [],
                "Especificaciones": [],
                "Procesos": [],
                "Componentes": []
            }
        
        # This would normally use NLP to extract actual vocabulary
        # For now, return the structure for integration
        return vocabulary
    
    def get_style_info(self) -> Dict[str, any]:
        """Get information about the current style settings."""
        config = self.get_current_config()
        return {
            "style": config.style.value,
            "level": config.level.value,
            "display_name": config.display_name,
            "tone_keywords": config.tone_keywords,
            "example_phrases": config.example_phrases[:2]  # Just show 2 examples
        }
    
    def get_available_styles(self) -> List[Tuple[str, str]]:
        """Get list of available style options."""
        styles = []
        for style in DescriptionStyle:
            styles.append((style.value, style.value.capitalize()))
        return styles
    
    def get_available_levels(self) -> List[Tuple[str, str]]:
        """Get list of available vocabulary levels."""
        levels = []
        for level in VocabularyLevel:
            levels.append((level.value, level.value.capitalize()))
        return levels
    
    def save_preferences(self, filepath: str):
        """Save style preferences to a JSON file."""
        preferences = {
            "style": self.current_style.value,
            "level": self.current_level.value
        }
        with open(filepath, 'w') as f:
            json.dump(preferences, f, indent=2)
    
    def load_preferences(self, filepath: str) -> bool:
        """
        Load style preferences from a JSON file.
        
        Returns:
            True if preferences were loaded successfully
        """
        try:
            with open(filepath, 'r') as f:
                preferences = json.load(f)
            
            style = DescriptionStyle(preferences.get("style", "academic"))
            level = VocabularyLevel(preferences.get("level", "intermediate"))
            self.set_style(style, level)
            return True
        except (FileNotFoundError, json.JSONDecodeError, ValueError):
            return False