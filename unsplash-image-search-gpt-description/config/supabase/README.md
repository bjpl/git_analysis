# VocabLens Supabase Configuration

This directory contains the complete Supabase backend infrastructure for VocabLens, a vocabulary learning application with image-based learning and AI-powered descriptions.

## 🏗️ Architecture Overview

### Database Schema
- **Users**: Extended user profiles with learning preferences
- **Vocabulary Items**: Core vocabulary with images, translations, and metadata
- **Search Sessions**: Track image search history and patterns
- **Quiz Results**: Store practice session results for analytics
- **Shared Lists**: Community vocabulary lists with sharing capabilities
- **User Preferences**: Personalized settings and learning preferences

### Edge Functions
- **image-search**: Unsplash API integration with style modifiers
- **ai-description**: AI-powered vocabulary descriptions using GPT-4V
- **translate**: Multi-language translation service

### Storage Buckets
- **image-cache**: Public cache for Unsplash images
- **user-uploads**: Private user profile pictures
- **exports**: Temporary vocabulary exports (CSV/JSON)

## 🚀 Quick Start

### Prerequisites
- Docker Desktop installed and running
- Node.js 16+ installed
- Supabase CLI installed (`npm install -g supabase`)

### Local Development Setup

1. **Clone and navigate to project**:
   ```bash
   cd your-project-directory
   ```

2. **Run the setup script**:
   ```bash
   chmod +x scripts/supabase/setup.sh
   ./scripts/supabase/setup.sh
   ```

3. **Set up environment variables**:
   ```bash
   cp config/supabase/env.example .env.local
   # Edit .env.local with your API keys
   ```

4. **Access local services**:
   - Supabase Studio: http://localhost:54323
   - Database: postgresql://postgres:postgres@localhost:54322/postgres
   - Email testing: http://localhost:54324

### Manual Setup (Alternative)

1. **Initialize Supabase**:
   ```bash
   supabase init
   supabase start
   ```

2. **Apply migrations**:
   ```bash
   supabase db reset --local
   ```

3. **Seed database**:
   ```bash
   supabase db seed
   ```

4. **Generate types**:
   ```bash
   node scripts/supabase/generate-types.js
   ```

## 📊 Database Schema Details

### Core Tables

#### Users Table
Extended user profiles with learning analytics:
- Personal information and preferences
- Learning statistics (streak, goals, progress)
- Subscription management
- Activity tracking

#### Vocabulary Items Table
Comprehensive vocabulary storage:
- Multi-language support
- Image associations with Unsplash integration
- Spaced repetition scheduling
- Mastery level tracking
- Rich metadata (pronunciation, examples, tags)

#### Advanced Features
- **Spaced Repetition Algorithm**: Automatic review scheduling
- **Full-Text Search**: Efficient vocabulary search
- **Progress Analytics**: Detailed learning statistics
- **Community Sharing**: Vocabulary list sharing

### Security (RLS Policies)

All tables implement Row Level Security:
- Users can only access their own data
- Public shared lists are accessible to all
- Storage buckets have appropriate access controls

## ⚡ Edge Functions

### Image Search Function
```typescript
POST /functions/v1/image-search
{
  "query": "mountain landscape",
  "style": "realistic", // realistic, artistic, minimalist, abstract, vintage
  "per_page": 12,
  "page": 1
}
```

### AI Description Function
```typescript
POST /functions/v1/ai-description
{
  "imageUrl": "https://...",
  "word": "mountain",
  "targetLanguage": "es",
  "style": "detailed" // simple, detailed, academic, conversational
}
```

### Translation Function
```typescript
POST /functions/v1/translate
{
  "text": "Hello world",
  "fromLanguage": "en",
  "toLanguage": "es",
  "context": "greeting"
}
```

## 🔧 Configuration

### Required Environment Variables

#### Application
```bash
NEXT_PUBLIC_SUPABASE_URL=your-project-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

#### External APIs
```bash
UNSPLASH_ACCESS_KEY=your-unsplash-key
OPENAI_API_KEY=your-openai-key
```

#### OAuth (Optional)
```bash
SUPABASE_AUTH_EXTERNAL_GITHUB_CLIENT_ID=your-github-id
SUPABASE_AUTH_EXTERNAL_GITHUB_SECRET=your-github-secret
SUPABASE_AUTH_EXTERNAL_GOOGLE_CLIENT_ID=your-google-id
SUPABASE_AUTH_EXTERNAL_GOOGLE_SECRET=your-google-secret
```

### Function Environment Variables

Set these in your Supabase dashboard for Edge Functions:
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `UNSPLASH_ACCESS_KEY`
- `OPENAI_API_KEY`

## 🚀 Deployment

### Deploy to Production

1. **Create Supabase project**:
   - Go to https://app.supabase.com
   - Create a new project
   - Note your project reference

2. **Deploy using script**:
   ```bash
   chmod +x scripts/supabase/deploy.sh
   ./scripts/supabase/deploy.sh your-project-ref
   ```

3. **Configure OAuth providers** in Supabase Auth settings

4. **Set function environment variables** in Functions section

### Manual Deployment

1. **Link project**:
   ```bash
   supabase login
   supabase link --project-ref your-project-ref
   ```

2. **Push database**:
   ```bash
   supabase db push
   ```

3. **Deploy functions**:
   ```bash
   supabase functions deploy image-search
   supabase functions deploy ai-description
   supabase functions deploy translate
   ```

## 🧪 Testing

### Sample Data
The seed file includes realistic sample data:
- Demo user profiles
- Vocabulary items with different difficulty levels
- Search sessions and quiz results
- Shared vocabulary lists

### Local Testing
```bash
# Reset database with fresh data
supabase db reset --local

# View logs
supabase functions logs image-search --local
```

## 📈 Advanced Features

### Spaced Repetition Algorithm
- Implements SuperMemo-style scheduling
- Adjusts intervals based on performance
- Tracks mastery levels (0-5)

### Analytics Functions
- Learning progress tracking
- Performance analytics
- Usage statistics

### Search Capabilities
- Full-text search across vocabulary
- Tag-based filtering
- Difficulty-based filtering
- Advanced sorting options

## 🔍 Monitoring

### Database Functions
```sql
-- Get vocabulary due for review
SELECT * FROM get_vocabulary_for_review('user-id', 10);

-- Update practice results
SELECT update_vocabulary_practice('item-id', true, 3500);

-- Search vocabulary
SELECT * FROM search_vocabulary('user-id', 'mountain', ARRAY['nature']);
```

### Function Logs
```bash
# View function logs
supabase functions logs --follow

# View specific function
supabase functions logs image-search --follow
```

## 🛠️ Maintenance

### Database Migrations
```bash
# Create new migration
supabase migration new migration_name

# Apply migrations
supabase db push

# Check differences
supabase db diff
```

### Type Generation
```bash
# Generate types from local
node scripts/supabase/generate-types.js

# Generate types from remote
node scripts/supabase/generate-types.js --remote=your-project-ref
```

### Backup and Recovery
```bash
# Backup database
pg_dump "postgresql://postgres:postgres@localhost:54322/postgres" > backup.sql

# Restore database
psql "postgresql://postgres:postgres@localhost:54322/postgres" < backup.sql
```

## 🔐 Security Best Practices

### Row Level Security
- All tables have comprehensive RLS policies
- Users can only access their own data
- Public content is properly filtered

### API Security
- All functions require authentication
- Input validation on all endpoints
- Rate limiting implemented
- Secure storage policies

### Environment Security
- Never commit API keys
- Use environment variable substitution
- Rotate keys regularly
- Monitor function usage

## 📚 Additional Resources

- [Supabase Documentation](https://supabase.com/docs)
- [Edge Functions Guide](https://supabase.com/docs/guides/functions)
- [Row Level Security](https://supabase.com/docs/guides/auth/row-level-security)
- [Database Design](https://supabase.com/docs/guides/database/overview)