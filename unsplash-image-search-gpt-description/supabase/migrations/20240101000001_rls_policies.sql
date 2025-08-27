-- Enable RLS on all tables
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.vocabulary_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.search_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.quiz_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.shared_lists ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_preferences ENABLE ROW LEVEL SECURITY;

-- Users policies
CREATE POLICY "Users can view own profile" ON public.users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.users
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile" ON public.users
    FOR INSERT WITH CHECK (auth.uid() = id);

-- Vocabulary items policies
CREATE POLICY "Users can view own vocabulary items" ON public.vocabulary_items
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own vocabulary items" ON public.vocabulary_items
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own vocabulary items" ON public.vocabulary_items
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own vocabulary items" ON public.vocabulary_items
    FOR DELETE USING (auth.uid() = user_id);

-- Search sessions policies
CREATE POLICY "Users can view own search sessions" ON public.search_sessions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own search sessions" ON public.search_sessions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own search sessions" ON public.search_sessions
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own search sessions" ON public.search_sessions
    FOR DELETE USING (auth.uid() = user_id);

-- Quiz results policies
CREATE POLICY "Users can view own quiz results" ON public.quiz_results
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own quiz results" ON public.quiz_results
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own quiz results" ON public.quiz_results
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own quiz results" ON public.quiz_results
    FOR DELETE USING (auth.uid() = user_id);

-- Shared lists policies
CREATE POLICY "Users can view own shared lists" ON public.shared_lists
    FOR SELECT USING (auth.uid() = owner_id);

CREATE POLICY "Users can view public shared lists" ON public.shared_lists
    FOR SELECT USING (is_public = true);

CREATE POLICY "Users can insert own shared lists" ON public.shared_lists
    FOR INSERT WITH CHECK (auth.uid() = owner_id);

CREATE POLICY "Users can update own shared lists" ON public.shared_lists
    FOR UPDATE USING (auth.uid() = owner_id);

CREATE POLICY "Users can delete own shared lists" ON public.shared_lists
    FOR DELETE USING (auth.uid() = owner_id);

-- User preferences policies
CREATE POLICY "Users can view own preferences" ON public.user_preferences
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own preferences" ON public.user_preferences
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own preferences" ON public.user_preferences
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own preferences" ON public.user_preferences
    FOR DELETE USING (auth.uid() = user_id);

-- Create function to handle user creation
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.users (id, email, full_name, avatar_url)
    VALUES (
        NEW.id,
        NEW.email,
        NEW.raw_user_meta_data->>'full_name',
        NEW.raw_user_meta_data->>'avatar_url'
    );
    
    -- Create default preferences
    INSERT INTO public.user_preferences (user_id)
    VALUES (NEW.id);
    
    RETURN NEW;
END;
$$ language 'plpgsql' SECURITY DEFINER;

-- Create trigger for new user creation
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

-- Function to get vocabulary items for review
CREATE OR REPLACE FUNCTION get_vocabulary_for_review(user_uuid UUID, limit_count INTEGER DEFAULT 10)
RETURNS TABLE (
    id UUID,
    word TEXT,
    definition TEXT,
    pronunciation TEXT,
    part_of_speech TEXT,
    example_sentence TEXT,
    difficulty_level TEXT,
    translation TEXT,
    image_url TEXT,
    image_alt_text TEXT,
    mastery_level INTEGER,
    times_practiced INTEGER,
    times_correct INTEGER,
    next_review_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        vi.id,
        vi.word,
        vi.definition,
        vi.pronunciation,
        vi.part_of_speech,
        vi.example_sentence,
        vi.difficulty_level,
        vi.translation,
        vi.image_url,
        vi.image_alt_text,
        vi.mastery_level,
        vi.times_practiced,
        vi.times_correct,
        vi.next_review_at
    FROM public.vocabulary_items vi
    WHERE vi.user_id = user_uuid
        AND vi.is_archived = FALSE
        AND vi.next_review_at <= NOW()
    ORDER BY vi.next_review_at ASC, vi.mastery_level ASC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to update vocabulary item after practice
CREATE OR REPLACE FUNCTION update_vocabulary_practice(
    item_id UUID,
    is_correct_answer BOOLEAN,
    response_time INTEGER DEFAULT NULL
)
RETURNS VOID AS $$
DECLARE
    current_mastery INTEGER;
    current_times_practiced INTEGER;
    current_times_correct INTEGER;
    next_interval INTERVAL;
BEGIN
    -- Get current stats
    SELECT mastery_level, times_practiced, times_correct
    INTO current_mastery, current_times_practiced, current_times_correct
    FROM public.vocabulary_items
    WHERE id = item_id;
    
    -- Calculate new mastery level based on spaced repetition algorithm
    IF is_correct_answer THEN
        current_mastery := LEAST(current_mastery + 1, 5);
        current_times_correct := current_times_correct + 1;
        
        -- Calculate next review interval based on mastery level
        CASE current_mastery
            WHEN 1 THEN next_interval := INTERVAL '1 day';
            WHEN 2 THEN next_interval := INTERVAL '3 days';
            WHEN 3 THEN next_interval := INTERVAL '1 week';
            WHEN 4 THEN next_interval := INTERVAL '2 weeks';
            WHEN 5 THEN next_interval := INTERVAL '1 month';
            ELSE next_interval := INTERVAL '1 day';
        END CASE;
    ELSE
        current_mastery := GREATEST(current_mastery - 1, 0);
        next_interval := INTERVAL '1 day';
    END IF;
    
    current_times_practiced := current_times_practiced + 1;
    
    -- Update the vocabulary item
    UPDATE public.vocabulary_items
    SET 
        mastery_level = current_mastery,
        times_practiced = current_times_practiced,
        times_correct = current_times_correct,
        last_practiced_at = NOW(),
        next_review_at = NOW() + next_interval
    WHERE id = item_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to search vocabulary items
CREATE OR REPLACE FUNCTION search_vocabulary(
    user_uuid UUID,
    search_query TEXT DEFAULT '',
    tag_filter TEXT[] DEFAULT '{}',
    difficulty_filter TEXT DEFAULT NULL,
    limit_count INTEGER DEFAULT 20,
    offset_count INTEGER DEFAULT 0
)
RETURNS TABLE (
    id UUID,
    word TEXT,
    definition TEXT,
    pronunciation TEXT,
    part_of_speech TEXT,
    example_sentence TEXT,
    difficulty_level TEXT,
    translation TEXT,
    image_url TEXT,
    image_alt_text TEXT,
    tags TEXT[],
    mastery_level INTEGER,
    times_practiced INTEGER,
    is_favorite BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        vi.id,
        vi.word,
        vi.definition,
        vi.pronunciation,
        vi.part_of_speech,
        vi.example_sentence,
        vi.difficulty_level,
        vi.translation,
        vi.image_url,
        vi.image_alt_text,
        vi.tags,
        vi.mastery_level,
        vi.times_practiced,
        vi.is_favorite,
        vi.created_at
    FROM public.vocabulary_items vi
    WHERE vi.user_id = user_uuid
        AND vi.is_archived = FALSE
        AND (
            search_query = '' OR
            to_tsvector('english', vi.word || ' ' || vi.definition) @@ plainto_tsquery('english', search_query)
        )
        AND (
            array_length(tag_filter, 1) IS NULL OR
            vi.tags && tag_filter
        )
        AND (
            difficulty_filter IS NULL OR
            vi.difficulty_level = difficulty_filter
        )
    ORDER BY 
        CASE WHEN search_query != '' THEN
            ts_rank(to_tsvector('english', vi.word || ' ' || vi.definition), plainto_tsquery('english', search_query))
        ELSE 0 END DESC,
        vi.created_at DESC
    LIMIT limit_count
    OFFSET offset_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;