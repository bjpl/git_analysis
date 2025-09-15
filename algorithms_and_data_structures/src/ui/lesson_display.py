#!/usr/bin/env python3
"""
Lesson Display Module - Beautiful formatting for algorithm lessons
Handles the display of educational content with proper formatting, frames, and visual hierarchy
"""

import re
import textwrap
from typing import List, Optional, Tuple
from .formatter import TerminalFormatter, Color


class LessonDisplay:
    """Display lessons with beautiful formatting and visual elements"""
    
    def __init__(self, formatter: Optional[TerminalFormatter] = None):
        """Initialize lesson display with formatter"""
        self.formatter = formatter or TerminalFormatter()
        self.width = self.formatter.width
        
    def display_lesson(self, content: str, title: Optional[str] = None) -> None:
        """
        Display lesson content with beautiful formatting
        
        Args:
            content: Lesson content with markdown-like formatting
            title: Optional lesson title
        """
        # Display title in a beautiful frame if provided
        if title:
            self._display_title_frame(title)
        
        # Parse and display content with proper formatting
        lines = content.split('\n')
        code_block = False
        code_lines = []
        
        for line in lines:
            # Handle code blocks
            if line.strip().startswith('```'):
                if code_block:
                    # End of code block - display it
                    self._display_code_block('\n'.join(code_lines), 
                                            lang=line.strip('```').strip())
                    code_lines = []
                    code_block = False
                else:
                    # Start of code block
                    code_block = True
                continue
            
            if code_block:
                code_lines.append(line)
                continue
            
            # Handle different line types
            if line.startswith('###'):
                self._display_heading(line.strip('#').strip(), level=3)
            elif line.startswith('##'):
                self._display_heading(line.strip('#').strip(), level=2)
            elif line.startswith('#'):
                self._display_heading(line.strip('#').strip(), level=1)
            elif line.strip().startswith('**') and line.strip().endswith('**'):
                # Bold line
                self._display_emphasized(line.strip('*').strip())
            elif line.strip().startswith('-'):
                # Bullet point
                self._display_bullet(line.strip('-').strip())
            elif line.strip().startswith(tuple(str(i) + '.' for i in range(1, 10))):
                # Numbered list
                self._display_numbered(line.strip())
            elif line.strip() == '':
                # Empty line
                print()
            else:
                # Regular paragraph
                self._display_paragraph(line)
    
    def _display_title_frame(self, title: str) -> None:
        """Display title in a beautiful frame"""
        # Calculate frame dimensions
        padding = 4
        title_len = len(title) + padding * 2
        frame_width = min(max(title_len, 60), self.width - 4)
        
        # Center the title
        centered_title = title.center(frame_width - 2)
        
        # Create the frame using ASCII characters for Windows compatibility
        top_border = "+" + "=" * (frame_width - 2) + "+"
        middle = "|" + centered_title + "|"
        bottom_border = "+" + "=" * (frame_width - 2) + "+"
        
        # Display with color
        print(self.formatter._colorize(top_border, Color.BRIGHT_CYAN, Color.BOLD))
        print(self.formatter._colorize(middle, Color.BRIGHT_CYAN, Color.BOLD))
        print(self.formatter._colorize(bottom_border, Color.BRIGHT_CYAN, Color.BOLD))
        print()
    
    def _display_heading(self, text: str, level: int = 1) -> None:
        """Display a heading with appropriate formatting"""
        print()  # Add space before heading
        
        if level == 1:
            # Main heading - large and bold with underline
            colored_text = self.formatter._colorize(text.upper(), 
                                                    Color.BRIGHT_YELLOW, 
                                                    Color.BOLD)
            print(colored_text)
            underline = "=" * len(text)
            print(self.formatter._colorize(underline, Color.BRIGHT_YELLOW))
        elif level == 2:
            # Sub-heading - medium with arrow
            arrow = self.formatter._colorize("->", Color.BRIGHT_CYAN, Color.BOLD)
            heading_text = self.formatter._colorize(text, 
                                                   Color.BRIGHT_CYAN, 
                                                   Color.BOLD)
            print(f"{arrow} {heading_text}")
        else:
            # Minor heading - smaller with indent
            bullet = self.formatter._colorize(">", Color.BRIGHT_GREEN)
            heading_text = self.formatter._colorize(text, 
                                                   Color.BRIGHT_GREEN, 
                                                   Color.BOLD)
            print(f"  {bullet} {heading_text}")
        
        print()  # Add space after heading
    
    def _display_paragraph(self, text: str) -> None:
        """Display a paragraph with proper wrapping and indentation"""
        # Handle inline formatting
        text = self._process_inline_formatting(text)
        
        # Wrap text to terminal width
        wrapped = textwrap.fill(text, 
                              width=self.width - 4,
                              initial_indent="  ",
                              subsequent_indent="  ")
        
        # Apply color
        colored = self.formatter._colorize(wrapped, Color.WHITE)
        print(colored)
    
    def _display_bullet(self, text: str) -> None:
        """Display a bullet point"""
        bullet = self.formatter._colorize("*", Color.BRIGHT_CYAN, Color.BOLD)
        text = self._process_inline_formatting(text)
        
        # Wrap with proper indentation
        wrapped = textwrap.fill(text,
                              width=self.width - 6,
                              initial_indent="",
                              subsequent_indent="    ")
        
        colored_text = self.formatter._colorize(wrapped, Color.WHITE)
        print(f"  {bullet} {colored_text}")
    
    def _display_numbered(self, text: str) -> None:
        """Display a numbered list item"""
        # Extract number and text
        parts = text.split('.', 1)
        if len(parts) == 2:
            num = parts[0].strip()
            content = parts[1].strip()
            
            num_colored = self.formatter._colorize(f"{num}.", 
                                                  Color.BRIGHT_YELLOW, 
                                                  Color.BOLD)
            content = self._process_inline_formatting(content)
            
            # Wrap with indentation
            wrapped = textwrap.fill(content,
                                  width=self.width - 8,
                                  initial_indent="",
                                  subsequent_indent="     ")
            
            colored_text = self.formatter._colorize(wrapped, Color.WHITE)
            print(f"  {num_colored} {colored_text}")
    
    def _display_emphasized(self, text: str) -> None:
        """Display emphasized (bold) text"""
        colored = self.formatter._colorize(text, Color.BRIGHT_WHITE, Color.BOLD)
        print(f"  {colored}")
    
    def _display_code_block(self, code: str, lang: str = "python") -> None:
        """Display a code block with syntax highlighting simulation"""
        # Create a bordered box for code using ASCII characters
        lines = code.split('\n')
        max_len = max(len(line) for line in lines) if lines else 0
        box_width = min(max_len + 4, self.width - 4)
        
        # Box borders using ASCII for Windows compatibility
        top = "  +" + "-" * (box_width - 2) + "+"
        bottom = "  +" + "-" * (box_width - 2) + "+"
        
        print(self.formatter._colorize(top, Color.BRIGHT_BLACK))
        
        # Display code lines with simulated syntax highlighting
        for line in lines:
            # Simple syntax highlighting
            highlighted = self._highlight_code(line, lang)
            padded = highlighted.ljust(box_width - 4)
            border_left = self.formatter._colorize("  | ", Color.BRIGHT_BLACK)
            border_right = self.formatter._colorize(" |", Color.BRIGHT_BLACK)
            print(f"{border_left}{padded}{border_right}")
        
        print(self.formatter._colorize(bottom, Color.BRIGHT_BLACK))
        print()
    
    def _highlight_code(self, line: str, lang: str) -> str:
        """Apply simple syntax highlighting to code"""
        if lang.lower() in ['python', 'py']:
            # Python keywords
            keywords = ['def', 'return', 'if', 'else', 'elif', 'for', 'while', 
                       'in', 'not', 'and', 'or', 'None', 'True', 'False',
                       'class', 'import', 'from', 'as', 'try', 'except']
            
            highlighted = line
            
            # Highlight keywords
            for keyword in keywords:
                pattern = r'\b' + keyword + r'\b'
                replacement = self.formatter._colorize(keyword, 
                                                      Color.BRIGHT_MAGENTA, 
                                                      Color.BOLD)
                highlighted = re.sub(pattern, replacement, highlighted)
            
            # Highlight strings (simple version)
            highlighted = re.sub(r'"[^"]*"', 
                               lambda m: self.formatter._colorize(m.group(), 
                                                                 Color.BRIGHT_GREEN),
                               highlighted)
            highlighted = re.sub(r"'[^']*'", 
                               lambda m: self.formatter._colorize(m.group(), 
                                                                 Color.BRIGHT_GREEN),
                               highlighted)
            
            # Highlight comments
            if '#' in highlighted:
                parts = highlighted.split('#', 1)
                if len(parts) == 2:
                    comment = self.formatter._colorize('#' + parts[1], 
                                                      Color.BRIGHT_BLACK)
                    highlighted = parts[0] + comment
            
            return highlighted
        
        # Default: return as-is with default color
        return self.formatter._colorize(line, Color.BRIGHT_BLUE)
    
    def _process_inline_formatting(self, text: str) -> str:
        """Process inline markdown-style formatting"""
        # Bold text
        text = re.sub(r'\*\*([^*]+)\*\*', 
                     lambda m: self.formatter._colorize(m.group(1), 
                                                       Color.BRIGHT_WHITE, 
                                                       Color.BOLD),
                     text)
        
        # Inline code
        text = re.sub(r'`([^`]+)`',
                     lambda m: self.formatter._colorize(m.group(1), 
                                                       Color.BRIGHT_CYAN),
                     text)
        
        return text
    
    def display_practice_problem(self, problem: dict) -> None:
        """Display a practice problem with nice formatting"""
        # Problem title in a box
        self._display_problem_box(problem.get('title', 'Practice Problem'),
                                 problem.get('description', ''),
                                 problem.get('example', ''))
        
        # Hints if available
        if 'hints' in problem:
            print(self.formatter._colorize("\n[Hint] Hints available - press 'h' to reveal",
                                          Color.BRIGHT_YELLOW))
    
    def _display_problem_box(self, title: str, description: str, example: str) -> None:
        """Display a practice problem in a formatted box"""
        box_width = min(70, self.width - 4)
        
        # Create the box using ASCII characters for Windows compatibility
        top = "+" + "=" * (box_width - 2) + "+"
        divider = "+" + "-" * (box_width - 2) + "+"
        bottom = "+" + "=" * (box_width - 2) + "+"
        
        print(self.formatter._colorize(top, Color.BRIGHT_CYAN))
        
        # Title
        title_line = f"| {title.center(box_width - 4)} |"
        print(self.formatter._colorize(title_line, Color.BRIGHT_CYAN, Color.BOLD))
        
        print(self.formatter._colorize(divider, Color.BRIGHT_CYAN))
        
        # Description
        desc_lines = textwrap.wrap(description, width=box_width - 6)
        for line in desc_lines:
            padded_line = f"|  {line.ljust(box_width - 5)} |"
            print(self.formatter._colorize(padded_line, Color.WHITE))
        
        # Example if provided
        if example:
            print(self.formatter._colorize("|" + " " * (box_width - 2) + "|", 
                                          Color.BRIGHT_CYAN))
            print(self.formatter._colorize("|  Example:".ljust(box_width - 1) + "|", 
                                          Color.BRIGHT_GREEN, Color.BOLD))
            
            example_lines = example.split('\n')
            for line in example_lines:
                wrapped = textwrap.wrap(line, width=box_width - 8)
                for wrapped_line in wrapped:
                    padded_line = f"|    {wrapped_line.ljust(box_width - 7)} |"
                    print(self.formatter._colorize(padded_line, 
                                                  Color.BRIGHT_BLUE))
        
        print(self.formatter._colorize(bottom, Color.BRIGHT_CYAN))