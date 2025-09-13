#!/usr/bin/env python3
"""
Enhanced Learning System - Comprehensive CLI + Claude Integration
This system thoughtfully bridges your CLI with Claude for maximum learning effectiveness
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import re

@dataclass
class LearningContext:
    """Comprehensive context for current learning session"""
    lesson_id: str
    lesson_title: str
    lesson_content: str
    lesson_code: Optional[str]
    user_progress: Dict
    previous_questions: List[str]
    notes: List[str]
    comprehension_attempts: int
    time_spent: int
    difficulty_level: str
    
class ComprehensiveLearningEnhancer:
    """
    Thoughtfully enhances the CLI experience by:
    1. Generating intelligent, context-aware questions
    2. Formatting information optimally for Claude
    3. Structuring notes from Claude's responses
    4. Tracking learning patterns
    5. Providing adaptive guidance
    """
    
    def __init__(self, db_path="curriculum.db"):
        self.db_path = db_path
        self.current_context = None
        self.question_history = []
        self.insight_bank = {}
        
    def analyze_lesson_for_questions(self, lesson: Dict) -> Dict[str, List[str]]:
        """
        Comprehensively analyze lesson content to generate targeted questions
        Returns categorized questions for different learning objectives
        """
        
        questions = {
            "conceptual": [],      # Understanding the 'why'
            "implementation": [],  # The 'how' of coding it
            "complexity": [],      # Time/space analysis
            "applications": [],    # Real-world usage
            "comparisons": [],     # Vs other approaches
            "debugging": [],       # Common issues
            "optimization": [],    # Making it better
            "edge_cases": []      # Special scenarios
        }
        
        content = lesson.get('content', '').lower()
        title = lesson.get('title', '')
        code = lesson.get('code', '')
        
        # Conceptual Understanding Questions
        questions["conceptual"].extend([
            f"What is the core intuition behind {title}?",
            f"Why was {title} invented? What problem does it uniquely solve?",
            f"Can you explain {title} using a real-world analogy?",
            f"What are the key invariants that {title} maintains?",
            f"How would you explain {title} to someone without a CS background?"
        ])
        
        # Implementation Questions
        if code:
            questions["implementation"].extend([
                f"What are the critical steps in implementing {title}?",
                f"What data structures are essential for {title} and why?",
                f"Can you trace through {title} with a specific example?",
                f"What are common bugs when implementing {title}?",
                f"How would the implementation change for different data types?"
            ])
            
            # Language-specific implementations
            questions["implementation"].extend([
                f"How would you implement {title} in JavaScript/TypeScript?",
                f"What Python-specific features can optimize {title}?",
                f"How does {title} differ in functional vs imperative languages?"
            ])
        
        # Complexity Analysis Questions
        if any(term in content for term in ['o(', 'complexity', 'big-o', 'performance']):
            questions["complexity"].extend([
                f"Why is the time complexity of {title} what it is?",
                f"Can you prove the worst-case complexity of {title}?",
                f"What input would cause {title} to hit its worst-case performance?",
                f"How does space complexity trade off with time in {title}?",
                f"Are there scenarios where {title}'s average case differs significantly from worst case?"
            ])
        
        # Real-world Application Questions
        questions["applications"].extend([
            f"What companies use {title} in production and for what?",
            f"Can you give 3 real software systems that rely on {title}?",
            f"When would you choose NOT to use {title}?",
            f"How does {title} scale in distributed systems?",
            f"What modern variations or improvements exist for {title}?"
        ])
        
        # Comparison Questions
        questions["comparisons"].extend([
            f"When would you choose {title} over simpler alternatives?",
            f"What are the trade-offs between {title} and its alternatives?",
            f"How does {title} compare in terms of maintainability vs performance?",
            f"In what scenarios does {title} outperform more complex solutions?",
            f"What makes {title} better or worse than similar algorithms?"
        ])
        
        # Debugging and Testing Questions
        questions["debugging"].extend([
            f"What test cases would comprehensively validate {title}?",
            f"How would you debug a faulty {title} implementation?",
            f"What edge cases often break {title} implementations?",
            f"How can you verify correctness of {title} for large inputs?",
            f"What logging would help diagnose issues in {title}?"
        ])
        
        # Optimization Questions
        questions["optimization"].extend([
            f"How can {title} be optimized for cache performance?",
            f"Are there ways to parallelize {title}?",
            f"What preprocessing could improve {title}'s performance?",
            f"How would you adapt {title} for memory-constrained environments?",
            f"Can {title} be improved with modern hardware features (SIMD, GPU)?"
        ])
        
        # Edge Cases and Special Scenarios
        questions["edge_cases"].extend([
            f"How does {title} handle empty inputs?",
            f"What happens with {title} on extremely large datasets?",
            f"How does {title} behave with duplicate values?",
            f"What modifications are needed for {title} to handle negative values?",
            f"How robust is {title} to malformed or adversarial inputs?"
        ])
        
        # Filter out less relevant categories based on lesson content
        filtered_questions = {}
        for category, q_list in questions.items():
            if q_list:  # Only include non-empty categories
                # Prioritize most relevant questions based on content analysis
                filtered_questions[category] = self._prioritize_questions(q_list, lesson)
        
        return filtered_questions
    
    def _prioritize_questions(self, questions: List[str], lesson: Dict) -> List[str]:
        """Prioritize questions based on lesson content and difficulty"""
        
        difficulty = lesson.get('difficulty', 'intermediate')
        
        # Adjust question count based on difficulty
        if difficulty == 'beginner':
            return questions[:3]  # Fewer, simpler questions
        elif difficulty == 'advanced':
            return questions[:7]  # More complex questions
        else:
            return questions[:5]  # Balanced set
    
    def format_claude_context(self, 
                            lesson: Dict,
                            specific_question: Optional[str] = None,
                            include_history: bool = True) -> str:
        """
        Create comprehensive context for Claude to provide the best possible answer
        """
        
        # Build rich context
        context_parts = []
        
        # 1. Current Learning Context
        context_parts.append("📚 CURRENT LEARNING CONTEXT")
        context_parts.append("=" * 50)
        context_parts.append(f"Topic: {lesson.get('title', 'Unknown')}")
        context_parts.append(f"Difficulty: {lesson.get('difficulty', 'Not specified')}")
        context_parts.append(f"Module: {lesson.get('module', 'Core Concepts')}")
        
        # 2. Lesson Content
        context_parts.append("\n📖 LESSON CONTENT")
        context_parts.append("=" * 50)
        content = lesson.get('content', 'No content available')
        context_parts.append(content[:1000] if len(content) > 1000 else content)
        
        # 3. Code Example (if available)
        if lesson.get('code'):
            context_parts.append("\n💻 CODE EXAMPLE")
            context_parts.append("=" * 50)
            context_parts.append(lesson['code'])
        
        # 4. Learning Objectives
        if lesson.get('learning_objectives'):
            context_parts.append("\n🎯 LEARNING OBJECTIVES")
            context_parts.append("=" * 50)
            for obj in lesson['learning_objectives']:
                context_parts.append(f"• {obj}")
        
        # 5. Previous Questions (if relevant)
        if include_history and self.question_history:
            context_parts.append("\n📝 PREVIOUS QUESTIONS IN THIS SESSION")
            context_parts.append("=" * 50)
            for prev_q in self.question_history[-3:]:  # Last 3 questions
                context_parts.append(f"• {prev_q}")
        
        # 6. Specific Question
        if specific_question:
            context_parts.append("\n❓ MY SPECIFIC QUESTION")
            context_parts.append("=" * 50)
            context_parts.append(specific_question)
            
            # Add any code the user is debugging
            if "code" in specific_question.lower() or "error" in specific_question.lower():
                context_parts.append("\n🔧 DEBUGGING CONTEXT")
                context_parts.append("Please help me understand what's wrong and how to fix it.")
        
        # 7. Response Guidelines for Claude
        context_parts.append("\n📋 PLEASE PROVIDE")
        context_parts.append("=" * 50)
        context_parts.append("1. Clear explanation with examples")
        context_parts.append("2. Step-by-step reasoning if applicable")
        context_parts.append("3. Common pitfalls to avoid")
        context_parts.append("4. Practical applications")
        context_parts.append("5. Connections to related concepts")
        
        return "\n".join(context_parts)
    
    def generate_smart_followups(self, original_question: str, topic: str) -> List[str]:
        """Generate intelligent follow-up questions based on the original question"""
        
        followups = []
        
        # Analyze the type of original question
        if "why" in original_question.lower():
            followups.extend([
                f"Can you show me a concrete example that demonstrates this?",
                f"What would happen if we didn't do it this way?",
                f"How did computer scientists figure this out originally?"
            ])
        
        elif "how" in original_question.lower():
            followups.extend([
                f"What's the most common mistake when doing this?",
                f"Can you break this down into smaller steps?",
                f"Is there a visual way to understand this process?"
            ])
        
        elif "when" in original_question.lower():
            followups.extend([
                f"What are the specific conditions that make this the best choice?",
                f"Can you give me a real-world scenario where this applies?",
                f"What are the alternatives and their trade-offs?"
            ])
        
        elif "code" in original_question.lower() or "implement" in original_question.lower():
            followups.extend([
                f"How would I test this implementation thoroughly?",
                f"What edge cases should I consider?",
                f"How can I optimize this further?"
            ])
        
        # Add topic-specific follow-ups
        if "sort" in topic.lower():
            followups.append("How does this compare to other sorting algorithms?")
        elif "search" in topic.lower():
            followups.append("What data structure makes this search efficient?")
        elif "tree" in topic.lower() or "graph" in topic.lower():
            followups.append("How would this work with cyclic vs acyclic structures?")
        
        return followups[:3]  # Return top 3 most relevant
    
    def structure_claude_response_as_note(self, 
                                         question: str,
                                         claude_response: str,
                                         lesson_title: str) -> str:
        """
        Structure Claude's response into a well-organized note for the database
        """
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Extract key insights using pattern matching
        key_points = self._extract_key_points(claude_response)
        
        structured_note = f"""
================================================================================
📅 {timestamp} | 📚 {lesson_title}
================================================================================

❓ QUESTION:
{question}

💡 KEY INSIGHTS:
{chr(10).join(f'• {point}' for point in key_points[:5])}

📝 DETAILED EXPLANATION:
{claude_response[:500]}{'...' if len(claude_response) > 500 else ''}

🎯 ACTION ITEMS:
• Practice implementing this concept
• Try solving related problems
• Review this note before the quiz

🔗 RELATED CONCEPTS:
{self._extract_related_concepts(claude_response, lesson_title)}

⭐ REMEMBER:
{self._extract_key_takeaway(claude_response)}

================================================================================
"""
        return structured_note
    
    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key points from Claude's response"""
        
        key_points = []
        
        # Look for numbered or bulleted lists
        patterns = [
            r'^\d+\.\s+(.+)$',  # Numbered lists
            r'^[•·▪]\s+(.+)$',  # Bullet points
            r'^-\s+(.+)$',      # Dash lists
        ]
        
        for line in text.split('\n'):
            for pattern in patterns:
                match = re.match(pattern, line.strip())
                if match:
                    key_points.append(match.group(1))
                    break
        
        # If no structured list found, extract important sentences
        if not key_points:
            sentences = text.split('.')
            for sentence in sentences:
                if any(keyword in sentence.lower() for keyword in 
                      ['important', 'remember', 'key', 'crucial', 'essential']):
                    key_points.append(sentence.strip())
        
        return key_points[:5]  # Limit to 5 key points
    
    def _extract_related_concepts(self, text: str, current_topic: str) -> str:
        """Extract concepts related to the current topic"""
        
        # Common CS concepts to look for
        concepts = [
            'array', 'list', 'tree', 'graph', 'hash', 'stack', 'queue',
            'recursion', 'iteration', 'dynamic programming', 'greedy',
            'divide and conquer', 'backtracking', 'sorting', 'searching'
        ]
        
        mentioned = []
        text_lower = text.lower()
        
        for concept in concepts:
            if concept in text_lower and concept.lower() not in current_topic.lower():
                mentioned.append(concept.capitalize())
        
        return ', '.join(mentioned[:3]) if mentioned else 'No specific relations mentioned'
    
    def _extract_key_takeaway(self, text: str) -> str:
        """Extract the most important takeaway from the response"""
        
        # Look for conclusion indicators
        conclusions = []
        
        patterns = [
            r'[Ii]n summary[,:]?\s*(.+?)(?:\.|$)',
            r'[Tt]he key (?:point|thing|idea) is[,:]?\s*(.+?)(?:\.|$)',
            r'[Rr]emember[,:]?\s*(.+?)(?:\.|$)',
            r'[Mm]ost importantly[,:]?\s*(.+?)(?:\.|$)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                conclusions.extend(matches)
        
        if conclusions:
            return conclusions[0][:200]  # First conclusion, limited length
        
        # Fallback: return first important-looking sentence
        sentences = text.split('.')
        for sentence in sentences:
            if len(sentence) > 20 and len(sentence) < 200:
                return sentence.strip()
        
        return "Review the full explanation above for complete understanding"
    
    def create_practice_problems(self, lesson: Dict) -> List[Dict]:
        """
        Generate practice problems based on the lesson content
        These can be attempted before asking Claude for help
        """
        
        problems = []
        title = lesson.get('title', '')
        
        # Generate problems based on lesson type
        if 'sort' in title.lower():
            problems.append({
                'description': f'Implement {title} from scratch without looking at the code',
                'hint': 'Start with the base case, then think about how to combine/divide',
                'validation': 'Test with: [], [1], [2,1], [3,1,2], [1,2,3]'
            })
            
        elif 'search' in title.lower():
            problems.append({
                'description': f'Write {title} that returns the index or -1 if not found',
                'hint': 'Consider what makes this search efficient',
                'validation': 'Test with empty array, single element, target at start/middle/end'
            })
            
        elif 'tree' in title.lower() or 'graph' in title.lower():
            problems.append({
                'description': f'Draw out {title} operations on paper first',
                'hint': 'Visualize the structure changes step by step',
                'validation': 'Trace through your code with the drawing'
            })
        
        # Add a debugging problem
        problems.append({
            'description': f'Find and fix the bug in this broken {title} implementation',
            'hint': 'Common issues: off-by-one errors, wrong comparisons, missing base cases',
            'validation': 'Test with edge cases: empty, single element, duplicates'
        })
        
        # Add an analysis problem  
        problems.append({
            'description': f'Analyze the time and space complexity of {title}',
            'hint': 'Count operations in terms of input size n',
            'validation': 'Explain best, average, and worst cases'
        })
        
        return problems
    
    def track_learning_pattern(self, lesson_id: str, question_type: str, time_spent: int):
        """Track what types of questions the user asks most frequently"""
        
        if not hasattr(self, 'learning_patterns'):
            self.learning_patterns = {}
        
        if lesson_id not in self.learning_patterns:
            self.learning_patterns[lesson_id] = {
                'question_types': {},
                'total_time': 0,
                'question_count': 0
            }
        
        pattern = self.learning_patterns[lesson_id]
        pattern['question_types'][question_type] = pattern['question_types'].get(question_type, 0) + 1
        pattern['total_time'] += time_spent
        pattern['question_count'] += 1
    
    def get_personalized_recommendations(self) -> List[str]:
        """Based on learning patterns, recommend what to focus on"""
        
        if not hasattr(self, 'learning_patterns') or not self.learning_patterns:
            return ["Keep asking questions about concepts that confuse you!"]
        
        recommendations = []
        
        # Analyze patterns
        total_questions = sum(p['question_count'] for p in self.learning_patterns.values())
        
        if total_questions > 0:
            # Find most common question types
            all_types = {}
            for pattern in self.learning_patterns.values():
                for q_type, count in pattern['question_types'].items():
                    all_types[q_type] = all_types.get(q_type, 0) + count
            
            if all_types:
                most_common = max(all_types, key=all_types.get)
                
                if most_common == 'conceptual':
                    recommendations.append("You often ask 'why' questions - great for deep understanding!")
                    recommendations.append("Try implementing the concepts to solidify your knowledge")
                elif most_common == 'implementation':
                    recommendations.append("You focus on coding - excellent practical approach!")
                    recommendations.append("Also explore the theory behind why these implementations work")
                elif most_common == 'debugging':
                    recommendations.append("You're working through implementation challenges")
                    recommendations.append("Consider tracing through algorithms on paper first")
        
        # Time-based recommendations
        avg_time = sum(p['total_time'] for p in self.learning_patterns.values()) / len(self.learning_patterns)
        if avg_time > 1800:  # 30+ minutes average
            recommendations.append("You're spending good time on each topic - this deep focus will pay off!")
        
        return recommendations

# Integration helper specifically for use with the CLI
class CLIClaudeIntegration:
    """Helper to integrate Claude assistance into the existing CLI"""
    
    def __init__(self):
        self.enhancer = ComprehensiveLearningEnhancer()
        
    def enhance_lesson_display(self, lesson: Dict) -> str:
        """Add Claude-aware enhancements to lesson display"""
        
        enhancement = "\n" + "="*80 + "\n"
        enhancement += "🤖 CLAUDE LEARNING ASSISTANCE AVAILABLE\n"
        enhancement += "="*80 + "\n\n"
        
        # Generate smart questions
        questions = self.enhancer.analyze_lesson_for_questions(lesson)
        
        enhancement += "📝 SUGGESTED QUESTIONS TO EXPLORE:\n\n"
        
        # Show top questions from each category
        for category, q_list in list(questions.items())[:3]:  # Top 3 categories
            if q_list:
                enhancement += f"**{category.upper()}:**\n"
                for q in q_list[:2]:  # Top 2 questions per category
                    enhancement += f"  • {q}\n"
                enhancement += "\n"
        
        # Add practice problems
        problems = self.enhancer.create_practice_problems(lesson)
        if problems:
            enhancement += "🎯 TRY THESE PRACTICE PROBLEMS FIRST:\n\n"
            for i, problem in enumerate(problems[:2], 1):
                enhancement += f"{i}. {problem['description']}\n"
                enhancement += f"   Hint: {problem['hint']}\n\n"
        
        enhancement += "="*80 + "\n"
        enhancement += "💡 Copy any question above and ask Claude for a detailed explanation!\n"
        enhancement += "📌 Save important insights as notes in your learning session.\n"
        enhancement += "="*80 + "\n"
        
        return enhancement
    
    def format_question_for_claude(self, lesson: Dict, question: str) -> str:
        """Format a question with full context for Claude"""
        return self.enhancer.format_claude_context(lesson, question)
    
    def save_claude_discussion(self, question: str, response: str, lesson: Dict) -> str:
        """Convert Claude discussion into a structured note"""
        return self.enhancer.structure_claude_response_as_note(
            question, response, lesson.get('title', 'Unknown Topic')
        )

# Make it easy to use in the existing CLI
def integrate_with_cli():
    """Quick integration function for the existing CLI"""
    return CLIClaudeIntegration()

if __name__ == "__main__":
    # Demo the comprehensive system
    print("🚀 Comprehensive Learning Enhancement System")
    print("="*60)
    
    # Example lesson
    sample_lesson = {
        'id': 'algo_001',
        'title': 'Binary Search',
        'content': 'Binary search is an efficient algorithm for finding an item in a sorted list...',
        'code': 'def binary_search(arr, target):\n    left, right = 0, len(arr)-1\n    ...',
        'difficulty': 'intermediate',
        'module': 'Searching Algorithms'
    }
    
    # Initialize the integration
    integration = integrate_with_cli()
    
    # Show enhanced display
    print(integration.enhance_lesson_display(sample_lesson))
    
    # Show how to format a question
    formatted = integration.format_question_for_claude(
        sample_lesson, 
        "Why is binary search O(log n)?"
    )
    print("\n📋 FORMATTED CONTEXT FOR CLAUDE:")
    print("="*60)
    print(formatted[:500] + "...")