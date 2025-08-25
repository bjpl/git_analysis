#!/usr/bin/env python3
"""
Application Icon Generator and Manager

This module provides utilities for generating application icons in various formats
and sizes required for Windows executables and installers.

Features:
- Generate ICO files from PNG sources
- Create multi-resolution icons
- Generate placeholder icons
- Icon validation and optimization
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple, Optional
from io import BytesIO

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: PIL/Pillow not available. Icon generation will be limited.")


class IconGenerator:
    """Generates and manages application icons."""
    
    # Standard Windows icon sizes
    ICON_SIZES = [16, 20, 24, 30, 32, 36, 40, 48, 60, 64, 72, 96, 128, 256]
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.installer_dir = project_root / "installer"
        self.assets_dir = project_root / "assets"
        
        # Ensure directories exist
        self.installer_dir.mkdir(exist_ok=True)
        self.assets_dir.mkdir(exist_ok=True)
    
    def create_text_icon(self, text: str, size: int = 256, 
                        bg_color: str = '#2E86AB', text_color: str = 'white') -> Image.Image:
        """Create a simple text-based icon."""
        if not PIL_AVAILABLE:
            raise ImportError("PIL/Pillow is required for icon generation")
        
        # Create image with rounded rectangle background
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw rounded rectangle background
        corner_radius = size // 8
        draw.rounded_rectangle(
            [corner_radius, corner_radius, size - corner_radius, size - corner_radius],
            radius=corner_radius,
            fill=bg_color
        )
        
        # Calculate font size based on icon size
        font_size = size // 4
        
        try:
            # Try to use a nice font
            font = ImageFont.truetype("arial.ttf", font_size)
        except (OSError, IOError):
            try:
                # Fallback to default font
                font = ImageFont.load_default()
            except:
                font = None
        
        # Draw text
        if font:
            # Get text bounding box
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        else:
            # Estimate text size without font
            text_width = len(text) * (font_size // 2)
            text_height = font_size
        
        # Center text
        text_x = (size - text_width) // 2
        text_y = (size - text_height) // 2
        
        draw.text((text_x, text_y), text, fill=text_color, font=font)
        
        return img
    
    def create_gradient_icon(self, size: int = 256, 
                           colors: List[str] = None) -> Image.Image:
        """Create an icon with gradient background."""
        if not PIL_AVAILABLE:
            raise ImportError("PIL/Pillow is required for icon generation")
        
        if colors is None:
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']  # Nice gradient colors
        
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        
        # Create gradient
        for y in range(size):
            # Calculate color based on position
            progress = y / size
            if progress < 0.5:
                # Blend first two colors
                t = progress * 2
                color = self._blend_colors(colors[0], colors[1], t)
            else:
                # Blend second and third colors
                t = (progress - 0.5) * 2
                color = self._blend_colors(colors[1], colors[2] if len(colors) > 2 else colors[1], t)
            
            # Draw line
            draw = ImageDraw.Draw(img)
            draw.line([(0, y), (size, y)], fill=color)
        
        # Add some visual elements
        draw = ImageDraw.Draw(img)
        
        # Draw a stylized "U" for Unsplash
        center_x, center_y = size // 2, size // 2
        u_width = size // 3
        u_height = size // 2
        stroke_width = max(2, size // 32)
        
        # Draw U shape
        u_left = center_x - u_width // 2
        u_right = center_x + u_width // 2
        u_top = center_y - u_height // 2
        u_bottom = center_y + u_height // 2
        
        # Left vertical line
        draw.line([(u_left, u_top), (u_left, u_bottom - u_width // 4)], 
                 fill='white', width=stroke_width)
        
        # Right vertical line
        draw.line([(u_right, u_top), (u_right, u_bottom - u_width // 4)], 
                 fill='white', width=stroke_width)
        
        # Bottom arc
        arc_box = [u_left, u_bottom - u_width // 2, u_right, u_bottom]
        draw.arc(arc_box, 0, 180, fill='white', width=stroke_width)
        
        return img
    
    def _blend_colors(self, color1: str, color2: str, t: float) -> str:
        """Blend two hex colors."""
        # Convert hex to RGB
        c1 = tuple(int(color1[i:i+2], 16) for i in (1, 3, 5))
        c2 = tuple(int(color2[i:i+2], 16) for i in (1, 3, 5))
        
        # Blend
        blended = tuple(int(c1[i] * (1 - t) + c2[i] * t) for i in range(3))
        
        # Convert back to hex
        return f"#{blended[0]:02x}{blended[1]:02x}{blended[2]:02x}"
    
    def create_ico_from_image(self, source_image: Image.Image, 
                             output_path: Path, sizes: List[int] = None) -> Path:
        """Create ICO file from PIL Image with multiple resolutions."""
        if not PIL_AVAILABLE:
            raise ImportError("PIL/Pillow is required for ICO generation")
        
        if sizes is None:
            sizes = [16, 32, 48, 64, 128, 256]
        
        # Create different sized versions
        icon_images = []
        for size in sizes:
            resized = source_image.resize((size, size), Image.Resampling.LANCZOS)
            icon_images.append(resized)
        
        # Save as ICO
        output_path.parent.mkdir(parents=True, exist_ok=True)
        source_image.save(output_path, format='ICO', sizes=[(img.width, img.height) for img in icon_images])
        
        print(f"ICO file created: {output_path} (sizes: {sizes})")
        return output_path
    
    def create_png_from_image(self, source_image: Image.Image, 
                             output_path: Path, size: int = 256) -> Path:
        """Create PNG file from PIL Image."""
        if not PIL_AVAILABLE:
            raise ImportError("PIL/Pillow is required for PNG generation")
        
        # Resize if needed
        if source_image.size != (size, size):
            source_image = source_image.resize((size, size), Image.Resampling.LANCZOS)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        source_image.save(output_path, format='PNG', optimize=True)
        
        print(f"PNG file created: {output_path} ({size}x{size})")
        return output_path
    
    def generate_default_icons(self) -> dict:
        """Generate default application icons."""
        icons = {}
        
        if not PIL_AVAILABLE:
            print("Warning: Cannot generate icons without PIL/Pillow")
            return self._create_placeholder_ico()
        
        try:
            # Create different icon variants
            
            # 1. Text-based icon with app initials
            text_icon = self.create_text_icon("UG", 256, '#2E86AB', 'white')
            icons['text_ico'] = self.create_ico_from_image(
                text_icon, self.installer_dir / "app_icon_text.ico"
            )
            icons['text_png'] = self.create_png_from_image(
                text_icon, self.assets_dir / "app_icon_text.png"
            )
            
            # 2. Gradient icon
            gradient_icon = self.create_gradient_icon(256)
            icons['gradient_ico'] = self.create_ico_from_image(
                gradient_icon, self.installer_dir / "app_icon_gradient.ico"
            )
            icons['gradient_png'] = self.create_png_from_image(
                gradient_icon, self.assets_dir / "app_icon_gradient.png"
            )
            
            # Create default icon (copy of gradient)
            default_ico = self.installer_dir / "app_icon.ico"
            gradient_icon.save(default_ico, format='ICO', 
                             sizes=[(s, s) for s in [16, 32, 48, 64, 128, 256]])
            icons['default'] = default_ico
            
            print(f"Generated {len(icons)} icon files")
            
        except Exception as e:
            print(f"Error generating icons: {e}")
            return self._create_placeholder_ico()
        
        return icons
    
    def _create_placeholder_ico(self) -> dict:
        """Create a simple placeholder ICO file."""
        # Create a minimal ICO file manually (16x16 pixel, 1-bit)
        ico_header = b'\x00\x00\x01\x00\x01\x00\x10\x10\x00\x00\x01\x00\x01\x00\x30\x00\x00\x00\x16\x00\x00\x00'
        # Simple 16x16 bitmap data (black square with white border)
        bitmap_data = b'\x28\x00\x00\x00\x10\x00\x00\x00\x20\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        
        placeholder_path = self.installer_dir / "app_icon.ico"
        with open(placeholder_path, 'wb') as f:
            f.write(ico_header + bitmap_data)
        
        print(f"Created placeholder ICO: {placeholder_path}")
        return {'placeholder': placeholder_path}
    
    def convert_png_to_ico(self, png_path: Path, output_path: Path = None, 
                          sizes: List[int] = None) -> Path:
        """Convert PNG file to ICO with multiple resolutions."""
        if not PIL_AVAILABLE:
            raise ImportError("PIL/Pillow is required for PNG to ICO conversion")
        
        if not png_path.exists():
            raise FileNotFoundError(f"PNG file not found: {png_path}")
        
        if output_path is None:
            output_path = png_path.with_suffix('.ico')
        
        if sizes is None:
            sizes = self.ICON_SIZES
        
        # Load PNG
        with Image.open(png_path) as img:
            # Convert to RGBA if needed
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            return self.create_ico_from_image(img, output_path, sizes)
    
    def validate_icon(self, icon_path: Path) -> bool:
        """Validate icon file format and size."""
        if not icon_path.exists():
            print(f"Icon file not found: {icon_path}")
            return False
        
        if not PIL_AVAILABLE:
            # Basic file extension check
            return icon_path.suffix.lower() == '.ico'
        
        try:
            with Image.open(icon_path) as img:
                if img.format != 'ICO':
                    print(f"Invalid icon format: {img.format} (expected ICO)")
                    return False
                
                # Check if it has multiple sizes
                if hasattr(img, 'n_frames') and img.n_frames > 1:
                    print(f"Icon has {img.n_frames} sizes - Good!")
                else:
                    print(f"Icon has single size: {img.size}")
                
                return True
                
        except Exception as e:
            print(f"Error validating icon: {e}")
            return False
    
    def create_installer_icons(self) -> dict:
        """Create all icons needed for the installer."""
        icons = {}
        
        try:
            # Generate default icons
            generated = self.generate_default_icons()
            icons.update(generated)
            
            # Create installer-specific sizes if needed
            if PIL_AVAILABLE and 'default' in icons:
                with Image.open(icons['default']) as img:
                    # Small icon for installer
                    small_icon = img.resize((32, 32), Image.Resampling.LANCZOS)
                    small_path = self.installer_dir / "installer_small.ico"
                    self.create_ico_from_image(small_icon, small_path, [16, 32])
                    icons['installer_small'] = small_path
                    
                    # Large icon for installer
                    large_icon = img.resize((64, 64), Image.Resampling.LANCZOS)
                    large_path = self.installer_dir / "installer_large.ico"
                    self.create_ico_from_image(large_icon, large_path, [48, 64])
                    icons['installer_large'] = large_path
            
        except Exception as e:
            print(f"Error creating installer icons: {e}")
        
        return icons


def main():
    """Main entry point for icon generation."""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        project_root = Path(__file__).parent.parent
        generator = IconGenerator(project_root)
        
        if command == "generate":
            print("Generating default application icons...")
            icons = generator.generate_default_icons()
            
            print("\nGenerated icons:")
            for icon_type, path in icons.items():
                print(f"  {icon_type}: {path}")
            
        elif command == "convert" and len(sys.argv) > 2:
            png_path = Path(sys.argv[2])
            print(f"Converting {png_path} to ICO...")
            ico_path = generator.convert_png_to_ico(png_path)
            print(f"Created: {ico_path}")
            
        elif command == "validate" and len(sys.argv) > 2:
            icon_path = Path(sys.argv[2])
            print(f"Validating {icon_path}...")
            if generator.validate_icon(icon_path):
                print("Icon is valid!")
            else:
                print("Icon validation failed!")
                
        elif command == "installer":
            print("Creating installer icons...")
            icons = generator.create_installer_icons()
            
            print("\nInstaller icons:")
            for icon_type, path in icons.items():
                print(f"  {icon_type}: {path}")
        
        else:
            print("Unknown command or missing arguments")
            return 1
    
    else:
        print("Usage:")
        print("  python icon_generator.py generate        - Generate default icons")
        print("  python icon_generator.py convert <png>   - Convert PNG to ICO")
        print("  python icon_generator.py validate <ico>  - Validate ICO file")
        print("  python icon_generator.py installer       - Create installer icons")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
