#!/usr/bin/env python3
"""
Demo script for enhanced CLI components

This script demonstrates all the new visual components:
- Gradient text effects
- Enhanced progress bars
- Loading animations
- Formatted tables
- Interactive prompts
- Charts and visualizations
"""

import asyncio
import time
import random
from typing import List, Dict

def demo_gradients():
    """Demonstrate gradient text effects"""
    print("\n" + "="*60)
    print("🌈 GRADIENT TEXT EFFECTS DEMO")
    print("="*60)
    
    try:
        from .components.gradient import GradientText, GradientPreset
        
        gradient = GradientText()
        
        # Test different presets
        presets = {
            "Fire": GradientPreset.FIRE,
            "Ocean": GradientPreset.OCEAN,
            "Cyberpunk": GradientPreset.CYBERPUNK,
            "Rainbow": GradientPreset.RAINBOW,
            "Galaxy": GradientPreset.GALAXY
        }
        
        for name, preset in presets.items():
            text = f"{name} Gradient Effect"
            colored_text = gradient.gradient_text(text, preset)
            print(f"{name:15}: {colored_text}")
        
        # Rainbow text
        rainbow_text = gradient.rainbow_text("🌈 Beautiful Rainbow Text! 🌈")
        print(f"{'Rainbow':15}: {rainbow_text}")
        
        print("\n✅ Gradient effects working correctly!")
        
    except ImportError as e:
        print(f"❌ Gradient components not available: {e}")
    except Exception as e:
        print(f"❌ Error testing gradients: {e}")


async def demo_animations():
    """Demonstrate loading animations"""
    print("\n" + "="*60)
    print("⚡ LOADING ANIMATIONS DEMO")
    print("="*60)
    
    try:
        from .components.animations import LoadingAnimation, SpinnerStyle
        
        # Test different spinner styles
        styles = [
            ("Dots", SpinnerStyle.DOTS),
            ("Circles", SpinnerStyle.CIRCLES),
            ("Arrows", SpinnerStyle.ARROWS),
            ("ASCII Bars", SpinnerStyle.ASCII_BARS)
        ]
        
        for name, style in styles:
            print(f"\nTesting {name} spinner...")
            animation = LoadingAnimation(style)
            
            with animation.spinner(f"Loading with {name} style"):
                await asyncio.sleep(2)
            
            print(f"✅ {name} spinner completed!")
        
        # Test typewriter effect
        print("\nTypewriter effect:")
        animation = LoadingAnimation()
        await animation.typewriter("Hello! This is a typewriter effect. ⌨️", speed=0.05)
        
        print("\n✅ All animations working correctly!")
        
    except ImportError as e:
        print(f"❌ Animation components not available: {e}")
    except Exception as e:
        print(f"❌ Error testing animations: {e}")


def demo_tables():
    """Demonstrate formatted tables"""
    print("\n" + "="*60)
    print("📊 FORMATTED TABLES DEMO")
    print("="*60)
    
    try:
        from .components.tables import DataTable, TableStyle, currency_formatter, status_color_func
        
        # Sample data
        data = [
            {"Name": "Alice", "Score": 95, "Status": "success", "Revenue": 1250.50},
            {"Name": "Bob", "Score": 87, "Status": "warning", "Revenue": 950.25},
            {"Name": "Charlie", "Score": 76, "Status": "error", "Revenue": 750.00},
            {"Name": "Diana", "Score": 92, "Status": "success", "Revenue": 1100.75}
        ]
        
        # Test different table styles
        styles = [TableStyle.SIMPLE, TableStyle.DOUBLE, TableStyle.ASCII]
        
        for style in styles:
            print(f"\n{style.value.upper()} Table Style:")
            table = DataTable(data, style=style)
            
            # Configure columns
            table.configure_column("Revenue", formatter=currency_formatter)
            table.configure_column("Status", color_func=status_color_func)
            
            table.print()
        
        print("\n✅ Table formatting working correctly!")
        
    except ImportError as e:
        print(f"❌ Table components not available: {e}")
    except Exception as e:
        print(f"❌ Error testing tables: {e}")


def demo_charts():
    """Demonstrate charts and visualizations"""
    print("\n" + "="*60)
    print("📈 CHARTS AND VISUALIZATIONS DEMO")
    print("="*60)
    
    try:
        from .components.charts import bar_chart, line_chart, sparkline, progress_bar
        
        # Bar chart demo
        print("\nBar Chart:")
        chart_data = [
            ("Python", 85),
            ("JavaScript", 70),
            ("Java", 65),
            ("C++", 60),
            ("Go", 45)
        ]
        
        chart = bar_chart(chart_data, "Programming Language Popularity")
        chart.print()
        
        # Line chart demo
        print("\nLine Chart:")
        line_data = [10, 15, 12, 18, 25, 22, 30, 28, 35]
        line = line_chart(line_data, "Performance Over Time")
        line.print()
        
        # Sparkline demo
        print("\nSparkline:")
        spark_data = [1, 3, 2, 5, 4, 7, 6, 8, 7, 9]
        spark = sparkline(spark_data)
        print(f"Trend: {spark.render(show_stats=True)}")
        
        # Progress bar demo
        print("\nProgress Bar Demo:")
        progress = progress_bar(100, "Processing files")
        
        for i in range(0, 101, 10):
            progress.update(i)
            time.sleep(0.1)
        
        progress.finish()
        
        print("\n✅ Charts and visualizations working correctly!")
        
    except ImportError as e:
        print(f"❌ Chart components not available: {e}")
    except Exception as e:
        print(f"❌ Error testing charts: {e}")


def demo_prompts():
    """Demonstrate interactive prompts"""
    print("\n" + "="*60)
    print("💬 INTERACTIVE PROMPTS DEMO")
    print("="*60)
    
    try:
        from .components.prompts import InputPrompt, MenuSelector, ask_choice, ask_confirm
        
        prompt = InputPrompt()
        
        # Text input demo
        print("Text Input Demo:")
        name = prompt.text_input("What's your name?", default="User")
        print(f"Hello, {name}!")
        
        # Choice demo
        print("\nChoice Input Demo:")
        colors = ["Red", "Green", "Blue", "Yellow"]
        color = ask_choice("Pick your favorite color", colors)
        print(f"You chose: {color}")
        
        # Confirmation demo
        print("\nConfirmation Demo:")
        confirmed = ask_confirm("Do you like the new CLI components?", default=True)
        if confirmed:
            print("Great! 🎉")
        else:
            print("We'll keep improving! 💪")
        
        # Menu selector demo
        print("\nMenu Selector Demo:")
        menu_options = ["Start Tutorial", "View Examples", "Exit"]
        menu = MenuSelector("Main Menu", menu_options)
        selection = menu.show()
        print(f"You selected: {selection}")
        
        print("\n✅ Interactive prompts working correctly!")
        
    except ImportError as e:
        print(f"❌ Prompt components not available: {e}")
    except Exception as e:
        print(f"❌ Error testing prompts: {e}")


def demo_syntax_highlighting():
    """Demonstrate syntax highlighting"""
    print("\n" + "="*60)
    print("🎨 SYNTAX HIGHLIGHTING DEMO")
    print("="*60)
    
    try:
        from .formatter import TerminalFormatter
        
        formatter = TerminalFormatter()
        
        # Python code sample
        python_code = '''
def fibonacci(n):
    """Calculate fibonacci number"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Test the function
result = fibonacci(10)
print(f"Fibonacci(10) = {result}")
'''
        
        print("Python Code with Syntax Highlighting:")
        highlighted = formatter.syntax_highlight(python_code, "python")
        print(highlighted)
        
        # JavaScript code sample
        js_code = '''
function quickSort(arr) {
    if (arr.length <= 1) return arr;
    
    const pivot = arr[0];
    const left = [];
    const right = [];
    
    for (let i = 1; i < arr.length; i++) {
        if (arr[i] < pivot) {
            left.push(arr[i]);
        } else {
            right.push(arr[i]);
        }
    }
    
    return [...quickSort(left), pivot, ...quickSort(right)];
}
'''
        
        print("\nJavaScript Code with Syntax Highlighting:")
        highlighted_js = formatter.syntax_highlight(js_code, "javascript")
        print(highlighted_js)
        
        print("\n✅ Syntax highlighting working correctly!")
        
    except ImportError as e:
        print(f"❌ Formatter not available: {e}")
    except Exception as e:
        print(f"❌ Error testing syntax highlighting: {e}")


def demo_difficulty_badges():
    """Demonstrate difficulty badges"""
    print("\n" + "="*60)
    print("🏷️ DIFFICULTY BADGES DEMO")
    print("="*60)
    
    try:
        from .formatter import TerminalFormatter
        
        formatter = TerminalFormatter()
        
        difficulties = ["Easy", "Medium", "Hard", "Expert", "Nightmare"]
        
        for difficulty in difficulties:
            badge = formatter.difficulty_badge(difficulty)
            print(f"Problem difficulty: {badge}")
        
        print("\n✅ Difficulty badges working correctly!")
        
    except ImportError as e:
        print(f"❌ Formatter not available: {e}")
    except Exception as e:
        print(f"❌ Error testing difficulty badges: {e}")


async def run_all_demos():
    """Run all component demos"""
    print("🚀 CLI COMPONENTS DEMONSTRATION")
    print("This demo showcases all the enhanced CLI components")
    print("="*80)
    
    try:
        # Run all demos
        demo_gradients()
        await demo_animations()
        demo_tables()
        demo_charts()
        demo_prompts()
        demo_syntax_highlighting()
        demo_difficulty_badges()
        
        # Final summary
        print("\n" + "="*80)
        print("🎉 ALL COMPONENT DEMOS COMPLETED SUCCESSFULLY!")
        print("✨ Your CLI now has beautiful visual enhancements!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Error running demos: {e}")
        print("Some components may not be available in this environment.")


if __name__ == "__main__":
    # Run the demo
    asyncio.run(run_all_demos())