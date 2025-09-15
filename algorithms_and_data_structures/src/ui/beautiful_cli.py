#!/usr/bin/env python3
"""
Beautiful CLI - Combining Academic Elegance with Professional Documentation
Inspired by Version 1 (Elegant Academic) and Version 5 (Professional Documentation)
Optimized for Windows PowerShell
"""

import sys
import os
import time
import random
from typing import Optional, List, Dict, Any
from enum import Enum

# Enhanced color codes for beautiful CLI output  
class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    
    # Bright colors for Windows PowerShell
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Bright colors (better for Windows)
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    
    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"


class BeautifulCLI:
    """Beautiful CLI implementation combining best of Version 1 and 5"""
    
    def __init__(self):
        """Initialize the beautiful CLI"""
        self.width = self._get_terminal_width()
        self.enable_animations = True
        self.typing_speed = 0.03  # Seconds per character
        
    def _get_terminal_width(self) -> int:
        """Get terminal width"""
        try:
            import shutil
            return min(shutil.get_terminal_size().columns, 100)
        except:
            return 80
    
    def colorize(self, text: str, color: str, style: str = "") -> str:
        """Apply color and optional style to text"""
        return f"{color}{style}{text}{Color.RESET}"
    
    def typing_effect(self, text: str, color: str = Color.WHITE, speed: float = None):
        """Create typing animation effect"""
        if not self.enable_animations:
            print(self.colorize(text, color))
            return
            
        speed = speed or self.typing_speed
        for char in text:
            sys.stdout.write(self.colorize(char, color))
            sys.stdout.flush()
            time.sleep(speed)
        print()  # New line at the end
    
    def gradient_text(self, text: str, start_color: str = Color.BRIGHT_CYAN, 
                     end_color: str = Color.BRIGHT_MAGENTA) -> str:
        """Create gradient effect with colors"""
        # For simplicity, alternate between colors
        colors = [start_color, Color.BRIGHT_BLUE, end_color]
        result = ""
        for i, char in enumerate(text):
            color = colors[i % len(colors)]
            result += self.colorize(char, color)
        return result
    
    def create_header_v1_style(self, title: str, subtitle: str = ""):
        """Create Version 1 style elegant academic header"""
        width = min(78, self.width - 2)
        
        # Beautiful header with rich borders (ASCII-safe for Windows)
        print(self.colorize("+" + "=" * width + "+", Color.BRIGHT_CYAN))
        
        # Title line with emoji and formatting
        title_line = f"  ALGORITHMS MASTERY: {title}  "
        padding = width - len(title_line)
        print(self.colorize("|", Color.BRIGHT_CYAN) + 
              self.colorize(title_line, Color.BRIGHT_WHITE, Color.BOLD) +
              " " * padding +
              self.colorize("|", Color.BRIGHT_CYAN))
        
        if subtitle:
            subtitle_line = f"  {subtitle}  "
            padding = width - len(subtitle_line)
            print(self.colorize("|", Color.BRIGHT_CYAN) + 
                  self.colorize(subtitle_line, Color.CYAN) +
                  " " * padding +
                  self.colorize("|", Color.BRIGHT_CYAN))
        
        print(self.colorize("+" + "=" * width + "+", Color.BRIGHT_CYAN))
    
    def create_learning_journey_box(self, items: List[tuple]):
        """Create learning journey section inspired by Version 1"""
        width = min(78, self.width - 2)
        
        print("\n" + self.colorize("+--- ", Color.BRIGHT_BLUE) + 
              self.colorize("Today's Learning Journey", Color.BRIGHT_YELLOW, Color.BOLD) +
              self.colorize(" " + "-" * (width - 28) + "+", Color.BRIGHT_BLUE))
        
        print(self.colorize("|", Color.BRIGHT_BLUE))
        
        for icon, title, description in items:
            line = f"  {icon} {title}: {description}"
            print(self.colorize("|", Color.BRIGHT_BLUE) + 
                  self.colorize("  > ", Color.GREEN, Color.BOLD) +
                  self.colorize(f"{title}:", Color.GREEN, Color.BOLD) + 
                  f" {description}")
        
        print(self.colorize("|", Color.BRIGHT_BLUE))
        print(self.colorize("+" + "-" * width + "+", Color.BRIGHT_BLUE))
    
    def create_key_insight_box(self, insight: str, details: str = ""):
        """Create key insight box inspired by Version 1"""
        width = 40
        
        print("\n" + self.colorize("+", Color.MAGENTA) + 
              self.colorize("-" * width, Color.MAGENTA) +
              self.colorize("+", Color.MAGENTA))
        
        # Title centered
        title = "KEY INSIGHT"
        padding = (width - len(title)) // 2
        print(self.colorize("|", Color.MAGENTA) + 
              " " * padding +
              self.colorize(title, Color.BRIGHT_YELLOW, Color.BOLD) +
              " " * (width - padding - len(title)) +
              self.colorize("|", Color.MAGENTA))
        
        print(self.colorize("+", Color.MAGENTA) + 
              self.colorize("-" * width, Color.MAGENTA) +
              self.colorize("+", Color.MAGENTA))
        
        # Insight text
        print(self.colorize("|", Color.MAGENTA) + 
              f"  {insight[:width-4]}  " +
              self.colorize("|", Color.MAGENTA))
        
        if details:
            print(self.colorize("|", Color.MAGENTA) + 
                  f"  {details[:width-4]}  " +
                  self.colorize("|", Color.MAGENTA))
        
        print(self.colorize("+", Color.MAGENTA) + 
              self.colorize("-" * width, Color.MAGENTA) +
              self.colorize("+", Color.MAGENTA))
    
    def create_professional_section_v5(self, title: str, sections: Dict[str, List[str]]):
        """Create Version 5 style professional documentation section"""
        width = 70
        
        # Professional header with line
        print("\n" + self.colorize("=" * width, Color.BRIGHT_BLACK))
        print(self.colorize(title.upper(), Color.BRIGHT_WHITE, Color.BOLD))
        print(self.colorize("=" * width, Color.BRIGHT_BLACK))
        
        # Contents with hierarchy
        print(self.colorize("\nCONTENTS", Color.BRIGHT_BLUE, Color.BOLD))
        
        for i, (section, items) in enumerate(sections.items(), 1):
            # Main section
            print(self.colorize("+- ", Color.BRIGHT_BLACK) + f"{i}. {section}")
            
            # Sub-items
            for j, item in enumerate(items, 1):
                if j == len(items):
                    print(self.colorize("|  +- ", Color.BRIGHT_BLACK) + f"{i}.{j} {item}")
                else:
                    print(self.colorize("|  +- ", Color.BRIGHT_BLACK) + f"{i}.{j} {item}")
    
    def create_definition_box(self, term: str, definition: str):
        """Create professional definition box inspired by Version 5"""
        width = 56
        
        print("\n" + self.colorize("+- DEFINITION " + "-" * (width - 13) + "+", Color.BRIGHT_GREEN))
        
        # Term and definition
        print(self.colorize("|", Color.BRIGHT_GREEN) + 
              self.colorize(f" {term}:", Color.BRIGHT_WHITE, Color.BOLD) + 
              f" {definition[:width-len(term)-5]}")
        
        # Wrap long definitions
        if len(definition) > width - len(term) - 5:
            remaining = definition[width-len(term)-5:]
            words = remaining.split()
            line = ""
            for word in words:
                if len(line) + len(word) + 1 <= width - 3:
                    line += word + " "
                else:
                    if line:
                        print(self.colorize("|", Color.BRIGHT_GREEN) + f" {line}")
                    line = word + " "
            if line:
                print(self.colorize("|", Color.BRIGHT_GREEN) + f" {line}")
        
        print(self.colorize("+" + "-" * width + "+", Color.BRIGHT_GREEN))
    
    def create_performance_table(self, data: List[tuple]):
        """Create performance table inspired by Version 5"""
        # Header
        print(self.colorize("\nPERFORMANCE", Color.BRIGHT_YELLOW, Color.BOLD))
        print(self.colorize("+-------------+-----------+-----------+", Color.WHITE))
        print(self.colorize("|", Color.WHITE) + 
              self.colorize(" Operation   ", Color.BRIGHT_CYAN, Color.BOLD) +
              self.colorize("|", Color.WHITE) +
              self.colorize(" Average   ", Color.BRIGHT_GREEN, Color.BOLD) +
              self.colorize("|", Color.WHITE) +
              self.colorize(" Worst     ", Color.BRIGHT_RED, Color.BOLD) +
              self.colorize("|", Color.WHITE))
        print(self.colorize("+-------------+-----------+-----------+", Color.WHITE))
        
        # Data rows
        for operation, average, worst in data:
            print(self.colorize("|", Color.WHITE) + 
                  f" {operation:11} " +
                  self.colorize("|", Color.WHITE) + " " +
                  self.colorize(f"{average:9}", Color.BRIGHT_GREEN) + " " +
                  self.colorize("|", Color.WHITE) + " " +
                  self.colorize(f"{worst:9}", Color.BRIGHT_RED) + " " +
                  self.colorize("|", Color.WHITE))
        
        print(self.colorize("+-------------+-----------+-----------+", Color.WHITE))
    
    def animated_progress_bar(self, total: int, description: str = "Progress"):
        """Create animated progress bar"""
        bar_length = 40
        
        for i in range(total + 1):
            percent = i / total
            filled = int(bar_length * percent)
            
            # Create bar
            bar = "#" * filled + "-" * (bar_length - filled)
            
            # Color based on progress
            if percent < 0.33:
                color = Color.BRIGHT_RED
            elif percent < 0.66:
                color = Color.BRIGHT_YELLOW
            else:
                color = Color.BRIGHT_GREEN
            
            # Display
            sys.stdout.write("\r")
            sys.stdout.write(f"{description}: [")
            sys.stdout.write(self.colorize(bar, color))
            sys.stdout.write(f"] {percent*100:6.1f}%")
            sys.stdout.flush()
            
            time.sleep(0.05)  # Animation speed
        
        print()  # New line when complete
    
    def show_menu_with_animation(self, title: str, options: List[tuple]):
        """Show menu with typing animation"""
        self.create_header_v1_style(title, "Interactive Learning Platform")
        
        print("\n" + self.colorize("Select an option:", Color.BRIGHT_CYAN, Color.BOLD))
        print()
        
        for option_tuple in options:
            num, icon, option, description = option_tuple
            # Animated appearance
            line = f"  [{num}] {icon} {option}"
            print(self.colorize(line, Color.BRIGHT_GREEN))
            
            # Description with indent
            desc_line = f"      {description}"
            print(self.colorize(desc_line, Color.BRIGHT_BLACK))
            
            if self.enable_animations:
                time.sleep(0.1)  # Stagger appearance
        
        print("\n" + self.colorize("=" * 60, Color.BRIGHT_CYAN))
    
    def demo_all_features(self):
        """Demonstrate all beautiful CLI features"""
        # Clear screen
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Version 1 Style: Elegant Academic
        print(self.gradient_text("=" * 80))
        print(self.gradient_text("     BEAUTIFUL CLI DEMONSTRATION     ".center(80)))
        print(self.gradient_text("=" * 80))
        
        # Header
        self.create_header_v1_style(
            "Understanding Arrays", 
            "Your Gateway to Efficient Data Management"
        )
        
        # Learning Journey
        journey_items = [
            ("", "Foundation", "What makes arrays special in computing"),
            ("", "Real World", "How Spotify uses arrays for playlists"),
            ("", "Deep Dive", "Memory layout and performance secrets")
        ]
        self.create_learning_journey_box(journey_items)
        
        # Key Insight
        self.create_key_insight_box(
            "Arrays = Numbered parking spaces",
            "Instant access with spot number!"
        )
        
        # Version 5 Style: Professional Documentation
        sections = {
            "Introduction to Arrays": [
                "What Problems Do They Solve?",
                "Real-World Applications"
            ],
            "Implementation Details": [
                "Memory Allocation",
                "Access Patterns",
                "Cache Optimization"
            ],
            "Practice Exercises": [
                "Basic Operations",
                "Advanced Algorithms"
            ]
        }
        self.create_professional_section_v5("ARRAYS & DATA STRUCTURES", sections)
        
        # Definition Box
        self.create_definition_box(
            "Array",
            "A data structure consisting of a collection of elements, each identified by an array index"
        )
        
        # Performance Table
        performance_data = [
            ("Access", "O(1)", "O(1)"),
            ("Search", "O(n)", "O(n)"),
            ("Insert", "O(n)", "O(n)"),
            ("Delete", "O(n)", "O(n)")
        ]
        self.create_performance_table(performance_data)
        
        # Animated Progress Bar
        print("\n" + self.colorize("Loading your learning experience...", Color.BRIGHT_YELLOW))
        self.animated_progress_bar(20, "Initializing")
        
        # Interactive Menu
        menu_options = [
            ("1", "📚", "Start Learning", "Begin with fundamentals"),
            ("2", "💪", "Practice Mode", "Hands-on exercises"),
            ("3", "🧠", "Quiz Time", "Test your knowledge"),
            ("4", "📊", "View Progress", "Track your journey"),
            ("5", "🚪", "Exit", "Save and quit")
        ]
        self.show_menu_with_animation("MAIN MENU", menu_options)
        
        # Footer
        print("\n" + self.colorize("=" * 80, Color.BRIGHT_CYAN))
        print(self.colorize("Ready to master algorithms? Let's begin!", 
                           Color.BRIGHT_MAGENTA, Color.BOLD).center(80))
        print(self.colorize("=" * 80, Color.BRIGHT_CYAN))


def main():
    """Main demonstration"""
    cli = BeautifulCLI()
    
    # Enable color support for Windows
    if sys.platform == 'win32':
        try:
            import colorama
            colorama.init()
        except ImportError:
            pass
    
    # Run demo
    cli.demo_all_features()
    
    # Wait for user
    input("\n" + cli.colorize("Press Enter to continue...", Color.BRIGHT_YELLOW))


if __name__ == "__main__":
    main()