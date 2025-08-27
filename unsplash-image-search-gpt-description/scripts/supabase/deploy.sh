#!/bin/bash

# Supabase Deployment Script for VocabLens
# This script deploys to remote Supabase project

set -e

echo "🚀 Deploying VocabLens to Supabase..."

# Check if project reference is provided
if [ -z "$1" ]; then
    echo "❌ Please provide your Supabase project reference"
    echo "Usage: ./scripts/supabase/deploy.sh your-project-ref"
    exit 1
fi

PROJECT_REF=$1

# Check if logged in to Supabase
if ! supabase projects list &> /dev/null; then
    echo "❌ Not logged in to Supabase. Please run: supabase auth login"
    exit 1
fi

echo "✅ Authenticated with Supabase"

# Link to remote project
echo "🔗 Linking to remote project: $PROJECT_REF"
supabase link --project-ref $PROJECT_REF

# Push database changes
echo "📤 Pushing database migrations..."
supabase db push

# Deploy Edge Functions
echo "⚡ Deploying Edge Functions..."

# Deploy image-search function
echo "  📸 Deploying image-search function..."
supabase functions deploy image-search --project-ref $PROJECT_REF

# Deploy ai-description function
echo "  🤖 Deploying ai-description function..."
supabase functions deploy ai-description --project-ref $PROJECT_REF

# Deploy translate function
echo "  🌐 Deploying translate function..."
supabase functions deploy translate --project-ref $PROJECT_REF

# Set function environment variables
echo "🔧 Setting up function environment variables..."
echo "Please set these environment variables in your Supabase dashboard:"
echo ""
echo "For all functions:"
echo "  SUPABASE_URL=your-supabase-url"
echo "  SUPABASE_ANON_KEY=your-anon-key"
echo ""
echo "For image-search function:"
echo "  UNSPLASH_ACCESS_KEY=your-unsplash-access-key"
echo ""
echo "For ai-description and translate functions:"
echo "  OPENAI_API_KEY=your-openai-api-key"
echo ""

# Generate types from remote
echo "🔄 Generating TypeScript types from remote..."
supabase gen types typescript --project-ref $PROJECT_REF > supabase/types/database.types.ts

# Verify deployment
echo "🔍 Verifying deployment..."
supabase functions list --project-ref $PROJECT_REF

echo "✅ Deployment complete!"
echo ""
echo "🌐 Your Supabase project: https://app.supabase.com/project/$PROJECT_REF"
echo ""
echo "📝 Post-deployment steps:"
echo "1. Configure OAuth providers in Supabase Auth settings"
echo "2. Set up your environment variables in the Functions section"
echo "3. Configure Storage bucket policies if needed"
echo "4. Update your application's environment variables"
echo "5. Test your Edge Functions in the Functions section"