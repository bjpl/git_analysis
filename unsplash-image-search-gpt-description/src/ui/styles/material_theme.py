"""
Material Design-inspired theme system for Tkinter applications.
Provides modern color schemes, elevation, and design tokens.
"""

import tkinter as tk
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum


class MaterialVariant(Enum):
    """Material Design color variants."""
    PRIMARY = "primary"
    SECONDARY = "secondary"  
    TERTIARY = "tertiary"
    ERROR = "error"
    WARNING = "warning"
    SUCCESS = "success"
    INFO = "info"


@dataclass
class ColorPalette:
    """Material Design color palette."""
    primary: str = "#1976d2"
    primary_variant: str = "#1565c0"
    secondary: str = "#03dac6"
    secondary_variant: str = "#018786"
    background: str = "#ffffff"
    surface: str = "#ffffff"
    error: str = "#b00020"
    warning: str = "#ff9800"
    success: str = "#4caf50"
    info: str = "#2196f3"
    
    on_primary: str = "#ffffff"
    on_secondary: str = "#000000"
    on_background: str = "#000000"
    on_surface: str = "#000000"
    on_error: str = "#ffffff"
    
    # Extended colors
    surface_variant: str = "#f5f5f5"
    outline: str = "#757575"
    outline_variant: str = "#c4c7c5"
    inverse_surface: str = "#2d2d2d"
    inverse_on_surface: str = "#ffffff"


@dataclass
class DarkColorPalette(ColorPalette):
    """Material Design dark theme color palette."""
    primary: str = "#bb86fc"
    primary_variant: str = "#985eff"
    secondary: str = "#03dac6"
    secondary_variant: str = "#03dac6"
    background: str = "#121212"
    surface: str = "#1f1f1f"
    error: str = "#cf6679"
    warning: str = "#ffb74d"
    success: str = "#81c784"
    info: str = "#64b5f6"
    
    on_primary: str = "#000000"
    on_secondary: str = "#000000" 
    on_background: str = "#ffffff"
    on_surface: str = "#ffffff"
    on_error: str = "#000000"
    
    surface_variant: str = "#2d2d2d"
    outline: str = "#8a8a8a"
    outline_variant: str = "#444746"
    inverse_surface: str = "#ffffff"
    inverse_on_surface: str = "#000000"


@dataclass
class Typography:
    """Material Design typography scale."""
    # Headlines
    headline_large: tuple = ("Segoe UI", 32, "normal")
    headline_medium: tuple = ("Segoe UI", 28, "normal")
    headline_small: tuple = ("Segoe UI", 24, "normal")
    
    # Titles
    title_large: tuple = ("Segoe UI", 22, "normal")
    title_medium: tuple = ("Segoe UI", 16, "bold")
    title_small: tuple = ("Segoe UI", 14, "bold")
    
    # Body text
    body_large: tuple = ("Segoe UI", 16, "normal")
    body_medium: tuple = ("Segoe UI", 14, "normal")
    body_small: tuple = ("Segoe UI", 12, "normal")
    
    # Labels  
    label_large: tuple = ("Segoe UI", 14, "bold")
    label_medium: tuple = ("Segoe UI", 12, "bold")
    label_small: tuple = ("Segoe UI", 11, "bold")


@dataclass  
class Elevation:
    """Material Design elevation system."""
    level_0: Dict[str, Any] = field(default_factory=lambda: {
        "shadow_blur": 0,
        "shadow_offset": (0, 0),
        "shadow_color": "#000000",
        "shadow_opacity": 0.0
    })
    
    level_1: Dict[str, Any] = field(default_factory=lambda: {
        "shadow_blur": 3,
        "shadow_offset": (0, 1),
        "shadow_color": "#000000", 
        "shadow_opacity": 0.12
    })
    
    level_2: Dict[str, Any] = field(default_factory=lambda: {
        "shadow_blur": 6,
        "shadow_offset": (0, 2),
        "shadow_color": "#000000",
        "shadow_opacity": 0.16
    })
    
    level_3: Dict[str, Any] = field(default_factory=lambda: {
        "shadow_blur": 12,
        "shadow_offset": (0, 4),
        "shadow_color": "#000000",
        "shadow_opacity": 0.20
    })
    
    level_4: Dict[str, Any] = field(default_factory=lambda: {
        "shadow_blur": 24,
        "shadow_offset": (0, 8),
        "shadow_color": "#000000",
        "shadow_opacity": 0.24
    })


@dataclass
class Spacing:
    """Material Design spacing system."""
    xs: int = 4
    sm: int = 8
    md: int = 16
    lg: int = 24
    xl: int = 32
    xxl: int = 48
    xxxl: int = 64
    

@dataclass
class BorderRadius:
    """Material Design border radius system."""
    none: int = 0
    xs: int = 4
    sm: int = 8
    md: int = 12
    lg: int = 16
    xl: int = 20
    xxl: int = 28
    full: int = 9999


@dataclass
class Breakpoints:
    """Responsive breakpoints."""
    xs: int = 0
    sm: int = 600
    md: int = 960
    lg: int = 1280
    xl: int = 1920


class MaterialColors:
    """Extended Material Design color system."""
    
    # Primary colors
    BLUE = {
        50: "#e3f2fd", 100: "#bbdefb", 200: "#90caf9", 300: "#64b5f6",
        400: "#42a5f5", 500: "#2196f3", 600: "#1e88e5", 700: "#1976d2",
        800: "#1565c0", 900: "#0d47a1"
    }
    
    GREEN = {
        50: "#e8f5e8", 100: "#c8e6c9", 200: "#a5d6a7", 300: "#81c784",
        400: "#66bb6a", 500: "#4caf50", 600: "#43a047", 700: "#388e3c",
        800: "#2e7d32", 900: "#1b5e20"
    }
    
    RED = {
        50: "#ffebee", 100: "#ffcdd2", 200: "#ef9a9a", 300: "#e57373",
        400: "#ef5350", 500: "#f44336", 600: "#e53935", 700: "#d32f2f",
        800: "#c62828", 900: "#b71c1c"
    }
    
    ORANGE = {
        50: "#fff3e0", 100: "#ffe0b2", 200: "#ffcc02", 300: "#ffb74d",
        400: "#ffa726", 500: "#ff9800", 600: "#fb8c00", 700: "#f57c00",
        800: "#ef6c00", 900: "#e65100"
    }
    
    PURPLE = {
        50: "#f3e5f5", 100: "#e1bee7", 200: "#ce93d8", 300: "#ba68c8",
        400: "#ab47bc", 500: "#9c27b0", 600: "#8e24aa", 700: "#7b1fa2",
        800: "#6a1b9a", 900: "#4a148c"
    }
    
    GREY = {
        50: "#fafafa", 100: "#f5f5f5", 200: "#eeeeee", 300: "#e0e0e0",
        400: "#bdbdbd", 500: "#9e9e9e", 600: "#757575", 700: "#616161",
        800: "#424242", 900: "#212121"
    }


class MaterialTheme:
    """Complete Material Design theme system."""
    
    def __init__(self, theme_name: str = "light", 
                 primary_color: str = "#1976d2",
                 secondary_color: str = "#03dac6"):
        self.theme_name = theme_name
        self.primary_color = primary_color
        self.secondary_color = secondary_color
        
        # Initialize theme components
        self.colors = self._create_color_palette()
        self.typography = Typography()
        self.elevation = Elevation()
        self.spacing = Spacing()
        self.radius = BorderRadius()
        self.breakpoints = Breakpoints()
        
    def _create_color_palette(self) -> Union[ColorPalette, DarkColorPalette]:
        """Create color palette based on theme."""
        if self.theme_name == "dark":
            palette = DarkColorPalette()
        else:
            palette = ColorPalette()
            
        # Override with custom colors if provided
        if self.primary_color != "#1976d2":
            palette.primary = self.primary_color
        if self.secondary_color != "#03dac6":
            palette.secondary = self.secondary_color
            
        return palette
    
    def get_color(self, color_name: str, variant: str = "500") -> str:
        """Get color from extended palette."""
        color_map = {
            "blue": MaterialColors.BLUE,
            "green": MaterialColors.GREEN,
            "red": MaterialColors.RED,
            "orange": MaterialColors.ORANGE,
            "purple": MaterialColors.PURPLE,
            "grey": MaterialColors.GREY,
        }
        
        if color_name in color_map:
            return color_map[color_name].get(int(variant), color_map[color_name][500])
        
        # Fallback to basic palette
        return getattr(self.colors, color_name, "#000000")
    
    def get_text_color(self, background_color: str) -> str:
        """Get appropriate text color for background."""
        # Simple luminance check - in production would use proper contrast calculation
        bg = background_color.lstrip("#")
        r, g, b = int(bg[0:2], 16), int(bg[2:4], 16), int(bg[4:6], 16)
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        
        return self.colors.on_surface if luminance > 0.5 else self.colors.inverse_on_surface
    
    def get_font(self, style: str) -> tuple:
        """Get font configuration for typography style."""
        return getattr(self.typography, style, self.typography.body_medium)
    
    def get_elevation_style(self, level: int) -> Dict[str, Any]:
        """Get elevation style for given level."""
        level_attr = f"level_{min(4, max(0, level))}"
        return getattr(self.elevation, level_attr, self.elevation.level_0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Export theme as dictionary for legacy compatibility."""
        return {
            # Basic colors
            "bg": self.colors.background,
            "fg": self.colors.on_background,
            "primary": self.colors.primary,
            "secondary": self.colors.secondary,
            "error": self.colors.error,
            "warning": self.colors.warning,
            "success": self.colors.success,
            "info": self.colors.info,
            
            # Surface colors
            "surface": self.colors.surface,
            "surface_variant": self.colors.surface_variant,
            
            # Interactive colors
            "select_bg": self.colors.primary,
            "select_fg": self.colors.on_primary,
            
            # UI element colors
            "frame_bg": self.colors.surface,
            "entry_bg": self.colors.surface,
            "entry_fg": self.colors.on_surface,
            "button_bg": self.colors.surface_variant,
            "button_fg": self.colors.on_surface,
            "button_active_bg": self.colors.primary,
            
            # Border and outline
            "border": self.colors.outline,
            "outline": self.colors.outline_variant,
            
            # Status colors
            "disabled_fg": self.colors.outline,
            
            # Text colors
            "text_bg": self.colors.background,
            "text_fg": self.colors.on_background,
            
            # Tooltip
            "tooltip_bg": self.colors.inverse_surface,
            "tooltip_fg": self.colors.inverse_on_surface,
            
            # Progress
            "progress_bg": self.colors.surface_variant,
            "progress_fg": self.colors.primary,
            
            # Scrollbar
            "scrollbar_bg": self.colors.surface_variant,
            "scrollbar_thumb": self.colors.outline,
        }
    
    def create_variant(self, variant: MaterialVariant, shade: int = 500) -> "MaterialTheme":
        """Create theme variant with different primary color."""
        color_map = {
            MaterialVariant.PRIMARY: MaterialColors.BLUE,
            MaterialVariant.SECONDARY: MaterialColors.GREEN,
            MaterialVariant.TERTIARY: MaterialColors.PURPLE,
            MaterialVariant.ERROR: MaterialColors.RED,
            MaterialVariant.WARNING: MaterialColors.ORANGE,
            MaterialVariant.SUCCESS: MaterialColors.GREEN,
            MaterialVariant.INFO: MaterialColors.BLUE,
        }
        
        primary = color_map[variant][shade]
        return MaterialTheme(self.theme_name, primary, self.secondary_color)