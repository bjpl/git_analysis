-- Demo data for development and testing
-- This seed file creates sample data for testing the application

-- Insert demo users (these will be created through the auth system)
-- Note: In production, users are created through Supabase Auth

-- Demo vocabulary entries for user testing
-- This assumes test users exist with known UUIDs (you'll need to update these)

-- First, let's create some demo shared collections
INSERT INTO shared_collections (id, owner_id, name, description, is_public, is_featured, category, difficulty_level, tags) VALUES
  ('550e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440000', 'Nature Vocabulary', 'Essential Spanish vocabulary for describing nature scenes', true, true, 'nature', 2, ARRAY['nature', 'outdoors', 'landscape']),
  ('550e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440000', 'Food & Cooking', 'Kitchen and food-related Spanish terms', true, false, 'food', 1, ARRAY['food', 'cooking', 'kitchen']),
  ('550e8400-e29b-41d4-a716-446655440003', '550e8400-e29b-41d4-a716-446655440000', 'Advanced Literature', 'Complex vocabulary for literary Spanish', true, false, 'literature', 4, ARRAY['literature', 'advanced', 'poetry']);

-- Demo vocabulary entries
INSERT INTO vocabulary (user_id, spanish_text, english_translation, context, word_type, learning_score, difficulty_level, tags) VALUES
  -- Nature vocabulary
  ('550e8400-e29b-41d4-a716-446655440000', 'el bosque', 'the forest', 'Un hermoso bosque verde se extiende hasta el horizonte.', 'sustantivo', 85, 2, ARRAY['nature', 'landscape']),
  ('550e8400-e29b-41d4-a716-446655440000', 'las montañas', 'the mountains', 'Las montañas cubiertas de nieve brillan bajo el sol.', 'sustantivo', 90, 2, ARRAY['nature', 'landscape']),
  ('550e8400-e29b-41d4-a716-446655440000', 'el río cristalino', 'the crystal clear river', 'El río cristalino serpentea entre las rocas.', 'frase', 70, 3, ARRAY['nature', 'water']),
  ('550e8400-e29b-41d4-a716-446655440000', 'florecer', 'to bloom', 'Las flores empiezan a florecer en primavera.', 'verbo', 75, 2, ARRAY['nature', 'plants']),
  ('550e8400-e29b-41d4-a716-446655440000', 'majestuoso', 'majestic', 'El paisaje majestuoso nos dejó sin palabras.', 'adjetivo', 80, 3, ARRAY['nature', 'descriptive']),
  
  -- Food vocabulary
  ('550e8400-e29b-41d4-a716-446655440000', 'la cocina', 'the kitchen', 'Me gusta cocinar en mi cocina moderna.', 'sustantivo', 95, 1, ARRAY['food', 'kitchen']),
  ('550e8400-e29b-41d4-a716-446655440000', 'los ingredientes', 'the ingredients', 'Necesito comprar ingredientes frescos para la cena.', 'sustantivo', 88, 2, ARRAY['food', 'cooking']),
  ('550e8400-e29b-41d4-a716-446655440000', 'hervir', 'to boil', 'Voy a hervir agua para la pasta.', 'verbo', 82, 2, ARRAY['food', 'cooking']),
  ('550e8400-e29b-41d4-a716-446655440000', 'delicioso', 'delicious', 'Este plato está absolutamente delicioso.', 'adjetivo', 92, 1, ARRAY['food', 'taste']),
  ('550e8400-e29b-41d4-a716-446655440000', 'el sabor exquisito', 'the exquisite flavor', 'El sabor exquisito de esta comida es memorable.', 'frase', 65, 4, ARRAY['food', 'taste']),
  
  -- Advanced vocabulary
  ('550e8400-e29b-41d4-a716-446655440000', 'la melancolía', 'melancholy', 'Una profunda melancolía invadía su corazón.', 'sustantivo', 60, 4, ARRAY['emotions', 'literature']),
  ('550e8400-e29b-41d4-a716-446655440000', 'contemplar', 'to contemplate', 'Le gusta contemplar las estrellas por la noche.', 'verbo', 72, 3, ARRAY['actions', 'philosophical']),
  ('550e8400-e29b-41d4-a716-446655440000', 'efímero', 'ephemeral', 'La belleza de las flores es efímera pero intensa.', 'adjetivo', 55, 5, ARRAY['descriptive', 'philosophical']);

-- Demo sessions
INSERT INTO sessions (user_id, search_query, generated_description, style_used, level_used, duration_seconds, vocabulary_learned) VALUES
  ('550e8400-e29b-41d4-a716-446655440000', 'forest landscape', 'Un bosque majestuoso se extiende hasta donde alcanza la vista, con árboles centenarios que susurran secretos al viento.', 'poetic', 'intermediate', 450, 5),
  ('550e8400-e29b-41d4-a716-446655440000', 'cooking kitchen', 'La cocina moderna está equipada con electrodomésticos de última generación y una isla central donde se preparan deliciosas comidas.', 'academic', 'beginner', 320, 3),
  ('550e8400-e29b-41d4-a716-446655440000', 'mountain sunset', 'El atardecer pinta las montañas con tonos dorados y púrpuras, creando un espectáculo natural de incomparable belleza.', 'poetic', 'advanced', 380, 4);

-- Demo quiz attempts
INSERT INTO quiz_attempts (user_id, vocabulary_id, quiz_type, question_text, user_answer, correct_answer, is_correct, response_time_ms) VALUES
  ('550e8400-e29b-41d4-a716-446655440000', (SELECT id FROM vocabulary WHERE spanish_text = 'el bosque' LIMIT 1), 'translation', 'What does "el bosque" mean in English?', 'the forest', 'the forest', true, 2340),
  ('550e8400-e29b-41d4-a716-446655440000', (SELECT id FROM vocabulary WHERE spanish_text = 'las montañas' LIMIT 1), 'translation', 'What does "las montañas" mean in English?', 'the mountains', 'the mountains', true, 1890),
  ('550e8400-e29b-41d4-a716-446655440000', (SELECT id FROM vocabulary WHERE spanish_text = 'la melancolía' LIMIT 1), 'translation', 'What does "la melancolía" mean in English?', 'sadness', 'melancholy', false, 4560);

-- Map vocabulary to collections
INSERT INTO collection_vocabulary (collection_id, vocabulary_id, order_index) VALUES
  -- Nature collection
  ('550e8400-e29b-41d4-a716-446655440001', (SELECT id FROM vocabulary WHERE spanish_text = 'el bosque' LIMIT 1), 1),
  ('550e8400-e29b-41d4-a716-446655440001', (SELECT id FROM vocabulary WHERE spanish_text = 'las montañas' LIMIT 1), 2),
  ('550e8400-e29b-41d4-a716-446655440001', (SELECT id FROM vocabulary WHERE spanish_text = 'el río cristalino' LIMIT 1), 3),
  ('550e8400-e29b-41d4-a716-446655440001', (SELECT id FROM vocabulary WHERE spanish_text = 'florecer' LIMIT 1), 4),
  ('550e8400-e29b-41d4-a716-446655440001', (SELECT id FROM vocabulary WHERE spanish_text = 'majestuoso' LIMIT 1), 5),
  
  -- Food collection
  ('550e8400-e29b-41d4-a716-446655440002', (SELECT id FROM vocabulary WHERE spanish_text = 'la cocina' LIMIT 1), 1),
  ('550e8400-e29b-41d4-a716-446655440002', (SELECT id FROM vocabulary WHERE spanish_text = 'los ingredientes' LIMIT 1), 2),
  ('550e8400-e29b-41d4-a716-446655440002', (SELECT id FROM vocabulary WHERE spanish_text = 'hervir' LIMIT 1), 3),
  ('550e8400-e29b-41d4-a716-446655440002', (SELECT id FROM vocabulary WHERE spanish_text = 'delicioso' LIMIT 1), 4),
  ('550e8400-e29b-41d4-a716-446655440002', (SELECT id FROM vocabulary WHERE spanish_text = 'el sabor exquisito' LIMIT 1), 5),
  
  -- Literature collection
  ('550e8400-e29b-41d4-a716-446655440003', (SELECT id FROM vocabulary WHERE spanish_text = 'la melancolía' LIMIT 1), 1),
  ('550e8400-e29b-41d4-a716-446655440003', (SELECT id FROM vocabulary WHERE spanish_text = 'contemplar' LIMIT 1), 2),
  ('550e8400-e29b-41d4-a716-446655440003', (SELECT id FROM vocabulary WHERE spanish_text = 'efímero' LIMIT 1), 3);

-- Demo achievements
INSERT INTO achievements (user_id, achievement_type, achievement_name, description, icon_url) VALUES
  ('550e8400-e29b-41d4-a716-446655440000', 'first_vocab', 'First Word', 'Added your first vocabulary word', '🎯'),
  ('550e8400-e29b-41d4-a716-446655440000', 'quiz_master', 'Quiz Master', 'Completed 10 quizzes with 80% accuracy', '🏆'),
  ('550e8400-e29b-41d4-a716-446655440000', 'streak_starter', 'Streak Starter', 'Maintained a 7-day learning streak', '🔥');

-- Demo learning streaks
INSERT INTO learning_streaks (user_id, current_streak, longest_streak, last_activity_date) VALUES
  ('550e8400-e29b-41d4-a716-446655440000', 5, 12, CURRENT_DATE);

-- Demo analytics events (anonymized)
INSERT INTO analytics_events (user_id, event_type, event_data, page_url) VALUES
  ('550e8400-e29b-41d4-a716-446655440000', 'page_view', '{"page": "home"}', '/'),
  ('550e8400-e29b-41d4-a716-446655440000', 'search_performed', '{"query": "forest", "results": 10}', '/search'),
  ('550e8400-e29b-41d4-a716-446655440000', 'vocabulary_added', '{"word": "el bosque", "source": "description"}', '/search'),
  ('550e8400-e29b-41d4-a716-446655440000', 'quiz_completed', '{"score": 8, "total": 10, "accuracy": 0.8}', '/quiz'),
  (NULL, 'anonymous_page_view', '{"page": "home"}', '/'),
  (NULL, 'anonymous_search', '{"query": "mountain"}', '/search');

-- Function to generate more demo data if needed
CREATE OR REPLACE FUNCTION generate_demo_analytics(days INTEGER DEFAULT 30)
RETURNS VOID AS $$
DECLARE
  day_counter INTEGER := 0;
  demo_user_id UUID := '550e8400-e29b-41d4-a716-446655440000';
BEGIN
  WHILE day_counter < days LOOP
    -- Generate daily page views
    INSERT INTO analytics_events (user_id, event_type, event_data, created_at) VALUES
      (demo_user_id, 'daily_login', '{}', CURRENT_DATE - day_counter);
    
    -- Generate some vocabulary learning events
    IF random() > 0.3 THEN
      INSERT INTO analytics_events (user_id, event_type, event_data, created_at) VALUES
        (demo_user_id, 'vocabulary_reviewed', '{"count": ' || (random() * 10 + 1)::INTEGER || '}', CURRENT_DATE - day_counter);
    END IF;
    
    -- Generate quiz events
    IF random() > 0.6 THEN
      INSERT INTO analytics_events (user_id, event_type, event_data, created_at) VALUES
        (demo_user_id, 'quiz_completed', '{"score": ' || (random() * 5 + 5)::INTEGER || ', "total": 10}', CURRENT_DATE - day_counter);
    END IF;
    
    day_counter := day_counter + 1;
  END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Generate 30 days of demo analytics
SELECT generate_demo_analytics(30);

-- Drop the demo function
DROP FUNCTION generate_demo_analytics(INTEGER);