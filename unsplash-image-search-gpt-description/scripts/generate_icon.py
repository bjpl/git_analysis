#!/usr/bin/env python3
"""
Icon Generator for UnsplashGPT-Enhanced

Generates Windows .ico file from available PNG assets or creates a simple programmatic icon.
Supports multiple sizes for optimal Windows integration.
"""

import os
import sys
from pathlib import Path
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: PIL/Pillow not available. Install with: pip install Pillow")

def create_programmatic_icon():
    """Create a simple programmatic icon when no assets are available."""
    if not PIL_AVAILABLE:
        print("Error: PIL/Pillow required for icon generation")
        return None
    
    # Create a 256x256 base image
    size = 256
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Background circle with gradient effect
    center = size // 2
    radius = size // 2 - 10
    
    # Draw background circle
    draw.ellipse(
        [center - radius, center - radius, center + radius, center + radius],
        fill=(41, 128, 185, 255),  # Blue background
        outline=(52, 152, 219, 255),
        width=3
    )
    
    # Draw inner elements
    # Camera/search icon representation
    inner_radius = radius // 2
    
    # Search magnifier
    draw.ellipse(
        [center - inner_radius//2, center - inner_radius//2 - 20, 
         center + inner_radius//2, center + inner_radius//2 - 20],
        outline=(255, 255, 255, 255),
        width=8
    )
    
    # Magnifier handle
    draw.line(
        [center + inner_radius//3, center + inner_radius//3 - 20,
         center + inner_radius//2 + 15, center + inner_radius//2 + 15 - 20],
        fill=(255, 255, 255, 255),
        width=8
    )
    
    # Add "GPT" text
    try:
        # Try to use a built-in font
        font_size = 24
        font = ImageFont.load_default()
        
        # Calculate text position
        text = "GPT"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        text_x = center - text_width // 2
        text_y = center + inner_radius//2 + 10
        
        draw.text(
            (text_x, text_y),
            text,
            fill=(255, 255, 255, 255),
            font=font
        )
        
    except Exception as e:
        print(f"Warning: Could not add text to icon: {e}")
    
    return image

def convert_png_to_ico(png_path, ico_path):
    """Convert PNG file to multi-size ICO file."""
    if not PIL_AVAILABLE:
        print("Error: PIL/Pillow required for PNG to ICO conversion")
        return False
    
    try:
        # Load PNG image
        with Image.open(png_path) as img:
            # Ensure RGBA mode
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Generate multiple sizes for ICO
            sizes = [16, 24, 32, 48, 64, 96, 128, 256]
            images = []
            
            for size in sizes:
                resized = img.resize((size, size), Image.LANCZOS)
                images.append(resized)
            
            # Save as ICO with multiple sizes
            images[0].save(
                ico_path,
                format='ICO',
                sizes=[(size, size) for size in sizes],
                append_images=images[1:]
            )
            
            print(f"Successfully converted {png_path} to {ico_path}")
            return True
            
    except Exception as e:
        print(f"Error converting PNG to ICO: {e}")
        return False

def find_best_png():
    """Find the best PNG asset to use as icon source."""
    project_root = Path(__file__).parent.parent
    
    # Candidate PNG files in order of preference
    candidates = [
        project_root / "assets" / "app_icon.png",
        project_root / "assets" / "app_icon_gradient.png",
        project_root / "assets" / "app_icon_text.png",
        project_root / "assets" / "icon.png",
        project_root / "installer" / "app_icon.png",
        project_root / "icon.png",
    ]
    
    for candidate in candidates:
        if candidate.exists():
            print(f"Found PNG asset: {candidate}")
            return candidate
    
    return None

def generate_icon():
    """Main icon generation function."""
    project_root = Path(__file__).parent.parent
    
    # Output paths
    installer_dir = project_root / "installer"
    installer_dir.mkdir(exist_ok=True)
    
    assets_dir = project_root / "assets"
    assets_dir.mkdir(exist_ok=True)
    
    ico_paths = [
        installer_dir / "app_icon.ico",
        assets_dir / "app_icon.ico",
    ]
    
    print("UnsplashGPT-Enhanced Icon Generator")
    print("===================================\n")
    
    # Try to find existing PNG first
    png_source = find_best_png()
    
    if png_source:
        print(f"Using existing PNG: {png_source}")
        
        # Convert PNG to ICO for all output locations
        success = False
        for ico_path in ico_paths:
            if convert_png_to_ico(png_source, ico_path):
                success = True
        
        if success:
            print("\nIcon generation completed successfully!")
            return True
        else:
            print("\nFailed to convert PNG to ICO, trying programmatic generation...")
    
    # Fallback to programmatic icon generation
    print("Creating programmatic icon...")
    
    if not PIL_AVAILABLE:
        print("\nError: Cannot generate icon without PIL/Pillow")
        print("Install with: pip install Pillow")
        return False
    
    # Generate programmatic icon
    icon_image = create_programmatic_icon()
    if not icon_image:
        print("Failed to create programmatic icon")
        return False
    
    # Save as ICO to all locations
    success = False
    
    for ico_path in ico_paths:
        try:
            # Generate multiple sizes
            sizes = [16, 24, 32, 48, 64, 96, 128, 256]
            images = []
            
            for size in sizes:
                resized = icon_image.resize((size, size), Image.LANCZOS)
                images.append(resized)
            
            # Save as ICO
            images[0].save(
                ico_path,
                format='ICO',
                sizes=[(size, size) for size in sizes],
                append_images=images[1:]
            )
            
            print(f"Generated icon: {ico_path}")
            success = True
            
        except Exception as e:
            print(f"Error saving icon to {ico_path}: {e}")
    
    if success:
        print("\nProgrammatic icon generation completed successfully!")
        return True
    else:
        print("\nFailed to generate any icons")
        return False

def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h', 'help']:
        print("Icon Generator for UnsplashGPT-Enhanced")
        print("Usage: python generate_icon.py [generate]")
        print("\nThis script:")
        print("1. Searches for existing PNG assets")
        print("2. Converts PNG to multi-size ICO file")
        print("3. Falls back to programmatic icon if no PNG found")
        print("\nOutput locations:")
        print("- installer/app_icon.ico")
        print("- assets/app_icon.ico")
        print("\nRequirements:")
        print("- PIL/Pillow: pip install Pillow")
        return
    
    # Check if we should force regeneration
    force = len(sys.argv) > 1 and sys.argv[1] == 'generate'
    
    # Check if icons already exist
    project_root = Path(__file__).parent.parent
    existing_icons = list(project_root.glob("**/app_icon.ico"))
    
    if existing_icons and not force:
        print(f"Icon already exists: {existing_icons[0]}")
        print("Use 'python generate_icon.py generate' to force regeneration")
        return
    
    # Generate icon
    success = generate_icon()
    
    if success:
        print("\n✅ Icon generation successful!")
        print("The generated .ico file will be used by PyInstaller for the executable.")
    else:
        print("\n❌ Icon generation failed.")
        print("PyInstaller will build without a custom icon.")
        sys.exit(1)

if __name__ == "__main__":
    main()
