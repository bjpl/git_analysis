#!/usr/bin/env python3
"""
Claude Helper - Templates for getting the most out of Claude as your learning companion
"""

class ClaudeHelper:
    """Generate question templates to ask Claude for maximum learning value"""
    
    @staticmethod
    def get_question_templates(lesson_title, lesson_content):
        """Generate smart question templates based on the lesson"""
        
        templates = []
        
        # Core understanding questions
        templates.append(f"Can you explain why {lesson_title} works the way it does?")
        templates.append(f"What's the intuition behind {lesson_title}?")
        templates.append(f"What problem does {lesson_title} solve that simpler approaches don't?")
        
        # Complexity and performance
        if any(term in lesson_content.lower() for term in ['o(', 'complexity', 'performance']):
            templates.append(f"Why is the time complexity what it is for {lesson_title}?")
            templates.append(f"Can you trace through an example showing the complexity?")
            templates.append(f"What are the best/worst/average cases?")
        
        # Implementation details
        if 'code' in lesson_content.lower() or 'implement' in lesson_content.lower():
            templates.append(f"What are common mistakes when implementing {lesson_title}?")
            templates.append(f"Can you show me {lesson_title} in JavaScript/Java/C++?")
            templates.append(f"What edge cases should I consider?")
        
        # Real-world applications
        templates.append(f"Where is {lesson_title} used in real software?")
        templates.append(f"What are practical examples of {lesson_title}?")
        templates.append(f"When should I choose {lesson_title} over alternatives?")
        
        # Connections and comparisons
        templates.append(f"How does {lesson_title} relate to other algorithms I've learned?")
        templates.append(f"What are the trade-offs compared to alternative approaches?")
        templates.append(f"What should I learn before/after {lesson_title}?")
        
        # Debugging and problem-solving
        templates.append(f"I'm confused about [specific part]. Can you clarify?")
        templates.append(f"My implementation isn't working. Here's my code: [paste code]")
        templates.append(f"The comprehension question asks [question]. Why is [answer] correct?")
        
        return templates
    
    @staticmethod
    def format_for_claude(lesson, user_question=None, user_code=None):
        """Format lesson context for asking Claude"""
        
        context = f"""
I'm learning about: {lesson.get('title', 'this topic')}

Lesson Content:
{lesson.get('content', 'No content available')}

{'Code Example:' if lesson.get('code') else ''}
{lesson.get('code', '')}

My Question: {user_question if user_question else '[Your specific question here]'}

{'My Code Attempt:' if user_code else ''}
{user_code if user_code else ''}
"""
        return context.strip()
    
    @staticmethod
    def get_note_template(claude_response):
        """Template for saving Claude's response as a note"""
        
        return f"""
KEY INSIGHTS:
- [Main concept explained]
- [Important detail 1]
- [Important detail 2]

REMEMBER:
{claude_response[:200]}...

TO REVIEW:
- [Action item 1]
- [Practice problem]
"""

    @staticmethod
    def print_helper_guide():
        """Print a quick guide for using Claude effectively"""
        
        guide = """
========================================
🤖 CLAUDE LEARNING COMPANION GUIDE
========================================

WHEN TO ASK CLAUDE:
✓ You don't understand why something works
✓ You want to see more examples
✓ You need help debugging your code
✓ You want real-world applications
✓ You're curious about trade-offs
✓ You failed a comprehension check

HOW TO ASK EFFECTIVELY:
1. Share the lesson title and relevant content
2. Be specific about what confuses you
3. Include your code if you're debugging
4. Ask follow-up questions to go deeper

EXAMPLE QUESTIONS:
• "Why does quicksort have O(n²) worst case?"
• "Show me binary search with step-by-step trace"
• "My merge sort is returning unsorted arrays - here's my code..."
• "What's the intuition for why hash tables are O(1)?"
• "When would I use BFS instead of DFS?"

SAVING INSIGHTS:
After Claude explains, save key points as notes in your CLI:
- Main concept in your own words
- Aha moments
- Things to practice
- Connections to other topics

========================================
"""
        print(guide)
        return guide

# Quick example of how to use this in your CLI
if __name__ == "__main__":
    
    # Example lesson
    sample_lesson = {
        'title': 'Binary Search',
        'content': 'Binary search is an efficient algorithm for finding an item in a sorted list...',
        'code': 'def binary_search(arr, target):...'
    }
    
    # Get question suggestions
    helper = ClaudeHelper()
    questions = helper.get_question_templates(
        sample_lesson['title'], 
        sample_lesson['content']
    )
    
    print("📝 Suggested Questions to Ask Claude:")
    print("=" * 40)
    for i, q in enumerate(questions[:5], 1):
        print(f"{i}. {q}")
    
    print("\n🎯 Format your question like this:")
    print("=" * 40)
    formatted = helper.format_for_claude(sample_lesson, "Why is it O(log n)?")
    print(formatted[:300] + "...")