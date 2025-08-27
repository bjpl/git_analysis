-- Supabase Realtime Configuration
-- Enable realtime for collaborative features

-- Enable realtime on tables that need live updates
ALTER PUBLICATION supabase_realtime ADD TABLE public.vocabulary;
ALTER PUBLICATION supabase_realtime ADD TABLE public.vocabulary_collections;
ALTER PUBLICATION supabase_realtime ADD TABLE public.vocabulary_collection_items;
ALTER PUBLICATION supabase_realtime ADD TABLE public.learning_sessions;
ALTER PUBLICATION supabase_realtime ADD TABLE public.quiz_attempts;
ALTER PUBLICATION supabase_realtime ADD TABLE public.user_activity;

-- Presence system for study groups
CREATE TABLE public.user_presence (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
  room_type TEXT NOT NULL CHECK (room_type IN ('collection', 'session', 'quiz', 'general')),
  room_id UUID NOT NULL, -- collection_id, session_id, etc.
  
  -- Presence data
  status TEXT DEFAULT 'online' CHECK (status IN ('online', 'idle', 'offline')),
  activity TEXT, -- 'studying', 'taking_quiz', 'browsing'
  last_seen TIMESTAMPTZ DEFAULT NOW(),
  
  -- User info for display
  user_data JSONB DEFAULT '{}'::jsonb, -- username, avatar, etc.
  
  -- Session metadata
  joined_at TIMESTAMPTZ DEFAULT NOW(),
  metadata JSONB DEFAULT '{}'::jsonb,
  
  UNIQUE(user_id, room_type, room_id)
);

CREATE INDEX idx_user_presence_room ON public.user_presence(room_type, room_id);
CREATE INDEX idx_user_presence_user ON public.user_presence(user_id);
CREATE INDEX idx_user_presence_active ON public.user_presence(status) WHERE status != 'offline';

-- Enable realtime for presence
ALTER PUBLICATION supabase_realtime ADD TABLE public.user_presence;

-- RLS for presence
ALTER TABLE public.user_presence ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own presence" ON public.user_presence
  FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view room presence" ON public.user_presence
  FOR SELECT USING (
    -- Allow viewing presence in public collections
    (room_type = 'collection' AND EXISTS (
      SELECT 1 FROM public.vocabulary_collections vc
      WHERE vc.id = room_id::UUID 
      AND (vc.is_public = true OR vc.is_collaborative = true OR vc.user_id = auth.uid())
    ))
    OR
    -- Allow viewing presence in own sessions
    (room_type = 'session' AND EXISTS (
      SELECT 1 FROM public.learning_sessions ls
      WHERE ls.id = room_id::UUID AND ls.user_id = auth.uid()
    ))
    OR
    -- Allow viewing general presence
    room_type = 'general'
  );

-- Function to clean up stale presence records
CREATE OR REPLACE FUNCTION public.cleanup_stale_presence()
RETURNS void AS $$
BEGIN
  -- Remove presence records older than 5 minutes with no heartbeat
  DELETE FROM public.user_presence 
  WHERE last_seen < NOW() - INTERVAL '5 minutes';
  
  -- Mark users as offline if they haven't been seen in 2 minutes
  UPDATE public.user_presence 
  SET status = 'offline'
  WHERE last_seen < NOW() - INTERVAL '2 minutes' 
  AND status != 'offline';
END;
$$ LANGUAGE plpgsql;

-- Schedule cleanup every minute
SELECT cron.schedule(
  'cleanup-presence',
  '* * * * *', -- Every minute
  'SELECT public.cleanup_stale_presence();'
);

-- Collaborative vocabulary editing
CREATE TABLE public.vocabulary_edit_locks (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  vocabulary_id UUID REFERENCES public.vocabulary(id) ON DELETE CASCADE NOT NULL,
  user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
  lock_type TEXT DEFAULT 'editing' CHECK (lock_type IN ('editing', 'viewing')),
  
  -- Lock details
  locked_at TIMESTAMPTZ DEFAULT NOW(),
  expires_at TIMESTAMPTZ DEFAULT NOW() + INTERVAL '5 minutes',
  
  -- Metadata
  user_data JSONB DEFAULT '{}'::jsonb,
  
  UNIQUE(vocabulary_id, user_id)
);

CREATE INDEX idx_vocabulary_locks_vocab ON public.vocabulary_edit_locks(vocabulary_id);
CREATE INDEX idx_vocabulary_locks_expires ON public.vocabulary_edit_locks(expires_at);

-- Enable realtime for edit locks
ALTER PUBLICATION supabase_realtime ADD TABLE public.vocabulary_edit_locks;

-- RLS for edit locks
ALTER TABLE public.vocabulary_edit_locks ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own locks" ON public.vocabulary_edit_locks
  FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view vocabulary locks" ON public.vocabulary_edit_locks
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM public.vocabulary v
      WHERE v.id = vocabulary_id 
      AND (v.user_id = auth.uid() OR EXISTS (
        SELECT 1 FROM public.vocabulary_collection_items vci
        JOIN public.vocabulary_collections vc ON vci.collection_id = vc.id
        WHERE vci.vocabulary_id = v.id
        AND (vc.is_collaborative = true AND vc.user_id = auth.uid())
      ))
    )
  );

-- Function to clean up expired locks
CREATE OR REPLACE FUNCTION public.cleanup_expired_locks()
RETURNS void AS $$
BEGIN
  DELETE FROM public.vocabulary_edit_locks 
  WHERE expires_at < NOW();
END;
$$ LANGUAGE plpgsql;

-- Schedule lock cleanup every minute
SELECT cron.schedule(
  'cleanup-locks',
  '* * * * *', -- Every minute
  'SELECT public.cleanup_expired_locks();'
);

-- Activity notifications
CREATE TABLE public.user_notifications (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
  
  -- Notification content
  type TEXT NOT NULL CHECK (type IN ('vocabulary_shared', 'collection_invite', 'quiz_challenge', 'achievement', 'system')),
  title TEXT NOT NULL,
  message TEXT NOT NULL,
  
  -- Notification metadata
  data JSONB DEFAULT '{}'::jsonb,
  priority TEXT DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
  
  -- Status
  is_read BOOLEAN DEFAULT FALSE,
  read_at TIMESTAMPTZ,
  
  -- Actions
  action_url TEXT,
  action_label TEXT,
  
  -- Timing
  created_at TIMESTAMPTZ DEFAULT NOW(),
  expires_at TIMESTAMPTZ -- Optional expiration
);

CREATE INDEX idx_user_notifications_user ON public.user_notifications(user_id);
CREATE INDEX idx_user_notifications_unread ON public.user_notifications(user_id, is_read) WHERE NOT is_read;
CREATE INDEX idx_user_notifications_type ON public.user_notifications(user_id, type);

-- Enable realtime for notifications
ALTER PUBLICATION supabase_realtime ADD TABLE public.user_notifications;

-- RLS for notifications
ALTER TABLE public.user_notifications ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own notifications" ON public.user_notifications
  FOR ALL USING (auth.uid() = user_id);

-- Live quiz competitions
CREATE TABLE public.quiz_rooms (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  
  -- Room details
  name TEXT NOT NULL,
  description TEXT,
  room_code TEXT UNIQUE NOT NULL, -- 6-digit code for joining
  
  -- Creator and settings
  creator_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
  is_public BOOLEAN DEFAULT FALSE,
  max_participants INTEGER DEFAULT 10,
  
  -- Quiz configuration
  vocabulary_collection_id UUID REFERENCES public.vocabulary_collections(id) ON DELETE SET NULL,
  quiz_type TEXT DEFAULT 'translation' CHECK (quiz_type IN ('translation', 'multiple_choice', 'mixed')),
  question_count INTEGER DEFAULT 10,
  time_per_question INTEGER DEFAULT 30, -- seconds
  
  -- Room state
  status TEXT DEFAULT 'waiting' CHECK (status IN ('waiting', 'active', 'finished', 'cancelled')),
  current_question INTEGER DEFAULT 0,
  started_at TIMESTAMPTZ,
  finished_at TIMESTAMPTZ,
  
  -- Results
  winner_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_quiz_rooms_code ON public.quiz_rooms(room_code);
CREATE INDEX idx_quiz_rooms_creator ON public.quiz_rooms(creator_id);
CREATE INDEX idx_quiz_rooms_status ON public.quiz_rooms(status);

-- Quiz room participants
CREATE TABLE public.quiz_room_participants (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  room_id UUID REFERENCES public.quiz_rooms(id) ON DELETE CASCADE NOT NULL,
  user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
  
  -- Participant state
  is_ready BOOLEAN DEFAULT FALSE,
  current_score INTEGER DEFAULT 0,
  current_streak INTEGER DEFAULT 0,
  
  -- Answers for current quiz
  answers JSONB DEFAULT '[]'::jsonb,
  
  joined_at TIMESTAMPTZ DEFAULT NOW(),
  last_activity TIMESTAMPTZ DEFAULT NOW(),
  
  UNIQUE(room_id, user_id)
);

CREATE INDEX idx_quiz_participants_room ON public.quiz_room_participants(room_id);
CREATE INDEX idx_quiz_participants_user ON public.quiz_room_participants(user_id);

-- Enable realtime for quiz rooms
ALTER PUBLICATION supabase_realtime ADD TABLE public.quiz_rooms;
ALTER PUBLICATION supabase_realtime ADD TABLE public.quiz_room_participants;

-- RLS for quiz rooms
ALTER TABLE public.quiz_rooms ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.quiz_room_participants ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Everyone can view public quiz rooms" ON public.quiz_rooms
  FOR SELECT USING (is_public = true OR creator_id = auth.uid());

CREATE POLICY "Creators can manage their quiz rooms" ON public.quiz_rooms
  FOR ALL USING (auth.uid() = creator_id);

CREATE POLICY "Users can manage their participation" ON public.quiz_room_participants
  FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Room participants can view each other" ON public.quiz_room_participants
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM public.quiz_room_participants qrp2
      WHERE qrp2.room_id = public.quiz_room_participants.room_id
      AND qrp2.user_id = auth.uid()
    )
  );

-- Function to generate quiz room codes
CREATE OR REPLACE FUNCTION public.generate_quiz_room_code()
RETURNS TEXT AS $$
DECLARE
  code TEXT;
  exists_code BOOLEAN;
BEGIN
  LOOP
    -- Generate 6-digit code
    code := LPAD(FLOOR(RANDOM() * 1000000)::TEXT, 6, '0');
    
    -- Check if code already exists
    SELECT EXISTS(SELECT 1 FROM public.quiz_rooms WHERE room_code = code) INTO exists_code;
    
    -- If code doesn't exist, we can use it
    IF NOT exists_code THEN
      RETURN code;
    END IF;
  END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-generate room codes
CREATE OR REPLACE FUNCTION public.set_quiz_room_code()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.room_code IS NULL THEN
    NEW.room_code := public.generate_quiz_room_code();
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_quiz_room_code
  BEFORE INSERT ON public.quiz_rooms
  FOR EACH ROW EXECUTE FUNCTION public.set_quiz_room_code();

-- Function to clean up inactive quiz rooms
CREATE OR REPLACE FUNCTION public.cleanup_inactive_quiz_rooms()
RETURNS void AS $$
BEGIN
  -- Cancel rooms waiting for too long (1 hour)
  UPDATE public.quiz_rooms 
  SET status = 'cancelled', finished_at = NOW()
  WHERE status = 'waiting' 
  AND created_at < NOW() - INTERVAL '1 hour';
  
  -- Finish rooms active for too long (2 hours)
  UPDATE public.quiz_rooms 
  SET status = 'finished', finished_at = NOW()
  WHERE status = 'active' 
  AND started_at < NOW() - INTERVAL '2 hours';
  
  -- Remove participants who haven't been active
  DELETE FROM public.quiz_room_participants
  WHERE last_activity < NOW() - INTERVAL '10 minutes'
  AND room_id IN (
    SELECT id FROM public.quiz_rooms 
    WHERE status = 'waiting'
  );
END;
$$ LANGUAGE plpgsql;

-- Schedule quiz room cleanup every 5 minutes
SELECT cron.schedule(
  'cleanup-quiz-rooms',
  '*/5 * * * *', -- Every 5 minutes
  'SELECT public.cleanup_inactive_quiz_rooms();'
);

-- Triggers for updated_at on new tables
CREATE TRIGGER trigger_quiz_rooms_updated_at
  BEFORE UPDATE ON public.quiz_rooms
  FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();