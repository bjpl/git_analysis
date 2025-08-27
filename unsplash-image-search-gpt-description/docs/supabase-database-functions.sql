-- Supabase Database Functions for Business Logic
-- Advanced functions for vocabulary learning, analytics, and spaced repetition

-- 1. USER STATISTICS AND ANALYTICS

-- Function to calculate comprehensive user statistics
CREATE OR REPLACE FUNCTION public.calculate_user_statistics(p_user_id UUID)
RETURNS TABLE(
  total_vocabulary INTEGER,
  mastered_vocabulary INTEGER,
  vocabulary_added_last_30_days INTEGER,
  study_streak_days INTEGER,
  total_study_time_hours NUMERIC,
  average_accuracy NUMERIC,
  quiz_attempts_total INTEGER,
  favorite_study_time TEXT,
  most_challenging_word_type TEXT,
  learning_velocity_words_per_week NUMERIC,
  next_milestone TEXT
) AS $$
DECLARE
  study_streak INTEGER := 0;
  current_date DATE := CURRENT_DATE;
  check_date DATE;
BEGIN
  -- Calculate current study streak
  check_date := current_date;
  WHILE EXISTS (
    SELECT 1 FROM public.learning_sessions ls
    WHERE ls.user_id = p_user_id
    AND DATE(ls.started_at) = check_date
    AND ls.completed_at IS NOT NULL
  ) LOOP
    study_streak := study_streak + 1;
    check_date := check_date - INTERVAL '1 day';
  END LOOP;

  RETURN QUERY
  SELECT
    -- Total vocabulary
    COALESCE((SELECT COUNT(*)::INTEGER FROM public.vocabulary v WHERE v.user_id = p_user_id AND NOT v.is_archived), 0),
    
    -- Mastered vocabulary (mastery level >= 4)
    COALESCE((SELECT COUNT(*)::INTEGER FROM public.vocabulary v WHERE v.user_id = p_user_id AND v.mastery_level >= 4 AND NOT v.is_archived), 0),
    
    -- Vocabulary added in last 30 days
    COALESCE((SELECT COUNT(*)::INTEGER FROM public.vocabulary v WHERE v.user_id = p_user_id AND v.created_at >= CURRENT_DATE - INTERVAL '30 days'), 0),
    
    -- Study streak
    study_streak,
    
    -- Total study time in hours
    COALESCE((SELECT ROUND((SUM(ls.duration_seconds) / 3600.0)::NUMERIC, 1) FROM public.learning_sessions ls WHERE ls.user_id = p_user_id AND ls.completed_at IS NOT NULL), 0),
    
    -- Average accuracy
    COALESCE((SELECT ROUND(AVG(ls.accuracy_rate)::NUMERIC, 1) FROM public.learning_sessions ls WHERE ls.user_id = p_user_id AND ls.accuracy_rate IS NOT NULL), 0),
    
    -- Total quiz attempts
    COALESCE((SELECT COUNT(*)::INTEGER FROM public.quiz_attempts qa WHERE qa.user_id = p_user_id), 0),
    
    -- Favorite study time (hour of day with most sessions)
    COALESCE((
      SELECT EXTRACT(HOUR FROM ls.started_at)::TEXT || ':00' 
      FROM public.learning_sessions ls 
      WHERE ls.user_id = p_user_id 
      GROUP BY EXTRACT(HOUR FROM ls.started_at) 
      ORDER BY COUNT(*) DESC 
      LIMIT 1
    ), 'Not determined'),
    
    -- Most challenging word type (lowest average mastery)
    COALESCE((
      SELECT v.word_type 
      FROM public.vocabulary v 
      WHERE v.user_id = p_user_id AND NOT v.is_archived 
      GROUP BY v.word_type 
      ORDER BY AVG(v.mastery_level) ASC 
      LIMIT 1
    ), 'No data'),
    
    -- Learning velocity (words per week based on last 4 weeks)
    COALESCE((
      SELECT ROUND((COUNT(*) / 4.0)::NUMERIC, 1)
      FROM public.vocabulary v 
      WHERE v.user_id = p_user_id 
      AND v.created_at >= CURRENT_DATE - INTERVAL '28 days'
    ), 0),
    
    -- Next milestone
    CASE 
      WHEN COALESCE((SELECT COUNT(*) FROM public.vocabulary v WHERE v.user_id = p_user_id AND NOT v.is_archived), 0) < 100 THEN '100 vocabulary words'
      WHEN COALESCE((SELECT COUNT(*) FROM public.vocabulary v WHERE v.user_id = p_user_id AND v.mastery_level >= 4 AND NOT v.is_archived), 0) < 50 THEN 'Master 50 words'
      WHEN study_streak < 7 THEN '7-day study streak'
      WHEN study_streak < 30 THEN '30-day study streak'
      ELSE 'Vocabulary master!'
    END;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 2. SPACED REPETITION SYSTEM

-- Function to calculate next review date using spaced repetition algorithm
CREATE OR REPLACE FUNCTION public.calculate_next_review_date(
  current_mastery_level INTEGER,
  last_review_date TIMESTAMPTZ,
  was_correct BOOLEAN
) RETURNS TIMESTAMPTZ AS $$
DECLARE
  base_interval INTERVAL;
  multiplier NUMERIC := 1.0;
  next_date TIMESTAMPTZ;
BEGIN
  -- Base intervals based on mastery level
  base_interval := CASE current_mastery_level
    WHEN 0 THEN INTERVAL '1 day'
    WHEN 1 THEN INTERVAL '3 days'
    WHEN 2 THEN INTERVAL '1 week'
    WHEN 3 THEN INTERVAL '2 weeks'
    WHEN 4 THEN INTERVAL '1 month'
    ELSE INTERVAL '3 months'
  END;
  
  -- Adjust multiplier based on performance
  multiplier := CASE
    WHEN was_correct THEN 1.0
    ELSE 0.5  -- Review sooner if incorrect
  END;
  
  -- Calculate next review date
  next_date := COALESCE(last_review_date, NOW()) + (base_interval * multiplier);
  
  RETURN next_date;
END;
$$ LANGUAGE plpgsql;

-- Function to get vocabulary items due for review
CREATE OR REPLACE FUNCTION public.get_spaced_repetition_items(
  p_user_id UUID,
  p_limit INTEGER DEFAULT 20,
  p_difficulty_filter TEXT DEFAULT NULL,
  p_word_type_filter TEXT DEFAULT NULL
)
RETURNS TABLE(
  id UUID,
  spanish_text TEXT,
  english_translation TEXT,
  context TEXT,
  mastery_level INTEGER,
  times_encountered INTEGER,
  last_reviewed TIMESTAMPTZ,
  next_review TIMESTAMPTZ,
  priority_score NUMERIC
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    v.id,
    v.spanish_text,
    v.english_translation,
    v.context,
    v.mastery_level,
    v.times_encountered,
    v.last_reviewed,
    v.next_review,
    -- Priority score: overdue items get higher priority
    CASE 
      WHEN v.next_review <= NOW() THEN 
        100 + EXTRACT(DAYS FROM (NOW() - v.next_review)) -- Overdue bonus
      ELSE 
        50 + (5 - v.mastery_level) * 10 -- Lower mastery = higher priority
    END AS priority_score
  FROM public.vocabulary v
  WHERE v.user_id = p_user_id
    AND NOT v.is_archived
    AND (p_difficulty_filter IS NULL OR v.difficulty_level = p_difficulty_filter)
    AND (p_word_type_filter IS NULL OR v.word_type = p_word_type_filter)
    AND (v.next_review IS NULL OR v.next_review <= NOW() + INTERVAL '1 day')
  ORDER BY priority_score DESC, v.next_review ASC NULLS FIRST
  LIMIT p_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 3. QUIZ GENERATION

-- Function to generate adaptive quiz questions based on user performance
CREATE OR REPLACE FUNCTION public.generate_quiz_questions(
  p_user_id UUID,
  p_question_count INTEGER DEFAULT 10,
  p_quiz_type TEXT DEFAULT 'mixed',
  p_difficulty_preference TEXT DEFAULT 'adaptive'
)
RETURNS TABLE(
  vocabulary_id UUID,
  question_type TEXT,
  question_text TEXT,
  correct_answer TEXT,
  distractors JSONB,
  difficulty_level TEXT,
  estimated_time_seconds INTEGER
) AS $$
DECLARE
  vocab_record RECORD;
  question_types TEXT[] := ARRAY['translation', 'multiple_choice', 'fill_blank'];
  current_question_type TEXT;
  distractors_array TEXT[];
BEGIN
  -- Determine question types based on quiz type
  question_types := CASE p_quiz_type
    WHEN 'translation' THEN ARRAY['translation']
    WHEN 'multiple_choice' THEN ARRAY['multiple_choice']
    WHEN 'fill_blank' THEN ARRAY['fill_blank']
    ELSE ARRAY['translation', 'multiple_choice', 'fill_blank']
  END;

  -- Generate questions for vocabulary items
  FOR vocab_record IN
    SELECT * FROM public.get_spaced_repetition_items(p_user_id, p_question_count)
  LOOP
    -- Randomly select question type
    current_question_type := question_types[1 + floor(random() * array_length(question_types, 1))];
    
    -- Generate distractors for multiple choice
    IF current_question_type = 'multiple_choice' THEN
      SELECT ARRAY(
        SELECT v2.english_translation
        FROM public.vocabulary v2
        WHERE v2.user_id = p_user_id 
          AND v2.id != vocab_record.id
          AND v2.difficulty_level = vocab_record.difficulty_level
          AND v2.english_translation != vocab_record.english_translation
        ORDER BY RANDOM()
        LIMIT 3
      ) INTO distractors_array;
    END IF;
    
    RETURN QUERY SELECT
      vocab_record.id,
      current_question_type,
      CASE current_question_type
        WHEN 'translation' THEN 'What does "' || vocab_record.spanish_text || '" mean in English?'
        WHEN 'multiple_choice' THEN 'Choose the correct translation for "' || vocab_record.spanish_text || '"'
        WHEN 'fill_blank' THEN 'Fill in the blank: ' || COALESCE(vocab_record.context, 'The word means ___.')
      END,
      vocab_record.english_translation,
      CASE 
        WHEN current_question_type = 'multiple_choice' THEN 
          jsonb_build_array(vocab_record.english_translation) || to_jsonb(distractors_array)
        ELSE NULL
      END,
      vocab_record.difficulty_level::TEXT,
      CASE current_question_type
        WHEN 'translation' THEN 30
        WHEN 'multiple_choice' THEN 20
        WHEN 'fill_blank' THEN 45
      END;
  END LOOP;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 4. LEARNING ANALYTICS

-- Function to analyze learning patterns and provide insights
CREATE OR REPLACE FUNCTION public.analyze_learning_patterns(p_user_id UUID)
RETURNS TABLE(
  insight_type TEXT,
  insight_title TEXT,
  insight_description TEXT,
  data_points JSONB,
  recommendation TEXT,
  confidence_score NUMERIC
) AS $$
DECLARE
  total_sessions INTEGER;
  avg_session_length NUMERIC;
  peak_performance_hour INTEGER;
  struggling_word_types TEXT[];
BEGIN
  -- Get basic metrics
  SELECT COUNT(*), AVG(duration_seconds/60.0)
  INTO total_sessions, avg_session_length
  FROM public.learning_sessions
  WHERE user_id = p_user_id AND completed_at IS NOT NULL;
  
  -- Find peak performance time
  SELECT EXTRACT(HOUR FROM started_at)::INTEGER
  INTO peak_performance_hour
  FROM public.learning_sessions
  WHERE user_id = p_user_id AND accuracy_rate IS NOT NULL
  GROUP BY EXTRACT(HOUR FROM started_at)
  ORDER BY AVG(accuracy_rate) DESC
  LIMIT 1;
  
  -- Find struggling word types
  SELECT ARRAY_AGG(word_type)
  INTO struggling_word_types
  FROM (
    SELECT word_type
    FROM public.vocabulary
    WHERE user_id = p_user_id
    GROUP BY word_type
    HAVING AVG(mastery_level) < 2
    ORDER BY AVG(mastery_level) ASC
    LIMIT 3
  ) sub;

  -- Generate insights
  
  -- Insight 1: Study frequency
  RETURN QUERY SELECT
    'study_frequency'::TEXT,
    'Study Frequency Analysis'::TEXT,
    CASE 
      WHEN total_sessions >= 20 THEN 'You have excellent study consistency!'
      WHEN total_sessions >= 10 THEN 'Good study habits, try to be more consistent'
      ELSE 'Consider studying more regularly for better results'
    END::TEXT,
    jsonb_build_object(
      'total_sessions', total_sessions,
      'sessions_per_week', ROUND((total_sessions / GREATEST(1, EXTRACT(DAYS FROM (NOW() - (SELECT MIN(created_at) FROM public.learning_sessions WHERE user_id = p_user_id))) / 7))::NUMERIC, 1)
    ),
    CASE 
      WHEN total_sessions < 10 THEN 'Try to study for at least 10-15 minutes daily'
      ELSE 'Maintain your current study schedule'
    END::TEXT,
    CASE 
      WHEN total_sessions >= 20 THEN 0.9
      WHEN total_sessions >= 10 THEN 0.7
      ELSE 0.8
    END::NUMERIC;
  
  -- Insight 2: Session length optimization
  IF avg_session_length IS NOT NULL THEN
    RETURN QUERY SELECT
      'session_length'::TEXT,
      'Study Session Duration'::TEXT,
      CASE 
        WHEN avg_session_length > 60 THEN 'Your sessions are quite long - great dedication!'
        WHEN avg_session_length > 30 THEN 'Good session length for effective learning'
        WHEN avg_session_length > 15 THEN 'Consider slightly longer sessions for better retention'
        ELSE 'Your sessions are quite short - try extending them slightly'
      END::TEXT,
      jsonb_build_object('average_minutes', ROUND(avg_session_length, 1)),
      CASE 
        WHEN avg_session_length BETWEEN 20 AND 45 THEN 'Your session length is optimal'
        WHEN avg_session_length < 15 THEN 'Aim for 20-30 minute sessions for better retention'
        ELSE 'Consider breaking longer sessions into shorter, focused segments'
      END::TEXT,
      CASE 
        WHEN avg_session_length BETWEEN 20 AND 45 THEN 0.9
        ELSE 0.7
      END::NUMERIC;
  END IF;
  
  -- Insight 3: Peak performance time
  IF peak_performance_hour IS NOT NULL THEN
    RETURN QUERY SELECT
      'peak_performance'::TEXT,
      'Optimal Study Time'::TEXT,
      'Your best performance is around ' || peak_performance_hour || ':00'::TEXT,
      jsonb_build_object('peak_hour', peak_performance_hour),
      'Schedule your most challenging study sessions around ' || peak_performance_hour || ':00 for maximum effectiveness'::TEXT,
      0.8::NUMERIC;
  END IF;
  
  -- Insight 4: Struggling areas
  IF array_length(struggling_word_types, 1) > 0 THEN
    RETURN QUERY SELECT
      'struggling_areas'::TEXT,
      'Areas for Improvement'::TEXT,
      'Focus on these word types: ' || array_to_string(struggling_word_types, ', ')::TEXT,
      jsonb_build_object('word_types', struggling_word_types),
      'Create focused study sessions targeting ' || array_to_string(struggling_word_types, ' and ') || ' to improve overall mastery'::TEXT,
      0.85::NUMERIC;
  END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 5. VOCABULARY IMPORT/EXPORT HELPERS

-- Function to import vocabulary with duplicate detection and smart merging
CREATE OR REPLACE FUNCTION public.smart_vocabulary_import(
  p_user_id UUID,
  p_vocabulary_data JSONB,
  p_merge_strategy TEXT DEFAULT 'skip_duplicates' -- 'skip_duplicates', 'update_duplicates', 'create_variants'
) RETURNS TABLE(
  imported_count INTEGER,
  skipped_count INTEGER,
  updated_count INTEGER,
  error_count INTEGER,
  errors JSONB
) AS $$
DECLARE
  vocab_item JSONB;
  spanish_word TEXT;
  english_translation TEXT;
  existing_vocab_id UUID;
  import_count INTEGER := 0;
  skip_count INTEGER := 0;
  update_count INTEGER := 0;
  error_count INTEGER := 0;
  error_messages JSONB := '[]'::jsonb;
BEGIN
  -- Process each vocabulary item
  FOR vocab_item IN SELECT jsonb_array_elements(p_vocabulary_data)
  LOOP
    BEGIN
      -- Extract required fields
      spanish_word := vocab_item->>'spanish_text';
      english_translation := vocab_item->>'english_translation';
      
      -- Validate required fields
      IF spanish_word IS NULL OR english_translation IS NULL OR 
         LENGTH(TRIM(spanish_word)) = 0 OR LENGTH(TRIM(english_translation)) = 0 THEN
        error_count := error_count + 1;
        error_messages := error_messages || jsonb_build_object(
          'item', vocab_item,
          'error', 'Missing required fields: spanish_text and english_translation'
        );
        CONTINUE;
      END IF;
      
      -- Check for existing vocabulary
      SELECT id INTO existing_vocab_id
      FROM public.vocabulary
      WHERE user_id = p_user_id 
        AND LOWER(TRIM(spanish_text)) = LOWER(TRIM(spanish_word))
      LIMIT 1;
      
      IF existing_vocab_id IS NOT NULL THEN
        -- Handle duplicates based on strategy
        CASE p_merge_strategy
          WHEN 'skip_duplicates' THEN
            skip_count := skip_count + 1;
            
          WHEN 'update_duplicates' THEN
            UPDATE public.vocabulary SET
              english_translation = english_translation,
              context = COALESCE(vocab_item->>'context', context),
              difficulty_level = COALESCE(vocab_item->>'difficulty_level', difficulty_level),
              word_type = COALESCE(vocab_item->>'word_type', word_type),
              notes = COALESCE(vocab_item->>'notes', notes),
              updated_at = NOW()
            WHERE id = existing_vocab_id;
            update_count := update_count + 1;
            
          WHEN 'create_variants' THEN
            -- Create variant with suffix if translation is different
            IF NOT EXISTS (
              SELECT 1 FROM public.vocabulary 
              WHERE user_id = p_user_id 
                AND LOWER(TRIM(english_translation)) = LOWER(TRIM(english_translation))
            ) THEN
              INSERT INTO public.vocabulary (
                user_id, spanish_text, english_translation, context,
                difficulty_level, word_type, source_type, notes
              ) VALUES (
                p_user_id,
                spanish_word || ' (variant)',
                english_translation,
                vocab_item->>'context',
                COALESCE(vocab_item->>'difficulty_level', 'intermediate'),
                COALESCE(vocab_item->>'word_type', 'unknown'),
                'import',
                vocab_item->>'notes'
              );
              import_count := import_count + 1;
            ELSE
              skip_count := skip_count + 1;
            END IF;
        END CASE;
        
      ELSE
        -- Insert new vocabulary item
        INSERT INTO public.vocabulary (
          user_id, spanish_text, english_translation, context,
          difficulty_level, word_type, source_type, notes,
          times_encountered
        ) VALUES (
          p_user_id,
          TRIM(spanish_word),
          TRIM(english_translation),
          vocab_item->>'context',
          COALESCE(vocab_item->>'difficulty_level', 'intermediate'),
          COALESCE(vocab_item->>'word_type', 'unknown'),
          'import',
          vocab_item->>'notes',
          COALESCE((vocab_item->>'times_encountered')::INTEGER, 1)
        );
        import_count := import_count + 1;
      END IF;
      
    EXCEPTION WHEN OTHERS THEN
      error_count := error_count + 1;
      error_messages := error_messages || jsonb_build_object(
        'item', vocab_item,
        'error', SQLERRM
      );
    END;
  END LOOP;
  
  RETURN QUERY SELECT import_count, skip_count, update_count, error_count, error_messages;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 6. GAMIFICATION AND ACHIEVEMENTS

-- Function to check and award achievements
CREATE OR REPLACE FUNCTION public.check_and_award_achievements(p_user_id UUID)
RETURNS TABLE(
  achievement_type TEXT,
  achievement_name TEXT,
  achievement_description TEXT,
  points_awarded INTEGER,
  newly_earned BOOLEAN
) AS $$
DECLARE
  user_stats RECORD;
  vocab_count INTEGER;
  mastered_count INTEGER;
  streak_days INTEGER;
  study_hours NUMERIC;
BEGIN
  -- Get user statistics
  SELECT * INTO user_stats FROM public.calculate_user_statistics(p_user_id);
  
  vocab_count := user_stats.total_vocabulary;
  mastered_count := user_stats.mastered_vocabulary;
  streak_days := user_stats.study_streak_days;
  study_hours := user_stats.total_study_time_hours;
  
  -- Check vocabulary collection achievements
  IF vocab_count >= 100 AND NOT EXISTS (
    SELECT 1 FROM public.user_activity 
    WHERE user_id = p_user_id 
    AND activity_type = 'achievement_earned' 
    AND details->>'achievement' = 'vocab_collector_100'
  ) THEN
    -- Award achievement
    INSERT INTO public.user_activity (user_id, activity_type, details)
    VALUES (p_user_id, 'achievement_earned', jsonb_build_object(
      'achievement', 'vocab_collector_100',
      'points', 500,
      'earned_at', NOW()
    ));
    
    RETURN QUERY SELECT
      'collection'::TEXT,
      'Vocab Collector'::TEXT,
      'Collected 100 vocabulary words'::TEXT,
      500,
      true;
  END IF;
  
  -- Check mastery achievements
  IF mastered_count >= 50 AND NOT EXISTS (
    SELECT 1 FROM public.user_activity 
    WHERE user_id = p_user_id 
    AND activity_type = 'achievement_earned' 
    AND details->>'achievement' = 'word_master_50'
  ) THEN
    INSERT INTO public.user_activity (user_id, activity_type, details)
    VALUES (p_user_id, 'achievement_earned', jsonb_build_object(
      'achievement', 'word_master_50',
      'points', 1000,
      'earned_at', NOW()
    ));
    
    RETURN QUERY SELECT
      'mastery'::TEXT,
      'Word Master'::TEXT,
      'Mastered 50 vocabulary words'::TEXT,
      1000,
      true;
  END IF;
  
  -- Check study streak achievements
  IF streak_days >= 7 AND NOT EXISTS (
    SELECT 1 FROM public.user_activity 
    WHERE user_id = p_user_id 
    AND activity_type = 'achievement_earned' 
    AND details->>'achievement' = 'study_streak_7'
  ) THEN
    INSERT INTO public.user_activity (user_id, activity_type, details)
    VALUES (p_user_id, 'achievement_earned', jsonb_build_object(
      'achievement', 'study_streak_7',
      'points', 300,
      'earned_at', NOW()
    ));
    
    RETURN QUERY SELECT
      'streak'::TEXT,
      'Weekly Warrior'::TEXT,
      'Maintained a 7-day study streak'::TEXT,
      300,
      true;
  END IF;
  
  -- Check dedication achievements
  IF study_hours >= 10 AND NOT EXISTS (
    SELECT 1 FROM public.user_activity 
    WHERE user_id = p_user_id 
    AND activity_type = 'achievement_earned' 
    AND details->>'achievement' = 'dedicated_learner_10h'
  ) THEN
    INSERT INTO public.user_activity (user_id, activity_type, details)
    VALUES (p_user_id, 'achievement_earned', jsonb_build_object(
      'achievement', 'dedicated_learner_10h',
      'points', 750,
      'earned_at', NOW()
    ));
    
    RETURN QUERY SELECT
      'dedication'::TEXT,
      'Dedicated Learner'::TEXT,
      'Studied for 10+ hours total'::TEXT,
      750,
      true;
  END IF;
  
  -- Return all previously earned achievements
  RETURN QUERY
  SELECT
    COALESCE((details->>'category'), 'general')::TEXT,
    COALESCE((details->>'achievement'), 'unknown')::TEXT,
    COALESCE((details->>'description'), 'Achievement earned')::TEXT,
    COALESCE((details->>'points')::INTEGER, 0),
    false -- not newly earned
  FROM public.user_activity
  WHERE user_id = p_user_id
    AND activity_type = 'achievement_earned'
  ORDER BY created_at DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 7. PERFORMANCE OPTIMIZATION

-- Function to cleanup and optimize user data
CREATE OR REPLACE FUNCTION public.cleanup_old_sessions()
RETURNS void AS $$
BEGIN
  -- Archive very old learning sessions (older than 1 year)
  UPDATE public.learning_sessions
  SET notes = COALESCE(notes, '') || ' [ARCHIVED]'
  WHERE created_at < NOW() - INTERVAL '1 year'
    AND notes NOT LIKE '%[ARCHIVED]%';
  
  -- Delete incomplete sessions older than 30 days
  DELETE FROM public.learning_sessions
  WHERE completed_at IS NULL
    AND started_at < NOW() - INTERVAL '30 days';
  
  -- Clean up old activity logs (keep only 90 days)
  DELETE FROM public.user_activity
  WHERE created_at < NOW() - INTERVAL '90 days'
    AND activity_type NOT IN ('achievement_earned', 'account_created');
  
  -- Update vocabulary statistics
  REFRESH MATERIALIZED VIEW IF EXISTS public.user_vocabulary_stats;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Schedule cleanup job
SELECT cron.schedule(
  'cleanup-old-data',
  '0 3 * * 0', -- Weekly on Sunday at 3 AM
  'SELECT public.cleanup_old_sessions();'
);

-- Grant necessary permissions
GRANT EXECUTE ON FUNCTION public.calculate_user_statistics(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION public.calculate_next_review_date(INTEGER, TIMESTAMPTZ, BOOLEAN) TO authenticated;
GRANT EXECUTE ON FUNCTION public.get_spaced_repetition_items(UUID, INTEGER, TEXT, TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION public.generate_quiz_questions(UUID, INTEGER, TEXT, TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION public.analyze_learning_patterns(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION public.smart_vocabulary_import(UUID, JSONB, TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION public.check_and_award_achievements(UUID) TO authenticated;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_vocabulary_next_review ON public.vocabulary(user_id, next_review) WHERE next_review IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_learning_sessions_accuracy ON public.learning_sessions(user_id, accuracy_rate) WHERE accuracy_rate IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_user_activity_achievements ON public.user_activity(user_id, activity_type) WHERE activity_type = 'achievement_earned';