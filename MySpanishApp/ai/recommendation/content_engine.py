"""
Content Recommendation Engine
Analyzes user performance and recommends personalized learning content
"""

from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics
import math

from ..adaptive_difficulty.zpd_system import ZPDSystem, SkillAssessment
from ..spaced_repetition.performance_tracker import PerformanceTracker


@dataclass
class ContentItem:
    """Represents a piece of learning content"""
    content_id: str
    content_type: str  # vocabulary, grammar, exercise, etc.
    difficulty_level: float  # 0.0 to 1.0
    skills_addressed: List[str]
    prerequisites: List[str] = field(default_factory=list)
    estimated_time_minutes: int = 15
    engagement_score: float = 0.7
    cultural_content: bool = False
    topics: List[str] = field(default_factory=list)
    
    @property
    def complexity_score(self) -> float:
        """Calculate complexity based on multiple factors"""
        base_complexity = self.difficulty_level
        skill_complexity = len(self.skills_addressed) * 0.1
        prerequisite_complexity = len(self.prerequisites) * 0.05
        return min(1.0, base_complexity + skill_complexity + prerequisite_complexity)


@dataclass
class RecommendationScore:
    """Scoring for a content recommendation"""
    content_item: ContentItem
    total_score: float
    components: Dict[str, float] = field(default_factory=dict)
    reasoning: List[str] = field(default_factory=list)
    urgency: float = 0.5
    
    @property
    def priority_score(self) -> float:
        """Calculate priority combining score and urgency"""
        return self.total_score * (1 + self.urgency)


class ContentRecommendationEngine:
    """Intelligent content recommendation engine"""
    
    def __init__(self, 
                 zpd_system: Optional[ZPDSystem] = None,
                 performance_tracker: Optional[PerformanceTracker] = None):
        """
        Initialize recommendation engine
        
        Args:
            zpd_system: ZPD system for difficulty assessment
            performance_tracker: Performance tracker for user analytics
        """
        self.zpd_system = zpd_system or ZPDSystem()
        self.performance_tracker = performance_tracker or PerformanceTracker()
        
        # Content database (in practice, this would be loaded from database)
        self.content_database: Dict[str, ContentItem] = {}
        self.user_preferences: Dict[str, Dict[str, Any]] = {}
        self.content_interactions: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        # Recommendation weights
        self.scoring_weights = {
            'difficulty_match': 0.25,
            'skill_relevance': 0.20,
            'weakness_targeting': 0.20,
            'spaced_repetition': 0.15,
            'variety': 0.10,
            'engagement': 0.10
        }
        
        # Initialize with some example content
        self._initialize_sample_content()
    
    def add_content_item(self, content_item: ContentItem) -> None:
        """Add content item to the database"""
        self.content_database[content_item.content_id] = content_item
    
    def get_recommendations(self, 
                          user_id: str,
                          num_recommendations: int = 10,
                          session_length_minutes: int = 30,
                          content_types: Optional[List[str]] = None) -> List[RecommendationScore]:
        """
        Get personalized content recommendations
        
        Args:
            user_id: User identifier
            num_recommendations: Number of recommendations to return
            session_length_minutes: Target session length
            content_types: Filter by content types
            
        Returns:
            List of recommended content with scores
        """
        # Get user profile and performance data
        user_analysis = self._analyze_user_needs(user_id)
        
        # Score all available content
        scored_recommendations = []
        
        for content_id, content_item in self.content_database.items():
            # Filter by content type if specified
            if content_types and content_item.content_type not in content_types:
                continue
            
            # Skip if user has recently completed this content
            if self._recently_completed(user_id, content_id, days=3):
                continue
            
            # Check prerequisites
            if not self._prerequisites_met(user_id, content_item.prerequisites):
                continue
            
            score = self._score_content_item(user_id, content_item, user_analysis)
            scored_recommendations.append(score)
        
        # Sort by priority score
        scored_recommendations.sort(key=lambda x: x.priority_score, reverse=True)
        
        # Select recommendations considering session length and variety
        selected = self._select_optimal_set(
            scored_recommendations, 
            num_recommendations,
            session_length_minutes
        )
        
        return selected
    
    def get_weakness_focused_recommendations(self, 
                                          user_id: str,
                                          num_recommendations: int = 5) -> List[RecommendationScore]:
        """Get recommendations focused on user's weakest skills"""
        user_analysis = self._analyze_user_needs(user_id)
        
        # Focus on weakest skills
        weak_skills = user_analysis['weakest_skills'][:3]  # Top 3 weaknesses
        
        recommendations = []
        for content_id, content_item in self.content_database.items():
            # Check if content addresses weak skills
            skill_overlap = set(content_item.skills_addressed) & set(weak_skills)
            if not skill_overlap:
                continue
            
            score = self._score_content_item(user_id, content_item, user_analysis)
            # Boost score for weakness targeting
            score.components['weakness_boost'] = len(skill_overlap) * 0.3
            score.total_score += score.components['weakness_boost']
            score.reasoning.append(f"Targets weak skills: {', '.join(skill_overlap)}")
            
            recommendations.append(score)
        
        recommendations.sort(key=lambda x: x.priority_score, reverse=True)
        return recommendations[:num_recommendations]
    
    def get_review_recommendations(self, 
                                 user_id: str,
                                 num_recommendations: int = 8) -> List[RecommendationScore]:
        """Get recommendations for spaced repetition review"""
        # Get items due for review from spaced repetition system
        # This would integrate with the review scheduler
        
        user_analysis = self._analyze_user_needs(user_id)
        
        # Find content that hasn't been reviewed recently
        recommendations = []
        
        for content_id, content_item in self.content_database.items():
            last_interaction = self._get_last_interaction(user_id, content_id)
            
            if last_interaction:
                days_since = (datetime.now() - last_interaction['timestamp']).days
                performance = last_interaction.get('performance', 0.5)
                
                # Calculate review urgency based on forgetting curve
                if days_since >= 1:  # At least 1 day old
                    forgetting_factor = math.exp(-0.1 * days_since)  # Simple forgetting curve
                    review_urgency = (1 - performance) * (1 - forgetting_factor)
                    
                    score = self._score_content_item(user_id, content_item, user_analysis)
                    score.urgency = review_urgency
                    score.components['review_urgency'] = review_urgency * 0.4
                    score.total_score += score.components['review_urgency']
                    score.reasoning.append(f"Due for review (last seen {days_since} days ago)")
                    
                    recommendations.append(score)
        
        recommendations.sort(key=lambda x: x.priority_score, reverse=True)
        return recommendations[:num_recommendations]
    
    def get_progressive_recommendations(self, 
                                     user_id: str,
                                     skill_area: str,
                                     num_recommendations: int = 5) -> List[RecommendationScore]:
        """Get progressive recommendations for a specific skill area"""
        user_analysis = self._analyze_user_needs(user_id)
        current_level = user_analysis['skill_levels'].get(skill_area, 0.3)
        
        # Find content that progressively builds the skill
        relevant_content = [
            item for item in self.content_database.values()
            if skill_area in item.skills_addressed
        ]
        
        # Sort by difficulty and select appropriate progression
        relevant_content.sort(key=lambda x: x.difficulty_level)
        
        recommendations = []
        target_difficulties = [
            current_level - 0.1,  # Review level
            current_level,        # Current level
            current_level + 0.1,  # Slight challenge
            current_level + 0.2,  # Moderate challenge
            current_level + 0.3   # High challenge
        ]
        
        for target_diff in target_difficulties:
            best_match = min(
                relevant_content,
                key=lambda x: abs(x.difficulty_level - target_diff),
                default=None
            )
            
            if best_match and best_match.content_id not in [r.content_item.content_id for r in recommendations]:
                score = self._score_content_item(user_id, best_match, user_analysis)
                score.components['progression_fit'] = 0.3
                score.total_score += 0.3
                score.reasoning.append(f"Progressive difficulty for {skill_area}")
                
                recommendations.append(score)
        
        return recommendations[:num_recommendations]
    
    def record_content_interaction(self, 
                                 user_id: str,
                                 content_id: str,
                                 interaction_type: str,
                                 performance_score: float,
                                 time_spent_minutes: int,
                                 engagement_score: float = None) -> None:
        """Record user interaction with content"""
        interaction = {
            'timestamp': datetime.now(),
            'content_id': content_id,
            'interaction_type': interaction_type,
            'performance': performance_score,
            'time_spent': time_spent_minutes,
            'engagement': engagement_score
        }
        
        self.content_interactions[user_id].append(interaction)
        
        # Update content item engagement score
        if content_id in self.content_database and engagement_score is not None:
            content_item = self.content_database[content_id]
            # Exponential moving average
            alpha = 0.1
            content_item.engagement_score = (1 - alpha) * content_item.engagement_score + alpha * engagement_score
    
    def get_content_analytics(self, content_id: str) -> Dict[str, Any]:
        """Get analytics for specific content"""
        interactions = []
        for user_interactions in self.content_interactions.values():
            interactions.extend([i for i in user_interactions if i['content_id'] == content_id])
        
        if not interactions:
            return {'error': 'No interaction data found'}
        
        performances = [i['performance'] for i in interactions]
        time_spent = [i['time_spent'] for i in interactions]
        engagements = [i['engagement'] for i in interactions if i['engagement'] is not None]
        
        return {
            'total_interactions': len(interactions),
            'average_performance': statistics.mean(performances),
            'average_time_spent': statistics.mean(time_spent),
            'average_engagement': statistics.mean(engagements) if engagements else None,
            'completion_rate': len([i for i in interactions if i['interaction_type'] == 'completed']) / len(interactions),
            'difficulty_rating': self.content_database[content_id].difficulty_level if content_id in self.content_database else None
        }
    
    def update_user_preferences(self, 
                              user_id: str, 
                              preferences: Dict[str, Any]) -> None:
        """Update user preferences"""
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {}
        
        self.user_preferences[user_id].update(preferences)
    
    def _analyze_user_needs(self, user_id: str) -> Dict[str, Any]:
        """Analyze user needs and current state"""
        # Get ZPD analysis
        zpd_analysis = self.zpd_system.analyze_learning_progress(user_id)
        
        # Get performance trends
        performance_report = self.performance_tracker.generate_performance_report()
        
        # Analyze recent interactions
        recent_interactions = self._get_recent_interactions(user_id, days=7)
        
        # Content type preferences
        content_type_preferences = Counter([
            i['content_id'].split('_')[0] for i in recent_interactions
            if '_' in i['content_id']
        ])
        
        # Skill levels from ZPD system
        skill_levels = {}
        if 'skill_assessments' in zpd_analysis:
            skill_levels = {
                skill: assessment['level']
                for skill, assessment in zpd_analysis['skill_assessments'].items()
            }
        
        return {
            'skill_levels': skill_levels,
            'strengths': zpd_analysis.get('strengths', []),
            'weaknesses': zpd_analysis.get('weaknesses', []),
            'weakest_skills': zpd_analysis.get('weaknesses', [])[:5],
            'improving_skills': zpd_analysis.get('improving_skills', []),
            'declining_skills': zpd_analysis.get('declining_skills', []),
            'learning_velocity': zpd_analysis.get('learning_velocity', 1.0),
            'optimal_difficulty': zpd_analysis.get('optimal_difficulty', 0.5),
            'zpd_range': zpd_analysis.get('zpd_range', (0.3, 0.7)),
            'content_preferences': dict(content_type_preferences.most_common()),
            'recent_performance': statistics.mean([i['performance'] for i in recent_interactions]) if recent_interactions else 0.5,
            'session_preferences': self.user_preferences.get(user_id, {})
        }
    
    def _score_content_item(self, 
                          user_id: str, 
                          content_item: ContentItem,
                          user_analysis: Dict[str, Any]) -> RecommendationScore:
        """Score a content item for recommendation"""
        score = RecommendationScore(
            content_item=content_item,
            total_score=0.0,
            components={},
            reasoning=[]
        )
        
        # 1. Difficulty match score
        optimal_difficulty = user_analysis['optimal_difficulty']
        difficulty_diff = abs(content_item.difficulty_level - optimal_difficulty)
        difficulty_score = max(0, 1 - difficulty_diff * 2)  # Penalty for mismatch
        
        score.components['difficulty_match'] = difficulty_score * self.scoring_weights['difficulty_match']
        if difficulty_diff < 0.1:
            score.reasoning.append("Perfect difficulty match")
        elif difficulty_diff < 0.2:
            score.reasoning.append("Good difficulty match")
        
        # 2. Skill relevance score
        user_skills = set(user_analysis['skill_levels'].keys())
        content_skills = set(content_item.skills_addressed)
        skill_overlap = len(user_skills & content_skills)
        skill_relevance = skill_overlap / max(len(content_skills), 1)
        
        score.components['skill_relevance'] = skill_relevance * self.scoring_weights['skill_relevance']
        if skill_overlap > 0:
            score.reasoning.append(f"Addresses {skill_overlap} relevant skills")
        
        # 3. Weakness targeting score
        weaknesses = set(user_analysis['weakest_skills'])
        weakness_overlap = len(weaknesses & content_skills)
        weakness_score = weakness_overlap / max(len(weaknesses), 1)
        
        score.components['weakness_targeting'] = weakness_score * self.scoring_weights['weakness_targeting']
        if weakness_overlap > 0:
            score.reasoning.append(f"Targets {weakness_overlap} weak areas")
        
        # 4. Spaced repetition score
        last_interaction = self._get_last_interaction(user_id, content_item.content_id)
        if last_interaction:
            days_since = (datetime.now() - last_interaction['timestamp']).days
            # Optimal review timing based on performance
            last_performance = last_interaction.get('performance', 0.5)
            optimal_days = 1 + (last_performance * 7)  # 1-8 days based on performance
            timing_score = max(0, 1 - abs(days_since - optimal_days) / optimal_days)
        else:
            timing_score = 0.8  # New content gets high score
        
        score.components['spaced_repetition'] = timing_score * self.scoring_weights['spaced_repetition']
        
        # 5. Variety score
        recent_types = [self.content_database[i['content_id']].content_type 
                       for i in self._get_recent_interactions(user_id, days=3)
                       if i['content_id'] in self.content_database]
        
        type_frequency = recent_types.count(content_item.content_type)
        variety_score = max(0, 1 - type_frequency * 0.2)  # Penalty for repetition
        
        score.components['variety'] = variety_score * self.scoring_weights['variety']
        if type_frequency == 0:
            score.reasoning.append("Provides content variety")
        
        # 6. Engagement score
        score.components['engagement'] = content_item.engagement_score * self.scoring_weights['engagement']
        
        # Calculate total score
        score.total_score = sum(score.components.values())
        
        # Apply user preference bonuses
        preferences = user_analysis.get('session_preferences', {})
        if 'preferred_types' in preferences:
            if content_item.content_type in preferences['preferred_types']:
                score.total_score += 0.1
                score.reasoning.append("Matches user preferences")
        
        # Cultural content bonus if user is interested
        if content_item.cultural_content and preferences.get('cultural_interest', False):
            score.total_score += 0.05
            score.reasoning.append("Includes cultural content")
        
        return score
    
    def _select_optimal_set(self, 
                          scored_recommendations: List[RecommendationScore],
                          num_recommendations: int,
                          session_length_minutes: int) -> List[RecommendationScore]:
        """Select optimal set of recommendations considering constraints"""
        selected = []
        total_time = 0
        content_types_selected = set()
        
        for recommendation in scored_recommendations:
            if len(selected) >= num_recommendations:
                break
            
            # Check time constraint
            estimated_time = recommendation.content_item.estimated_time_minutes
            if total_time + estimated_time > session_length_minutes * 1.2:  # 20% buffer
                continue
            
            # Ensure variety in content types
            content_type = recommendation.content_item.content_type
            if len(content_types_selected) >= 3 and content_type in content_types_selected:
                continue
            
            selected.append(recommendation)
            total_time += estimated_time
            content_types_selected.add(content_type)
        
        return selected
    
    def _recently_completed(self, user_id: str, content_id: str, days: int = 3) -> bool:
        """Check if content was recently completed"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for interaction in self.content_interactions.get(user_id, []):
            if (interaction['content_id'] == content_id and 
                interaction['interaction_type'] == 'completed' and
                interaction['timestamp'] > cutoff_date):
                return True
        
        return False
    
    def _prerequisites_met(self, user_id: str, prerequisites: List[str]) -> bool:
        """Check if prerequisites are met"""
        if not prerequisites:
            return True
        
        # Check if user has completed prerequisite content
        completed_content = set()
        for interaction in self.content_interactions.get(user_id, []):
            if interaction['interaction_type'] == 'completed':
                completed_content.add(interaction['content_id'])
        
        return all(prereq in completed_content for prereq in prerequisites)
    
    def _get_recent_interactions(self, user_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get recent user interactions"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        return [
            interaction for interaction in self.content_interactions.get(user_id, [])
            if interaction['timestamp'] > cutoff_date
        ]
    
    def _get_last_interaction(self, user_id: str, content_id: str) -> Optional[Dict[str, Any]]:
        """Get last interaction with specific content"""
        interactions = [
            i for i in self.content_interactions.get(user_id, [])
            if i['content_id'] == content_id
        ]
        
        return max(interactions, key=lambda x: x['timestamp']) if interactions else None
    
    def _initialize_sample_content(self) -> None:
        """Initialize with sample content items"""
        sample_content = [
            ContentItem("vocab_basic_family", "vocabulary", 0.2, ["basic_words"], [], 10, 0.8, False, ["family"]),
            ContentItem("vocab_advanced_emotions", "vocabulary", 0.7, ["advanced_words"], ["vocab_basic_emotions"], 15, 0.7, False, ["emotions"]),
            ContentItem("grammar_present_tense", "grammar", 0.3, ["present_tense"], [], 20, 0.8, False, ["verbs"]),
            ContentItem("grammar_subjunctive_intro", "grammar", 0.8, ["subjunctive"], ["grammar_present_tense", "grammar_past_tenses"], 25, 0.6, False, ["advanced_grammar"]),
            ContentItem("exercise_conjugation", "exercise", 0.4, ["present_tense", "past_tenses"], ["grammar_present_tense"], 15, 0.7, False, ["practice"]),
            ContentItem("conversation_restaurant", "conversation", 0.5, ["speaking", "vocabulary"], ["vocab_basic_food"], 20, 0.9, True, ["dining", "culture"]),
            ContentItem("story_family_traditions", "story", 0.6, ["reading", "culture"], ["vocab_basic_family"], 18, 0.8, True, ["family", "traditions"]),
        ]
        
        for item in sample_content:
            self.add_content_item(item)