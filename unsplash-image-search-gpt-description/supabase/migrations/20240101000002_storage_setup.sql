-- Create storage buckets

-- Image cache bucket (public) for caching Unsplash images
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'image-cache',
    'image-cache',
    true,
    10485760, -- 10MB
    ARRAY['image/jpeg', 'image/png', 'image/webp', 'image/gif']
);

-- User uploads bucket (private) for profile pictures and user content
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'user-uploads',
    'user-uploads', 
    false,
    5242880, -- 5MB
    ARRAY['image/jpeg', 'image/png', 'image/webp']
);

-- Exports bucket (private, temporary) for CSV/JSON exports
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'exports',
    'exports',
    false,
    52428800, -- 50MB
    ARRAY['text/csv', 'application/json', 'text/plain']
);

-- Storage policies for image-cache bucket (public read)
CREATE POLICY "Public can view cached images"
ON storage.objects FOR SELECT
USING (bucket_id = 'image-cache');

CREATE POLICY "Service role can manage cached images"
ON storage.objects FOR ALL
USING (bucket_id = 'image-cache' AND auth.role() = 'service_role');

-- Storage policies for user-uploads bucket
CREATE POLICY "Users can view own uploads"
ON storage.objects FOR SELECT
USING (bucket_id = 'user-uploads' AND auth.uid()::text = (storage.foldername(name))[1]);

CREATE POLICY "Users can upload own files"
ON storage.objects FOR INSERT
WITH CHECK (bucket_id = 'user-uploads' AND auth.uid()::text = (storage.foldername(name))[1]);

CREATE POLICY "Users can update own uploads"
ON storage.objects FOR UPDATE
USING (bucket_id = 'user-uploads' AND auth.uid()::text = (storage.foldername(name))[1]);

CREATE POLICY "Users can delete own uploads"
ON storage.objects FOR DELETE
USING (bucket_id = 'user-uploads' AND auth.uid()::text = (storage.foldername(name))[1]);

-- Storage policies for exports bucket
CREATE POLICY "Users can view own exports"
ON storage.objects FOR SELECT
USING (bucket_id = 'exports' AND auth.uid()::text = (storage.foldername(name))[1]);

CREATE POLICY "Users can create own exports"
ON storage.objects FOR INSERT
WITH CHECK (bucket_id = 'exports' AND auth.uid()::text = (storage.foldername(name))[1]);

CREATE POLICY "Users can delete own exports"
ON storage.objects FOR DELETE
USING (bucket_id = 'exports' AND auth.uid()::text = (storage.foldername(name))[1]);

-- Automatic cleanup function for temporary export files
CREATE OR REPLACE FUNCTION cleanup_old_exports()
RETURNS void AS $$
BEGIN
    DELETE FROM storage.objects 
    WHERE bucket_id = 'exports' 
    AND created_at < NOW() - INTERVAL '24 hours';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create a scheduled function to clean up exports (requires pg_cron extension in production)
-- This would be set up in production: SELECT cron.schedule('cleanup-exports', '0 2 * * *', 'SELECT cleanup_old_exports();');