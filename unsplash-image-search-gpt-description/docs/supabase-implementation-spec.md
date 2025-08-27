# Supabase Implementation Specifications for Vocabulary Learning PWA

## Project Overview

This document provides complete Supabase implementation specifications for migrating the Unsplash Image Search & GPT Description desktop application to a Progressive Web App (PWA) with cloud backend capabilities.

## Current Application Analysis

Based on the existing desktop application:
- **Core Function**: Image search with AI-generated Spanish descriptions
- **Key Features**: Vocabulary extraction, clickable text translation, quiz system
- **Data Models**: Users, vocabulary entries, sessions, images, quizzes
- **APIs**: Unsplash (images), OpenAI (descriptions/translations)

## 1. Database Schema (PostgreSQL)

### Core Tables

```sql
-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Users table (extends auth.users)
CREATE TABLE public.profiles (
  id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
  username TEXT UNIQUE,
  email TEXT UNIQUE NOT NULL,
  full_name TEXT,
  avatar_url TEXT,
  language_preferences JSONB DEFAULT '{"native": "en", "learning": "es", "level": "intermediate"}'::jsonb,
  subscription_tier TEXT DEFAULT 'free' CHECK (subscription_tier IN ('free', 'premium', 'pro')),
  api_quotas JSONB DEFAULT '{"images_per_day": 50, "descriptions_per_day": 25, "translations_per_day": 100}'::jsonb,
  preferences JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vocabulary entries
CREATE TABLE public.vocabulary (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
  spanish_text TEXT NOT NULL,
  english_translation TEXT NOT NULL,
  context TEXT, -- Original sentence/context where found
  difficulty_level TEXT DEFAULT 'intermediate' CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced', 'native')),
  word_type TEXT DEFAULT 'unknown' CHECK (word_type IN ('noun', 'verb', 'adjective', 'phrase', 'expression', 'unknown')),
  
  -- Learning metrics
  times_encountered INTEGER DEFAULT 1,
  times_correct INTEGER DEFAULT 0,
  times_incorrect INTEGER DEFAULT 0,
  last_reviewed TIMESTAMPTZ,
  next_review TIMESTAMPTZ,
  mastery_level INTEGER DEFAULT 0 CHECK (mastery_level >= 0 AND mastery_level <= 5),
  
  -- Source information
  source_type TEXT DEFAULT 'description' CHECK (source_type IN ('description', 'manual', 'import', 'shared')),
  source_image_id UUID,
  source_session_id UUID,
  
  -- Metadata
  tags TEXT[] DEFAULT '{}',
  notes TEXT,
  is_favorite BOOLEAN DEFAULT FALSE,
  is_archived BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Images and descriptions
CREATE TABLE public.images (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
  unsplash_id TEXT UNIQUE NOT NULL,
  unsplash_url TEXT NOT NULL,
  thumbnail_url TEXT NOT NULL,
  alt_description TEXT,
  photographer TEXT,
  photographer_url TEXT,
  
  -- Search context
  search_query TEXT NOT NULL,
  search_timestamp TIMESTAMPTZ DEFAULT NOW(),
  
  -- AI-generated content
  ai_description TEXT,
  description_style TEXT DEFAULT 'academic' CHECK (description_style IN ('academic', 'poetic', 'technical', 'conversational')),
  vocabulary_level TEXT DEFAULT 'intermediate',
  
  -- Usage tracking
  times_used INTEGER DEFAULT 1,
  last_accessed TIMESTAMPTZ DEFAULT NOW(),
  
  -- Metadata
  is_favorite BOOLEAN DEFAULT FALSE,
  is_public BOOLEAN DEFAULT FALSE,
  tags TEXT[] DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT fk_source_image FOREIGN KEY (id) REFERENCES public.vocabulary(source_image_id) ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED
);

-- Learning sessions
CREATE TABLE public.learning_sessions (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
  session_type TEXT DEFAULT 'study' CHECK (session_type IN ('study', 'quiz', 'review', 'practice')),
  
  -- Session configuration
  target_vocabulary_count INTEGER DEFAULT 10,
  difficulty_level TEXT DEFAULT 'mixed',
  focus_areas TEXT[] DEFAULT '{}', -- ['verbs', 'nouns', 'phrases']
  
  -- Progress tracking
  started_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  duration_seconds INTEGER,
  items_studied INTEGER DEFAULT 0,
  items_correct INTEGER DEFAULT 0,
  items_incorrect INTEGER DEFAULT 0,
  completion_percentage DECIMAL(5,2) DEFAULT 0.0,
  
  -- Performance metrics
  average_response_time DECIMAL(8,3), -- in seconds
  streak_count INTEGER DEFAULT 0,
  accuracy_rate DECIMAL(5,2),
  
  -- Metadata
  notes TEXT,
  session_data JSONB DEFAULT '{}'::jsonb, -- Flexible session-specific data
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Quiz attempts and results
CREATE TABLE public.quiz_attempts (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
  session_id UUID REFERENCES public.learning_sessions(id) ON DELETE CASCADE,
  
  -- Quiz configuration
  quiz_type TEXT DEFAULT 'translation' CHECK (quiz_type IN ('translation', 'multiple_choice', 'fill_blank', 'audio', 'mixed')),
  vocabulary_ids UUID[] NOT NULL, -- Array of vocabulary IDs included
  
  -- Results
  score INTEGER NOT NULL,
  max_score INTEGER NOT NULL,
  percentage DECIMAL(5,2) GENERATED ALWAYS AS ((score::DECIMAL / max_score::DECIMAL) * 100) STORED,
  time_taken_seconds INTEGER,
  
  -- Detailed results
  question_results JSONB NOT NULL, -- Array of question results with timing
  mistakes_analysis JSONB DEFAULT '{}'::jsonb,
  
  started_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vocabulary collections/lists
CREATE TABLE public.vocabulary_collections (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  
  -- Sharing and collaboration
  is_public BOOLEAN DEFAULT FALSE,
  is_collaborative BOOLEAN DEFAULT FALSE,
  share_code TEXT UNIQUE, -- Generated code for sharing
  
  -- Metadata
  vocabulary_count INTEGER DEFAULT 0,
  total_studies INTEGER DEFAULT 0,
  average_mastery DECIMAL(3,2) DEFAULT 0.0,
  
  tags TEXT[] DEFAULT '{}',
  color_theme TEXT DEFAULT '#3B82F6',
  icon TEXT DEFAULT 'book',
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Many-to-many relationship between vocabulary and collections
CREATE TABLE public.vocabulary_collection_items (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  collection_id UUID REFERENCES public.vocabulary_collections(id) ON DELETE CASCADE NOT NULL,
  vocabulary_id UUID REFERENCES public.vocabulary(id) ON DELETE CASCADE NOT NULL,
  added_at TIMESTAMPTZ DEFAULT NOW(),
  added_by UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
  sort_order INTEGER DEFAULT 0,
  
  UNIQUE(collection_id, vocabulary_id)
);

-- User activity and analytics
CREATE TABLE public.user_activity (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
  activity_type TEXT NOT NULL CHECK (activity_type IN ('login', 'search', 'description_generated', 'vocabulary_added', 'quiz_completed', 'session_started')),
  
  -- Activity details
  details JSONB DEFAULT '{}'::jsonb,
  ip_address INET,
  user_agent TEXT,
  
  -- Performance tracking
  response_time_ms INTEGER,
  success BOOLEAN DEFAULT TRUE,
  error_message TEXT,
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Shared vocabulary marketplace (future feature)
CREATE TABLE public.shared_vocabulary_sets (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  creator_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
  title TEXT NOT NULL,
  description TEXT,
  language_pair TEXT DEFAULT 'es-en',
  difficulty_level TEXT DEFAULT 'intermediate',
  category TEXT,
  
  -- Content
  vocabulary_data JSONB NOT NULL, -- Flattened vocabulary entries
  sample_images TEXT[], -- URLs to sample images
  
  -- Community features
  downloads_count INTEGER DEFAULT 0,
  rating DECIMAL(3,2) DEFAULT 0.0,
  reviews_count INTEGER DEFAULT 0,
  
  -- Moderation
  is_approved BOOLEAN DEFAULT FALSE,
  is_featured BOOLEAN DEFAULT FALSE,
  moderated_at TIMESTAMPTZ,
  moderated_by UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add foreign key constraint for images (deferred to avoid circular dependency)
ALTER TABLE public.vocabulary ADD CONSTRAINT fk_source_image 
  FOREIGN KEY (source_image_id) REFERENCES public.images(id) ON DELETE SET NULL
  DEFERRABLE INITIALLY DEFERRED;
```

### Indexes for Performance

```sql
-- Core performance indexes
CREATE INDEX idx_profiles_username ON public.profiles(username);
CREATE INDEX idx_profiles_subscription_tier ON public.profiles(subscription_tier);

-- Vocabulary indexes
CREATE INDEX idx_vocabulary_user_id ON public.vocabulary(user_id);
CREATE INDEX idx_vocabulary_user_spanish ON public.vocabulary(user_id, spanish_text);
CREATE INDEX idx_vocabulary_mastery_level ON public.vocabulary(user_id, mastery_level);
CREATE INDEX idx_vocabulary_next_review ON public.vocabulary(next_review) WHERE next_review IS NOT NULL;
CREATE INDEX idx_vocabulary_tags ON public.vocabulary USING GIN(tags);
CREATE INDEX idx_vocabulary_difficulty ON public.vocabulary(difficulty_level, user_id);

-- Images indexes
CREATE INDEX idx_images_user_id ON public.images(user_id);
CREATE INDEX idx_images_search_query ON public.images(user_id, search_query);
CREATE INDEX idx_images_unsplash_id ON public.images(unsplash_id);
CREATE INDEX idx_images_tags ON public.images USING GIN(tags);
CREATE INDEX idx_images_last_accessed ON public.images(user_id, last_accessed DESC);

-- Sessions indexes
CREATE INDEX idx_sessions_user_id ON public.learning_sessions(user_id);
CREATE INDEX idx_sessions_type_user ON public.learning_sessions(session_type, user_id);
CREATE INDEX idx_sessions_started_at ON public.learning_sessions(user_id, started_at DESC);

-- Quiz attempts indexes
CREATE INDEX idx_quiz_attempts_user_id ON public.quiz_attempts(user_id);
CREATE INDEX idx_quiz_attempts_session_id ON public.quiz_attempts(session_id);
CREATE INDEX idx_quiz_attempts_completed ON public.quiz_attempts(user_id, completed_at DESC) WHERE completed_at IS NOT NULL;

-- Collections indexes
CREATE INDEX idx_collections_user_id ON public.vocabulary_collections(user_id);
CREATE INDEX idx_collections_public ON public.vocabulary_collections(is_public) WHERE is_public = TRUE;
CREATE INDEX idx_collections_share_code ON public.vocabulary_collections(share_code) WHERE share_code IS NOT NULL;

-- Activity indexes
CREATE INDEX idx_activity_user_id ON public.user_activity(user_id);
CREATE INDEX idx_activity_type_user ON public.user_activity(activity_type, user_id);
CREATE INDEX idx_activity_created_at ON public.user_activity(created_at DESC);
```

### Triggers for Updated_At Timestamps

```sql
-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all relevant tables
CREATE TRIGGER trigger_profiles_updated_at
  BEFORE UPDATE ON public.profiles
  FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER trigger_vocabulary_updated_at
  BEFORE UPDATE ON public.vocabulary
  FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER trigger_images_updated_at
  BEFORE UPDATE ON public.images
  FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER trigger_learning_sessions_updated_at
  BEFORE UPDATE ON public.learning_sessions
  FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER trigger_vocabulary_collections_updated_at
  BEFORE UPDATE ON public.vocabulary_collections
  FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER trigger_shared_vocabulary_sets_updated_at
  BEFORE UPDATE ON public.shared_vocabulary_sets
  FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();
```

### Useful Views

```sql
-- User vocabulary statistics view
CREATE OR REPLACE VIEW public.user_vocabulary_stats AS
SELECT 
  v.user_id,
  COUNT(*) as total_vocabulary,
  COUNT(*) FILTER (WHERE mastery_level >= 4) as mastered_words,
  COUNT(*) FILTER (WHERE mastery_level <= 1) as new_words,
  COUNT(*) FILTER (WHERE next_review <= NOW()) as due_for_review,
  AVG(mastery_level) as average_mastery,
  COUNT(DISTINCT word_type) as word_types_learned,
  MAX(created_at) as last_vocabulary_added
FROM public.vocabulary v
WHERE NOT is_archived
GROUP BY v.user_id;

-- Learning progress view
CREATE OR REPLACE VIEW public.learning_progress AS
SELECT 
  ls.user_id,
  DATE(ls.started_at) as study_date,
  COUNT(*) as sessions_count,
  SUM(items_studied) as total_items_studied,
  SUM(items_correct) as total_correct,
  SUM(items_incorrect) as total_incorrect,
  AVG(accuracy_rate) as average_accuracy,
  SUM(duration_seconds) as total_study_time_seconds
FROM public.learning_sessions ls
WHERE ls.completed_at IS NOT NULL
GROUP BY ls.user_id, DATE(ls.started_at);

-- Collection summary view
CREATE OR REPLACE VIEW public.collection_summaries AS
SELECT 
  vc.id,
  vc.user_id,
  vc.name,
  vc.description,
  vc.is_public,
  COUNT(vci.vocabulary_id) as vocabulary_count,
  AVG(v.mastery_level) as average_mastery,
  COUNT(v.id) FILTER (WHERE v.mastery_level >= 4) as mastered_count,
  vc.created_at,
  vc.updated_at
FROM public.vocabulary_collections vc
LEFT JOIN public.vocabulary_collection_items vci ON vc.id = vci.collection_id
LEFT JOIN public.vocabulary v ON vci.vocabulary_id = v.id AND NOT v.is_archived
GROUP BY vc.id, vc.user_id, vc.name, vc.description, vc.is_public, vc.created_at, vc.updated_at;
```

## 2. Row Level Security (RLS) Policies

```sql
-- Enable RLS on all tables
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.vocabulary ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.images ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.learning_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.quiz_attempts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.vocabulary_collections ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.vocabulary_collection_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_activity ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.shared_vocabulary_sets ENABLE ROW LEVEL SECURITY;

-- Profiles policies
CREATE POLICY "Users can view own profile" ON public.profiles
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.profiles
  FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile" ON public.profiles
  FOR INSERT WITH CHECK (auth.uid() = id);

-- Vocabulary policies
CREATE POLICY "Users can manage own vocabulary" ON public.vocabulary
  FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view shared collection vocabulary" ON public.vocabulary
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM public.vocabulary_collection_items vci
      JOIN public.vocabulary_collections vc ON vci.collection_id = vc.id
      WHERE vci.vocabulary_id = public.vocabulary.id
      AND (vc.is_public = true OR vc.is_collaborative = true)
    )
  );

-- Images policies
CREATE POLICY "Users can manage own images" ON public.images
  FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view public images" ON public.images
  FOR SELECT USING (is_public = true);

-- Learning sessions policies
CREATE POLICY "Users can manage own sessions" ON public.learning_sessions
  FOR ALL USING (auth.uid() = user_id);

-- Quiz attempts policies
CREATE POLICY "Users can manage own quiz attempts" ON public.quiz_attempts
  FOR ALL USING (auth.uid() = user_id);

-- Collections policies
CREATE POLICY "Users can manage own collections" ON public.vocabulary_collections
  FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view public collections" ON public.vocabulary_collections
  FOR SELECT USING (is_public = true);

CREATE POLICY "Users can view collaborative collections" ON public.vocabulary_collections
  FOR SELECT USING (is_collaborative = true);

-- Collection items policies
CREATE POLICY "Users can manage own collection items" ON public.vocabulary_collection_items
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM public.vocabulary_collections vc
      WHERE vc.id = collection_id AND vc.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can view public collection items" ON public.vocabulary_collection_items
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM public.vocabulary_collections vc
      WHERE vc.id = collection_id AND (vc.is_public = true OR vc.is_collaborative = true)
    )
  );

-- User activity policies
CREATE POLICY "Users can view own activity" ON public.user_activity
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "System can insert activity" ON public.user_activity
  FOR INSERT WITH CHECK (true); -- Allow system/edge functions to log activity

-- Shared vocabulary sets policies (marketplace)
CREATE POLICY "Everyone can view approved shared sets" ON public.shared_vocabulary_sets
  FOR SELECT USING (is_approved = true);

CREATE POLICY "Users can manage own shared sets" ON public.shared_vocabulary_sets
  FOR ALL USING (auth.uid() = creator_id);

-- Admin access patterns (for users with admin role)
CREATE POLICY "Admins have full access" ON public.profiles
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM public.profiles 
      WHERE id = auth.uid() 
      AND (preferences->>'role') = 'admin'
    )
  );

-- Apply similar admin policies to other tables as needed
```