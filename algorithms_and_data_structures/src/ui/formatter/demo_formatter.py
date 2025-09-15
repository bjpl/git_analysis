"""
Enhanced Formatter Demo Script
Showcases all formatting capabilities with Windows PowerShell compatibility
"""

import sys
import os
import time
import random

# Add the source directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ui.formatter.enhanced_formatter import (
    EnhancedFormatter, Color, HeaderStyle, TableStyle,
    quick_header, quick_table, quick_panel, quick_progress
)


def demo_terminal_capabilities(formatter):
    """Demonstrate terminal capability detection"""
    print(quick_header("Terminal Capabilities", "boxed", "bright_yellow"))
    
    caps = formatter.capabilities
    
    capability_data = [
        ["Feature", "Status", "Value"],
        ["Color Support", "✓" if caps.supports_color else "✗", str(caps.supports_color)],
        ["256 Colors", "✓" if caps.supports_256_color else "✗", str(caps.supports_256_color)],
        ["True Color", "✓" if caps.supports_true_color else "✗", str(caps.supports_true_color)],
        ["Terminal Width", "✓", str(caps.width)],
        ["Terminal Height", "✓", str(caps.height)],
        ["Windows OS", "✓" if caps.is_windows else "✗", str(caps.is_windows)],
        ["PowerShell", "✓" if caps.is_powershell else "✗", str(caps.is_powershell)]
    ]
    
    print(formatter.create_table(capability_data[1:], capability_data[0], TableStyle.FANCY_GRID))
    print()


def demo_colors_and_styles(formatter):
    """Demonstrate color and style capabilities"""
    print(quick_header("Colors and Styles Demo", "banner", "bright_magenta"))
    
    # Basic colors
    print("Basic Colors:")
    colors = [Color.RED, Color.GREEN, Color.BLUE, Color.YELLOW, Color.CYAN, Color.MAGENTA]
    for color in colors:
        colored_text = formatter.colorize(f"  {color.name.lower()} text", color)
        print(colored_text)
    
    print("\nBright Colors:")
    bright_colors = [Color.BRIGHT_RED, Color.BRIGHT_GREEN, Color.BRIGHT_BLUE, 
                    Color.BRIGHT_YELLOW, Color.BRIGHT_CYAN, Color.BRIGHT_MAGENTA]
    for color in bright_colors:
        colored_text = formatter.colorize(f"  {color.name.lower()} text", color)
        print(colored_text)
    
    print("\nStyles:")
    styles = [Color.BOLD, Color.UNDERLINE, Color.DIM]
    for style in styles:
        styled_text = formatter.colorize(f"  {style.name.lower()} text", Color.WHITE, style=style)
        print(styled_text)
    
    print("\nBackground Colors:")
    bg_colors = [Color.BG_RED, Color.BG_GREEN, Color.BG_BLUE]
    for bg_color in bg_colors:
        bg_text = formatter.colorize(f"  {bg_color.name.lower()} background", Color.WHITE, bg_color=bg_color)
        print(bg_text)
    
    print()


def demo_gradient_effects(formatter):
    """Demonstrate gradient text effects"""
    print(quick_header("Gradient Effects", "underlined", "bright_cyan"))
    
    # Rainbow gradient
    rainbow_colors = [
        Color.BRIGHT_RED, Color.BRIGHT_YELLOW, Color.BRIGHT_GREEN,
        Color.BRIGHT_CYAN, Color.BRIGHT_BLUE, Color.BRIGHT_MAGENTA
    ]
    
    rainbow_text = formatter.gradient_text("Rainbow Gradient Text Effect", rainbow_colors)
    print(f"Rainbow: {rainbow_text}")
    
    # Fire gradient
    fire_colors = [Color.BRIGHT_RED, Color.BRIGHT_YELLOW, Color.YELLOW, Color.RED]
    fire_text = formatter.gradient_text("Fire Gradient Effect", fire_colors)
    print(f"Fire:    {fire_text}")
    
    # Ocean gradient
    ocean_colors = [Color.BRIGHT_BLUE, Color.BRIGHT_CYAN, Color.CYAN, Color.BLUE]
    ocean_text = formatter.gradient_text("Ocean Gradient Effect", ocean_colors)
    print(f"Ocean:   {ocean_text}")
    
    # Sunset gradient
    sunset_colors = [Color.BRIGHT_YELLOW, Color.YELLOW, Color.RED, Color.MAGENTA]
    sunset_text = formatter.gradient_text("Sunset Gradient Effect", sunset_colors)
    print(f"Sunset:  {sunset_text}")
    
    print()


def demo_header_styles(formatter):
    """Demonstrate different header styles"""
    print(quick_header("Header Styles Showcase", "gradient"))
    
    print("1. Banner Style:")
    print(formatter.create_header("Banner Header Example", HeaderStyle.BANNER, width=60, color=Color.BRIGHT_BLUE))
    print()
    
    print("2. Centered Style:")
    print(formatter.create_header("Centered Header Example", HeaderStyle.CENTERED, width=60, color=Color.BRIGHT_GREEN))
    print()
    
    print("3. Boxed Style:")
    print(formatter.create_header("Boxed Header Example", HeaderStyle.BOXED, width=60, color=Color.BRIGHT_YELLOW))
    print()
    
    print("4. Underlined Style:")
    print(formatter.create_header("Underlined Header Example", HeaderStyle.UNDERLINED, width=60, color=Color.BRIGHT_RED))
    print()
    
    print("5. Gradient Style:")
    print(formatter.create_header("Gradient Header Example", HeaderStyle.GRADIENT, width=60))
    print()


def demo_progress_indicators(formatter):
    """Demonstrate progress bars and spinners"""
    print(quick_header("Progress Indicators", "boxed", "bright_green"))
    
    print("Progress Bars:")
    for i in range(0, 101, 20):
        progress = i / 100.0
        bar = formatter.create_progress_bar(progress, width=40, show_percentage=True)
        print(f"  {i:3d}%: {bar}")
    
    print("\nDifferent Progress Bar Styles:")
    
    # Custom colored progress bars
    styles = [
        (Color.BRIGHT_GREEN, "Success"),
        (Color.BRIGHT_YELLOW, "Warning"),
        (Color.BRIGHT_RED, "Error"),
        (Color.BRIGHT_CYAN, "Info")
    ]
    
    for color, label in styles:
        bar = formatter.create_progress_bar(0.75, width=30, color=color)
        print(f"  {label:8s}: {bar}")
    
    print("\nSpinner Demo (3 seconds):")
    
    # Demonstrate different spinner styles
    spinner_styles = ["simple", "dots_simple", "arrows"]
    
    for style in spinner_styles:
        print(f"  {style.capitalize()} spinner: ", end="", flush=True)
        
        with formatter.create_spinner(f"Loading with {style}...", style):
            time.sleep(1)
        
        print("Done!")
    
    print()


def demo_table_formatting(formatter):
    """Demonstrate table formatting capabilities"""
    print(quick_header("Table Formatting", "banner", "bright_cyan"))
    
    # Sample data for tables
    employee_data = [
        ["Alice Johnson", "Senior Engineer", "Engineering", "85000", "5 years"],
        ["Bob Smith", "Product Manager", "Product", "95000", "3 years"],
        ["Carol Davis", "UX Designer", "Design", "70000", "2 years"],
        ["David Wilson", "DevOps Engineer", "Engineering", "80000", "4 years"],
        ["Eva Brown", "Data Scientist", "Analytics", "90000", "3 years"],
        ["Frank Miller", "QA Engineer", "Engineering", "65000", "2 years"]
    ]
    
    headers = ["Name", "Position", "Department", "Salary", "Experience"]
    
    print("1. Grid Style (Default):")
    grid_table = formatter.create_table(employee_data, headers, TableStyle.GRID, alternating_colors=True)
    print(grid_table)
    print()
    
    print("2. Simple Style:")
    simple_table = formatter.create_table(employee_data[:3], headers, TableStyle.SIMPLE, alternating_colors=True)
    print(simple_table)
    print()
    
    print("3. Fancy Grid Style:")
    fancy_table = formatter.create_table(employee_data[:3], headers, TableStyle.FANCY_GRID, alternating_colors=True)
    print(fancy_table)
    print()
    
    print("4. Minimal Style:")
    minimal_table = formatter.create_table(employee_data[:3], headers, TableStyle.MINIMAL, alternating_colors=False)
    print(minimal_table)
    print()


def demo_panel_system(formatter):
    """Demonstrate panel creation and multi-panel layouts"""
    print(quick_header("Panel System", "gradient"))
    
    print("1. Basic Panel:")
    basic_panel = formatter.create_panel(
        "System Information",
        "Operating System: Windows 11\nProcessor: Intel Core i7\nMemory: 16 GB RAM\nStorage: 512 GB SSD",
        width=50,
        color=Color.BRIGHT_BLUE
    )
    print(basic_panel)
    print()
    
    print("2. Panel with Long Content (Auto-wrapping):")
    long_content = ("This is a very long line of content that will be automatically wrapped "
                   "within the panel boundaries to ensure proper display formatting. The panel "
                   "system handles text wrapping intelligently to maintain readability.")
    
    long_panel = formatter.create_panel(
        "Auto-Wrapping Demo",
        long_content,
        width=60,
        color=Color.BRIGHT_GREEN
    )
    print(long_panel)
    print()
    
    print("3. Multi-Panel Layout:")
    panels = [
        {
            "title": "CPU Usage",
            "content": "Current: 45%\nAverage: 38%\nPeak: 78%",
            "color": Color.BRIGHT_RED,
            "width": 30
        },
        {
            "title": "Memory Usage", 
            "content": "Used: 8.2 GB\nFree: 7.8 GB\nCached: 2.1 GB",
            "color": Color.BRIGHT_YELLOW,
            "width": 30
        },
        {
            "title": "Disk Usage",
            "content": "C: Drive: 245 GB used\n512 GB total\n52% full",
            "color": Color.BRIGHT_GREEN,
            "width": 30
        }
    ]
    
    multi_panel = formatter.create_multi_panel(panels, "vertical")
    print(multi_panel)
    print()


def demo_box_drawing(formatter):
    """Demonstrate Windows-safe box drawing"""
    print(quick_header("Box Drawing Characters", "boxed", "bright_white"))
    
    print("Available Box Characters (Windows-safe ASCII):")
    
    box_demo_data = []
    for char_name, char_value in formatter.box_chars.items():
        # Display character name and actual character
        display_char = f"'{char_value}'" if len(char_value) == 1 else f'"{char_value}"'
        box_demo_data.append([char_name.replace('_', ' ').title(), display_char, f"ASCII: {ord(char_value[0])}"])
    
    headers = ["Character Name", "Symbol", "ASCII Code"]
    print(formatter.create_table(box_demo_data, headers, TableStyle.GRID))
    
    print("\nBox Drawing Example:")
    
    # Create a custom box using the safe characters
    width = 40
    height = 5
    
    box_lines = []
    
    # Top border
    top_line = (formatter.box_chars['top_left'] + 
               formatter.box_chars['horizontal'] * (width - 2) + 
               formatter.box_chars['top_right'])
    box_lines.append(formatter.colorize(top_line, Color.BRIGHT_CYAN))
    
    # Content lines
    for i in range(height - 2):
        if i == 1:
            content = " Windows-Safe Box Drawing Demo "
            padding = (width - 2 - len(content)) // 2
            content_line = (formatter.box_chars['vertical'] + 
                          ' ' * padding + content + 
                          ' ' * (width - 2 - len(content) - padding) + 
                          formatter.box_chars['vertical'])
        else:
            content_line = (formatter.box_chars['vertical'] + 
                          ' ' * (width - 2) + 
                          formatter.box_chars['vertical'])
        
        box_lines.append(formatter.colorize(content_line, Color.BRIGHT_CYAN))
    
    # Bottom border
    bottom_line = (formatter.box_chars['bottom_left'] + 
                  formatter.box_chars['horizontal'] * (width - 2) + 
                  formatter.box_chars['bottom_right'])
    box_lines.append(formatter.colorize(bottom_line, Color.BRIGHT_CYAN))
    
    for line in box_lines:
        print(line)
    
    print()


def demo_interactive_features(formatter):
    """Demonstrate interactive formatting features"""
    print(quick_header("Interactive Features", "banner", "bright_magenta"))
    
    print("1. Live Progress Simulation:")
    print("   Simulating file download...")
    
    # Simulate a download progress
    total_steps = 50
    for i in range(total_steps + 1):
        progress = i / total_steps
        bar = formatter.create_progress_bar(progress, width=40)
        
        # Clear line and print new progress
        print(f"\r   {bar}", end="", flush=True)
        time.sleep(0.05)
    
    print()  # New line after progress
    print("   Download complete!")
    print()
    
    print("2. Dynamic Status Updates:")
    statuses = [
        ("Initializing...", Color.BRIGHT_YELLOW),
        ("Connecting to server...", Color.BRIGHT_BLUE),
        ("Authenticating...", Color.BRIGHT_CYAN),
        ("Downloading data...", Color.BRIGHT_GREEN),
        ("Processing results...", Color.BRIGHT_MAGENTA),
        ("Complete!", Color.BRIGHT_GREEN)
    ]
    
    for status, color in statuses:
        colored_status = formatter.colorize(f"   Status: {status}", color, style=Color.BOLD)
        print(f"\r{formatter.clear_line()}{colored_status}", end="", flush=True)
        time.sleep(0.8)
    
    print()  # New line after status updates
    print()


def demo_real_world_examples(formatter):
    """Demonstrate real-world usage examples"""
    print(quick_header("Real-World Examples", "gradient"))
    
    print("1. System Dashboard:")
    
    # Create a system dashboard layout
    system_info = formatter.create_panel(
        "System Status",
        f"Uptime: 7 days, 14 hours\nCPU Temp: 45°C\nFan Speed: 1200 RPM\nLast Updated: {time.strftime('%H:%M:%S')}",
        color=Color.BRIGHT_BLUE,
        width=35
    )
    
    network_info = formatter.create_panel(
        "Network Status", 
        "Interface: Ethernet\nIP Address: 192.168.1.100\nGateway: 192.168.1.1\nDNS: 8.8.8.8",
        color=Color.BRIGHT_GREEN,
        width=35
    )
    
    print(system_info)
    print()
    print(network_info)
    print()
    
    print("2. Task Status Report:")
    
    task_data = [
        ["Database Backup", "✓ Completed", "00:15:23", "Success"],
        ["Log Rotation", "✓ Completed", "00:02:45", "Success"], 
        ["Security Scan", "⚠ Running", "00:08:12", "In Progress"],
        ["System Update", "⏸ Pending", "--:--:--", "Scheduled"],
        ["File Cleanup", "✗ Failed", "00:01:12", "Error"]
    ]
    
    task_headers = ["Task", "Status", "Duration", "Result"]
    task_table = formatter.create_table(task_data, task_headers, TableStyle.FANCY_GRID, alternating_colors=True)
    print(task_table)
    print()
    
    print("3. Application Log Viewer:")
    
    log_entries = [
        ["2024-01-15 10:30:15", "INFO", "Application started successfully"],
        ["2024-01-15 10:30:16", "INFO", "Database connection established"],
        ["2024-01-15 10:35:22", "WARN", "High memory usage detected (85%)"],
        ["2024-01-15 10:40:11", "ERROR", "Failed to connect to external API"],
        ["2024-01-15 10:45:33", "INFO", "External API connection restored"]
    ]
    
    print("Recent Log Entries:")
    for timestamp, level, message in log_entries:
        level_colors = {
            "INFO": Color.BRIGHT_GREEN,
            "WARN": Color.BRIGHT_YELLOW,
            "ERROR": Color.BRIGHT_RED
        }
        
        colored_level = formatter.colorize(f"[{level:5s}]", level_colors.get(level, Color.WHITE), style=Color.BOLD)
        timestamp_colored = formatter.colorize(timestamp, Color.BRIGHT_BLACK)
        
        print(f"  {timestamp_colored} {colored_level} {message}")
    
    print()


def demo_performance_test(formatter):
    """Demonstrate performance with large datasets"""
    print(quick_header("Performance Demo", "boxed", "bright_yellow"))
    
    print("Generating large dataset...")
    
    # Generate random data for performance testing
    departments = ["Engineering", "Marketing", "Sales", "HR", "Finance", "Operations"]
    positions = ["Manager", "Senior", "Junior", "Lead", "Director", "Analyst"]
    
    large_data = []
    for i in range(100):
        name = f"Employee {i+1:03d}"
        position = f"{random.choice(positions)} {random.choice(['Developer', 'Designer', 'Analyst', 'Manager'])}"
        department = random.choice(departments)
        salary = f"${random.randint(50000, 150000):,}"
        
        large_data.append([name, position, department, salary])
    
    headers = ["Name", "Position", "Department", "Salary"]
    
    print(f"Creating table with {len(large_data)} rows...")
    
    start_time = time.time()
    large_table = formatter.create_table(large_data[:20], headers, TableStyle.GRID, alternating_colors=True)
    end_time = time.time()
    
    print(f"Table generation time: {end_time - start_time:.3f} seconds")
    print("(Showing first 20 rows)")
    print()
    print(large_table)
    print()


def main():
    """Main demo function"""
    formatter = EnhancedFormatter()
    
    print(quick_header("Enhanced Terminal Formatter Demo", "gradient"))
    print()
    
    # Introduction
    intro_panel = formatter.create_panel(
        "Welcome to the Enhanced Terminal Formatter",
        ("This demo showcases all the formatting capabilities of the Enhanced Terminal Formatter, "
         "specifically designed for Windows PowerShell compatibility. All features use ASCII-safe "
         "box drawing characters and include fallbacks for limited terminal environments."),
        width=80,
        color=Color.BRIGHT_CYAN
    )
    print(intro_panel)
    print()
    
    # Run all demos
    demos = [
        ("Terminal Capabilities", demo_terminal_capabilities),
        ("Colors and Styles", demo_colors_and_styles),
        ("Gradient Effects", demo_gradient_effects),
        ("Header Styles", demo_header_styles),
        ("Progress Indicators", demo_progress_indicators),
        ("Table Formatting", demo_table_formatting),
        ("Panel System", demo_panel_system),
        ("Box Drawing", demo_box_drawing),
        ("Interactive Features", demo_interactive_features),
        ("Real-World Examples", demo_real_world_examples),
        ("Performance Test", demo_performance_test)
    ]
    
    for demo_name, demo_func in demos:
        try:
            demo_func(formatter)
            
            # Separator between demos
            print(formatter.colorize("─" * 80, Color.BRIGHT_BLACK))
            print()
            
        except KeyboardInterrupt:
            print("\nDemo interrupted by user.")
            break
        except Exception as e:
            error_msg = f"Error in {demo_name} demo: {str(e)}"
            print(formatter.colorize(error_msg, Color.BRIGHT_RED))
            print()
    
    # Conclusion
    conclusion_panel = formatter.create_panel(
        "Demo Complete",
        ("Thank you for exploring the Enhanced Terminal Formatter! "
         "This module provides professional terminal formatting with full Windows PowerShell compatibility. "
         "All features are designed to work reliably across different terminal environments."),
        width=80,
        color=Color.BRIGHT_GREEN
    )
    print(conclusion_panel)


if __name__ == "__main__":
    main()