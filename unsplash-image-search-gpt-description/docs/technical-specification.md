# Technical Specification
## Hybrid PWA Migration Strategy

## Executive Summary

This technical specification outlines the complete migration strategy from the current Tkinter desktop application to a modern hybrid Progressive Web App (PWA) architecture. The solution provides 95% code reuse across web, desktop, and mobile platforms while maintaining feature parity and improving user experience.

## Architecture Decision Records (ADRs)

### ADR-001: Frontend Framework Selection

**Decision**: React with TypeScript  
**Status**: Approved  
**Date**: 2024-08-26

**Context**:
- Need cross-platform UI framework with strong ecosystem
- Requirement for PWA compatibility and offline capabilities
- Team familiarity and long-term maintenance considerations

**Decision**:
We will use React 18+ with TypeScript for the following reasons:

**Pros**:
- Largest ecosystem and community support
- Excellent PWA support through Create React App and Vite
- Strong TypeScript integration for type safety
- Concurrent features for better performance
- Extensive component libraries (Mantine, Ant Design)
- Easy integration with Tauri and Capacitor

**Cons**:
- Larger bundle size than lighter alternatives
- Learning curve for team members unfamiliar with React

**Alternatives Considered**:
- Vue.js: Smaller but less ecosystem support
- Svelte: Smallest bundle but limited component libraries
- Vanilla JS: Maximum performance but high development cost

### ADR-002: Desktop Wrapper Technology

**Decision**: Tauri (Rust-based)  
**Status**: Approved  
**Date**: 2024-08-26

**Context**:
- Need native desktop integration while maintaining web codebase
- Performance and security requirements
- Bundle size and memory usage considerations

**Decision**:
We will use Tauri instead of Electron for desktop wrapping.

**Pros**:
- 10x smaller bundle size (~10MB vs ~100MB)
- Better security model with permission-based system APIs
- Lower memory usage (~30MB vs ~100MB)
- Built-in auto-updater
- Rust backend enables WebAssembly integration
- System tray and native menu support

**Cons**:
- Newer technology with smaller ecosystem
- Requires Rust knowledge for advanced features
- Less mature than Electron

**Alternatives Considered**:
- Electron: Mature but resource-heavy
- Neutralino: Lightweight but limited features
- Flutter Desktop: Different paradigm, would require complete rewrite

### ADR-003: Data Storage Strategy

**Decision**: Local-First with IndexedDB + Optional Cloud Sync  
**Status**: Approved  
**Date**: 2024-08-26

**Context**:
- Offline-first requirements
- User privacy and data ownership
- Cross-device synchronization needs

**Decision**:
Primary data storage in browser's IndexedDB with optional cloud synchronization.

**Implementation**:
```typescript
interface DataStrategy {
  primary: 'IndexedDB',
  cloudSync: 'optional',
  conflictResolution: 'last-write-wins',
  encryption: 'client-side',
  backup: 'export-functionality'
}
```

**Benefits**:
- Works completely offline
- No vendor lock-in
- User owns their data
- GDPR compliant by design
- Fast local access

### ADR-004: Performance Critical Operations

**Decision**: WebAssembly (WASM) for Performance-Critical Operations  
**Status**: Approved  
**Date**: 2024-08-26

**Context**:
- Image processing and manipulation requirements
- Large dataset filtering and searching
- Text processing for vocabulary extraction

**Decision**:
Implement performance-critical operations in Rust, compiled to WebAssembly.

**Operations for WASM**:
- Image resizing and optimization
- Text parsing and vocabulary extraction
- Large data filtering and sorting
- Cryptographic operations (if needed)

## Detailed Technical Architecture

### Frontend Architecture

```typescript
// Application structure
src/
├── components/          # Reusable UI components
│   ├── common/         # Generic components
│   ├── image/          # Image-related components
│   └── vocabulary/     # Vocabulary components
├── features/           # Feature-specific modules
│   ├── image-search/   # Image search functionality
│   ├── ai-description/ # AI description generation
│   ├── vocabulary/     # Vocabulary management
│   └── quiz/          # Quiz system
├── services/          # API and business logic
│   ├── api/           # External API integrations
│   ├── storage/       # Data persistence
│   └── sync/          # Cloud synchronization
├── hooks/             # Custom React hooks
├── utils/             # Utility functions
└── types/            # TypeScript type definitions
```

### State Management

```typescript
// Using Zustand for lightweight state management
interface AppState {
  // UI State
  ui: {
    theme: 'light' | 'dark';
    language: 'en' | 'es';
    sidebarOpen: boolean;
    currentView: string;
  };
  
  // Application State
  imageSearch: {
    query: string;
    results: UnsplashImage[];
    selectedImage: UnsplashImage | null;
    loading: boolean;
  };
  
  // AI State
  ai: {
    description: string;
    generating: boolean;
    options: DescriptionOptions;
  };
  
  // Vocabulary State
  vocabulary: {
    words: VocabularyEntry[];
    currentQuiz: QuizSession | null;
    stats: LearningStats;
  };
  
  // User State
  user: {
    preferences: UserPreferences;
    apiKeys: ApiKeys;
    settings: AppSettings;
  };
}
```

### Service Layer Architecture

```typescript
// Service abstraction for cross-platform compatibility
abstract class BaseService {
  protected platform: 'web' | 'desktop' | 'mobile';
  
  constructor(platform: string) {
    this.platform = platform as any;
  }
  
  abstract initialize(): Promise<void>;
  abstract cleanup(): Promise<void>;
}

class ImageSearchService extends BaseService {
  private api: UnsplashAPI;
  private cache: CacheManager;
  
  async searchImages(query: string, options?: SearchOptions): Promise<SearchResult> {
    // Implementation with caching, error handling, and offline support
  }
}

class AIDescriptionService extends BaseService {
  private openai: OpenAI;
  private fallbacks: Array<AIProvider>;
  
  async generateDescription(image: string, options: DescriptionOptions): Promise<string> {
    // Implementation with streaming, fallbacks, and caching
  }
}

class VocabularyService extends BaseService {
  private storage: StorageManager;
  private translator: TranslationService;
  
  async addWord(word: string, translation: string, context: WordContext): Promise<void> {
    // Implementation with deduplication and smart learning
  }
}
```

### Performance Optimizations

#### 1. Code Splitting Strategy
```typescript
// Route-based code splitting
const ImageSearchPage = lazy(() => import('./pages/ImageSearch'));
const VocabularyPage = lazy(() => import('./pages/Vocabulary'));
const QuizPage = lazy(() => import('./pages/Quiz'));
const SettingsPage = lazy(() => import('./pages/Settings'));

// Component-based code splitting
const AIDescriptionModule = lazy(() => import('./features/ai-description'));
const AdvancedSearchModule = lazy(() => import('./features/advanced-search'));

// Service-based code splitting (loaded on demand)
const ExportService = lazy(() => import('./services/ExportService'));
const SyncService = lazy(() => import('./services/SyncService'));
```

#### 2. Virtual Scrolling Implementation
```typescript
// For large image result sets
import { useVirtualizer } from '@tanstack/react-virtual';

function ImageGrid({ images }: { images: UnsplashImage[] }) {
  const parentRef = useRef<HTMLDivElement>(null);
  
  const virtualizer = useVirtualizer({
    count: images.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 250, // Estimated height per item
    overscan: 5, // Render 5 items outside visible area
  });

  return (
    <div 
      ref={parentRef}
      className="image-grid-container"
      style={{ height: '600px', overflow: 'auto' }}
    >
      <div
        style={{
          height: `${virtualizer.getTotalSize()}px`,
          width: '100%',
          position: 'relative',
        }}
      >
        {virtualizer.getVirtualItems().map((virtualItem) => (
          <div
            key={virtualItem.key}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: `${virtualItem.size}px`,
              transform: `translateY(${virtualItem.start}px)`,
            }}
          >
            <ImageCard image={images[virtualItem.index]} />
          </div>
        ))}
      </div>
    </div>
  );
}
```

#### 3. WebAssembly Integration
```rust
// wasm-module/src/image_processing.rs
use wasm_bindgen::prelude::*;
use image::{ImageBuffer, Rgb};

#[wasm_bindgen]
pub struct ImageProcessor;

#[wasm_bindgen]
impl ImageProcessor {
    #[wasm_bindgen(constructor)]
    pub fn new() -> ImageProcessor {
        ImageProcessor
    }
    
    #[wasm_bindgen]
    pub fn resize_image(&self, data: &[u8], width: u32, height: u32) -> Vec<u8> {
        // Fast image resizing using Rust image crate
        let img = image::load_from_memory(data).unwrap();
        let resized = img.resize(width, height, image::imageops::FilterType::Lanczos3);
        
        let mut buffer = Vec::new();
        resized.write_to(&mut buffer, image::ImageOutputFormat::Jpeg(85)).unwrap();
        
        buffer
    }
    
    #[wasm_bindgen]
    pub fn optimize_for_web(&self, data: &[u8]) -> Vec<u8> {
        // Optimize images for web display
        // Reduce file size while maintaining visual quality
        let img = image::load_from_memory(data).unwrap();
        
        // Apply optimizations
        let optimized = img.resize(1200, 800, image::imageops::FilterType::Lanczos3);
        
        let mut buffer = Vec::new();
        optimized.write_to(&mut buffer, image::ImageOutputFormat::Jpeg(75)).unwrap();
        
        buffer
    }
}

// Text processing for vocabulary extraction
#[wasm_bindgen]
pub fn extract_vocabulary_fast(text: &str, language: &str) -> JsValue {
    // Fast text processing using Rust
    // This would be significantly faster than JavaScript for large texts
    
    let words = process_text_for_vocabulary(text, language);
    serde_wasm_bindgen::to_value(&words).unwrap()
}
```

### Data Migration Strategy

#### Phase 1: Export Current Data
```python
# migration/export_legacy_data.py
import json
import csv
from pathlib import Path
from datetime import datetime

def export_current_application_data():
    """Export all data from the current Tkinter application."""
    
    data_dir = Path('./data')
    export_data = {
        'version': '1.0.0',
        'exported_at': datetime.now().isoformat(),
        'vocabulary': export_vocabulary_data(),
        'settings': export_settings_data(),
        'session_history': export_session_data(),
        'user_preferences': export_user_preferences()
    }
    
    # Save to JSON for import into new system
    export_file = data_dir / 'legacy_export.json'
    with open(export_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    print(f"Data exported to: {export_file}")
    return export_data

def export_vocabulary_data():
    """Export vocabulary from CSV to structured format."""
    vocabulary = []
    csv_file = Path('./data/vocabulary.csv')
    
    if csv_file.exists():
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                vocabulary.append({
                    'spanish': row.get('Spanish', ''),
                    'english': row.get('English', ''),
                    'date_added': row.get('Date', ''),
                    'search_query': row.get('Search Query', ''),
                    'image_url': row.get('Image URL', ''),
                    'context': row.get('Context', ''),
                    'difficulty': 'intermediate',  # Default value
                    'learned': False,  # Default value
                    'review_count': 0,  # Default value
                    'last_reviewed': None  # Default value
                })
    
    return vocabulary

def export_settings_data():
    """Export application settings."""
    # This would read from your config files
    return {
        'api_keys_configured': True,  # Don't export actual keys
        'gpt_model': 'gpt-4o-mini',
        'theme': 'light',
        'language': 'en',
        'auto_save': True
    }

def export_session_data():
    """Export session history if available."""
    sessions = []
    log_file = Path('./data/session_log.json')
    
    if log_file.exists():
        with open(log_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            sessions = data.get('sessions', [])
    
    return sessions

def export_user_preferences():
    """Export UI preferences and customizations."""
    return {
        'window_size': {'width': 1100, 'height': 800},
        'zoom_level': 100,
        'description_style': 'academic',
        'vocabulary_level': 'intermediate',
        'auto_generate_quiz': True
    }

if __name__ == "__main__":
    export_current_application_data()
```

#### Phase 2: Import to New System
```typescript
// migration/import-legacy-data.ts
interface LegacyExportData {
  version: string;
  exported_at: string;
  vocabulary: LegacyVocabularyEntry[];
  settings: LegacySettings;
  session_history: LegacySession[];
  user_preferences: LegacyPreferences;
}

interface LegacyVocabularyEntry {
  spanish: string;
  english: string;
  date_added: string;
  search_query: string;
  image_url: string;
  context: string;
  difficulty: string;
  learned: boolean;
  review_count: number;
  last_reviewed: string | null;
}

export class LegacyDataImporter {
  private db: IDBDatabase;
  
  constructor(database: IDBDatabase) {
    this.db = database;
  }
  
  async importLegacyData(exportData: LegacyExportData): Promise<ImportResult> {
    const results: ImportResult = {
      vocabulary: { imported: 0, skipped: 0, errors: 0 },
      settings: { imported: 0, errors: 0 },
      sessions: { imported: 0, errors: 0 },
      preferences: { imported: 0, errors: 0 }
    };
    
    try {
      // Import vocabulary with deduplication
      results.vocabulary = await this.importVocabulary(exportData.vocabulary);
      
      // Import settings
      results.settings = await this.importSettings(exportData.settings);
      
      // Import session history
      results.sessions = await this.importSessions(exportData.session_history);
      
      // Import user preferences
      results.preferences = await this.importPreferences(exportData.user_preferences);
      
      return results;
      
    } catch (error) {
      console.error('Import failed:', error);
      throw new Error(`Import failed: ${error.message}`);
    }
  }
  
  private async importVocabulary(
    legacyVocab: LegacyVocabularyEntry[]
  ): Promise<ImportStats> {
    const stats: ImportStats = { imported: 0, skipped: 0, errors: 0 };
    
    const transaction = this.db.transaction(['vocabulary'], 'readwrite');
    const store = transaction.objectStore('vocabulary');
    
    for (const entry of legacyVocab) {
      try {
        // Check for duplicates
        const existing = await this.getExistingVocabularyEntry(
          store, 
          entry.spanish
        );
        
        if (existing) {
          stats.skipped++;
          continue;
        }
        
        // Transform legacy format to new format
        const newEntry: VocabularyEntry = {
          id: this.generateId(),
          spanish: entry.spanish,
          english: entry.english,
          dateAdded: new Date(entry.date_added || Date.now()),
          context: {
            searchQuery: entry.search_query,
            imageUrl: entry.image_url,
            fullText: entry.context
          },
          learning: {
            difficulty: entry.difficulty as DifficultyLevel,
            learned: entry.learned,
            reviewCount: entry.review_count,
            lastReviewed: entry.last_reviewed ? new Date(entry.last_reviewed) : null,
            nextReview: this.calculateNextReview(entry),
            successRate: 0
          },
          tags: this.extractTags(entry),
          createdAt: new Date(),
          updatedAt: new Date()
        };
        
        await store.add(newEntry);
        stats.imported++;
        
      } catch (error) {
        console.error(`Failed to import vocabulary entry:`, entry, error);
        stats.errors++;
      }
    }
    
    return stats;
  }
  
  private async importSettings(legacySettings: LegacySettings): Promise<ImportStats> {
    const stats: ImportStats = { imported: 0, errors: 0 };
    
    try {
      const transaction = this.db.transaction(['settings'], 'readwrite');
      const store = transaction.objectStore('settings');
      
      const newSettings: AppSettings = {
        id: 'user-settings',
        apiConfiguration: {
          openaiConfigured: legacySettings.api_keys_configured,
          unsplashConfigured: legacySettings.api_keys_configured,
          model: legacySettings.gpt_model || 'gpt-4o-mini'
        },
        ui: {
          theme: legacySettings.theme || 'light',
          language: legacySettings.language || 'en',
          zoomLevel: 100
        },
        learning: {
          autoGenerateQuiz: true,
          defaultDifficulty: 'intermediate',
          reviewAlgorithm: 'sm2'
        },
        privacy: {
          dataCollection: false,
          analytics: false,
          crashReporting: true
        },
        createdAt: new Date(),
        updatedAt: new Date()
      };
      
      await store.put(newSettings);
      stats.imported = 1;
      
    } catch (error) {
      console.error('Failed to import settings:', error);
      stats.errors = 1;
    }
    
    return stats;
  }
  
  private calculateNextReview(entry: LegacyVocabularyEntry): Date {
    // Implement spaced repetition algorithm
    const now = new Date();
    const baseInterval = 1; // days
    const factor = Math.max(1, entry.review_count) * 2.5;
    
    const nextReviewDate = new Date(now);
    nextReviewDate.setDate(now.getDate() + Math.floor(baseInterval * factor));
    
    return nextReviewDate;
  }
  
  private extractTags(entry: LegacyVocabularyEntry): string[] {
    const tags: string[] = [];
    
    // Extract tags from context
    if (entry.search_query) {
      tags.push(`query:${entry.search_query}`);
    }
    
    // Add difficulty tag
    if (entry.difficulty) {
      tags.push(`difficulty:${entry.difficulty}`);
    }
    
    // Add word type tags based on analysis
    const wordType = this.analyzeWordType(entry.spanish);
    if (wordType) {
      tags.push(`type:${wordType}`);
    }
    
    return tags;
  }
  
  private analyzeWordType(word: string): string | null {
    // Simple word type analysis
    const cleanWord = word.toLowerCase().trim();
    
    if (cleanWord.startsWith('el ') || cleanWord.startsWith('la ')) {
      return 'noun';
    }
    
    if (cleanWord.endsWith('ar') || cleanWord.endsWith('er') || cleanWord.endsWith('ir')) {
      return 'verb';
    }
    
    if (cleanWord.endsWith('mente')) {
      return 'adverb';
    }
    
    // Add more patterns as needed
    return null;
  }
}
```

### Platform-Specific Implementations

#### Tauri Desktop Configuration
```toml
# packages/desktop-app/src-tauri/Cargo.toml
[package]
name = "unsplash-ai-desktop"
version = "2.0.0"
description = "Unsplash AI Description Tool - Desktop Version"
authors = ["Your Name"]
license = "MIT"
repository = "https://github.com/yourusername/unsplash-ai-tool"
edition = "2021"

[build-dependencies]
tauri-build = { version = "1.0", features = [] }

[dependencies]
serde_json = "1.0"
serde = { version = "1.0", features = ["derive"] }
tauri = { version = "1.0", features = ["api-all"] }

[features]
default = ["custom-protocol"]
custom-protocol = ["tauri/custom-protocol"]
```

```json
// packages/desktop-app/src-tauri/tauri.conf.json
{
  "package": {
    "productName": "Unsplash AI Tool",
    "version": "2.0.0"
  },
  "build": {
    "distDir": "../web-app/dist",
    "devPath": "http://localhost:3000",
    "beforeDevCommand": "cd ../web-app && npm run dev",
    "beforeBuildCommand": "cd ../web-app && npm run build"
  },
  "tauri": {
    "allowlist": {
      "all": false,
      "fs": {
        "all": false,
        "readFile": true,
        "writeFile": true,
        "readDir": true,
        "copyFile": true,
        "createDir": true,
        "removeDir": true,
        "removeFile": true,
        "renameFile": true,
        "exists": true
      },
      "shell": {
        "all": false,
        "open": true
      },
      "dialog": {
        "all": false,
        "ask": true,
        "confirm": true,
        "message": true,
        "open": true,
        "save": true
      },
      "notification": {
        "all": true
      },
      "http": {
        "all": true,
        "request": true
      },
      "clipboard": {
        "all": true
      },
      "globalShortcut": {
        "all": true
      }
    },
    "bundle": {
      "active": true,
      "targets": "all",
      "identifier": "com.unsplash.ai.tool",
      "icon": [
        "icons/32x32.png",
        "icons/128x128.png",
        "icons/128x128@2x.png",
        "icons/icon.icns",
        "icons/icon.ico"
      ],
      "resources": [],
      "externalBin": [],
      "copyright": "",
      "category": "Education",
      "shortDescription": "",
      "longDescription": "",
      "deb": {
        "depends": []
      },
      "macOS": {
        "frameworks": [],
        "minimumSystemVersion": "",
        "exceptionDomain": "",
        "signingIdentity": null,
        "providerShortName": null,
        "entitlements": null
      },
      "windows": {
        "certificateThumbprint": null,
        "digestAlgorithm": "sha256",
        "timestampUrl": ""
      }
    },
    "security": {
      "csp": null
    },
    "windows": [
      {
        "fullscreen": false,
        "height": 800,
        "resizable": true,
        "title": "Unsplash AI Tool",
        "width": 1200,
        "minWidth": 800,
        "minHeight": 600,
        "center": true
      }
    ],
    "systemTray": {
      "iconPath": "icons/icon.png",
      "iconAsTemplate": true,
      "menuOnLeftClick": false
    },
    "updater": {
      "active": true,
      "endpoints": [
        "https://releases.yourdomain.com/{{target}}/{{current_version}}"
      ],
      "dialog": true,
      "pubkey": "your-public-key-here"
    }
  }
}
```

### Testing Strategy

#### Unit Tests
```typescript
// packages/web-app/src/features/image-search/__tests__/ImageSearchService.test.ts
import { ImageSearchService } from '../ImageSearchService';

describe('ImageSearchService', () => {
  let service: ImageSearchService;
  let mockApiKey: string;

  beforeEach(() => {
    mockApiKey = 'test-api-key';
    service = new ImageSearchService(mockApiKey);
  });

  describe('searchImages', () => {
    it('should return cached results when available', async () => {
      // Mock cache
      const cachedResults = { results: [], total: 0, total_pages: 0 };
      jest.spyOn(service as any, 'getFromIndexedDB').mockResolvedValue(cachedResults);

      const results = await service.searchImages('nature', 1, 10);

      expect(results).toEqual(cachedResults);
    });

    it('should fallback to offline results when network fails', async () => {
      // Mock network failure
      global.fetch = jest.fn().mockRejectedValue(new Error('Network error'));
      
      const offlineResults = { results: [], total: 0, total_pages: 0 };
      jest.spyOn(service as any, 'getOfflineResults').mockResolvedValue(offlineResults);

      const results = await service.searchImages('nature', 1, 10);

      expect(results).toEqual(offlineResults);
    });
  });
});
```

#### Integration Tests
```typescript
// packages/web-app/src/__tests__/integration/SearchWorkflow.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ImageSearchApp } from '../App';

describe('Search Workflow Integration', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });
  });

  it('should complete full search workflow', async () => {
    // Mock API responses
    global.fetch = jest.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          results: [
            {
              id: '1',
              urls: { regular: 'https://example.com/image1.jpg' },
              description: 'Test image'
            }
          ]
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          choices: [{
            message: { content: 'Generated description' }
          }]
        })
      });

    render(
      <QueryClientProvider client={queryClient}>
        <ImageSearchApp />
      </QueryClientProvider>
    );

    // Search for images
    const searchInput = screen.getByPlaceholderText('Search for images...');
    fireEvent.change(searchInput, { target: { value: 'nature' } });
    fireEvent.click(screen.getByText('Search'));

    // Wait for results
    await waitFor(() => {
      expect(screen.getByText('Test image')).toBeInTheDocument();
    });

    // Select image
    fireEvent.click(screen.getByText('Test image'));

    // Generate description
    fireEvent.click(screen.getByText('Generate Description'));

    // Wait for AI description
    await waitFor(() => {
      expect(screen.getByText('Generated description')).toBeInTheDocument();
    });
  });
});
```

#### End-to-End Tests (Cypress)
```typescript
// packages/web-app/cypress/e2e/user-workflow.cy.ts
describe('Complete User Workflow', () => {
  beforeEach(() => {
    cy.visit('/');
    
    // Mock API responses
    cy.intercept('GET', '**/search/photos**', {
      fixture: 'unsplash-search-response.json'
    }).as('searchImages');
    
    cy.intercept('POST', '**/chat/completions', {
      fixture: 'openai-completion-response.json'
    }).as('generateDescription');
  });

  it('should allow user to search, select image, and generate description', () => {
    // Search for images
    cy.get('[data-testid=search-input]').type('mountain landscape');
    cy.get('[data-testid=search-button]').click();

    // Wait for search results
    cy.wait('@searchImages');
    cy.get('[data-testid=image-result]').should('have.length.at.least', 1);

    // Select first image
    cy.get('[data-testid=image-result]').first().click();

    // Verify image is displayed
    cy.get('[data-testid=selected-image]').should('be.visible');

    // Add context note
    cy.get('[data-testid=context-input]').type('Focus on the natural beauty and lighting');

    // Generate description
    cy.get('[data-testid=generate-description-btn]').click();

    // Wait for AI response
    cy.wait('@generateDescription');

    // Verify description is generated
    cy.get('[data-testid=ai-description]')
      .should('be.visible')
      .and('contain.text', 'montaña');

    // Test vocabulary interaction
    cy.get('[data-testid=clickable-word]').first().click();
    
    // Verify translation tooltip
    cy.get('[data-testid=word-tooltip]').should('be.visible');

    // Test quiz functionality
    cy.get('[data-testid=start-quiz-btn]').click();
    cy.get('[data-testid=quiz-question]').should('be.visible');
  });

  it('should work offline after initial load', () => {
    // Load application online first
    cy.visit('/');
    cy.wait(2000); // Wait for service worker registration

    // Go offline
    cy.window().then((win) => {
      win.navigator.serviceWorker.getRegistration().then((registration) => {
        if (registration) {
          // Simulate offline mode
          cy.intercept('**', { forceNetworkError: true });
          
          // Test that cached content still works
          cy.get('[data-testid=search-input]').should('be.visible');
          cy.get('[data-testid=offline-indicator]').should('be.visible');
        }
      });
    });
  });
});
```

This comprehensive technical specification provides a complete roadmap for migrating your current Tkinter application to a modern hybrid PWA architecture. The solution maintains all existing functionality while adding significant improvements in performance, user experience, and cross-platform compatibility.