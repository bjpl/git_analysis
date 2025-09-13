#!/usr/bin/env python3
"""
Enhanced Lesson Formatter - Beautiful consistent formatting for all curriculum content
Ensures both menu AND content use the same pretty terminal formatting styles
"""

import re
import textwrap
from typing import List, Optional, Dict, Any, Tuple, Union
from .formatter import TerminalFormatter, Color
from .lesson_display import LessonDisplay


class EnhancedLessonFormatter:
    """Enhanced formatter that applies consistent beautiful formatting to all content"""
    
    def __init__(self, formatter: Optional[TerminalFormatter] = None):
        """Initialize enhanced lesson formatter"""
        self.formatter = formatter or TerminalFormatter()
        self.lesson_display = LessonDisplay(self.formatter)
        self.width = min(self.formatter.width, 80)  # Cap at 80 for readability
        
    def format_lesson_content(self, lesson: Dict[str, Any]) -> None:
        """
        Format and display complete lesson with beautiful consistent styling
        
        Args:
            lesson: Lesson data dictionary
        """
        # Clear screen for clean presentation
        print("\033[2J\033[H")  # ANSI clear screen
        
        # Display lesson header with beautiful frame
        self._display_lesson_header(lesson)
        
        # Display key topics with visual hierarchy
        if 'key_topics' in lesson:
            self._display_key_topics(lesson['key_topics'])
        
        # Display lesson info in a styled panel
        self._display_lesson_info(lesson)
        
        # Display main content with proper formatting
        if 'content' in lesson:
            self._display_formatted_content(lesson['content'])
        
        # Display code examples with syntax highlighting
        if 'code_examples' in lesson:
            self._display_code_examples(lesson['code_examples'])
        
        # Display practice problems
        if 'practice_problems' in lesson:
            self._display_practice_problems(lesson['practice_problems'])
        
        # Display interactive options
        self._display_interactive_options()
    
    def _display_lesson_header(self, lesson: Dict[str, Any]) -> None:
        """Display lesson header with beautiful formatting"""
        title = lesson.get('title', 'Untitled Lesson')
        subtitle = lesson.get('subtitle', '')
        
        # Create a beautiful header box
        print()
        # Use the header method with level parameter only
        print(self.formatter.header(title, level=1))
        if subtitle:
            print(self.formatter._colorize(subtitle.center(70), Color.BRIGHT_MAGENTA))
        print()
    
    def _display_key_topics(self, topics: List[str]) -> None:
        """Display key topics with styled bullets"""
        print(self.formatter._colorize(">>> 🎯 Key Topics >>>", 
                                       Color.BRIGHT_MAGENTA, Color.BOLD))
        print(self.formatter._colorize("-" * 40, Color.BRIGHT_MAGENTA))
        
        for i, topic in enumerate(topics, 1):
            bullet = self.formatter._colorize(f"{i}.", Color.BRIGHT_CYAN, Color.BOLD)
            topic_text = self.formatter._colorize(topic, Color.WHITE)
            print(f"  {bullet} {topic_text}")
        
        print()
    
    def _display_lesson_info(self, lesson: Dict[str, Any]) -> None:
        """Display lesson metadata in a formatted panel"""
        sections = []
        
        # Time complexity section
        if 'time_complexity' in lesson:
            complexity_content = self._format_complexity_info(lesson['time_complexity'])
            sections.append(("⏱️ Time Complexity", complexity_content))
        
        # Space complexity section  
        if 'space_complexity' in lesson:
            space_content = self._format_complexity_info(lesson['space_complexity'])
            sections.append(("💾 Space Complexity", space_content))
        
        # Prerequisites
        if 'prerequisites' in lesson:
            prereq_content = "\n".join(f"  • {p}" for p in lesson['prerequisites'])
            sections.append(("📚 Prerequisites", prereq_content))
        
        # Difficulty and estimated time
        meta_content = []
        if 'difficulty' in lesson:
            badge = self._create_difficulty_badge(lesson['difficulty'])
            meta_content.append(f"Difficulty: {badge}")
        if 'est_time' in lesson:
            time_str = self.formatter._colorize(f"{lesson['est_time']} min", 
                                               Color.BRIGHT_YELLOW)
            meta_content.append(f"Est. Time: {time_str}")
        
        if meta_content:
            sections.append(("📊 Lesson Info", "  " + "    ".join(meta_content)))
        
        # Display as a beautiful panel
        if sections:
            # Create a formatted panel-like display
            print(self.formatter._colorize("┌" + "─" * 68 + "┐", Color.BRIGHT_CYAN))
            print(self.formatter._colorize("│" + " Lesson Overview ".center(68) + "│", Color.BRIGHT_CYAN, Color.BOLD))
            print(self.formatter._colorize("├" + "─" * 68 + "┤", Color.BRIGHT_CYAN))
            
            for header, content in sections:
                print(self.formatter._colorize(f"│ {header:<66} │", Color.BRIGHT_YELLOW, Color.BOLD))
                for line in content.split('\n'):
                    if line.strip():
                        print(self.formatter._colorize(f"│{line[:67]:<68}│", Color.WHITE))
            
            print(self.formatter._colorize("└" + "─" * 68 + "┘", Color.BRIGHT_CYAN))
            print()
    
    def _normalize_content(self, content: Any) -> str:
        """Normalize content to string format
        
        Args:
            content: Content in various formats
            
        Returns:
            Normalized string content
        """
        if content is None:
            return ""
        
        if isinstance(content, str):
            return content
        
        if isinstance(content, dict):
            # Handle dict format with sections
            parts = []
            for key, value in content.items():
                if key in ['title', 'subtitle']:
                    continue  # Skip these as they're handled in header
                parts.append(f"## {key.replace('_', ' ').title()}")
                if isinstance(value, list):
                    for item in value:
                        parts.append(f"- {item}")
                else:
                    parts.append(str(value))
            return '\n\n'.join(parts)
        
        if isinstance(content, list):
            # Handle list format
            return '\n\n'.join(str(item) for item in content)
        
        # Fallback: convert to string
        return str(content)
    
    def _create_difficulty_badge(self, difficulty: str) -> str:
        """Create a color-coded difficulty badge"""
        difficulty_lower = difficulty.lower()
        
        if difficulty_lower in ['easy', 'beginner', 'basic']:
            return self.formatter._colorize(f"[{difficulty.upper()}]", Color.BRIGHT_GREEN, Color.BOLD)
        elif difficulty_lower in ['medium', 'intermediate', 'normal']:
            return self.formatter._colorize(f"[{difficulty.upper()}]", Color.BRIGHT_YELLOW, Color.BOLD)
        elif difficulty_lower in ['hard', 'advanced', 'expert']:
            return self.formatter._colorize(f"[{difficulty.upper()}]", Color.BRIGHT_RED, Color.BOLD)
        else:
            return self.formatter._colorize(f"[{difficulty.upper()}]", Color.WHITE, Color.BOLD)
    
    def _format_complexity_info(self, complexity: str) -> str:
        """Format complexity notation with color coding"""
        # Color code different complexities
        if 'O(1)' in complexity:
            color = Color.BRIGHT_GREEN
            label = "Constant"
        elif 'O(log' in complexity:
            color = Color.BRIGHT_CYAN
            label = "Logarithmic"
        elif 'O(n)' in complexity and 'O(n^' not in complexity:
            color = Color.BRIGHT_YELLOW
            label = "Linear"
        elif 'O(n log n)' in complexity:
            color = Color.YELLOW
            label = "Linearithmic"
        elif 'O(n^2)' in complexity or 'O(n²)' in complexity:
            color = Color.BRIGHT_RED
            label = "Quadratic"
        else:
            color = Color.BRIGHT_MAGENTA
            label = "Complex"
        
        formatted = self.formatter._colorize(complexity, color, Color.BOLD)
        return f"  {formatted} - {label}"
    
    def _display_formatted_content(self, content: Any) -> None:
        """Display main content with proper formatting
        
        Args:
            content: Can be string, dict, list, or None
        """
        print(self.formatter._colorize(">>> 📖 Lesson Content >>>", 
                                       Color.BRIGHT_CYAN, Color.BOLD))
        print(self.formatter._colorize("=" * 60, Color.BRIGHT_CYAN))
        print()
        
        # Handle different content types
        content_str = self._normalize_content(content)
        if not content_str:
            print(self.formatter._colorize("  No detailed content available yet.", 
                                          Color.WHITE))
            print()
            return
        
        # Parse and format content sections
        lines = content_str.split('\n')
        in_code_block = False
        code_lines = []
        code_lang = "python"
        
        for line in lines:
            # Handle code blocks
            if line.strip().startswith('```'):
                if in_code_block:
                    # End code block
                    self._display_code_block(code_lines, code_lang)
                    code_lines = []
                    in_code_block = False
                else:
                    # Start code block
                    lang_match = re.match(r'```(\w+)?', line.strip())
                    if lang_match and lang_match.group(1):
                        code_lang = lang_match.group(1)
                    in_code_block = True
                continue
            
            if in_code_block:
                code_lines.append(line)
                continue
            
            # Format different line types
            self._format_content_line(line)
        
        print()
    
    def _format_content_line(self, line: str) -> None:
        """Format a single content line based on its type"""
        stripped = line.strip()
        
        # Headers
        if stripped.startswith('###'):
            text = stripped.strip('#').strip()
            print()
            print(self.formatter._colorize(f"    ▸ {text}", Color.BRIGHT_GREEN, Color.BOLD))
            print()
        elif stripped.startswith('##'):
            text = stripped.strip('#').strip()
            print()
            print(self.formatter._colorize(f"  ▶ {text}", Color.BRIGHT_CYAN, Color.BOLD))
            print(self.formatter._colorize("  " + "-" * len(text), Color.BRIGHT_CYAN))
            print()
        elif stripped.startswith('#'):
            text = stripped.strip('#').strip()
            print()
            print(self.formatter._colorize(text.upper(), Color.BRIGHT_YELLOW, Color.BOLD))
            print(self.formatter._colorize("=" * len(text), Color.BRIGHT_YELLOW))
            print()
        
        # Bullet points
        elif stripped.startswith('- ') or stripped.startswith('* '):
            text = stripped[2:]
            bullet = self.formatter._colorize("•", Color.BRIGHT_CYAN, Color.BOLD)
            formatted_text = self._process_inline_formatting(text)
            wrapped = textwrap.fill(formatted_text, width=self.width - 4,
                                   initial_indent="", subsequent_indent="    ")
            print(f"  {bullet} {wrapped}")
        
        # Numbered lists
        elif re.match(r'^\d+\.', stripped):
            parts = stripped.split('.', 1)
            if len(parts) == 2:
                num = self.formatter._colorize(f"{parts[0]}.", 
                                              Color.BRIGHT_YELLOW, Color.BOLD)
                text = self._process_inline_formatting(parts[1].strip())
                wrapped = textwrap.fill(text, width=self.width - 6,
                                       initial_indent="", subsequent_indent="     ")
                print(f"  {num} {wrapped}")
        
        # Important/highlighted lines
        elif stripped.startswith('>'):
            text = stripped[1:].strip()
            formatted = self.formatter._colorize(f"  ➤ {text}", 
                                                Color.BRIGHT_MAGENTA, Color.BOLD)
            print(formatted)
        
        # Regular paragraphs
        elif stripped:
            formatted = self._process_inline_formatting(stripped)
            wrapped = textwrap.fill(formatted, width=self.width - 4,
                                   initial_indent="  ", subsequent_indent="  ")
            print(wrapped)
        
        # Empty lines
        else:
            print()
    
    def _process_inline_formatting(self, text: str) -> str:
        """Process inline markdown-style formatting"""
        # Bold text
        text = re.sub(r'\*\*([^*]+)\*\*', 
                     lambda m: self.formatter._colorize(m.group(1), 
                                                       Color.BRIGHT_WHITE, Color.BOLD),
                     text)
        
        # Italic (displayed as dim)
        text = re.sub(r'\*([^*]+)\*',
                     lambda m: self.formatter._colorize(m.group(1), 
                                                       Color.WHITE, Color.DIM),
                     text)
        
        # Inline code
        text = re.sub(r'`([^`]+)`',
                     lambda m: self.formatter._colorize(m.group(1), 
                                                       Color.BRIGHT_CYAN),
                     text)
        
        return text
    
    def _display_code_block(self, lines: List[str], language: str = "python") -> None:
        """Display a formatted code block with syntax highlighting"""
        if not lines:
            return
        
        # Create bordered box for code
        max_line_len = max(len(line) for line in lines) if lines else 0
        box_width = min(max_line_len + 6, self.width - 4)
        
        # Top border
        print("  " + self.formatter._colorize("┌" + "─" * (box_width - 2) + "┐", 
                                             Color.BRIGHT_BLACK))
        
        # Code lines with syntax highlighting
        for i, line in enumerate(lines, 1):
            line_num = self.formatter._colorize(f"{i:3d}", Color.BRIGHT_BLACK)
            highlighted = self._simple_syntax_highlight(line, language)
            
            # Ensure proper padding
            display_line = highlighted[:box_width - 8] if len(line) > box_width - 8 else highlighted
            padded = display_line.ljust(box_width - 8)
            
            border = self.formatter._colorize("│", Color.BRIGHT_BLACK)
            print(f"  {border} {line_num} {padded} {border}")
        
        # Bottom border
        print("  " + self.formatter._colorize("└" + "─" * (box_width - 2) + "┘", 
                                             Color.BRIGHT_BLACK))
        print()
    
    def _simple_syntax_highlight(self, line: str, language: str) -> str:
        """Apply simple syntax highlighting to code"""
        if language.lower() in ['python', 'py']:
            # Keywords
            keywords = ['def', 'return', 'if', 'else', 'elif', 'for', 'while',
                       'in', 'not', 'and', 'or', 'class', 'import', 'from',
                       'try', 'except', 'with', 'as', 'None', 'True', 'False']
            
            highlighted = line
            for keyword in keywords:
                pattern = r'\b' + keyword + r'\b'
                highlighted = re.sub(pattern,
                                    lambda m: self.formatter._colorize(m.group(), 
                                                                      Color.BRIGHT_MAGENTA, 
                                                                      Color.BOLD),
                                    highlighted)
            
            # Strings
            highlighted = re.sub(r'"[^"]*"',
                               lambda m: self.formatter._colorize(m.group(), 
                                                                 Color.BRIGHT_GREEN),
                               highlighted)
            highlighted = re.sub(r"'[^']*'",
                               lambda m: self.formatter._colorize(m.group(), 
                                                                 Color.BRIGHT_GREEN),
                               highlighted)
            
            # Comments
            if '#' in highlighted:
                parts = highlighted.split('#', 1)
                if len(parts) == 2:
                    highlighted = parts[0] + self.formatter._colorize('#' + parts[1], 
                                                                     Color.BRIGHT_BLACK)
            
            # Numbers
            highlighted = re.sub(r'\b\d+\b',
                               lambda m: self.formatter._colorize(m.group(), 
                                                                 Color.BRIGHT_YELLOW),
                               highlighted)
            
            return highlighted
        
        # Default: return with base color
        return self.formatter._colorize(line, Color.BRIGHT_BLUE)
    
    def _display_code_examples(self, examples: List[Dict[str, Any]]) -> None:
        """Display code examples section"""
        print(self.formatter._colorize(">>> 💻 Code Examples >>>", 
                                       Color.BRIGHT_GREEN, Color.BOLD))
        print(self.formatter._colorize("=" * 60, Color.BRIGHT_GREEN))
        print()
        
        for i, example in enumerate(examples, 1):
            # Example title
            title = example.get('title', f'Example {i}')
            print(self.formatter._colorize(f"▸ {title}", Color.BRIGHT_YELLOW, Color.BOLD))
            
            # Description
            if 'description' in example:
                desc = self._process_inline_formatting(example['description'])
                wrapped = textwrap.fill(desc, width=self.width - 4,
                                       initial_indent="  ", subsequent_indent="  ")
                print(wrapped)
                print()
            
            # Code
            if 'code' in example:
                code_lines = example['code'].split('\n')
                self._display_code_block(code_lines, example.get('language', 'python'))
            
            # Output
            if 'output' in example:
                print(self.formatter._colorize("  Output:", Color.BRIGHT_CYAN, Color.BOLD))
                output_lines = str(example['output']).split('\n')
                for line in output_lines:
                    print(self.formatter._colorize(f"    {line}", Color.GREEN))
                print()
    
    def _display_practice_problems(self, problems: List[Dict[str, Any]]) -> None:
        """Display practice problems section"""
        print(self.formatter._colorize(">>> 🎯 Practice Exercises >>>", 
                                       Color.BRIGHT_MAGENTA, Color.BOLD))
        print(self.formatter._colorize("=" * 60, Color.BRIGHT_MAGENTA))
        print()
        
        for i, problem in enumerate(problems, 1):
            # Problem number and title
            title = problem.get('title', f'Problem {i}')
            difficulty = problem.get('difficulty', 'medium')
            
            # Create problem header with difficulty badge
            badge = self._create_difficulty_badge(difficulty)
            header = f"Problem {i}: {title} {badge}"
            print(self.formatter._colorize(header, Color.BRIGHT_YELLOW, Color.BOLD))
            print(self.formatter._colorize("-" * 40, Color.BRIGHT_YELLOW))
            
            # Description
            if 'description' in problem:
                desc = self._process_inline_formatting(problem['description'])
                wrapped = textwrap.fill(desc, width=self.width - 4,
                                       initial_indent="  ", subsequent_indent="  ")
                print(wrapped)
                print()
            
            # Example
            if 'example' in problem:
                print(self.formatter._colorize("  Example:", Color.BRIGHT_CYAN, Color.BOLD))
                example_text = problem['example']
                for line in example_text.split('\n'):
                    print(self.formatter._colorize(f"    {line}", Color.CYAN))
                print()
            
            # Hint (if available)
            if 'hint' in problem:
                hint_text = self.formatter._colorize("[Hint available - press 'h' to reveal]", 
                                                    Color.BRIGHT_BLACK, Color.ITALIC)
                print(f"  {hint_text}")
                print()
    
    def _display_interactive_options(self) -> None:
        """Display interactive menu options"""
        # Create a simple rule with title
        print()
        print(self.formatter._colorize("═" * 30 + " Interactive Options " + "═" * 19, 
                                       Color.BRIGHT_CYAN, Color.BOLD))
        
        options = [
            ("[1]", "📝", "Take Notes", "Capture your thoughts and insights"),
            ("[2]", "🤖", "Claude Questions", "Get AI-powered explanations"),
            ("[3]", "💡", "Practice Problems", "8 problems available"),
            ("[4]", "🏃", "Mark Complete", "Finish and earn points"),
            ("[5]", "⏭️", "Skip to Next", "Continue without completing"),
            ("[0]", "🔙", "Back", "Return to curriculum")
        ]
        
        # Create formatted menu
        for key, icon, title, desc in options:
            key_colored = self.formatter._colorize(key, Color.BRIGHT_YELLOW, Color.BOLD)
            icon_colored = self.formatter._colorize(icon, Color.BRIGHT_CYAN)
            title_colored = self.formatter._colorize(title, Color.WHITE, Color.BOLD)
            desc_colored = self.formatter._colorize(f"- {desc}", Color.BRIGHT_BLACK)
            
            print(f"  {key_colored} {icon_colored} {title_colored} {desc_colored}")
        
        print()
    
    def format_real_world_impact(self, content: str) -> None:
        """Format and display real-world impact section with special styling"""
        print()
        print(self.formatter._colorize(">>> 🌍 Real-World Impact >>>", 
                                       Color.BRIGHT_GREEN, Color.BOLD))
        print(self.formatter._colorize("=" * 60, Color.BRIGHT_GREEN))
        print()
        
        # Parse the content for special formatting
        lines = content.split('\n')
        for line in lines:
            stripped = line.strip()
            
            # Company examples
            if any(company in stripped for company in ['Google', 'Amazon', 'Facebook', 'Microsoft', 'Apple']):
                # Highlight company names
                for company in ['Google', 'Amazon', 'Facebook', 'Microsoft', 'Apple']:
                    stripped = stripped.replace(company, 
                                              self.formatter._colorize(company, 
                                                                     Color.BRIGHT_CYAN, 
                                                                     Color.BOLD))
                print(f"  {stripped}")
            
            # Performance metrics
            elif any(metric in stripped for metric in ['O(', 'performance', 'speed', 'efficiency']):
                formatted = self.formatter._colorize(stripped, Color.BRIGHT_YELLOW)
                print(f"  {formatted}")
            
            # Regular content
            elif stripped:
                print(f"  {stripped}")
            else:
                print()
    
    def format_key_insight(self, insight: str) -> None:
        """Format and display key insights with special emphasis"""
        print()
        box_content = f"💡 KEY INSIGHT\n\n{insight}"
        # Create a simple box for the insight
        lines = box_content.split('\n')
        max_len = max(len(line) for line in lines)
        box_width = min(max_len + 4, 70)
        
        print(self.formatter._colorize("╔" + "═" * (box_width - 2) + "╗", Color.BRIGHT_YELLOW, Color.BOLD))
        for line in lines:
            padded = line.center(box_width - 2)
            print(self.formatter._colorize("║" + padded + "║", Color.BRIGHT_YELLOW, Color.BOLD))
        print(self.formatter._colorize("╚" + "═" * (box_width - 2) + "╝", Color.BRIGHT_YELLOW, Color.BOLD))
        print()