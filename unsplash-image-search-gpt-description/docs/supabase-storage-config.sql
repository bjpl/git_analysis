-- Supabase Storage Configuration
-- Create storage buckets with proper policies

-- 1. Image Cache Bucket (Public)
-- Stores cached Unsplash images for faster loading
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'image-cache',
  'image-cache',
  true,
  52428800, -- 50MB limit per file
  ARRAY['image/jpeg', 'image/png', 'image/webp']
);

-- Storage policy for image-cache bucket
CREATE POLICY "Public image cache read access" ON storage.objects
  FOR SELECT USING (bucket_id = 'image-cache');

CREATE POLICY "Authenticated users can upload cached images" ON storage.objects
  FOR INSERT WITH CHECK (
    bucket_id = 'image-cache' 
    AND auth.role() = 'authenticated'
  );

CREATE POLICY "Users can update own cached images" ON storage.objects
  FOR UPDATE USING (
    bucket_id = 'image-cache' 
    AND auth.uid()::text = (storage.foldername(name))[1]
  );

CREATE POLICY "Users can delete own cached images" ON storage.objects
  FOR DELETE USING (
    bucket_id = 'image-cache' 
    AND auth.uid()::text = (storage.foldername(name))[1]
  );

-- 2. User Uploads Bucket (Private)
-- Profile pictures, custom images uploaded by users
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'user-uploads',
  'user-uploads',
  false,
  10485760, -- 10MB limit per file
  ARRAY['image/jpeg', 'image/png', 'image/webp', 'image/gif']
);

-- Storage policy for user-uploads bucket
CREATE POLICY "Users can view own uploads" ON storage.objects
  FOR SELECT USING (
    bucket_id = 'user-uploads' 
    AND auth.uid()::text = (storage.foldername(name))[1]
  );

CREATE POLICY "Users can upload to own folder" ON storage.objects
  FOR INSERT WITH CHECK (
    bucket_id = 'user-uploads' 
    AND auth.uid()::text = (storage.foldername(name))[1]
  );

CREATE POLICY "Users can update own uploads" ON storage.objects
  FOR UPDATE USING (
    bucket_id = 'user-uploads' 
    AND auth.uid()::text = (storage.foldername(name))[1]
  );

CREATE POLICY "Users can delete own uploads" ON storage.objects
  FOR DELETE USING (
    bucket_id = 'user-uploads' 
    AND auth.uid()::text = (storage.foldername(name))[1]
  );

-- 3. Exports Bucket (Private, Temporary)
-- Generated export files (CSV, JSON)
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'exports',
  'exports',
  false,
  104857600, -- 100MB limit per file
  ARRAY['text/csv', 'application/json', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']
);

-- Storage policy for exports bucket
CREATE POLICY "Users can view own exports" ON storage.objects
  FOR SELECT USING (
    bucket_id = 'exports' 
    AND auth.uid()::text = (storage.foldername(name))[1]
  );

CREATE POLICY "System can create exports" ON storage.objects
  FOR INSERT WITH CHECK (
    bucket_id = 'exports'
    AND auth.role() = 'authenticated'
  );

CREATE POLICY "Users can delete own exports" ON storage.objects
  FOR DELETE USING (
    bucket_id = 'exports' 
    AND auth.uid()::text = (storage.foldername(name))[1]
  );

-- 4. Vocabulary Audio Bucket (Public)
-- Pronunciation files, TTS audio for vocabulary
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'vocabulary-audio',
  'vocabulary-audio',
  true,
  5242880, -- 5MB limit per file
  ARRAY['audio/mpeg', 'audio/wav', 'audio/mp4', 'audio/ogg']
);

-- Storage policy for vocabulary-audio bucket
CREATE POLICY "Public audio read access" ON storage.objects
  FOR SELECT USING (bucket_id = 'vocabulary-audio');

CREATE POLICY "Authenticated users can upload audio" ON storage.objects
  FOR INSERT WITH CHECK (
    bucket_id = 'vocabulary-audio' 
    AND auth.role() = 'authenticated'
  );

CREATE POLICY "Users can update audio files" ON storage.objects
  FOR UPDATE USING (
    bucket_id = 'vocabulary-audio' 
    AND auth.role() = 'authenticated'
  );

-- Functions for storage management

-- Function to clean up old cached images (older than 30 days)
CREATE OR REPLACE FUNCTION public.cleanup_old_cached_images()
RETURNS void AS $$
DECLARE
  old_files RECORD;
BEGIN
  -- Get files older than 30 days from image-cache bucket
  FOR old_files IN 
    SELECT name, bucket_id 
    FROM storage.objects 
    WHERE bucket_id = 'image-cache' 
    AND created_at < NOW() - INTERVAL '30 days'
  LOOP
    -- Delete old cached image
    PERFORM storage.delete_object(old_files.bucket_id, old_files.name);
  END LOOP;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to clean up expired export files (older than 24 hours)
CREATE OR REPLACE FUNCTION public.cleanup_expired_exports()
RETURNS void AS $$
DECLARE
  expired_files RECORD;
BEGIN
  -- Get files older than 24 hours from exports bucket
  FOR expired_files IN 
    SELECT name, bucket_id 
    FROM storage.objects 
    WHERE bucket_id = 'exports' 
    AND created_at < NOW() - INTERVAL '24 hours'
  LOOP
    -- Delete expired export file
    PERFORM storage.delete_object(expired_files.bucket_id, expired_files.name);
  END LOOP;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Schedule storage cleanup jobs
SELECT cron.schedule(
  'cleanup-cached-images',
  '0 2 * * *', -- Daily at 2 AM
  'SELECT public.cleanup_old_cached_images();'
);

SELECT cron.schedule(
  'cleanup-export-files',
  '0 */6 * * *', -- Every 6 hours
  'SELECT public.cleanup_expired_exports();'
);

-- Function to get storage usage by user
CREATE OR REPLACE FUNCTION public.get_user_storage_usage(user_uuid UUID)
RETURNS TABLE(
  bucket_name TEXT,
  file_count BIGINT,
  total_size_bytes BIGINT,
  total_size_mb NUMERIC
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    so.bucket_id as bucket_name,
    COUNT(*) as file_count,
    COALESCE(SUM(so.metadata->>'size')::BIGINT, 0) as total_size_bytes,
    ROUND(COALESCE(SUM(so.metadata->>'size')::BIGINT, 0) / 1048576.0, 2) as total_size_mb
  FROM storage.objects so
  WHERE so.bucket_id IN ('user-uploads', 'exports', 'image-cache')
  AND (storage.foldername(so.name))[1] = user_uuid::text
  GROUP BY so.bucket_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check storage quotas
CREATE OR REPLACE FUNCTION public.check_storage_quota(user_uuid UUID, bucket_name TEXT)
RETURNS TABLE(
  quota_mb INTEGER,
  used_mb NUMERIC,
  available_mb NUMERIC,
  quota_exceeded BOOLEAN
) AS $$
DECLARE
  user_subscription TEXT;
  quota_limit INTEGER;
  current_usage NUMERIC;
BEGIN
  -- Get user subscription tier
  SELECT subscription_tier INTO user_subscription
  FROM public.profiles
  WHERE id = user_uuid;
  
  -- Set quota based on subscription tier
  quota_limit := CASE 
    WHEN user_subscription = 'free' THEN 100 -- 100MB
    WHEN user_subscription = 'premium' THEN 1000 -- 1GB
    WHEN user_subscription = 'pro' THEN 5000 -- 5GB
    ELSE 100
  END;
  
  -- Calculate current usage for the bucket
  SELECT COALESCE(SUM(so.metadata->>'size')::BIGINT / 1048576.0, 0)
  INTO current_usage
  FROM storage.objects so
  WHERE so.bucket_id = bucket_name
  AND (storage.foldername(so.name))[1] = user_uuid::text;
  
  RETURN QUERY SELECT 
    quota_limit,
    current_usage,
    (quota_limit - current_usage),
    (current_usage > quota_limit);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- View for storage analytics
CREATE OR REPLACE VIEW public.storage_analytics AS
SELECT 
  so.bucket_id,
  COUNT(*) as total_files,
  SUM((so.metadata->>'size')::BIGINT) as total_bytes,
  ROUND(SUM((so.metadata->>'size')::BIGINT) / 1048576.0, 2) as total_mb,
  AVG((so.metadata->>'size')::BIGINT) as avg_file_size_bytes,
  MIN(so.created_at) as oldest_file,
  MAX(so.created_at) as newest_file
FROM storage.objects so
GROUP BY so.bucket_id;

-- Storage optimization recommendations
CREATE OR REPLACE FUNCTION public.get_storage_recommendations(user_uuid UUID)
RETURNS TABLE(
  recommendation_type TEXT,
  description TEXT,
  potential_savings_mb NUMERIC,
  action_required TEXT
) AS $$
BEGIN
  -- Recommendation 1: Clean up old cached images
  RETURN QUERY
  SELECT 
    'cleanup_cache'::TEXT,
    'Remove cached images older than 7 days'::TEXT,
    COALESCE(SUM((so.metadata->>'size')::BIGINT) / 1048576.0, 0),
    'Delete old cached images'::TEXT
  FROM storage.objects so
  WHERE so.bucket_id = 'image-cache'
  AND (storage.foldername(so.name))[1] = user_uuid::text
  AND so.created_at < NOW() - INTERVAL '7 days'
  HAVING COUNT(*) > 0;
  
  -- Recommendation 2: Compress large uploads
  RETURN QUERY
  SELECT 
    'compress_uploads'::TEXT,
    'Compress images larger than 2MB'::TEXT,
    COALESCE(SUM((so.metadata->>'size')::BIGINT * 0.3) / 1048576.0, 0), -- Assume 30% compression
    'Compress and re-upload large images'::TEXT
  FROM storage.objects so
  WHERE so.bucket_id = 'user-uploads'
  AND (storage.foldername(so.name))[1] = user_uuid::text
  AND (so.metadata->>'size')::BIGINT > 2097152 -- 2MB
  HAVING COUNT(*) > 0;
  
  -- Recommendation 3: Remove unused exports
  RETURN QUERY
  SELECT 
    'cleanup_exports'::TEXT,
    'Remove export files older than 2 hours'::TEXT,
    COALESCE(SUM((so.metadata->>'size')::BIGINT) / 1048576.0, 0),
    'Delete old export files'::TEXT
  FROM storage.objects so
  WHERE so.bucket_id = 'exports'
  AND (storage.foldername(so.name))[1] = user_uuid::text
  AND so.created_at < NOW() - INTERVAL '2 hours'
  HAVING COUNT(*) > 0;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Image optimization function
CREATE OR REPLACE FUNCTION public.optimize_user_images(user_uuid UUID)
RETURNS TABLE(
  optimized_count INTEGER,
  space_saved_mb NUMERIC,
  status TEXT
) AS $$
DECLARE
  optimization_count INTEGER := 0;
  space_saved NUMERIC := 0;
BEGIN
  -- This is a placeholder for image optimization logic
  -- In a real implementation, you would:
  -- 1. Retrieve images from storage
  -- 2. Optimize them (resize, compress, convert format)
  -- 3. Replace the original files
  -- 4. Update metadata
  
  -- For now, return placeholder values
  SELECT 0, 0.0, 'Image optimization feature coming soon'
  INTO optimization_count, space_saved, status;
  
  RETURN QUERY SELECT optimization_count, space_saved, status::TEXT;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant necessary permissions
GRANT EXECUTE ON FUNCTION public.cleanup_old_cached_images() TO authenticated;
GRANT EXECUTE ON FUNCTION public.cleanup_expired_exports() TO authenticated;
GRANT EXECUTE ON FUNCTION public.get_user_storage_usage(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION public.check_storage_quota(UUID, TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION public.get_storage_recommendations(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION public.optimize_user_images(UUID) TO authenticated;

-- Enable RLS on storage.objects (if not already enabled)
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;