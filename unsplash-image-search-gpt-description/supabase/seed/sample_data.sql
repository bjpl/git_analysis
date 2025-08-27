-- Insert sample users (these will be created through auth, but we can set up their profiles)
-- Note: In production, these would be created through the auth.users table and trigger

-- Sample vocabulary items for development
INSERT INTO public.vocabulary_items (
  user_id,
  word,
  definition,
  pronunciation,
  part_of_speech,
  example_sentence,
  difficulty_level,
  source_language,
  target_language,
  translation,
  image_url,
  image_alt_text,
  image_source,
  tags,
  mastery_level,
  times_practiced,
  times_correct
) VALUES 
  (
    '00000000-0000-0000-0000-000000000001'::uuid,
    'mountain',
    'A large landform that rises prominently above its surroundings, generally exhibiting steep slopes',
    '/ˈmaʊntɪn/',
    'noun',
    'The mountain peak was covered in snow.',
    'easy',
    'en',
    'es',
    'montaña',
    'https://images.unsplash.com/photo-1506905925346-21bda4d32df4',
    'Snow-covered mountain peak against blue sky',
    'unsplash',
    ARRAY['nature', 'geography', 'landscape'],
    2,
    5,
    4
  ),
  (
    '00000000-0000-0000-0000-000000000001'::uuid,
    'serendipity',
    'The occurrence and development of events by chance in a happy or beneficial way',
    '/ˌsɛrənˈdɪpɪti/',
    'noun',
    'Finding that book was pure serendipity.',
    'hard',
    'en',
    'es',
    'serendipia',
    'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d',
    'Person discovering something unexpected in a library',
    'unsplash',
    ARRAY['emotion', 'philosophy', 'chance'],
    1,
    2,
    1
  ),
  (
    '00000000-0000-0000-0000-000000000001'::uuid,
    'bicycle',
    'A vehicle consisting of two wheels held in a frame one behind the other, propelled by pedals',
    '/ˈbaɪsɪkəl/',
    'noun',
    'She rides her bicycle to work every day.',
    'easy',
    'en',
    'fr',
    'bicyclette',
    'https://images.unsplash.com/photo-1544191696-15693980b3b5',
    'Red bicycle parked against a wall',
    'unsplash',
    ARRAY['transportation', 'exercise', 'vehicle'],
    3,
    8,
    7
  ),
  (
    '00000000-0000-0000-0000-000000000001'::uuid,
    'tranquil',
    'Free from disturbance; calm and peaceful',
    '/ˈtræŋkwɪl/',
    'adjective',
    'The tranquil lake reflected the sunset perfectly.',
    'medium',
    'en',
    'es',
    'tranquilo',
    'https://images.unsplash.com/photo-1439066615861-d1af74d74000',
    'Calm lake at sunset with perfect reflections',
    'unsplash',
    ARRAY['emotion', 'peace', 'nature'],
    2,
    6,
    5
  );

-- Sample search sessions
INSERT INTO public.search_sessions (
  user_id,
  query,
  style,
  results_count,
  selected_image_id,
  duration_seconds
) VALUES 
  (
    '00000000-0000-0000-0000-000000000001'::uuid,
    'mountain landscape',
    'realistic',
    12,
    'photo-1506905925346-21bda4d32df4',
    45
  ),
  (
    '00000000-0000-0000-0000-000000000001'::uuid,
    'bicycle transportation',
    'minimalist',
    8,
    'photo-1544191696-15693980b3b5',
    28
  ),
  (
    '00000000-0000-0000-0000-000000000001'::uuid,
    'peaceful nature',
    'artistic',
    15,
    'photo-1439066615861-d1af74d74000',
    62
  );

-- Sample quiz results
INSERT INTO public.quiz_results (
  user_id,
  quiz_type,
  vocabulary_item_id,
  question,
  user_answer,
  correct_answer,
  is_correct,
  response_time_ms,
  difficulty
) VALUES 
  (
    '00000000-0000-0000-0000-000000000001'::uuid,
    'multiple_choice',
    (SELECT id FROM public.vocabulary_items WHERE word = 'mountain' LIMIT 1),
    'What is the Spanish translation of "mountain"?',
    'montaña',
    'montaña',
    true,
    3500,
    'easy'
  ),
  (
    '00000000-0000-0000-0000-000000000001'::uuid,
    'flashcard',
    (SELECT id FROM public.vocabulary_items WHERE word = 'tranquil' LIMIT 1),
    'Define: tranquil',
    'calm and peaceful',
    'free from disturbance; calm and peaceful',
    true,
    5200,
    'medium'
  ),
  (
    '00000000-0000-0000-0000-000000000001'::uuid,
    'typing',
    (SELECT id FROM public.vocabulary_items WHERE word = 'serendipity' LIMIT 1),
    'Type the definition of serendipity',
    'happy coincidence',
    'the occurrence and development of events by chance in a happy or beneficial way',
    false,
    12000,
    'hard'
  );

-- Sample shared lists
INSERT INTO public.shared_lists (
  owner_id,
  title,
  description,
  is_public,
  vocabulary_items,
  tags
) VALUES 
  (
    '00000000-0000-0000-0000-000000000001'::uuid,
    'Nature Vocabulary',
    'Essential vocabulary for describing natural landscapes and environments',
    true,
    ARRAY[
      (SELECT id FROM public.vocabulary_items WHERE word = 'mountain' LIMIT 1),
      (SELECT id FROM public.vocabulary_items WHERE word = 'tranquil' LIMIT 1)
    ],
    ARRAY['nature', 'geography', 'environment']
  ),
  (
    '00000000-0000-0000-0000-000000000001'::uuid,
    'Advanced English Words',
    'Challenging vocabulary for advanced learners',
    false,
    ARRAY[
      (SELECT id FROM public.vocabulary_items WHERE word = 'serendipity' LIMIT 1)
    ],
    ARRAY['advanced', 'philosophy', 'abstract']
  );

-- Sample user preferences
INSERT INTO public.user_preferences (
  user_id,
  notifications_enabled,
  email_reminders,
  study_reminder_time,
  auto_play_pronunciation,
  show_pronunciation,
  show_example_sentences,
  quiz_auto_advance,
  dark_mode,
  language_interface,
  spaced_repetition_enabled,
  daily_goal_notifications
) VALUES 
  (
    '00000000-0000-0000-0000-000000000001'::uuid,
    true,
    true,
    '19:00:00',
    false,
    true,
    true,
    false,
    false,
    'en',
    true,
    true
  );