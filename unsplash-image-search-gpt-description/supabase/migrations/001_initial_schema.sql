-- Initial database schema for Unsplash GPT PWA
-- This migration creates the foundational tables and security policies

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create custom types
CREATE TYPE learning_level AS ENUM ('beginner', 'intermediate', 'advanced', 'native');
CREATE TYPE description_style AS ENUM ('academic', 'poetic', 'technical');
CREATE TYPE word_type AS ENUM ('sustantivo', 'verbo', 'adjetivo', 'frase');
CREATE TYPE quiz_type AS ENUM ('translation', 'multiple_choice', 'audio', 'typing');

-- User profiles table
CREATE TABLE profiles (
  id UUID REFERENCES auth.users ON DELETE CASCADE,
  email TEXT UNIQUE NOT NULL,
  full_name TEXT,
  avatar_url TEXT,
  learning_level learning_level DEFAULT 'intermediate',
  preferred_style description_style DEFAULT 'academic',
  timezone TEXT DEFAULT 'UTC',
  language_interface TEXT DEFAULT 'en',
  daily_goal INTEGER DEFAULT 10,
  notifications_enabled BOOLEAN DEFAULT true,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
  PRIMARY KEY (id)
);

-- Vocabulary entries table
CREATE TABLE vocabulary (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
  spanish_text TEXT NOT NULL,
  english_translation TEXT NOT NULL,
  context TEXT,
  image_url TEXT,
  search_query TEXT,
  word_type word_type NOT NULL,
  learning_score INTEGER DEFAULT 0 CHECK (learning_score >= 0 AND learning_score <= 100),
  difficulty_level INTEGER DEFAULT 1 CHECK (difficulty_level >= 1 AND difficulty_level <= 5),
  last_reviewed TIMESTAMP WITH TIME ZONE,
  next_review TIMESTAMP WITH TIME ZONE,
  review_count INTEGER DEFAULT 0,
  streak_count INTEGER DEFAULT 0,
  is_favorite BOOLEAN DEFAULT false,
  tags TEXT[] DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
  
  -- Indexes for better performance
  CONSTRAINT unique_user_spanish UNIQUE(user_id, spanish_text)
);

-- Learning sessions table
CREATE TABLE sessions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
  search_query TEXT,
  image_url TEXT,
  generated_description TEXT,
  user_notes TEXT,
  style_used description_style,
  level_used learning_level,
  duration_seconds INTEGER DEFAULT 0,
  vocabulary_learned INTEGER DEFAULT 0,
  ai_tokens_used INTEGER DEFAULT 0,
  session_type TEXT DEFAULT 'standard',
  device_type TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Quiz attempts table
CREATE TABLE quiz_attempts (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
  vocabulary_id UUID REFERENCES vocabulary(id) ON DELETE CASCADE NOT NULL,
  quiz_type quiz_type NOT NULL,
  question_text TEXT NOT NULL,
  user_answer TEXT,
  correct_answer TEXT NOT NULL,
  is_correct BOOLEAN NOT NULL,
  response_time_ms INTEGER,
  difficulty INTEGER DEFAULT 1,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Shared collections table
CREATE TABLE shared_collections (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  owner_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  is_public BOOLEAN DEFAULT false,
  is_featured BOOLEAN DEFAULT false,
  category TEXT,
  difficulty_level INTEGER DEFAULT 1 CHECK (difficulty_level >= 1 AND difficulty_level <= 5),
  subscriber_count INTEGER DEFAULT 0,
  vocabulary_count INTEGER DEFAULT 0,
  tags TEXT[] DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Collection vocabulary mappings
CREATE TABLE collection_vocabulary (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  collection_id UUID REFERENCES shared_collections(id) ON DELETE CASCADE NOT NULL,
  vocabulary_id UUID REFERENCES vocabulary(id) ON DELETE CASCADE NOT NULL,
  order_index INTEGER DEFAULT 0,
  added_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
  
  CONSTRAINT unique_collection_vocabulary UNIQUE(collection_id, vocabulary_id)
);

-- Collection subscriptions
CREATE TABLE collection_subscriptions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
  collection_id UUID REFERENCES shared_collections(id) ON DELETE CASCADE NOT NULL,
  subscribed_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
  
  CONSTRAINT unique_user_collection_subscription UNIQUE(user_id, collection_id)
);

-- User achievements and badges
CREATE TABLE achievements (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
  achievement_type TEXT NOT NULL,
  achievement_name TEXT NOT NULL,
  description TEXT,
  icon_url TEXT,
  earned_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
  
  CONSTRAINT unique_user_achievement UNIQUE(user_id, achievement_type)
);

-- Learning streaks table
CREATE TABLE learning_streaks (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
  current_streak INTEGER DEFAULT 0,
  longest_streak INTEGER DEFAULT 0,
  last_activity_date DATE DEFAULT CURRENT_DATE,
  streak_start_date DATE DEFAULT CURRENT_DATE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
  
  CONSTRAINT unique_user_streak UNIQUE(user_id)
);

-- Analytics and metrics table
CREATE TABLE analytics_events (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES profiles(id) ON DELETE SET NULL,
  session_id TEXT,
  event_type TEXT NOT NULL,
  event_data JSONB DEFAULT '{}',
  page_url TEXT,
  user_agent TEXT,
  ip_address INET,
  country_code TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Create indexes for better query performance
CREATE INDEX idx_vocabulary_user_id ON vocabulary(user_id);
CREATE INDEX idx_vocabulary_learning_score ON vocabulary(learning_score);
CREATE INDEX idx_vocabulary_next_review ON vocabulary(next_review) WHERE next_review IS NOT NULL;
CREATE INDEX idx_vocabulary_word_type ON vocabulary(word_type);
CREATE INDEX idx_vocabulary_tags ON vocabulary USING gin(tags);
CREATE INDEX idx_vocabulary_created_at ON vocabulary(created_at);

CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_created_at ON sessions(created_at);

CREATE INDEX idx_quiz_attempts_user_id ON quiz_attempts(user_id);
CREATE INDEX idx_quiz_attempts_vocabulary_id ON quiz_attempts(vocabulary_id);
CREATE INDEX idx_quiz_attempts_created_at ON quiz_attempts(created_at);

CREATE INDEX idx_shared_collections_owner_id ON shared_collections(owner_id);
CREATE INDEX idx_shared_collections_public ON shared_collections(is_public) WHERE is_public = true;
CREATE INDEX idx_shared_collections_featured ON shared_collections(is_featured) WHERE is_featured = true;

CREATE INDEX idx_analytics_events_user_id ON analytics_events(user_id);
CREATE INDEX idx_analytics_events_type ON analytics_events(event_type);
CREATE INDEX idx_analytics_events_created_at ON analytics_events(created_at);

-- Enable Row Level Security (RLS)
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE vocabulary ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE quiz_attempts ENABLE ROW LEVEL SECURITY;
ALTER TABLE shared_collections ENABLE ROW LEVEL SECURITY;
ALTER TABLE collection_vocabulary ENABLE ROW LEVEL SECURITY;
ALTER TABLE collection_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE achievements ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_streaks ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics_events ENABLE ROW LEVEL SECURITY;

-- RLS Policies

-- Profiles policies
CREATE POLICY "Users can view own profile" ON profiles
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON profiles
  FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile" ON profiles
  FOR INSERT WITH CHECK (auth.uid() = id);

-- Vocabulary policies
CREATE POLICY "Users can manage own vocabulary" ON vocabulary
  FOR ALL USING (auth.uid() = user_id);

-- Sessions policies
CREATE POLICY "Users can manage own sessions" ON sessions
  FOR ALL USING (auth.uid() = user_id);

-- Quiz attempts policies
CREATE POLICY "Users can manage own quiz attempts" ON quiz_attempts
  FOR ALL USING (auth.uid() = user_id);

-- Shared collections policies
CREATE POLICY "Users can view public collections" ON shared_collections
  FOR SELECT USING (is_public = true OR auth.uid() = owner_id);

CREATE POLICY "Users can manage own collections" ON shared_collections
  FOR ALL USING (auth.uid() = owner_id);

-- Collection vocabulary policies
CREATE POLICY "Users can view collection vocabulary if they can see collection" ON collection_vocabulary
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM shared_collections sc
      WHERE sc.id = collection_id
      AND (sc.is_public = true OR sc.owner_id = auth.uid())
    )
  );

CREATE POLICY "Users can manage vocabulary in own collections" ON collection_vocabulary
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM shared_collections sc
      WHERE sc.id = collection_id
      AND sc.owner_id = auth.uid()
    )
  );

-- Collection subscriptions policies
CREATE POLICY "Users can manage own subscriptions" ON collection_subscriptions
  FOR ALL USING (auth.uid() = user_id);

-- Achievements policies
CREATE POLICY "Users can view own achievements" ON achievements
  FOR SELECT USING (auth.uid() = user_id);

-- Learning streaks policies
CREATE POLICY "Users can manage own streaks" ON learning_streaks
  FOR ALL USING (auth.uid() = user_id);

-- Analytics policies (restricted)
CREATE POLICY "Users can insert own analytics" ON analytics_events
  FOR INSERT WITH CHECK (auth.uid() = user_id OR user_id IS NULL);

-- Functions for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = timezone('utc'::text, now());
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON profiles
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_vocabulary_updated_at BEFORE UPDATE ON vocabulary
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_shared_collections_updated_at BEFORE UPDATE ON shared_collections
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_learning_streaks_updated_at BEFORE UPDATE ON learning_streaks
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to handle new user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, email, full_name, avatar_url)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'full_name', ''),
    COALESCE(NEW.raw_user_meta_data->>'avatar_url', '')
  );
  
  INSERT INTO public.learning_streaks (user_id)
  VALUES (NEW.id);
  
  RETURN NEW;
END;
$$ language 'plpgsql' SECURITY definer;

-- Create trigger for new user signup
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Function to update collection vocabulary count
CREATE OR REPLACE FUNCTION update_collection_vocabulary_count()
RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN
    UPDATE shared_collections 
    SET vocabulary_count = vocabulary_count + 1 
    WHERE id = NEW.collection_id;
    RETURN NEW;
  ELSIF TG_OP = 'DELETE' THEN
    UPDATE shared_collections 
    SET vocabulary_count = vocabulary_count - 1 
    WHERE id = OLD.collection_id;
    RETURN OLD;
  END IF;
  RETURN NULL;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_collection_count
  AFTER INSERT OR DELETE ON collection_vocabulary
  FOR EACH ROW EXECUTE FUNCTION update_collection_vocabulary_count();

-- Function to update collection subscriber count
CREATE OR REPLACE FUNCTION update_collection_subscriber_count()
RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN
    UPDATE shared_collections 
    SET subscriber_count = subscriber_count + 1 
    WHERE id = NEW.collection_id;
    RETURN NEW;
  ELSIF TG_OP = 'DELETE' THEN
    UPDATE shared_collections 
    SET subscriber_count = subscriber_count - 1 
    WHERE id = OLD.collection_id;
    RETURN OLD;
  END IF;
  RETURN NULL;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_subscriber_count
  AFTER INSERT OR DELETE ON collection_subscriptions
  FOR EACH ROW EXECUTE FUNCTION update_collection_subscriber_count();