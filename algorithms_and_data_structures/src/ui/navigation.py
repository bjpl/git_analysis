#!/usr/bin/env python3
"""
Enhanced Navigation System - Arrow key navigation with fallback
"""

import asyncio
import sys
import os
from typing import List, Tuple, Optional, Callable, Any, Dict
from dataclasses import dataclass
from enum import Enum

from .formatter import TerminalFormatter, Color, Theme


class NavigationMode(Enum):
    """Navigation input modes"""
    ARROW_KEYS = "arrow_keys"
    NUMBER_INPUT = "number_input"
    HYBRID = "hybrid"


@dataclass
class MenuItem:
    """Menu item with enhanced properties"""
    key: str
    icon: str
    title: str
    description: str
    action: Optional[Callable] = None
    shortcut: Optional[str] = None
    enabled: bool = True
    color: Optional[Color] = None


class NavigationController:
    """Enhanced navigation controller with arrow key support"""
    
    def __init__(self, formatter: TerminalFormatter):
        """Initialize navigation controller"""
        self.formatter = formatter
        self.current_index = 0
        self.mode = NavigationMode.HYBRID
        self.items: List[MenuItem] = []
        self.title = ""
        self.show_instructions = True
        self.auto_select_timeout = 0  # 0 = disabled
        
        # Performance optimization for Windows
        self._input_buffer = []
        self._last_render_time = 0
        self._min_render_interval = 0.05  # 50ms minimum between renders
    
    async def show_menu(self, title: str, items: List[MenuItem], 
                       selected_index: int = 0, 
                       mode: NavigationMode = NavigationMode.HYBRID) -> Tuple[int, str]:
        """Display and handle menu navigation
        
        Args:
            title: Menu title
            items: List of menu items
            selected_index: Initially selected item index
            mode: Navigation mode
            
        Returns:
            Tuple of (selected_index, action_key)
        """
        self.title = title
        self.items = items
        self.current_index = max(0, min(selected_index, len(items) - 1))
        self.mode = mode
        
        # Initial render
        await self._render_menu()
        
        while True:
            try:
                # Get input based on mode
                if mode == NavigationMode.ARROW_KEYS:
                    key = await self._get_arrow_input()
                elif mode == NavigationMode.NUMBER_INPUT:
                    key = await self._get_number_input()
                else:  # HYBRID
                    key = await self._get_hybrid_input()
                
                # Handle navigation
                action = await self._handle_input(key)
                if action:
                    return self.current_index, action
                    
            except KeyboardInterrupt:
                return -1, "quit"
            except Exception as e:
                self.formatter.error(f"Navigation error: {e}")
                return -1, "error"
    
    async def _render_menu(self) -> None:
        """Render the menu with current selection"""
        # Performance optimization - throttle renders
        current_time = asyncio.get_event_loop().time()
        if current_time - self._last_render_time < self._min_render_interval:
            return
        self._last_render_time = current_time
        
        # Clear screen with transition effect
        self.formatter.transition_effect("fade")
        self._clear_screen()
        
        # Render title with academic styling
        print(self.formatter.header(self.title, level=1))
        
        # Render menu items with selection highlighting
        self._render_items()
        
        # Render navigation instructions
        if self.show_instructions:
            self._render_instructions()
    
    def _render_items(self) -> None:
        """Render menu items with highlighting"""
        print()  # Spacing
        
        for i, item in enumerate(self.items):
            if not item.enabled:
                # Disabled item
                line = f"   {item.icon} {item.title} - {item.description}"
                print(self.formatter._colorize(line, Color.BRIGHT_BLACK))
                continue
            
            # Determine if this item is selected
            is_selected = (i == self.current_index)
            
            # Create the display line
            if is_selected:
                # Selected item with enhanced styling
                prefix = "▶ "
                line = f"{prefix}{item.icon} {item.title}"
                
                # Box around selected item
                padding = " " * 2
                box_content = f"{padding}{line}{padding}"
                border_char = "━"
                
                print(f"   ┌{border_char * (len(box_content) - 4)}┐")
                colored_line = self.formatter._colorize(box_content, 
                                                       Color.BRIGHT_YELLOW, Color.BOLD)
                print(f"   │{colored_line}│")
                print(f"   └{border_char * (len(box_content) - 4)}┘")
                
                # Description on separate line
                desc_line = f"     {item.description}"
                print(self.formatter._colorize(desc_line, Color.BRIGHT_CYAN))
            else:
                # Unselected item
                prefix = "  "
                number = f"[{item.key}]" if item.key.isdigit() else f"[{item.key}]"
                line = f"{prefix}{number} {item.icon} {item.title}"
                
                # Use item color or default
                color = item.color or self.formatter.theme.text
                print(self.formatter._colorize(line, color))
                
                # Subtle description
                desc_line = f"      {item.description}"
                print(self.formatter._colorize(desc_line, Color.BRIGHT_BLACK))
        
        print()  # Spacing
    
    def _render_instructions(self) -> None:
        """Render navigation instructions"""
        instructions = []
        
        if self.mode in [NavigationMode.ARROW_KEYS, NavigationMode.HYBRID]:
            instructions.append("↑↓ Navigate")
            instructions.append("Enter Select")
        
        if self.mode in [NavigationMode.NUMBER_INPUT, NavigationMode.HYBRID]:
            instructions.append("Number Keys")
        
        instructions.extend(["Esc/Q Quit", "? Help"])
        
        # Create instruction bar
        instruction_text = " | ".join(instructions)
        border = "─" * len(instruction_text)
        
        print(self.formatter._colorize(f"┌{border}┐", Color.BRIGHT_BLACK))
        print(self.formatter._colorize(f"│{instruction_text}│", Color.BRIGHT_WHITE))
        print(self.formatter._colorize(f"└{border}┘", Color.BRIGHT_BLACK))
    
    async def _get_hybrid_input(self) -> str:
        """Get input in hybrid mode (arrow keys + numbers)"""
        # Check for immediate number input
        if os.name == 'nt':
            import msvcrt
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key.isdigit():
                    return key.decode('utf-8')
                elif key == b'\xe0':  # Arrow key prefix
                    arrow = msvcrt.getch()
                    if arrow == b'H':
                        return 'UP'
                    elif arrow == b'P':
                        return 'DOWN'
                elif key == b'\r':
                    return 'ENTER'
                elif key in [b'\x1b', b'q', b'Q']:
                    return 'QUIT'
                elif key == b'?':
                    return 'HELP'
        
        # Fallback to input() for non-Windows or complex input
        try:
            user_input = input(self.formatter._colorize("\n➤ Your choice: ", 
                                                       Color.BRIGHT_GREEN)).strip()
            
            # Parse input
            if user_input.upper() in ['Q', 'QUIT', 'EXIT']:
                return 'QUIT'
            elif user_input == '?':
                return 'HELP'
            elif user_input.isdigit():
                return user_input
            elif user_input.upper() in ['U', 'UP']:
                return 'UP'
            elif user_input.upper() in ['D', 'DOWN']:
                return 'DOWN'
            elif user_input in ['', '\n']:
                return 'ENTER'
            else:
                return user_input.upper()
                
        except (EOFError, KeyboardInterrupt):
            return 'QUIT'
    
    async def _get_arrow_input(self) -> str:
        """Get arrow key input"""
        return self.formatter.get_key_input()
    
    async def _get_number_input(self) -> str:
        """Get number input"""
        try:
            choice = input(self.formatter._colorize("\nEnter choice number: ", 
                                                   Color.BRIGHT_GREEN)).strip()
            return choice
        except (EOFError, KeyboardInterrupt):
            return 'QUIT'
    
    async def _handle_input(self, key: str) -> Optional[str]:
        """Handle input and return action if menu should exit"""
        if key in ['QUIT', 'ESCAPE', 'Q']:
            return 'quit'
        
        elif key == 'UP':
            # Move up, wrap around
            self.current_index = (self.current_index - 1) % len(self.items)
            # Skip disabled items
            while not self.items[self.current_index].enabled:
                self.current_index = (self.current_index - 1) % len(self.items)
            await self._render_menu()
            
        elif key == 'DOWN':
            # Move down, wrap around
            self.current_index = (self.current_index + 1) % len(self.items)
            # Skip disabled items
            while not self.items[self.current_index].enabled:
                self.current_index = (self.current_index + 1) % len(self.items)
            await self._render_menu()
            
        elif key == 'ENTER':
            # Select current item
            if self.items[self.current_index].enabled:
                return self.items[self.current_index].key
            
        elif key == 'HELP':
            await self._show_help()
            await self._render_menu()
            
        elif key.isdigit():
            # Direct number selection
            try:
                # Find item with matching key
                for i, item in enumerate(self.items):
                    if item.key == key and item.enabled:
                        self.current_index = i
                        return item.key
                
                # If no exact match, try as index
                index = int(key) - 1
                if 0 <= index < len(self.items) and self.items[index].enabled:
                    self.current_index = index
                    return self.items[index].key
                    
            except (ValueError, IndexError):
                pass
        
        else:
            # Try to match by key
            for i, item in enumerate(self.items):
                if item.key.upper() == key.upper() and item.enabled:
                    self.current_index = i
                    return item.key
        
        return None
    
    async def _show_help(self) -> None:
        """Show help information"""
        self._clear_screen()
        
        print(self.formatter.header("Navigation Help", level=2))
        
        help_content = """
        NAVIGATION CONTROLS:
        
        Arrow Keys:
        • ↑ / ↓     Navigate through menu items
        • Enter     Select highlighted item
        
        Number Keys:
        • 1-9       Direct selection by number
        
        Other Keys:
        • Q / Esc   Quit or go back
        • ?         Show this help
        
        FEATURES:
        • Use arrow keys for quick navigation
        • Type numbers for direct selection
        • Menu items wrap around (top to bottom)
        • Disabled items are automatically skipped
        
        TIPS:
        • Arrow keys work best in modern terminals
        • Number input always works as fallback
        • Mix both methods for fastest navigation
        """
        
        print(self.formatter.box(help_content, title="Help", 
                               style="single", padding=2, align="left"))
        
        input(self.formatter._colorize("\nPress Enter to continue...", 
                                      Color.BRIGHT_YELLOW))
    
    def _clear_screen(self) -> None:
        """Clear screen efficiently for Windows PowerShell"""
        try:
            if os.name == 'nt':
                # Windows - use ANSI escape codes for better performance
                print('\033[2J\033[H', end='')
                sys.stdout.flush()
            else:
                # Unix/Linux
                print('\033[2J\033[H', end='')
                sys.stdout.flush()
        except Exception:
            # Fallback - print newlines
            print('\n' * 3)


class QuizNavigation:
    """Specialized navigation for quiz systems"""
    
    def __init__(self, formatter: TerminalFormatter):
        self.formatter = formatter
        self.question_index = 0
        self.total_questions = 0
        self.user_answers: Dict[int, Any] = {}
        self.time_limit = None
        self.start_time = None
    
    async def show_question(self, question_data: Dict[str, Any], 
                          question_num: int, total: int) -> Tuple[str, bool]:
        """Show quiz question with navigation
        
        Args:
            question_data: Question data dictionary
            question_num: Current question number (1-based)
            total: Total number of questions
            
        Returns:
            Tuple of (answer, is_correct)
        """
        self.question_index = question_num - 1
        self.total_questions = total
        
        # Clear screen with effect
        self.formatter.transition_effect("slide")
        print('\033[2J\033[H', end='')
        
        # Progress indicator
        progress = (question_num / total) * 100
        progress_bar = await self.formatter.animated_progress_bar(
            total, f"Question Progress", "pulse"
        )
        await progress_bar.update(question_num)
        
        # Question header
        header_text = f"Question {question_num} of {total}"
        print(self.formatter.header(header_text, level=1))
        
        # Question content
        question_text = question_data.get('question', '')
        await self.formatter.type_text(question_text, speed=0.02)
        
        # Options
        options = question_data.get('options', [])
        correct_index = question_data.get('correct', 0)
        
        print("\n" + self.formatter._colorize("Choose your answer:", 
                                             Color.BRIGHT_CYAN, Color.BOLD))
        
        # Create menu items for options
        menu_items = []
        for i, option in enumerate(options):
            item = MenuItem(
                key=str(i + 1),
                icon="○",
                title=option,
                description="",
                color=Color.WHITE
            )
            menu_items.append(item)
        
        # Add navigation options
        nav_items = [
            MenuItem("S", "⏩", "Skip Question", "Move to next question"),
            MenuItem("B", "⏪", "Back", "Previous question", enabled=question_num > 1),
            MenuItem("Q", "🚪", "Quit Quiz", "Exit the quiz")
        ]
        
        all_items = menu_items + nav_items
        
        # Show navigation menu
        nav_controller = NavigationController(self.formatter)
        selected_index, action = await nav_controller.show_menu(
            "Select Your Answer", all_items, mode=NavigationMode.HYBRID
        )
        
        # Process result
        if action == 'Q':
            return "quit", False
        elif action == 'S':
            return "skip", False
        elif action == 'B':
            return "back", False
        elif action.isdigit():
            answer_index = int(action) - 1
            if 0 <= answer_index < len(options):
                is_correct = (answer_index == correct_index)
                
                # Visual feedback
                if is_correct:
                    feedback = self.formatter.success("Correct! ✓")
                    await self.formatter.type_text("\n🎉 Well done!", speed=0.05)
                else:
                    feedback = self.formatter.error("Incorrect ✗")
                    correct_answer = options[correct_index]
                    await self.formatter.type_text(
                        f"\n💡 The correct answer was: {correct_answer}", 
                        speed=0.03
                    )
                
                print(feedback)
                await asyncio.sleep(2)  # Show feedback
                
                return action, is_correct
        
        return "skip", False


class ProgressVisualization:
    """Real-time progress visualization system"""
    
    def __init__(self, formatter: TerminalFormatter):
        self.formatter = formatter
        self.current_progress = 0
        self.milestones = []
        self.achievements = []
    
    async def show_live_progress(self, total: int, current: int, 
                               title: str = "Progress") -> None:
        """Show live progress visualization
        
        Args:
            total: Total progress value
            current: Current progress value
            title: Progress title
        """
        # Clear area for progress display
        print('\033[2J\033[H', end='')
        
        # Title
        print(self.formatter.header(title, level=1))
        
        # Main progress bar with animation
        progress_bar = await self.formatter.animated_progress_bar(
            total, "Overall Progress", "pulse"
        )
        await progress_bar.update(current)
        
        # Progress percentage
        percentage = (current / total) * 100 if total > 0 else 0
        
        # Visual progress indicator
        self._render_progress_circle(percentage)
        
        # Milestones
        await self._render_milestones(percentage)
        
        # Performance stats
        await self._render_stats(current, total, percentage)
    
    def _render_progress_circle(self, percentage: float) -> None:
        """Render circular progress indicator"""
        # ASCII art progress circle
        circle_chars = ["○", "◔", "◑", "◕", "●"]
        filled_index = int((percentage / 100) * (len(circle_chars) - 1))
        circle_char = circle_chars[filled_index]
        
        # Create visual representation
        lines = [
            "    Progress Visualization    ",
            "                              ",
            f"        {circle_char} {percentage:5.1f}%        ",
            "                              "
        ]
        
        # Box it with color
        content = "\n".join(lines)
        print(self.formatter.box(content, title="Visual Progress", 
                               style="rounded", color=Color.BRIGHT_GREEN))
    
    async def _render_milestones(self, percentage: float) -> None:
        """Render progress milestones"""
        milestones = [
            (25, "🌱", "Getting Started"),
            (50, "🚀", "Halfway There"),
            (75, "🔥", "Almost Done"),
            (100, "🏆", "Complete!")
        ]
        
        print(self.formatter._colorize("\nMilestones:", Color.BRIGHT_YELLOW, Color.BOLD))
        
        for threshold, icon, description in milestones:
            if percentage >= threshold:
                # Achieved milestone
                line = f"  {icon} {description} ✓"
                print(self.formatter._colorize(line, Color.BRIGHT_GREEN))
            else:
                # Not yet achieved
                line = f"  ⚪ {description}"
                print(self.formatter._colorize(line, Color.BRIGHT_BLACK))
    
    async def _render_stats(self, current: int, total: int, percentage: float) -> None:
        """Render performance statistics"""
        remaining = total - current
        
        stats_content = f"""Current: {current:>8}
Total:   {total:>8}
Remaining: {remaining:>6}
Progress: {percentage:>6.1f}%"""
        
        print(self.formatter.box(stats_content, title="Statistics", 
                               style="single", color=Color.BRIGHT_BLUE))