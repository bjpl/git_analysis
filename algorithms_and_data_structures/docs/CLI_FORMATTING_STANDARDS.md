# CLI Formatting Standards

## 🎨 Beautiful CLI Design System

This document defines the unified formatting standards for the Algorithm Learning Platform CLI, ensuring consistent and beautiful output across all modules.

## 📚 Core Principles

### Visual Hierarchy
- **Headers**: Use DOUBLE_EDGE boxes with magenta/bright_blue colors
- **Content**: Use ROUNDED boxes with cyan borders
- **Emphasis**: Use HEAVY_HEAD boxes for important information
- **Code**: Use ROUNDED boxes with syntax highlighting

### Color Palette

#### Primary Colors (Gradient Flow)
- `bold magenta` - Headers and main titles
- `bright_blue` - Borders and accents
- `cyan` - Subtitles and secondary information

#### Semantic Colors
- `bold green` - Success messages (✅)
- `bold yellow` - Warnings and highlights (⚠️)
- `bold red` - Errors and critical info (❌)
- `italic cyan` - Information and tips (ℹ️)

#### Content Colors
- `white` - Main text
- `bright_white` - Secondary text
- `dim white` - Muted text

### Spacing Standards
- Panel padding: `(1, 2)` - 1 line vertical, 2 characters horizontal
- Section gap: 1 line between major sections
- Indentation: 2 spaces for nested content

## 🚀 Implementation

### Using the Unified Formatter

```python
from src.cli_formatter import CLIFormatter, BoxStyle

# Initialize formatter
formatter = CLIFormatter()

# Display header
formatter.display_header(
    "🚀 Algorithm Learning Platform",
    "Master Data Structures & Algorithms",
    BoxStyle.HEADER
)

# Display content panel
formatter.display_panel(
    "Your content here",
    title="📚 Section Title",
    style=BoxStyle.CONTENT
)

# Display table
columns = [
    {'name': 'Column 1', 'style': 'cyan'},
    {'name': 'Column 2', 'style': 'yellow'}
]
rows = [['Data 1', 'Data 2']]
formatter.display_table("Table Title", columns, rows)

# Display code
formatter.display_code(
    "def hello():\n    print('Hello!')",
    title="Example Code",
    language="python"
)

# Status messages
formatter.success("Operation completed!")
formatter.warning("Check this warning")
formatter.error("An error occurred")
formatter.info("Helpful information")
```

## 📦 Box Styles

### DOUBLE_EDGE (Headers)
```
╔═══════════════════╗
║     Header        ║
╚═══════════════════╝
```

### ROUNDED (Content)
```
┌───────────────────┐
│     Content       │
└───────────────────┘
```

### HEAVY_HEAD (Emphasis)
```
┏━━━━━━━━━━━━━━━━━━┓
┃    Important      ┃
┗━━━━━━━━━━━━━━━━━━┛
```

## 🎯 Component Standards

### Headers
- Always use DOUBLE_EDGE box style
- Primary color: bold magenta
- Border color: bright_blue
- Include emoji for visual anchor
- Center-align text

### Tables
- Use ROUNDED box style
- Header style: bold magenta
- Border style: bright_blue
- Title style: cyan with emoji
- Zebra striping for rows (optional)

### Code Blocks
- Use ROUNDED box style
- Monokai syntax theme
- Line numbers enabled
- Title with 💻 emoji
- Padding: (1, 2)

### Progress Bars
- Spinner: dots style in magenta
- Bar: blue with green completion
- Percentage: yellow text
- Description: cyan text

### Trees
- Root: folder emoji + magenta text
- Branches: cyan guide lines
- Folders: 📁 emoji
- Files: 📄 emoji
- Values: white text

## 🔄 Fallback Modes

### Rich Not Available
1. Try colorama for colored output
2. Fall back to plain text with ASCII borders

### Colorama Fallback
- Use basic ANSI colors
- ASCII box drawing characters
- Maintain emoji support

### Plain Text Fallback
- Simple ASCII borders (-, +, |)
- No colors
- Preserve structure and alignment

## ✨ Best Practices

1. **Consistency**: Always use the unified formatter
2. **Emoji Usage**: One emoji per title/section
3. **Color Balance**: Don't overuse bright colors
4. **Spacing**: Maintain breathing room between elements
5. **Accessibility**: Ensure fallback modes work properly

## 📊 Visual Examples

### Complete Dashboard Layout
```
╔════════════════════════════════════════════╗
║    🚀 Algorithm Learning Platform          ║
╚════════════════════════════════════════════╝

┌─────────── 📚 Progress Overview ───────────┐
│ • Lessons: 12/20 completed                 │
│ • Practice: 45 problems solved             │
│ • Quiz Score: 92%                         │
└────────────────────────────────────────────┘

      📊 Algorithm Complexity      
┌──────────┬──────────┬──────────┐
│ Algorithm│ Time     │ Space    │
├──────────┼──────────┼──────────┤
│ QuickSort│ O(nlogn) │ O(logn)  │
│ MergeSort│ O(nlogn) │ O(n)     │
└──────────┴──────────┴──────────┘

✅ Ready to continue learning!
```

## 🛠️ Migration Guide

### Updating Existing Code

Replace old formatting:
```python
# Old
print("=" * 60)
print(title.center(60))
print("=" * 60)

# New
formatter.display_header(title, subtitle, BoxStyle.HEADER)
```

Replace status messages:
```python
# Old
print(f"Success: {message}")

# New
formatter.success(message)
```

## 📝 Testing

Run the formatter test suite:
```bash
python tests/test_unified_formatter.py
```

This will demonstrate all formatting capabilities and ensure consistency.

## 🚦 Checklist

Before releasing any CLI module:
- [ ] Uses unified formatter for all output
- [ ] Consistent color scheme applied
- [ ] Proper box styles for context
- [ ] Emoji usage follows standards
- [ ] Fallback modes tested
- [ ] Spacing and padding correct
- [ ] Visual hierarchy maintained

## 📚 Resources

- Formatter Module: `src/cli_formatter.py`
- Test Suite: `tests/test_unified_formatter.py`
- Example Implementation: `algo_teach.py`
- Rich Documentation: https://rich.readthedocs.io/