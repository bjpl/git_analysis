# VocabLens Design System

## Overview

The VocabLens Design System provides a comprehensive, accessible, and consistent UI/UX foundation for the vocabulary learning PWA. Built with React, TypeScript, and Tailwind CSS, it emphasizes accessibility, responsive design, and smooth user interactions.

## Core Principles

### 1. Accessibility First
- WCAG 2.1 AA compliance
- Screen reader support
- Keyboard navigation
- Focus management
- Color contrast compliance

### 2. Responsive Design
- Mobile-first approach
- Fluid typography and spacing
- Touch-friendly interfaces
- Progressive enhancement

### 3. Performance
- CSS variables for theming
- Optimized animations
- Lazy loading patterns
- Minimal bundle impact

### 4. Consistency
- Unified design tokens
- Systematic component library
- Predictable interactions
- Coherent visual language

## Design Tokens

### Colors

The color system is built with CSS variables that adapt to light and dark themes:

```css
/* Light Theme */
--color-background: 255 255 255;
--color-foreground: 15 23 42;
--color-primary: 79 70 229;
--color-success: 34 197 94;
--color-warning: 245 158 11;
--color-error: 239 68 68;

/* Dark Theme */
--color-background: 2 6 23;
--color-foreground: 248 250 252;
--color-primary: 129 140 248;
```

### Typography

Typography scale follows a modular approach:

```css
--text-xs: 0.75rem;     /* 12px */
--text-sm: 0.875rem;    /* 14px */
--text-base: 1rem;      /* 16px */
--text-lg: 1.125rem;    /* 18px */
--text-xl: 1.25rem;     /* 20px */
--text-2xl: 1.5rem;     /* 24px */
--text-3xl: 1.875rem;   /* 30px */
--text-4xl: 2.25rem;    /* 36px */
```

### Spacing

Consistent spacing system:

```css
--spacing-xs: 0.25rem;  /* 4px */
--spacing-sm: 0.5rem;   /* 8px */
--spacing-md: 1rem;     /* 16px */
--spacing-lg: 1.5rem;   /* 24px */
--spacing-xl: 2rem;     /* 32px */
```

### Transitions

Standardized animation durations:

```css
--transition-fast: 150ms;
--transition-normal: 300ms;
--transition-slow: 500ms;
```

## Component Library

### Core Components

#### Button
Accessible button with multiple variants and states:

```tsx
import { Button } from '@/components/Shared/Button/Button';

<Button variant="primary" size="md" loading={isLoading}>
  Save Changes
</Button>
```

**Variants:** `primary`, `secondary`, `outline`, `ghost`, `danger`, `success`
**Sizes:** `sm`, `md`, `lg`, `icon`

#### Input
Form input with validation support:

```tsx
import { AccessibleField, AccessibleInput } from '@/components/Shared/Accessibility/AccessibilityComponents';

<AccessibleField
  id="email"
  label="Email Address"
  description="We'll never share your email"
  error={emailError}
  required
>
  <AccessibleInput
    type="email"
    placeholder="Enter your email"
    error={emailError}
  />
</AccessibleField>
```

#### Modal
Accessible modal with focus management:

```tsx
import { Modal } from '@/components/Shared/Modal/Modal';

<Modal
  isOpen={isOpen}
  onClose={onClose}
  title="Confirm Action"
  description="This action cannot be undone"
  size="md"
>
  <p>Modal content goes here</p>
</Modal>
```

### Layout Components

#### AppShell
Main application layout with responsive navigation:

```tsx
import { AppShell } from '@/components/Layout/AppShell';
import { ThemeProvider } from '@/contexts/ThemeContext';
import { NotificationProvider } from '@/components/Shared/Notification/NotificationSystem';

<ThemeProvider>
  <NotificationProvider position="top-right">
    <AppShell>
      <YourPageContent />
    </AppShell>
  </NotificationProvider>
</ThemeProvider>
```

#### Header
Responsive header with search and navigation:

```tsx
import { Header } from '@/components/Layout/Header';

<Header 
  onMenuClick={toggleSidebar}
  showMenuButton={isMobile}
/>
```

### Feedback Components

#### Notifications
Toast notification system:

```tsx
import { useNotificationHelpers } from '@/components/Shared/Notification/NotificationSystem';

const { success, error, warning, info } = useNotificationHelpers();

// Usage
success("Success!", "Your changes have been saved");
error("Error!", "Something went wrong", { persistent: true });
```

#### Loading States
Various loading indicators:

```tsx
import { LoadingSpinner, LoadingSkeleton, PageLoading } from '@/components/Shared/LoadingStates/LoadingSkeleton';

// Spinner
<LoadingSpinner size="lg" variant="default" />

// Skeleton
<LoadingSkeleton variant="text" lines={3} />

// Page loading
<PageLoading message="Loading content..." />
```

#### Error Handling
Comprehensive error boundaries and displays:

```tsx
import { ErrorBoundary, NetworkError, ServerError } from '@/components/Shared/ErrorHandling/ErrorComponents';

// Error boundary
<ErrorBoundary onError={handleError}>
  <YourComponent />
</ErrorBoundary>

// Specific error types
<NetworkError onRetry={handleRetry} />
<ServerError message="Custom error message" />
```

### Accessibility Components

#### Screen Reader Support
```tsx
import { ScreenReaderOnly, LiveRegion } from '@/components/Shared/Accessibility/AccessibilityComponents';

<ScreenReaderOnly>
  Additional context for screen readers
</ScreenReaderOnly>

<LiveRegion politeness="polite">
  Dynamic content announcements
</LiveRegion>
```

#### Skip Links
```tsx
import { SkipLink } from '@/components/Shared/Accessibility/AccessibilityComponents';

<SkipLink href="#main-content">
  Skip to main content
</SkipLink>
```

## Theme System

### Theme Provider
Wrap your app with the theme provider:

```tsx
import { ThemeProvider, ThemeToggle } from '@/contexts/ThemeContext';

<ThemeProvider defaultTheme="system">
  <YourApp />
  <ThemeToggle showLabel size="md" />
</ThemeProvider>
```

### Using Themes
```tsx
import { useTheme, ThemeAware } from '@/contexts/ThemeContext';

const { theme, resolvedTheme, setTheme, toggleTheme } = useTheme();

// Conditional rendering based on theme
<ThemeAware
  light={<LightModeIcon />}
  dark={<DarkModeIcon />}
/>
```

## Responsive Design

### Breakpoints
Custom responsive breakpoints:

```css
/* Mobile first approach */
@media (min-width: 475px) { /* xs */ }
@media (min-width: 640px) { /* sm */ }
@media (min-width: 768px) { /* md */ }
@media (min-width: 1024px) { /* lg */ }
@media (min-width: 1280px) { /* xl */ }
@media (min-width: 1536px) { /* 2xl */ }

/* Custom breakpoints */
@media (max-width: 767px) { /* mobile */ }
@media (min-width: 768px) and (max-width: 1023px) { /* tablet */ }
@media (min-width: 1024px) { /* desktop */ }
```

### Responsive Utilities
```tsx
// Touch targets (minimum 44px)
<button className="touch-target">
  Mobile-friendly button
</button>

// Safe area insets for iOS
<div className="safe-area-inset">
  Content respects device notches
</div>
```

## Animations

### CSS Animations
Built-in animation classes:

```css
.animate-fade-in      /* Fade in effect */
.animate-slide-up     /* Slide up from bottom */
.animate-slide-down   /* Slide down from top */
.animate-scale-in     /* Scale from 95% to 100% */
.animate-bounce-gentle /* Gentle bounce effect */
.animate-shimmer      /* Loading shimmer effect */
```

### Reduced Motion
Respects user preferences:

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

## Accessibility Features

### Focus Management
- Visible focus indicators
- Focus trapping in modals
- Focus restoration
- Skip links for keyboard navigation

### Screen Reader Support
- Semantic HTML structure
- ARIA labels and roles
- Live regions for dynamic content
- Screen reader only content

### Color and Contrast
- WCAG AA compliant color ratios
- High contrast mode support
- Color-blind friendly palette
- System preference detection

### Keyboard Navigation
- Full keyboard accessibility
- Logical tab order
- Keyboard shortcuts
- Arrow key navigation for complex components

## Usage Examples

### Basic Page Layout
```tsx
import React from 'react';
import { ThemeProvider } from '@/contexts/ThemeContext';
import { NotificationProvider } from '@/components/Shared/Notification/NotificationSystem';
import { ErrorBoundary } from '@/components/Shared/ErrorHandling/ErrorComponents';
import { AppShell } from '@/components/Layout/AppShell';

function MyPage() {
  return (
    <ThemeProvider>
      <NotificationProvider>
        <ErrorBoundary>
          <AppShell>
            <main className="container mx-auto px-4 py-8">
              <h1 className="text-3xl font-bold text-foreground mb-6">
                My Page
              </h1>
              {/* Page content */}
            </main>
          </AppShell>
        </ErrorBoundary>
      </NotificationProvider>
    </ThemeProvider>
  );
}
```

### Form with Validation
```tsx
import { AccessibleField, AccessibleInput } from '@/components/Shared/Accessibility/AccessibilityComponents';
import { Button } from '@/components/Shared/Button/Button';
import { useNotificationHelpers } from '@/components/Shared/Notification/NotificationSystem';

function MyForm() {
  const { success, error } = useNotificationHelpers();
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      await submitForm();
      success("Success!", "Form submitted successfully");
    } catch (err) {
      error("Error!", "Failed to submit form");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <AccessibleField
        id="name"
        label="Full Name"
        required
      >
        <AccessibleInput
          type="text"
          placeholder="Enter your name"
        />
      </AccessibleField>
      
      <Button 
        type="submit" 
        loading={isLoading}
        className="w-full"
      >
        Submit
      </Button>
    </form>
  );
}
```

## Best Practices

### 1. Use Semantic HTML
Always use appropriate HTML elements for their intended purpose.

### 2. Provide Alt Text
Include descriptive alt text for all images and icons.

### 3. Maintain Focus Order
Ensure logical tab order and proper focus management.

### 4. Test with Screen Readers
Regularly test with screen reader software.

### 5. Respect User Preferences
Honor system preferences for motion, contrast, and themes.

### 6. Mobile First
Design and develop for mobile devices first.

### 7. Performance
Keep bundle sizes small and optimize for Core Web Vitals.

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Resources

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [MDN Accessibility](https://developer.mozilla.org/en-US/docs/Web/Accessibility)
- [React Accessibility](https://reactjs.org/docs/accessibility.html)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)