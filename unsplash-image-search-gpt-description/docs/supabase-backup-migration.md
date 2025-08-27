# Supabase Backup and Migration Strategy

## Overview

Comprehensive backup and migration strategy for the Vocabulary Learning PWA, including data protection, disaster recovery, and smooth migration paths from desktop to web.

## 1. Backup Strategy

### Automated Database Backups

```sql
-- Create backup schema
CREATE SCHEMA IF NOT EXISTS backups;

-- Function to create full database backup
CREATE OR REPLACE FUNCTION backups.create_full_backup(backup_name TEXT DEFAULT NULL)
RETURNS TEXT AS $$
DECLARE
  backup_id TEXT;
  backup_timestamp TIMESTAMPTZ := NOW();
  table_count INTEGER := 0;
BEGIN
  -- Generate backup ID
  backup_id := COALESCE(backup_name, 'backup_' || TO_CHAR(backup_timestamp, 'YYYYMMDD_HH24MISS'));
  
  -- Create backup metadata table if not exists
  CREATE TABLE IF NOT EXISTS backups.backup_metadata (
    id SERIAL PRIMARY KEY,
    backup_id TEXT UNIQUE NOT NULL,
    backup_type TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    status TEXT DEFAULT 'in_progress',
    tables_backed_up TEXT[],
    total_rows BIGINT,
    backup_size_mb NUMERIC,
    notes TEXT
  );
  
  -- Insert backup record
  INSERT INTO backups.backup_metadata (backup_id, backup_type, status)
  VALUES (backup_id, 'full', 'in_progress');
  
  -- Backup core tables
  EXECUTE format('CREATE TABLE IF NOT EXISTS backups.%I_profiles AS SELECT * FROM public.profiles', backup_id);
  EXECUTE format('CREATE TABLE IF NOT EXISTS backups.%I_vocabulary AS SELECT * FROM public.vocabulary', backup_id);
  EXECUTE format('CREATE TABLE IF NOT EXISTS backups.%I_images AS SELECT * FROM public.images', backup_id);
  EXECUTE format('CREATE TABLE IF NOT EXISTS backups.%I_learning_sessions AS SELECT * FROM public.learning_sessions', backup_id);
  EXECUTE format('CREATE TABLE IF NOT EXISTS backups.%I_quiz_attempts AS SELECT * FROM public.quiz_attempts', backup_id);
  EXECUTE format('CREATE TABLE IF NOT EXISTS backups.%I_vocabulary_collections AS SELECT * FROM public.vocabulary_collections', backup_id);
  EXECUTE format('CREATE TABLE IF NOT EXISTS backups.%I_vocabulary_collection_items AS SELECT * FROM public.vocabulary_collection_items', backup_id);
  EXECUTE format('CREATE TABLE IF NOT EXISTS backups.%I_user_activity AS SELECT * FROM public.user_activity WHERE created_at >= NOW() - INTERVAL ''90 days''', backup_id);
  
  -- Update backup metadata
  UPDATE backups.backup_metadata 
  SET 
    status = 'completed',
    tables_backed_up = ARRAY['profiles', 'vocabulary', 'images', 'learning_sessions', 'quiz_attempts', 'vocabulary_collections', 'vocabulary_collection_items', 'user_activity'],
    total_rows = (
      SELECT SUM(row_count) FROM (
        SELECT COUNT(*) as row_count FROM public.profiles
        UNION ALL SELECT COUNT(*) FROM public.vocabulary
        UNION ALL SELECT COUNT(*) FROM public.images
        UNION ALL SELECT COUNT(*) FROM public.learning_sessions
        UNION ALL SELECT COUNT(*) FROM public.quiz_attempts
        UNION ALL SELECT COUNT(*) FROM public.vocabulary_collections
        UNION ALL SELECT COUNT(*) FROM public.vocabulary_collection_items
        UNION ALL SELECT COUNT(*) FROM public.user_activity WHERE created_at >= NOW() - INTERVAL '90 days'
      ) counts
    )
  WHERE backup_id = backup_id;
  
  RETURN backup_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to create incremental backup
CREATE OR REPLACE FUNCTION backups.create_incremental_backup(
  since_timestamp TIMESTAMPTZ DEFAULT NOW() - INTERVAL '1 day'
)
RETURNS TEXT AS $$
DECLARE
  backup_id TEXT;
  backup_timestamp TIMESTAMPTZ := NOW();
BEGIN
  backup_id := 'incremental_' || TO_CHAR(backup_timestamp, 'YYYYMMDD_HH24MISS');
  
  -- Insert backup record
  INSERT INTO backups.backup_metadata (backup_id, backup_type, status)
  VALUES (backup_id, 'incremental', 'in_progress');
  
  -- Backup only changed/new data
  EXECUTE format(
    'CREATE TABLE IF NOT EXISTS backups.%I_profiles AS SELECT * FROM public.profiles WHERE updated_at >= %L',
    backup_id, since_timestamp
  );
  
  EXECUTE format(
    'CREATE TABLE IF NOT EXISTS backups.%I_vocabulary AS SELECT * FROM public.vocabulary WHERE updated_at >= %L OR created_at >= %L',
    backup_id, since_timestamp, since_timestamp
  );
  
  EXECUTE format(
    'CREATE TABLE IF NOT EXISTS backups.%I_images AS SELECT * FROM public.images WHERE updated_at >= %L OR created_at >= %L',
    backup_id, since_timestamp, since_timestamp
  );
  
  EXECUTE format(
    'CREATE TABLE IF NOT EXISTS backups.%I_learning_sessions AS SELECT * FROM public.learning_sessions WHERE started_at >= %L',
    backup_id, since_timestamp
  );
  
  EXECUTE format(
    'CREATE TABLE IF NOT EXISTS backups.%I_quiz_attempts AS SELECT * FROM public.quiz_attempts WHERE started_at >= %L',
    backup_id, since_timestamp
  );
  
  -- Update backup metadata
  UPDATE backups.backup_metadata 
  SET status = 'completed'
  WHERE backup_id = backup_id;
  
  RETURN backup_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to restore from backup
CREATE OR REPLACE FUNCTION backups.restore_from_backup(
  backup_id TEXT,
  restore_tables TEXT[] DEFAULT NULL,
  dry_run BOOLEAN DEFAULT TRUE
)
RETURNS TABLE(
  table_name TEXT,
  action TEXT,
  row_count BIGINT,
  status TEXT
) AS $$
DECLARE
  table_to_restore TEXT;
  tables_to_restore TEXT[];
  row_count BIGINT;
  sql_command TEXT;
BEGIN
  -- Default to all tables if none specified
  tables_to_restore := COALESCE(
    restore_tables,
    ARRAY['profiles', 'vocabulary', 'images', 'learning_sessions', 'quiz_attempts', 'vocabulary_collections', 'vocabulary_collection_items', 'user_activity']
  );
  
  -- Check if backup exists
  IF NOT EXISTS (SELECT 1 FROM backups.backup_metadata WHERE backup_metadata.backup_id = restore_from_backup.backup_id) THEN
    RAISE EXCEPTION 'Backup % not found', backup_id;
  END IF;
  
  FOREACH table_to_restore IN ARRAY tables_to_restore
  LOOP
    -- Check if backup table exists
    sql_command := format('SELECT COUNT(*) FROM backups.%I_%s', backup_id, table_to_restore);
    
    BEGIN
      EXECUTE sql_command INTO row_count;
      
      IF dry_run THEN
        RETURN QUERY SELECT 
          table_to_restore,
          'restore'::TEXT,
          row_count,
          'dry_run_success'::TEXT;
      ELSE
        -- Perform actual restore (this is dangerous!)
        -- In production, you'd want more sophisticated restore logic
        EXECUTE format('TRUNCATE TABLE public.%I CASCADE', table_to_restore);
        EXECUTE format('INSERT INTO public.%I SELECT * FROM backups.%I_%s', table_to_restore, backup_id, table_to_restore);
        
        RETURN QUERY SELECT 
          table_to_restore,
          'restore'::TEXT,
          row_count,
          'completed'::TEXT;
      END IF;
      
    EXCEPTION WHEN OTHERS THEN
      RETURN QUERY SELECT 
        table_to_restore,
        'restore'::TEXT,
        0::BIGINT,
        ('error: ' || SQLERRM)::TEXT;
    END;
  END LOOP;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to cleanup old backups
CREATE OR REPLACE FUNCTION backups.cleanup_old_backups(
  retain_days INTEGER DEFAULT 30,
  retain_count INTEGER DEFAULT 10
)
RETURNS INTEGER AS $$
DECLARE
  backup_to_delete RECORD;
  deleted_count INTEGER := 0;
  backup_table TEXT;
BEGIN
  -- Get backups to delete (older than retain_days or beyond retain_count)
  FOR backup_to_delete IN
    SELECT backup_id, tables_backed_up
    FROM backups.backup_metadata
    WHERE created_at < NOW() - (retain_days || ' days')::INTERVAL
    OR backup_id NOT IN (
      SELECT backup_id
      FROM backups.backup_metadata
      ORDER BY created_at DESC
      LIMIT retain_count
    )
  LOOP
    -- Drop backup tables
    IF backup_to_delete.tables_backed_up IS NOT NULL THEN
      FOREACH backup_table IN ARRAY backup_to_delete.tables_backed_up
      LOOP
        EXECUTE format('DROP TABLE IF EXISTS backups.%I_%s', backup_to_delete.backup_id, backup_table);
      END LOOP;
    END IF;
    
    -- Remove metadata
    DELETE FROM backups.backup_metadata WHERE backup_id = backup_to_delete.backup_id;
    deleted_count := deleted_count + 1;
  END LOOP;
  
  RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Schedule automated backups
SELECT cron.schedule(
  'daily-full-backup',
  '0 2 * * *', -- Daily at 2 AM
  'SELECT backups.create_full_backup();'
);

SELECT cron.schedule(
  'hourly-incremental-backup',
  '0 * * * *', -- Every hour
  'SELECT backups.create_incremental_backup();'
);

SELECT cron.schedule(
  'weekly-backup-cleanup',
  '0 3 * * 0', -- Weekly on Sunday at 3 AM
  'SELECT backups.cleanup_old_backups();'
);
```

### Storage Backup Configuration

```sql
-- Function to backup storage metadata
CREATE OR REPLACE FUNCTION backups.backup_storage_metadata()
RETURNS TEXT AS $$
DECLARE
  backup_id TEXT := 'storage_' || TO_CHAR(NOW(), 'YYYYMMDD_HH24MISS');
BEGIN
  -- Backup storage object metadata
  EXECUTE format(
    'CREATE TABLE IF NOT EXISTS backups.%I_storage_objects AS SELECT * FROM storage.objects',
    backup_id
  );
  
  -- Backup storage bucket configuration
  EXECUTE format(
    'CREATE TABLE IF NOT EXISTS backups.%I_storage_buckets AS SELECT * FROM storage.buckets',
    backup_id
  );
  
  -- Record backup
  INSERT INTO backups.backup_metadata (backup_id, backup_type, status, notes)
  VALUES (backup_id, 'storage', 'completed', 'Storage metadata backup');
  
  RETURN backup_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Schedule storage backup
SELECT cron.schedule(
  'daily-storage-backup',
  '0 4 * * *', -- Daily at 4 AM
  'SELECT backups.backup_storage_metadata();'
);
```

## 2. Desktop to Web Migration Strategy

### Migration Assessment Function

```sql
-- Function to assess desktop data for migration
CREATE OR REPLACE FUNCTION public.assess_desktop_migration(
  csv_data JSONB,
  sample_size INTEGER DEFAULT 100
)
RETURNS TABLE(
  total_records INTEGER,
  valid_records INTEGER,
  duplicate_records INTEGER,
  invalid_records INTEGER,
  estimated_cleanup_time_minutes INTEGER,
  migration_recommendations JSONB
) AS $$
DECLARE
  total_count INTEGER;
  valid_count INTEGER := 0;
  duplicate_count INTEGER := 0;
  invalid_count INTEGER := 0;
  sample_item JSONB;
  spanish_words TEXT[];
  recommendations JSONB := '[]'::jsonb;
BEGIN
  total_count := jsonb_array_length(csv_data);
  
  -- Analyze sample data
  FOR sample_item IN 
    SELECT jsonb_array_elements(csv_data) 
    LIMIT sample_size
  LOOP
    -- Check validity
    IF sample_item->>'Spanish' IS NOT NULL 
       AND sample_item->>'English' IS NOT NULL
       AND LENGTH(TRIM(sample_item->>'Spanish')) > 0
       AND LENGTH(TRIM(sample_item->>'English')) > 0 THEN
      valid_count := valid_count + 1;
      
      -- Check for duplicates
      IF sample_item->>'Spanish' = ANY(spanish_words) THEN
        duplicate_count := duplicate_count + 1;
      ELSE
        spanish_words := array_append(spanish_words, sample_item->>'Spanish');
      END IF;
    ELSE
      invalid_count := invalid_count + 1;
    END IF;
  END LOOP;
  
  -- Generate recommendations
  IF duplicate_count > total_count * 0.1 THEN
    recommendations := recommendations || jsonb_build_object(
      'type', 'duplicates',
      'message', 'High number of duplicates detected. Consider deduplication.',
      'priority', 'high'
    );
  END IF;
  
  IF invalid_count > total_count * 0.05 THEN
    recommendations := recommendations || jsonb_build_object(
      'type', 'invalid_data',
      'message', 'Significant invalid records found. Manual cleanup recommended.',
      'priority', 'medium'
    );
  END IF;
  
  recommendations := recommendations || jsonb_build_object(
    'type', 'batch_size',
    'message', 'Recommended batch size: ' || LEAST(1000, GREATEST(100, total_count / 10)),
    'priority', 'info'
  );
  
  RETURN QUERY SELECT
    total_count,
    (valid_count::NUMERIC / sample_size * total_count)::INTEGER,
    (duplicate_count::NUMERIC / sample_size * total_count)::INTEGER,
    (invalid_count::NUMERIC / sample_size * total_count)::INTEGER,
    GREATEST(5, total_count / 1000),
    recommendations;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Staged migration function
CREATE OR REPLACE FUNCTION public.migrate_desktop_vocabulary(
  p_user_id UUID,
  p_csv_data JSONB,
  p_batch_size INTEGER DEFAULT 500,
  p_stage TEXT DEFAULT 'preview' -- 'preview', 'staging', 'production'
)
RETURNS TABLE(
  stage TEXT,
  batch_number INTEGER,
  records_processed INTEGER,
  records_imported INTEGER,
  records_skipped INTEGER,
  records_failed INTEGER,
  completion_percentage NUMERIC,
  errors JSONB
) AS $$
DECLARE
  total_records INTEGER;
  current_batch INTEGER := 1;
  batch_start INTEGER := 1;
  batch_end INTEGER;
  batch_data JSONB;
  import_result RECORD;
BEGIN
  total_records := jsonb_array_length(p_csv_data);
  
  -- Create staging tables if in staging mode
  IF p_stage = 'staging' THEN
    DROP TABLE IF EXISTS staging.vocabulary_migration;
    CREATE TABLE staging.vocabulary_migration AS 
    SELECT * FROM public.vocabulary WHERE false; -- Structure only
    
    ALTER TABLE staging.vocabulary_migration ADD COLUMN migration_batch INTEGER;
    ALTER TABLE staging.vocabulary_migration ADD COLUMN migration_status TEXT DEFAULT 'pending';
  END IF;
  
  -- Process in batches
  WHILE batch_start <= total_records LOOP
    batch_end := LEAST(batch_start + p_batch_size - 1, total_records);
    
    -- Extract batch data
    SELECT jsonb_agg(item) INTO batch_data
    FROM (
      SELECT jsonb_array_elements(p_csv_data) as item
      OFFSET (batch_start - 1) LIMIT p_batch_size
    ) sub;
    
    -- Process batch based on stage
    CASE p_stage
      WHEN 'preview' THEN
        -- Just validate and count
        SELECT * INTO import_result FROM public.smart_vocabulary_import(
          p_user_id,
          batch_data,
          'skip_duplicates'
        );
        
      WHEN 'staging' THEN
        -- Import to staging table
        -- This would need custom implementation
        import_result.imported_count := 0;
        import_result.skipped_count := 0;
        import_result.error_count := 0;
        
      WHEN 'production' THEN
        -- Import to production
        SELECT * INTO import_result FROM public.smart_vocabulary_import(
          p_user_id,
          batch_data,
          'skip_duplicates'
        );
    END CASE;
    
    RETURN QUERY SELECT
      p_stage,
      current_batch,
      batch_end - batch_start + 1,
      import_result.imported_count,
      import_result.skipped_count,
      import_result.error_count,
      ROUND((batch_end::NUMERIC / total_records * 100), 2),
      import_result.errors;
    
    current_batch := current_batch + 1;
    batch_start := batch_end + 1;
  END LOOP;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

### Data Validation and Cleanup

```sql
-- Function to validate migrated data
CREATE OR REPLACE FUNCTION public.validate_migration_data(p_user_id UUID)
RETURNS TABLE(
  validation_type TEXT,
  status TEXT,
  records_checked INTEGER,
  issues_found INTEGER,
  issue_details JSONB
) AS $$
DECLARE
  vocab_count INTEGER;
  orphaned_images INTEGER;
  duplicate_count INTEGER;
  invalid_dates INTEGER;
  missing_translations INTEGER;
BEGIN
  -- Check total vocabulary count
  SELECT COUNT(*) INTO vocab_count
  FROM public.vocabulary
  WHERE user_id = p_user_id;
  
  RETURN QUERY SELECT
    'total_records'::TEXT,
    CASE WHEN vocab_count > 0 THEN 'pass' ELSE 'fail' END::TEXT,
    vocab_count,
    0,
    jsonb_build_object('message', vocab_count || ' vocabulary records found');
  
  -- Check for orphaned images
  SELECT COUNT(*) INTO orphaned_images
  FROM public.images i
  WHERE i.user_id = p_user_id
    AND NOT EXISTS (
      SELECT 1 FROM public.vocabulary v
      WHERE v.source_image_id = i.id
    );
  
  RETURN QUERY SELECT
    'orphaned_images'::TEXT,
    CASE WHEN orphaned_images = 0 THEN 'pass' ELSE 'warning' END::TEXT,
    orphaned_images,
    orphaned_images,
    jsonb_build_object('message', orphaned_images || ' orphaned image records');
  
  -- Check for duplicates
  SELECT COUNT(*) INTO duplicate_count
  FROM (
    SELECT spanish_text, COUNT(*) as cnt
    FROM public.vocabulary
    WHERE user_id = p_user_id
    GROUP BY spanish_text
    HAVING COUNT(*) > 1
  ) dups;
  
  RETURN QUERY SELECT
    'duplicates'::TEXT,
    CASE WHEN duplicate_count = 0 THEN 'pass' ELSE 'warning' END::TEXT,
    duplicate_count,
    duplicate_count,
    jsonb_build_object('message', duplicate_count || ' duplicate vocabulary entries');
  
  -- Check for invalid dates
  SELECT COUNT(*) INTO invalid_dates
  FROM public.vocabulary
  WHERE user_id = p_user_id
    AND (created_at > NOW() OR created_at < '2020-01-01'::date);
  
  RETURN QUERY SELECT
    'invalid_dates'::TEXT,
    CASE WHEN invalid_dates = 0 THEN 'pass' ELSE 'fail' END::TEXT,
    invalid_dates,
    invalid_dates,
    jsonb_build_object('message', invalid_dates || ' records with invalid dates');
  
  -- Check for missing translations
  SELECT COUNT(*) INTO missing_translations
  FROM public.vocabulary
  WHERE user_id = p_user_id
    AND (english_translation IS NULL OR LENGTH(TRIM(english_translation)) = 0);
  
  RETURN QUERY SELECT
    'missing_translations'::TEXT,
    CASE WHEN missing_translations = 0 THEN 'pass' ELSE 'fail' END::TEXT,
    missing_translations,
    missing_translations,
    jsonb_build_object('message', missing_translations || ' records missing translations');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to fix common migration issues
CREATE OR REPLACE FUNCTION public.fix_migration_issues(
  p_user_id UUID,
  p_fix_types TEXT[] DEFAULT ARRAY['duplicates', 'orphaned_images', 'invalid_dates']
)
RETURNS TABLE(
  fix_type TEXT,
  records_affected INTEGER,
  status TEXT,
  details TEXT
) AS $$
DECLARE
  fix_type TEXT;
  affected_count INTEGER;
BEGIN
  FOREACH fix_type IN ARRAY p_fix_types
  LOOP
    affected_count := 0;
    
    CASE fix_type
      WHEN 'duplicates' THEN
        -- Keep the most recent duplicate and archive others
        UPDATE public.vocabulary v1
        SET is_archived = true,
            notes = COALESCE(notes, '') || ' [Archived as duplicate]'
        FROM public.vocabulary v2
        WHERE v1.user_id = p_user_id
          AND v2.user_id = p_user_id
          AND v1.spanish_text = v2.spanish_text
          AND v1.id != v2.id
          AND v1.created_at < v2.created_at;
        
        GET DIAGNOSTICS affected_count = ROW_COUNT;
        
      WHEN 'orphaned_images' THEN
        -- Delete orphaned image records
        DELETE FROM public.images
        WHERE user_id = p_user_id
          AND NOT EXISTS (
            SELECT 1 FROM public.vocabulary v
            WHERE v.source_image_id = images.id
          );
        
        GET DIAGNOSTICS affected_count = ROW_COUNT;
        
      WHEN 'invalid_dates' THEN
        -- Fix obviously wrong dates
        UPDATE public.vocabulary
        SET created_at = GREATEST(
          '2020-01-01 00:00:00+00'::timestamptz,
          LEAST(NOW(), created_at)
        )
        WHERE user_id = p_user_id
          AND (created_at > NOW() OR created_at < '2020-01-01'::date);
        
        GET DIAGNOSTICS affected_count = ROW_COUNT;
    END CASE;
    
    RETURN QUERY SELECT
      fix_type,
      affected_count,
      CASE WHEN affected_count > 0 THEN 'fixed' ELSE 'no_issues' END::TEXT,
      affected_count || ' records processed'::TEXT;
  END LOOP;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

## 3. Disaster Recovery Plan

### Recovery Point Objective (RPO): 1 hour
### Recovery Time Objective (RTO): 4 hours

```sql
-- Function to create emergency backup
CREATE OR REPLACE FUNCTION backups.create_emergency_backup(
  p_reason TEXT DEFAULT 'emergency'
)
RETURNS TEXT AS $$
DECLARE
  backup_id TEXT;
BEGIN
  backup_id := 'emergency_' || TO_CHAR(NOW(), 'YYYYMMDD_HH24MISS');
  
  -- Create immediate full backup
  PERFORM backups.create_full_backup(backup_id);
  
  -- Create storage metadata backup
  PERFORM backups.backup_storage_metadata();
  
  -- Log emergency backup
  INSERT INTO public.user_activity (
    user_id,
    activity_type,
    details
  )
  SELECT 
    id,
    'emergency_backup',
    jsonb_build_object('backup_id', backup_id, 'reason', p_reason)
  FROM public.profiles
  WHERE (preferences->>'role') = 'admin'
  LIMIT 1;
  
  RETURN backup_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to verify backup integrity
CREATE OR REPLACE FUNCTION backups.verify_backup_integrity(backup_id TEXT)
RETURNS TABLE(
  table_name TEXT,
  backup_count BIGINT,
  current_count BIGINT,
  integrity_check TEXT
) AS $$
DECLARE
  table_names TEXT[] := ARRAY['profiles', 'vocabulary', 'images', 'learning_sessions'];
  tbl TEXT;
  backup_count BIGINT;
  current_count BIGINT;
BEGIN
  FOREACH tbl IN ARRAY table_names
  LOOP
    -- Get backup table count
    EXECUTE format('SELECT COUNT(*) FROM backups.%I_%s', backup_id, tbl) INTO backup_count;
    
    -- Get current table count
    EXECUTE format('SELECT COUNT(*) FROM public.%I', tbl) INTO current_count;
    
    RETURN QUERY SELECT
      tbl,
      backup_count,
      current_count,
      CASE 
        WHEN backup_count = current_count THEN 'exact_match'
        WHEN backup_count < current_count THEN 'backup_behind'
        ELSE 'data_loss_detected'
      END;
  END LOOP;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Recovery procedure checklist function
CREATE OR REPLACE FUNCTION backups.get_recovery_checklist()
RETURNS TABLE(
  step_number INTEGER,
  step_title TEXT,
  step_description TEXT,
  estimated_time_minutes INTEGER,
  dependencies TEXT[]
) AS $$
BEGIN
  RETURN QUERY VALUES
    (1, 'Assess Damage', 'Determine scope of data loss or corruption', 15, ARRAY[]::TEXT[]),
    (2, 'Stop Write Operations', 'Prevent further data corruption', 5, ARRAY['step_1']),
    (3, 'Identify Recovery Point', 'Choose appropriate backup for restoration', 10, ARRAY['step_1']),
    (4, 'Verify Backup Integrity', 'Ensure backup is complete and valid', 20, ARRAY['step_3']),
    (5, 'Create Current State Backup', 'Backup current state before restoration', 30, ARRAY['step_2']),
    (6, 'Begin Restoration', 'Start restoring from backup', 60, ARRAY['step_4', 'step_5']),
    (7, 'Validate Restored Data', 'Run integrity checks on restored data', 30, ARRAY['step_6']),
    (8, 'Restore Storage Assets', 'Restore file storage if needed', 45, ARRAY['step_6']),
    (9, 'Test Application Functions', 'Verify all features work correctly', 30, ARRAY['step_7', 'step_8']),
    (10, 'Resume Normal Operations', 'Re-enable write operations and user access', 10, ARRAY['step_9']);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

## 4. Monitoring and Alerting

```sql
-- Function to monitor backup health
CREATE OR REPLACE FUNCTION backups.monitor_backup_health()
RETURNS TABLE(
  check_type TEXT,
  status TEXT,
  last_backup TIMESTAMPTZ,
  days_since_backup NUMERIC,
  alert_level TEXT
) AS $$
DECLARE
  last_full_backup TIMESTAMPTZ;
  last_incremental_backup TIMESTAMPTZ;
  days_since_full NUMERIC;
  days_since_incremental NUMERIC;
BEGIN
  -- Check last full backup
  SELECT MAX(created_at) INTO last_full_backup
  FROM backups.backup_metadata
  WHERE backup_type = 'full' AND status = 'completed';
  
  days_since_full := EXTRACT(DAYS FROM (NOW() - last_full_backup));
  
  RETURN QUERY SELECT
    'full_backup'::TEXT,
    CASE 
      WHEN last_full_backup IS NULL THEN 'critical'
      WHEN days_since_full > 7 THEN 'warning'
      WHEN days_since_full > 1 THEN 'info'
      ELSE 'ok'
    END::TEXT,
    last_full_backup,
    days_since_full,
    CASE 
      WHEN last_full_backup IS NULL THEN 'critical'
      WHEN days_since_full > 7 THEN 'high'
      WHEN days_since_full > 1 THEN 'medium'
      ELSE 'low'
    END::TEXT;
  
  -- Check last incremental backup
  SELECT MAX(created_at) INTO last_incremental_backup
  FROM backups.backup_metadata
  WHERE backup_type = 'incremental' AND status = 'completed';
  
  days_since_incremental := EXTRACT(DAYS FROM (NOW() - last_incremental_backup));
  
  RETURN QUERY SELECT
    'incremental_backup'::TEXT,
    CASE 
      WHEN last_incremental_backup IS NULL THEN 'warning'
      WHEN days_since_incremental > 0.5 THEN 'info'
      ELSE 'ok'
    END::TEXT,
    last_incremental_backup,
    days_since_incremental,
    CASE 
      WHEN last_incremental_backup IS NULL THEN 'medium'
      WHEN days_since_incremental > 0.5 THEN 'low'
      ELSE 'low'
    END::TEXT;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to send backup alerts (would integrate with external service)
CREATE OR REPLACE FUNCTION backups.check_and_alert()
RETURNS void AS $$
DECLARE
  health_check RECORD;
  alert_message TEXT;
BEGIN
  FOR health_check IN SELECT * FROM backups.monitor_backup_health()
  LOOP
    IF health_check.alert_level IN ('high', 'critical') THEN
      alert_message := format(
        'BACKUP ALERT: %s backup is %s. Last backup: %s (%s days ago)',
        health_check.check_type,
        health_check.status,
        COALESCE(health_check.last_backup::TEXT, 'never'),
        COALESCE(health_check.days_since_backup::TEXT, '∞')
      );
      
      -- Log alert (in production, you'd send to external alerting system)
      INSERT INTO public.user_activity (
        user_id,
        activity_type,
        details
      )
      SELECT 
        id,
        'backup_alert',
        jsonb_build_object(
          'alert_level', health_check.alert_level,
          'check_type', health_check.check_type,
          'message', alert_message
        )
      FROM public.profiles
      WHERE (preferences->>'role') = 'admin'
      LIMIT 1;
    END IF;
  END LOOP;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Schedule monitoring
SELECT cron.schedule(
  'backup-health-check',
  '0 */6 * * *', -- Every 6 hours
  'SELECT backups.check_and_alert();'
);
```

## 5. GDPR Compliance and Data Export

```sql
-- Function for GDPR-compliant data export
CREATE OR REPLACE FUNCTION public.export_user_data_gdpr(p_user_id UUID)
RETURNS JSONB AS $$
DECLARE
  user_data JSONB := '{}'::jsonb;
BEGIN
  -- User profile data
  SELECT to_jsonb(p) INTO user_data 
  FROM (
    SELECT 
      id, email, username, full_name, 
      language_preferences, subscription_tier,
      preferences, created_at, updated_at
    FROM public.profiles 
    WHERE id = p_user_id
  ) p;
  
  -- Add vocabulary data
  user_data := user_data || jsonb_build_object(
    'vocabulary',
    (
      SELECT jsonb_agg(
        jsonb_build_object(
          'spanish_text', spanish_text,
          'english_translation', english_translation,
          'context', context,
          'difficulty_level', difficulty_level,
          'word_type', word_type,
          'mastery_level', mastery_level,
          'times_encountered', times_encountered,
          'created_at', created_at
        )
      )
      FROM public.vocabulary 
      WHERE user_id = p_user_id AND NOT is_archived
    )
  );
  
  -- Add learning sessions
  user_data := user_data || jsonb_build_object(
    'learning_sessions',
    (
      SELECT jsonb_agg(
        jsonb_build_object(
          'session_type', session_type,
          'started_at', started_at,
          'completed_at', completed_at,
          'duration_seconds', duration_seconds,
          'items_studied', items_studied,
          'accuracy_rate', accuracy_rate
        )
      )
      FROM public.learning_sessions
      WHERE user_id = p_user_id
    )
  );
  
  -- Add quiz attempts (last 100)
  user_data := user_data || jsonb_build_object(
    'recent_quiz_attempts',
    (
      SELECT jsonb_agg(
        jsonb_build_object(
          'quiz_type', quiz_type,
          'score', score,
          'max_score', max_score,
          'started_at', started_at,
          'completed_at', completed_at
        )
      )
      FROM (
        SELECT * FROM public.quiz_attempts
        WHERE user_id = p_user_id
        ORDER BY started_at DESC
        LIMIT 100
      ) recent_quizzes
    )
  );
  
  -- Add collections
  user_data := user_data || jsonb_build_object(
    'vocabulary_collections',
    (
      SELECT jsonb_agg(
        jsonb_build_object(
          'name', name,
          'description', description,
          'vocabulary_count', vocabulary_count,
          'created_at', created_at
        )
      )
      FROM public.vocabulary_collections
      WHERE user_id = p_user_id
    )
  );
  
  RETURN user_data;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function for complete user data deletion (GDPR right to be forgotten)
CREATE OR REPLACE FUNCTION public.delete_user_data_gdpr(p_user_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
  -- This would typically be called after a grace period
  -- Delete in order to respect foreign key constraints
  
  DELETE FROM public.quiz_attempts WHERE user_id = p_user_id;
  DELETE FROM public.vocabulary_collection_items WHERE vocabulary_id IN (
    SELECT id FROM public.vocabulary WHERE user_id = p_user_id
  );
  DELETE FROM public.vocabulary_collections WHERE user_id = p_user_id;
  DELETE FROM public.learning_sessions WHERE user_id = p_user_id;
  DELETE FROM public.vocabulary WHERE user_id = p_user_id;
  DELETE FROM public.images WHERE user_id = p_user_id;
  DELETE FROM public.user_activity WHERE user_id = p_user_id;
  DELETE FROM public.user_sessions WHERE user_id = p_user_id;
  DELETE FROM public.user_notifications WHERE user_id = p_user_id;
  DELETE FROM public.profiles WHERE id = p_user_id;
  
  -- Delete from auth.users (this should cascade to profiles)
  DELETE FROM auth.users WHERE id = p_user_id;
  
  RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

## 6. Implementation Checklist

### Pre-Migration Checklist
- [ ] Set up Supabase project and configure environment
- [ ] Run database schema creation scripts
- [ ] Configure storage buckets and policies
- [ ] Set up Edge Functions
- [ ] Test authentication flows
- [ ] Configure backup automation
- [ ] Set up monitoring and alerting

### Migration Execution Checklist
- [ ] Export desktop application data
- [ ] Assess migration data quality
- [ ] Run migration in staging environment
- [ ] Validate migrated data
- [ ] Fix any migration issues
- [ ] Perform production migration
- [ ] Verify all data integrity
- [ ] Test all application features
- [ ] Monitor system performance

### Post-Migration Checklist
- [ ] Verify backup systems are working
- [ ] Test disaster recovery procedures
- [ ] Monitor system health and performance
- [ ] Gather user feedback
- [ ] Document lessons learned
- [ ] Plan for ongoing maintenance

This backup and migration strategy provides:

1. **Automated backups** with retention policies
2. **Disaster recovery** procedures and checklists  
3. **Desktop-to-web migration** with validation
4. **Data integrity** checks and fixes
5. **GDPR compliance** for data export/deletion
6. **Monitoring and alerting** for backup health

The system ensures business continuity and data protection while enabling smooth migration from desktop to web platform.