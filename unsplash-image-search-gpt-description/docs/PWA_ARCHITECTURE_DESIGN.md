# PWA Architecture Design: Unsplash Image Search with Supabase

## Executive Summary

This document outlines the complete system architecture for migrating the desktop Unsplash Image Search application to a Progressive Web App (PWA) using React 18, TypeScript, and Supabase as the backend service. The architecture supports offline-first functionality, real-time collaboration, scalable infrastructure, and comprehensive Spanish vocabulary learning features.

## 1. System Overview

### 1.1 Architecture Philosophy
- **Progressive Enhancement**: Works offline-first, enhances with connectivity
- **Mobile-First Design**: Responsive across all device types
- **Security by Design**: Zero-trust architecture with RLS policies
- **Scalable Infrastructure**: Auto-scaling with global edge distribution
- **Developer Experience**: Type-safe, testable, maintainable codebase

### 1.2 Technology Stack

#### Frontend Stack
- **Framework**: React 18 with Concurrent Features
- **Language**: TypeScript 5.0+
- **State Management**: TanStack Query + Zustand
- **UI Framework**: Tailwind CSS + Shadcn/ui
- **PWA**: Vite PWA plugin with Workbox
- **Build Tool**: Vite 4.0+
- **Testing**: Vitest + React Testing Library + Playwright

#### Backend Stack
- **Backend-as-a-Service**: Supabase
- **Database**: PostgreSQL 15 with extensions
- **Authentication**: Supabase Auth (JWT-based)
- **Real-time**: Supabase Realtime (WebSocket)
- **Storage**: Supabase Storage (S3-compatible)
- **Edge Functions**: Deno-based serverless functions

#### Third-party Services
- **Image Search**: Unsplash API (proxied)
- **AI Descriptions**: OpenAI GPT-4 (streamed)
- **Analytics**: PostHog (privacy-focused)
- **Error Tracking**: Sentry
- **CDN**: Vercel Edge Network

## 2. System Architecture

### 2.1 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  React 18 PWA Application                                                   │
│  ├── Service Worker (Workbox)          ├── React Components                 │
│  ├── IndexedDB Cache                   ├── TanStack Query                   │
│  ├── Background Sync                   ├── Zustand Store                    │
│  └── Push Notifications                └── TypeScript Types                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                              EDGE LAYER                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  Vercel Edge Functions                 │  Supabase Edge Functions           │
│  ├── Route Handlers                    ├── API Proxies                      │
│  ├── Middleware                        ├── AI Stream Processing             │
│  ├── Static Assets                     ├── Image Processing                 │
│  └── CDN Distribution                  └── Webhook Handlers                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                            BACKEND LAYER                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  Supabase Platform                                                          │
│  ├── PostgreSQL Database               ├── Authentication                   │
│  ├── Row Level Security                ├── Real-time Subscriptions          │
│  ├── Storage Buckets                   ├── API Gateway                      │
│  └── Database Functions                └── Connection Pooling               │
├─────────────────────────────────────────────────────────────────────────────┤
│                          EXTERNAL SERVICES                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  ├── Unsplash API                      ├── OpenAI API                       │
│  ├── PostHog Analytics                 ├── Sentry Error Tracking            │
│  └── Email Service (Resend)            └── Push Notification Service        │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Component Architecture (C4 Model)

#### Level 1: System Context
```
┌──────────────┐    ┌─────────────────────┐    ┌──────────────┐
│    Users     │───▶│  Vocabulary PWA     │───▶│  AI Services │
│              │    │                     │    │              │
│ • Students   │    │ • Image Search      │    │ • OpenAI     │
│ • Teachers   │    │ • Vocabulary        │    │ • Unsplash   │
│ • Learners   │    │ • Quizzes          │    │              │
└──────────────┘    └─────────────────────┘    └──────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │   Supabase   │
                    │              │
                    │ • Database   │
                    │ • Auth       │
                    │ • Storage    │
                    └──────────────┘
```

#### Level 2: Container Diagram
```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Web Browser                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │
│  │   React App     │  │  Service Worker │  │   IndexedDB     │         │
│  │                 │  │                 │  │                 │         │
│  │ • Components    │  │ • Offline Cache │  │ • Local Storage │         │
│  │ • State Mgmt    │  │ • Background    │  │ • Search Cache  │         │
│  │ • API Client    │  │   Sync          │  │ • User Data     │         │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘         │
└─────────────────────────────────────────────────────────────────────────┘
           │                        │                        │
           ▼                        ▼                        ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  Vercel Edge    │  │ Supabase Edge   │  │   Supabase      │
│                 │  │   Functions     │  │   Platform      │
│ • Static Host   │  │                 │  │                 │
│ • Edge Routes   │  │ • API Proxy     │  │ • PostgreSQL    │
│ • Middleware    │  │ • AI Streaming  │  │ • Auth System   │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

## 3. Database Schema Design

### 3.1 PostgreSQL Schema with Extensions

```sql
-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "fuzzystrmatch";

-- Custom types
CREATE TYPE description_style AS ENUM ('academic', 'poetic', 'technical');
CREATE TYPE vocabulary_level AS ENUM ('beginner', 'intermediate', 'advanced', 'native');
CREATE TYPE quiz_difficulty AS ENUM ('easy', 'medium', 'hard');

-- Users table (extends auth.users)
CREATE TABLE public.user_profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    username TEXT UNIQUE,
    display_name TEXT,
    avatar_url TEXT,
    native_language TEXT DEFAULT 'en',
    target_language TEXT DEFAULT 'es',
    learning_level vocabulary_level DEFAULT 'intermediate',
    preferred_style description_style DEFAULT 'academic',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Search sessions
CREATE TABLE public.search_sessions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.user_profiles(id) ON DELETE CASCADE NOT NULL,
    query TEXT NOT NULL,
    style description_style DEFAULT 'academic',
    vocabulary_level vocabulary_level DEFAULT 'intermediate',
    images_viewed INTEGER DEFAULT 0,
    descriptions_generated INTEGER DEFAULT 0,
    vocabulary_collected INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vocabulary items
CREATE TABLE public.vocabulary_items (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.user_profiles(id) ON DELETE CASCADE NOT NULL,
    session_id UUID REFERENCES public.search_sessions(id) ON DELETE SET NULL,
    
    -- Vocabulary data
    spanish_word TEXT NOT NULL,
    english_translation TEXT NOT NULL,
    part_of_speech TEXT,
    difficulty_level vocabulary_level DEFAULT 'intermediate',
    
    -- Context information
    context_sentence TEXT,
    image_url TEXT,
    image_alt_text TEXT,
    search_query TEXT,
    
    -- Learning metadata
    times_reviewed INTEGER DEFAULT 0,
    times_correct INTEGER DEFAULT 0,
    last_reviewed_at TIMESTAMPTZ,
    mastery_level REAL DEFAULT 0.0,
    
    -- Audit fields
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(user_id, spanish_word)
);

-- Image cache and metadata
CREATE TABLE public.cached_images (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    unsplash_id TEXT UNIQUE NOT NULL,
    url_regular TEXT NOT NULL,
    url_small TEXT NOT NULL,
    url_thumb TEXT NOT NULL,
    
    -- Image metadata
    description TEXT,
    alt_description TEXT,
    tags TEXT[],
    color TEXT,
    width INTEGER,
    height INTEGER,
    
    -- Attribution
    photographer_name TEXT,
    photographer_username TEXT,
    photographer_url TEXT,
    
    -- Cache metadata
    cache_expires_at TIMESTAMPTZ,
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMPTZ DEFAULT NOW(),
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- AI-generated descriptions
CREATE TABLE public.ai_descriptions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.user_profiles(id) ON DELETE CASCADE NOT NULL,
    session_id UUID REFERENCES public.search_sessions(id) ON DELETE SET NULL,
    image_id UUID REFERENCES public.cached_images(id) ON DELETE CASCADE NOT NULL,
    
    -- Description content
    content TEXT NOT NULL,
    style description_style NOT NULL,
    vocabulary_level vocabulary_level NOT NULL,
    word_count INTEGER,
    
    -- Generation metadata
    model_used TEXT DEFAULT 'gpt-4',
    generation_time_ms INTEGER,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    
    -- Quality metrics
    user_rating INTEGER CHECK (user_rating >= 1 AND user_rating <= 5),
    vocabulary_extracted INTEGER DEFAULT 0,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Quiz sessions
CREATE TABLE public.quiz_sessions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.user_profiles(id) ON DELETE CASCADE NOT NULL,
    
    -- Quiz configuration
    title TEXT DEFAULT 'Vocabulary Quiz',
    difficulty quiz_difficulty DEFAULT 'medium',
    total_questions INTEGER NOT NULL,
    time_limit_seconds INTEGER,
    
    -- Quiz state
    current_question INTEGER DEFAULT 0,
    score INTEGER DEFAULT 0,
    is_completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMPTZ,
    
    -- Performance metrics
    accuracy_percentage REAL,
    average_response_time_ms INTEGER,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Quiz questions and answers
CREATE TABLE public.quiz_questions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    quiz_session_id UUID REFERENCES public.quiz_sessions(id) ON DELETE CASCADE NOT NULL,
    vocabulary_item_id UUID REFERENCES public.vocabulary_items(id) ON DELETE CASCADE NOT NULL,
    
    -- Question data
    question_text TEXT NOT NULL,
    question_type TEXT DEFAULT 'multiple_choice',
    correct_answer TEXT NOT NULL,
    incorrect_options TEXT[],
    
    -- Response data
    user_answer TEXT,
    is_correct BOOLEAN,
    response_time_ms INTEGER,
    answered_at TIMESTAMPTZ,
    
    -- Question metadata
    question_order INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Shared vocabulary lists
CREATE TABLE public.shared_lists (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    owner_id UUID REFERENCES public.user_profiles(id) ON DELETE CASCADE NOT NULL,
    
    -- List metadata
    title TEXT NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    share_code TEXT UNIQUE,
    
    -- List statistics
    vocabulary_count INTEGER DEFAULT 0,
    subscriber_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Many-to-many relationship for shared lists
CREATE TABLE public.shared_list_items (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    shared_list_id UUID REFERENCES public.shared_lists(id) ON DELETE CASCADE NOT NULL,
    vocabulary_item_id UUID REFERENCES public.vocabulary_items(id) ON DELETE CASCADE NOT NULL,
    added_by UUID REFERENCES public.user_profiles(id) ON DELETE SET NULL,
    added_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(shared_list_id, vocabulary_item_id)
);

-- User preferences
CREATE TABLE public.user_preferences (
    user_id UUID REFERENCES public.user_profiles(id) ON DELETE CASCADE PRIMARY KEY,
    
    -- UI preferences
    theme TEXT DEFAULT 'system',
    language TEXT DEFAULT 'en',
    notifications_enabled BOOLEAN DEFAULT TRUE,
    
    -- Learning preferences
    default_style description_style DEFAULT 'academic',
    default_level vocabulary_level DEFAULT 'intermediate',
    quiz_reminder_interval_hours INTEGER DEFAULT 24,
    
    -- PWA preferences
    offline_sync_enabled BOOLEAN DEFAULT TRUE,
    auto_cache_images BOOLEAN DEFAULT TRUE,
    max_cache_size_mb INTEGER DEFAULT 100,
    
    -- Privacy preferences
    analytics_enabled BOOLEAN DEFAULT TRUE,
    share_progress BOOLEAN DEFAULT FALSE,
    
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Analytics and usage tracking
CREATE TABLE public.usage_analytics (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.user_profiles(id) ON DELETE CASCADE,
    
    -- Event data
    event_type TEXT NOT NULL,
    event_data JSONB,
    
    -- Session context
    session_id TEXT,
    page_url TEXT,
    user_agent TEXT,
    
    -- Performance metrics
    load_time_ms INTEGER,
    interaction_time_ms INTEGER,
    
    -- Geographic data (anonymized)
    country_code TEXT,
    timezone TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 3.2 Indexes for Performance

```sql
-- Performance indexes
CREATE INDEX idx_vocabulary_user_id ON public.vocabulary_items(user_id);
CREATE INDEX idx_vocabulary_session_id ON public.vocabulary_items(session_id);
CREATE INDEX idx_vocabulary_mastery ON public.vocabulary_items(mastery_level);
CREATE INDEX idx_search_sessions_user ON public.search_sessions(user_id);
CREATE INDEX idx_cached_images_unsplash ON public.cached_images(unsplash_id);
CREATE INDEX idx_ai_descriptions_user ON public.ai_descriptions(user_id);
CREATE INDEX idx_quiz_sessions_user ON public.quiz_sessions(user_id);
CREATE INDEX idx_analytics_user_event ON public.usage_analytics(user_id, event_type);

-- Full-text search indexes
CREATE INDEX idx_vocabulary_spanish_fts ON public.vocabulary_items USING GIN(to_tsvector('spanish', spanish_word));
CREATE INDEX idx_vocabulary_english_fts ON public.vocabulary_items USING GIN(to_tsvector('english', english_translation));
CREATE INDEX idx_descriptions_content_fts ON public.ai_descriptions USING GIN(to_tsvector('spanish', content));
```

### 3.3 Row Level Security (RLS) Policies

```sql
-- Enable RLS on all tables
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.search_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.vocabulary_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.cached_images ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ai_descriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.quiz_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.quiz_questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.shared_lists ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.shared_list_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.usage_analytics ENABLE ROW LEVEL SECURITY;

-- User profiles policies
CREATE POLICY "Users can view their own profile" ON public.user_profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile" ON public.user_profiles
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert their own profile" ON public.user_profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

-- Vocabulary items policies
CREATE POLICY "Users can manage their vocabulary" ON public.vocabulary_items
    FOR ALL USING (auth.uid() = user_id);

-- Search sessions policies
CREATE POLICY "Users can manage their search sessions" ON public.search_sessions
    FOR ALL USING (auth.uid() = user_id);

-- AI descriptions policies
CREATE POLICY "Users can view their descriptions" ON public.ai_descriptions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create descriptions" ON public.ai_descriptions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Cached images policies (read-only for all authenticated users)
CREATE POLICY "Authenticated users can view cached images" ON public.cached_images
    FOR SELECT TO authenticated USING (true);

-- Quiz policies
CREATE POLICY "Users can manage their quizzes" ON public.quiz_sessions
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can manage their quiz questions" ON public.quiz_questions
    FOR ALL USING (
        auth.uid() = (
            SELECT user_id FROM public.quiz_sessions 
            WHERE id = quiz_session_id
        )
    );

-- Shared lists policies
CREATE POLICY "Users can view public lists" ON public.shared_lists
    FOR SELECT USING (is_public = true OR auth.uid() = owner_id);

CREATE POLICY "Users can manage their lists" ON public.shared_lists
    FOR ALL USING (auth.uid() = owner_id);

-- User preferences policies
CREATE POLICY "Users can manage their preferences" ON public.user_preferences
    FOR ALL USING (auth.uid() = user_id);

-- Analytics policies (insert only)
CREATE POLICY "Users can insert their analytics" ON public.usage_analytics
    FOR INSERT WITH CHECK (auth.uid() = user_id OR user_id IS NULL);
```

## 4. Frontend Architecture

### 4.1 React Component Hierarchy

```
App
├── Providers
│   ├── QueryProvider (TanStack Query)
│   ├── AuthProvider (Supabase Auth)
│   ├── ThemeProvider (Tailwind + Context)
│   └── ErrorBoundary (Sentry Integration)
│
├── Layout
│   ├── Header
│   │   ├── SearchBar
│   │   ├── UserMenu
│   │   └── NotificationCenter
│   ├── Sidebar
│   │   ├── Navigation
│   │   ├── RecentSessions
│   │   └── QuickStats
│   └── Footer
│       ├── OfflineIndicator
│       └── SyncStatus
│
├── Features
│   ├── Authentication
│   │   ├── LoginForm
│   │   ├── SignUpForm
│   │   └── PasswordReset
│   │
│   ├── ImageSearch
│   │   ├── SearchInterface
│   │   ├── StyleSelector
│   │   ├── ImageGallery
│   │   ├── ImageViewer
│   │   └── SearchHistory
│   │
│   ├── AIDescriptions
│   │   ├── DescriptionGenerator
│   │   ├── DescriptionViewer
│   │   ├── StyleCustomizer
│   │   └── StreamingIndicator
│   │
│   ├── VocabularyManagement
│   │   ├── VocabularyList
│   │   ├── VocabularyCard
│   │   ├── WordDetails
│   │   ├── ClickableText
│   │   └── ImportExport
│   │
│   ├── Quiz System
│   │   ├── QuizCreator
│   │   ├── QuizPlayer
│   │   ├── QuestionTypes
│   │   ├── ScoreBoard
│   │   └── ProgressTracker
│   │
│   ├── Collaboration
│   │   ├── SharedLists
│   │   ├── ListSharing
│   │   └── RealTimeUpdates
│   │
│   └── Settings
│       ├── ProfileSettings
│       ├── LearningPreferences
│       ├── DataManagement
│       └── PWASettings
│
└── Shared Components
    ├── UI Components (Shadcn/ui)
    ├── LoadingStates
    ├── ErrorStates
    ├── EmptyStates
    ├── ConfirmationDialogs
    └── KeyboardShortcuts
```

### 4.2 State Management Architecture

#### TanStack Query Configuration
```typescript
// lib/query-client.ts
import { QueryClient } from '@tanstack/react-query';
import { createSyncStoragePersister } from '@tanstack/query-sync-storage-persister';
import { persistQueryClient } from '@tanstack/react-query-persist-client';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes
      retry: (failureCount, error) => {
        if (error instanceof NetworkError) return false;
        return failureCount < 3;
      },
    },
    mutations: {
      retry: 1,
      networkMode: 'offlineFirst',
    },
  },
});

// PWA persistence
const persister = createSyncStoragePersister({
  storage: window.localStorage,
});

persistQueryClient({
  queryClient,
  persister,
  maxAge: 24 * 60 * 60 * 1000, // 24 hours
});
```

#### Zustand Store Configuration
```typescript
// stores/app-store.ts
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

interface AppState {
  // UI State
  isOffline: boolean;
  isSyncing: boolean;
  sidebarOpen: boolean;
  
  // User Preferences
  theme: 'light' | 'dark' | 'system';
  language: string;
  descriptionStyle: DescriptionStyle;
  vocabularyLevel: VocabularyLevel;
  
  // Current Session
  currentSessionId: string | null;
  searchQuery: string;
  selectedImage: ImageData | null;
  
  // Offline Queue
  pendingMutations: Array<PendingMutation>;
  
  // Actions
  setOfflineStatus: (isOffline: boolean) => void;
  setSyncStatus: (isSyncing: boolean) => void;
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
  updatePreferences: (preferences: Partial<UserPreferences>) => void;
  queueMutation: (mutation: PendingMutation) => void;
  processPendingMutations: () => Promise<void>;
}

export const useAppStore = create<AppState>()(
  devtools(
    persist(
      immer((set, get) => ({
        // Initial state
        isOffline: false,
        isSyncing: false,
        sidebarOpen: true,
        theme: 'system',
        language: 'en',
        descriptionStyle: 'academic',
        vocabularyLevel: 'intermediate',
        currentSessionId: null,
        searchQuery: '',
        selectedImage: null,
        pendingMutations: [],
        
        // Actions implementation
        setOfflineStatus: (isOffline) => set({ isOffline }),
        setSyncStatus: (isSyncing) => set({ isSyncing }),
        setTheme: (theme) => set({ theme }),
        
        updatePreferences: (preferences) => set((state) => {
          Object.assign(state, preferences);
        }),
        
        queueMutation: (mutation) => set((state) => {
          state.pendingMutations.push(mutation);
        }),
        
        processPendingMutations: async () => {
          // Implementation for processing offline mutations
        },
      })),
      {
        name: 'vocabulary-app-storage',
        partialize: (state) => ({
          theme: state.theme,
          language: state.language,
          descriptionStyle: state.descriptionStyle,
          vocabularyLevel: state.vocabularyLevel,
          pendingMutations: state.pendingMutations,
        }),
      }
    ),
    { name: 'VocabularyApp' }
  )
);
```

### 4.3 PWA Configuration

#### Service Worker with Workbox
```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/images\.unsplash\.com\/.*/i,
            handler: 'CacheFirst',
            options: {
              cacheName: 'unsplash-images',
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 30 * 24 * 60 * 60, // 30 days
              },
            },
          },
          {
            urlPattern: /^https:\/\/.*\.supabase\.co\/rest\/.*/i,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'supabase-api',
              networkTimeoutSeconds: 5,
              cacheableResponse: {
                statuses: [200],
              },
            },
          },
        ],
        cleanupOutdatedCaches: true,
        skipWaiting: true,
        clientsClaim: true,
      },
      includeAssets: ['favicon.ico', 'apple-touch-icon.png'],
      manifest: {
        name: 'Vocabulary Learning App',
        short_name: 'VocabApp',
        description: 'Learn Spanish vocabulary through AI-powered image descriptions',
        theme_color: '#3b82f6',
        background_color: '#ffffff',
        display: 'standalone',
        start_url: '/',
        orientation: 'portrait-primary',
        categories: ['education', 'productivity'],
        screenshots: [
          {
            src: '/screenshots/desktop.png',
            sizes: '1280x800',
            type: 'image/png',
            form_factor: 'wide',
          },
          {
            src: '/screenshots/mobile.png',
            sizes: '375x812',
            type: 'image/png',
            form_factor: 'narrow',
          },
        ],
        icons: [
          {
            src: '/icons/icon-72x72.png',
            sizes: '72x72',
            type: 'image/png',
          },
          {
            src: '/icons/icon-192x192.png',
            sizes: '192x192',
            type: 'image/png',
          },
          {
            src: '/icons/icon-512x512.png',
            sizes: '512x512',
            type: 'image/png',
          },
        ],
      },
    }),
  ],
});
```

#### Background Sync Implementation
```typescript
// lib/background-sync.ts
interface SyncData {
  type: 'vocabulary' | 'quiz' | 'description' | 'search';
  data: any;
  timestamp: number;
  retryCount: number;
}

export class BackgroundSyncManager {
  private static instance: BackgroundSyncManager;
  private syncQueue: SyncData[] = [];
  
  static getInstance() {
    if (!this.instance) {
      this.instance = new BackgroundSyncManager();
    }
    return this.instance;
  }
  
  async addToQueue(type: SyncData['type'], data: any) {
    const syncData: SyncData = {
      type,
      data,
      timestamp: Date.now(),
      retryCount: 0,
    };
    
    this.syncQueue.push(syncData);
    await this.saveQueue();
    
    if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
      const registration = await navigator.serviceWorker.ready;
      await registration.sync.register(`vocabulary-sync-${type}`);
    } else {
      // Fallback for browsers without background sync
      this.processQueue();
    }
  }
  
  async processQueue() {
    const pendingItems = [...this.syncQueue];
    
    for (const item of pendingItems) {
      try {
        await this.syncItem(item);
        this.removeFromQueue(item);
      } catch (error) {
        item.retryCount++;
        if (item.retryCount >= 3) {
          this.removeFromQueue(item);
        }
      }
    }
    
    await this.saveQueue();
  }
  
  private async syncItem(item: SyncData) {
    const supabase = createClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
    );
    
    switch (item.type) {
      case 'vocabulary':
        await supabase.from('vocabulary_items').insert(item.data);
        break;
      case 'quiz':
        await supabase.from('quiz_sessions').insert(item.data);
        break;
      // ... other sync types
    }
  }
  
  private removeFromQueue(item: SyncData) {
    const index = this.syncQueue.findIndex(i => i.timestamp === item.timestamp);
    if (index > -1) {
      this.syncQueue.splice(index, 1);
    }
  }
  
  private async saveQueue() {
    const db = await openDB('vocabulary-sync', 1, {
      upgrade(db) {
        db.createObjectStore('syncQueue');
      },
    });
    
    await db.put('syncQueue', this.syncQueue, 'queue');
  }
  
  private async loadQueue() {
    try {
      const db = await openDB('vocabulary-sync', 1);
      this.syncQueue = (await db.get('syncQueue', 'queue')) || [];
    } catch {
      this.syncQueue = [];
    }
  }
}
```

## 5. API Design

### 5.1 Supabase Edge Functions

#### Image Search Proxy
```typescript
// supabase/functions/image-search/index.ts
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

interface UnsplashResponse {
  results: Array<{
    id: string;
    urls: {
      regular: string;
      small: string;
      thumb: string;
    };
    description: string;
    alt_description: string;
    user: {
      name: string;
      username: string;
    };
    tags: Array<{ title: string }>;
    color: string;
    width: number;
    height: number;
  }>;
  total: number;
  total_pages: number;
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders });
  }

  try {
    const supabase = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    );

    // Verify user authentication
    const authHeader = req.headers.get('Authorization')!;
    const { data: { user }, error: authError } = await supabase.auth.getUser(
      authHeader.replace('Bearer ', '')
    );

    if (authError || !user) {
      throw new Error('Unauthorized');
    }

    const { query, page = 1, per_page = 10, orientation } = await req.json();

    // Rate limiting check
    const rateLimitKey = `rate_limit:${user.id}:search`;
    const { data: rateLimit } = await supabase
      .from('usage_analytics')
      .select('count(*)')
      .eq('user_id', user.id)
      .eq('event_type', 'image_search')
      .gte('created_at', new Date(Date.now() - 60 * 60 * 1000).toISOString());

    if (rateLimit && rateLimit.length > 60) { // 60 searches per hour
      throw new Error('Rate limit exceeded');
    }

    // Check cache first
    const { data: cachedResults } = await supabase
      .from('cached_images')
      .select('*')
      .textSearch('tags', query)
      .range((page - 1) * per_page, page * per_page - 1);

    if (cachedResults && cachedResults.length >= per_page) {
      return new Response(JSON.stringify({
        results: cachedResults,
        cached: true,
      }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }

    // Fetch from Unsplash API
    const unsplashUrl = new URL('https://api.unsplash.com/search/photos');
    unsplashUrl.searchParams.set('query', query);
    unsplashUrl.searchParams.set('page', page.toString());
    unsplashUrl.searchParams.set('per_page', per_page.toString());
    if (orientation) unsplashUrl.searchParams.set('orientation', orientation);

    const response = await fetch(unsplashUrl.toString(), {
      headers: {
        'Authorization': `Client-ID ${Deno.env.get('UNSPLASH_ACCESS_KEY')}`,
      },
    });

    if (!response.ok) {
      throw new Error(`Unsplash API error: ${response.status}`);
    }

    const data: UnsplashResponse = await response.json();

    // Cache images for future use
    const imagesToCache = data.results.map(image => ({
      unsplash_id: image.id,
      url_regular: image.urls.regular,
      url_small: image.urls.small,
      url_thumb: image.urls.thumb,
      description: image.description,
      alt_description: image.alt_description,
      tags: image.tags.map(tag => tag.title),
      color: image.color,
      width: image.width,
      height: image.height,
      photographer_name: image.user.name,
      photographer_username: image.user.username,
      cache_expires_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
    }));

    await supabase.from('cached_images').upsert(imagesToCache);

    // Log search analytics
    await supabase.from('usage_analytics').insert({
      user_id: user.id,
      event_type: 'image_search',
      event_data: { query, page, results_count: data.results.length },
    });

    return new Response(JSON.stringify(data), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });

  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 400,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  }
});
```

#### AI Description Streaming
```typescript
// supabase/functions/ai-description/index.ts
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders });
  }

  try {
    const supabase = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    );

    const authHeader = req.headers.get('Authorization')!;
    const { data: { user } } = await supabase.auth.getUser(
      authHeader.replace('Bearer ', '')
    );

    if (!user) throw new Error('Unauthorized');

    const { imageUrl, style, level, context, sessionId } = await req.json();

    // Rate limiting for AI generation (more restrictive)
    const { data: recentGenerations } = await supabase
      .from('ai_descriptions')
      .select('count(*)')
      .eq('user_id', user.id)
      .gte('created_at', new Date(Date.now() - 60 * 60 * 1000).toISOString());

    if (recentGenerations && recentGenerations.length > 20) {
      throw new Error('AI generation rate limit exceeded');
    }

    // Build style-specific prompt
    const prompt = buildDescriptionPrompt(style, level, context);

    // Stream response from OpenAI
    const openAIResponse = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${Deno.env.get('OPENAI_API_KEY')}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'gpt-4-vision-preview',
        messages: [{
          role: 'user',
          content: [
            { type: 'text', text: prompt },
            { type: 'image_url', image_url: { url: imageUrl, detail: 'high' } }
          ]
        }],
        max_tokens: 600,
        temperature: 0.7,
        stream: true,
      }),
    });

    if (!openAIResponse.ok) {
      throw new Error(`OpenAI API error: ${openAIResponse.status}`);
    }

    // Create streaming response
    const encoder = new TextEncoder();
    const decoder = new TextDecoder();
    let fullContent = '';
    let tokenCount = 0;
    const startTime = Date.now();

    const stream = new ReadableStream({
      async start(controller) {
        try {
          const reader = openAIResponse.body?.getReader();
          if (!reader) throw new Error('No response body');

          while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');

            for (const line of lines) {
              if (line.startsWith('data: ')) {
                const data = line.slice(6);
                if (data === '[DONE]') continue;

                try {
                  const parsed = JSON.parse(data);
                  const delta = parsed.choices?.[0]?.delta?.content || '';
                  if (delta) {
                    fullContent += delta;
                    tokenCount++;
                    controller.enqueue(encoder.encode(`data: ${JSON.stringify({
                      content: delta,
                      fullContent,
                      tokenCount,
                    })}\n\n`));
                  }
                } catch {
                  // Skip invalid JSON
                }
              }
            }
          }

          // Save completed description to database
          await supabase.from('ai_descriptions').insert({
            user_id: user.id,
            session_id: sessionId,
            content: fullContent,
            style,
            vocabulary_level: level,
            word_count: fullContent.split(' ').length,
            model_used: 'gpt-4-vision-preview',
            generation_time_ms: Date.now() - startTime,
            completion_tokens: tokenCount,
          });

          controller.enqueue(encoder.encode('data: [DONE]\n\n'));
          controller.close();

        } catch (error) {
          controller.error(error);
        }
      },
    });

    return new Response(stream, {
      headers: {
        ...corsHeaders,
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      },
    });

  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 400,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  }
});

function buildDescriptionPrompt(style: string, level: string, context: string): string {
  const basePrompt = "Analiza esta imagen y descríbela en español latinoamericano.";
  
  const styleInstructions = {
    academic: "Usa un tono formal y académico con vocabulario preciso.",
    poetic: "Usa un lenguaje poético y expresivo con metáforas y sensaciones.",
    technical: "Enfócate en aspectos técnicos, materiales, y especificaciones.",
  };
  
  const levelInstructions = {
    beginner: "Usa vocabulario básico y estructuras simples.",
    intermediate: "Usa vocabulario intermedio con algunas expresiones avanzadas.",
    advanced: "Usa vocabulario sofisticado y estructuras complejas.",
    native: "Usa el nivel más alto de español con expresiones idiomáticas.",
  };
  
  return `${basePrompt}\n\n${styleInstructions[style]}\n${levelInstructions[level]}\n\n${context ? `Contexto adicional: ${context}` : ''}`;
}
```

### 5.2 Client-Side API Layer

```typescript
// lib/api/index.ts
import { createClient } from '@supabase/supabase-js';
import { Database } from '../types/database';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL!;
const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY!;

export const supabase = createClient<Database>(supabaseUrl, supabaseKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
  },
  realtime: {
    params: {
      eventsPerSecond: 10,
    },
  },
});

// API client with error handling and retries
export class APIClient {
  private static instance: APIClient;
  
  static getInstance() {
    if (!this.instance) {
      this.instance = new APIClient();
    }
    return this.instance;
  }
  
  async searchImages(params: SearchImageParams): Promise<SearchImageResponse> {
    const { data, error } = await supabase.functions.invoke('image-search', {
      body: params,
    });
    
    if (error) throw new Error(error.message);
    return data;
  }
  
  async generateDescription(params: GenerateDescriptionParams): Promise<ReadableStream> {
    const { data, error } = await supabase.functions.invoke('ai-description', {
      body: params,
    });
    
    if (error) throw new Error(error.message);
    return data;
  }
  
  async createVocabularyItem(item: CreateVocabularyItemParams): Promise<VocabularyItem> {
    const { data, error } = await supabase
      .from('vocabulary_items')
      .insert(item)
      .select()
      .single();
    
    if (error) throw new Error(error.message);
    return data;
  }
  
  async getUserVocabulary(userId: string, filters?: VocabularyFilters): Promise<VocabularyItem[]> {
    let query = supabase
      .from('vocabulary_items')
      .select('*')
      .eq('user_id', userId);
    
    if (filters?.search) {
      query = query.or(`spanish_word.ilike.%${filters.search}%,english_translation.ilike.%${filters.search}%`);
    }
    
    if (filters?.difficulty) {
      query = query.eq('difficulty_level', filters.difficulty);
    }
    
    const { data, error } = await query.order('created_at', { ascending: false });
    
    if (error) throw new Error(error.message);
    return data || [];
  }
  
  // Real-time subscriptions
  subscribeToVocabularyUpdates(userId: string, callback: (payload: any) => void) {
    return supabase
      .channel('vocabulary_updates')
      .on('postgres_changes', {
        event: '*',
        schema: 'public',
        table: 'vocabulary_items',
        filter: `user_id=eq.${userId}`,
      }, callback)
      .subscribe();
  }
}
```

## 6. Offline Capabilities

### 6.1 IndexedDB Schema
```typescript
// lib/offline-db.ts
import Dexie, { Table } from 'dexie';
import { VocabularyItem, SearchSession, AIDescription } from '../types';

export interface CachedImage {
  id?: number;
  unsplashId: string;
  urlRegular: string;
  urlSmall: string;
  urlThumb: string;
  blob?: Blob;
  cachedAt: Date;
}

export interface PendingSync {
  id?: number;
  type: 'vocabulary' | 'session' | 'description';
  action: 'create' | 'update' | 'delete';
  data: any;
  createdAt: Date;
  retryCount: number;
}

class OfflineDatabase extends Dexie {
  vocabularyItems!: Table<VocabularyItem>;
  searchSessions!: Table<SearchSession>;
  aiDescriptions!: Table<AIDescription>;
  cachedImages!: Table<CachedImage>;
  pendingSync!: Table<PendingSync>;

  constructor() {
    super('VocabularyAppDB');
    
    this.version(1).stores({
      vocabularyItems: '++id, userId, spanishWord, englishTranslation, sessionId, createdAt',
      searchSessions: '++id, userId, query, createdAt',
      aiDescriptions: '++id, userId, sessionId, content, style, createdAt',
      cachedImages: '++id, unsplashId, cachedAt',
      pendingSync: '++id, type, createdAt, retryCount',
    });

    // Add indexes for offline search
    this.version(2).stores({
      vocabularyItems: '++id, userId, spanishWord, englishTranslation, sessionId, createdAt, [userId+spanishWord]',
      searchSessions: '++id, userId, query, createdAt, [userId+query]',
      aiDescriptions: '++id, userId, sessionId, content, style, createdAt, [userId+sessionId]',
      cachedImages: '++id, unsplashId, cachedAt',
      pendingSync: '++id, type, createdAt, retryCount',
    });
  }
}

export const offlineDB = new OfflineDatabase();

// Offline-first data access layer
export class OfflineDataManager {
  async getVocabulary(userId: string): Promise<VocabularyItem[]> {
    return await offlineDB.vocabularyItems
      .where('userId')
      .equals(userId)
      .reverse()
      .sortBy('createdAt');
  }
  
  async addVocabulary(item: VocabularyItem): Promise<void> {
    // Add to local database
    await offlineDB.vocabularyItems.add(item);
    
    // Queue for sync
    await this.queueForSync('vocabulary', 'create', item);
  }
  
  async searchVocabulary(userId: string, query: string): Promise<VocabularyItem[]> {
    const lowerQuery = query.toLowerCase();
    return await offlineDB.vocabularyItems
      .where('userId')
      .equals(userId)
      .filter(item => 
        item.spanishWord.toLowerCase().includes(lowerQuery) ||
        item.englishTranslation.toLowerCase().includes(lowerQuery)
      )
      .toArray();
  }
  
  async cacheImage(unsplashId: string, url: string): Promise<void> {
    try {
      const response = await fetch(url);
      const blob = await response.blob();
      
      await offlineDB.cachedImages.put({
        unsplashId,
        urlRegular: url,
        urlSmall: url,
        urlThumb: url,
        blob,
        cachedAt: new Date(),
      });
    } catch (error) {
      console.warn('Failed to cache image:', error);
    }
  }
  
  async getCachedImage(unsplashId: string): Promise<string | null> {
    const cached = await offlineDB.cachedImages
      .where('unsplashId')
      .equals(unsplashId)
      .first();
    
    if (cached?.blob) {
      return URL.createObjectURL(cached.blob);
    }
    
    return null;
  }
  
  private async queueForSync(type: PendingSync['type'], action: PendingSync['action'], data: any): Promise<void> {
    await offlineDB.pendingSync.add({
      type,
      action,
      data,
      createdAt: new Date(),
      retryCount: 0,
    });
  }
  
  async processPendingSync(): Promise<void> {
    const pending = await offlineDB.pendingSync.toArray();
    
    for (const item of pending) {
      try {
        await this.syncItem(item);
        await offlineDB.pendingSync.delete(item.id!);
      } catch (error) {
        // Increment retry count
        await offlineDB.pendingSync.update(item.id!, {
          retryCount: item.retryCount + 1,
        });
        
        // Remove if too many retries
        if (item.retryCount >= 3) {
          await offlineDB.pendingSync.delete(item.id!);
        }
      }
    }
  }
  
  private async syncItem(item: PendingSync): Promise<void> {
    const apiClient = APIClient.getInstance();
    
    switch (`${item.type}_${item.action}`) {
      case 'vocabulary_create':
        await apiClient.createVocabularyItem(item.data);
        break;
      // Add other sync cases
    }
  }
}

export const offlineDataManager = new OfflineDataManager();
```

### 6.2 Network Status Management
```typescript
// hooks/use-network-status.ts
import { useState, useEffect } from 'react';
import { useAppStore } from '../stores/app-store';

export function useNetworkStatus() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const { setOfflineStatus } = useAppStore();

  useEffect(() => {
    function handleOnline() {
      setIsOnline(true);
      setOfflineStatus(false);
    }

    function handleOffline() {
      setIsOnline(false);
      setOfflineStatus(true);
    }

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [setOfflineStatus]);

  return isOnline;
}
```

## 7. Deployment Architecture

### 7.1 Vercel Deployment Configuration

```json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "buildCommand": "npm run build"
      }
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ],
  "headers": [
    {
      "source": "/sw.js",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "no-cache"
        }
      ]
    },
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        }
      ]
    }
  ],
  "env": {
    "VITE_SUPABASE_URL": "@supabase-url",
    "VITE_SUPABASE_ANON_KEY": "@supabase-anon-key"
  }
}
```

### 7.2 Environment Configuration
```env
# .env.example
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
VITE_POSTHOG_KEY=your-posthog-key
VITE_SENTRY_DSN=your-sentry-dsn
VITE_APP_VERSION=1.0.0
VITE_FEATURE_FLAGS=offline_sync:true,real_time:true
```

### 7.3 Supabase Configuration
```sql
-- Setup.sql for Supabase project initialization
-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Enable RLS by default
ALTER DATABASE postgres SET row_security = on;

-- Create storage buckets
INSERT INTO storage.buckets (id, name, public) 
VALUES 
  ('avatars', 'avatars', true),
  ('images', 'images', false);

-- Storage policies
CREATE POLICY "Users can upload their avatars" ON storage.objects
  FOR INSERT WITH CHECK (bucket_id = 'avatars' AND auth.uid()::text = (storage.foldername(name))[1]);

CREATE POLICY "Users can view all avatars" ON storage.objects
  FOR SELECT USING (bucket_id = 'avatars');

-- Enable real-time for specific tables
ALTER PUBLICATION supabase_realtime ADD TABLE public.vocabulary_items;
ALTER PUBLICATION supabase_realtime ADD TABLE public.shared_lists;
ALTER PUBLICATION supabase_realtime ADD TABLE public.quiz_sessions;
```

## 8. Security Architecture

### 8.1 Security Principles
1. **Zero Trust Architecture**: Verify every request
2. **Defense in Depth**: Multiple security layers
3. **Principle of Least Privilege**: Minimal required permissions
4. **Data Encryption**: At rest and in transit
5. **Audit Logging**: Comprehensive activity tracking

### 8.2 Authentication & Authorization Flow
```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────┐
│   Client    │───▶│    Vercel    │───▶│  Supabase   │───▶│ PostgreSQL   │
│   (React)   │    │   (Edge)     │    │   (Auth)    │    │   (RLS)      │
└─────────────┘    └──────────────┘    └─────────────┘    └──────────────┘
       │                    │                    │                    │
       │ 1. Login Request   │ 2. Verify JWT     │ 3. Check RLS       │
       │                    │                    │                    │
       │ 4. Access Token ◄──│ 5. Valid User ◄───│ 6. Authorized ◄────│
       │                    │                    │                    │
```

### 8.3 Content Security Policy
```typescript
// middleware.ts (Vercel Edge)
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const response = NextResponse.next();
  
  // Security headers
  response.headers.set('X-DNS-Prefetch-Control', 'off');
  response.headers.set('X-Frame-Options', 'DENY');
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  response.headers.set('Permissions-Policy', 'camera=(), microphone=(), geolocation=()');
  
  // CSP
  const csp = [
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net",
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
    "font-src 'self' https://fonts.gstatic.com",
    "img-src 'self' data: blob: https://images.unsplash.com https://*.supabase.co",
    "connect-src 'self' https://*.supabase.co wss://*.supabase.co https://api.openai.com https://api.unsplash.com",
    "worker-src 'self' blob:",
    "object-src 'none'",
    "base-uri 'self'",
    "form-action 'self'",
    "frame-ancestors 'none'",
  ].join('; ');
  
  response.headers.set('Content-Security-Policy', csp);
  
  return response;
}

export const config = {
  matcher: [
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};
```

## 9. Cost Analysis

### 9.1 Cost Breakdown by User Scale

#### 1,000 Monthly Active Users
```
Vercel (Hobby/Pro):
- Hosting: $20/month (Pro plan)
- Edge Functions: ~$5/month (limited usage)
- Bandwidth: Included in plan

Supabase (Pro):
- Database: $25/month (included 8GB storage)
- Auth: Included
- Storage: $0.021/GB (minimal usage: ~$2)
- Edge Functions: $2/100K invocations (~$10)

OpenAI API:
- Descriptions: 10K descriptions × $0.01 = $100
- Translations: 5K translations × $0.002 = $10

Third-party Services:
- PostHog: $0 (under 1M events)
- Sentry: $26/month (small team plan)

Monthly Total: ~$198
Cost per user: ~$0.20
```

#### 10,000 Monthly Active Users
```
Vercel (Team):
- Hosting: $50/month (Team plan)
- Edge Functions: ~$30/month
- Bandwidth: ~$20/month

Supabase (Pro):
- Database: $50/month (16GB storage)
- Auth: $0.00325/MAU (10K × $0.00325) = $33
- Storage: ~$10/month (500GB images)
- Edge Functions: $2/100K × 5 = $100

OpenAI API:
- Descriptions: 100K descriptions × $0.01 = $1,000
- Translations: 50K translations × $0.002 = $100

Third-party Services:
- PostHog: $450/month (10M events)
- Sentry: $80/month (team plan)

Monthly Total: ~$1,923
Cost per user: ~$0.19
```

#### 100,000 Monthly Active Users
```
Vercel (Enterprise):
- Hosting: $500/month (custom enterprise)
- Edge Functions: ~$200/month
- Bandwidth: ~$150/month

Supabase (Team/Enterprise):
- Database: $599/month (custom plan)
- Auth: 100K × $0.00325 = $325
- Storage: ~$100/month (5TB images)
- Edge Functions: $2/100K × 50 = $1,000

OpenAI API:
- Descriptions: 1M descriptions × $0.01 = $10,000
- Translations: 500K translations × $0.002 = $1,000

Third-party Services:
- PostHog: $2,000/month (100M events)
- Sentry: $200/month (large team)

CDN/Performance:
- Cloudflare Pro: $20/month
- Image optimization: ~$300/month

Monthly Total: ~$16,394
Cost per user: ~$0.16
```

### 9.2 Cost Optimization Strategies

1. **Caching Strategy**:
   - Edge caching for static assets
   - Database query result caching
   - Image CDN with long TTL
   - Service Worker caching

2. **API Optimization**:
   - Batch API requests where possible
   - Implement request deduplication
   - Use cheaper models for simple tasks
   - Cache AI-generated content

3. **Infrastructure Optimization**:
   - Implement proper database indexing
   - Use database connection pooling
   - Optimize bundle size for faster loads
   - Implement lazy loading for components

4. **Feature Scaling**:
   - Implement usage-based feature access
   - Progressive feature unlocking
   - Smart quota management
   - Background processing for non-critical tasks

## 10. Monitoring and Analytics

### 10.1 Performance Monitoring
```typescript
// lib/monitoring.ts
import * as Sentry from '@sentry/react';
import { BrowserTracing } from '@sentry/tracing';
import posthog from 'posthog-js';

// Initialize Sentry
Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN,
  integrations: [
    new BrowserTracing({
      tracePropagationTargets: [
        'localhost',
        /^https:\/\/.*\.supabase\.co/,
      ],
    }),
  ],
  tracesSampleRate: 0.1,
  environment: import.meta.env.MODE,
});

// Initialize PostHog
posthog.init(import.meta.env.VITE_POSTHOG_KEY, {
  api_host: 'https://app.posthog.com',
  autocapture: false, // We'll track events manually
  capture_pageview: false, // We'll handle this in React
});

// Performance monitoring utilities
export class PerformanceMonitor {
  static startTransaction(name: string) {
    return Sentry.startTransaction({ name });
  }

  static trackPageView(path: string) {
    posthog.capture('$pageview', { $current_url: path });
  }

  static trackUserAction(action: string, properties?: Record<string, any>) {
    posthog.capture(action, properties);
  }

  static trackError(error: Error, context?: Record<string, any>) {
    Sentry.captureException(error, { contexts: { custom: context } });
  }

  static setUser(user: { id: string; email?: string }) {
    Sentry.setUser(user);
    posthog.identify(user.id, user);
  }
}

// React component for performance tracking
export function withPerformanceTracking<T extends {}>(
  Component: React.ComponentType<T>,
  componentName: string
) {
  return function PerformanceTrackedComponent(props: T) {
    useEffect(() => {
      const transaction = PerformanceMonitor.startTransaction(`Component: ${componentName}`);
      
      return () => {
        transaction.finish();
      };
    }, []);

    return <Component {...props} />;
  };
}
```

### 10.2 Business Metrics Dashboard
```typescript
// components/AdminDashboard.tsx
interface MetricData {
  activeUsers: number;
  totalSessions: number;
  vocabularyItemsCreated: number;
  aiDescriptionsGenerated: number;
  quizzesCompleted: number;
  averageSessionDuration: number;
  retentionRate: number;
  errorRate: number;
}

export function AdminDashboard() {
  const { data: metrics } = useQuery({
    queryKey: ['admin-metrics'],
    queryFn: async () => {
      const { data } = await supabase.rpc('get_admin_metrics');
      return data as MetricData;
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <MetricCard
        title="Active Users"
        value={metrics?.activeUsers || 0}
        change="+12%"
        icon={<Users className="h-5 w-5" />}
      />
      <MetricCard
        title="Vocabulary Items"
        value={metrics?.vocabularyItemsCreated || 0}
        change="+8%"
        icon={<BookOpen className="h-5 w-5" />}
      />
      <MetricCard
        title="AI Descriptions"
        value={metrics?.aiDescriptionsGenerated || 0}
        change="+15%"
        icon={<Sparkles className="h-5 w-5" />}
      />
      <MetricCard
        title="Retention Rate"
        value={`${metrics?.retentionRate || 0}%`}
        change="+3%"
        icon={<TrendingUp className="h-5 w-5" />}
      />
    </div>
  );
}
```

## 11. Migration Strategy

### 11.1 Data Migration from Desktop App
```typescript
// scripts/migrate-desktop-data.ts
import { createClient } from '@supabase/supabase-js';
import { parse } from 'csv-parse/sync';
import { readFileSync } from 'fs';

interface DesktopVocabularyEntry {
  Spanish: string;
  English: string;
  Date: string;
  'Search Query': string;
  'Image URL': string;
  Context: string;
}

async function migrateVocabularyData(userId: string, csvFilePath: string) {
  const supabase = createClient(
    process.env.SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!
  );

  const csvContent = readFileSync(csvFilePath, 'utf-8');
  const records: DesktopVocabularyEntry[] = parse(csvContent, {
    columns: true,
    skip_empty_lines: true,
  });

  const vocabularyItems = records.map(record => ({
    user_id: userId,
    spanish_word: record.Spanish,
    english_translation: record.English,
    context_sentence: record.Context,
    image_url: record['Image URL'],
    search_query: record['Search Query'],
    created_at: new Date(record.Date).toISOString(),
  }));

  // Batch insert to avoid rate limits
  const batchSize = 100;
  for (let i = 0; i < vocabularyItems.length; i += batchSize) {
    const batch = vocabularyItems.slice(i, i + batchSize);
    const { error } = await supabase
      .from('vocabulary_items')
      .insert(batch);
    
    if (error) {
      console.error(`Error inserting batch ${i}-${i + batchSize}:`, error);
    } else {
      console.log(`Migrated batch ${i}-${i + batchSize} successfully`);
    }
  }
}

// Usage
// migrateVocabularyData('user-uuid', 'path/to/vocabulary.csv');
```

### 11.2 Feature Parity Checklist
- [ ] Image search with Unsplash API
- [ ] AI-powered Spanish descriptions with GPT-4
- [ ] Interactive clickable text for vocabulary learning
- [ ] Vocabulary management and storage
- [ ] Quiz system with different question types
- [ ] CSV export functionality
- [ ] Session tracking and statistics
- [ ] Multiple description styles (academic, poetic, technical)
- [ ] Different vocabulary levels (beginner to native)
- [ ] Offline functionality
- [ ] Real-time synchronization
- [ ] Multi-device support
- [ ] Social features (shared lists)
- [ ] Advanced analytics

## 12. Future Enhancements

### 12.1 Phase 2 Features
1. **Advanced AI Features**:
   - Speech synthesis for pronunciation
   - Image recognition for vocabulary suggestions
   - Personalized learning paths
   - Spaced repetition algorithms

2. **Social Learning**:
   - Study groups and challenges
   - Leaderboards and achievements
   - Peer review of vocabulary lists
   - Community-generated content

3. **Mobile Native Features**:
   - Camera integration for real-world vocabulary
   - Offline speech recognition
   - Push notifications for study reminders
   - Widget for home screen vocabulary

4. **Enterprise Features**:
   - Teacher dashboards
   - Classroom management
   - Progress analytics
   - Custom branding

### 12.2 Technical Improvements
1. **Performance Optimizations**:
   - Service Worker optimization
   - Database query optimization
   - Image lazy loading and optimization
   - Bundle splitting and code splitting

2. **Developer Experience**:
   - Comprehensive testing suite
   - CI/CD pipeline improvements
   - Documentation generation
   - Development tools and debugging

3. **Accessibility**:
   - Screen reader compatibility
   - Keyboard navigation
   - High contrast mode
   - Multi-language UI support

## Conclusion

This PWA architecture design provides a comprehensive, scalable, and maintainable solution for migrating the desktop Unsplash image search application to a modern web platform. The architecture emphasizes:

1. **Progressive Enhancement**: Works offline-first with online enhancements
2. **Scalability**: Handles growth from 1K to 100K+ users efficiently
3. **Security**: Zero-trust architecture with comprehensive policies
4. **Performance**: Optimized for speed and user experience
5. **Maintainability**: Clean, type-safe, and well-documented codebase

The estimated development timeline is 12-16 weeks for the initial release, with costs ranging from $0.16-0.20 per user depending on scale. The architecture supports both B2C and B2B use cases with enterprise-ready features and comprehensive analytics.

This foundation enables future enhancements while maintaining system integrity and user experience quality throughout the application's lifecycle.