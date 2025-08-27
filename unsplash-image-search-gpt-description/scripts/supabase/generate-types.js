#!/usr/bin/env node

const { execSync } = require('child_process')
const fs = require('fs')
const path = require('path')

/**
 * Generate TypeScript types from Supabase schema
 * This script uses the Supabase CLI to generate types from the database schema
 */
async function generateTypes() {
  try {
    console.log('🔄 Generating TypeScript types from Supabase schema...')
    
    // Check if Supabase CLI is installed
    try {
      execSync('supabase --version', { stdio: 'pipe' })
    } catch (error) {
      console.error('❌ Supabase CLI is not installed. Please install it first:')
      console.error('npm install -g supabase')
      process.exit(1)
    }

    // Check if we're in a Supabase project
    const configPath = path.join(process.cwd(), 'supabase', 'config.toml')
    if (!fs.existsSync(configPath)) {
      console.error('❌ Not in a Supabase project directory. Please run from the project root.')
      process.exit(1)
    }

    // Generate types
    const outputPath = path.join(process.cwd(), 'supabase', 'types', 'database.types.ts')
    const command = `supabase gen types typescript --local > "${outputPath}"`
    
    console.log('📝 Running command:', command)
    execSync(command, { stdio: 'inherit' })
    
    console.log('✅ TypeScript types generated successfully!')
    console.log('📁 Output location:', outputPath)
    
    // Verify the file was created
    if (fs.existsSync(outputPath)) {
      const stats = fs.statSync(outputPath)
      console.log(`📊 File size: ${(stats.size / 1024).toFixed(2)} KB`)
    } else {
      console.error('❌ Types file was not created. Check your Supabase setup.')
      process.exit(1)
    }
    
  } catch (error) {
    console.error('❌ Error generating types:', error.message)
    process.exit(1)
  }
}

/**
 * Generate types from remote Supabase project
 */
async function generateTypesFromRemote(projectRef) {
  try {
    console.log(`🌐 Generating types from remote project: ${projectRef}`)
    
    const outputPath = path.join(process.cwd(), 'supabase', 'types', 'database.types.ts')
    const command = `supabase gen types typescript --project-id ${projectRef} > "${outputPath}"`
    
    console.log('📝 Running command:', command)
    execSync(command, { stdio: 'inherit' })
    
    console.log('✅ Remote TypeScript types generated successfully!')
    console.log('📁 Output location:', outputPath)
    
  } catch (error) {
    console.error('❌ Error generating remote types:', error.message)
    console.error('Make sure you are logged in: supabase auth login')
    process.exit(1)
  }
}

// Parse command line arguments
const args = process.argv.slice(2)
const remoteFlag = args.find(arg => arg.startsWith('--remote='))

if (remoteFlag) {
  const projectRef = remoteFlag.split('=')[1]
  if (!projectRef) {
    console.error('❌ Please provide a project reference: --remote=your-project-ref')
    process.exit(1)
  }
  generateTypesFromRemote(projectRef)
} else {
  generateTypes()
}