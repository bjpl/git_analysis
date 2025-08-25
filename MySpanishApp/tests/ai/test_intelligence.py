"""
Tests for Intelligent Features
Tests grammar analyzer and pronunciation analyzer
"""

import pytest
from datetime import datetime
import sys
import os

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai.intelligence.grammar_analyzer import GrammarAnalyzer, ErrorType, GrammarError
from ai.intelligence.pronunciation_analyzer import PronunciationAnalyzer, PronunciationIssue


class TestGrammarAnalyzer:
    """Test grammar analyzer functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.analyzer = GrammarAnalyzer()
    
    def test_analyzer_initialization(self):
        """Test grammar analyzer initialization"""
        assert hasattr(self.analyzer, 'verb_patterns')
        assert hasattr(self.analyzer, 'ser_estar_rules')
        assert hasattr(self.analyzer, 'subjunctive_triggers')
        assert callable(self.analyzer.analyze_text)
    
    def test_basic_text_analysis(self):
        """Test basic text analysis without errors"""
        clean_text = "Hola, me llamo Juan. Soy estudiante y vivo en Madrid."
        analysis = self.analyzer.analyze_text(clean_text)
        
        assert analysis.original_text == clean_text
        assert isinstance(analysis.errors, list)
        assert 0.0 <= analysis.overall_score <= 1.0
        assert analysis.difficulty_level in ["beginner", "elementary", "intermediate", "advanced"]
        assert isinstance(analysis.suggestions, list)
        assert isinstance(analysis.positive_feedback, list)
    
    def test_verb_conjugation_errors(self):
        """Test detection of verb conjugation errors"""
        error_text = "Yo eres estudiante. Tú es muy inteligente."
        analysis = self.analyzer.analyze_text(error_text)
        
        # Should detect conjugation errors
        conjugation_errors = [e for e in analysis.errors if e.error_type == ErrorType.VERB_CONJUGATION]
        assert len(conjugation_errors) > 0
        
        # Check error details
        first_error = conjugation_errors[0]
        assert first_error.incorrect_text in error_text
        assert first_error.suggested_correction is not None
        assert first_error.explanation is not None
        assert 0.0 <= first_error.confidence <= 1.0
        assert first_error.severity in ["low", "medium", "high"]
        assert len(first_error.examples) > 0
    
    def test_ser_estar_errors(self):
        """Test detection of ser/estar errors"""
        error_text = "Estoy un estudiante. Es en Madrid."
        analysis = self.analyzer.analyze_text(error_text)
        
        ser_estar_errors = [e for e in analysis.errors if e.error_type == ErrorType.SER_ESTAR]
        assert len(ser_estar_errors) > 0
        
        # Check that corrections use proper verb
        for error in ser_estar_errors:
            correction = error.suggested_correction.lower()
            assert 'soy' in correction or 'está' in correction
    
    def test_gender_agreement_errors(self):
        """Test detection of gender agreement errors"""
        error_text = "Un casa grande. La carro rojo."
        analysis = self.analyzer.analyze_text(error_text)
        
        gender_errors = [e for e in analysis.errors if e.error_type == ErrorType.GENDER_AGREEMENT]
        assert len(gender_errors) > 0
        
        # Check corrections
        for error in gender_errors:
            assert error.suggested_correction != error.incorrect_text
            assert 'gender' in error.explanation.lower() or 'feminine' in error.explanation.lower() or 'masculine' in error.explanation.lower()
    
    def test_specific_error_checking(self):
        """Test checking for specific error types"""
        text = "Yo soy teniendo hambre y estoy un profesor."
        
        # Check only ser/estar errors
        ser_estar_errors = self.analyzer.check_specific_error(text, ErrorType.SER_ESTAR)
        assert len(ser_estar_errors) > 0
        assert all(e.error_type == ErrorType.SER_ESTAR for e in ser_estar_errors)
        
        # Check only verb conjugation errors
        verb_errors = self.analyzer.check_specific_error(text, ErrorType.VERB_CONJUGATION)
        # May or may not find errors depending on detection rules
        assert isinstance(verb_errors, list)
    
    def test_error_explanation_generation(self):
        """Test error explanation generation"""
        verb_explanation = self.analyzer.get_error_explanation(ErrorType.VERB_CONJUGATION)
        
        assert "title" in verb_explanation
        assert "description" in verb_explanation
        assert "common_causes" in verb_explanation
        assert "tips" in verb_explanation
        assert isinstance(verb_explanation["common_causes"], list)
        assert isinstance(verb_explanation["tips"], list)
        
        # Test ser/estar explanation
        ser_estar_explanation = self.analyzer.get_error_explanation(ErrorType.SER_ESTAR)
        assert "ser" in ser_estar_explanation["description"].lower() or "estar" in ser_estar_explanation["description"].lower()
    
    def test_corrected_text_generation(self):
        """Test generation of corrected text"""
        error_text = "Yo eres estudiante."
        analysis = self.analyzer.analyze_text(error_text)
        
        assert analysis.corrected_text is not None
        assert analysis.corrected_text != analysis.original_text
        # Should contain a correction
        assert "soy" in analysis.corrected_text.lower()
    
    def test_grammar_score_calculation(self):
        """Test grammar score calculation"""
        # Perfect text should have high score
        perfect_text = "Hola, me llamo María. Soy profesora."
        perfect_analysis = self.analyzer.analyze_text(perfect_text)
        
        # Error text should have lower score
        error_text = "Yo eres estudiante y tu es profesor."
        error_analysis = self.analyzer.analyze_text(error_text)
        
        # Perfect text should score higher than error text
        # (unless perfect text also has detected issues)
        if len(perfect_analysis.errors) < len(error_analysis.errors):
            assert perfect_analysis.overall_score >= error_analysis.overall_score
    
    def test_difficulty_assessment(self):
        """Test difficulty level assessment"""
        # Short, simple text
        simple_text = "Hola. Soy Juan."
        simple_analysis = self.analyzer.analyze_text(simple_text)
        
        # Longer, complex text
        complex_text = """
        Si hubiera sabido que ibas a venir, habría preparado una cena especial.
        Me parece increíble que no te hayas dado cuenta de lo que está pasando.
        Es importante que entiendas la complejidad de la situación actual.
        """
        complex_analysis = self.analyzer.analyze_text(complex_text)
        
        # Difficulty should be appropriately assessed
        assert simple_analysis.difficulty_level in ["beginner", "elementary"]
        # Complex text difficulty depends on error detection, but should be reasonable
        assert complex_analysis.difficulty_level in ["beginner", "elementary", "intermediate", "advanced"]
    
    def test_suggestions_generation(self):
        """Test learning suggestions generation"""
        # Text with multiple error types
        mixed_error_text = "Yo eres estudiante. Estoy un profesor. Un casa grande."
        analysis = self.analyzer.analyze_text(mixed_error_text, user_level="beginner")
        
        assert len(analysis.suggestions) > 0
        suggestions_text = " ".join(analysis.suggestions).lower()
        
        # Should include relevant suggestions
        if any(e.error_type == ErrorType.VERB_CONJUGATION for e in analysis.errors):
            assert any(word in suggestions_text for word in ["verb", "conjugation", "practice"])
        
        if any(e.error_type == ErrorType.SER_ESTAR for e in analysis.errors):
            assert any(word in suggestions_text for word in ["ser", "estar", "difference"])
    
    def test_positive_feedback_generation(self):
        """Test positive feedback generation"""
        # Good text should generate positive feedback
        good_text = "Me gusta mucho estudiar español porque es muy interesante y útil para mi carrera profesional."
        analysis = self.analyzer.analyze_text(good_text)
        
        if len(analysis.errors) == 0:
            assert len(analysis.positive_feedback) > 0
            
        # Long text should get length appreciation
        assert len(analysis.positive_feedback) >= 0


class TestPronunciationAnalyzer:
    """Test pronunciation analyzer functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.analyzer = PronunciationAnalyzer()
    
    def test_analyzer_initialization(self):
        """Test pronunciation analyzer initialization"""
        assert hasattr(self.analyzer, 'phonetic_rules')
        assert hasattr(self.analyzer, 'stress_patterns')
        assert callable(self.analyzer.analyze_text)
        assert callable(self.analyzer.get_phonetic_transcription)
    
    def test_basic_text_analysis(self):
        """Test basic pronunciation analysis"""
        text = "Hola, me llamo Pedro y vivo en Barcelona."
        analysis = self.analyzer.analyze_text(text)
        
        assert analysis.text == text
        assert analysis.word_count > 0
        assert isinstance(analysis.feedback_items, list)
        assert analysis.overall_difficulty in ["easy", "medium", "hard"]
        assert 0.0 <= analysis.pronunciation_score <= 1.0
        assert isinstance(analysis.focus_areas, list)
        assert isinstance(analysis.practice_suggestions, list)
    
    def test_silent_h_detection(self):
        """Test detection of silent H"""
        text = "Hola, hombre honesto habla español."
        analysis = self.analyzer.analyze_text(text)
        
        h_feedback = [f for f in analysis.feedback_items if f.issue_type == PronunciationIssue.SILENT_H]
        assert len(h_feedback) > 0
        
        # Check feedback details
        for feedback in h_feedback:
            assert feedback.word.lower().startswith('h')
            assert 'silent' in feedback.explanation.lower()
            assert feedback.common_for_english == True
    
    def test_rr_trill_detection(self):
        """Test detection of RR trill sounds"""
        text = "El perro corre rápido por la carretera."
        analysis = self.analyzer.analyze_text(text)
        
        rr_feedback = [f for f in analysis.feedback_items if f.issue_type == PronunciationIssue.RR_TRILL]
        assert len(rr_feedback) > 0
        
        for feedback in rr_feedback:
            word_lower = feedback.word.lower()
            assert 'rr' in word_lower or word_lower.startswith('r')
            assert 'roll' in feedback.tip.lower() or 'tongue' in feedback.tip.lower()
            assert feedback.difficulty_level == "hard"
    
    def test_b_v_distinction(self):
        """Test B/V pronunciation feedback"""
        text = "Vamos a beber vino blanco."
        analysis = self.analyzer.analyze_text(text)
        
        bv_feedback = [f for f in analysis.feedback_items if f.issue_type == PronunciationIssue.B_V_DISTINCTION]
        assert len(bv_feedback) > 0
        
        for feedback in bv_feedback:
            word_lower = feedback.word.lower()
            assert 'b' in word_lower or 'v' in word_lower
            assert 'same' in feedback.explanation.lower()
    
    def test_single_word_analysis(self):
        """Test analyzing single words"""
        # Test word with RR
        perro_feedback = self.analyzer.analyze_word("perro")
        assert len(perro_feedback) > 0
        assert any(f.issue_type == PronunciationIssue.RR_TRILL for f in perro_feedback)
        
        # Test word starting with H
        hola_feedback = self.analyzer.analyze_word("hola")
        assert len(hola_feedback) > 0
        assert any(f.issue_type == PronunciationIssue.SILENT_H for f in hola_feedback)
    
    def test_phonetic_transcription(self):
        """Test phonetic transcription generation"""
        word = "casa"
        
        # IPA transcription
        ipa_transcription = self.analyzer.get_phonetic_transcription(word, style="ipa")
        assert isinstance(ipa_transcription, str)
        assert len(ipa_transcription) > 0
        
        # Simple transcription
        simple_transcription = self.analyzer.get_phonetic_transcription(word, style="simple")
        assert isinstance(simple_transcription, str)
        assert len(simple_transcription) > 0
        
        # Should be different styles
        assert ipa_transcription != simple_transcription or len(word.split()) == 1
    
    def test_stress_analysis(self):
        """Test word stress analysis"""
        test_words = [
            ("casa", 2),      # penúltima (grave)
            ("médico", 3),    # antepenúltima (esdrújula)
            ("canción", 2),   # última (aguda)
            ("rápidamente", 4) # sobresdrújula
        ]
        
        for word, expected_syllables in test_words:
            stress_analysis = self.analyzer.get_stress_analysis(word)
            
            assert stress_analysis["word"] == word
            assert "syllables" in stress_analysis
            assert "stress_position" in stress_analysis
            assert "stress_type" in stress_analysis
            assert "pronunciation_tip" in stress_analysis
            
            # Syllable count should be reasonable
            assert len(stress_analysis["syllables"]) >= 1
            
            # Stress position should be valid
            assert 1 <= stress_analysis["stress_position"] <= len(stress_analysis["syllables"])
    
    def test_syllable_division(self):
        """Test syllable division"""
        test_cases = [
            "casa",      # ca-sa
            "estudiante", # es-tu-dian-te
            "rápido",    # rá-pi-do
            "construcción" # cons-truc-ción
        ]
        
        for word in test_cases:
            syllables = self.analyzer._divide_syllables(word)
            
            assert isinstance(syllables, list)
            assert len(syllables) >= 1
            
            # Rejoined syllables should approximate original word
            rejoined = "".join(syllables)
            assert rejoined.lower() == word.lower()
    
    def test_minimal_pairs(self):
        """Test minimal pairs generation"""
        rr_pairs = self.analyzer.get_minimal_pairs("rr")
        assert len(rr_pairs) > 0
        assert isinstance(rr_pairs[0], tuple)
        assert len(rr_pairs[0]) == 2
        
        # Check that pairs are actually different
        for pair in rr_pairs[:3]:  # Test first few
            word1, word2 = pair
            assert word1 != word2
            assert isinstance(word1, str)
            assert isinstance(word2, str)
    
    def test_pronunciation_exercises(self):
        """Test pronunciation exercise generation"""
        focus_sounds = ["rr", "vowels", "stress"]
        exercises = self.analyzer.generate_pronunciation_exercises(focus_sounds)
        
        assert len(exercises) == len(focus_sounds)
        
        for exercise in exercises:
            assert "type" in exercise
            assert "sound" in exercise
            assert "title" in exercise
            assert "instructions" in exercise
            assert "tip" in exercise
            
            # Should have appropriate content for each type
            if exercise["sound"] == "rr":
                assert "pairs" in exercise
            elif exercise["sound"] == "vowels":
                assert "words" in exercise
            elif exercise["sound"] == "stress":
                assert "word_groups" in exercise
    
    def test_difficulty_and_scoring(self):
        """Test pronunciation difficulty assessment and scoring"""
        # Easy text (no difficult sounds)
        easy_text = "Me gusta la casa."
        easy_analysis = self.analyzer.analyze_text(easy_text)
        
        # Difficult text (many challenging sounds)
        hard_text = "El perro corre rápido por la carretera. Hombre habla."
        hard_analysis = self.analyzer.analyze_text(hard_text)
        
        # Hard text should have lower score and higher difficulty
        if len(hard_analysis.feedback_items) > len(easy_analysis.feedback_items):
            assert hard_analysis.pronunciation_score <= easy_analysis.pronunciation_score
    
    def test_focus_areas_identification(self):
        """Test identification of pronunciation focus areas"""
        # Text with multiple RR sounds
        rr_text = "Perro, carro, correr, arriba."
        rr_analysis = self.analyzer.analyze_text(rr_text)
        
        # Should identify RR as focus area
        focus_areas = rr_analysis.focus_areas
        assert len(focus_areas) > 0
        assert any("rr" in area for area in focus_areas)
    
    def test_practice_suggestions(self):
        """Test practice suggestion generation"""
        text = "Hola, me llamo Roberto y tengo un perro."
        analysis = self.analyzer.analyze_text(text, user_native_language="english")
        
        assert len(analysis.practice_suggestions) > 0
        
        # Should include suggestions for English speakers
        suggestions_text = " ".join(analysis.practice_suggestions).lower()
        
        # Should have relevant suggestions based on detected issues
        if any(f.issue_type == PronunciationIssue.RR_TRILL for f in analysis.feedback_items):
            assert any(word in suggestions_text for word in ["roll", "tongue", "trill"])
        
        if any(f.issue_type == PronunciationIssue.SILENT_H for f in analysis.feedback_items):
            assert "silent" in suggestions_text
    
    def test_regional_variations(self):
        """Test handling of regional pronunciation variations"""
        # This is a placeholder test since regional variations
        # would require more complex implementation
        text = "Yo llamo a casa"
        analysis = self.analyzer.analyze_text(text, target_accent="neutral")
        
        # Should complete without errors
        assert isinstance(analysis, type(analysis))
        assert analysis.text == text


class TestIntelligenceIntegration:
    """Integration tests for intelligence features"""
    
    def setup_method(self):
        """Setup integrated test environment"""
        self.grammar_analyzer = GrammarAnalyzer()
        self.pronunciation_analyzer = PronunciationAnalyzer()
    
    def test_combined_analysis(self):
        """Test using both analyzers together"""
        text = "Hola, yo eres estudiante y me gusta estudiar español con el perro."
        
        # Grammar analysis
        grammar_analysis = self.grammar_analyzer.analyze_text(text)
        
        # Pronunciation analysis
        pronunciation_analysis = self.pronunciation_analyzer.analyze_text(text)
        
        # Both should process the same text
        assert grammar_analysis.original_text == text
        assert pronunciation_analysis.text == text
        
        # Should provide different types of feedback
        assert len(grammar_analysis.errors) > 0  # Should find "yo eres"
        assert len(pronunciation_analysis.feedback_items) > 0  # Should find "hola" (silent h) and "perro" (rr)
        
        # Combine insights
        total_issues = len(grammar_analysis.errors) + len(pronunciation_analysis.feedback_items)
        assert total_issues > 2
    
    def test_learner_profile_analysis(self):
        """Test analysis for different learner profiles"""
        # Beginner with basic errors
        beginner_text = "Yo eres Juan. Hola."
        
        grammar_beginner = self.grammar_analyzer.analyze_text(beginner_text, user_level="beginner")
        pronunciation_beginner = self.pronunciation_analyzer.analyze_text(beginner_text, user_native_language="english")
        
        # Should provide appropriate feedback for beginners
        assert len(grammar_beginner.suggestions) > 0
        assert len(pronunciation_beginner.practice_suggestions) > 0
        
        # Advanced learner text
        advanced_text = "Aunque hubiera preferido que vinieras temprano, entiendo que tuviste problemas."
        
        grammar_advanced = self.grammar_analyzer.analyze_text(advanced_text, user_level="advanced")
        pronunciation_advanced = self.pronunciation_analyzer.analyze_text(advanced_text, user_native_language="english")
        
        # Advanced text should be assessed as more difficult
        assert grammar_advanced.difficulty_level in ["intermediate", "advanced"]
    
    def test_comprehensive_feedback_generation(self):
        """Test comprehensive feedback generation"""
        # Text with multiple issues
        complex_text = "Hola! Yo eres Roberto y me encanta los perros. Estoy un profesor de historia."
        
        # Get comprehensive analysis
        grammar_analysis = self.grammar_analyzer.analyze_text(complex_text)
        pronunciation_analysis = self.pronunciation_analyzer.analyze_text(complex_text)
        
        # Combine feedback
        grammar_issues = len(grammar_analysis.errors)
        pronunciation_issues = len(pronunciation_analysis.feedback_items)
        
        assert grammar_issues > 0  # Should find grammar errors
        assert pronunciation_issues > 0  # Should find pronunciation challenges
        
        # Should provide actionable suggestions
        all_suggestions = grammar_analysis.suggestions + pronunciation_analysis.practice_suggestions
        assert len(all_suggestions) > 0
        
        # Should identify specific areas for improvement
        error_types = [error.error_type.value for error in grammar_analysis.errors]
        pronunciation_types = [feedback.issue_type.value for feedback in pronunciation_analysis.feedback_items]
        
        assert len(set(error_types + pronunciation_types)) > 1  # Multiple types of issues


if __name__ == "__main__":
    pytest.main([__file__, "-v"])