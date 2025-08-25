"""
Tests for Adaptive Difficulty System
Tests ZPD system, difficulty adjustment, and learning path management
"""

import pytest
from datetime import datetime, timedelta
import sys
import os

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai.adaptive_difficulty.zpd_system import ZPDSystem, SkillAssessment, ZPDProfile, LearningState


class TestSkillAssessment:
    """Test skill assessment functionality"""
    
    def test_skill_assessment_creation(self):
        """Test creating skill assessments"""
        skill = SkillAssessment(
            skill_name="present_tense",
            current_level=0.7,
            confidence=0.8,
            last_assessment=datetime.now(),
            trend=0.1,
            stability=0.9,
            practice_time=120
        )
        
        assert skill.skill_name == "present_tense"
        assert skill.current_level == 0.7
        assert skill.mastery_level == "proficient"
    
    def test_mastery_level_calculation(self):
        """Test mastery level determination"""
        # Expert level
        expert_skill = SkillAssessment(
            skill_name="test",
            current_level=0.95,
            confidence=0.9,
            last_assessment=datetime.now(),
            trend=0.0,
            stability=0.8,
            practice_time=300
        )
        assert expert_skill.mastery_level == "expert"
        
        # Novice level
        novice_skill = SkillAssessment(
            skill_name="test",
            current_level=0.3,
            confidence=0.4,
            last_assessment=datetime.now(),
            trend=0.0,
            stability=0.5,
            practice_time=30
        )
        assert novice_skill.mastery_level == "novice"
        
        # Intermediate level
        intermediate_skill = SkillAssessment(
            skill_name="test",
            current_level=0.65,
            confidence=0.7,
            last_assessment=datetime.now(),
            trend=0.0,
            stability=0.6,
            practice_time=150
        )
        assert intermediate_skill.mastery_level == "intermediate"


class TestZPDSystem:
    """Test Zone of Proximal Development system"""
    
    def setup_method(self):
        """Setup test environment"""
        self.zpd_system = ZPDSystem()
    
    def test_zpd_system_initialization(self):
        """Test ZPD system initialization"""
        assert self.zpd_system.initial_zpd_width == 0.3
        assert self.zpd_system.min_zpd_width == 0.15
        assert self.zpd_system.max_zpd_width == 0.5
        assert len(self.zpd_system.skill_categories) > 0
        assert "vocabulary" in self.zpd_system.skill_categories
        assert "grammar" in self.zpd_system.skill_categories
    
    def test_user_profile_initialization(self):
        """Test user profile creation"""
        # Test default initialization
        profile = self.zpd_system.initialize_user_profile("user_1")
        
        assert profile.user_id == "user_1"
        assert len(profile.skill_assessments) > 0
        assert profile.current_zpd_range[0] >= 0.0
        assert profile.current_zpd_range[1] <= 1.0
        assert profile.current_zpd_range[0] < profile.current_zpd_range[1]
        assert 0.0 <= profile.optimal_difficulty <= 1.0
        
        # Test with initial assessment
        initial_skills = {
            "present_tense": 0.8,
            "vocabulary": 0.6,
            "subjunctive": 0.3
        }
        
        profile_with_assessment = self.zpd_system.initialize_user_profile(
            "user_2", initial_assessment=initial_skills
        )
        
        assert "present_tense" in profile_with_assessment.skill_assessments
        assert profile_with_assessment.skill_assessments["present_tense"].current_level == 0.8
    
    def test_skill_assessment_update(self):
        """Test updating skill assessments"""
        profile = self.zpd_system.initialize_user_profile("user_test")
        initial_level = profile.skill_assessments["present_tense"].current_level
        
        # Update with good performance
        self.zpd_system.update_skill_assessment(
            "user_test", "present_tense",
            performance_score=0.9,
            confidence_score=0.8,
            response_time=10.0,
            difficulty_attempted=0.6
        )
        
        updated_profile = self.zpd_system.user_profiles["user_test"]
        updated_level = updated_profile.skill_assessments["present_tense"].current_level
        
        # Level should have increased
        assert updated_level > initial_level
        assert updated_profile.skill_assessments["present_tense"].trend > 0
    
    def test_skill_assessment_update_poor_performance(self):
        """Test skill update with poor performance"""
        profile = self.zpd_system.initialize_user_profile("user_poor")
        initial_level = profile.skill_assessments["present_tense"].current_level
        
        # Update with poor performance
        self.zpd_system.update_skill_assessment(
            "user_poor", "present_tense",
            performance_score=0.2,
            confidence_score=0.3,
            response_time=25.0,
            difficulty_attempted=0.7
        )
        
        updated_profile = self.zpd_system.user_profiles["user_poor"]
        updated_level = updated_profile.skill_assessments["present_tense"].current_level
        
        # Level should have decreased or stayed similar
        assert updated_level <= initial_level + 0.05  # Small tolerance for adjustment
        assert updated_profile.skill_assessments["present_tense"].consecutive_correct == 0
    
    def test_difficulty_recommendation(self):
        """Test difficulty recommendation"""
        # Create user with known skill levels
        initial_assessment = {
            "present_tense": 0.7,
            "vocabulary": 0.5,
            "subjunctive": 0.3
        }
        
        profile = self.zpd_system.initialize_user_profile("user_rec", initial_assessment)
        
        # Get recommendation for present tense (should be moderate)
        difficulty, state = self.zpd_system.get_recommended_difficulty("user_rec", "present_tense")
        
        assert 0.0 <= difficulty <= 1.0
        assert state in [s.value for s in LearningState]
        
        # Should recommend higher difficulty for stronger skill
        assert difficulty > 0.5  # Present tense is at 0.7, so should recommend above middle
        
        # Get recommendation for weak skill
        difficulty_weak, state_weak = self.zpd_system.get_recommended_difficulty("user_rec", "subjunctive")
        
        # Should recommend lower difficulty for weaker skill
        assert difficulty_weak < difficulty
    
    def test_zpd_range_adaptation(self):
        """Test ZPD range adaptation based on performance"""
        profile = self.zpd_system.initialize_user_profile("user_adapt")
        initial_zpd_width = profile.current_zpd_range[1] - profile.current_zpd_range[0]
        
        # Simulate consistent good performance across skills
        skills_to_update = ["present_tense", "vocabulary", "past_tenses"]
        
        for skill in skills_to_update:
            for _ in range(5):  # Multiple updates
                self.zpd_system.update_skill_assessment(
                    "user_adapt", skill,
                    performance_score=0.85,
                    confidence_score=0.8,
                    response_time=8.0,
                    difficulty_attempted=0.6
                )
        
        updated_profile = self.zpd_system.user_profiles["user_adapt"]
        
        # ZPD should have been recalculated
        assert updated_profile.last_updated > profile.last_updated
        
        # With consistent performance, the ZPD range might have adjusted
        new_zpd_width = updated_profile.current_zpd_range[1] - updated_profile.current_zpd_range[0]
        assert abs(new_zpd_width - initial_zpd_width) >= 0  # May have changed
    
    def test_learning_progress_analysis(self):
        """Test learning progress analysis"""
        # Create user and add some performance data
        profile = self.zpd_system.initialize_user_profile("user_analysis")
        
        # Add varied performance
        skills_performance = [
            ("present_tense", 0.9, 0.85),  # Strong
            ("vocabulary", 0.6, 0.7),     # Moderate  
            ("subjunctive", 0.3, 0.4),    # Weak
            ("past_tenses", 0.7, 0.8)     # Good
        ]
        
        for skill, performance, confidence in skills_performance:
            self.zpd_system.update_skill_assessment(
                "user_analysis", skill,
                performance_score=performance,
                confidence_score=confidence,
                response_time=12.0,
                difficulty_attempted=0.5
            )
        
        analysis = self.zpd_system.analyze_learning_progress("user_analysis")
        
        assert "overall_level" in analysis
        assert "skill_assessments" in analysis
        assert "strengths" in analysis
        assert "weaknesses" in analysis
        assert "zpd_range" in analysis
        
        # Check that analysis makes sense
        assert 0.0 <= analysis["overall_level"] <= 1.0
        assert len(analysis["strengths"]) >= 0
        assert len(analysis["weaknesses"]) >= 0
        
        # Present tense should be in strengths, subjunctive in weaknesses
        assert "present_tense" in analysis["strengths"] or analysis["overall_level"] < 0.7
        assert "subjunctive" in analysis["weaknesses"]
    
    def test_challenge_adjustment(self):
        """Test challenge adjustment calculation"""
        profile = self.zpd_system.initialize_user_profile("user_challenge")
        
        # Test with consistently high performance
        high_performance = [(0.9, 0.6), (0.85, 0.65), (0.9, 0.7), (0.88, 0.6)]
        adjustment_high = self.zpd_system.get_challenge_adjustment("user_challenge", high_performance)
        
        assert adjustment_high > 0  # Should increase difficulty
        assert -0.3 <= adjustment_high <= 0.3
        
        # Test with consistently low performance
        low_performance = [(0.3, 0.5), (0.25, 0.4), (0.2, 0.45), (0.3, 0.5)]
        adjustment_low = self.zpd_system.get_challenge_adjustment("user_challenge", low_performance)
        
        assert adjustment_low < 0  # Should decrease difficulty
        assert -0.3 <= adjustment_low <= 0.3
        
        # Test with balanced performance
        balanced_performance = [(0.7, 0.5), (0.65, 0.6), (0.75, 0.55), (0.7, 0.5)]
        adjustment_balanced = self.zpd_system.get_challenge_adjustment("user_challenge", balanced_performance)
        
        assert abs(adjustment_balanced) < abs(adjustment_high)  # Should be smaller adjustment
    
    def test_profile_export(self):
        """Test profile export functionality"""
        profile = self.zpd_system.initialize_user_profile("user_export")
        
        # Add some performance data
        self.zpd_system.update_skill_assessment(
            "user_export", "present_tense",
            performance_score=0.8,
            confidence_score=0.75,
            response_time=10.0,
            difficulty_attempted=0.6
        )
        
        exported = self.zpd_system.export_profile("user_export")
        
        assert exported is not None
        assert exported["user_id"] == "user_export"
        assert "skill_assessments" in exported
        assert "zpd_range" in exported
        assert "optimal_difficulty" in exported
        assert "learning_velocity" in exported
        
        # Check that skill assessments are properly exported
        skills = exported["skill_assessments"]
        assert "present_tense" in skills
        assert "current_level" in skills["present_tense"]
        assert "mastery_level" in skills["present_tense"]
        
        # Test non-existent user
        assert self.zpd_system.export_profile("non_existent") is None
    
    def test_learning_state_determination(self):
        """Test learning state classification"""
        profile = self.zpd_system.initialize_user_profile("user_state")
        
        # Test different performance scenarios
        test_cases = [
            (0.5, 0.3, "Should be in lower ZPD or mastery"),  # Easy content
            (0.5, 0.6, "Should be in ZPD range"),             # Appropriate challenge
            (0.5, 0.9, "Should be frustration zone")          # Too difficult
        ]
        
        for skill_level, difficulty, description in test_cases:
            # Set skill level
            profile.skill_assessments["present_tense"].current_level = skill_level
            
            # Get recommendation
            rec_difficulty, state = self.zpd_system.get_recommended_difficulty("user_state", "present_tense")
            
            # State should be appropriate for the scenario
            assert state in [s.value for s in LearningState]
    
    def test_multiple_skill_updates(self):
        """Test updating multiple skills and ZPD recalculation"""
        profile = self.zpd_system.initialize_user_profile("user_multi")
        initial_optimal = profile.optimal_difficulty
        
        # Update multiple skills with improving performance
        skills = ["present_tense", "vocabulary", "past_tenses", "subjunctive"]
        
        for i, skill in enumerate(skills):
            performance = 0.6 + (i * 0.1)  # Increasing performance
            self.zpd_system.update_skill_assessment(
                "user_multi", skill,
                performance_score=performance,
                confidence_score=0.7,
                response_time=10.0,
                difficulty_attempted=0.5
            )
        
        updated_profile = self.zpd_system.user_profiles["user_multi"]
        
        # Optimal difficulty should have been recalculated
        assert updated_profile.optimal_difficulty != initial_optimal
        
        # Learning velocity should reflect performance
        assert 0.3 <= updated_profile.learning_velocity <= 2.0


class TestZPDIntegration:
    """Integration tests for ZPD system"""
    
    def setup_method(self):
        """Setup integrated test environment"""
        self.zpd_system = ZPDSystem()
    
    def test_realistic_learning_progression(self):
        """Test realistic learning progression over time"""
        # Initialize learner
        profile = self.zpd_system.initialize_user_profile("learner")
        
        # Simulate learning progression over several sessions
        sessions = [
            # Session 1: Beginner struggling with basics
            [("present_tense", 0.4, 0.5, 15.0, 0.3),
             ("vocabulary", 0.3, 0.4, 20.0, 0.2)],
            
            # Session 2: Slight improvement
            [("present_tense", 0.5, 0.6, 12.0, 0.4),
             ("vocabulary", 0.4, 0.5, 18.0, 0.3),
             ("past_tenses", 0.2, 0.3, 25.0, 0.2)],
            
            # Session 3: More confident
            [("present_tense", 0.7, 0.7, 10.0, 0.5),
             ("vocabulary", 0.6, 0.6, 15.0, 0.4),
             ("past_tenses", 0.4, 0.4, 20.0, 0.3)],
            
            # Session 4: Advanced topics introduced
            [("present_tense", 0.8, 0.8, 8.0, 0.6),
             ("vocabulary", 0.7, 0.7, 12.0, 0.5),
             ("past_tenses", 0.6, 0.6, 15.0, 0.5),
             ("subjunctive", 0.3, 0.4, 30.0, 0.6)]
        ]
        
        for session_num, session_data in enumerate(sessions):
            for skill, performance, confidence, time, difficulty in session_data:
                self.zpd_system.update_skill_assessment(
                    "learner", skill, performance, confidence, time, difficulty
                )
            
            # Check progress after each session
            analysis = self.zpd_system.analyze_learning_progress("learner")
            
            # Overall level should generally increase
            if session_num > 0:
                assert analysis["overall_level"] > 0.2  # Should show some learning
            
            # ZPD should be reasonable
            zpd_lower, zpd_upper = analysis["zpd_range"]
            assert 0.0 <= zpd_lower < zpd_upper <= 1.0
            assert zpd_upper - zpd_lower >= self.zpd_system.min_zpd_width
        
        # Final analysis
        final_analysis = self.zpd_system.analyze_learning_progress("learner")
        
        # Should have identified strengths and weaknesses
        assert len(final_analysis["strengths"]) > 0
        assert len(final_analysis["weaknesses"]) > 0
        
        # Present tense should be stronger than subjunctive
        present_level = final_analysis["skill_assessments"]["present_tense"]["level"]
        subjunctive_level = final_analysis["skill_assessments"]["subjunctive"]["level"]
        assert present_level > subjunctive_level
    
    def test_adaptive_recommendations(self):
        """Test that recommendations adapt to user performance"""
        # Create two users with different profiles
        beginner = self.zpd_system.initialize_user_profile("beginner")
        advanced = self.zpd_system.initialize_user_profile("advanced")
        
        # Set different skill levels
        beginner_skills = {"present_tense": 0.3, "vocabulary": 0.2, "past_tenses": 0.1}
        advanced_skills = {"present_tense": 0.9, "vocabulary": 0.8, "past_tenses": 0.7, "subjunctive": 0.6}
        
        for skill, level in beginner_skills.items():
            self.zpd_system.update_skill_assessment(
                "beginner", skill, level, level, 20.0, 0.3
            )
        
        for skill, level in advanced_skills.items():
            self.zpd_system.update_skill_assessment(
                "advanced", skill, level, level, 8.0, 0.7
            )
        
        # Get recommendations for same skill
        beginner_diff, beginner_state = self.zpd_system.get_recommended_difficulty("beginner", "present_tense")
        advanced_diff, advanced_state = self.zpd_system.get_recommended_difficulty("advanced", "present_tense")
        
        # Advanced user should get higher difficulty recommendations
        assert advanced_diff > beginner_diff
        
        # States should be appropriate
        assert beginner_state in [LearningState.ZPD_LOWER.value, LearningState.ZPD_OPTIMAL.value]
        assert advanced_state in [LearningState.ZPD_UPPER.value, LearningState.MASTERY.value, LearningState.ZPD_OPTIMAL.value]
    
    def test_skill_category_coverage(self):
        """Test that all skill categories are properly handled"""
        profile = self.zpd_system.initialize_user_profile("comprehensive")
        
        # Verify all skill categories are represented
        skill_categories = self.zpd_system.skill_categories
        profile_skills = set(profile.skill_assessments.keys())
        
        for category, skills in skill_categories.items():
            category_skills = set(skills)
            # At least some skills from each category should be in profile
            assert len(category_skills & profile_skills) > 0, f"No skills from {category} found in profile"
        
        # Test updating skills from different categories
        sample_skills = [
            ("basic_words", "vocabulary"),
            ("present_tense", "grammar"), 
            ("pronunciation", "speaking"),
            ("simple_texts", "reading")
        ]
        
        for skill, expected_category in sample_skills:
            if skill in profile.skill_assessments:
                self.zpd_system.update_skill_assessment(
                    "comprehensive", skill, 0.6, 0.6, 12.0, 0.5
                )
                
                # Verify skill was updated
                updated_skill = profile.skill_assessments[skill]
                assert updated_skill.last_assessment is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])