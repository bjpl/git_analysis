#!/bin/bash

# Supabase Setup Script for VocabLens
# This script sets up the local Supabase environment

set -e

echo "🚀 Setting up Supabase for VocabLens..."

# Check if Supabase CLI is installed
if ! command -v supabase &> /dev/null; then
    echo "❌ Supabase CLI not found. Installing..."
    npm install -g supabase
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker and run this script again."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Initialize Supabase project (if not already initialized)
if [ ! -f "supabase/config.toml" ]; then
    echo "📁 Initializing Supabase project..."
    supabase init
    echo "✅ Supabase project initialized"
else
    echo "✅ Supabase project already initialized"
fi

# Start Supabase services
echo "🔄 Starting Supabase services..."
supabase start

echo "📊 Supabase services status:"
supabase status

# Apply migrations
echo "🔄 Applying database migrations..."
supabase db reset --local

echo "🌱 Seeding database with sample data..."
supabase db seed

# Generate TypeScript types
echo "🔄 Generating TypeScript types..."
if [ -f "scripts/supabase/generate-types.js" ]; then
    node scripts/supabase/generate-types.js
else
    supabase gen types typescript --local > supabase/types/database.types.ts
fi

echo "✅ Setup complete!"
echo ""
echo "🌐 Supabase Studio: http://localhost:54323"
echo "📧 Inbucket (Email testing): http://localhost:54324"
echo "🗄️ Database URL: postgresql://postgres:postgres@localhost:54322/postgres"
echo ""
echo "📝 Next steps:"
echo "1. Set up your environment variables in .env.local"
echo "2. Configure your OAuth providers in Supabase Studio"
echo "3. Start your application development!"
echo ""
echo "🛠️ Useful commands:"
echo "  supabase status       - Check service status"
echo "  supabase stop         - Stop all services"
echo "  supabase db reset     - Reset database with fresh migrations"
echo "  supabase db diff      - Check for schema changes"