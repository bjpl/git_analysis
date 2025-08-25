"""
Grammar Analyzer for Spanish Language Learning
Detects and analyzes grammar errors with detailed explanations
"""

import re
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json


class ErrorType(Enum):
    """Types of grammar errors"""
    VERB_CONJUGATION = "verb_conjugation"
    GENDER_AGREEMENT = "gender_agreement"
    NUMBER_AGREEMENT = "number_agreement"
    SER_ESTAR = "ser_estar"
    SUBJUNCTIVE = "subjunctive"
    PREPOSITION = "preposition"
    WORD_ORDER = "word_order"
    ARTICLE_USAGE = "article_usage"
    PRONOUN_PLACEMENT = "pronoun_placement"
    ACCENT_MARKS = "accent_marks"
    SPELLING = "spelling"
    VOCABULARY = "vocabulary"


@dataclass
class GrammarError:
    """Represents a detected grammar error"""
    error_type: ErrorType
    position: Tuple[int, int]  # Start and end position in text
    incorrect_text: str
    suggested_correction: str
    explanation: str
    confidence: float  # 0.0 to 1.0
    rule_violated: str
    examples: List[str]
    severity: str = "medium"  # low, medium, high


@dataclass
class GrammarAnalysis:
    """Complete grammar analysis result"""
    original_text: str
    corrected_text: str
    errors: List[GrammarError]
    overall_score: float  # 0.0 to 1.0
    difficulty_level: str
    suggestions: List[str]
    positive_feedback: List[str]


class GrammarAnalyzer:
    """Spanish grammar analyzer with error detection and correction"""
    
    def __init__(self):
        """Initialize grammar analyzer with rules and patterns"""
        self.verb_patterns = self._load_verb_patterns()
        self.noun_patterns = self._load_noun_patterns()
        self.adjective_patterns = self._load_adjective_patterns()
        self.common_errors = self._load_common_error_patterns()
        self.ser_estar_rules = self._load_ser_estar_rules()
        self.subjunctive_triggers = self._load_subjunctive_triggers()
        
    def analyze_text(self, text: str, user_level: str = "intermediate") -> GrammarAnalysis:
        """
        Analyze text for grammar errors and provide corrections
        
        Args:
            text: Spanish text to analyze
            user_level: User's proficiency level
            
        Returns:
            Complete grammar analysis
        """
        errors = []
        corrected_text = text
        
        # Run various error detection methods
        errors.extend(self._check_verb_conjugation(text))
        errors.extend(self._check_gender_agreement(text))
        errors.extend(self._check_number_agreement(text))
        errors.extend(self._check_ser_estar_usage(text))
        errors.extend(self._check_subjunctive_usage(text))
        errors.extend(self._check_preposition_usage(text))
        errors.extend(self._check_article_usage(text))
        errors.extend(self._check_pronoun_placement(text))
        errors.extend(self._check_accent_marks(text))
        errors.extend(self._check_word_order(text))
        errors.extend(self._check_common_misspellings(text))
        
        # Sort errors by position and confidence
        errors.sort(key=lambda e: (e.position[0], -e.confidence))
        
        # Apply corrections to generate corrected text
        corrected_text = self._apply_corrections(text, errors)
        
        # Calculate overall score
        overall_score = self._calculate_grammar_score(text, errors)
        
        # Generate difficulty assessment
        difficulty_level = self._assess_difficulty(text, errors)
        
        # Generate suggestions and positive feedback
        suggestions = self._generate_suggestions(errors, user_level)
        positive_feedback = self._generate_positive_feedback(text, errors, user_level)
        
        return GrammarAnalysis(
            original_text=text,
            corrected_text=corrected_text,
            errors=errors,
            overall_score=overall_score,
            difficulty_level=difficulty_level,
            suggestions=suggestions,
            positive_feedback=positive_feedback
        )
    
    def check_specific_error(self, text: str, error_type: ErrorType) -> List[GrammarError]:
        """Check for a specific type of error"""
        error_methods = {
            ErrorType.VERB_CONJUGATION: self._check_verb_conjugation,
            ErrorType.GENDER_AGREEMENT: self._check_gender_agreement,
            ErrorType.NUMBER_AGREEMENT: self._check_number_agreement,
            ErrorType.SER_ESTAR: self._check_ser_estar_usage,
            ErrorType.SUBJUNCTIVE: self._check_subjunctive_usage,
            ErrorType.PREPOSITION: self._check_preposition_usage,
            ErrorType.ARTICLE_USAGE: self._check_article_usage,
            ErrorType.PRONOUN_PLACEMENT: self._check_pronoun_placement,
            ErrorType.ACCENT_MARKS: self._check_accent_marks,
            ErrorType.WORD_ORDER: self._check_word_order,
            ErrorType.SPELLING: self._check_common_misspellings
        }
        
        method = error_methods.get(error_type)
        if method:
            return method(text)
        return []
    
    def get_error_explanation(self, error_type: ErrorType, context: str = "") -> Dict[str, Any]:
        """Get detailed explanation for an error type"""
        explanations = {
            ErrorType.VERB_CONJUGATION: {
                "title": "Verb Conjugation Error",
                "description": "The verb form doesn't match the subject or tense required",
                "common_causes": [
                    "Incorrect person/number agreement",
                    "Wrong tense selection",
                    "Irregular verb conjugation mistakes"
                ],
                "tips": [
                    "Remember that Spanish verbs change form based on who does the action",
                    "Pay attention to time indicators (ayer, mañana, ahora)",
                    "Practice irregular verbs separately"
                ]
            },
            ErrorType.GENDER_AGREEMENT: {
                "title": "Gender Agreement Error", 
                "description": "Adjectives and articles must match the gender of the noun",
                "common_causes": [
                    "Adjective doesn't match noun gender",
                    "Article doesn't match noun gender",
                    "Confusion about noun gender"
                ],
                "tips": [
                    "Most nouns ending in -a are feminine, -o are masculine",
                    "Learn gender with each new noun",
                    "Adjectives must agree: casa blanca, carro blanco"
                ]
            },
            ErrorType.SER_ESTAR: {
                "title": "Ser vs Estar Usage Error",
                "description": "Incorrect choice between ser and estar verbs",
                "common_causes": [
                    "Using ser for temporary states",
                    "Using estar for permanent characteristics",
                    "Confusion about which situations require which verb"
                ],
                "tips": [
                    "Ser: permanent traits, time, origin, profession",
                    "Estar: location, temporary states, ongoing actions",
                    "Remember PLACE (Position, Location, Action, Condition, Emotion) for estar"
                ]
            }
        }
        
        return explanations.get(error_type, {
            "title": f"{error_type.value.replace('_', ' ').title()} Error",
            "description": "Grammar error detected",
            "common_causes": [],
            "tips": []
        })
    
    def _check_verb_conjugation(self, text: str) -> List[GrammarError]:
        """Check for verb conjugation errors"""
        errors = []
        
        # Common conjugation errors
        conjugation_errors = [
            (r'\byo eres\b', 'yo soy', "First person singular uses 'soy', not 'eres'"),
            (r'\btú es\b', 'tú eres', "Second person singular uses 'eres', not 'es'"),
            (r'\bél tienen\b', 'él tiene', "Third person singular uses 'tiene', not 'tienen'"),
            (r'\bellos tiene\b', 'ellos tienen', "Third person plural uses 'tienen', not 'tiene'"),
            (r'\byo vives\b', 'yo vivo', "First person singular of 'vivir' is 'vivo'"),
            (r'\bnosotros vive\b', 'nosotros vivimos', "First person plural uses 'vivimos'"),
        ]
        
        for pattern, correction, explanation in conjugation_errors:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                incorrect = match.group()
                errors.append(GrammarError(
                    error_type=ErrorType.VERB_CONJUGATION,
                    position=(match.start(), match.end()),
                    incorrect_text=incorrect,
                    suggested_correction=correction,
                    explanation=explanation,
                    confidence=0.9,
                    rule_violated="Subject-verb agreement",
                    examples=[
                        "Yo soy estudiante (I am a student)",
                        "Tú eres inteligente (You are intelligent)",
                        "Él tiene hambre (He is hungry)"
                    ],
                    severity="high"
                ))
        
        return errors
    
    def _check_gender_agreement(self, text: str) -> List[GrammarError]:
        """Check for gender agreement errors"""
        errors = []
        
        # Common gender agreement errors
        gender_errors = [
            (r'\buna problema\b', 'un problema', "'Problema' is masculine despite ending in -a"),
            (r'\bel agua fría\b', 'el agua fría', "Correct - 'agua' uses 'el' but is feminine"),
            (r'\bla mano blanco\b', 'la mano blanca', "'Mano' is feminine, adjective should be 'blanca'"),
            (r'\bun casa\b', 'una casa', "'Casa' is feminine, should use 'una'"),
            (r'\bla carro\b', 'el carro', "'Carro' is masculine, should use 'el'"),
        ]
        
        for pattern, correction, explanation in gender_errors:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                incorrect = match.group()
                errors.append(GrammarError(
                    error_type=ErrorType.GENDER_AGREEMENT,
                    position=(match.start(), match.end()),
                    incorrect_text=incorrect,
                    suggested_correction=correction,
                    explanation=explanation,
                    confidence=0.85,
                    rule_violated="Gender agreement between articles/adjectives and nouns",
                    examples=[
                        "la casa blanca (feminine noun with feminine adjective)",
                        "el carro blanco (masculine noun with masculine adjective)",
                        "un problema grande (masculine noun despite -a ending)"
                    ],
                    severity="medium"
                ))
        
        return errors
    
    def _check_ser_estar_usage(self, text: str) -> List[GrammarError]:
        """Check for ser/estar usage errors"""
        errors = []
        
        # Common ser/estar errors
        ser_estar_errors = [
            (r'\bestoy un estudiante\b', 'soy un estudiante', "Use 'ser' for permanent identity/profession"),
            (r'\bes en Madrid\b', 'está en Madrid', "Use 'estar' for location"),
            (r'\bestá muy inteligente\b', 'es muy inteligente', "Use 'ser' for permanent characteristics"),
            (r'\bsoy cansado\b', 'estoy cansado', "Use 'estar' for temporary states"),
            (r'\beres enojado\b', 'estás enojado', "Use 'estar' for temporary emotions"),
        ]
        
        for pattern, correction, explanation in ser_estar_errors:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                incorrect = match.group()
                errors.append(GrammarError(
                    error_type=ErrorType.SER_ESTAR,
                    position=(match.start(), match.end()),
                    incorrect_text=incorrect,
                    suggested_correction=correction,
                    explanation=explanation,
                    confidence=0.8,
                    rule_violated="Appropriate ser/estar usage",
                    examples=[
                        "Soy profesor (permanent profession)",
                        "Estoy cansado (temporary state)",
                        "Está en casa (location)"
                    ],
                    severity="high"
                ))
        
        return errors
    
    def _check_subjunctive_usage(self, text: str) -> List[GrammarError]:
        """Check for subjunctive mood errors"""
        errors = []
        
        # Subjunctive trigger phrases that should be followed by subjunctive
        subjunctive_triggers = [
            r'\bespero que\b',
            r'\bquiero que\b', 
            r'\bdudo que\b',
            r'\bes importante que\b',
            r'\bes necesario que\b'
        ]
        
        # Look for triggers followed by indicative instead of subjunctive
        for trigger in subjunctive_triggers:
            pattern = f'{trigger}\\s+(\\w+)\\s+(\\w+)'
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                trigger_phrase = match.group().split()[:-1]  # Everything except the verb
                verb = match.group().split()[-1]
                
                # Check if verb looks like indicative (simplified check)
                if verb.lower() in ['tienes', 'tiene', 'comes', 'come', 'vives', 'vive']:
                    subjunctive_form = self._get_subjunctive_form(verb)
                    if subjunctive_form:
                        errors.append(GrammarError(
                            error_type=ErrorType.SUBJUNCTIVE,
                            position=(match.start(), match.end()),
                            incorrect_text=match.group(),
                            suggested_correction=f"{' '.join(trigger_phrase)} {subjunctive_form}",
                            explanation=f"After '{' '.join(trigger_phrase)}', use subjunctive mood",
                            confidence=0.75,
                            rule_violated="Subjunctive after expressions of doubt, emotion, desire",
                            examples=[
                                "Espero que tengas suerte (I hope you have luck)",
                                "Quiero que vengas (I want you to come)",
                                "Dudo que sea verdad (I doubt it's true)"
                            ],
                            severity="medium"
                        ))
        
        return errors
    
    def _check_preposition_usage(self, text: str) -> List[GrammarError]:
        """Check for preposition errors"""
        errors = []
        
        preposition_errors = [
            (r'\bpienso en ti\b', 'pienso en ti', "Correct usage"),
            (r'\bvoy a la escuela\b', 'voy a la escuela', "Correct usage"),
            (r'\bestoy en casa\b', 'estoy en casa', "Correct usage"),
            # Add more specific error patterns based on common mistakes
        ]
        
        return errors
    
    def _check_article_usage(self, text: str) -> List[GrammarError]:
        """Check for article usage errors"""
        errors = []
        
        article_errors = [
            (r'\bel agua\b', 'el agua', "Correct - feminine noun uses 'el' to avoid hiatus"),
            (r'\bla agua\b', 'el agua', "Use 'el' with feminine nouns starting with stressed 'a'"),
        ]
        
        for pattern, correction, explanation in article_errors:
            if pattern != correction:  # Only process actual errors
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    errors.append(GrammarError(
                        error_type=ErrorType.ARTICLE_USAGE,
                        position=(match.start(), match.end()),
                        incorrect_text=match.group(),
                        suggested_correction=correction,
                        explanation=explanation,
                        confidence=0.8,
                        rule_violated="Article usage rules",
                        examples=["el agua fría", "el águila", "el hacha"],
                        severity="medium"
                    ))
        
        return errors
    
    def _check_number_agreement(self, text: str) -> List[GrammarError]:
        """Check for number agreement errors"""
        errors = []
        
        number_errors = [
            (r'\blos casa\b', 'las casas', "Plural article with singular noun"),
            (r'\buna libros\b', 'unos libros', "Singular article with plural noun"),
            (r'\bel niños\b', 'los niños', "Singular article with plural noun"),
        ]
        
        for pattern, correction, explanation in number_errors:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                errors.append(GrammarError(
                    error_type=ErrorType.NUMBER_AGREEMENT,
                    position=(match.start(), match.end()),
                    incorrect_text=match.group(),
                    suggested_correction=correction,
                    explanation=explanation,
                    confidence=0.85,
                    rule_violated="Number agreement between articles and nouns",
                    examples=[
                        "los niños (plural article + plural noun)",
                        "la niña (singular article + singular noun)"
                    ],
                    severity="medium"
                ))
        
        return errors
    
    def _check_pronoun_placement(self, text: str) -> List[GrammarError]:
        """Check for pronoun placement errors"""
        errors = []
        # Implementation for pronoun placement rules
        return errors
    
    def _check_accent_marks(self, text: str) -> List[GrammarError]:
        """Check for missing or incorrect accent marks"""
        errors = []
        
        # Common words that need accents
        accent_corrections = {
            'esta': 'está',  # this/is (context dependent)
            'mas': 'más',    # more
            'si': 'sí',      # yes (context dependent)  
            'tu': 'tú',      # you (context dependent)
            'mi': 'mí',      # me (context dependent)
            'el': 'él',      # he (context dependent)
        }
        
        for incorrect, correct in accent_corrections.items():
            # This would need more sophisticated context analysis
            pattern = f'\\b{incorrect}\\b'
            matches = re.finditer(pattern, text)
            for match in matches:
                # In a real implementation, we'd need context analysis
                # to determine when the accent is actually needed
                pass
        
        return errors
    
    def _check_word_order(self, text: str) -> List[GrammarError]:
        """Check for word order errors"""
        errors = []
        
        # Common word order errors
        word_order_errors = [
            (r'\bgusta me\b', 'me gusta', "Indirect object pronoun comes before verb"),
            (r'\bgustan me\b', 'me gustan', "Indirect object pronoun comes before verb"),
        ]
        
        for pattern, correction, explanation in word_order_errors:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                errors.append(GrammarError(
                    error_type=ErrorType.WORD_ORDER,
                    position=(match.start(), match.end()),
                    incorrect_text=match.group(),
                    suggested_correction=correction,
                    explanation=explanation,
                    confidence=0.9,
                    rule_violated="Spanish word order rules",
                    examples=[
                        "Me gusta la pizza",
                        "Te gustan los libros",
                        "Nos gusta estudiar"
                    ],
                    severity="medium"
                ))
        
        return errors
    
    def _check_common_misspellings(self, text: str) -> List[GrammarError]:
        """Check for common spelling errors"""
        errors = []
        
        common_misspellings = {
            'tambien': 'también',
            'haber': 'haber',  # Context dependent - sometimes should be 'a ver'
            'aver': 'a ver',
            'porque': 'porque',  # Context dependent - sometimes 'por qué'
            'porque': 'por qué',  # When used as question
        }
        
        for incorrect, correct in common_misspellings.items():
            pattern = f'\\b{incorrect}\\b'
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                errors.append(GrammarError(
                    error_type=ErrorType.SPELLING,
                    position=(match.start(), match.end()),
                    incorrect_text=match.group(),
                    suggested_correction=correct,
                    explanation=f"Common misspelling: '{incorrect}' should be '{correct}'",
                    confidence=0.7,
                    rule_violated="Spelling rules",
                    examples=[f"Correct: {correct}"],
                    severity="low"
                ))
        
        return errors
    
    def _apply_corrections(self, text: str, errors: List[GrammarError]) -> str:
        """Apply corrections to generate corrected text"""
        corrected = text
        
        # Sort errors by position (reverse order to maintain positions)
        sorted_errors = sorted(errors, key=lambda e: e.position[0], reverse=True)
        
        for error in sorted_errors:
            if error.confidence >= 0.8:  # Only apply high-confidence corrections
                start, end = error.position
                corrected = corrected[:start] + error.suggested_correction + corrected[end:]
        
        return corrected
    
    def _calculate_grammar_score(self, text: str, errors: List[GrammarError]) -> float:
        """Calculate overall grammar score"""
        if not text.strip():
            return 0.0
        
        # Count words
        word_count = len(text.split())
        
        # Weight errors by severity
        error_weight = 0
        for error in errors:
            if error.severity == "high":
                error_weight += 3
            elif error.severity == "medium":
                error_weight += 2
            else:
                error_weight += 1
        
        # Calculate score (fewer errors = higher score)
        if word_count == 0:
            return 0.0
        
        error_density = error_weight / word_count
        score = max(0.0, 1.0 - error_density * 0.5)  # Scale factor
        
        return min(1.0, score)
    
    def _assess_difficulty(self, text: str, errors: List[GrammarError]) -> str:
        """Assess the difficulty level of the text"""
        word_count = len(text.split())
        error_count = len(errors)
        
        if word_count < 10:
            return "beginner"
        elif word_count < 50:
            if error_count <= 2:
                return "elementary"
            else:
                return "beginner"
        elif word_count < 150:
            if error_count <= 3:
                return "intermediate"
            else:
                return "elementary"
        else:
            if error_count <= 5:
                return "advanced"
            else:
                return "intermediate"
    
    def _generate_suggestions(self, errors: List[GrammarError], user_level: str) -> List[str]:
        """Generate learning suggestions based on errors"""
        suggestions = []
        
        error_types = [error.error_type for error in errors]
        error_counts = {error_type: error_types.count(error_type) for error_type in set(error_types)}
        
        # Most frequent errors first
        sorted_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)
        
        for error_type, count in sorted_errors[:3]:  # Top 3 error types
            if error_type == ErrorType.VERB_CONJUGATION:
                suggestions.append("Practice verb conjugation with regular and irregular verbs")
            elif error_type == ErrorType.GENDER_AGREEMENT:
                suggestions.append("Review gender rules and practice adjective agreement")
            elif error_type == ErrorType.SER_ESTAR:
                suggestions.append("Study the differences between ser and estar with examples")
            elif error_type == ErrorType.SUBJUNCTIVE:
                suggestions.append("Learn subjunctive triggers and practice subjunctive conjugations")
        
        return suggestions
    
    def _generate_positive_feedback(self, text: str, errors: List[GrammarError], user_level: str) -> List[str]:
        """Generate positive feedback"""
        feedback = []
        
        word_count = len(text.split())
        error_count = len(errors)
        
        if error_count == 0:
            feedback.append("¡Excelente! No grammar errors detected.")
        elif error_count <= 2 and word_count >= 20:
            feedback.append("Great job! Very few errors in a substantial piece of text.")
        
        if word_count >= 50:
            feedback.append("Impressive length - you're expressing complex ideas!")
        
        # Check for advanced structures used correctly
        if 'subjuntivo' in text.lower() or any(word in text.lower() for word in ['espero que', 'quiero que', 'dudo que']):
            feedback.append("Good use of advanced grammar structures!")
        
        return feedback
    
    def _get_subjunctive_form(self, indicative_verb: str) -> Optional[str]:
        """Get subjunctive form of indicative verb (simplified)"""
        subjunctive_map = {
            'tienes': 'tengas',
            'tiene': 'tenga',
            'comes': 'comas', 
            'come': 'coma',
            'vives': 'vivas',
            'vive': 'viva'
        }
        
        return subjunctive_map.get(indicative_verb.lower())
    
    def _load_verb_patterns(self) -> Dict[str, Any]:
        """Load verb conjugation patterns"""
        return {}
    
    def _load_noun_patterns(self) -> Dict[str, Any]:
        """Load noun patterns for gender/number"""
        return {}
    
    def _load_adjective_patterns(self) -> Dict[str, Any]:
        """Load adjective agreement patterns"""
        return {}
    
    def _load_common_error_patterns(self) -> List[Tuple[str, str, str]]:
        """Load common error patterns"""
        return []
    
    def _load_ser_estar_rules(self) -> Dict[str, Any]:
        """Load ser/estar usage rules"""
        return {}
    
    def _load_subjunctive_triggers(self) -> List[str]:
        """Load subjunctive trigger phrases"""
        return ['espero que', 'quiero que', 'dudo que', 'es importante que']