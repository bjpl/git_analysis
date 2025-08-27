/**
 * Translation Service for VocabLens
 * Supports Google Translate API and DeepL API for enhanced vocabulary translations
 */

import { apiConfig, getApiHeaders, buildApiUrl, ApiError, calculateRetryDelay } from '../config/api';
import { TranslationAPI } from '../types/api';
import { rateLimiter } from './rateLimiter';
import { apiErrorHandler } from './apiErrorHandler';

export interface TranslationOptions {
  text: string | string[];
  targetLanguage: string;
  sourceLanguage?: string;
  service?: 'google' | 'deepl' | 'auto';
  formality?: 'default' | 'more' | 'less';
  context?: 'vocabulary' | 'definition' | 'example' | 'general';
}

export interface TranslationResult {
  originalText: string;
  translatedText: string;
  detectedLanguage?: string;
  service: 'google' | 'deepl' | 'fallback';
  confidence?: number;
  alternatives?: string[];
}

export interface LanguageDetectionResult {
  language: string;
  confidence: number;
  isReliable: boolean;
}

export interface SupportedLanguage {
  code: string;
  name: string;
  nativeName: string;
  supportsFormality?: boolean;
}

class TranslationService {
  private readonly googleEnabled = apiConfig.translation.googleTranslate.enabled;
  private readonly deeplEnabled = apiConfig.translation.deepl.enabled;
  private requestQueue: Promise<any>[] = [];

  /**
   * Translate text using the configured translation service
   */
  async translate(options: TranslationOptions): Promise<TranslationResult[]> {
    const {
      text,
      targetLanguage,
      sourceLanguage = 'auto',
      service = 'auto',
      formality = 'default',
      context = 'general'
    } = options;

    // Validate input
    this.validateTranslationRequest(options);

    const texts = Array.isArray(text) ? text : [text];
    const results: TranslationResult[] = [];

    // Determine which service to use
    const selectedService = this.selectTranslationService(service);

    try {
      await this.enforceRateLimit();

      switch (selectedService) {
        case 'deepl':
          const deeplResults = await this.translateWithDeepL({
            text: texts,
            target_lang: this.normalizeLanguageCode(targetLanguage, 'deepl'),
            source_lang: sourceLanguage !== 'auto' ? this.normalizeLanguageCode(sourceLanguage, 'deepl') : undefined,
            formality: this.mapFormalityLevel(formality),
            tag_handling: context === 'vocabulary' ? 'xml' : undefined
          });
          
          results.push(...deeplResults.map((result, index) => ({
            originalText: texts[index],
            translatedText: result.text,
            detectedLanguage: result.detected_source_language,
            service: 'deepl' as const,
            confidence: 0.9 // DeepL generally high quality
          })));
          break;

        case 'google':
          const googleResults = await this.translateWithGoogle({
            q: texts,
            target: this.normalizeLanguageCode(targetLanguage, 'google'),
            source: sourceLanguage !== 'auto' ? this.normalizeLanguageCode(sourceLanguage, 'google') : undefined,
            format: 'text'
          });

          results.push(...googleResults.data.translations.map((result, index) => ({
            originalText: texts[index],
            translatedText: result.translatedText,
            detectedLanguage: result.detectedSourceLanguage,
            service: 'google' as const,
            confidence: 0.85
          })));
          break;

        default:
          // Fallback to basic translation or return original
          results.push(...texts.map(t => ({
            originalText: t,
            translatedText: t, // No translation available
            service: 'fallback' as const,
            confidence: 0
          })));
      }

      return results;
    } catch (error) {
      const transformedError = apiErrorHandler.handleError(error, {
        service: 'translate',
        operation: 'translate',
        endpoint: selectedService,
        metadata: { targetLanguage, sourceLanguage, textCount: texts.length }
      });

      // Try fallback service if primary fails
      if (selectedService !== 'fallback') {
        console.warn(`Translation service ${selectedService} failed, trying fallback`);
        const fallbackService = selectedService === 'google' ? 'deepl' : 'google';
        
        try {
          return await this.translate({
            ...options,
            service: fallbackService
          });
        } catch (fallbackError) {
          // Both services failed, return original text
          return texts.map(t => ({
            originalText: t,
            translatedText: t,
            service: 'fallback' as const,
            confidence: 0
          }));
        }
      }

      throw transformedError;
    }
  }

  /**
   * Translate with Google Translate API
   */
  private async translateWithGoogle(request: TranslationAPI.GoogleTranslateRequest): Promise<TranslationAPI.GoogleTranslateResponse> {
    if (!this.googleEnabled || !apiConfig.translation.googleTranslate.apiKey) {
      throw new ApiError('Google Translate is not configured', 503, 'SERVICE_UNAVAILABLE', 'translate');
    }

    const url = buildApiUrl(
      import.meta.env.VITE_GOOGLE_TRANSLATE_API_URL || 'https://translation.googleapis.com/language/translate/v2',
      ''
    );

    const response = await this.fetchWithTimeout(url, {
      method: 'POST',
      headers: getApiHeaders('translate'),
      body: JSON.stringify(request)
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: { message: response.statusText } }));
      throw new ApiError(
        `Google Translate API error: ${error.error?.message || response.statusText}`,
        response.status,
        'GOOGLE_TRANSLATE_ERROR',
        'translate'
      );
    }

    return await response.json();
  }

  /**
   * Translate with DeepL API
   */
  private async translateWithDeepL(request: TranslationAPI.DeepLTranslateRequest): Promise<TranslationAPI.DeepLTranslateResponse> {
    if (!this.deeplEnabled || !apiConfig.translation.deepl.apiKey) {
      throw new ApiError('DeepL is not configured', 503, 'SERVICE_UNAVAILABLE', 'translate');
    }

    const url = buildApiUrl('https://api-free.deepl.com/v2', '/translate');

    // Convert array to multiple text parameters
    const body = new URLSearchParams();
    if (Array.isArray(request.text)) {
      request.text.forEach(text => body.append('text', text));
    } else {
      body.append('text', request.text);
    }
    
    body.append('target_lang', request.target_lang);
    if (request.source_lang) body.append('source_lang', request.source_lang);
    if (request.formality) body.append('formality', request.formality);
    if (request.tag_handling) body.append('tag_handling', request.tag_handling);

    const response = await this.fetchWithTimeout(url, {
      method: 'POST',
      headers: {
        ...getApiHeaders('translate'),
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: body.toString()
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: response.statusText }));
      throw new ApiError(
        `DeepL API error: ${error.message || response.statusText}`,
        response.status,
        'DEEPL_ERROR',
        'translate'
      );
    }

    return await response.json();
  }

  /**
   * Detect language of given text
   */
  async detectLanguage(text: string): Promise<LanguageDetectionResult> {
    if (!this.googleEnabled) {
      return {
        language: 'en',
        confidence: 0,
        isReliable: false
      };
    }

    try {
      await this.enforceRateLimit();

      const url = buildApiUrl(
        import.meta.env.VITE_GOOGLE_TRANSLATE_API_URL || 'https://translation.googleapis.com/language/translate/v2',
        '/detect'
      );

      const response = await this.fetchWithTimeout(url, {
        method: 'POST',
        headers: getApiHeaders('translate'),
        body: JSON.stringify({ q: text })
      });

      if (!response.ok) {
        throw new ApiError('Language detection failed', response.status, 'DETECTION_FAILED', 'translate');
      }

      const result: TranslationAPI.LanguageDetectionResponse = await response.json();
      const detection = result.data.detections[0]?.[0];

      if (!detection) {
        return {
          language: 'en',
          confidence: 0,
          isReliable: false
        };
      }

      return {
        language: detection.language,
        confidence: detection.confidence,
        isReliable: detection.isReliable
      };
    } catch (error) {
      console.error('Language detection failed:', error);
      return {
        language: 'en',
        confidence: 0,
        isReliable: false
      };
    }
  }

  /**
   * Get list of supported languages for translation
   */
  async getSupportedLanguages(service: 'google' | 'deepl' = 'google'): Promise<SupportedLanguage[]> {
    // For now, return a static list of common languages
    // This could be enhanced to fetch from APIs dynamically
    const commonLanguages: SupportedLanguage[] = [
      { code: 'en', name: 'English', nativeName: 'English' },
      { code: 'es', name: 'Spanish', nativeName: 'Español', supportsFormality: true },
      { code: 'fr', name: 'French', nativeName: 'Français', supportsFormality: true },
      { code: 'de', name: 'German', nativeName: 'Deutsch', supportsFormality: true },
      { code: 'it', name: 'Italian', nativeName: 'Italiano', supportsFormality: true },
      { code: 'pt', name: 'Portuguese', nativeName: 'Português', supportsFormality: true },
      { code: 'ru', name: 'Russian', nativeName: 'Русский' },
      { code: 'ja', name: 'Japanese', nativeName: '日本語' },
      { code: 'ko', name: 'Korean', nativeName: '한국어' },
      { code: 'zh', name: 'Chinese', nativeName: '中文' },
      { code: 'ar', name: 'Arabic', nativeName: 'العربية' },
      { code: 'hi', name: 'Hindi', nativeName: 'हिन्दी' }
    ];

    return commonLanguages;
  }

  /**
   * Check if translation services are available
   */
  getServiceStatus(): {
    google: { available: boolean; reason?: string };
    deepl: { available: boolean; reason?: string };
  } {
    return {
      google: {
        available: this.googleEnabled && !!apiConfig.translation.googleTranslate.apiKey,
        reason: !this.googleEnabled ? 'Service disabled' : !apiConfig.translation.googleTranslate.apiKey ? 'API key missing' : undefined
      },
      deepl: {
        available: this.deeplEnabled && !!apiConfig.translation.deepl.apiKey,
        reason: !this.deeplEnabled ? 'Service disabled' : !apiConfig.translation.deepl.apiKey ? 'API key missing' : undefined
      }
    };
  }

  /**
   * Translate vocabulary-specific content with context
   */
  async translateVocabulary(options: {
    word: string;
    definition?: string;
    examples?: string[];
    targetLanguage: string;
    sourceLanguage?: string;
  }): Promise<{
    word: TranslationResult;
    definition?: TranslationResult;
    examples?: TranslationResult[];
  }> {
    const { word, definition, examples, targetLanguage, sourceLanguage } = options;

    const results: any = {};

    // Translate the word
    const wordResults = await this.translate({
      text: word,
      targetLanguage,
      sourceLanguage,
      context: 'vocabulary'
    });
    results.word = wordResults[0];

    // Translate definition if provided
    if (definition) {
      const definitionResults = await this.translate({
        text: definition,
        targetLanguage,
        sourceLanguage,
        context: 'definition'
      });
      results.definition = definitionResults[0];
    }

    // Translate examples if provided
    if (examples && examples.length > 0) {
      const exampleResults = await this.translate({
        text: examples,
        targetLanguage,
        sourceLanguage,
        context: 'example'
      });
      results.examples = exampleResults;
    }

    return results;
  }

  // Private helper methods

  private validateTranslationRequest(options: TranslationOptions): void {
    if (!options.text || (Array.isArray(options.text) && options.text.length === 0)) {
      throw new ApiError('Text is required for translation', 400, 'INVALID_REQUEST', 'translate');
    }

    if (!options.targetLanguage) {
      throw new ApiError('Target language is required', 400, 'INVALID_REQUEST', 'translate');
    }

    // Validate language codes
    const validLanguageCodes = /^[a-z]{2}(-[A-Z]{2})?$/;
    if (!validLanguageCodes.test(options.targetLanguage)) {
      throw new ApiError('Invalid target language code', 400, 'INVALID_LANGUAGE_CODE', 'translate');
    }

    if (options.sourceLanguage && options.sourceLanguage !== 'auto' && !validLanguageCodes.test(options.sourceLanguage)) {
      throw new ApiError('Invalid source language code', 400, 'INVALID_LANGUAGE_CODE', 'translate');
    }
  }

  private selectTranslationService(preferred: 'google' | 'deepl' | 'auto'): 'google' | 'deepl' | 'fallback' {
    if (preferred === 'auto') {
      // Prefer DeepL for better quality, fallback to Google
      if (this.deeplEnabled && apiConfig.translation.deepl.apiKey) return 'deepl';
      if (this.googleEnabled && apiConfig.translation.googleTranslate.apiKey) return 'google';
      return 'fallback';
    }

    if (preferred === 'deepl' && this.deeplEnabled && apiConfig.translation.deepl.apiKey) {
      return 'deepl';
    }

    if (preferred === 'google' && this.googleEnabled && apiConfig.translation.googleTranslate.apiKey) {
      return 'google';
    }

    return 'fallback';
  }

  private normalizeLanguageCode(code: string, service: 'google' | 'deepl'): string {
    // Map common language codes between services
    const mappings: Record<string, Record<string, string>> = {
      deepl: {
        'en': 'EN',
        'es': 'ES',
        'fr': 'FR',
        'de': 'DE',
        'it': 'IT',
        'pt': 'PT',
        'ru': 'RU',
        'ja': 'JA',
        'ko': 'KO',
        'zh': 'ZH'
      },
      google: {
        'en': 'en',
        'es': 'es',
        'fr': 'fr',
        'de': 'de',
        'it': 'it',
        'pt': 'pt',
        'ru': 'ru',
        'ja': 'ja',
        'ko': 'ko',
        'zh': 'zh'
      }
    };

    return mappings[service]?.[code.toLowerCase()] || code;
  }

  private mapFormalityLevel(formality: string): 'default' | 'more' | 'less' | undefined {
    const mapping: Record<string, 'default' | 'more' | 'less'> = {
      'default': 'default',
      'formal': 'more',
      'informal': 'less',
      'more': 'more',
      'less': 'less'
    };

    return mapping[formality];
  }

  private async enforceRateLimit(): Promise<void> {
    const result = await rateLimiter.checkRateLimit('translate');
    if (!result.allowed) {
      const delay = result.retryAfter ? result.retryAfter * 1000 : 1000;
      await this.delay(delay);
    }
  }

  private async fetchWithTimeout(url: string, options: RequestInit): Promise<Response> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), apiConfig.timeouts.default);

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
        throw new ApiError('Translation request timeout', 408, 'TIMEOUT', 'translate');
      }
      throw error;
    }
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Export singleton instance
export const translationService = new TranslationService();

// Configure rate limiting for translation services
rateLimiter.configure('translate', {
  windowMs: 60 * 1000, // 1 minute
  maxRequests: 30, // Conservative limit
  minDelay: 1000, // 1 second between requests
  burstSize: 5
});

export default TranslationService;