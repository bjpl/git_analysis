# Implementation Examples
## Transforming Current Features to Hybrid PWA Architecture

This document provides concrete implementation examples showing how your existing Tkinter application features would be transformed into the hybrid PWA architecture.

## Current vs. New Architecture Comparison

### Image Search Component

#### Current (Tkinter)
```python
# Current implementation in main.py
def thread_search_images(self, query):
    try:
        headers = {"Authorization": f"Client-ID {self.UNSPLASH_ACCESS_KEY}"}
        url = f"https://api.unsplash.com/search/photos?query={query}&page={self.current_page}&per_page=10"
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        self.current_results = data.get("results", [])
        # ... rest of implementation
```

#### New (React + TypeScript)
```typescript
// packages/web-app/src/features/image-search/ImageSearchService.ts
interface UnsplashResponse {
  results: UnsplashImage[];
  total: number;
  total_pages: number;
}

interface UnsplashImage {
  id: string;
  urls: {
    regular: string;
    small: string;
    thumb: string;
  };
  description: string;
  alt_description: string;
}

export class ImageSearchService {
  private apiKey: string;
  private cache = new Map<string, UnsplashResponse>();

  constructor(apiKey: string) {
    this.apiKey = apiKey;
  }

  async searchImages(
    query: string, 
    page = 1, 
    perPage = 10
  ): Promise<UnsplashResponse> {
    const cacheKey = `${query}-${page}-${perPage}`;
    
    // Check cache first (local-first)
    const cached = this.cache.get(cacheKey);
    if (cached) return cached;

    // Check IndexedDB cache
    const dbCached = await this.getFromIndexedDB(cacheKey);
    if (dbCached) {
      this.cache.set(cacheKey, dbCached);
      return dbCached;
    }

    try {
      const response = await fetch(
        `https://api.unsplash.com/search/photos?query=${query}&page=${page}&per_page=${perPage}`,
        {
          headers: {
            'Authorization': `Client-ID ${this.apiKey}`,
          },
        }
      );

      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      
      const data = await response.json() as UnsplashResponse;
      
      // Cache in memory and IndexedDB
      this.cache.set(cacheKey, data);
      await this.saveToIndexedDB(cacheKey, data);
      
      return data;
    } catch (error) {
      // Offline fallback
      const offlineResults = await this.getOfflineResults(query);
      if (offlineResults) return offlineResults;
      
      throw error;
    }
  }

  private async getFromIndexedDB(key: string): Promise<UnsplashResponse | null> {
    // IndexedDB implementation
    return new Promise((resolve) => {
      const request = indexedDB.open('ImageSearchDB', 1);
      request.onsuccess = () => {
        const db = request.result;
        const transaction = db.transaction(['searches'], 'readonly');
        const store = transaction.objectStore('searches');
        const getRequest = store.get(key);
        
        getRequest.onsuccess = () => resolve(getRequest.result?.data || null);
        getRequest.onerror = () => resolve(null);
      };
    });
  }

  private async saveToIndexedDB(key: string, data: UnsplashResponse): Promise<void> {
    // Save with expiration timestamp
    const item = {
      key,
      data,
      timestamp: Date.now(),
      expires: Date.now() + (1000 * 60 * 60 * 24) // 24 hours
    };
    
    return new Promise((resolve, reject) => {
      const request = indexedDB.open('ImageSearchDB', 1);
      request.onsuccess = () => {
        const db = request.result;
        const transaction = db.transaction(['searches'], 'readwrite');
        const store = transaction.objectStore('searches');
        
        store.put(item).onsuccess = () => resolve();
        store.put(item).onerror = () => reject();
      };
    });
  }
}
```

#### React Component Implementation
```typescript
// packages/web-app/src/features/image-search/ImageSearchComponent.tsx
import React, { useState, useCallback, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useVirtualizer } from '@tanstack/react-virtual';
import { ImageSearchService } from './ImageSearchService';

interface ImageSearchProps {
  onImageSelect: (image: UnsplashImage) => void;
  apiKey: string;
}

export const ImageSearchComponent: React.FC<ImageSearchProps> = ({
  onImageSelect,
  apiKey
}) => {
  const [query, setQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');

  const searchService = useMemo(() => new ImageSearchService(apiKey), [apiKey]);

  // Debounced search to avoid excessive API calls
  const debounce = useCallback(
    debounceFunction((value: string) => setDebouncedQuery(value), 300),
    []
  );

  React.useEffect(() => {
    if (query.trim()) {
      debounce(query.trim());
    }
  }, [query, debounce]);

  // React Query for caching and background refetching
  const {
    data: searchResults,
    isLoading,
    isError,
    error
  } = useQuery({
    queryKey: ['image-search', debouncedQuery],
    queryFn: () => searchService.searchImages(debouncedQuery),
    enabled: Boolean(debouncedQuery),
    staleTime: 1000 * 60 * 5, // 5 minutes
    cacheTime: 1000 * 60 * 30, // 30 minutes
    retry: 2,
    retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000)
  });

  // Virtual scrolling for performance with large result sets
  const parentRef = React.useRef<HTMLDivElement>(null);
  const virtualizer = useVirtualizer({
    count: searchResults?.results.length || 0,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 300,
    overscan: 5
  });

  const handleSearch = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    // Search is handled by the debounced effect
  }, []);

  return (
    <div className="image-search">
      <form onSubmit={handleSearch} className="search-form">
        <div className="search-input-group">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search for images..."
            className="search-input"
            disabled={isLoading}
          />
          <button 
            type="submit" 
            disabled={isLoading || !query.trim()}
            className="search-button"
          >
            {isLoading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </form>

      {isError && (
        <div className="error-message">
          <p>Search failed: {error?.message}</p>
          <p>Check your connection or try again.</p>
        </div>
      )}

      {searchResults && (
        <div 
          ref={parentRef}
          className="results-container"
          style={{ height: '600px', overflow: 'auto' }}
        >
          <div
            style={{
              height: `${virtualizer.getTotalSize()}px`,
              width: '100%',
              position: 'relative'
            }}
          >
            {virtualizer.getVirtualItems().map((virtualItem) => {
              const image = searchResults.results[virtualItem.index];
              return (
                <div
                  key={virtualItem.key}
                  style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '100%',
                    height: `${virtualItem.size}px`,
                    transform: `translateY(${virtualItem.start}px)`
                  }}
                >
                  <ImageCard 
                    image={image}
                    onSelect={() => onImageSelect(image)}
                  />
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

// Utility function
function debounceFunction<T extends (...args: any[]) => void>(
  func: T,
  wait: number
): T {
  let timeout: NodeJS.Timeout;
  return ((...args: any[]) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(null, args), wait);
  }) as T;
}
```

### AI Description Generation

#### Current (Python + OpenAI)
```python
# Current implementation
def thread_generate_description(self, user_note):
    try:
        if self.style_manager:
            prompt = self.style_manager.generate_description_prompt(
                context=user_note,
                focus_areas=[user_note] if user_note else []
            )
        else:
            # Fallback prompt...
            
        response = self.openai_client.chat.completions.create(
            model=self.GPT_MODEL,
            messages=[{
                "role": "user",
                "content": [{
                    "type": "text", "text": prompt
                }, {
                    "type": "image_url", 
                    "image_url": {"url": self.current_image_url, "detail": "high"}
                }]
            }],
            max_tokens=600,
            temperature=0.7,
        )
        
        generated_text = response.choices[0].message.content.strip()
        self.after(0, lambda: self.display_description(generated_text))
```

#### New (React + Streaming)
```typescript
// packages/web-app/src/features/ai-description/AIDescriptionService.ts
import { OpenAI } from 'openai';

export interface DescriptionOptions {
  style: 'academic' | 'poetic' | 'technical' | 'conversational';
  vocabularyLevel: 'beginner' | 'intermediate' | 'advanced' | 'native';
  focusAreas: string[];
  userContext?: string;
}

export class AIDescriptionService {
  private openai: OpenAI;
  private fallbackProvider?: 'anthropic' | 'local';

  constructor(apiKey: string, fallbackProvider?: 'anthropic' | 'local') {
    this.openai = new OpenAI({ 
      apiKey,
      dangerouslyAllowBrowser: true // Only for demo - use proxy in production
    });
    this.fallbackProvider = fallbackProvider;
  }

  async *generateDescription(
    imageUrl: string,
    options: DescriptionOptions,
    onProgress?: (chunk: string) => void
  ): AsyncGenerator<string, string, unknown> {
    const prompt = this.buildPrompt(options);
    
    try {
      const stream = await this.openai.chat.completions.create({
        model: 'gpt-4-vision-preview',
        messages: [{
          role: 'user',
          content: [
            { type: 'text', text: prompt },
            { 
              type: 'image_url', 
              image_url: { url: imageUrl, detail: 'high' }
            }
          ]
        }],
        max_tokens: 600,
        temperature: 0.7,
        stream: true
      });

      let fullResponse = '';
      
      for await (const chunk of stream) {
        const content = chunk.choices[0]?.delta?.content || '';
        if (content) {
          fullResponse += content;
          onProgress?.(content);
          yield content;
        }
      }

      // Cache the complete response
      await this.cacheResponse(imageUrl, options, fullResponse);
      
      return fullResponse;
      
    } catch (error) {
      console.error('Primary AI service failed:', error);
      
      // Fallback to alternative provider or cached response
      const cached = await this.getCachedResponse(imageUrl, options);
      if (cached) {
        yield cached;
        return cached;
      }
      
      if (this.fallbackProvider) {
        return yield* this.useFallbackProvider(imageUrl, options, onProgress);
      }
      
      throw error;
    }
  }

  private buildPrompt(options: DescriptionOptions): string {
    const styleInstructions = {
      academic: 'Use formal, precise academic language with technical vocabulary.',
      poetic: 'Use creative, evocative language with metaphors and imagery.',
      technical: 'Focus on technical aspects, composition, and visual elements.',
      conversational: 'Use natural, everyday language as if talking to a friend.'
    };

    const vocabularyInstructions = {
      beginner: 'Use simple, common words. Explain any complex terms.',
      intermediate: 'Use varied vocabulary appropriate for intermediate learners.',
      advanced: 'Use sophisticated vocabulary and complex sentence structures.',
      native: 'Use advanced vocabulary and idiomatic expressions freely.'
    };

    let prompt = `Analiza esta imagen y descríbela en español latinoamericano.\n\n`;
    prompt += `ESTILO: ${styleInstructions[options.style]}\n`;
    prompt += `VOCABULARIO: ${vocabularyInstructions[options.vocabularyLevel]}\n\n`;

    if (options.focusAreas.length > 0) {
      prompt += `ÁREAS DE ENFOQUE: ${options.focusAreas.join(', ')}\n\n`;
    }

    if (options.userContext) {
      prompt += `CONTEXTO ADICIONAL: ${options.userContext}\n\n`;
    }

    prompt += `Proporciona una descripción detallada de 1-2 párrafos.`;

    return prompt;
  }

  private async cacheResponse(
    imageUrl: string, 
    options: DescriptionOptions, 
    response: string
  ): Promise<void> {
    const key = this.generateCacheKey(imageUrl, options);
    const item = {
      key,
      response,
      timestamp: Date.now(),
      expires: Date.now() + (1000 * 60 * 60 * 24 * 7) // 1 week
    };

    return new Promise((resolve) => {
      const request = indexedDB.open('AIResponsesDB', 1);
      request.onsuccess = () => {
        const db = request.result;
        const transaction = db.transaction(['responses'], 'readwrite');
        const store = transaction.objectStore('responses');
        
        store.put(item).onsuccess = () => resolve();
      };
    });
  }

  private async getCachedResponse(
    imageUrl: string, 
    options: DescriptionOptions
  ): Promise<string | null> {
    const key = this.generateCacheKey(imageUrl, options);
    
    return new Promise((resolve) => {
      const request = indexedDB.open('AIResponsesDB', 1);
      request.onsuccess = () => {
        const db = request.result;
        const transaction = db.transaction(['responses'], 'readonly');
        const store = transaction.objectStore('responses');
        const getRequest = store.get(key);
        
        getRequest.onsuccess = () => {
          const item = getRequest.result;
          if (item && item.expires > Date.now()) {
            resolve(item.response);
          } else {
            resolve(null);
          }
        };
        getRequest.onerror = () => resolve(null);
      };
    });
  }

  private generateCacheKey(imageUrl: string, options: DescriptionOptions): string {
    return `${imageUrl}-${options.style}-${options.vocabularyLevel}-${options.focusAreas.join('-')}`;
  }

  private async *useFallbackProvider(
    imageUrl: string,
    options: DescriptionOptions,
    onProgress?: (chunk: string) => void
  ): AsyncGenerator<string, string, unknown> {
    // Implementation for fallback providers (Anthropic, local LLM, etc.)
    // This would be similar but using different APIs
    throw new Error('Fallback provider not implemented');
  }
}
```

#### React Component for AI Description
```typescript
// packages/web-app/src/features/ai-description/AIDescriptionComponent.tsx
import React, { useState, useCallback } from 'react';
import { AIDescriptionService, DescriptionOptions } from './AIDescriptionService';

interface AIDescriptionProps {
  imageUrl: string;
  apiKey: string;
  onDescriptionGenerated: (description: string) => void;
}

export const AIDescriptionComponent: React.FC<AIDescriptionProps> = ({
  imageUrl,
  apiKey,
  onDescriptionGenerated
}) => {
  const [description, setDescription] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [options, setOptions] = useState<DescriptionOptions>({
    style: 'conversational',
    vocabularyLevel: 'intermediate',
    focusAreas: [],
    userContext: ''
  });

  const aiService = React.useMemo(
    () => new AIDescriptionService(apiKey),
    [apiKey]
  );

  const generateDescription = useCallback(async () => {
    if (!imageUrl) return;

    setIsGenerating(true);
    setDescription('');

    try {
      const generator = aiService.generateDescription(
        imageUrl,
        options,
        (chunk) => {
          // Real-time streaming - show text as it's generated
          setDescription(prev => prev + chunk);
        }
      );

      let fullDescription = '';
      for await (const chunk of generator) {
        fullDescription += chunk;
      }

      onDescriptionGenerated(fullDescription);
      
    } catch (error) {
      console.error('Failed to generate description:', error);
      setDescription('Error generating description. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  }, [imageUrl, options, aiService, onDescriptionGenerated]);

  return (
    <div className="ai-description">
      <div className="description-controls">
        <div className="style-selector">
          <label htmlFor="style">Style:</label>
          <select
            id="style"
            value={options.style}
            onChange={(e) => setOptions(prev => ({ 
              ...prev, 
              style: e.target.value as DescriptionOptions['style']
            }))}
            disabled={isGenerating}
          >
            <option value="conversational">Conversational</option>
            <option value="academic">Academic</option>
            <option value="poetic">Poetic</option>
            <option value="technical">Technical</option>
          </select>
        </div>

        <div className="vocabulary-selector">
          <label htmlFor="vocabulary">Vocabulary Level:</label>
          <select
            id="vocabulary"
            value={options.vocabularyLevel}
            onChange={(e) => setOptions(prev => ({ 
              ...prev, 
              vocabularyLevel: e.target.value as DescriptionOptions['vocabularyLevel']
            }))}
            disabled={isGenerating}
          >
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
            <option value="native">Native</option>
          </select>
        </div>

        <div className="context-input">
          <label htmlFor="context">Additional Context:</label>
          <textarea
            id="context"
            value={options.userContext}
            onChange={(e) => setOptions(prev => ({ 
              ...prev, 
              userContext: e.target.value
            }))}
            placeholder="Any specific aspects you'd like me to focus on..."
            disabled={isGenerating}
          />
        </div>

        <button 
          onClick={generateDescription}
          disabled={isGenerating || !imageUrl}
          className="generate-button"
        >
          {isGenerating ? 'Generating...' : 'Generate Description'}
        </button>
      </div>

      <div className="description-output">
        <div className="description-text">
          {description && (
            <ClickableText
              text={description}
              onWordClick={(word) => {
                // Handle vocabulary extraction
                console.log('Word clicked:', word);
              }}
            />
          )}
          {isGenerating && <div className="typing-indicator">▊</div>}
        </div>

        {description && (
          <div className="description-actions">
            <button 
              onClick={() => navigator.clipboard.writeText(description)}
              className="copy-button"
            >
              📋 Copy
            </button>
            <button 
              onClick={() => {
                // Export or save functionality
              }}
              className="save-button"
            >
              💾 Save
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
```

### Vocabulary Management System

#### Enhanced Clickable Text Component
```typescript
// packages/web-app/src/features/vocabulary/ClickableTextComponent.tsx
import React, { useCallback, useState } from 'react';
import { VocabularyService } from './VocabularyService';

interface ClickableTextProps {
  text: string;
  onWordClick: (word: string, translation?: string) => void;
  vocabularyService: VocabularyService;
  language?: 'es' | 'en';
}

export const ClickableText: React.FC<ClickableTextProps> = ({
  text,
  onWordClick,
  vocabularyService,
  language = 'es'
}) => {
  const [hoveredWord, setHoveredWord] = useState<string | null>(null);
  const [translations, setTranslations] = useState<Map<string, string>>(new Map());

  const handleWordClick = useCallback(async (word: string) => {
    // Clean the word (remove punctuation, etc.)
    const cleanWord = word.replace(/[^\w\sáéíóúüñ]/gi, '').toLowerCase();
    
    if (cleanWord.length < 2) return;

    try {
      // Get or generate translation
      let translation = translations.get(cleanWord);
      
      if (!translation) {
        translation = await vocabularyService.translateWord(cleanWord, language);
        setTranslations(prev => new Map(prev).set(cleanWord, translation!));
      }

      // Add to vocabulary collection
      await vocabularyService.addWord(cleanWord, translation, {
        context: text,
        sourceLanguage: language,
        targetLanguage: language === 'es' ? 'en' : 'es'
      });

      onWordClick(cleanWord, translation);
      
    } catch (error) {
      console.error('Failed to process word:', error);
      onWordClick(cleanWord);
    }
  }, [text, onWordClick, vocabularyService, language, translations]);

  const handleWordHover = useCallback(async (word: string) => {
    const cleanWord = word.replace(/[^\w\sáéíóúüñ]/gi, '').toLowerCase();
    
    if (cleanWord.length < 2) return;
    
    setHoveredWord(cleanWord);

    // Preload translation for better UX
    if (!translations.has(cleanWord)) {
      try {
        const translation = await vocabularyService.translateWord(cleanWord, language);
        setTranslations(prev => new Map(prev).set(cleanWord, translation));
      } catch (error) {
        // Silent fail for hover preloading
      }
    }
  }, [vocabularyService, language, translations]);

  // Split text into clickable words while preserving formatting
  const renderClickableText = useCallback(() => {
    const words = text.split(/(\s+)/);
    
    return words.map((word, index) => {
      const isSpace = /^\s+$/.test(word);
      if (isSpace) return word;

      const cleanWord = word.replace(/[^\w\sáéíóúüñ]/gi, '').toLowerCase();
      const isClickable = cleanWord.length >= 2;

      if (isClickable) {
        const translation = translations.get(cleanWord);
        const isHovered = hoveredWord === cleanWord;

        return (
          <span
            key={index}
            className={`clickable-word ${isHovered ? 'hovered' : ''}`}
            onClick={() => handleWordClick(word)}
            onMouseEnter={() => handleWordHover(word)}
            onMouseLeave={() => setHoveredWord(null)}
            title={translation || 'Click to translate'}
          >
            {word}
            {isHovered && translation && (
              <span className="word-tooltip">{translation}</span>
            )}
          </span>
        );
      }

      return <span key={index}>{word}</span>;
    });
  }, [text, translations, hoveredWord, handleWordClick, handleWordHover]);

  return (
    <div className="clickable-text">
      {renderClickableText()}
    </div>
  );
};
```

### Offline Synchronization

#### Service Worker Implementation
```typescript
// packages/web-app/public/sw.ts - Service Worker for offline functionality
const CACHE_NAME = 'unsplash-ai-v1';
const API_CACHE = 'api-cache-v1';

// Cache static assets
const STATIC_ASSETS = [
  '/',
  '/static/js/bundle.js',
  '/static/css/main.css',
  '/manifest.json'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(STATIC_ASSETS))
  );
});

self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Handle API requests
  if (url.origin === 'https://api.unsplash.com' || url.origin === 'https://api.openai.com') {
    event.respondWith(handleApiRequest(request));
    return;
  }

  // Handle static assets
  if (request.destination === 'script' || request.destination === 'style') {
    event.respondWith(
      caches.match(request).then(response => 
        response || fetch(request)
      )
    );
    return;
  }

  // Handle navigation requests
  if (request.mode === 'navigate') {
    event.respondWith(
      caches.match('/').then(response => 
        response || fetch(request)
      )
    );
  }
});

async function handleApiRequest(request: Request): Promise<Response> {
  const cache = await caches.open(API_CACHE);
  
  try {
    // Try network first for fresh data
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      // Cache successful responses
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
    
  } catch (error) {
    // Network failed, try cache
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // No cache available, return offline response
    return new Response(
      JSON.stringify({ 
        error: 'Offline', 
        message: 'No network connection and no cached data available' 
      }),
      { 
        status: 503,
        statusText: 'Service Unavailable',
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// Background sync for vocabulary data
self.addEventListener('sync', (event) => {
  if (event.tag === 'vocabulary-sync') {
    event.waitUntil(syncVocabularyData());
  }
});

async function syncVocabularyData() {
  // Sync local vocabulary changes with cloud storage
  const db = await openIndexedDB();
  const transaction = db.transaction(['vocabulary'], 'readonly');
  const store = transaction.objectStore('vocabulary');
  
  const pendingSync = await store.getAll();
  
  for (const item of pendingSync) {
    if (item.needsSync) {
      try {
        // Sync with cloud storage (Supabase, Firebase, etc.)
        await syncToCloud(item);
        
        // Mark as synced
        item.needsSync = false;
        await store.put(item);
        
      } catch (error) {
        console.error('Sync failed for item:', item.id, error);
      }
    }
  }
}
```

This implementation provides:

1. **Complete feature parity** with your current Tkinter app
2. **Enhanced user experience** with streaming AI responses
3. **Offline-first architecture** with intelligent caching
4. **Performance optimizations** using virtual scrolling and debouncing
5. **Modern web standards** with PWA capabilities
6. **Cross-platform compatibility** ready for Tauri/Capacitor wrapping

The architecture maintains all your existing functionality while adding modern web capabilities like real-time streaming, offline support, and responsive design that works across all devices.