import { useState, useCallback, useRef, useEffect } from 'react';
import { DescriptionStyle, UseAIGenerationReturn, VocabularyWord } from '../types';
import toast from 'react-hot-toast';
import { useLocalStorage } from './useLocalStorage';
import { useOffline } from './useOffline';

interface GenerateDescriptionRequest {
  imageId: string;
  imageUrl: string;
  style: DescriptionStyle;
  language?: string;
  includeVocabulary?: boolean;
  context?: string;
  focusAreas?: string[];
  vocabularyLevel?: 1 | 2 | 3 | 4 | 5;
}

interface GenerateDescriptionResponse {
  description: string;
  vocabulary?: VocabularyWord[];
  tokenCount?: number;
  processingTime?: number;
}

interface StreamChunk {
  type: 'content' | 'vocabulary' | 'metadata' | 'error' | 'done';
  content?: string;
  vocabulary?: VocabularyWord;
  metadata?: {
    tokenCount: number;
    processingTime: number;
  };
  error?: string;
}

interface CachedDescription {
  imageId: string;
  style: DescriptionStyle;
  description: string;
  vocabulary: VocabularyWord[];
  timestamp: number;
  context?: string;
  focusAreas?: string[];
}

class AIGenerationAPI {
  private baseURL = process.env.REACT_APP_SUPABASE_URL || '/api';
  private apiKey = process.env.REACT_APP_SUPABASE_ANON_KEY;

  async generateDescription(request: GenerateDescriptionRequest, signal?: AbortSignal): Promise<ReadableStream<Uint8Array>> {
    // Try Supabase Edge Function first
    try {
      const response = await fetch(`${this.baseURL}/functions/v1/ai-description`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream',
          'Authorization': `Bearer ${this.apiKey}`,
        },
        body: JSON.stringify(request),
        signal,
      });

      if (!response.ok) {
        throw new Error(`Supabase function failed: ${response.statusText}`);
      }

      if (!response.body) {
        throw new Error('No response stream available');
      }

      return response.body;
    } catch (error) {
      // Fallback to direct API if Supabase fails
      console.warn('Supabase function failed, falling back to direct API:', error);
      
      const response = await fetch(`${this.baseURL}/generate-description`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream',
        },
        body: JSON.stringify(request),
        signal,
      });

      if (!response.ok) {
        throw new Error(`Generation failed: ${response.statusText}`);
      }

      if (!response.body) {
        throw new Error('No response stream available');
      }

      return response.body;
    }
  }

  // Cache management
  getCacheKey(imageId: string, style: DescriptionStyle, context?: string, focusAreas?: string[]): string {
    const contextHash = context ? btoa(context).slice(0, 10) : '';
    const focusHash = focusAreas?.length ? btoa(focusAreas.join(',')).slice(0, 10) : '';
    return `desc_${imageId}_${style}_${contextHash}_${focusHash}`;
  }

  getCachedDescription(cacheKey: string): CachedDescription | null {
    try {
      const cached = localStorage.getItem(cacheKey);
      if (!cached) return null;
      
      const parsed: CachedDescription = JSON.parse(cached);
      
      // Check if cache is still valid (24 hours)
      const isExpired = Date.now() - parsed.timestamp > 24 * 60 * 60 * 1000;
      if (isExpired) {
        localStorage.removeItem(cacheKey);
        return null;
      }
      
      return parsed;
    } catch {
      return null;
    }
  }

  setCachedDescription(cacheKey: string, data: CachedDescription): void {
    try {
      localStorage.setItem(cacheKey, JSON.stringify(data));
    } catch (error) {
      console.warn('Failed to cache description:', error);
    }
  }
}

const aiAPI = new AIGenerationAPI();

export const useAIGeneration = (): UseAIGenerationReturn & {
  vocabulary: VocabularyWord[];
  tokenCount: number;
  processingTime: number;
  progress: number;
  retryCount: number;
  clearCache: () => void;
  getCachedDescriptions: () => CachedDescription[];
} => {
  const [description, setDescription] = useState('');
  const [vocabulary, setVocabulary] = useState<VocabularyWord[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<{ code: string; message: string; timestamp: string; recoverable: boolean; details?: unknown } | null>(null);
  const [tokenCount, setTokenCount] = useState(0);
  const [processingTime, setProcessingTime] = useState(0);
  const [progress, setProgress] = useState(0);
  const [retryCount, setRetryCount] = useState(0);
  
  const readerRef = useRef<ReadableStreamDefaultReader<Uint8Array> | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const startTimeRef = useRef<number>(0);
  
  const { isOnline } = useOffline();
  const [cachedDescriptions, setCachedDescriptions] = useLocalStorage<CachedDescription[]>('ai-descriptions', []);

  const generate = useCallback(async (
    imageId: string, 
    style: DescriptionStyle,
    options: {
      context?: string;
      focusAreas?: string[];
      vocabularyLevel?: 1 | 2 | 3 | 4 | 5;
      forceRefresh?: boolean;
    } = {}
  ) => {
    const { context, focusAreas, vocabularyLevel = 3, forceRefresh = false } = options;
    
    // Cancel any ongoing generation
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Check cache first (unless force refresh)
    if (!forceRefresh) {
      const cacheKey = aiAPI.getCacheKey(imageId, style, context, focusAreas);
      const cached = aiAPI.getCachedDescription(cacheKey);
      
      if (cached) {
        setDescription(cached.description);
        setVocabulary(cached.vocabulary);
        setTokenCount(cached.description.split(' ').length);
        setProcessingTime(0);
        setProgress(100);
        toast.success('Loaded cached description');
        return;
      }
    }

    // Reset state
    setDescription('');
    setVocabulary([]);
    setError(null);
    setIsGenerating(true);
    setProgress(0);
    setTokenCount(0);
    setProcessingTime(0);
    startTimeRef.current = Date.now();

    // Create new abort controller
    abortControllerRef.current = new AbortController();

    try {
      // Check if we're offline
      if (!isOnline) {
        throw new Error('No internet connection. Please check your network and try again.');
      }

      const imageUrl = `https://source.unsplash.com/${imageId}`;
      
      const stream = await aiAPI.generateDescription({
        imageId,
        imageUrl,
        style,
        language: 'en',
        includeVocabulary: true,
        context,
        focusAreas,
        vocabularyLevel,
      }, abortControllerRef.current.signal);

      const reader = stream.getReader();
      readerRef.current = reader;
      
      const decoder = new TextDecoder();
      let buffer = '';
      let accumulatedContent = '';
      let accumulatedVocabulary: VocabularyWord[] = [];

      try {
        while (true) {
          const { done, value } = await reader.read();
          
          if (done) break;
          
          // Check if generation was cancelled
          if (abortControllerRef.current?.signal.aborted) {
            break;
          }

          const chunk = decoder.decode(value, { stream: true });
          buffer += chunk;

          // Process Server-Sent Events
          const lines = buffer.split('\n');
          buffer = lines.pop() || ''; // Keep incomplete line in buffer

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6);
              
              if (data === '[DONE]') {
                setIsGenerating(false);
                setProgress(100);
                setProcessingTime(Date.now() - startTimeRef.current);
                
                // Cache the completed description
                const cacheKey = aiAPI.getCacheKey(imageId, style, context, focusAreas);
                aiAPI.setCachedDescription(cacheKey, {
                  imageId,
                  style,
                  description: accumulatedContent,
                  vocabulary: accumulatedVocabulary,
                  timestamp: Date.now(),
                  context,
                  focusAreas,
                });
                
                return;
              }

              try {
                const parsed: StreamChunk = JSON.parse(data);
                
                switch (parsed.type) {
                  case 'content':
                    if (parsed.content) {
                      accumulatedContent += parsed.content;
                      setDescription(accumulatedContent);
                      setTokenCount(accumulatedContent.split(' ').length);
                      // Update progress based on estimated completion
                      const estimatedProgress = Math.min(90, (accumulatedContent.length / 1000) * 100);
                      setProgress(estimatedProgress);
                    }
                    break;
                    
                  case 'vocabulary':
                    if (parsed.vocabulary) {
                      accumulatedVocabulary.push(parsed.vocabulary);
                      setVocabulary([...accumulatedVocabulary]);
                    }
                    break;
                    
                  case 'metadata':
                    if (parsed.metadata) {
                      setTokenCount(parsed.metadata.tokenCount);
                      setProcessingTime(parsed.metadata.processingTime);
                    }
                    break;
                    
                  case 'error':
                    if (parsed.error) {
                      throw new Error(parsed.error);
                    }
                    break;
                }
              } catch (parseError) {
                // Handle non-JSON chunks (plain text streaming)
                if (data.trim() && !data.includes('error')) {
                  accumulatedContent += data;
                  setDescription(accumulatedContent);
                  setTokenCount(accumulatedContent.split(' ').length);
                }
              }
            }
          }
        }
      } finally {
        reader.releaseLock();
        readerRef.current = null;
      }

    } catch (err: any) {
      if (err.name === 'AbortError' || abortControllerRef.current?.signal.aborted) {
        // Generation was cancelled
        setDescription(prev => prev + '\n\n[Generation cancelled]');
        setProgress(0);
      } else {
        console.error('Generation error:', err);
        
        const errorMessage = err.message || 'Failed to generate description';
        setError({
          code: 'GENERATION_ERROR',
          message: errorMessage,
          timestamp: new Date().toISOString(),
          recoverable: true,
          details: err,
        });

        toast.error(errorMessage);

        // Retry logic for recoverable errors
        if (retryCount < 3 && errorMessage.includes('network')) {
          setTimeout(() => {
            setRetryCount(prev => prev + 1);
            generate(imageId, style, options);
          }, Math.pow(2, retryCount) * 1000); // Exponential backoff
          return;
        }

        // Fallback to mock generation for demo
        if (process.env.NODE_ENV === 'development') {
          setError(null);
          await generateMockDescription(style, context, focusAreas);
        }
      }
    } finally {
      setIsGenerating(false);
      abortControllerRef.current = null;
    }
  }, [isOnline, retryCount]);

  // Mock generation for development/demo
  const generateMockDescription = async (style: DescriptionStyle, context?: string, focusAreas?: string[]) => {
    const mockDescriptions = {
      academic: 'This photograph demonstrates sophisticated compositional techniques through its strategic use of lighting and spatial relationships. The interplay between foreground and background elements creates a visual hierarchy that guides the viewer\'s attention systematically through the frame. The photographer\'s choice of depth of field effectively isolates the primary subject while maintaining contextual awareness of the surrounding environment.',
      
      poetic: 'Golden threads of sunlight weave through the scene like whispered secrets, casting dancing shadows that tell stories of moments suspended in time. Each element in this visual symphony harmonizes with gentle grace, creating a melody of light and form that speaks to the soul\'s deepest yearning for beauty and connection.',
      
      technical: 'Captured with a shallow depth of field approximately f/2.8, this image exhibits excellent bokeh characteristics in the background elements. The exposure appears balanced for the midtones, with highlight retention maintaining detail in the brightest areas. The composition follows the rule of thirds, with the primary subject positioned along the intersecting lines for optimal visual impact.',
      
      casual: 'This is such a gorgeous shot! The lighting is absolutely perfect - you can see how it creates this amazing mood throughout the whole image. The photographer really knew what they were doing when they chose this angle and timing. It\'s the kind of photo that makes you stop scrolling and just appreciate the moment.',
      
      creative: 'In this captured moment, reality transforms into a canvas of infinite possibilities. The image breathes with life, each pixel a doorway to imagination. Here, light becomes storyteller and shadow becomes poet, crafting a narrative that transcends the boundaries between the seen and the felt, the known and the wondered.',
    };

    let mockText = mockDescriptions[style];
    
    // Modify description based on context and focus areas
    if (context) {
      mockText += ` ${context} This additional context enriches our understanding of the visual narrative presented.`;
    }
    
    if (focusAreas?.length) {
      const focusText = focusAreas.map(area => {
        switch (area) {
          case 'lighting': return 'The strategic use of light creates compelling visual depth.';
          case 'composition': return 'The compositional elements work in harmonious balance.';
          case 'colors': return 'The color palette evokes specific emotional responses.';
          case 'emotions': return 'The emotional resonance is palpable throughout the frame.';
          default: return `The ${area} contributes significantly to the overall impact.`;
        }
      }).join(' ');
      mockText += ` ${focusText}`;
    }

    const words = mockText.split(' ');
    const mockVocabularyWords: VocabularyWord[] = [
      {
        id: '1',
        word: 'compositional',
        definition: 'Relating to the arrangement of elements in a work of art',
        language: 'en',
        difficulty_level: 4,
        context: 'Used in photography and art analysis',
        learned: false,
        review_count: 0,
        created_at: new Date().toISOString(),
      },
      {
        id: '2',
        word: 'interplay',
        definition: 'The way in which two or more things have an effect on each other',
        language: 'en',
        difficulty_level: 3,
        context: 'Describing relationships between visual elements',
        learned: false,
        review_count: 0,
        created_at: new Date().toISOString(),
      },
    ];
    
    // Simulate streaming by adding words progressively
    let accumulatedContent = '';
    for (let i = 0; i < words.length; i++) {
      if (abortControllerRef.current?.signal.aborted) break;
      
      const newWord = i === 0 ? words[i] : ' ' + words[i];
      accumulatedContent += newWord;
      
      setDescription(accumulatedContent);
      setTokenCount(accumulatedContent.split(' ').length);
      setProgress(Math.min(90, (i / words.length) * 100));
      
      // Add vocabulary words at random intervals
      if (i % 20 === 0 && mockVocabularyWords.length > 0) {
        const vocabWord = mockVocabularyWords.shift();
        if (vocabWord) {
          setVocabulary(prev => [...prev, vocabWord]);
        }
      }
      
      // Random delay between 30-120ms to simulate realistic streaming
      await new Promise(resolve => setTimeout(resolve, Math.random() * 90 + 30));
    }
    
    // Add remaining vocabulary
    if (mockVocabularyWords.length > 0) {
      setVocabulary(prev => [...prev, ...mockVocabularyWords]);
    }
    
    setProgress(100);
    setProcessingTime(Date.now() - startTimeRef.current);
  };

  const cancel = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    
    if (readerRef.current) {
      readerRef.current.cancel();
      readerRef.current = null;
    }
    
    setIsGenerating(false);
    setProgress(0);
    toast.info('Generation cancelled');
  }, []);

  const clearCache = useCallback(() => {
    // Clear AI description cache
    const keys = Object.keys(localStorage).filter(key => key.startsWith('desc_'));
    keys.forEach(key => localStorage.removeItem(key));
    setCachedDescriptions([]);
    toast.success('Description cache cleared');
  }, [setCachedDescriptions]);

  const getCachedDescriptions = useCallback((): CachedDescription[] => {
    const keys = Object.keys(localStorage).filter(key => key.startsWith('desc_'));
    const cached: CachedDescription[] = [];
    
    keys.forEach(key => {
      try {
        const data = JSON.parse(localStorage.getItem(key) || '');
        if (data && data.timestamp) {
          cached.push(data);
        }
      } catch {
        // Invalid cache entry, remove it
        localStorage.removeItem(key);
      }
    });
    
    return cached.sort((a, b) => b.timestamp - a.timestamp);
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      
      if (readerRef.current) {
        readerRef.current.cancel();
      }
    };
  }, []);

  // Reset retry count on successful generation
  useEffect(() => {
    if (!isGenerating && !error && description) {
      setRetryCount(0);
    }
  }, [isGenerating, error, description]);

  return {
    description,
    vocabulary,
    isGenerating,
    error,
    tokenCount,
    processingTime,
    progress,
    retryCount,
    generate,
    cancel,
    clearCache,
    getCachedDescriptions,
  };
};