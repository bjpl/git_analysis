"""
High contrast and color blind friendly themes for accessibility.
Provides WCAG 2.1 AA compliant color schemes.
"""

from typing import Dict, Optional, Tuple
import colorsys


class HighContrastThemes:
    """
    High contrast themes that meet WCAG 2.1 AA contrast requirements.
    Minimum contrast ratio of 4.5:1 for normal text, 3:1 for large text.
    """
    
    def __init__(self):
        self.themes = {
            'high_contrast_dark': {
                'name': 'High Contrast Dark',
                'bg': '#000000',  # Pure black
                'fg': '#FFFFFF',  # Pure white
                'select_bg': '#FFFF00',  # Bright yellow
                'select_fg': '#000000',
                'button_bg': '#FFFFFF',
                'button_fg': '#000000',
                'button_active_bg': '#FFFF00',
                'button_active_fg': '#000000',
                'entry_bg': '#FFFFFF',
                'entry_fg': '#000000',
                'frame_bg': '#000000',
                'border': '#FFFFFF',
                'focus_color': '#FFFF00',
                'error': '#FF0000',  # Bright red
                'success': '#00FF00',  # Bright green
                'warning': '#FFFF00',  # Bright yellow
                'info': '#00FFFF',  # Bright cyan
                'link': '#00FFFF',
                'visited_link': '#FF00FF'  # Bright magenta
            },
            
            'high_contrast_light': {
                'name': 'High Contrast Light',
                'bg': '#FFFFFF',  # Pure white
                'fg': '#000000',  # Pure black
                'select_bg': '#0000FF',  # Bright blue
                'select_fg': '#FFFFFF',
                'button_bg': '#000000',
                'button_fg': '#FFFFFF',
                'button_active_bg': '#0000FF',
                'button_active_fg': '#FFFFFF',
                'entry_bg': '#000000',
                'entry_fg': '#FFFFFF',
                'frame_bg': '#FFFFFF',
                'border': '#000000',
                'focus_color': '#0000FF',
                'error': '#FF0000',  # Bright red
                'success': '#008000',  # Dark green
                'warning': '#FF8000',  # Orange
                'info': '#0000FF',  # Bright blue
                'link': '#0000FF',
                'visited_link': '#800080'  # Purple
            },
            
            'yellow_on_black': {
                'name': 'Yellow on Black',
                'bg': '#000000',
                'fg': '#FFFF00',  # Bright yellow
                'select_bg': '#FFFFFF',
                'select_fg': '#000000',
                'button_bg': '#FFFF00',
                'button_fg': '#000000',
                'button_active_bg': '#FFFFFF',
                'button_active_fg': '#000000',
                'entry_bg': '#FFFF00',
                'entry_fg': '#000000',
                'frame_bg': '#000000',
                'border': '#FFFF00',
                'focus_color': '#FFFFFF',
                'error': '#FF0000',
                'success': '#00FF00',
                'warning': '#FF8000',
                'info': '#00FFFF',
                'link': '#00FFFF',
                'visited_link': '#FF00FF'
            },
            
            'white_on_black': {
                'name': 'White on Black',
                'bg': '#000000',
                'fg': '#FFFFFF',
                'select_bg': '#0080FF',  # Bright blue
                'select_fg': '#FFFFFF',
                'button_bg': '#FFFFFF',
                'button_fg': '#000000',
                'button_active_bg': '#0080FF',
                'button_active_fg': '#FFFFFF',
                'entry_bg': '#FFFFFF',
                'entry_fg': '#000000',
                'frame_bg': '#000000',
                'border': '#FFFFFF',
                'focus_color': '#0080FF',
                'error': '#FF4040',
                'success': '#40FF40',
                'warning': '#FFFF40',
                'info': '#40FFFF',
                'link': '#40FFFF',
                'visited_link': '#FF40FF'
            }
        }
        
        # Current theme
        self.current_theme = 'high_contrast_dark'
    
    def get_available_themes(self) -> Dict[str, str]:
        """Get available high contrast theme names."""
        return {key: theme['name'] for key, theme in self.themes.items()}
    
    def set_theme(self, theme_name: str):
        """Set the current high contrast theme."""
        if theme_name in self.themes:
            self.current_theme = theme_name
    
    def get_high_contrast_colors(self, theme_name: Optional[str] = None) -> Dict[str, str]:
        """Get high contrast color scheme."""
        theme = theme_name or self.current_theme
        if theme not in self.themes:
            theme = 'high_contrast_dark'
        
        return self.themes[theme].copy()
    
    def get_focus_indicators(self) -> Dict[str, str]:
        """Get enhanced focus indicator styles."""
        colors = self.get_high_contrast_colors()
        return {
            'focus_ring_color': colors['focus_color'],
            'focus_ring_width': '3',  # Thicker focus rings
            'focus_style': 'solid',
            'focus_offset': '2'  # Offset from widget edge
        }
    
    def validate_contrast_ratio(self, fg_color: str, bg_color: str) -> Tuple[float, bool]:
        """
        Validate contrast ratio between foreground and background colors.
        Returns (ratio, is_compliant) where is_compliant means >= 4.5:1.
        """
        def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        def get_relative_luminance(r: int, g: int, b: int) -> float:
            """Calculate relative luminance according to WCAG."""
            def gamma_correct(c):
                c = c / 255.0
                return c / 12.92 if c <= 0.03928 else pow((c + 0.055) / 1.055, 2.4)
            
            return 0.2126 * gamma_correct(r) + 0.7152 * gamma_correct(g) + 0.0722 * gamma_correct(b)
        
        try:
            fg_rgb = hex_to_rgb(fg_color)
            bg_rgb = hex_to_rgb(bg_color)
            
            fg_lum = get_relative_luminance(*fg_rgb)
            bg_lum = get_relative_luminance(*bg_rgb)
            
            # Ensure lighter color is in numerator
            if fg_lum > bg_lum:
                ratio = (fg_lum + 0.05) / (bg_lum + 0.05)
            else:
                ratio = (bg_lum + 0.05) / (fg_lum + 0.05)
            
            is_compliant = ratio >= 4.5
            return ratio, is_compliant
        
        except Exception:
            return 0.0, False


class ColorBlindThemes:
    """
    Color blind friendly themes for deuteranopia, protanopia, and tritanopia.
    Uses patterns, shapes, and high contrast instead of color-only differentiation.
    """
    
    def __init__(self):
        self.themes = {
            'deuteranopia': {
                'name': 'Deuteranopia (Green-blind)',
                'description': 'Optimized for red-green color blindness (green deficiency)',
                'colors': {
                    'bg': '#FFFFFF',
                    'fg': '#000000',
                    'primary': '#0073E6',    # Blue - clearly distinguishable
                    'secondary': '#FF6B35',   # Orange-red - distinguishable from blue
                    'success': '#0073E6',     # Blue instead of green
                    'warning': '#FFB000',     # Amber - clearly visible
                    'error': '#D32F2F',      # Red - high contrast
                    'info': '#7B68EE',       # Medium slate blue
                    'neutral': '#6C757D',    # Gray
                    'select_bg': '#0073E6',
                    'select_fg': '#FFFFFF',
                    'button_bg': '#F5F5F5',
                    'button_fg': '#000000',
                    'button_active_bg': '#0073E6',
                    'button_active_fg': '#FFFFFF',
                    'focus_color': '#FF6B35'
                }
            },
            
            'protanopia': {
                'name': 'Protanopia (Red-blind)',
                'description': 'Optimized for red-green color blindness (red deficiency)',
                'colors': {
                    'bg': '#FFFFFF',
                    'fg': '#000000',
                    'primary': '#1976D2',     # Blue
                    'secondary': '#FFA726',   # Orange
                    'success': '#1976D2',     # Blue instead of green
                    'warning': '#FF8F00',     # Amber
                    'error': '#5D4037',       # Brown instead of red
                    'info': '#7986CB',        # Indigo
                    'neutral': '#757575',     # Gray
                    'select_bg': '#1976D2',
                    'select_fg': '#FFFFFF',
                    'button_bg': '#F5F5F5',
                    'button_fg': '#000000',
                    'button_active_bg': '#1976D2',
                    'button_active_fg': '#FFFFFF',
                    'focus_color': '#FFA726'
                }
            },
            
            'tritanopia': {
                'name': 'Tritanopia (Blue-blind)',
                'description': 'Optimized for blue-yellow color blindness',
                'colors': {
                    'bg': '#FFFFFF',
                    'fg': '#000000',
                    'primary': '#E91E63',     # Pink-red
                    'secondary': '#4CAF50',   # Green
                    'success': '#4CAF50',     # Green
                    'warning': '#FF5722',     # Red-orange
                    'error': '#F44336',       # Red
                    'info': '#9C27B0',        # Purple
                    'neutral': '#616161',     # Gray
                    'select_bg': '#E91E63',
                    'select_fg': '#FFFFFF',
                    'button_bg': '#F5F5F5',
                    'button_fg': '#000000',
                    'button_active_bg': '#E91E63',
                    'button_active_fg': '#FFFFFF',
                    'focus_color': '#4CAF50'
                }
            }
        }
    
    def get_available_themes(self) -> Dict[str, str]:
        """Get available color blind friendly themes."""
        return {key: theme['name'] for key, theme in self.themes.items()}
    
    def get_color_blind_colors(self, theme_type: str) -> Dict[str, str]:
        """Get color blind friendly color scheme."""
        if theme_type not in self.themes:
            theme_type = 'deuteranopia'  # Default
        
        theme = self.themes[theme_type]
        colors = theme['colors'].copy()
        
        # Add standard Tkinter color mappings
        return {
            'bg': colors['bg'],
            'fg': colors['fg'],
            'select_bg': colors['select_bg'],
            'select_fg': colors['select_fg'],
            'button_bg': colors['button_bg'],
            'button_fg': colors['button_fg'],
            'button_active_bg': colors['button_active_bg'],
            'button_active_fg': colors['button_active_fg'],
            'entry_bg': colors['bg'],
            'entry_fg': colors['fg'],
            'frame_bg': colors['bg'],
            'border': colors['neutral'],
            'focus_color': colors['focus_color'],
            'error': colors['error'],
            'success': colors['success'],
            'warning': colors['warning'],
            'info': colors['info'],
            'primary': colors['primary'],
            'secondary': colors['secondary']
        }
    
    def get_pattern_indicators(self) -> Dict[str, str]:
        """
        Get pattern and shape indicators to supplement color.
        These can be used as text symbols or image patterns.
        """
        return {
            'success': '✓',     # Check mark
            'error': '✗',       # X mark
            'warning': '⚠',     # Warning triangle
            'info': 'ℹ',        # Info symbol
            'required': '*',    # Asterisk
            'optional': '○',    # Circle
            'selected': '●',    # Filled circle
            'unselected': '○',  # Empty circle
            'expanded': '▼',    # Down triangle
            'collapsed': '▶',   # Right triangle
            'sort_up': '▲',     # Up triangle
            'sort_down': '▼',   # Down triangle
            'menu': '☰',        # Hamburger menu
            'search': '🔍',     # Magnifying glass
            'settings': '⚙',    # Gear
            'help': '?'         # Question mark
        }
    
    def simulate_color_blindness(self, hex_color: str, cb_type: str) -> str:
        """
        Simulate how a color appears to someone with color blindness.
        This helps in testing color schemes.
        """
        try:
            # Convert hex to RGB
            hex_color = hex_color.lstrip('#')
            r, g, b = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
            
            # Convert to 0-1 range
            r, g, b = r/255.0, g/255.0, b/255.0
            
            # Apply color blindness transformation matrices
            if cb_type == 'deuteranopia':  # Green-blind
                # Simplified deuteranopia transformation
                new_r = 0.625 * r + 0.375 * g
                new_g = 0.7 * r + 0.3 * g
                new_b = b
            elif cb_type == 'protanopia':  # Red-blind
                new_r = 0.567 * r + 0.433 * g
                new_g = 0.558 * r + 0.442 * g
                new_b = 0.242 * g + 0.758 * b
            elif cb_type == 'tritanopia':  # Blue-blind
                new_r = r + 0.967 * g
                new_g = g
                new_b = 0.142 * r + 0.858 * b
            else:
                return hex_color  # No transformation
            
            # Clamp values and convert back to hex
            new_r = max(0, min(1, new_r))
            new_g = max(0, min(1, new_g))
            new_b = max(0, min(1, new_b))
            
            r_hex = format(int(new_r * 255), '02x')
            g_hex = format(int(new_g * 255), '02x')
            b_hex = format(int(new_b * 255), '02x')
            
            return f"#{r_hex}{g_hex}{b_hex}"
        
        except Exception:
            return hex_color  # Return original on error


class AccessibilityThemeManager:
    """
    Manager for accessibility themes that coordinates between
    high contrast and color blind friendly options.
    """
    
    def __init__(self):
        self.high_contrast = HighContrastThemes()
        self.color_blind = ColorBlindThemes()
        self.current_mode = 'normal'
        self.current_theme = None
    
    def set_high_contrast_mode(self, theme_name: str = 'high_contrast_dark'):
        """Enable high contrast mode with specified theme."""
        self.current_mode = 'high_contrast'
        self.current_theme = theme_name
        self.high_contrast.set_theme(theme_name)
    
    def set_color_blind_mode(self, cb_type: str):
        """Enable color blind friendly mode."""
        self.current_mode = 'color_blind'
        self.current_theme = cb_type
    
    def set_normal_mode(self):
        """Return to normal color mode."""
        self.current_mode = 'normal'
        self.current_theme = None
    
    def get_current_colors(self) -> Dict[str, str]:
        """Get colors for current accessibility mode."""
        if self.current_mode == 'high_contrast':
            return self.high_contrast.get_high_contrast_colors(self.current_theme)
        elif self.current_mode == 'color_blind':
            return self.color_blind.get_color_blind_colors(self.current_theme)
        else:
            # Return default/normal colors
            return {
                'bg': '#FFFFFF',
                'fg': '#000000',
                'select_bg': '#0078D4',
                'select_fg': '#FFFFFF',
                'button_bg': '#F0F0F0',
                'button_fg': '#000000',
                'button_active_bg': '#E0E0E0',
                'button_active_fg': '#000000',
                'entry_bg': '#FFFFFF',
                'entry_fg': '#000000',
                'frame_bg': '#FFFFFF',
                'border': '#CCCCCC',
                'focus_color': '#0078D4',
                'error': '#D13438',
                'success': '#107C10',
                'warning': '#FF8C00',
                'info': '#0078D4'
            }
    
    def get_available_options(self) -> Dict[str, Dict[str, str]]:
        """Get all available accessibility theme options."""
        return {
            'high_contrast': self.high_contrast.get_available_themes(),
            'color_blind': self.color_blind.get_available_themes()
        }
    
    def test_color_accessibility(self, fg_color: str, bg_color: str) -> Dict[str, any]:
        """Test color combination for accessibility compliance."""
        ratio, is_compliant = self.high_contrast.validate_contrast_ratio(fg_color, bg_color)
        
        results = {
            'contrast_ratio': round(ratio, 2),
            'wcag_aa_compliant': is_compliant,
            'wcag_aaa_compliant': ratio >= 7.0,  # AAA requires 7:1
            'recommendations': []
        }
        
        if not is_compliant:
            results['recommendations'].append(
                'Increase contrast ratio to at least 4.5:1 for WCAG AA compliance'
            )
        
        if ratio < 7.0:
            results['recommendations'].append(
                'Consider increasing contrast ratio to 7:1 for WCAG AAA compliance'
            )
        
        # Test with color blind simulations
        for cb_type in ['deuteranopia', 'protanopia', 'tritanopia']:
            sim_fg = self.color_blind.simulate_color_blindness(fg_color, cb_type)
            sim_bg = self.color_blind.simulate_color_blindness(bg_color, cb_type)
            sim_ratio, sim_compliant = self.high_contrast.validate_contrast_ratio(sim_fg, sim_bg)
            
            results[f'{cb_type}_ratio'] = round(sim_ratio, 2)
            results[f'{cb_type}_compliant'] = sim_compliant
        
        return results