// Quick API Connection Test Script
import dotenv from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Load environment variables
const envPath = join(__dirname, '.env');
if (fs.existsSync(envPath)) {
  dotenv.config({ path: envPath });
  console.log('✅ Environment variables loaded');
} else {
  console.error('❌ .env file not found');
  process.exit(1);
}

// Test Unsplash API
async function testUnsplash() {
  const apiKey = process.env.VITE_UNSPLASH_API_KEY;
  if (!apiKey) {
    console.error('❌ Unsplash API key not found');
    return false;
  }
  
  try {
    const response = await fetch('https://api.unsplash.com/photos/random', {
      headers: {
        'Authorization': `Client-ID ${apiKey}`
      }
    });
    
    if (response.ok) {
      console.log('✅ Unsplash API: Connected successfully');
      return true;
    } else {
      console.error(`❌ Unsplash API: ${response.status} ${response.statusText}`);
      return false;
    }
  } catch (error) {
    console.error('❌ Unsplash API:', error.message);
    return false;
  }
}

// Test OpenAI API
async function testOpenAI() {
  const apiKey = process.env.VITE_OPENAI_API_KEY;
  if (!apiKey) {
    console.error('❌ OpenAI API key not found');
    return false;
  }
  
  try {
    const response = await fetch('https://api.openai.com/v1/models', {
      headers: {
        'Authorization': `Bearer ${apiKey}`
      }
    });
    
    if (response.ok) {
      console.log('✅ OpenAI API: Connected successfully');
      return true;
    } else {
      console.error(`❌ OpenAI API: ${response.status} ${response.statusText}`);
      return false;
    }
  } catch (error) {
    console.error('❌ OpenAI API:', error.message);
    return false;
  }
}

// Test Supabase
async function testSupabase() {
  const url = process.env.VITE_SUPABASE_URL;
  const key = process.env.VITE_SUPABASE_ANON_KEY;
  
  if (!url || !key) {
    console.error('❌ Supabase credentials not found');
    return false;
  }
  
  try {
    const response = await fetch(`${url}/rest/v1/`, {
      headers: {
        'apikey': key,
        'Authorization': `Bearer ${key}`
      }
    });
    
    if (response.ok || response.status === 404) { // 404 is ok, means API is reachable
      console.log('✅ Supabase: Connected successfully');
      return true;
    } else {
      console.error(`❌ Supabase: ${response.status} ${response.statusText}`);
      return false;
    }
  } catch (error) {
    console.error('❌ Supabase:', error.message);
    return false;
  }
}

// Run all tests
async function runTests() {
  console.log('\n🔍 Testing API Connections...\n');
  
  const results = await Promise.all([
    testUnsplash(),
    testOpenAI(),
    testSupabase()
  ]);
  
  const allPassed = results.every(r => r);
  
  console.log('\n' + '='.repeat(40));
  if (allPassed) {
    console.log('✅ All API connections successful!');
  } else {
    console.log('⚠️  Some API connections failed');
    console.log('Please check your .env file');
  }
  console.log('='.repeat(40) + '\n');
}

runTests();