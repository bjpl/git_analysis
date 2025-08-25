# UI Style Guide - Modern Material Design System

## Overview

This style guide defines the visual language and interaction patterns for the Unsplash Image Search application. It implements Material Design principles adapted for Tkinter, providing a modern, accessible, and cohesive user experience.

## Design Philosophy

### Core Principles

1. **Clarity** - Information hierarchy guides users naturally
2. **Consistency** - Predictable patterns across all interfaces  
3. **Accessibility** - Inclusive design for all users
4. **Efficiency** - Streamlined workflows and quick interactions
5. **Delight** - Smooth animations and thoughtful micro-interactions

### Material Design Adaptation

- **Elevation & Depth** - Simulated through borders, shadows, and color
- **Motion & Animation** - Smooth transitions and meaningful animations
- **Color & Theme** - Comprehensive light/dark theme system
- **Typography** - Clear hierarchy with Segoe UI font family
- **Touch-First** - Generous hit targets and spacing

## Color System

### Primary Palette

```python
# Light Theme
PRIMARY = "#1976d2"          # Blue 700
PRIMARY_VARIANT = "#1565c0"   # Blue 800
SECONDARY = "#03dac6"         # Teal A400
BACKGROUND = "#ffffff"        # Pure white
SURFACE = "#ffffff"           # Pure white
ERROR = "#b00020"            # Red A700

# Dark Theme  
PRIMARY = "#bb86fc"          # Purple 200
PRIMARY_VARIANT = "#985eff"   # Purple A100
SECONDARY = "#03dac6"         # Teal A400
BACKGROUND = "#121212"        # Near black
SURFACE = "#1f1f1f"          # Dark grey
ERROR = "#cf6679"            # Pink A100
```

### Extended Color Palette

#### Blue Scale
- **50**: `#e3f2fd` - Very light blue for backgrounds
- **100**: `#bbdefb` - Light blue for hover states
- **500**: `#2196f3` - Primary blue for interactive elements
- **700**: `#1976d2` - Default primary color
- **900**: `#0d47a1` - Dark blue for emphasis

#### Semantic Colors
- **Success**: `#4caf50` (Green 500)
- **Warning**: `#ff9800` (Orange 500)  
- **Error**: `#f44336` (Red 500)
- **Info**: `#2196f3` (Blue 500)

### Usage Guidelines

- Use primary colors for main actions and navigation
- Secondary colors for FABs and accent elements
- Surface colors for cards and elevated components
- Semantic colors for status indicators and feedback

## Typography

### Font Stack
Primary: **Segoe UI** (Windows), fallback to system defaults

### Type Scale

| Style | Size | Weight | Usage |
|-------|------|--------|-------|
| **Headline Large** | 32px | Normal | Page titles |
| **Headline Medium** | 28px | Normal | Section headers |
| **Headline Small** | 24px | Normal | Card headers |
| **Title Large** | 22px | Normal | Dialog titles |
| **Title Medium** | 16px | Bold | Component labels |
| **Title Small** | 14px | Bold | Field labels |
| **Body Large** | 16px | Normal | Main content |
| **Body Medium** | 14px | Normal | Secondary content |
| **Body Small** | 12px | Normal | Captions, metadata |
| **Label Large** | 14px | Bold | Button text |
| **Label Medium** | 12px | Bold | Form labels |
| **Label Small** | 11px | Bold | Chips, badges |

### Implementation
```python
# Creating styled typography
title_label = style_manager.create_label(
    parent, "Page Title", heading=1  # Uses Headline Large
)

body_text = style_manager.create_label(
    parent, "Content text"  # Uses Body Medium (default)
)
```

## Layout & Spacing

### Spacing Scale
- **XS**: 4px - Element padding, borders
- **SM**: 8px - Tight groupings  
- **MD**: 16px - Standard spacing
- **LG**: 24px - Section spacing
- **XL**: 32px - Page margins
- **XXL**: 48px - Major sections
- **XXXL**: 64px - Page sections

### Grid System
- **Base unit**: 8px grid for consistent alignment
- **Breakpoints**: 
  - SM: 600px (tablets)
  - MD: 960px (small desktops) 
  - LG: 1280px (large desktops)
  - XL: 1920px (wide screens)

### Layout Patterns
```python
# Card layout with proper spacing
card = style_manager.create_frame(parent, variant='card')
card.pack(fill='x', padx=16, pady=8)  # MD spacing

# Content within card
content = tk.Frame(card)
content.pack(fill='both', expand=True, padx=24, pady=16)  # LG padding
```

## Components

### Buttons

#### Primary Button
- **Use**: Main actions, form submissions
- **Style**: Filled with primary color
- **Animation**: Ripple effect, elevation on hover

```python
primary_btn = style_manager.create_button(
    parent, "Search Images", variant='primary'
)
```

#### Secondary Button
- **Use**: Secondary actions
- **Style**: Outlined or filled with secondary color
- **Animation**: Subtle hover state

#### Text Button
- **Use**: Low-emphasis actions, links
- **Style**: Text-only with hover background
- **Animation**: Background fade on hover

### Input Fields

#### Standard Entry
- **Border**: 1px solid outline color
- **Focus**: Primary color border, slight glow
- **Padding**: 12px horizontal, 8px vertical
- **Font**: Body Medium

#### Search Bar
- **Enhanced**: With icon, autocomplete dropdown
- **Border Radius**: 8px for modern appearance
- **Shadow**: Subtle elevation when focused

### Cards

#### Standard Card
- **Background**: Surface color
- **Border**: 1px solid outline variant
- **Border Radius**: 12px
- **Padding**: 24px
- **Shadow**: Level 1 elevation

#### Interactive Card
- **Hover**: Slight elevation increase
- **Click**: Ripple animation
- **Selection**: Primary color border

### Navigation

#### Search Controls
- **Layout**: Horizontal toolbar
- **Spacing**: 16px between elements
- **Height**: 56px minimum for touch targets

#### Filter Panel
- **Appearance**: Collapsible panel
- **Animation**: Slide down/up transition
- **Background**: Surface variant color

## Interaction States

### Hover States
- **Buttons**: Background color change + elevation
- **Cards**: Shadow increase + border highlight
- **Interactive elements**: Cursor change + visual feedback

### Focus States
- **Keyboard navigation**: Visible focus ring
- **Color**: Primary color outline
- **Width**: 2px outline with 4px offset

### Loading States
- **Buttons**: Spinner replaces text
- **Content**: Skeleton loaders
- **Full screen**: Modal overlay with spinner

### Error States
- **Form fields**: Red border + error text
- **Toast notifications**: Error color background
- **Icons**: Error symbols with semantic color

## Animations & Transitions

### Timing Functions
```python
# Available easing functions
EASE_OUT = "ease_out"          # Default for most UI
EASE_IN_OUT = "ease_in_out"    # Modal transitions
BOUNCE_OUT = "bounce_out"       # Playful interactions
ELASTIC_OUT = "elastic_out"     # Attention-getting
```

### Duration Scale
- **Fast**: 200ms - Hover effects, toggles
- **Medium**: 300ms - Modal enter/exit
- **Slow**: 500ms - Page transitions
- **Extra Slow**: 1000ms - Loading animations

### Animation Patterns

#### Page Transitions
```python
# Fade in new content
style_manager.animate_widget(
    new_content, 'fade_in', duration=0.3, easing=Easing.EASE_OUT
)
```

#### Micro-interactions
```python
# Button press feedback
style_manager.animate_widget(
    button, 'pulse', scale=1.02, duration=0.15
)
```

#### Loading States
```python
# Skeleton shimmer
skeleton.start_animation()
```

## Responsive Design

### Breakpoint Behavior

#### Small (< 600px)
- Single column layout
- Reduced padding/margins
- Simplified navigation
- Touch-optimized controls

#### Medium (600px - 960px)
- Two column layout where appropriate
- Standard spacing
- Full feature set

#### Large (> 960px)
- Multi-column layouts
- Generous spacing
- Advanced interactions
- Keyboard shortcuts

### Implementation
```python
# Responsive breakpoints
style_manager.add_breakpoint('mobile', 0, 599)
style_manager.add_breakpoint('tablet', 600, 959)
style_manager.add_breakpoint('desktop', 960, float('inf'))
```

## Accessibility

### Color Contrast
- **Normal text**: 4.5:1 minimum contrast ratio
- **Large text**: 3:1 minimum contrast ratio
- **UI components**: 3:1 minimum contrast ratio

### Keyboard Navigation
- **Tab order**: Logical flow through interface
- **Focus indicators**: Clear visual feedback
- **Shortcuts**: Common operations accessible via keyboard

### Screen Reader Support
- **Labels**: Descriptive text for all interactive elements
- **Roles**: Proper ARIA roles where applicable
- **State announcements**: Loading, error, success states

## Dark Theme

### Color Adaptations
- **Higher contrast**: Brighter colors on dark backgrounds
- **Reduced eye strain**: Slightly desaturated colors
- **Depth perception**: Lighter surfaces appear elevated

### Implementation
```python
# Theme switching
theme = MaterialTheme('dark')
style_manager.set_theme(theme)
```

## Usage Examples

### Creating a Modern Search Interface
```python
# Advanced search bar with Material Design
search_bar = AdvancedSearchBar(
    parent, style_manager, data_dir,
    on_search=handle_search,
    on_clear=handle_clear
)

# Image gallery with smooth interactions
gallery = ImageGallery(
    parent, style_manager,
    on_image_select=handle_select,
    on_view_change=handle_view_change
)

# Progress dashboard with data visualization
dashboard = VocabularyDashboard(
    parent, style_manager, data_dir,
    on_export=handle_export
)
```

### Styling Custom Components
```python
# Register custom widget with classes
style_manager.register_widget(
    custom_widget, 
    widget_id="my_component",
    classes=['frame', 'custom', 'highlighted']
)

# Add hover effects
style_manager.set_state(widget, 'hover')  # On mouse enter
style_manager.clear_state(widget)         # On mouse leave
```

### Custom Animations
```python
# Slide in from left
style_manager.animate_widget(
    panel, 'slide_in', 
    direction='left', 
    duration=0.4,
    easing=Easing.EASE_OUT_CUBIC
)

# Custom property animation
style_manager.animation_manager.animate_property(
    widget, 'width', 100, 200, 
    duration=0.3, 
    easing=Easing.EASE_IN_OUT
)
```

## Best Practices

### Do's ✅
- Use consistent spacing based on 8px grid
- Provide visual feedback for all interactions
- Maintain proper color contrast ratios
- Animate state changes smoothly
- Group related functionality visually
- Use semantic colors for status indicators

### Don'ts ❌
- Mix different corner radius values randomly
- Use more than 3 font weights in one interface  
- Animate too many elements simultaneously
- Use colors that fail accessibility standards
- Create inconsistent hover states
- Ignore keyboard navigation requirements

### Performance Tips
- Limit simultaneous animations to 2-3 elements
- Use efficient easing functions (avoid complex calculations)
- Implement virtualization for large lists
- Cache styled components when possible
- Defer heavy animations until user interaction

## Component Catalog

### Form Elements
- ✅ Enhanced Entry Fields
- ✅ Advanced Search Bar  
- ✅ Filter Dropdowns
- ✅ Progress Indicators
- ✅ Loading States

### Data Display
- ✅ Image Gallery (Grid/List views)
- ✅ Vocabulary Dashboard
- ✅ Progress Charts
- ✅ Statistics Cards
- ✅ Category Breakdowns

### Navigation & Layout
- ✅ Responsive Containers
- ✅ Card Layouts
- ✅ Modal Overlays
- ✅ Collapsible Panels

### Feedback & Status
- ✅ Loading Spinners
- ✅ Progress Rings
- ✅ Toast Notifications (via system)
- ✅ Error States
- ✅ Success Indicators

## Browser Support

### Tkinter Limitations
- No true transparency (simulated with color blending)
- Limited shadow support (using borders)
- Canvas-based custom components for advanced effects
- Platform-specific font rendering differences

### Fallbacks
- Graceful degradation for unsupported features
- Platform-appropriate fonts and spacing
- Consistent behavior across Windows versions

---

## Conclusion

This style guide provides the foundation for creating modern, accessible interfaces within the constraints of Tkinter. By following these guidelines, developers can build cohesive user experiences that feel native to modern design standards while maintaining the reliability and performance of desktop applications.

The implementation prioritizes practical usage over pixel-perfect Material Design compliance, ensuring that the end result is both visually appealing and functionally robust for desktop users.