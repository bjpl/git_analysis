# API Integration Specifications - PWA Conversion

## Overview

This document specifies the API integration architecture for converting the desktop application to a PWA, focusing on secure server-side API management, performance optimization, and scalability considerations.

## Current Desktop API Architecture

### Desktop Application API Usage
```python
# Current direct API calls from client
unsplash_headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Direct API calls expose keys in client-side code
response = requests.get(
    "https://api.unsplash.com/search/photos", 
    headers=unsplash_headers
)
```

**Limitations:**
- API keys stored locally in config files
- Direct client-to-API communication
- No centralized rate limiting or monitoring
- Limited error handling and retry logic
- No caching layer for repeated requests

## PWA API Architecture

### Server-Side API Proxy Pattern

```typescript
// Supabase Edge Function: image-search
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const { query, page = 1, per_page = 10 } = await req.json()
    
    // Server-side API call with stored secrets
    const unsplashResponse = await fetch(
      `https://api.unsplash.com/search/photos?query=${encodeURIComponent(query)}&page=${page}&per_page=${per_page}`,
      {
        headers: {
          'Authorization': `Client-ID ${Deno.env.get('UNSPLASH_ACCESS_KEY')}`,
          'Accept-Version': 'v1'
        }
      }
    )

    if (!unsplashResponse.ok) {
      throw new Error(`Unsplash API error: ${unsplashResponse.status}`)
    }

    const data = await unsplashResponse.json()
    
    return new Response(JSON.stringify(data), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    })
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    })
  }
})
```

## API Integration Specifications

### 1. Image Search Service (Unsplash API)

#### 1.1 Endpoint Specifications

**Edge Function:** `/functions/v1/image-search`

**Request Format:**
```typescript
interface ImageSearchRequest {
  query: string;           // Search term (required)
  page?: number;          // Page number (default: 1)
  per_page?: number;      // Results per page (default: 10, max: 30)
  orientation?: 'landscape' | 'portrait' | 'squarish';
  color?: string;         // Color filter
  featured?: boolean;     // Only featured photos
  user_id?: string;       // For personalized results
}
```

**Response Format:**
```typescript
interface ImageSearchResponse {
  results: Array<{
    id: string;
    urls: {
      raw: string;
      full: string;
      regular: string;
      small: string;
      thumb: string;
    };
    alt_description: string;
    description: string;
    user: {
      name: string;
      username: string;
    };
    created_at: string;
  }>;
  total: number;
  total_pages: number;
}
```

#### 1.2 Caching Strategy

```typescript
// Redis cache implementation in Edge Function
const cacheKey = `unsplash:${query}:${page}:${per_page}`;
const cached = await redis.get(cacheKey);

if (cached) {
  return new Response(cached, {
    headers: { 
      ...corsHeaders, 
      'Content-Type': 'application/json',
      'X-Cache': 'HIT'
    }
  });
}

// Cache for 30 minutes
await redis.setex(cacheKey, 1800, JSON.stringify(data));
```

#### 1.3 Rate Limiting

```typescript
// Rate limiting by user ID
const rateLimitKey = `rate_limit:image_search:${userId}`;
const currentCount = await redis.get(rateLimitKey) || 0;

if (currentCount >= 50) { // 50 requests per hour
  return new Response(JSON.stringify({
    error: 'Rate limit exceeded',
    reset_time: Date.now() + 3600000
  }), {
    status: 429,
    headers: corsHeaders
  });
}

await redis.incr(rateLimitKey);
await redis.expire(rateLimitKey, 3600);
```

### 2. AI Description Service (OpenAI API)

#### 2.1 Endpoint Specifications

**Edge Function:** `/functions/v1/ai-description`

**Request Format:**
```typescript
interface AIDescriptionRequest {
  image_url: string;       // Image URL (required)
  user_notes?: string;     // Optional context
  style: 'academic' | 'poetic' | 'technical';
  level: 'beginner' | 'intermediate' | 'advanced' | 'native';
  streaming?: boolean;     // Enable streaming response
  user_id: string;        // For usage tracking
}
```

**Streaming Response:**
```typescript
// Server-Sent Events for real-time streaming
const stream = new ReadableStream({
  start(controller) {
    openai.chat.completions.create({
      model: 'gpt-4-vision-preview',
      messages: [
        {
          role: 'user',
          content: [
            { type: 'text', text: prompt },
            { type: 'image_url', image_url: { url: image_url } }
          ]
        }
      ],
      stream: true
    }).then(async (completion) => {
      for await (const chunk of completion) {
        const content = chunk.choices[0]?.delta?.content || '';
        if (content) {
          controller.enqueue(`data: ${JSON.stringify({ content })}\n\n`);
        }
      }
      controller.close();
    });
  }
});

return new Response(stream, {
  headers: {
    ...corsHeaders,
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive'
  }
});
```

#### 2.2 Prompt Management

```typescript
// Dynamic prompt generation based on user preferences
class PromptBuilder {
  static buildDescriptionPrompt(
    style: StyleType, 
    level: LevelType, 
    context?: string
  ): string {
    const basePrompt = "Describe this image in Spanish";
    const styleInstructions = this.getStyleInstructions(style);
    const levelInstructions = this.getLevelInstructions(level);
    
    return `${basePrompt}. ${styleInstructions} ${levelInstructions}${
      context ? `\n\nUser context: ${context}` : ''
    }`;
  }

  private static getStyleInstructions(style: StyleType): string {
    const instructions = {
      academic: "Use formal, educational language with precise terminology.",
      poetic: "Use descriptive, artistic language with metaphors and imagery.",
      technical: "Use specific, technical vocabulary with detailed observations."
    };
    return instructions[style];
  }

  private static getLevelInstructions(level: LevelType): string {
    const instructions = {
      beginner: "Use simple vocabulary and basic sentence structures.",
      intermediate: "Use moderate vocabulary with some complex structures.",
      advanced: "Use sophisticated vocabulary and complex grammar.",
      native: "Use native-level expressions and cultural references."
    };
    return instructions[level];
  }
}
```

### 3. Vocabulary Extraction Service

#### 3.1 Endpoint Specifications

**Edge Function:** `/functions/v1/vocabulary-extract`

**Request Format:**
```typescript
interface VocabularyExtractionRequest {
  text: string;           // Spanish text to analyze
  level: LevelType;       // User's learning level
  categories: string[];   // Desired categories
  max_per_category?: number; // Max items per category (default: 5)
}
```

**Response Format:**
```typescript
interface VocabularyExtractionResponse {
  categories: {
    sustantivos: Array<{
      spanish: string;
      english: string;
      confidence: number;
      frequency_rank: number;
    }>;
    verbos: Array<{
      spanish: string;
      english: string;
      conjugation: string;
      confidence: number;
    }>;
    adjetivos: Array<{
      spanish: string;
      english: string;
      gender_agreement: string;
      confidence: number;
    }>;
    frases_clave: Array<{
      spanish: string;
      english: string;
      context_importance: number;
      confidence: number;
    }>;
  };
  metadata: {
    processing_time_ms: number;
    total_extractions: number;
    difficulty_level: string;
  };
}
```

#### 3.2 Smart Extraction Algorithm

```typescript
class VocabularyExtractor {
  async extractFromText(
    text: string, 
    userLevel: LevelType,
    existingVocabulary: Set<string>
  ): Promise<VocabularyExtractionResponse> {
    
    const prompt = this.buildExtractionPrompt(text, userLevel);
    
    const response = await this.openai.chat.completions.create({
      model: 'gpt-4',
      messages: [{ role: 'user', content: prompt }],
      response_format: { type: 'json_object' },
      temperature: 0.3
    });

    const extracted = JSON.parse(response.choices[0].message.content);
    
    // Filter out already known vocabulary
    const filtered = this.filterKnownVocabulary(extracted, existingVocabulary);
    
    // Rank by learning priority
    const ranked = this.rankByPriority(filtered, userLevel);
    
    return this.formatResponse(ranked);
  }

  private filterKnownVocabulary(
    extracted: any, 
    known: Set<string>
  ): any {
    Object.keys(extracted).forEach(category => {
      extracted[category] = extracted[category].filter(
        item => !known.has(item.spanish.toLowerCase())
      );
    });
    return extracted;
  }

  private rankByPriority(vocabulary: any, level: LevelType): any {
    const priorityWeights = {
      beginner: { frequency: 0.7, difficulty: 0.3 },
      intermediate: { frequency: 0.5, difficulty: 0.5 },
      advanced: { frequency: 0.3, difficulty: 0.7 },
      native: { frequency: 0.2, difficulty: 0.8 }
    };
    
    const weights = priorityWeights[level];
    
    Object.keys(vocabulary).forEach(category => {
      vocabulary[category].sort((a, b) => {
        const scoreA = (a.frequency_rank * weights.frequency) + 
                      (a.difficulty_score * weights.difficulty);
        const scoreB = (b.frequency_rank * weights.frequency) + 
                      (b.difficulty_score * weights.difficulty);
        return scoreB - scoreA;
      });
    });
    
    return vocabulary;
  }
}
```

### 4. Translation Service

#### 4.1 Context-Aware Translation

**Edge Function:** `/functions/v1/translate`

```typescript
interface TranslationRequest {
  spanish_text: string;
  context?: string;        // Original description for context
  image_url?: string;      // Image context
  user_level: LevelType;   // For appropriate explanation level
}

interface TranslationResponse {
  english_translation: string;
  alternative_translations?: string[];
  grammatical_info: {
    word_type: string;
    gender?: string;
    conjugation?: string;
  };
  usage_examples: Array<{
    spanish: string;
    english: string;
  }>;
  difficulty_level: number; // 1-5 scale
  cultural_notes?: string;
}
```

#### 4.2 Translation Caching

```typescript
// Multilevel caching strategy
class TranslationCache {
  async getTranslation(
    spanish: string, 
    context?: string
  ): Promise<TranslationResponse | null> {
    
    // Level 1: Exact match with context
    const exactKey = `translation:${spanish}:${this.hashContext(context)}`;
    let cached = await redis.get(exactKey);
    if (cached) return JSON.parse(cached);
    
    // Level 2: Word/phrase without context
    const wordKey = `translation:${spanish}`;
    cached = await redis.get(wordKey);
    if (cached) {
      const translation = JSON.parse(cached);
      // Enhance with context if available
      return context ? this.enhanceWithContext(translation, context) : translation;
    }
    
    return null;
  }

  async cacheTranslation(
    spanish: string, 
    translation: TranslationResponse,
    context?: string
  ): Promise<void> {
    const exactKey = `translation:${spanish}:${this.hashContext(context)}`;
    const wordKey = `translation:${spanish}`;
    
    // Cache with context for 7 days
    await redis.setex(exactKey, 604800, JSON.stringify(translation));
    
    // Cache without context for 30 days (base translation)
    const baseTranslation = { ...translation };
    delete baseTranslation.usage_examples; // Remove context-specific examples
    await redis.setex(wordKey, 2592000, JSON.stringify(baseTranslation));
  }
}
```

### 5. User Progress & Analytics Service

#### 5.1 Learning Analytics

**Edge Function:** `/functions/v1/analytics`

```typescript
interface AnalyticsData {
  user_id: string;
  session_data: {
    session_id: string;
    start_time: Date;
    duration_minutes: number;
    images_viewed: number;
    vocabulary_collected: number;
    translations_requested: number;
    quiz_attempts: number;
    quiz_accuracy: number;
  };
  vocabulary_interactions: Array<{
    spanish_text: string;
    action: 'view' | 'translate' | 'collect' | 'quiz_correct' | 'quiz_incorrect';
    timestamp: Date;
    context: string;
  }>;
}

class AnalyticsProcessor {
  async processSessionData(data: AnalyticsData): Promise<void> {
    await Promise.all([
      this.updateUserProgress(data),
      this.updateVocabularyScores(data),
      this.calculateSpacedRepetition(data),
      this.generateRecommendations(data)
    ]);
  }

  private async updateVocabularyScores(data: AnalyticsData): Promise<void> {
    const { supabase } = this;
    
    for (const interaction of data.vocabulary_interactions) {
      const scoreUpdate = this.calculateScoreChange(interaction);
      
      await supabase
        .from('vocabulary')
        .update({
          learning_score: supabase.raw(`learning_score + ${scoreUpdate}`),
          last_reviewed: new Date(),
          next_review: this.calculateNextReview(interaction, scoreUpdate)
        })
        .eq('spanish_text', interaction.spanish_text)
        .eq('user_id', data.user_id);
    }
  }

  private calculateNextReview(
    interaction: VocabularyInteraction, 
    scoreChange: number
  ): Date {
    // SM-2 spaced repetition algorithm
    const baseIntervals = [1, 6, 24, 72, 168, 336]; // hours
    const currentScore = Math.max(0, Math.min(5, interaction.current_score + scoreChange));
    const intervalHours = baseIntervals[currentScore] || 672; // 4 weeks max
    
    return new Date(Date.now() + intervalHours * 60 * 60 * 1000);
  }
}
```

### 6. Security & Rate Limiting

#### 6.1 Authentication Middleware

```typescript
// JWT verification middleware
async function authenticateUser(req: Request): Promise<string | null> {
  const authHeader = req.headers.get('Authorization');
  if (!authHeader?.startsWith('Bearer ')) {
    return null;
  }

  const token = authHeader.substring(7);
  
  try {
    const { data: { user }, error } = await supabase.auth.getUser(token);
    if (error || !user) {
      return null;
    }
    
    return user.id;
  } catch (error) {
    console.error('Auth verification failed:', error);
    return null;
  }
}
```

#### 6.2 Comprehensive Rate Limiting

```typescript
class RateLimiter {
  private limits = {
    image_search: { requests: 50, window: 3600 }, // 50/hour
    ai_description: { requests: 100, window: 3600 }, // 100/hour
    translation: { requests: 500, window: 3600 }, // 500/hour
    vocabulary_extract: { requests: 200, window: 3600 } // 200/hour
  };

  async checkLimit(
    service: string, 
    userId: string
  ): Promise<{ allowed: boolean; resetTime?: number }> {
    const limit = this.limits[service];
    if (!limit) return { allowed: true };

    const key = `rate_limit:${service}:${userId}`;
    const current = await redis.get(key);
    
    if (!current) {
      await redis.setex(key, limit.window, 1);
      return { allowed: true };
    }

    const count = parseInt(current);
    if (count >= limit.requests) {
      const ttl = await redis.ttl(key);
      return { 
        allowed: false, 
        resetTime: Date.now() + (ttl * 1000)
      };
    }

    await redis.incr(key);
    return { allowed: true };
  }
}
```

### 7. Error Handling & Monitoring

#### 7.1 Comprehensive Error Handling

```typescript
class APIErrorHandler {
  static handleError(error: any, service: string): Response {
    const timestamp = new Date().toISOString();
    const errorId = crypto.randomUUID();
    
    // Log error for monitoring
    console.error(`[${timestamp}] ${service} Error ${errorId}:`, error);
    
    // Determine error type and response
    if (error.name === 'RateLimitError') {
      return new Response(JSON.stringify({
        error: 'Rate limit exceeded',
        error_id: errorId,
        retry_after: error.retryAfter
      }), {
        status: 429,
        headers: {
          'Content-Type': 'application/json',
          'Retry-After': error.retryAfter.toString()
        }
      });
    }

    if (error.name === 'APIKeyError') {
      return new Response(JSON.stringify({
        error: 'Service temporarily unavailable',
        error_id: errorId
      }), {
        status: 503,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Generic error response
    return new Response(JSON.stringify({
      error: 'Internal server error',
      error_id: errorId
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
```

### 8. Performance Optimization

#### 8.1 Response Optimization

```typescript
// Response compression and optimization
function optimizeResponse(data: any): Response {
  const compressed = gzip(JSON.stringify(data));
  
  return new Response(compressed, {
    headers: {
      'Content-Type': 'application/json',
      'Content-Encoding': 'gzip',
      'Cache-Control': 'public, max-age=300', // 5 minutes
      'ETag': generateETag(data)
    }
  });
}

// Batch API optimization
class BatchProcessor {
  async processBatch<T, R>(
    items: T[],
    processor: (item: T) => Promise<R>,
    batchSize = 5
  ): Promise<R[]> {
    const results: R[] = [];
    
    for (let i = 0; i < items.length; i += batchSize) {
      const batch = items.slice(i, i + batchSize);
      const batchResults = await Promise.all(
        batch.map(item => processor(item))
      );
      results.push(...batchResults);
    }
    
    return results;
  }
}
```

This API integration specification provides a comprehensive foundation for implementing secure, scalable, and performant server-side API management for the PWA conversion, ensuring proper security, monitoring, and optimization throughout the system.