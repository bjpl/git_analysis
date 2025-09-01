# VocabLens UI Component Specifications

## Overview
This document contains the specifications for all VocabLens UI components, designed with modern UX principles, responsive layouts, and full dark mode support.

## Core Components

### 1. SearchBar Component
**Location**: `src/components/ImageSearch/SearchBar.tsx`

**Features**:
- Auto-complete with debounced search (300ms delay)
- Keyboard navigation (Arrow keys, Enter, Escape)
- Search suggestions dropdown
- Clear search functionality
- Loading states with spinner
- Accessibility support (ARIA labels, roles)
- Responsive design for mobile/desktop
- Dark mode compatible

**Props**:
```typescript
interface SearchBarProps {
  onSearch: (query: string) => void;
  isLoading?: boolean;
  suggestions?: string[];
  placeholder?: string;
}
```

**Usage**:
```jsx
<SearchBar
  onSearch={handleSearch}
  isLoading={isSearching}
  suggestions={searchSuggestions}
  placeholder="Search for images..."
/>
```

### 2. ImageCard Component
**Location**: `src/components/ImageSearch/ImageCard.tsx`

**Features**:
- Lazy image loading with error handling
- Hover overlay with actions (View, Generate Description, Download)
- Like/favorite functionality with toast notifications
- User attribution display
- Image metadata (dimensions, tags)
- Loading skeleton states
- Keyboard accessibility
- Download tracking integration
- Responsive hover effects

**Props**:
```typescript
interface ImageCardProps {
  image: Image;
  onSelect: (image: Image) => void;
  onGenerateDescription: (image: Image) => void;
  isSelected?: boolean;
  showActions?: boolean;
}
```

### 3. ImageGrid Component
**Location**: `src/components/ImageSearch/ImageGrid.tsx`

**Features**:
- Virtualized grid using react-window for performance
- Responsive column calculation (1-4 columns)
- Multiple aspect ratio support (square, portrait, landscape, auto)
- Keyboard navigation with arrow keys
- Loading states and empty states
- Configurable grid gap and minimum column width
- Accessibility with ARIA grid role
- Smooth scrolling with custom scrollbars

**Props**:
```typescript
interface ImageGridProps {
  images: Image[];
  isLoading?: boolean;
  onImageSelect: (image: Image) => void;
  onGenerateDescription: (image: Image) => void;
  selectedImageId?: string;
  className?: string;
  showActions?: boolean;
  gridGap?: number;
  minColumnWidth?: number;
  maxColumns?: number;
  aspectRatio?: 'square' | 'portrait' | 'landscape' | 'auto';
}
```

### 4. SearchResults Component (Enhanced)
**Location**: `src/components/ImageSearch/SearchResults.tsx`

**Features**:
- Infinite scrolling with react-window-infinite-loader
- Responsive grid layout
- Loading more indicator
- Results count display
- Empty state handling
- Performance optimized with virtualization

### 5. LoadingSpinner Component
**Location**: `src/components/Shared/LoadingStates/LoadingSpinner.tsx`

**Features**:
- Multiple sizes (xs, sm, md, lg, xl)
- Multiple variants (primary, secondary, white, gray)
- Full-screen loading option
- Pre-configured variants for common use cases
- Accessibility with proper ARIA labels
- Dark mode compatible

**Props**:
```typescript
interface LoadingSpinnerProps {
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  variant?: 'primary' | 'secondary' | 'white' | 'gray';
  className?: string;
  label?: string;
  fullScreen?: boolean;
}
```

**Pre-configured Variants**:
- `PrimarySpinner`
- `SecondarySpinner`
- `WhiteSpinner`
- `GraySpinner`
- `ButtonSpinner`
- `CardSpinner`
- `FullPageSpinner`

### 6. LoadingSkeleton Component (Enhanced)
**Location**: `src/components/Shared/LoadingStates/LoadingSkeleton.tsx`

**Features**:
- Multiple variants (rectangular, circular, text, card, image, avatar)
- Multi-line text support
- Pre-configured skeletons (CardSkeleton, ImageCardSkeleton, ListItemSkeleton)
- PageLoading component for full-page states
- Smooth animations with CSS

## Design System Integration

### Responsive Design
- **Mobile First**: Components designed for mobile-first approach
- **Breakpoints**: xs (475px), mobile (max 767px), tablet (768-1023px), desktop (1024px+)
- **Flexible Grid**: 1-4 columns based on screen size
- **Touch-Friendly**: 44px minimum touch targets

### Dark Mode Support
- **CSS Variables**: Uses CSS custom properties for colors
- **Automatic Detection**: Respects system dark mode preference
- **Toggle Support**: Can be overridden by user preference
- **Consistent Colors**: All components support both light and dark themes

### Color Palette
```css
/* Light Mode */
--color-background: 255 255 255;
--color-foreground: 0 0 0;
--color-primary: 99 102 241;

/* Dark Mode */
--color-background: 17 24 39;
--color-foreground: 249 250 251;
--color-primary: 129 140 248;
```

### Animation System
- **Tailwind Animations**: fade-in, slide-up, slide-down, scale-in
- **Custom Animations**: bounce-gentle, pulse-slow, shimmer
- **Performance**: Hardware-accelerated transforms
- **Reduced Motion**: Respects `prefers-reduced-motion`

## Accessibility Features

### Keyboard Navigation
- Tab order optimization
- Arrow key navigation in grids
- Enter/Space for actions
- Escape to close overlays

### Screen Reader Support
- Proper ARIA labels and roles
- Alt text for all images
- Loading state announcements
- Error message association

### Focus Management
- Visible focus indicators
- Focus trapping in modals
- Skip links for navigation
- Logical tab order

## Performance Optimizations

### React Performance
- `React.memo` for expensive components
- `useMemo` for calculated values
- `useCallback` for event handlers
- Virtualization for large lists

### Image Optimization
- Lazy loading with Intersection Observer
- Progressive loading (thumb → small → full)
- Error handling with fallbacks
- WebP format support

### Bundle Optimization
- Tree-shaking compatible exports
- Dynamic imports for heavy components
- Minimal external dependencies
- CSS purging in production

## Testing Strategy

### Unit Tests
- Component rendering
- Props validation
- Event handling
- Accessibility compliance

### Integration Tests
- User interactions
- Keyboard navigation
- Loading states
- Error scenarios

### Visual Regression Tests
- Cross-browser compatibility
- Responsive layouts
- Dark mode variants
- Animation states

## Usage Examples

### Basic Image Search Interface
```jsx
import { SearchBar, ImageGrid } from '../components/ImageSearch';
import { LoadingSpinner } from '../components/Shared/LoadingStates/LoadingSpinner';

function SearchPage() {
  const [images, setImages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedImageId, setSelectedImageId] = useState();

  return (
    <div className="container mx-auto px-4 py-8">
      <SearchBar
        onSearch={handleSearch}
        isLoading={isLoading}
        suggestions={searchSuggestions}
      />
      
      {isLoading && images.length === 0 ? (
        <LoadingSpinner fullScreen label="Searching images..." />
      ) : (
        <ImageGrid
          images={images}
          isLoading={isLoading}
          onImageSelect={setSelectedImageId}
          onGenerateDescription={handleGenerateDescription}
          selectedImageId={selectedImageId}
          className="mt-8"
        />
      )}
    </div>
  );
}
```

### Responsive Grid with Custom Configuration
```jsx
<ImageGrid
  images={images}
  onImageSelect={handleSelect}
  onGenerateDescription={handleGenerate}
  aspectRatio="landscape"
  minColumnWidth={320}
  maxColumns={3}
  gridGap={20}
  showActions={true}
/>
```

### Loading States Pattern
```jsx
// Button loading state
<Button disabled={isLoading}>
  {isLoading ? <ButtonSpinner /> : 'Generate Description'}
</Button>

// Card loading state
{isLoading ? (
  <CardSpinner />
) : (
  <ImageCard image={image} {...props} />
)}

// Full page loading
{isInitialLoading && (
  <FullPageSpinner label="Loading VocabLens..." />
)}
```

## Component Coordination

All components are designed to work together seamlessly:

1. **Search Flow**: SearchBar → ImageGrid → ImageCard
2. **Loading States**: Consistent across all components
3. **Theme Support**: Unified dark mode implementation
4. **Keyboard Navigation**: Coordinated focus management
5. **Responsive Design**: Consistent breakpoints and spacing

## Memory Storage for Agent Coordination

Component specifications have been stored in memory with the following keys:
- `swarm/ui-components/search-bar`
- `swarm/ui-components/image-card`
- `swarm/ui-components/image-grid`
- `swarm/ui-components/loading-spinner`
- `swarm/ui-components/loading-skeleton`

This allows other agents to reference and build upon these implementations.