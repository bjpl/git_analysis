/**
 * OpenAI API Service for VocabLens PWA
 * Handles AI-powered text generation and vocabulary descriptions
 */
import { apiConfig, getApiHeaders, buildApiUrl, ApiError, timeouts } from '../config/api';
import { apiConfigService } from './apiConfigService';
import { retryWithBackoff, CircuitBreaker, RetryPolicy } from './retryService';
import { cacheService } from './cacheService';
import { rateLimiter } from './rateLimiter';
import { apiMonitoringService } from './apiMonitoringService';

export interface ChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

export interface ChatCompletionRequest {
  model: string;
  messages: ChatMessage[];
  temperature?: number;
  max_tokens?: number;
  top_p?: number;
  frequency_penalty?: number;
  presence_penalty?: number;
  stop?: string[];
}

export interface ChatCompletionResponse {
  id: string;
  object: string;
  created: number;
  model: string;
  choices: Array<{
    index: number;
    message: ChatMessage;
    finish_reason: string;
  }>;
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

export interface VisionRequest {
  imageUrl: string;
  prompt?: string;
  maxTokens?: number;
  detail?: 'low' | 'high';
}

export interface StreamingOptions {
  onToken?: (token: string) => void;
  onComplete?: (fullResponse: string) => void;
  onError?: (error: Error) => void;
}

export interface VocabularyGenerationOptions {
  word: string;
  context?: string;
  imageDescription?: string;
  difficulty?: 'beginner' | 'intermediate' | 'advanced';
  style?: 'simple' | 'detailed' | 'academic' | 'conversational';
  includeExamples?: boolean;
  maxLength?: number;
  streaming?: boolean;
  streamingOptions?: StreamingOptions;
}

export interface GeneratedVocabulary {
  word: string;
  definition: string;
  translation?: string;
  examples: string[];
  context: string;
  difficulty: number;
  tags: string[];
  pronunciation?: string;
}

class OpenAIService {
  private readonly baseUrl = apiConfig.endpoints.openai.base;
  private requestQueue: Promise<any>[] = [];
  private circuitBreaker: CircuitBreaker;
  private retryPolicy: RetryPolicy;

  constructor() {
    this.circuitBreaker = new CircuitBreaker({
      failureThreshold: 3,
      recoveryTimeout: 60000,
      monitoringPeriod: 120000
    });
    
    this.retryPolicy = {
      maxRetries: 2,
      baseDelay: 2000,
      maxDelay: 15000,
      backoffMultiplier: 2.5,
      jitter: true,
      retryableStatusCodes: [408, 429, 500, 502, 503, 504]
    };
  }

  /**
   * Get API headers with runtime or fallback API key
   */
  private async getHeaders(): Promise<Record<string, string>> {
    const apiKey = await apiConfigService.getEffectiveApiKey('openai');
    
    if (!apiKey) {
      throw new ApiError(
        'OpenAI API key not configured. Please set up your API key in settings.',
        401,
        'NO_API_KEY',
        'openai'
      );
    }

    return {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json'
    };
  }

  /**
   * Generate a chat completion using OpenAI API with advanced retry and caching
   */
  async createChatCompletion(
    request: ChatCompletionRequest, 
    streaming?: boolean,
    streamingOptions?: StreamingOptions
  ): Promise<ChatCompletionResponse> {
    const startTime = Date.now();
    
    try {
      this.validateChatRequest(request);
      
      // Generate cache key for non-streaming requests
      const cacheKey = !streaming ? this.generateCacheKey('completion', request) : null;
      
      // Check cache for non-streaming requests
      if (cacheKey) {
        const cachedResult = await cacheService.get<ChatCompletionResponse>(cacheKey);
        if (cachedResult) {
          apiMonitoringService.recordCacheHit('openai', 'createChatCompletion');
          return cachedResult;
        }
      }
      
      await rateLimiter.acquire('openai', this.calculateTokenCost(request));

      const url = buildApiUrl(this.baseUrl, apiConfig.endpoints.openai.completions);

      const requestBody = {
        model: request.model || apiConfig.ai.defaultModel,
        messages: request.messages,
        temperature: request.temperature ?? apiConfig.ai.temperature,
        max_tokens: request.max_tokens || apiConfig.ai.maxTokens,
        top_p: request.top_p,
        frequency_penalty: request.frequency_penalty,
        presence_penalty: request.presence_penalty,
        stop: request.stop,
        stream: streaming || false
      };

      const result = await this.circuitBreaker.execute(async () => {
        return retryWithBackoff(async () => {
          const headers = await this.getHeaders();
          
          if (streaming) {
            return this.handleStreamingRequest(url, headers, requestBody, streamingOptions);
          }
          
          const response = await this.fetchWithTimeout(url, {
            method: 'POST',
            headers,
            body: JSON.stringify(requestBody)
          });

          if (!response.ok) {
            await this.handleApiError(response);
          }

          return await response.json();
        }, this.retryPolicy);
      });
      
      // Cache successful non-streaming results
      if (cacheKey && !streaming) {
        await cacheService.set(cacheKey, result, {
          ttl: apiConfig.cache?.completionTtl || 1800000, // 30 minutes
          tags: ['openai', 'completion']
        });
      }
      
      apiMonitoringService.recordSuccess('openai', 'createChatCompletion', Date.now() - startTime);
      return result;
      
    } catch (error) {
      const duration = Date.now() - startTime;
      
      if (error instanceof ApiError) {
        apiMonitoringService.recordError('openai', 'createChatCompletion', error, duration);
        throw error;
      }
      
      const apiError = new ApiError(
        `Failed to create chat completion: ${error instanceof Error ? error.message : 'Unknown error'}`,
        500,
        'CHAT_COMPLETION_FAILED',
        'openai'
      );
      
      apiMonitoringService.recordError('openai', 'createChatCompletion', apiError, duration);
      throw apiError;
    }
  }

  /**
   * Generate vocabulary description with streaming support
   */
  async generateVocabularyDescription(options: VocabularyGenerationOptions): Promise<GeneratedVocabulary> {
    const systemPrompt = this.buildVocabularySystemPrompt(options);
    const userPrompt = this.buildVocabularyUserPrompt(options);

    const messages: ChatMessage[] = [
      { role: 'system', content: systemPrompt },
      { role: 'user', content: userPrompt }
    ];

    try {
      const response = await this.createChatCompletion(
        {
          model: apiConfig.ai.defaultModel,
          messages,
          temperature: apiConfig.ai.temperature,
          max_tokens: options.maxLength || apiConfig.ai.maxDescriptionLength
        },
        options.streaming,
        options.streamingOptions
      );

      const content = response.choices[0]?.message?.content;
      if (!content) {
        throw new ApiError('Empty response from OpenAI', 500, 'EMPTY_RESPONSE', 'openai');
      }

      return this.parseVocabularyResponse(content, options.word);
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      
      throw new ApiError(
        `Failed to generate vocabulary description: ${error instanceof Error ? error.message : 'Unknown error'}`,
        500,
        'VOCABULARY_GENERATION_FAILED',
        'openai'
      );
    }
  }

  /**
   * Generate context-aware descriptions for images
   */
  async generateImageContext(
    imageDescription: string,
    word?: string,
    learningGoal?: string
  ): Promise<string> {
    const systemPrompt = `You are an AI assistant specialized in creating educational content for vocabulary learning. 
Your task is to analyze images and create contextual descriptions that help language learners understand and remember new words.`;

    const userPrompt = `Image description: "${imageDescription}"
${word ? `Target word: "${word}"` : ''}
${learningGoal ? `Learning goal: "${learningGoal}"` : ''}

Create a brief, educational context description (2-3 sentences) that:
1. Describes what's happening in the image
2. ${word ? `Highlights how the word "${word}" relates to the scene` : 'Identifies key vocabulary opportunities'}
3. Uses simple, clear language appropriate for language learners

Response:`;

    const messages: ChatMessage[] = [
      { role: 'system', content: systemPrompt },
      { role: 'user', content: userPrompt }
    ];

    try {
      const response = await this.createChatCompletion({
        model: apiConfig.ai.defaultModel,
        messages,
        temperature: 0.7,
        max_tokens: 200
      });

      return response.choices[0]?.message?.content?.trim() || '';
    } catch (error) {
      console.error('Failed to generate image context:', error);
      return imageDescription; // Fallback to original description
    }
  }

  /**
   * Generate example sentences for a vocabulary word
   */
  async generateExamples(
    word: string,
    definition: string,
    count: number = 3,
    difficulty: 'beginner' | 'intermediate' | 'advanced' = 'intermediate'
  ): Promise<string[]> {
    const difficultyLevels = {
      beginner: 'simple, everyday language with common words',
      intermediate: 'moderate complexity with varied vocabulary',
      advanced: 'sophisticated language with nuanced usage'
    };

    const systemPrompt = `You are creating example sentences for vocabulary learning. Create ${count} example sentences that demonstrate the word's usage clearly and effectively.`;

    const userPrompt = `Word: "${word}"
Definition: "${definition}"
Difficulty level: ${difficulty} (use ${difficultyLevels[difficulty]})

Create ${count} example sentences that:
1. Show the word in different contexts
2. Are grammatically correct and natural
3. Help learners understand the word's meaning and usage
4. Are appropriate for ${difficulty} level learners

Format your response as a numbered list:
1. [First example]
2. [Second example]
3. [Third example]`;

    const messages: ChatMessage[] = [
      { role: 'system', content: systemPrompt },
      { role: 'user', content: userPrompt }
    ];

    try {
      const response = await this.createChatCompletion({
        model: apiConfig.ai.defaultModel,
        messages,
        temperature: 0.8,
        max_tokens: 300
      });

      const content = response.choices[0]?.message?.content || '';
      return this.parseExamplesList(content);
    } catch (error) {
      console.error('Failed to generate examples:', error);
      return []; // Return empty array as fallback
    }
  }

  /**
   * Analyze image using GPT-4 Vision
   */
  async analyzeImageWithVision(visionRequest: VisionRequest): Promise<string> {
    const startTime = Date.now();
    
    try {
      // Generate cache key
      const cacheKey = this.generateCacheKey('vision', visionRequest);
      
      // Check cache first
      const cachedResult = await cacheService.get<string>(cacheKey);
      if (cachedResult) {
        apiMonitoringService.recordCacheHit('openai', 'analyzeImageWithVision');
        return cachedResult;
      }
      
      await rateLimiter.acquire('openai', 1000); // Vision requests cost more tokens

      const messages: ChatMessage[] = [
        {
          role: 'user',
          content: `${visionRequest.prompt || 'Describe this image in detail for vocabulary learning purposes.'}
          
          Image: ${visionRequest.imageUrl}`
        }
      ];

      const response = await this.createChatCompletion({
        model: 'gpt-4-vision-preview',
        messages,
        max_tokens: visionRequest.maxTokens || 500
      });

      const content = response.choices[0]?.message?.content;
      if (!content) {
        throw new ApiError('Empty response from GPT-4 Vision', 500, 'EMPTY_VISION_RESPONSE', 'openai');
      }
      
      // Cache the result
      await cacheService.set(cacheKey, content, {
        ttl: apiConfig.cache?.visionTtl || 3600000, // 1 hour
        tags: ['openai', 'vision']
      });
      
      apiMonitoringService.recordSuccess('openai', 'analyzeImageWithVision', Date.now() - startTime);
      return content;
      
    } catch (error) {
      const duration = Date.now() - startTime;
      
      if (error instanceof ApiError) {
        apiMonitoringService.recordError('openai', 'analyzeImageWithVision', error, duration);
        throw error;
      }
      
      const apiError = new ApiError(
        `Failed to analyze image: ${error instanceof Error ? error.message : 'Unknown error'}`,
        500,
        'VISION_ANALYSIS_FAILED',
        'openai'
      );
      
      apiMonitoringService.recordError('openai', 'analyzeImageWithVision', apiError, duration);
      throw apiError;
    }
  }

  /**
   * Check if the API key is valid
   */
  async validateApiKey(apiKey?: string): Promise<boolean> {
    try {
      const headers = apiKey 
        ? {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
          }
        : await this.getHeaders();
        
      const url = buildApiUrl(this.baseUrl, apiConfig.endpoints.openai.models);
      const response = await fetch(url, {
        method: 'GET',
        headers
      });

      return response.ok;
    } catch {
      return false;
    }
  }

  /**
   * Get service health status
   */
  async getHealthStatus(): Promise<{
    status: 'healthy' | 'degraded' | 'unhealthy';
    circuitBreakerState: string;
    rateLimit: { remaining: number; resetTime: number };
    lastError?: string;
  }> {
    const circuitState = this.circuitBreaker.getState();
    const rateLimitStatus = rateLimiter.getStatus('openai');
    
    return {
      status: circuitState === 'CLOSED' ? 'healthy' : 'degraded',
      circuitBreakerState: circuitState,
      rateLimit: {
        remaining: rateLimitStatus.remaining,
        resetTime: rateLimitStatus.resetTime
      },
      lastError: circuitState === 'OPEN' ? 'Circuit breaker is open' : undefined
    };
  }

  /**
   * Clear cache for specific tags or all OpenAI data
   */
  async clearCache(tags?: string[]): Promise<void> {
    const cacheTags = tags ? ['openai', ...tags] : ['openai'];
    await cacheService.invalidateByTags(cacheTags);
  }

  // Private helper methods

  private generateCacheKey(operation: string, params: any): string {
    const sortedParams = JSON.stringify(params, Object.keys(params).sort());
    return `openai:${operation}:${Buffer.from(sortedParams).toString('base64')}`;
  }

  private calculateTokenCost(request: ChatCompletionRequest): number {
    // Rough estimate: 1 token per 4 characters for English text
    const messageText = request.messages.map(m => m.content).join(' ');
    return Math.ceil(messageText.length / 4) + (request.max_tokens || 0);
  }

  private async handleStreamingRequest(
    url: string,
    headers: Record<string, string>,
    requestBody: any,
    streamingOptions?: StreamingOptions
  ): Promise<ChatCompletionResponse> {
    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify(requestBody)
    });

    if (!response.ok) {
      await this.handleApiError(response);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new ApiError('No response body reader available', 500, 'NO_READER', 'openai');
    }

    let fullResponse = '';
    const decoder = new TextDecoder();

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n').filter(line => line.trim());

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') continue;

            try {
              const parsed = JSON.parse(data);
              const token = parsed.choices?.[0]?.delta?.content;
              if (token) {
                fullResponse += token;
                streamingOptions?.onToken?.(token);
              }
            } catch (e) {
              // Ignore malformed JSON chunks
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }

    streamingOptions?.onComplete?.(fullResponse);

    // Return mock response structure for streaming
    return {
      id: 'streaming-' + Date.now(),
      object: 'chat.completion',
      created: Math.floor(Date.now() / 1000),
      model: requestBody.model,
      choices: [{
        index: 0,
        message: { role: 'assistant', content: fullResponse },
        finish_reason: 'stop'
      }],
      usage: {
        prompt_tokens: 0,
        completion_tokens: 0,
        total_tokens: 0
      }
    };
  }

  private validateChatRequest(request: ChatCompletionRequest): void {
    if (!request.messages || request.messages.length === 0) {
      throw new ApiError('Messages array is required', 400, 'INVALID_REQUEST', 'openai');
    }

    if (request.model && !apiConfig.ai.supportedModels.includes(request.model as any)) {
      console.warn(`Model ${request.model} is not in the supported models list`);
    }

    for (const message of request.messages) {
      if (!message.role || !message.content) {
        throw new ApiError('Each message must have role and content', 400, 'INVALID_MESSAGE', 'openai');
      }
    }
  }

  private async handleApiError(response: Response): Promise<never> {
    let errorMessage = `OpenAI API error: ${response.statusText}`;
    let code = 'OPENAI_API_ERROR';

    try {
      const errorData = await response.json();
      if (errorData.error) {
        errorMessage = errorData.error.message || errorMessage;
        code = errorData.error.code || code;
      }
    } catch {
      // If we can't parse the error response, use the default message
    }

    switch (response.status) {
      case 401:
        throw new ApiError('Invalid API key', 401, 'INVALID_API_KEY', 'openai');
      case 429:
        throw new ApiError('Rate limit exceeded', 429, 'RATE_LIMIT_EXCEEDED', 'openai');
      case 500:
      case 502:
      case 503:
        throw new ApiError('OpenAI service temporarily unavailable', response.status, 'SERVICE_UNAVAILABLE', 'openai');
      default:
        throw new ApiError(errorMessage, response.status, code, 'openai');
    }
  }

  private async enforceRateLimit(): Promise<void> {
    // Legacy method - now handled by rateLimiter.acquire()
    // Keep for backward compatibility
    await rateLimiter.acquire('openai', 1);
  }

  private async fetchWithTimeout(url: string, options: RequestInit): Promise<Response> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeouts.ai);

    const request = fetch(url, {
      ...options,
      signal: controller.signal
    });

    this.requestQueue.push(request);

    try {
      const response = await request;
      clearTimeout(timeoutId);
      return response;
    } catch (error) {
      clearTimeout(timeoutId);
      if (error instanceof Error && error.name === 'AbortError') {
        throw new ApiError('Request timeout', 408, 'TIMEOUT', 'openai');
      }
      throw error;
    }
  }

  private buildVocabularySystemPrompt(options: VocabularyGenerationOptions): string {
    const styleInstructions = {
      simple: 'Use simple, clear language that a beginner can understand.',
      detailed: 'Provide comprehensive explanations with nuanced details.',
      academic: 'Use formal, scholarly language appropriate for academic contexts.',
      conversational: 'Use friendly, informal language as if explaining to a friend.'
    };

    return `You are an expert language teacher and lexicographer. Your task is to create comprehensive vocabulary entries that help language learners understand and remember new words effectively.

Style: ${styleInstructions[options.style || 'simple']}
Difficulty: ${options.difficulty || 'intermediate'}
${options.includeExamples ? 'Include 2-3 example sentences.' : 'Focus on clear definitions.'}

Return your response in this exact JSON format:
{
  "word": "the word being defined",
  "definition": "clear, concise definition",
  "translation": "translation if applicable",
  "examples": ["example sentence 1", "example sentence 2", "example sentence 3"],
  "context": "contextual explanation relating to any provided image or scenario",
  "difficulty": number from 1-10,
  "tags": ["relevant", "tags", "for", "categorization"],
  "pronunciation": "phonetic pronunciation if helpful"
}`;
  }

  private buildVocabularyUserPrompt(options: VocabularyGenerationOptions): string {
    let prompt = `Word: "${options.word}"`;
    
    if (options.context) {
      prompt += `\nContext: ${options.context}`;
    }
    
    if (options.imageDescription) {
      prompt += `\nImage description: ${options.imageDescription}`;
    }

    prompt += `\n\nCreate a comprehensive vocabulary entry for this word, considering the provided context and image description.`;

    return prompt;
  }

  private parseVocabularyResponse(content: string, word: string): GeneratedVocabulary {
    try {
      // Try to parse as JSON first
      const parsed = JSON.parse(content);
      
      return {
        word: parsed.word || word,
        definition: parsed.definition || '',
        translation: parsed.translation,
        examples: Array.isArray(parsed.examples) ? parsed.examples : [],
        context: parsed.context || '',
        difficulty: typeof parsed.difficulty === 'number' ? parsed.difficulty : 5,
        tags: Array.isArray(parsed.tags) ? parsed.tags : [],
        pronunciation: parsed.pronunciation
      };
    } catch {
      // If JSON parsing fails, extract information manually
      return this.parseVocabularyTextResponse(content, word);
    }
  }

  private parseVocabularyTextResponse(content: string, word: string): GeneratedVocabulary {
    // Basic text parsing as fallback
    const lines = content.split('\n').filter(line => line.trim());
    
    return {
      word,
      definition: lines[0] || 'Definition not available',
      examples: lines.filter(line => 
        line.includes('example') || 
        line.match(/^\d+\./) || 
        line.includes(word)
      ).slice(0, 3),
      context: content.substring(0, 200),
      difficulty: 5,
      tags: [word.toLowerCase()],
    };
  }

  private parseExamplesList(content: string): string[] {
    const lines = content.split('\n').filter(line => line.trim());
    const examples: string[] = [];

    for (const line of lines) {
      const trimmed = line.trim();
      // Look for numbered list items
      const match = trimmed.match(/^\d+\.\s*(.+)$/);
      if (match) {
        examples.push(match[1]);
      } else if (trimmed && !trimmed.includes(':') && trimmed.length > 10) {
        // Add non-numbered lines that look like sentences
        examples.push(trimmed);
      }
    }

    return examples.slice(0, 5); // Limit to 5 examples max
  }
}

// Export singleton instance
export const openaiService = new OpenAIService();
export default OpenAIService;