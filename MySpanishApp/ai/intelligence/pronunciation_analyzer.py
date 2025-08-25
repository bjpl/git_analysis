"""
Pronunciation Analyzer for Spanish Language Learning
Analyzes pronunciation patterns and provides feedback (text-based analysis)
"""

import re
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json


class PronunciationIssue(Enum):
    """Types of pronunciation issues"""
    SILENT_H = "silent_h"
    RR_TRILL = "rr_trill" 
    VOWEL_CLARITY = "vowel_clarity"
    STRESS_PATTERN = "stress_pattern"
    B_V_DISTINCTION = "b_v_distinction"
    CONSONANT_CLUSTERS = "consonant_clusters"
    DIPHTHONGS = "diphthongs"
    LIAISON = "liaison"
    REGIONAL_VARIATION = "regional_variation"


@dataclass
class PronunciationFeedback:
    """Feedback for pronunciation"""
    word: str
    phonetic: str  # IPA or simplified phonetic
    issue_type: PronunciationIssue
    explanation: str
    tip: str
    audio_example: Optional[str] = None  # URL to audio example
    difficulty_level: str = "medium"
    common_for_english: bool = False  # Common issue for English speakers


@dataclass
class PronunciationAnalysis:
    """Complete pronunciation analysis"""
    text: str
    word_count: int
    feedback_items: List[PronunciationFeedback]
    overall_difficulty: str
    pronunciation_score: float
    focus_areas: List[str]
    practice_suggestions: List[str]


class PronunciationAnalyzer:
    """Spanish pronunciation analyzer with feedback generation"""
    
    def __init__(self):
        """Initialize pronunciation analyzer"""
        self.phonetic_rules = self._load_phonetic_rules()
        self.stress_patterns = self._load_stress_patterns()
        self.difficult_sounds = self._load_difficult_sounds()
        self.regional_variations = self._load_regional_variations()
        
    def analyze_text(self, 
                    text: str, 
                    user_native_language: str = "english",
                    target_accent: str = "neutral") -> PronunciationAnalysis:
        """
        Analyze text for pronunciation challenges
        
        Args:
            text: Spanish text to analyze
            user_native_language: User's native language for targeted feedback
            target_accent: Target Spanish accent/region
            
        Returns:
            Pronunciation analysis with feedback
        """
        words = self._extract_words(text)
        feedback_items = []
        
        for word in words:
            word_feedback = self._analyze_word_pronunciation(
                word, user_native_language, target_accent
            )
            feedback_items.extend(word_feedback)
        
        # Calculate overall difficulty and score
        difficulty = self._calculate_pronunciation_difficulty(feedback_items)
        score = self._calculate_pronunciation_score(feedback_items, len(words))
        
        # Generate focus areas and suggestions
        focus_areas = self._identify_focus_areas(feedback_items)
        suggestions = self._generate_practice_suggestions(feedback_items, user_native_language)
        
        return PronunciationAnalysis(
            text=text,
            word_count=len(words),
            feedback_items=feedback_items,
            overall_difficulty=difficulty,
            pronunciation_score=score,
            focus_areas=focus_areas,
            practice_suggestions=suggestions
        )
    
    def analyze_word(self, 
                    word: str, 
                    user_native_language: str = "english") -> List[PronunciationFeedback]:
        """Analyze pronunciation of a single word"""
        return self._analyze_word_pronunciation(word, user_native_language, "neutral")
    
    def get_phonetic_transcription(self, text: str, style: str = "ipa") -> str:
        """
        Get phonetic transcription of text
        
        Args:
            text: Spanish text
            style: 'ipa' for International Phonetic Alphabet, 'simple' for simplified
            
        Returns:
            Phonetic transcription
        """
        words = self._extract_words(text)
        transcriptions = []
        
        for word in words:
            if style == "ipa":
                transcription = self._get_ipa_transcription(word)
            else:
                transcription = self._get_simple_transcription(word)
            
            transcriptions.append(transcription)
        
        return " ".join(transcriptions)
    
    def get_stress_analysis(self, word: str) -> Dict[str, Any]:
        """Analyze stress pattern of a word"""
        syllables = self._divide_syllables(word)
        stress_position = self._find_stress_position(word, syllables)
        
        return {
            "word": word,
            "syllables": syllables,
            "syllable_count": len(syllables),
            "stress_position": stress_position,
            "stress_type": self._classify_stress_type(word, stress_position),
            "pronunciation_tip": self._get_stress_tip(word, stress_position)
        }
    
    def get_minimal_pairs(self, target_sound: str) -> List[Tuple[str, str]]:
        """Get minimal pairs for practicing specific sounds"""
        minimal_pairs = {
            "rr": [
                ("pero", "perro"), ("caro", "carro"), ("para", "parra"),
                ("cero", "cerro"), ("coral", "corral")
            ],
            "b_v": [
                ("vaca", "baca"), ("tubo", "tuvo"), ("cava", "caba"),
                ("vino", "bino"), ("ave", "abe")
            ],
            "d": [
                ("nada", "nata"), ("todo", "toto"), ("cada", "cata"),
                ("donde", "tonte"), ("verdad", "vertat")
            ]
        }
        
        return minimal_pairs.get(target_sound, [])
    
    def generate_pronunciation_exercises(self, 
                                       focus_sounds: List[str],
                                       difficulty_level: str = "intermediate") -> List[Dict[str, Any]]:
        """Generate pronunciation exercises for specific sounds"""
        exercises = []
        
        for sound in focus_sounds:
            if sound == "rr":
                exercises.append({
                    "type": "minimal_pairs",
                    "sound": sound,
                    "title": "Rolling R (RR) Practice",
                    "pairs": self.get_minimal_pairs("rr"),
                    "instructions": "Practice the difference between single R and rolled RR",
                    "tip": "Touch tongue tip to roof of mouth and blow air to create vibration"
                })
            
            elif sound == "vowels":
                exercises.append({
                    "type": "vowel_clarity",
                    "sound": sound,
                    "title": "Spanish Vowel Clarity",
                    "words": ["casa", "mesa", "piso", "poco", "luna"],
                    "instructions": "Practice pure vowel sounds - avoid English diphthongs",
                    "tip": "Spanish vowels are crisp and don't glide like English vowels"
                })
            
            elif sound == "stress":
                exercises.append({
                    "type": "stress_practice",
                    "sound": sound,
                    "title": "Word Stress Practice",
                    "word_groups": [
                        {"pattern": "última", "words": ["médico", "rápido", "teléfono"]},
                        {"pattern": "penúltima", "words": ["casa", "mesa", "amigo"]},
                        {"pattern": "antepenúltima", "words": ["música", "película", "gramática"]}
                    ],
                    "instructions": "Practice stress patterns in Spanish words",
                    "tip": "Most Spanish words stress the second-to-last syllable"
                })
        
        return exercises
    
    def _analyze_word_pronunciation(self, 
                                  word: str, 
                                  native_language: str, 
                                  target_accent: str) -> List[PronunciationFeedback]:
        """Analyze pronunciation challenges for a single word"""
        feedback = []
        
        # Check for silent H
        if word.lower().startswith('h'):
            feedback.append(PronunciationFeedback(
                word=word,
                phonetic=self._get_simple_transcription(word),
                issue_type=PronunciationIssue.SILENT_H,
                explanation=f"The 'h' in '{word}' is silent in Spanish",
                tip="Don't pronounce the 'h' sound - it's completely silent",
                difficulty_level="easy",
                common_for_english=True
            ))
        
        # Check for RR sound
        if 'rr' in word.lower() or word.lower().startswith('r'):
            feedback.append(PronunciationFeedback(
                word=word,
                phonetic=self._get_simple_transcription(word),
                issue_type=PronunciationIssue.RR_TRILL,
                explanation=f"'{word}' contains the rolled 'rr' or initial 'r' sound",
                tip="Roll your tongue by touching the tip to the roof of your mouth and blowing air",
                difficulty_level="hard",
                common_for_english=True
            ))
        
        # Check for B/V distinction (or lack thereof)
        if 'b' in word.lower() or 'v' in word.lower():
            feedback.append(PronunciationFeedback(
                word=word,
                phonetic=self._get_simple_transcription(word),
                issue_type=PronunciationIssue.B_V_DISTINCTION,
                explanation=f"In '{word}', both 'b' and 'v' are pronounced the same",
                tip="Both letters make a soft 'b' sound, like 'b' in 'able'",
                difficulty_level="medium",
                common_for_english=True
            ))
        
        # Check stress patterns
        stress_analysis = self.get_stress_analysis(word)
        if len(word) > 2:  # Only for longer words
            feedback.append(PronunciationFeedback(
                word=word,
                phonetic=self._get_simple_transcription(word),
                issue_type=PronunciationIssue.STRESS_PATTERN,
                explanation=f"'{word}' is stressed on syllable {stress_analysis['stress_position']}: {'-'.join(stress_analysis['syllables'])}",
                tip=stress_analysis['pronunciation_tip'],
                difficulty_level="medium",
                common_for_english=native_language == "english"
            ))
        
        # Check for diphthongs
        diphthongs = self._find_diphthongs(word)
        if diphthongs:
            for diphthong in diphthongs:
                feedback.append(PronunciationFeedback(
                    word=word,
                    phonetic=self._get_simple_transcription(word),
                    issue_type=PronunciationIssue.DIPHTHONGS,
                    explanation=f"'{word}' contains the diphthong '{diphthong}'",
                    tip=f"Pronounce '{diphthong}' as a smooth glide between vowels",
                    difficulty_level="medium",
                    common_for_english=True
                ))
        
        # Check for consonant clusters
        clusters = self._find_consonant_clusters(word)
        if clusters:
            for cluster in clusters:
                feedback.append(PronunciationFeedback(
                    word=word,
                    phonetic=self._get_simple_transcription(word),
                    issue_type=PronunciationIssue.CONSONANT_CLUSTERS,
                    explanation=f"'{word}' contains the consonant cluster '{cluster}'",
                    tip=f"Practice the '{cluster}' sound combination slowly, then speed up",
                    difficulty_level="medium",
                    common_for_english=native_language == "english"
                ))
        
        return feedback
    
    def _extract_words(self, text: str) -> List[str]:
        """Extract words from text"""
        # Remove punctuation and split
        words = re.findall(r'\b[a-záéíóúüñ]+\b', text.lower())
        return [word for word in words if len(word) > 1]  # Filter out single letters
    
    def _get_ipa_transcription(self, word: str) -> str:
        """Get IPA transcription (simplified mapping)"""
        # This is a simplified version - a real implementation would need
        # a comprehensive phonetic dictionary
        ipa_map = {
            'a': 'a', 'e': 'e', 'i': 'i', 'o': 'o', 'u': 'u',
            'j': 'x', 'g': 'g', 'ñ': 'ɲ', 'rr': 'r', 'r': 'ɾ',
            'll': 'ʎ', 'ch': 'tʃ', 'qu': 'k', 'c': 'k'
        }
        
        # Simple character-by-character mapping
        result = ""
        i = 0
        while i < len(word):
            if i < len(word) - 1:
                two_char = word[i:i+2]
                if two_char in ipa_map:
                    result += ipa_map[two_char]
                    i += 2
                    continue
            
            if word[i] in ipa_map:
                result += ipa_map[word[i]]
            else:
                result += word[i]
            i += 1
        
        return f"/{result}/"
    
    def _get_simple_transcription(self, word: str) -> str:
        """Get simplified phonetic transcription"""
        # Simplified phonetic representation for learners
        transcription = word
        
        # Basic transformations
        transcription = re.sub(r'h', '', transcription)  # Silent h
        transcription = re.sub(r'qu', 'k', transcription)  # qu -> k
        transcription = re.sub(r'c([ie])', r's\1', transcription)  # ce, ci -> se, si
        transcription = re.sub(r'z', 's', transcription)  # z -> s (Latin American)
        transcription = re.sub(r'j', 'h', transcription)  # j -> h sound
        transcription = re.sub(r'g([ie])', r'h\1', transcription)  # ge, gi -> he, hi
        transcription = re.sub(r'll', 'y', transcription)  # ll -> y
        transcription = re.sub(r'ñ', 'ny', transcription)  # ñ -> ny
        
        return transcription
    
    def _divide_syllables(self, word: str) -> List[str]:
        """Divide word into syllables (simplified algorithm)"""
        # This is a simplified syllable division - real Spanish syllabification
        # requires more complex rules
        
        vowels = 'aeiouáéíóúü'
        syllables = []
        current_syllable = ""
        
        for i, char in enumerate(word.lower()):
            current_syllable += char
            
            # If current char is vowel and next is consonant, or end of word
            if char in vowels:
                # Look ahead
                if i == len(word) - 1:  # End of word
                    syllables.append(current_syllable)
                    break
                elif i < len(word) - 1:
                    next_char = word[i + 1].lower()
                    if next_char not in vowels:  # Consonant follows
                        # Check if we should break here or continue
                        if i < len(word) - 2:
                            char_after_next = word[i + 2].lower()
                            if char_after_next in vowels:  # CV pattern ahead
                                syllables.append(current_syllable)
                                current_syllable = ""
        
        # Handle any remaining syllable
        if current_syllable:
            if syllables:
                syllables[-1] += current_syllable
            else:
                syllables.append(current_syllable)
        
        return syllables if syllables else [word]
    
    def _find_stress_position(self, word: str, syllables: List[str]) -> int:
        """Find stressed syllable position"""
        # Check for written accent
        for i, syllable in enumerate(syllables):
            if any(accent in syllable for accent in 'áéíóú'):
                return i + 1  # 1-indexed
        
        # Apply default stress rules
        if word.endswith(('a', 'e', 'i', 'o', 'u', 'n', 's')):
            # Stress on second-to-last syllable
            return max(1, len(syllables) - 1)
        else:
            # Stress on last syllable
            return len(syllables)
    
    def _classify_stress_type(self, word: str, stress_position: int) -> str:
        """Classify stress type"""
        syllable_count = len(self._divide_syllables(word))
        
        if stress_position == syllable_count:
            return "aguda" if stress_position > 1 else "monosílaba"
        elif stress_position == syllable_count - 1:
            return "grave/llana"
        elif stress_position == syllable_count - 2:
            return "esdrújula"
        else:
            return "sobresdrújula"
    
    def _get_stress_tip(self, word: str, stress_position: int) -> str:
        """Get pronunciation tip for stress"""
        syllables = self._divide_syllables(word)
        stressed_syllable = syllables[stress_position - 1] if stress_position <= len(syllables) else syllables[-1]
        
        return f"Emphasize the syllable '{stressed_syllable}' in '{word}'"
    
    def _find_diphthongs(self, word: str) -> List[str]:
        """Find diphthongs in word"""
        diphthongs = []
        weak_vowels = 'iu'
        strong_vowels = 'aeo'
        
        i = 0
        while i < len(word) - 1:
            current = word[i].lower()
            next_char = word[i + 1].lower()
            
            # Check for diphthong patterns
            if ((current in weak_vowels and next_char in strong_vowels) or
                (current in strong_vowels and next_char in weak_vowels) or
                (current in weak_vowels and next_char in weak_vowels)):
                diphthongs.append(current + next_char)
                i += 2
            else:
                i += 1
        
        return diphthongs
    
    def _find_consonant_clusters(self, word: str) -> List[str]:
        """Find consonant clusters that might be difficult"""
        clusters = []
        consonants = 'bcdfghjklmnpqrstvwxyz'
        
        i = 0
        while i < len(word) - 1:
            current = word[i].lower()
            next_char = word[i + 1].lower()
            
            if current in consonants and next_char in consonants:
                cluster = current + next_char
                # Check for common difficult clusters
                if cluster in ['pr', 'pl', 'br', 'bl', 'tr', 'dr', 'cr', 'cl', 'fr', 'fl', 'gr', 'gl']:
                    clusters.append(cluster)
                i += 2
            else:
                i += 1
        
        return clusters
    
    def _calculate_pronunciation_difficulty(self, feedback_items: List[PronunciationFeedback]) -> str:
        """Calculate overall pronunciation difficulty"""
        if not feedback_items:
            return "easy"
        
        difficulty_scores = {
            "easy": 1,
            "medium": 2,
            "hard": 3
        }
        
        total_score = sum(difficulty_scores.get(item.difficulty_level, 2) for item in feedback_items)
        average_score = total_score / len(feedback_items)
        
        if average_score <= 1.3:
            return "easy"
        elif average_score <= 2.3:
            return "medium"
        else:
            return "hard"
    
    def _calculate_pronunciation_score(self, feedback_items: List[PronunciationFeedback], word_count: int) -> float:
        """Calculate pronunciation score (0-1)"""
        if word_count == 0:
            return 1.0
        
        # Count challenging sounds
        challenging_count = sum(1 for item in feedback_items if item.difficulty_level in ["medium", "hard"])
        
        # Calculate score
        difficulty_ratio = challenging_count / word_count
        score = max(0.0, 1.0 - difficulty_ratio * 0.3)  # Max 30% penalty
        
        return min(1.0, score)
    
    def _identify_focus_areas(self, feedback_items: List[PronunciationFeedback]) -> List[str]:
        """Identify main areas to focus on"""
        issue_counts = {}
        for item in feedback_items:
            issue_type = item.issue_type.value
            issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
        
        # Sort by frequency and return top 3
        sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
        return [issue for issue, count in sorted_issues[:3]]
    
    def _generate_practice_suggestions(self, 
                                     feedback_items: List[PronunciationFeedback],
                                     native_language: str) -> List[str]:
        """Generate practice suggestions"""
        suggestions = []
        
        issue_types = [item.issue_type for item in feedback_items]
        
        if PronunciationIssue.RR_TRILL in issue_types:
            suggestions.append("Practice rolling R with tongue twisters: 'Erre con erre cigarro'")
        
        if PronunciationIssue.VOWEL_CLARITY in issue_types:
            suggestions.append("Practice pure Spanish vowels - avoid English diphthongs")
        
        if PronunciationIssue.STRESS_PATTERN in issue_types:
            suggestions.append("Listen to native speakers and mark stress patterns in new words")
        
        if PronunciationIssue.SILENT_H in issue_types:
            suggestions.append("Remember that H is always silent in Spanish")
        
        if native_language == "english":
            suggestions.append("Focus on rhythm - Spanish has more syllable-timed rhythm than English")
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def _load_phonetic_rules(self) -> Dict[str, Any]:
        """Load phonetic transformation rules"""
        return {}
    
    def _load_stress_patterns(self) -> Dict[str, Any]:
        """Load stress pattern rules"""
        return {}
    
    def _load_difficult_sounds(self) -> Dict[str, Any]:
        """Load information about difficult sounds"""
        return {}
    
    def _load_regional_variations(self) -> Dict[str, Any]:
        """Load regional pronunciation variations"""
        return {}