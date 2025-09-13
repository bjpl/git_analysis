# CLI Design System - Windows PowerShell Compatible

## Overview
A comprehensive design system combining elegant academic styling with professional documentation hierarchy, optimized for Windows terminal environments.

## Core Design Principles

1. **Windows Terminal Compatibility** - ASCII-only box drawing characters
2. **Visual Hierarchy** - Clear information architecture
3. **Academic Elegance** - Learning-focused presentation
4. **Professional Documentation** - Structured content organization
5. **Accessibility** - High contrast and readable typography

## Color Palette

### Primary Colors (Windows Compatible)
```
Bright Cyan     (96) - Headers, titles, primary actions
Bright Blue     (94) - Secondary headers, navigation
Bright Green    (92) - Success states, progress indicators
Bright Yellow   (93) - Warnings, highlights, emphasis
Bright Red      (91) - Errors, critical information
Bright Magenta  (95) - Special content, callouts
Bright White    (97) - Primary text content
Gray           (90) - Secondary text, borders
```

### Gradient Effects (ASCII-based)
```
Light: ░░░ (25% density)
Medium: ▒▒▒ (50% density)  
Heavy: ▓▓▓ (75% density)
Solid: ███ (100% density)
```

## Typography System

### Text Hierarchy
```
H1 - Main Title:     [BRIGHT_CYAN + BOLD]
H2 - Section:        [BRIGHT_BLUE + BOLD]
H3 - Subsection:     [BRIGHT_MAGENTA + BOLD]
H4 - Item Header:    [BRIGHT_YELLOW + BOLD]
Body Text:           [BRIGHT_WHITE]
Secondary Text:      [GRAY]
Code/Commands:       [BRIGHT_GREEN + MONOSPACE]
```

### Emphasis Styles
```
**Bold Text**:       [BOLD]
*Italic Text*:       [UNDERLINE] (terminal alternative)
`Code Inline`:       [BRIGHT_GREEN + BACKGROUND_BLACK]
```

## Box Drawing System (ASCII Compatible)

### Basic Border Characters
```
┌ = +    ┐ = +    ┘ = +    └ = +
┬ = +    ┴ = +    ├ = +    ┤ = +
─ = -    │ = |    ┼ = +
```

### Border Styles

#### Simple Border
```
+----------------------------------+
|            Content               |
+----------------------------------+
```

#### Double Border (Heavy emphasis)
```
+==================================+
||            Content             ||
+==================================+
```

#### Gradient Border
```
+░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░+
░             Content             ░
+░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░+
```

#### Academic Frame
```
+====================================+
||  ███ ALGORITHM LEARNING SYSTEM  ███||
+====================================+
|                                    |
|  Content goes here...              |
|                                    |
+------------------------------------+
```

## Layout Patterns

### 1. Main Menu Layout
```
+========================================+
||  ███ ALGORITHMS & DATA STRUCTURES ███||
+========================================+
|                                        |
|  ▓ 1. Array & String Algorithms       |
|  ▒ 2. Sorting & Searching             |
|  ░ 3. Tree & Graph Algorithms         |
|  ▓ 4. Dynamic Programming             |
|  ▒ 5. System Design Patterns          |
|                                        |
|  [Enter number to continue...]         |
+----------------------------------------+
```

### 2. Learning Section Header
```
+============================================+
||  ░░░ SECTION 1: ARRAY ALGORITHMS ░░░     ||
+============================================+
|                                            |
|  Progress: [████████░░] 80% Complete      |
|                                            |
|  Topics Covered:                           |
|  ✓ Linear Search        ✓ Binary Search    |
|  ✓ Two Pointers         ○ Sliding Window   |
|                                            |
+--------------------------------------------+
```

### 3. Algorithm Detail View
```
+================================================+
||    ▓▓▓ BINARY SEARCH ALGORITHM ▓▓▓           ||
+================================================+
|                                                |
|  Complexity:                                   |
|  • Time:  O(log n)                            |
|  • Space: O(1)                                |
|                                                |
|  Use Cases:                                    |
|  ░ Sorted array searching                     |
|  ░ Finding insertion points                   |
|  ░ Peak finding problems                      |
|                                                |
+------------------------------------------------+
|  def binary_search(arr, target):              |
|      left, right = 0, len(arr) - 1            |
|      while left <= right:                     |
|          mid = (left + right) // 2             |
|          if arr[mid] == target:                |
|              return mid                        |
|          elif arr[mid] < target:               |
|              left = mid + 1                    |
|          else:                                 |
|              right = mid - 1                   |
|      return -1                                 |
+------------------------------------------------+
```

### 4. Progress Dashboard
```
+==================================================+
||  ▓▓▓ LEARNING PROGRESS DASHBOARD ▓▓▓           ||
+==================================================+
|                                                  |
|  Overall Progress: [██████████] 100%            |
|                                                  |
|  ┌─ Categories ─────────────────────────────────┐|
|  | Arrays & Strings    [████████░░] 80%        ||
|  | Sorting Algorithms  [██████████] 100%       ||
|  | Tree Structures     [██████░░░░] 60%        ||
|  | Graph Algorithms    [████░░░░░░] 40%        ||
|  | Dynamic Programming [██░░░░░░░░] 20%        ||
|  └─────────────────────────────────────────────┘|
|                                                  |
|  Recent Achievements:                            |
|  🏆 Quick Sort Master       🎯 Tree Traversal    |
|  ⚡ Binary Search Expert    📊 Graph Basics      |
|                                                  |
+--------------------------------------------------+
```

### 5. Interactive Menu
```
+============================================+
||  ░░░ CHOOSE YOUR LEARNING PATH ░░░       ||
+============================================+
|                                            |
|  ┌─ Beginner Track ────────────────────┐  |
|  │ ▓ Start with fundamentals           │  |
|  │ ▒ Basic sorting & searching         │  |
|  │ ░ Simple data structures            │  |
|  └─────────────────────────────────────┘  |
|                                            |
|  ┌─ Intermediate Track ─────────────────┐  |
|  │ ▓ Advanced algorithms               │  |
|  │ ▒ Complex data structures           │  |
|  │ ░ Optimization techniques           │  |
|  └─────────────────────────────────────┘  |
|                                            |
|  ┌─ Expert Track ───────────────────────┐  |
|  │ ▓ System design patterns            │  |
|  │ ▒ Advanced optimization             │  |
|  │ ░ Research-level algorithms         │  |
|  └─────────────────────────────────────┘  |
|                                            |
|  [Use arrow keys to navigate]              |
+--------------------------------------------+
```

### 6. Code Execution View
```
+====================================================+
||     ▓▓▓ ALGORITHM EXECUTION SANDBOX ▓▓▓          ||
+====================================================+
|                                                    |
|  Input:  [5, 2, 8, 1, 9, 3]                      |
|  Target: 8                                         |
|                                                    |
|  ┌─ Execution Steps ─────────────────────────────┐ |
|  │ Step 1: left=0, right=5, mid=2 → arr[2]=8   │ |
|  │ Step 2: Found target at index 2              │ |
|  │ Result: Index 2                              │ |
|  └───────────────────────────────────────────────┘ |
|                                                    |
|  ┌─ Performance Metrics ─────────────────────────┐ |
|  │ Time Complexity:  O(log n) ✓                 │ |
|  │ Space Complexity: O(1) ✓                     │ |
|  │ Execution Time:   0.001ms                    │ |
|  │ Memory Usage:     12KB                       │ |
|  └───────────────────────────────────────────────┘ |
|                                                    |
+----------------------------------------------------+
```

## Status Indicators

### Progress Bars
```
[██████████] 100% Complete
[████████░░]  80% In Progress
[████░░░░░░]  40% Started
[░░░░░░░░░░]   0% Not Started
```

### Status Icons (ASCII)
```
✓ Complete    ○ Pending     × Failed
→ In Progress ★ Featured    ! Important
? Help        ↑ Advanced    ↓ Basic
```

### Difficulty Levels
```
▓ Expert      (Dark block)
▒ Intermediate (Medium block)
░ Beginner    (Light block)
```

## Content Organization

### Information Hierarchy
1. **Title/Header** - Bright Cyan, Bold, Large
2. **Section Headers** - Bright Blue, Bold
3. **Subsections** - Bright Magenta, Bold
4. **Body Content** - Bright White
5. **Code Examples** - Bright Green, Monospace
6. **Meta Information** - Gray, Smaller

### Navigation Patterns
```
← Back        → Forward      ↑ Up Level    ↓ Down Level
⌂ Home        ⚙ Settings     ? Help        × Exit
```

## Implementation Guidelines

### Color Application
```python
# ANSI Color Codes for Windows
BRIGHT_CYAN = '\033[96m'
BRIGHT_BLUE = '\033[94m'
BRIGHT_GREEN = '\033[92m'
BRIGHT_YELLOW = '\033[93m'
BRIGHT_RED = '\033[91m'
BRIGHT_MAGENTA = '\033[95m'
BRIGHT_WHITE = '\033[97m'
GRAY = '\033[90m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
RESET = '\033[0m'
```

### Box Drawing Functions
```python
def create_border(width, height, style='simple'):
    if style == 'simple':
        top = '+' + '-' * (width-2) + '+'
        bottom = top
        side = '|' + ' ' * (width-2) + '|'
    elif style == 'double':
        top = '+' + '=' * (width-2) + '+'
        bottom = top
        side = '||' + ' ' * (width-4) + '||'
    return top, side, bottom
```

### Typography Functions
```python
def format_title(text):
    return f"{BRIGHT_CYAN}{BOLD}{text}{RESET}"

def format_header(text):
    return f"{BRIGHT_BLUE}{BOLD}{text}{RESET}"

def format_code(text):
    return f"{BRIGHT_GREEN}{text}{RESET}"
```

## Responsive Design

### Terminal Width Adaptations
- **80+ columns**: Full layout with sidebars
- **60-79 columns**: Compact layout, stacked elements
- **<60 columns**: Minimal layout, essential content only

### Content Scaling
- Automatically adjust box widths
- Wrap long text appropriately
- Scale progress bars proportionally
- Maintain aspect ratios for visual elements

## Accessibility Features

### High Contrast Mode
- Increase color brightness
- Thicker borders and separators
- Larger text spacing
- Bold emphasis for all headers

### Screen Reader Compatibility
- Descriptive text for visual elements
- Logical content order
- Clear navigation cues
- Semantic markup where possible

## Example Implementation Snippets

### Main Title Banner
```python
def render_main_title():
    width = 50
    title = "ALGORITHMS & DATA STRUCTURES"
    
    print(f"{BRIGHT_CYAN}+{'=' * (width-2)}+{RESET}")
    print(f"{BRIGHT_CYAN}||{GRAY}{'█' * 3}{RESET} {BRIGHT_WHITE}{BOLD}{title}{RESET} {GRAY}{'█' * 3}{BRIGHT_CYAN}||{RESET}")
    print(f"{BRIGHT_CYAN}+{'=' * (width-2)}+{RESET}")
```

### Progress Indicator
```python
def render_progress(percentage, width=20):
    filled = int(width * percentage / 100)
    empty = width - filled
    bar = f"{BRIGHT_GREEN}{'█' * filled}{GRAY}{'░' * empty}{RESET}"
    return f"[{bar}] {percentage}%"
```

### Section Header
```python
def render_section_header(title, width=40):
    padding = (width - len(title) - 8) // 2
    decoration = f"{GRAY}{'░' * 3}{RESET}"
    
    print(f"{BRIGHT_BLUE}+{'=' * (width-2)}+{RESET}")
    print(f"{BRIGHT_BLUE}||{RESET}  {decoration} {BRIGHT_BLUE}{BOLD}{title}{RESET} {decoration}  {BRIGHT_BLUE}||{RESET}")
    print(f"{BRIGHT_BLUE}+{'=' * (width-2)}+{RESET}")
```

This design system provides a comprehensive foundation for creating beautiful, functional CLI interfaces that work perfectly in Windows PowerShell environments while maintaining the elegant academic style and professional documentation hierarchy you requested.