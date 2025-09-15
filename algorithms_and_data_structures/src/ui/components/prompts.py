#!/usr/bin/env python3
"""
Beautiful Input Prompts - Enhanced input prompts with validation and styling

This module provides:
- Styled input prompts with validation
- Multi-choice selection menus
- Confirmation dialogs
- Password input with masking
- Autocomplete functionality
- Real-time validation feedback
"""

import sys
import os
import re
import time
from typing import List, Dict, Any, Optional, Union, Callable, Tuple
from enum import Enum
from dataclasses import dataclass
import difflib


class PromptStyle(Enum):
    """Input prompt styles"""
    DEFAULT = "default"
    MODERN = "modern"
    MINIMAL = "minimal"
    FANCY = "fancy"


class ValidationResult(Enum):
    """Validation result types"""
    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"


@dataclass
class ValidationResponse:
    """Response from input validation"""
    result: ValidationResult
    message: str = ""


class InputPrompt:
    """Enhanced input prompt with styling and validation"""
    
    def __init__(self, style: PromptStyle = PromptStyle.DEFAULT,
                 color_enabled: bool = True):
        """Initialize input prompt
        
        Args:
            style: Prompt visual style
            color_enabled: Whether colors are supported
        """
        self.style = style
        self.color_enabled = color_enabled
        
        # Style configurations
        self.styles = {
            PromptStyle.DEFAULT: {
                'prompt_char': '> ',
                'border_char': '-',
                'success_icon': '✓',
                'error_icon': '✗',
                'warning_icon': '⚠',
                'info_icon': 'ℹ'
            },
            PromptStyle.MODERN: {
                'prompt_char': '❯ ',
                'border_char': '─',
                'success_icon': '✅',
                'error_icon': '❌',
                'warning_icon': '⚠️',
                'info_icon': '💡'
            },
            PromptStyle.MINIMAL: {
                'prompt_char': ': ',
                'border_char': ' ',
                'success_icon': '+',
                'error_icon': 'x',
                'warning_icon': '!',
                'info_icon': 'i'
            },
            PromptStyle.FANCY: {
                'prompt_char': '╰─❯ ',
                'border_char': '═',
                'success_icon': '◆',
                'error_icon': '◇',
                'warning_icon': '◈',
                'info_icon': '◉'
            }
        }
        
        # Fallback to ASCII if Unicode not supported
        if not self._supports_unicode():
            self._fallback_to_ascii()
    
    def _supports_unicode(self) -> bool:
        """Check if terminal supports Unicode"""
        try:
            test_chars = "❯✓✗⚠ℹ"
            for char in test_chars:
                char.encode(sys.stdout.encoding or 'utf-8')
            return True
        except (UnicodeEncodeError, LookupError):
            return False
    
    def _fallback_to_ascii(self):
        """Fallback to ASCII-compatible characters"""
        ascii_styles = {
            PromptStyle.DEFAULT: {
                'prompt_char': '> ',
                'border_char': '-',
                'success_icon': '[OK]',
                'error_icon': '[ERROR]',
                'warning_icon': '[WARN]',
                'info_icon': '[INFO]'
            },
            PromptStyle.MODERN: {
                'prompt_char': '> ',
                'border_char': '-',
                'success_icon': '[+]',
                'error_icon': '[x]',
                'warning_icon': '[!]',
                'info_icon': '[i]'
            },
            PromptStyle.MINIMAL: {
                'prompt_char': ': ',
                'border_char': ' ',
                'success_icon': '+',
                'error_icon': 'x',
                'warning_icon': '!',
                'info_icon': 'i'
            },
            PromptStyle.FANCY: {
                'prompt_char': '>> ',
                'border_char': '=',
                'success_icon': '[OK]',
                'error_icon': '[ERR]',
                'warning_icon': '[WRN]',
                'info_icon': '[INF]'
            }
        }
        self.styles = ascii_styles
    
    def _get_style_config(self) -> Dict[str, str]:
        """Get current style configuration"""
        return self.styles.get(self.style, self.styles[PromptStyle.DEFAULT])
    
    def _colorize(self, text: str, color_code: str) -> str:
        """Apply color to text if colors are enabled"""
        if self.color_enabled:
            return f"{color_code}{text}\033[0m"
        return text
    
    def text_input(self, prompt: str, default: Optional[str] = None,
                  validator: Optional[Callable[[str], ValidationResponse]] = None,
                  placeholder: Optional[str] = None,
                  required: bool = False) -> str:
        """Get text input with validation
        
        Args:
            prompt: Prompt message
            default: Default value
            validator: Validation function
            placeholder: Placeholder text
            required: Whether input is required
            
        Returns:
            User input string
        """
        style_config = self._get_style_config()
        
        while True:
            # Build prompt line
            prompt_line = ""
            
            if self.style == PromptStyle.FANCY:
                # Fancy box-style prompt
                prompt_line += self._colorize("╭─ ", "\033[96m") if self.color_enabled else "+- "
                prompt_line += self._colorize(prompt, "\033[97m")
                
                if default:
                    prompt_line += self._colorize(f" (default: {default})", "\033[90m")
                
                prompt_line += "\n"
                prompt_line += self._colorize(style_config['prompt_char'], "\033[96m")
                
            else:
                # Standard prompt
                prompt_line += self._colorize(prompt, "\033[97m")
                
                if default:
                    prompt_line += self._colorize(f" (default: {default})", "\033[90m")
                
                if placeholder and not default:
                    prompt_line += self._colorize(f" [{placeholder}]", "\033[90m")
                
                prompt_line += self._colorize(style_config['prompt_char'], "\033[96m")
            
            # Get input
            try:
                user_input = input(prompt_line).strip()
            except (EOFError, KeyboardInterrupt):
                print()
                return default or ""
            
            # Use default if no input provided
            if not user_input and default:
                user_input = default
            
            # Check if required
            if required and not user_input:
                self._show_message("Input is required", ValidationResult.INVALID)
                continue
            
            # Validate input
            if validator and user_input:
                validation = validator(user_input)
                
                if validation.result == ValidationResult.INVALID:
                    self._show_message(validation.message, ValidationResult.INVALID)
                    continue
                elif validation.result == ValidationResult.WARNING:
                    self._show_message(validation.message, ValidationResult.WARNING)
                    # Continue with warning, don't break
            
            return user_input
    
    def password_input(self, prompt: str = "Password",
                      confirm: bool = False,
                      min_length: int = 0) -> str:
        """Get password input with masking
        
        Args:
            prompt: Prompt message
            confirm: Whether to confirm password
            min_length: Minimum password length
            
        Returns:
            Password string
        """
        import getpass
        
        while True:
            # First password input
            password_prompt = self._colorize(f"{prompt}: ", "\033[97m")
            try:
                password = getpass.getpass(password_prompt)
            except (EOFError, KeyboardInterrupt):
                print()
                return ""
            
            # Check minimum length
            if len(password) < min_length:
                self._show_message(f"Password must be at least {min_length} characters", 
                                 ValidationResult.INVALID)
                continue
            
            # Confirm password if requested
            if confirm:
                confirm_prompt = self._colorize("Confirm password: ", "\033[97m")
                try:
                    confirm_password = getpass.getpass(confirm_prompt)
                except (EOFError, KeyboardInterrupt):
                    print()
                    return ""
                
                if password != confirm_password:
                    self._show_message("Passwords do not match", ValidationResult.INVALID)
                    continue
            
            return password
    
    def number_input(self, prompt: str, min_value: Optional[float] = None,
                    max_value: Optional[float] = None,
                    integer_only: bool = False,
                    default: Optional[Union[int, float]] = None) -> Union[int, float]:
        """Get numeric input with validation
        
        Args:
            prompt: Prompt message
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            integer_only: Whether to accept only integers
            default: Default value
            
        Returns:
            Numeric value
        """
        def number_validator(value: str) -> ValidationResponse:
            try:
                if integer_only:
                    num = int(value)
                else:
                    num = float(value)
                
                if min_value is not None and num < min_value:
                    return ValidationResponse(ValidationResult.INVALID, 
                                            f"Value must be at least {min_value}")
                
                if max_value is not None and num > max_value:
                    return ValidationResponse(ValidationResult.INVALID,
                                            f"Value must be at most {max_value}")
                
                return ValidationResponse(ValidationResult.VALID)
                
            except ValueError:
                return ValidationResponse(ValidationResult.INVALID,
                                        "Please enter a valid number")
        
        # Build prompt with constraints
        constraint_info = []
        if min_value is not None:
            constraint_info.append(f"min: {min_value}")
        if max_value is not None:
            constraint_info.append(f"max: {max_value}")
        
        full_prompt = prompt
        if constraint_info:
            full_prompt += f" ({', '.join(constraint_info)})"
        
        while True:
            result = self.text_input(full_prompt, str(default) if default is not None else None,
                                   number_validator, required=True)
            
            try:
                if integer_only:
                    return int(result)
                else:
                    return float(result)
            except ValueError:
                continue
    
    def choice_input(self, prompt: str, choices: List[str],
                    default: Optional[str] = None,
                    show_indices: bool = True) -> str:
        """Get choice input from a list of options
        
        Args:
            prompt: Prompt message
            choices: List of choices
            default: Default choice
            show_indices: Whether to show numeric indices
            
        Returns:
            Selected choice
        """
        if not choices:
            return ""
        
        # Display choices
        print(self._colorize(f"\n{prompt}", "\033[97m"))
        
        for i, choice in enumerate(choices, 1):
            prefix = f"{i}. " if show_indices else "• "
            
            if choice == default:
                choice_line = self._colorize(f"  {prefix}{choice} (default)", "\033[92m")
            else:
                cyan_color = '\033[96m'
                choice_line = f"  {self._colorize(prefix, cyan_color)}{choice}"
            
            print(choice_line)
        
        # Get selection
        while True:
            if show_indices:
                selection_prompt = "Enter choice number"
                if default:
                    selection_prompt += f" (default: {default})"
                selection_prompt += ": "
                
                user_input = self.text_input(selection_prompt, 
                                           str(choices.index(default) + 1) if default in choices else None)
                
                try:
                    index = int(user_input) - 1
                    if 0 <= index < len(choices):
                        return choices[index]
                    else:
                        self._show_message("Invalid choice number", ValidationResult.INVALID)
                        continue
                except ValueError:
                    self._show_message("Please enter a valid number", ValidationResult.INVALID)
                    continue
            else:
                # Text-based selection
                user_input = self.text_input("Enter your choice", default)
                
                # Exact match
                if user_input in choices:
                    return user_input
                
                # Fuzzy matching
                matches = difflib.get_close_matches(user_input, choices, n=1, cutoff=0.6)
                if matches:
                    return matches[0]
                
                self._show_message("Invalid choice", ValidationResult.INVALID)
                continue
    
    def confirm_input(self, prompt: str, default: bool = False) -> bool:
        """Get yes/no confirmation
        
        Args:
            prompt: Confirmation prompt
            default: Default value
            
        Returns:
            Boolean confirmation result
        """
        yes_values = ['y', 'yes', 'true', '1', 'on']
        no_values = ['n', 'no', 'false', '0', 'off']
        
        default_text = "(Y/n)" if default else "(y/N)"
        full_prompt = f"{prompt} {default_text}"
        
        while True:
            result = self.text_input(full_prompt, "y" if default else "n")
            
            if result.lower() in yes_values:
                return True
            elif result.lower() in no_values:
                return False
            else:
                self._show_message("Please enter 'y' for yes or 'n' for no", 
                                 ValidationResult.INVALID)
    
    def autocomplete_input(self, prompt: str, suggestions: List[str],
                          min_chars: int = 1) -> str:
        """Get input with autocomplete suggestions
        
        Args:
            prompt: Prompt message
            suggestions: List of autocomplete suggestions
            min_chars: Minimum characters before showing suggestions
            
        Returns:
            User input
        """
        print(self._colorize(f"{prompt}", "\033[97m"))
        
        while True:
            user_input = self.text_input("Type to search (tab for suggestions)")
            
            if len(user_input) >= min_chars:
                # Find matching suggestions
                matches = [s for s in suggestions if s.lower().startswith(user_input.lower())]
                
                if matches:
                    if len(matches) == 1:
                        # Auto-complete if only one match
                        return matches[0]
                    else:
                        # Show suggestions
                        print(self._colorize("\nSuggestions:", "\033[93m"))
                        for i, match in enumerate(matches[:10], 1):  # Limit to 10
                            print(f"  {i}. {match}")
                        
                        # Ask user to choose or continue typing
                        choice = self.text_input("Select number or continue typing", user_input)
                        
                        try:
                            index = int(choice) - 1
                            if 0 <= index < len(matches):
                                return matches[index]
                        except ValueError:
                            user_input = choice
                            continue
                else:
                    print(self._colorize("No matches found", "\033[91m"))
            
            return user_input
    
    def _show_message(self, message: str, result_type: ValidationResult):
        """Show a validation or info message"""
        style_config = self._get_style_config()
        
        if result_type == ValidationResult.VALID:
            icon = style_config['success_icon']
            color = "\033[92m"  # Green
        elif result_type == ValidationResult.INVALID:
            icon = style_config['error_icon']
            color = "\033[91m"  # Red
        else:  # WARNING
            icon = style_config['warning_icon']
            color = "\033[93m"  # Yellow
        
        if self.color_enabled:
            print(f"{color}{icon} {message}\033[0m")
        else:
            print(f"{icon} {message}")


class MenuSelector:
    """Interactive menu selector with keyboard navigation"""
    
    def __init__(self, title: str, options: List[str],
                 color_enabled: bool = True):
        """Initialize menu selector
        
        Args:
            title: Menu title
            options: List of menu options
            color_enabled: Whether colors are supported
        """
        self.title = title
        self.options = options
        self.color_enabled = color_enabled
        self.selected_index = 0
    
    def show(self) -> Optional[str]:
        """Show interactive menu and return selected option
        
        Returns:
            Selected option or None if cancelled
        """
        if not self.options:
            return None
        
        # Try to use interactive mode if supported
        if self._supports_interactive():
            return self._interactive_select()
        else:
            return self._simple_select()
    
    def _supports_interactive(self) -> bool:
        """Check if terminal supports interactive input"""
        return sys.stdin.isatty() and hasattr(sys.stdin, 'read')
    
    def _interactive_select(self) -> Optional[str]:
        """Interactive selection with arrow keys"""
        import termios
        import tty
        
        if os.name == 'nt':
            # Windows doesn't support termios, fall back to simple
            return self._simple_select()
        
        # Save terminal settings
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        
        try:
            tty.setraw(sys.stdin.fileno())
            
            while True:
                # Clear screen and show menu
                self._render_menu()
                
                # Read key
                key = sys.stdin.read(1)
                
                if key == '\x1b':  # Escape sequence
                    key += sys.stdin.read(2)
                    if key == '\x1b[A':  # Up arrow
                        self.selected_index = (self.selected_index - 1) % len(self.options)
                    elif key == '\x1b[B':  # Down arrow
                        self.selected_index = (self.selected_index + 1) % len(self.options)
                elif key in ['\r', '\n']:  # Enter
                    return self.options[self.selected_index]
                elif key == '\x03':  # Ctrl+C
                    raise KeyboardInterrupt
                elif key == '\x1b':  # Escape
                    return None
        
        finally:
            # Restore terminal settings
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            print()  # Add newline
    
    def _simple_select(self) -> Optional[str]:
        """Simple numbered selection"""
        prompt = InputPrompt(color_enabled=self.color_enabled)
        
        print(self._colorize(f"\n{self.title}", "\033[1;96m"))
        print(self._colorize("=" * len(self.title), "\033[96m"))
        
        for i, option in enumerate(self.options, 1):
            yellow_color = '\033[93m'
            print(f"  {self._colorize(f'{i}.', yellow_color)} {option}")
        
        while True:
            try:
                choice = prompt.number_input("Select option", min_value=1, 
                                           max_value=len(self.options), integer_only=True)
                return self.options[int(choice) - 1]
            except (ValueError, IndexError, KeyboardInterrupt):
                return None
    
    def _render_menu(self):
        """Render the interactive menu"""
        # Clear screen
        print('\033[2J\033[H', end='')
        
        # Title
        print(self._colorize(f"{self.title}", "\033[1;96m"))
        print(self._colorize("=" * len(self.title), "\033[96m"))
        print()
        
        # Options
        for i, option in enumerate(self.options):
            if i == self.selected_index:
                # Highlighted option
                green_color = '\033[92m'
                white_color = '\033[1;97m'
                line = f"{self._colorize('► ', green_color)}{self._colorize(option, white_color)}"
            else:
                line = f"  {option}"
            print(line)
        
        # Instructions
        print()
        print(self._colorize("Use ↑↓ arrows to navigate, Enter to select, Esc to cancel", "\033[90m"))
    
    def _colorize(self, text: str, color_code: str) -> str:
        """Apply color if enabled"""
        if self.color_enabled:
            return f"{color_code}{text}\033[0m"
        return text


# Validation helper functions
def email_validator(email: str) -> ValidationResponse:
    """Validate email address format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return ValidationResponse(ValidationResult.VALID)
    return ValidationResponse(ValidationResult.INVALID, "Invalid email address format")


def url_validator(url: str) -> ValidationResponse:
    """Validate URL format"""
    pattern = r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$'
    if re.match(pattern, url):
        return ValidationResponse(ValidationResult.VALID)
    return ValidationResponse(ValidationResult.INVALID, "Invalid URL format")


def phone_validator(phone: str) -> ValidationResponse:
    """Validate phone number format"""
    # Remove common separators
    clean_phone = re.sub(r'[-.\s()+]', '', phone)
    if len(clean_phone) >= 10 and clean_phone.isdigit():
        return ValidationResponse(ValidationResult.VALID)
    return ValidationResponse(ValidationResult.INVALID, "Invalid phone number format")


def length_validator(min_length: int = 0, max_length: int = 1000) -> Callable[[str], ValidationResponse]:
    """Create a length validator"""
    def validator(text: str) -> ValidationResponse:
        if len(text) < min_length:
            return ValidationResponse(ValidationResult.INVALID, 
                                    f"Must be at least {min_length} characters")
        if len(text) > max_length:
            return ValidationResponse(ValidationResult.INVALID,
                                    f"Must be at most {max_length} characters")
        return ValidationResponse(ValidationResult.VALID)
    return validator


# Convenience functions
def ask_text(prompt: str, **kwargs) -> str:
    """Quick text input"""
    p = InputPrompt()
    return p.text_input(prompt, **kwargs)


def ask_number(prompt: str, **kwargs) -> Union[int, float]:
    """Quick number input"""
    p = InputPrompt()
    return p.number_input(prompt, **kwargs)


def ask_choice(prompt: str, choices: List[str], **kwargs) -> str:
    """Quick choice input"""
    p = InputPrompt()
    return p.choice_input(prompt, choices, **kwargs)


def ask_confirm(prompt: str, **kwargs) -> bool:
    """Quick confirmation"""
    p = InputPrompt()
    return p.confirm_input(prompt, **kwargs)


def ask_password(prompt: str = "Password", **kwargs) -> str:
    """Quick password input"""
    p = InputPrompt()
    return p.password_input(prompt, **kwargs)


def show_menu(title: str, options: List[str]) -> Optional[str]:
    """Quick menu selection"""
    menu = MenuSelector(title, options)
    return menu.show()