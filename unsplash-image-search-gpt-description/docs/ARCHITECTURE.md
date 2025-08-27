# VocabLens PWA - Component Architecture

## Overview

VocabLens is a Progressive Web Application built with React 18, TypeScript, and modern web technologies. It provides an immersive vocabulary learning experience through AI-powered image descriptions.

## Architecture Principles

- **Component-First Design**: Modular, reusable components with single responsibilities
- **TypeScript Strict Mode**: Full type safety and excellent developer experience
- **Performance Optimized**: Virtual scrolling, lazy loading, and code splitting
- **Offline Capable**: Service worker with intelligent caching and offline queue
- **Accessible**: WCAG 2.1 AA compliant with comprehensive ARIA support
- **Responsive**: Mobile-first design with adaptive layouts

## Technology Stack

### Core
- **React 18.2+** with concurrent features
- **TypeScript 5.2+** with strict mode
- **Vite 4.5+** for fast development and optimized builds
- **Tailwind CSS 3.3+** for utility-first styling

### State Management
- **Zustand 4.4+** for global state management
- **TanStack Query 5.8+** for server state and caching
- **React Router 6.17+** for client-side routing

### UI Components
- **Heroicons 2.0+** for consistent iconography
- **React Hot Toast** for notifications
- **React Window** for virtualization
- **CVA (Class Variance Authority)** for component variants

### Backend Integration
- **Supabase** for authentication and database
- **Unsplash API** for image search
- **OpenAI API** for AI-generated descriptions

### PWA Features
- **Vite PWA Plugin** for service worker generation
- **Workbox** for advanced caching strategies
- **Web App Manifest** for installability

## Directory Structure

```
src/
├── components/           # React components organized by feature
│   ├── Layout/          # App shell and navigation
│   ├── ImageSearch/     # Image search and display
│   ├── DescriptionGenerator/ # AI description generation
│   ├── VocabularyManager/   # Vocabulary CRUD operations
│   ├── QuizSystem/      # Interactive quiz components
│   ├── PWAPrompt/       # Install and update prompts
│   └── Shared/          # Reusable UI components
├── hooks/               # Custom React hooks
├── stores/              # Zustand store definitions
├── types/               # TypeScript type definitions
├── utils/               # Utility functions and helpers
└── App.tsx             # Root application component
```

## Component Categories

### 1. Layout Components
- **App.tsx**: Root component with providers and routing
- **Layout.tsx**: Main app shell with navigation and theme switching
- **Header.tsx**: Top navigation with user menu
- **Sidebar.tsx**: Collapsible sidebar for additional navigation

### 2. Feature Components

#### ImageSearch
- **SearchBar.tsx**: Intelligent search with autocomplete
- **SearchResults.tsx**: Virtualized grid with infinite scrolling  
- **ImageCard.tsx**: Individual image with actions and metadata
- **ImageModal.tsx**: Full-screen image viewer with keyboard navigation

#### DescriptionGenerator
- **DescriptionPanel.tsx**: Main container with style selection
- **StreamingText.tsx**: Real-time text streaming with cursor animation
- **StyleSelector.tsx**: Academic/Poetic/Technical style options
- **VocabularyHighlighter.tsx**: Interactive word highlighting and tooltips

#### VocabularyManager
- **VocabularyList.tsx**: Filterable, sortable word list with statistics
- **VocabularyItem.tsx**: Individual word card with inline editing
- **ExportDialog.tsx**: CSV and Anki export functionality
- **ClickableWord.tsx**: Translatable word component

### 3. Shared Components

#### UI Primitives
- **Button.tsx**: CVA-powered button with multiple variants
- **LoadingSkeleton.tsx**: Animated loading placeholders
- **EmptyState.tsx**: Friendly empty state illustrations
- **ErrorBoundary.tsx**: Graceful error handling with recovery

#### Layout Helpers  
- **Toast.tsx**: Consistent notification system
- **OfflineIndicator.tsx**: Network status and sync queue display
- **PWAPrompt.tsx**: Install and update notifications

## State Management Architecture

### Global State (Zustand)
```typescript
// appStore.ts - Application-wide settings
interface AppState {
  user: User | null
  theme: 'light' | 'dark' | 'system'
  isOnline: boolean
  settings: UserSettings
}

// imageSearchStore.ts - Search state
interface ImageSearchState {
  query: string
  results: Image[]
  selectedImage: Image | null
  filters: SearchFilters
}

// vocabularyStore.ts - Vocabulary management
interface VocabularyState {
  words: VocabularyWord[]
  filters: VocabularyFilters
  sortBy: SortOption
}
```

### Server State (TanStack Query)
- **Image API**: Unsplash search with infinite queries and image caching
- **Vocabulary API**: Supabase CRUD operations with optimistic updates
- **AI API**: Streaming description generation with SSE
- **Quiz API**: Real-time multiplayer quiz sessions

## Custom Hooks Architecture

### Core Hooks
- **useSupabase**: Authentication and database client
- **useImageSearch**: Infinite scroll image search with caching
- **useAIGeneration**: Streaming AI description generation  
- **useVocabulary**: Full CRUD vocabulary management
- **useOfflineSync**: Offline queue management and synchronization

### Utility Hooks
- **useDebounce**: Input debouncing for search optimization
- **useWindowSize**: Responsive layout calculations
- **useLocalStorage**: Persistent client state
- **useIntersectionObserver**: Infinite scroll and lazy loading

## Performance Optimizations

### Code Splitting
```typescript
// Lazy load major route components
const ImageSearchPage = lazy(() => import('./pages/ImageSearchPage'))
const VocabularyPage = lazy(() => import('./pages/VocabularyPage'))
const QuizPage = lazy(() => import('./pages/QuizPage'))

// Manual chunk splitting in vite.config.ts
manualChunks: {
  'react-vendor': ['react', 'react-dom'],
  'router-vendor': ['react-router-dom'],
  'query-vendor': ['@tanstack/react-query'],
  'ui-vendor': ['@heroicons/react', 'react-hot-toast']
}
```

### Virtualization
```typescript
// Virtual scrolling for large image lists
<FixedSizeGrid
  columnCount={columnsPerRow}
  columnWidth={columnWidth}
  height={containerHeight}
  rowCount={rowCount}
  rowHeight={rowHeight}
  itemData={gridData}
>
  {GridItem}
</FixedSizeGrid>
```

### Memoization
```typescript
// Expensive computations cached with useMemo
const sortedWords = useMemo(() => {
  return words.sort((a, b) => /* sort logic */)
}, [words, sortBy, sortOrder])

// Component memoization for stable props
export const ImageCard = memo<ImageCardProps>(({ image, onSelect }) => {
  // Component implementation
})
```

## Accessibility Features

### Keyboard Navigation
- Full keyboard support for all interactive elements
- Focus management with trapped focus in modals
- Skip links for screen reader users
- Logical tab order throughout the application

### Screen Reader Support
- Comprehensive ARIA labels and descriptions
- Live regions for dynamic content updates
- Proper heading hierarchy (h1-h6)
- Alternative text for all images

### Color and Contrast
- WCAG AA contrast ratios (4.5:1 minimum)
- Color-blind friendly palette
- Focus indicators visible at all zoom levels
- Dark mode support with automatic system detection

## PWA Capabilities

### Installation
- Web App Manifest for Add to Home Screen
- Install prompt with user-friendly messaging  
- Standalone display mode for app-like experience
- Custom icon set for different platforms

### Offline Functionality
- Service Worker with Workbox for intelligent caching
- Background sync for vocabulary and quiz data
- Offline queue for user actions
- Graceful degradation when offline

### Caching Strategies
```typescript
// Image caching with expiration
{
  urlPattern: /^https:\/\/images\.unsplash\.com\/.*/i,
  handler: 'CacheFirst',
  options: {
    cacheName: 'unsplash-images-cache',
    expiration: {
      maxEntries: 200,
      maxAgeSeconds: 60 * 60 * 24 * 30 // 30 days
    }
  }
}
```

## Testing Strategy

### Unit Testing
- **Vitest** for fast unit test execution
- **React Testing Library** for component testing
- **MSW** for API mocking
- Coverage threshold: 80%+ for critical paths

### Integration Testing
- Full user workflows tested end-to-end
- Database integration tests with Supabase
- API integration tests with proper mocking
- Cross-browser compatibility testing

### Accessibility Testing
- **axe-core** for automated a11y testing
- Manual testing with screen readers
- Keyboard navigation testing
- Color contrast validation

## Development Workflow

### Code Quality
```json
// package.json scripts
{
  "lint": "eslint src --ext ts,tsx",
  "type-check": "tsc --noEmit", 
  "format": "prettier --write \"src/**/*.{ts,tsx}\"",
  "test": "vitest",
  "test:coverage": "vitest --coverage"
}
```

### Git Hooks
- **Husky** for pre-commit hooks
- **lint-staged** for staged file linting
- Automated type checking before push
- Commit message linting with conventional commits

### CI/CD Pipeline
- Automated testing on PR creation
- Build verification and bundle analysis
- Lighthouse CI for performance monitoring
- Automated deployment to staging environment

## Security Considerations

### API Security
- Environment variable validation
- API key rotation strategy
- Rate limiting and error handling
- CORS configuration for production

### Data Protection
- Client-side input validation
- XSS prevention with proper escaping
- Secure storage of sensitive data
- GDPR compliance for user data

## Browser Support

### Target Browsers
- Chrome 88+ (90%+ of users)
- Firefox 85+ 
- Safari 14+
- Edge 88+

### Progressive Enhancement
- Core functionality works without JavaScript
- Enhanced features for modern browsers
- Graceful fallbacks for older browsers
- Mobile-first responsive design

## Future Enhancements

### Planned Features
- Real-time multiplayer quiz system
- Advanced spaced repetition algorithm
- Social features and word sharing
- Voice recognition for pronunciation
- Augmented reality word overlay

### Performance Roadmap
- HTTP/3 and Server Push optimization
- WebAssembly for intensive computations
- Edge computing for global performance
- Advanced caching with Cloudflare

This architecture provides a solid foundation for a scalable, maintainable, and performant vocabulary learning application that delivers an exceptional user experience across all devices and network conditions.