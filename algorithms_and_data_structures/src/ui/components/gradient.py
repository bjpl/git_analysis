#!/usr/bin/env python3
"""
Gradient Text Effects - Beautiful gradient text for terminal output

This module provides:
- RGB to ANSI color conversion
- Gradient text generation
- Rainbow effects
- Color interpolation
- Windows-compatible fallbacks
"""

import colorsys
import re
from typing import List, Tuple, Optional, Union
from enum import Enum
import sys
import os


class GradientDirection(Enum):
    """Gradient direction options"""
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    DIAGONAL = "diagonal"
    RADIAL = "radial"


class GradientPreset(Enum):
    """Pre-defined gradient presets"""
    FIRE = [(255, 0, 0), (255, 165, 0), (255, 255, 0)]
    OCEAN = [(0, 0, 255), (0, 128, 255), (0, 255, 255)]
    SUNSET = [(255, 94, 77), (255, 154, 0), (255, 206, 84)]
    FOREST = [(34, 139, 34), (50, 205, 50), (124, 252, 0)]
    PURPLE = [(75, 0, 130), (138, 43, 226), (218, 112, 214)]
    RAINBOW = [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (75, 0, 130), (148, 0, 211)]
    CYBERPUNK = [(0, 255, 255), (255, 0, 255), (255, 255, 0)]
    GALAXY = [(25, 25, 112), (72, 61, 139), (123, 104, 238)]


class GradientText:
    """Create beautiful gradient text effects for terminal output"""
    
    def __init__(self, color_enabled: Optional[bool] = None):
        """Initialize gradient text generator
        
        Args:
            color_enabled: Override color support detection
        """
        self._color_enabled = color_enabled
        self.supports_truecolor = self._detect_truecolor_support()
    
    @property
    def color_enabled(self) -> bool:
        """Check if color output is enabled"""
        if self._color_enabled is not None:
            return self._color_enabled
        
        # Auto-detect color support
        if not sys.stdout.isatty():
            return False
        
        # Check environment variables
        if os.environ.get('NO_COLOR'):
            return False
        
        if os.environ.get('FORCE_COLOR'):
            return True
        
        # Check terminal capabilities
        term = os.environ.get('TERM', '')
        colorterm = os.environ.get('COLORTERM', '')
        
        if 'truecolor' in colorterm or '24bit' in colorterm:
            return True
        
        if 'color' in term or term in ['xterm', 'xterm-256color', 'screen']:
            return True
        
        # Windows color support
        if sys.platform == 'win32':
            try:
                import colorama
                colorama.init()
                return True
            except ImportError:
                return False
        
        return True
    
    def _detect_truecolor_support(self) -> bool:
        """Detect if terminal supports true color (24-bit)"""
        if not self.color_enabled:
            return False
        
        # Check environment variables
        colorterm = os.environ.get('COLORTERM', '')
        if 'truecolor' in colorterm or '24bit' in colorterm:
            return True
        
        term = os.environ.get('TERM', '')
        if 'xterm' in term or 'screen' in term:
            return True
        
        # Windows Terminal and modern terminals
        if sys.platform == 'win32':
            wt_session = os.environ.get('WT_SESSION')
            if wt_session:
                return True
        
        return False
    
    def rgb_to_ansi(self, r: int, g: int, b: int, background: bool = False) -> str:
        """Convert RGB values to ANSI color code
        
        Args:
            r, g, b: RGB color values (0-255)
            background: Whether this is a background color
            
        Returns:
            ANSI color code string
        """
        if not self.color_enabled:
            return ""
        
        if self.supports_truecolor:
            # True color (24-bit)
            code = 48 if background else 38
            return f"\033[{code};2;{r};{g};{b}m"
        else:
            # Fallback to 256-color or 16-color
            return self._rgb_to_256_color(r, g, b, background)
    
    def _rgb_to_256_color(self, r: int, g: int, b: int, background: bool = False) -> str:
        """Convert RGB to 256-color ANSI code"""
        # Convert to 6x6x6 color cube
        r_idx = int(r / 255 * 5)
        g_idx = int(g / 255 * 5)
        b_idx = int(b / 255 * 5)
        
        color_idx = 16 + (36 * r_idx) + (6 * g_idx) + b_idx
        
        code = 48 if background else 38
        return f"\033[{code};5;{color_idx}m"
    
    def interpolate_color(self, color1: Tuple[int, int, int], 
                         color2: Tuple[int, int, int], 
                         factor: float) -> Tuple[int, int, int]:
        """Interpolate between two RGB colors
        
        Args:
            color1: First RGB color tuple
            color2: Second RGB color tuple
            factor: Interpolation factor (0.0 to 1.0)
            
        Returns:
            Interpolated RGB color tuple
        """
        factor = max(0.0, min(1.0, factor))
        
        r = int(color1[0] + (color2[0] - color1[0]) * factor)
        g = int(color1[1] + (color2[1] - color1[1]) * factor)
        b = int(color1[2] + (color2[2] - color1[2]) * factor)
        
        return (r, g, b)
    
    def generate_gradient_colors(self, colors: List[Tuple[int, int, int]], 
                                steps: int) -> List[Tuple[int, int, int]]:
        """Generate a list of interpolated colors for a gradient
        
        Args:
            colors: List of RGB color tuples to interpolate between
            steps: Number of color steps to generate
            
        Returns:
            List of interpolated RGB color tuples
        """
        if len(colors) < 2:
            return colors * steps
        
        if steps <= 1:
            return [colors[0]]
        
        gradient_colors = []
        segments = len(colors) - 1
        steps_per_segment = (steps - 1) / segments
        
        for i in range(steps):
            # Determine which segment we're in
            segment_pos = i / steps_per_segment
            segment_idx = int(segment_pos)
            
            # Handle edge case
            if segment_idx >= segments:
                gradient_colors.append(colors[-1])
                continue
            
            # Local position within the segment (0.0 to 1.0)
            local_pos = segment_pos - segment_idx
            
            # Interpolate between the two colors in this segment
            color = self.interpolate_color(colors[segment_idx], colors[segment_idx + 1], local_pos)
            gradient_colors.append(color)
        
        return gradient_colors
    
    def gradient_text(self, text: str, 
                     colors: Union[List[Tuple[int, int, int]], GradientPreset],
                     direction: GradientDirection = GradientDirection.HORIZONTAL) -> str:
        """Apply gradient coloring to text
        
        Args:
            text: Text to apply gradient to
            colors: List of RGB colors or preset gradient
            direction: Gradient direction
            
        Returns:
            Gradient-colored text string
        """
        if not self.color_enabled:
            return text
        
        # Handle preset gradients
        if isinstance(colors, GradientPreset):
            colors = colors.value
        
        if not colors:
            return text
        
        lines = text.split('\n')
        result_lines = []
        
        if direction == GradientDirection.VERTICAL:
            # Vertical gradient - different color for each line
            if len(lines) > 1:
                gradient_colors = self.generate_gradient_colors(colors, len(lines))
                for line, color in zip(lines, gradient_colors):
                    colored_line = self.rgb_to_ansi(*color) + line + "\033[0m"
                    result_lines.append(colored_line)
            else:
                # Single line - apply horizontal gradient
                result_lines.append(self._apply_horizontal_gradient(text, colors))
        
        elif direction == GradientDirection.DIAGONAL:
            # Diagonal gradient - combines horizontal and vertical
            for i, line in enumerate(lines):
                # Shift the gradient for each line
                shift_factor = i / max(len(lines) - 1, 1)
                shifted_colors = self._shift_gradient_colors(colors, shift_factor)
                colored_line = self._apply_horizontal_gradient(line, shifted_colors)
                result_lines.append(colored_line)
        
        else:  # HORIZONTAL or RADIAL (treat radial as horizontal for now)
            for line in lines:
                result_lines.append(self._apply_horizontal_gradient(line, colors))
        
        return '\n'.join(result_lines)
    
    def _apply_horizontal_gradient(self, text: str, 
                                  colors: List[Tuple[int, int, int]]) -> str:
        """Apply horizontal gradient to a single line of text"""
        if not text.strip():
            return text
        
        # Remove existing ANSI codes for accurate length calculation
        clean_text = re.sub(r'\033\[[0-9;]*m', '', text)
        
        if len(clean_text) <= 1:
            if colors:
                return self.rgb_to_ansi(*colors[0]) + text + "\033[0m"
            return text
        
        gradient_colors = self.generate_gradient_colors(colors, len(clean_text))
        
        result = ""
        char_index = 0
        
        for char in text:
            # Skip ANSI escape sequences
            if char == '\033':
                # Find the end of the ANSI sequence
                ansi_seq = char
                i = text.find(char) + 1
                while i < len(text) and text[i] != 'm':
                    ansi_seq += text[i]
                    i += 1
                if i < len(text):
                    ansi_seq += text[i]  # Add the 'm'
                result += ansi_seq
                continue
            
            # Apply gradient color to visible characters
            if char_index < len(gradient_colors):
                color = gradient_colors[char_index]
                result += self.rgb_to_ansi(*color) + char
                char_index += 1
            else:
                result += char
        
        result += "\033[0m"  # Reset color
        return result
    
    def _shift_gradient_colors(self, colors: List[Tuple[int, int, int]], 
                              shift_factor: float) -> List[Tuple[int, int, int]]:
        """Shift gradient colors for diagonal effect"""
        if not colors or len(colors) < 2:
            return colors
        
        # Create a longer gradient and take a slice
        extended_colors = colors + colors
        gradient = self.generate_gradient_colors(extended_colors, len(colors) * 2)
        
        start_idx = int(len(gradient) * shift_factor * 0.5)
        end_idx = start_idx + len(colors)
        
        return gradient[start_idx:end_idx] or colors
    
    def rainbow_text(self, text: str, 
                    saturation: float = 1.0, 
                    value: float = 1.0) -> str:
        """Apply rainbow gradient to text
        
        Args:
            text: Text to apply rainbow to
            saturation: Color saturation (0.0 to 1.0)
            value: Color brightness (0.0 to 1.0)
            
        Returns:
            Rainbow-colored text
        """
        if not self.color_enabled:
            return text
        
        clean_text = re.sub(r'\033\[[0-9;]*m', '', text)
        
        if not clean_text.strip():
            return text
        
        result = ""
        char_index = 0
        
        for char in text:
            if char == '\033':
                # Skip ANSI sequences
                ansi_start = text.find(char)
                ansi_end = text.find('m', ansi_start)
                if ansi_end != -1:
                    ansi_seq = text[ansi_start:ansi_end + 1]
                    result += ansi_seq
                continue
            
            if char.strip():  # Only color visible characters
                # Calculate hue based on position
                hue = (char_index / max(len(clean_text) - 1, 1)) % 1.0
                
                # Convert HSV to RGB
                r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
                r, g, b = int(r * 255), int(g * 255), int(b * 255)
                
                result += self.rgb_to_ansi(r, g, b) + char
                char_index += 1
            else:
                result += char
        
        result += "\033[0m"
        return result
    
    def pulse_text(self, text: str, color: Tuple[int, int, int], 
                  intensity: float = 0.5) -> str:
        """Create a pulsing color effect (static version)
        
        Args:
            text: Text to apply pulse effect to
            color: Base RGB color
            intensity: Pulse intensity (0.0 to 1.0)
            
        Returns:
            Text with pulsing color effect
        """
        if not self.color_enabled:
            return text
        
        # Create darker and lighter versions of the color
        darker = tuple(int(c * (1 - intensity)) for c in color)
        lighter = tuple(int(min(255, c * (1 + intensity))) for c in color)
        
        # For static version, alternate between colors
        colors = [darker, color, lighter, color]
        return self.gradient_text(text, colors)
    
    def glow_text(self, text: str, color: Tuple[int, int, int]) -> str:
        """Create a glowing text effect
        
        Args:
            text: Text to apply glow to
            color: Glow color
            
        Returns:
            Text with glow effect
        """
        if not self.color_enabled:
            return text
        
        # Create glow by using background color
        bg_color = tuple(int(c * 0.3) for c in color)  # Darker background
        
        # Apply foreground and background colors
        fg_code = self.rgb_to_ansi(*color, False)
        bg_code = self.rgb_to_ansi(*bg_color, True)
        
        return f"{bg_code}{fg_code}{text}\033[0m"
    
    def fire_text(self, text: str) -> str:
        """Apply fire gradient effect"""
        return self.gradient_text(text, GradientPreset.FIRE)
    
    def ocean_text(self, text: str) -> str:
        """Apply ocean gradient effect"""
        return self.gradient_text(text, GradientPreset.OCEAN)
    
    def cyberpunk_text(self, text: str) -> str:
        """Apply cyberpunk gradient effect"""
        return self.gradient_text(text, GradientPreset.CYBERPUNK)
    
    def galaxy_text(self, text: str) -> str:
        """Apply galaxy gradient effect"""
        return self.gradient_text(text, GradientPreset.GALAXY)


# Convenience functions for easy use
def gradient(text: str, colors: Union[List[Tuple[int, int, int]], GradientPreset], 
            direction: GradientDirection = GradientDirection.HORIZONTAL) -> str:
    """Convenience function to apply gradient to text"""
    gt = GradientText()
    return gt.gradient_text(text, colors, direction)


def rainbow(text: str, saturation: float = 1.0, value: float = 1.0) -> str:
    """Convenience function to apply rainbow to text"""
    gt = GradientText()
    return gt.rainbow_text(text, saturation, value)


def fire(text: str) -> str:
    """Convenience function for fire gradient"""
    gt = GradientText()
    return gt.fire_text(text)


def ocean(text: str) -> str:
    """Convenience function for ocean gradient"""
    gt = GradientText()
    return gt.ocean_text(text)


def cyberpunk(text: str) -> str:
    """Convenience function for cyberpunk gradient"""
    gt = GradientText()
    return gt.cyberpunk_text(text)


def galaxy(text: str) -> str:
    """Convenience function for galaxy gradient"""
    gt = GradientText()
    return gt.galaxy_text(text)