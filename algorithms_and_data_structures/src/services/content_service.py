"""
Content Service - Business logic for content operations
Manages problems, concepts, explanations, and content delivery.
"""

import json
import random
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import asdict
from datetime import datetime, timedelta

from models.content_models import Problem, Concept, Topic, QuizQuestion
from models.user_profile import UserProfile, UserProgress
from data.database_manager import DatabaseManager
from utils.logging_config import get_logger


class ContentService:
    """
    Service for managing educational content including problems,
    concepts, explanations, and content delivery strategies.
    """
    
    def __init__(self, db_manager: DatabaseManager, config: Dict[str, Any]):
        """
        Initialize the content service.
        
        Args:
            db_manager: Database manager instance
            config: Application configuration
        """
        self.db_manager = db_manager
        self.config = config
        self.logger = get_logger(__name__)
        
        # Content generation settings
        self.default_problem_count = config.get('default_problem_count', 10)
        self.max_problem_attempts = config.get('max_problem_attempts', 3)
        self.quiz_question_types = config.get('quiz_question_types', 
                                            ['multiple_choice', 'true_false', 'fill_blank', 'code_completion'])
        
        self.logger.info("Content service initialized")
    
    def get_topic_content(self, topic_name: str, 
                         difficulty: Optional[str] = None) -> Optional[Topic]:
        """
        Get complete topic content including problems and concepts.
        
        Args:
            topic_name: Name of the topic
            difficulty: Optional difficulty filter
            
        Returns:
            Topic with all content or None if not found
        """
        try:
            topic = self.db_manager.get_topic_by_name(topic_name)
            if not topic:
                self.logger.warning(f"Topic not found: {topic_name}")
                return None
            
            # Filter by difficulty if specified
            if difficulty and topic.difficulty != difficulty:
                self.logger.info(f"Topic '{topic_name}' difficulty mismatch: {topic.difficulty} != {difficulty}")
                return None
            
            # Load complete content
            topic.problems = self.db_manager.get_problems_for_topic(topic_name)
            topic.concepts = self.db_manager.get_concepts_for_topic(topic_name)
            
            self.logger.info(f"Loaded topic '{topic_name}' with {len(topic.problems)} problems and {len(topic.concepts)} concepts")
            return topic
            
        except Exception as e:
            self.logger.error(f"Failed to get topic content for '{topic_name}': {str(e)}")
            return None
    
    def get_practice_problems(self, topic: Optional[str] = None,
                            difficulty: Optional[str] = None,
                            count: int = None,
                            user_profile: Optional[UserProfile] = None) -> List[Problem]:
        """
        Get practice problems based on criteria and user preferences.
        
        Args:
            topic: Topic name filter
            difficulty: Difficulty level filter
            count: Number of problems to return
            user_profile: User profile for personalization
            
        Returns:
            List of practice problems
        """
        try:
            count = count or self.default_problem_count
            
            # Get problems from database
            problems = self.db_manager.get_problems(
                topic=topic,
                difficulty=difficulty,
                limit=count * 3  # Get more than needed for filtering
            )
            
            if not problems:
                self.logger.warning(f"No problems found for topic='{topic}', difficulty='{difficulty}'")
                return []
            
            # Apply user-based filtering and selection
            if user_profile:
                problems = self._personalize_problem_selection(problems, user_profile)
            
            # Select final set of problems
            selected_problems = self._select_diverse_problems(problems, count)
            
            self.logger.info(f"Selected {len(selected_problems)} practice problems")
            return selected_problems
            
        except Exception as e:
            self.logger.error(f"Failed to get practice problems: {str(e)}")
            return []
    
    def get_problem_by_id(self, problem_id: str) -> Optional[Problem]:
        """
        Get a specific problem by ID.
        
        Args:
            problem_id: Problem identifier
            
        Returns:
            Problem if found, None otherwise
        """
        try:
            problem = self.db_manager.get_problem_by_id(problem_id)
            if problem:
                self.logger.info(f"Retrieved problem: {problem.title}")
            else:
                self.logger.warning(f"Problem not found: {problem_id}")
            return problem
            
        except Exception as e:
            self.logger.error(f"Failed to get problem '{problem_id}': {str(e)}")
            return None
    
    def get_concept_explanation(self, concept_name: str, 
                              user_level: str = 'intermediate') -> Optional[Concept]:
        """
        Get concept explanation adapted to user level.
        
        Args:
            concept_name: Name of the concept
            user_level: User's understanding level
            
        Returns:
            Concept with appropriate explanation
        """
        try:
            concept = self.db_manager.get_concept_by_name(concept_name)
            if not concept:
                self.logger.warning(f"Concept not found: {concept_name}")
                return None
            
            # Adapt explanation to user level
            adapted_concept = self._adapt_concept_to_level(concept, user_level)
            
            self.logger.info(f"Retrieved concept explanation: {concept_name}")
            return adapted_concept
            
        except Exception as e:
            self.logger.error(f"Failed to get concept explanation for '{concept_name}': {str(e)}")
            return None
    
    def generate_quiz_questions(self, topic: Optional[str] = None,
                              count: int = 10,
                              user_profile: Optional[UserProfile] = None) -> List[QuizQuestion]:
        """
        Generate quiz questions for assessment.
        
        Args:
            topic: Topic name filter
            count: Number of questions
            user_profile: User profile for personalization
            
        Returns:
            List of quiz questions
        """
        try:
            # Get content for questions
            if topic:
                topic_content = self.get_topic_content(topic)
                if not topic_content:
                    return []
                concepts = topic_content.concepts
                problems = topic_content.problems
            else:
                # Get mixed content from user's progress
                concepts = self._get_concepts_for_quiz(user_profile)
                problems = self._get_problems_for_quiz(user_profile)
            
            # Generate questions
            questions = []
            question_types = self.quiz_question_types.copy()
            
            for i in range(count):
                question_type = random.choice(question_types)
                
                if question_type == 'multiple_choice' and concepts:
                    question = self._generate_multiple_choice_question(concepts)
                elif question_type == 'true_false' and concepts:
                    question = self._generate_true_false_question(concepts)
                elif question_type == 'fill_blank' and concepts:
                    question = self._generate_fill_blank_question(concepts)
                elif question_type == 'code_completion' and problems:
                    question = self._generate_code_completion_question(problems)
                else:
                    # Fallback to multiple choice
                    if concepts:
                        question = self._generate_multiple_choice_question(concepts)
                    else:
                        continue
                
                if question:
                    questions.append(question)
            
            self.logger.info(f"Generated {len(questions)} quiz questions")
            return questions
            
        except Exception as e:
            self.logger.error(f"Failed to generate quiz questions: {str(e)}")
            return []
    
    def search_content(self, query: str, search_type: str = 'all',
                      user_profile: Optional[UserProfile] = None) -> Dict[str, List]:
        """
        Search for content based on query.
        
        Args:
            query: Search query
            search_type: Type of content to search ('all', 'topics', 'problems', 'concepts')
            user_profile: User profile for personalized results
            
        Returns:
            Dictionary with search results by type
        """
        try:
            results = {}
            
            if search_type in ['all', 'topics']:
                topics = self.db_manager.search_topics(query)
                results['topics'] = [topic.name for topic in topics]
            
            if search_type in ['all', 'problems']:
                problems = self.db_manager.search_problems(query)
                results['problems'] = [problem.title for problem in problems]
            
            if search_type in ['all', 'concepts']:
                concepts = self.db_manager.search_concepts(query)
                results['concepts'] = [concept.name for concept in concepts]
            
            # Apply user-based ranking if profile available
            if user_profile:
                results = self._rank_search_results(results, user_profile)
            
            total_results = sum(len(items) for items in results.values())
            self.logger.info(f"Search for '{query}' returned {total_results} results")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to search content: {str(e)}")
            return {}
    
    def get_content_recommendations(self, user_profile: UserProfile,
                                  recommendation_type: str = 'next_steps') -> List[Dict[str, Any]]:
        """
        Get content recommendations for a user.
        
        Args:
            user_profile: User profile
            recommendation_type: Type of recommendations ('next_steps', 'review', 'challenge')
            
        Returns:
            List of content recommendations
        """
        try:
            recommendations = []
            
            if recommendation_type == 'next_steps':
                recommendations = self._get_next_step_recommendations(user_profile)
            elif recommendation_type == 'review':
                recommendations = self._get_review_recommendations(user_profile)
            elif recommendation_type == 'challenge':
                recommendations = self._get_challenge_recommendations(user_profile)
            
            self.logger.info(f"Generated {len(recommendations)} '{recommendation_type}' recommendations")
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Failed to get content recommendations: {str(e)}")
            return []
    
    def validate_solution(self, problem_id: str, solution: str,
                         user_profile: Optional[UserProfile] = None) -> Dict[str, Any]:
        """
        Validate a solution to a problem.
        
        Args:
            problem_id: Problem identifier
            solution: User's solution
            user_profile: User profile for personalized feedback
            
        Returns:
            Validation result with feedback
        """
        try:
            problem = self.get_problem_by_id(problem_id)
            if not problem:
                return {'valid': False, 'error': 'Problem not found'}
            
            # Basic validation logic (would be more sophisticated in practice)
            validation_result = {
                'valid': False,
                'score': 0,
                'feedback': [],
                'hints': [],
                'next_steps': []
            }
            
            # Placeholder validation logic
            # In a real implementation, this would run test cases, check syntax, etc.
            if solution.strip():
                validation_result['valid'] = True
                validation_result['score'] = 75  # Placeholder score
                validation_result['feedback'].append("Solution submitted successfully")
            else:
                validation_result['feedback'].append("Solution is empty")
            
            self.logger.info(f"Validated solution for problem {problem_id}")
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Failed to validate solution: {str(e)}")
            return {'valid': False, 'error': str(e)}
    
    def get_problem_hints(self, problem_id: str, user_profile: Optional[UserProfile] = None) -> List[str]:
        """
        Get progressive hints for a problem.
        
        Args:
            problem_id: Problem identifier
            user_profile: User profile for personalized hints
            
        Returns:
            List of hints
        """
        try:
            problem = self.get_problem_by_id(problem_id)
            if not problem:
                return []
            
            hints = problem.hints.copy() if problem.hints else []
            
            # Personalize hints based on user profile
            if user_profile:
                hints = self._personalize_hints(hints, user_profile)
            
            self.logger.info(f"Retrieved {len(hints)} hints for problem {problem_id}")
            return hints
            
        except Exception as e:
            self.logger.error(f"Failed to get problem hints: {str(e)}")
            return []
    
    def _personalize_problem_selection(self, problems: List[Problem], 
                                     user_profile: UserProfile) -> List[Problem]:
        """Personalize problem selection based on user profile."""
        # Filter based on user's progress and preferences
        if hasattr(user_profile, 'progress') and user_profile.progress:
            # Avoid recently solved problems
            recently_solved = set(user_profile.progress.recent_problems)
            problems = [p for p in problems if p.id not in recently_solved]
            
            # Prefer topics user is currently working on
            current_topics = set(user_profile.progress.current_topics)
            if current_topics:
                topic_problems = [p for p in problems if p.topic in current_topics]
                if topic_problems:
                    problems = topic_problems
        
        return problems
    
    def _select_diverse_problems(self, problems: List[Problem], count: int) -> List[Problem]:
        """Select a diverse set of problems."""
        if len(problems) <= count:
            return problems
        
        # Group by difficulty and topic for diversity
        grouped = {}
        for problem in problems:
            key = (problem.difficulty, problem.topic)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(problem)
        
        # Select problems ensuring diversity
        selected = []
        groups = list(grouped.keys())
        group_index = 0
        
        while len(selected) < count and any(grouped.values()):
            group_key = groups[group_index % len(groups)]
            if grouped[group_key]:
                selected.append(grouped[group_key].pop(0))
            group_index += 1
        
        # Fill remaining slots randomly if needed
        remaining_problems = [p for group in grouped.values() for p in group]
        while len(selected) < count and remaining_problems:
            selected.append(remaining_problems.pop(random.randint(0, len(remaining_problems) - 1)))
        
        return selected[:count]
    
    def _adapt_concept_to_level(self, concept: Concept, user_level: str) -> Concept:
        """Adapt concept explanation to user level."""
        # Create a copy with level-appropriate explanation
        adapted_concept = Concept(
            name=concept.name,
            description=concept.description,
            topic=concept.topic,
            difficulty=concept.difficulty,
            examples=concept.examples,
            related_concepts=concept.related_concepts
        )
        
        # Modify explanation based on level
        if user_level == 'beginner':
            # Simplify explanation
            adapted_concept.description = self._simplify_explanation(concept.description)
        elif user_level == 'advanced':
            # Add more technical details
            adapted_concept.description = self._enhance_explanation(concept.description)
        
        return adapted_concept
    
    def _simplify_explanation(self, explanation: str) -> str:
        """Simplify explanation for beginners."""
        # Placeholder implementation
        return f"[Simplified] {explanation}"
    
    def _enhance_explanation(self, explanation: str) -> str:
        """Enhance explanation for advanced users."""
        # Placeholder implementation
        return f"{explanation} [Advanced details would be added here]"
    
    def _get_concepts_for_quiz(self, user_profile: Optional[UserProfile]) -> List[Concept]:
        """Get concepts relevant for quiz generation."""
        if user_profile and hasattr(user_profile, 'progress'):
            # Get concepts from user's current topics
            current_topics = user_profile.progress.current_topics
            concepts = []
            for topic in current_topics:
                topic_concepts = self.db_manager.get_concepts_for_topic(topic)
                concepts.extend(topic_concepts)
            return concepts
        else:
            # Get random concepts
            return self.db_manager.get_random_concepts(50)
    
    def _get_problems_for_quiz(self, user_profile: Optional[UserProfile]) -> List[Problem]:
        """Get problems relevant for quiz generation."""
        if user_profile and hasattr(user_profile, 'progress'):
            # Get problems from user's current topics
            current_topics = user_profile.progress.current_topics
            problems = []
            for topic in current_topics:
                topic_problems = self.db_manager.get_problems_for_topic(topic)
                problems.extend(topic_problems)
            return problems
        else:
            # Get random problems
            return self.db_manager.get_random_problems(50)
    
    def _generate_multiple_choice_question(self, concepts: List[Concept]) -> QuizQuestion:
        """Generate a multiple choice question."""
        concept = random.choice(concepts)
        
        # Placeholder question generation
        question = QuizQuestion(
            id=f"mc_{datetime.now().timestamp()}",
            question=f"What is {concept.name}?",
            question_type='multiple_choice',
            options=[
                concept.description,
                "Incorrect option 1",
                "Incorrect option 2",
                "Incorrect option 3"
            ],
            correct_answer=concept.description,
            explanation=f"The correct answer is based on the definition of {concept.name}",
            difficulty=concept.difficulty,
            topic=concept.topic,
            points=1
        )
        
        # Shuffle options
        random.shuffle(question.options)
        
        return question
    
    def _generate_true_false_question(self, concepts: List[Concept]) -> QuizQuestion:
        """Generate a true/false question."""
        concept = random.choice(concepts)
        
        # Randomly make true or false
        is_true = random.choice([True, False])
        statement = concept.description if is_true else f"NOT: {concept.description}"
        
        question = QuizQuestion(
            id=f"tf_{datetime.now().timestamp()}",
            question=f"True or False: {statement}",
            question_type='true_false',
            options=["True", "False"],
            correct_answer="True" if is_true else "False",
            explanation=f"The statement is {'correct' if is_true else 'incorrect'} regarding {concept.name}",
            difficulty=concept.difficulty,
            topic=concept.topic,
            points=1
        )
        
        return question
    
    def _generate_fill_blank_question(self, concepts: List[Concept]) -> QuizQuestion:
        """Generate a fill-in-the-blank question."""
        concept = random.choice(concepts)
        
        # Create a statement with a blank
        description = concept.description
        words = description.split()
        if len(words) > 3:
            blank_index = random.randint(1, len(words) - 2)
            blank_word = words[blank_index]
            words[blank_index] = "______"
            question_text = " ".join(words)
        else:
            question_text = f"Complete: {concept.name} is ______"
            blank_word = "definition"
        
        question = QuizQuestion(
            id=f"fb_{datetime.now().timestamp()}",
            question=question_text,
            question_type='fill_blank',
            options=[],
            correct_answer=blank_word,
            explanation=f"The missing word relates to {concept.name}",
            difficulty=concept.difficulty,
            topic=concept.topic,
            points=1
        )
        
        return question
    
    def _generate_code_completion_question(self, problems: List[Problem]) -> QuizQuestion:
        """Generate a code completion question."""
        problem = random.choice(problems)
        
        # Create a code snippet with missing parts
        if problem.solution:
            code_lines = problem.solution.split('\n')
            if len(code_lines) > 2:
                line_to_blank = random.randint(1, len(code_lines) - 1)
                original_line = code_lines[line_to_blank]
                code_lines[line_to_blank] = "    // Complete this line"
                incomplete_code = '\n'.join(code_lines)
            else:
                incomplete_code = "// Complete the solution"
                original_line = problem.solution
        else:
            incomplete_code = f"// Solve: {problem.title}"
            original_line = "solution"
        
        question = QuizQuestion(
            id=f"cc_{datetime.now().timestamp()}",
            question=f"Complete the following code:\n```\n{incomplete_code}\n```",
            question_type='code_completion',
            options=[],
            correct_answer=original_line,
            explanation=f"This completes the solution for {problem.title}",
            difficulty=problem.difficulty,
            topic=problem.topic,
            points=2
        )
        
        return question
    
    def _rank_search_results(self, results: Dict[str, List], user_profile: UserProfile) -> Dict[str, List]:
        """Rank search results based on user profile."""
        # Placeholder implementation - would use more sophisticated ranking
        return results
    
    def _get_next_step_recommendations(self, user_profile: UserProfile) -> List[Dict[str, Any]]:
        """Get next step content recommendations."""
        recommendations = []
        
        # Placeholder recommendations
        recommendations.append({
            'type': 'topic',
            'title': 'Binary Trees',
            'reason': 'Next in your learning path',
            'priority': 'high'
        })
        
        return recommendations
    
    def _get_review_recommendations(self, user_profile: UserProfile) -> List[Dict[str, Any]]:
        """Get review content recommendations."""
        recommendations = []
        
        # Placeholder recommendations
        recommendations.append({
            'type': 'concept',
            'title': 'Time Complexity',
            'reason': 'Review recommended based on recent errors',
            'priority': 'medium'
        })
        
        return recommendations
    
    def _get_challenge_recommendations(self, user_profile: UserProfile) -> List[Dict[str, Any]]:
        """Get challenge content recommendations."""
        recommendations = []
        
        # Placeholder recommendations
        recommendations.append({
            'type': 'problem',
            'title': 'Advanced Graph Algorithms',
            'reason': 'Challenge yourself with harder problems',
            'priority': 'low'
        })
        
        return recommendations
    
    def _personalize_hints(self, hints: List[str], user_profile: UserProfile) -> List[str]:
        """Personalize hints based on user profile."""
        # Placeholder implementation
        return hints