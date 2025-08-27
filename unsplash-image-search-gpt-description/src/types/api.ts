/**
 * Comprehensive API Types and Interfaces for VocabLens
 * Centralized type definitions for all external service integrations
 */

// ========================================
// COMMON API TYPES
// ========================================

export interface ApiResponse<T = any> {
  data: T;
  success: boolean;
  error?: ApiError;
  meta?: {
    timestamp: string;
    requestId: string;
    service: string;
    cached?: boolean;
    rateLimit?: RateLimitInfo;
  };
}

export interface ApiError {
  code: string;
  message: string;
  details?: any;
  statusCode?: number;
  service: 'unsplash' | 'openai' | 'supabase' | 'translate' | 'app';
  endpoint?: string;
  retryable?: boolean;
  retryAfter?: number;
  correlationId?: string;
  timestamp?: string;
  userMessage?: string;
  suggestions?: string[];
  documentation?: string;
}

export interface RateLimitInfo {
  limit: number;
  remaining: number;
  reset: number;
  retryAfter?: number;
}

export interface PaginationParams {
  page?: number;
  per_page?: number;
  cursor?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    per_page: number;
    total: number;
    total_pages: number;
    has_next: boolean;
    has_prev: boolean;
    next_cursor?: string;
    prev_cursor?: string;
  };
}

// ========================================
// UNSPLASH API TYPES
// ========================================

export namespace UnsplashAPI {
  export interface Image {
    id: string;
    created_at: string;
    updated_at: string;
    width: number;
    height: number;
    color: string;
    blur_hash?: string;
    downloads: number;
    likes: number;
    description?: string;
    alt_description?: string;
    urls: {
      raw: string;
      full: string;
      regular: string;
      small: string;
      thumb: string;
    };
    links: {
      self: string;
      html: string;
      download: string;
      download_location: string;
    };
    user: User;
    exif?: ExifData;
    location?: Location;
    tags: Tag[];
    current_user_collections?: Collection[];
    sponsored?: boolean;
    sponsorship?: Sponsorship;
  }

  export interface User {
    id: string;
    username: string;
    name: string;
    first_name: string;
    last_name?: string;
    portfolio_url?: string;
    bio?: string;
    location?: string;
    total_likes: number;
    total_photos: number;
    total_collections: number;
    instagram_username?: string;
    twitter_username?: string;
    profile_image: {
      small: string;
      medium: string;
      large: string;
    };
    links: {
      self: string;
      html: string;
      photos: string;
      likes: string;
      portfolio: string;
    };
  }

  export interface Tag {
    type: string;
    title: string;
    source?: {
      ancestry: {
        type: {
          slug: string;
          pretty_slug: string;
        };
        category?: {
          slug: string;
          pretty_slug: string;
        };
        subcategory?: {
          slug: string;
          pretty_slug: string;
        };
      };
      title: string;
      subtitle: string;
      description: string;
      meta_title: string;
      meta_description: string;
      cover_photo: Image;
    };
  }

  export interface Collection {
    id: string;
    title: string;
    description?: string;
    published_at: string;
    last_collected_at: string;
    updated_at: string;
    total_photos: number;
    private: boolean;
    share_key?: string;
    cover_photo?: Image;
    preview_photos?: Image[];
    user: User;
    links: {
      self: string;
      html: string;
      photos: string;
    };
  }

  export interface ExifData {
    make?: string;
    model?: string;
    name?: string;
    exposure_time?: string;
    aperture?: string;
    focal_length?: string;
    iso?: number;
  }

  export interface Location {
    name?: string;
    city?: string;
    country?: string;
    position: {
      latitude: number;
      longitude: number;
    };
  }

  export interface Sponsorship {
    impression_urls: string[];
    tagline: string;
    tagline_url: string;
    sponsor: User;
  }

  export interface SearchParams {
    query: string;
    page?: number;
    per_page?: number;
    order_by?: 'latest' | 'oldest' | 'popular' | 'relevant';
    collections?: string;
    content_filter?: 'low' | 'high';
    color?: 'black_and_white' | 'black' | 'white' | 'yellow' | 'orange' | 'red' | 'purple' | 'magenta' | 'green' | 'teal' | 'blue';
    orientation?: 'landscape' | 'portrait' | 'squarish';
  }

  export interface SearchResponse {
    total: number;
    total_pages: number;
    results: Image[];
  }

  export interface DownloadResponse {
    url: string;
  }

  export interface Statistics {
    id: string;
    downloads: {
      total: number;
      historical: {
        change: number;
        average: number;
        resolution: string;
        quantity: number;
        values: Array<{
          date: string;
          value: number;
        }>;
      };
    };
    views: {
      total: number;
      historical: {
        change: number;
        average: number;
        resolution: string;
        quantity: number;
        values: Array<{
          date: string;
          value: number;
        }>;
      };
    };
  }
}

// ========================================
// OPENAI API TYPES
// ========================================

export namespace OpenAIAPI {
  export interface ChatMessage {
    role: 'system' | 'user' | 'assistant' | 'function';
    content: string;
    name?: string;
    function_call?: {
      name: string;
      arguments: string;
    };
  }

  export interface ChatCompletionRequest {
    model: string;
    messages: ChatMessage[];
    temperature?: number;
    max_tokens?: number;
    top_p?: number;
    n?: number;
    stream?: boolean;
    stop?: string | string[];
    presence_penalty?: number;
    frequency_penalty?: number;
    logit_bias?: Record<string, number>;
    user?: string;
    functions?: FunctionDefinition[];
    function_call?: 'none' | 'auto' | { name: string };
  }

  export interface ChatCompletionResponse {
    id: string;
    object: string;
    created: number;
    model: string;
    system_fingerprint?: string;
    choices: Array<{
      index: number;
      message: ChatMessage;
      logprobs?: {
        content: Array<{
          token: string;
          logprob: number;
          bytes: number[];
          top_logprobs: Array<{
            token: string;
            logprob: number;
            bytes: number[];
          }>;
        }>;
      };
      finish_reason: 'stop' | 'length' | 'function_call' | 'content_filter' | 'null';
    }>;
    usage: {
      prompt_tokens: number;
      completion_tokens: number;
      total_tokens: number;
    };
  }

  export interface FunctionDefinition {
    name: string;
    description?: string;
    parameters: {
      type: 'object';
      properties: Record<string, any>;
      required?: string[];
    };
  }

  export interface Model {
    id: string;
    object: string;
    created: number;
    owned_by: string;
  }

  export interface ModelsResponse {
    object: string;
    data: Model[];
  }

  export interface EmbeddingRequest {
    model: string;
    input: string | string[] | number[] | number[][];
    encoding_format?: 'float' | 'base64';
    dimensions?: number;
    user?: string;
  }

  export interface EmbeddingResponse {
    object: string;
    data: Array<{
      object: string;
      embedding: number[];
      index: number;
    }>;
    model: string;
    usage: {
      prompt_tokens: number;
      total_tokens: number;
    };
  }

  export interface ImageGenerationRequest {
    prompt: string;
    model?: string;
    n?: number;
    quality?: 'standard' | 'hd';
    response_format?: 'url' | 'b64_json';
    size?: '1024x1024' | '1792x1024' | '1024x1792';
    style?: 'vivid' | 'natural';
    user?: string;
  }

  export interface ImageGenerationResponse {
    created: number;
    data: Array<{
      revised_prompt?: string;
      url?: string;
      b64_json?: string;
    }>;
  }

  export interface ModerationRequest {
    input: string | string[];
    model?: string;
  }

  export interface ModerationResponse {
    id: string;
    model: string;
    results: Array<{
      flagged: boolean;
      categories: {
        sexual: boolean;
        hate: boolean;
        harassment: boolean;
        'self-harm': boolean;
        'sexual/minors': boolean;
        'hate/threatening': boolean;
        'violence/graphic': boolean;
        'self-harm/intent': boolean;
        'self-harm/instructions': boolean;
        'harassment/threatening': boolean;
        violence: boolean;
      };
      category_scores: {
        sexual: number;
        hate: number;
        harassment: number;
        'self-harm': number;
        'sexual/minors': number;
        'hate/threatening': number;
        'violence/graphic': number;
        'self-harm/intent': number;
        'self-harm/instructions': number;
        'harassment/threatening': number;
        violence: number;
      };
    }>;
  }
}

// ========================================
// SUPABASE API TYPES
// ========================================

export namespace SupabaseAPI {
  export interface Profile {
    id: string;
    email: string;
    username?: string;
    full_name?: string;
    avatar_url?: string;
    language_preference: string;
    daily_goal: number;
    timezone?: string;
    learning_streak: number;
    total_vocabulary: number;
    created_at: string;
    updated_at: string;
  }

  export interface VocabularyItem {
    id: string;
    user_id: string;
    word: string;
    definition: string;
    translation?: string;
    pronunciation?: string;
    part_of_speech?: string;
    language: string;
    difficulty_level: number;
    context?: string;
    image_id?: string;
    image_url?: string;
    learned: boolean;
    review_count: number;
    correct_count: number;
    last_reviewed: string | null;
    next_review: string | null;
    ease_factor: number;
    interval_days: number;
    tags: string[];
    examples: string[];
    created_at: string;
    updated_at: string;
  }

  export interface SearchSession {
    id: string;
    user_id: string;
    query: string;
    total_images: number;
    vocabulary_created: number;
    duration_seconds: number;
    metadata: Record<string, any>;
    created_at: string;
  }

  export interface QuizResult {
    id: string;
    user_id: string;
    vocabulary_item_id: string;
    question_type: 'definition' | 'translation' | 'context' | 'pronunciation';
    correct: boolean;
    response_time_ms: number;
    difficulty_level: number;
    created_at: string;
  }

  export interface SharedList {
    id: string;
    user_id: string;
    title: string;
    description?: string;
    vocabulary_ids: string[];
    public: boolean;
    share_code?: string;
    download_count: number;
    created_at: string;
    updated_at: string;
  }

  export interface UserPreferences {
    id: string;
    user_id: string;
    theme: 'light' | 'dark' | 'auto';
    language: string;
    notifications_enabled: boolean;
    sound_enabled: boolean;
    auto_pronunciation: boolean;
    difficulty_preference: number;
    daily_goal: number;
    preferred_image_style: string;
    learning_mode: 'casual' | 'intensive' | 'exam_prep';
    created_at: string;
    updated_at: string;
  }

  export interface LearningStatistics {
    user_id: string;
    date: string;
    vocabulary_learned: number;
    quiz_attempts: number;
    quiz_correct: number;
    study_time_minutes: number;
    images_viewed: number;
    streak_days: number;
  }

  export interface DatabaseError {
    message: string;
    details?: string;
    hint?: string;
    code?: string;
  }

  export interface RealtimePayload<T = any> {
    commit_timestamp: string;
    eventType: 'INSERT' | 'UPDATE' | 'DELETE';
    schema: string;
    table: string;
    columns: Array<{
      name: string;
      type: string;
    }>;
    record: T;
    old_record?: T;
  }
}

// ========================================
// TRANSLATION API TYPES
// ========================================

export namespace TranslationAPI {
  export interface GoogleTranslateRequest {
    q: string | string[];
    target: string;
    source?: string;
    format?: 'text' | 'html';
    model?: 'base' | 'nmt';
  }

  export interface GoogleTranslateResponse {
    data: {
      translations: Array<{
        translatedText: string;
        detectedSourceLanguage?: string;
        model?: string;
      }>;
    };
  }

  export interface DeepLTranslateRequest {
    text: string | string[];
    target_lang: string;
    source_lang?: string;
    split_sentences?: 'none' | 'all' | 'nonewlines';
    preserve_formatting?: boolean;
    formality?: 'default' | 'more' | 'less' | 'prefer_more' | 'prefer_less';
    glossary_id?: string;
    tag_handling?: 'xml' | 'html';
    outline_detection?: boolean;
    non_splitting_tags?: string[];
    splitting_tags?: string[];
    ignore_tags?: string[];
  }

  export interface DeepLTranslateResponse {
    translations: Array<{
      detected_source_language: string;
      text: string;
    }>;
  }

  export interface LanguageDetectionRequest {
    q: string;
  }

  export interface LanguageDetectionResponse {
    data: {
      detections: Array<Array<{
        language: string;
        isReliable: boolean;
        confidence: number;
      }>>;
    };
  }

  export interface SupportedLanguage {
    language: string;
    name: string;
    supports_formality?: boolean;
  }
}

// ========================================
// VOCABULARY GENERATION TYPES
// ========================================

export interface VocabularyGenerationOptions {
  word: string;
  context?: string;
  imageDescription?: string;
  imageUrl?: string;
  targetLanguage: string;
  sourceLanguage: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  style: 'simple' | 'detailed' | 'academic' | 'conversational';
  includeExamples: boolean;
  includeTranslation: boolean;
  includePronunciation: boolean;
  maxLength?: number;
  customPrompt?: string;
}

export interface GeneratedVocabulary {
  word: string;
  definition: string;
  translation?: string;
  pronunciation?: string;
  partOfSpeech?: string;
  examples: string[];
  context: string;
  difficulty: number;
  tags: string[];
  relatedWords?: string[];
  etymology?: string;
  culturalNotes?: string;
  memoryTips?: string[];
  confidence: number;
  generationTime: number;
  model: string;
}

// ========================================
// CACHE & STORAGE TYPES
// ========================================

export interface CacheEntry<T = any> {
  data: T;
  timestamp: number;
  ttl: number;
  key: string;
  version: string;
  compressed?: boolean;
  tags?: string[];
}

export interface StorageQuota {
  usage: number;
  quota: number;
  available: number;
  percentage: number;
}

export interface BackupData {
  version: string;
  timestamp: string;
  user_id: string;
  vocabulary: SupabaseAPI.VocabularyItem[];
  preferences: SupabaseAPI.UserPreferences;
  statistics: SupabaseAPI.LearningStatistics[];
  metadata: {
    total_items: number;
    export_reason: string;
    app_version: string;
  };
}

// ========================================
// PERFORMANCE & MONITORING TYPES
// ========================================

export interface PerformanceMetric {
  name: string;
  value: number;
  unit: string;
  timestamp: number;
  tags: Record<string, string>;
}

export interface APICallMetrics {
  service: string;
  endpoint: string;
  method: string;
  status: number;
  duration: number;
  size: number;
  cached: boolean;
  retries: number;
  timestamp: number;
}

export interface ErrorMetrics {
  service: string;
  error_code: string;
  error_message: string;
  count: number;
  last_occurrence: string;
  user_affected: boolean;
}

// ========================================
// WEBHOOK & REAL-TIME TYPES
// ========================================

export interface WebhookPayload<T = any> {
  id: string;
  event: string;
  created: number;
  data: T;
  type: string;
  livemode: boolean;
  pending_webhooks: number;
  request: {
    id: string;
    idempotency_key?: string;
  };
}

export interface RealtimeSubscription {
  id: string;
  table: string;
  filter?: string;
  event: 'INSERT' | 'UPDATE' | 'DELETE' | '*';
  callback: (payload: SupabaseAPI.RealtimePayload) => void;
  status: 'SUBSCRIBED' | 'TIMED_OUT' | 'CLOSED' | 'CHANNEL_ERROR';
}

// ========================================
// UTILITY TYPES
// ========================================

export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>;

export type OptionalFields<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

export type ServiceName = 'unsplash' | 'openai' | 'supabase' | 'translate';

export type Environment = 'development' | 'staging' | 'production' | 'test';

export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

// ========================================
// VALIDATION TYPES
// ========================================

export interface ValidationRule {
  field: string;
  rules: Array<{
    type: 'required' | 'min' | 'max' | 'pattern' | 'custom';
    value?: any;
    message: string;
    validator?: (value: any) => boolean;
  }>;
}

export interface ValidationResult {
  valid: boolean;
  errors: Array<{
    field: string;
    message: string;
    value?: any;
  }>;
}

// ========================================
// EXPORT MAIN TYPES
// ========================================

export {
  ApiResponse,
  ApiError,
  RateLimitInfo,
  PaginationParams,
  PaginatedResponse,
  VocabularyGenerationOptions,
  GeneratedVocabulary,
  CacheEntry,
  StorageQuota,
  BackupData,
  PerformanceMetric,
  APICallMetrics,
  ErrorMetrics,
  ValidationRule,
  ValidationResult,
  ServiceName,
  Environment,
  LogLevel,
  DeepPartial,
  RequiredFields,
  OptionalFields
};