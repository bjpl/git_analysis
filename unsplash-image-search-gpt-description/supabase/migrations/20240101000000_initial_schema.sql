-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Users table (extends auth.users)
CREATE TABLE public.users (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    preferred_language TEXT DEFAULT 'en',
    theme_preference TEXT DEFAULT 'system' CHECK (theme_preference IN ('light', 'dark', 'system')),
    quiz_difficulty TEXT DEFAULT 'medium' CHECK (quiz_difficulty IN ('easy', 'medium', 'hard')),
    daily_goal INTEGER DEFAULT 10 CHECK (daily_goal > 0),
    streak_count INTEGER DEFAULT 0,
    last_activity_date DATE DEFAULT CURRENT_DATE,
    total_words_learned INTEGER DEFAULT 0,
    subscription_tier TEXT DEFAULT 'free' CHECK (subscription_tier IN ('free', 'premium', 'pro')),
    subscription_expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Vocabulary items table
CREATE TABLE public.vocabulary_items (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    word TEXT NOT NULL,
    definition TEXT NOT NULL,
    pronunciation TEXT,
    part_of_speech TEXT,
    example_sentence TEXT,
    difficulty_level TEXT DEFAULT 'medium' CHECK (difficulty_level IN ('easy', 'medium', 'hard')),
    source_language TEXT DEFAULT 'en',
    target_language TEXT DEFAULT 'es',
    translation TEXT,
    image_url TEXT,
    image_alt_text TEXT,
    image_source TEXT DEFAULT 'unsplash',
    unsplash_photo_id TEXT,
    unsplash_photographer TEXT,
    tags TEXT[] DEFAULT '{}',
    mastery_level INTEGER DEFAULT 0 CHECK (mastery_level >= 0 AND mastery_level <= 5),
    times_practiced INTEGER DEFAULT 0,
    times_correct INTEGER DEFAULT 0,
    last_practiced_at TIMESTAMP WITH TIME ZONE,
    next_review_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() + INTERVAL '1 day',
    is_favorite BOOLEAN DEFAULT FALSE,
    is_archived BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, word, target_language)
);

-- Search sessions table
CREATE TABLE public.search_sessions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    query TEXT NOT NULL,
    style TEXT DEFAULT 'realistic' CHECK (style IN ('realistic', 'artistic', 'minimalist', 'abstract', 'vintage')),
    results_count INTEGER DEFAULT 0,
    selected_image_id TEXT,
    duration_seconds INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Quiz results table
CREATE TABLE public.quiz_results (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    quiz_type TEXT NOT NULL CHECK (quiz_type IN ('flashcard', 'multiple_choice', 'typing', 'listening')),
    vocabulary_item_id UUID REFERENCES public.vocabulary_items(id) ON DELETE CASCADE NOT NULL,
    question TEXT NOT NULL,
    user_answer TEXT,
    correct_answer TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL,
    response_time_ms INTEGER,
    difficulty TEXT DEFAULT 'medium' CHECK (difficulty IN ('easy', 'medium', 'hard')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Shared lists table
CREATE TABLE public.shared_lists (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    owner_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    share_code TEXT UNIQUE DEFAULT encode(gen_random_bytes(8), 'base64'),
    vocabulary_items UUID[] DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    download_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User preferences table
CREATE TABLE public.user_preferences (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE UNIQUE NOT NULL,
    notifications_enabled BOOLEAN DEFAULT TRUE,
    email_reminders BOOLEAN DEFAULT TRUE,
    study_reminder_time TIME DEFAULT '18:00:00',
    auto_play_pronunciation BOOLEAN DEFAULT FALSE,
    show_pronunciation BOOLEAN DEFAULT TRUE,
    show_example_sentences BOOLEAN DEFAULT TRUE,
    quiz_auto_advance BOOLEAN DEFAULT FALSE,
    dark_mode BOOLEAN DEFAULT FALSE,
    language_interface TEXT DEFAULT 'en',
    spaced_repetition_enabled BOOLEAN DEFAULT TRUE,
    daily_goal_notifications BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_vocabulary_items_user_id ON public.vocabulary_items(user_id);
CREATE INDEX idx_vocabulary_items_next_review ON public.vocabulary_items(user_id, next_review_at) WHERE is_archived = FALSE;
CREATE INDEX idx_vocabulary_items_mastery ON public.vocabulary_items(user_id, mastery_level);
CREATE INDEX idx_vocabulary_items_word_search ON public.vocabulary_items USING gin(to_tsvector('english', word || ' ' || definition));
CREATE INDEX idx_vocabulary_items_tags ON public.vocabulary_items USING gin(tags);

CREATE INDEX idx_search_sessions_user_id ON public.search_sessions(user_id);
CREATE INDEX idx_search_sessions_created_at ON public.search_sessions(created_at DESC);

CREATE INDEX idx_quiz_results_user_id ON public.quiz_results(user_id);
CREATE INDEX idx_quiz_results_vocabulary_item ON public.quiz_results(vocabulary_item_id);
CREATE INDEX idx_quiz_results_created_at ON public.quiz_results(created_at DESC);

CREATE INDEX idx_shared_lists_owner_id ON public.shared_lists(owner_id);
CREATE INDEX idx_shared_lists_public ON public.shared_lists(is_public) WHERE is_public = TRUE;
CREATE INDEX idx_shared_lists_share_code ON public.shared_lists(share_code);

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON public.users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_vocabulary_items_updated_at
    BEFORE UPDATE ON public.vocabulary_items
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_search_sessions_updated_at
    BEFORE UPDATE ON public.search_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_shared_lists_updated_at
    BEFORE UPDATE ON public.shared_lists
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_preferences_updated_at
    BEFORE UPDATE ON public.user_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to update user stats
CREATE OR REPLACE FUNCTION update_user_stats()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        -- Update total words learned
        UPDATE public.users 
        SET total_words_learned = (
            SELECT COUNT(*) 
            FROM public.vocabulary_items 
            WHERE user_id = NEW.user_id AND is_archived = FALSE
        ),
        last_activity_date = CURRENT_DATE
        WHERE id = NEW.user_id;
        
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        -- Update total words learned
        UPDATE public.users 
        SET total_words_learned = (
            SELECT COUNT(*) 
            FROM public.vocabulary_items 
            WHERE user_id = OLD.user_id AND is_archived = FALSE
        )
        WHERE id = OLD.user_id;
        
        RETURN OLD;
    END IF;
    
    RETURN NULL;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_user_stats_trigger
    AFTER INSERT OR DELETE ON public.vocabulary_items
    FOR EACH ROW
    EXECUTE FUNCTION update_user_stats();

-- Function to update streak
CREATE OR REPLACE FUNCTION update_user_streak()
RETURNS TRIGGER AS $$
BEGIN
    DECLARE
        last_activity DATE;
        current_streak INTEGER;
    BEGIN
        SELECT last_activity_date, streak_count 
        INTO last_activity, current_streak
        FROM public.users 
        WHERE id = NEW.user_id;
        
        -- If last activity was yesterday, increment streak
        -- If last activity was today, don't change streak
        -- If last activity was more than 1 day ago, reset streak
        IF last_activity = CURRENT_DATE - INTERVAL '1 day' THEN
            UPDATE public.users
            SET streak_count = current_streak + 1,
                last_activity_date = CURRENT_DATE
            WHERE id = NEW.user_id;
        ELSIF last_activity < CURRENT_DATE - INTERVAL '1 day' THEN
            UPDATE public.users
            SET streak_count = 1,
                last_activity_date = CURRENT_DATE
            WHERE id = NEW.user_id;
        ELSIF last_activity < CURRENT_DATE THEN
            UPDATE public.users
            SET last_activity_date = CURRENT_DATE
            WHERE id = NEW.user_id;
        END IF;
        
        RETURN NEW;
    END;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_user_streak_trigger
    AFTER INSERT ON public.quiz_results
    FOR EACH ROW
    EXECUTE FUNCTION update_user_streak();