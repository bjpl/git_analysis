import React, { memo, useMemo, useCallback } from 'react';
import { debounce } from 'lodash-es';

// Memoized text processing component
export const MemoizedStreamingText = memo<{
  content: string;
  isStreaming: boolean;
  onComplete?: () => void;
  className?: string;
}>(({ content, isStreaming, onComplete, className }) => {
  // Memoize text processing to avoid unnecessary re-renders
  const processedContent = useMemo(() => {
    if (!content) return [];
    
    // Split into paragraphs and process
    return content.split('\n').filter(p => p.trim()).map((paragraph, index) => ({
      id: index,
      text: paragraph.trim(),
      words: paragraph.trim().split(' ').length,
    }));
  }, [content]);

  // Memoize cursor animation to avoid excessive DOM updates
  const cursorElement = useMemo(() => {
    if (!isStreaming) return null;
    
    return (
      <span 
        className="inline-block w-0.5 h-5 bg-indigo-600 dark:bg-indigo-400 ml-1 animate-pulse"
        aria-hidden="true"
      />
    );
  }, [isStreaming]);

  return (
    <div className={`prose prose-gray dark:prose-invert max-w-none ${className}`}>
      {processedContent.map((paragraph) => (
        <p key={paragraph.id} className={paragraph.id > 0 ? 'mt-4' : ''}>
          {paragraph.text}
        </p>
      ))}
      {cursorElement}
    </div>
  );
});

MemoizedStreamingText.displayName = 'MemoizedStreamingText';

// Debounced vocabulary extraction hook
export const useDebouncedVocabularyExtraction = (
  text: string,
  extractionFunction: (text: string) => Promise<any[]>,
  delay: number = 500
) => {
  const [vocabulary, setVocabulary] = React.useState<any[]>([]);
  const [isExtracting, setIsExtracting] = React.useState(false);

  // Debounced extraction function
  const debouncedExtract = useMemo(
    () => debounce(async (textToExtract: string) => {
      if (!textToExtract || textToExtract.length < 50) {
        setVocabulary([]);
        return;
      }

      setIsExtracting(true);
      try {
        const extracted = await extractionFunction(textToExtract);
        setVocabulary(extracted);
      } catch (error) {
        console.error('Vocabulary extraction failed:', error);
      } finally {
        setIsExtracting(false);
      }
    }, delay),
    [extractionFunction, delay]
  );

  // Effect to trigger extraction
  React.useEffect(() => {
    debouncedExtract(text);
    
    // Cleanup function
    return () => {
      debouncedExtract.cancel();
    };
  }, [text, debouncedExtract]);

  return { vocabulary, isExtracting };
};

// Optimized text highlighting component
export const OptimizedTextHighlighter = memo<{
  text: string;
  vocabularyWords: string[];
  onWordClick: (word: string) => void;
  showDifficultyColors: boolean;
}>(({ text, vocabularyWords, onWordClick, showDifficultyColors }) => {
  // Memoize highlighted text to avoid expensive DOM operations
  const highlightedHTML = useMemo(() => {
    if (!vocabularyWords.length || !text) return text;

    let highlighted = text;
    
    // Use a single pass with a combined regex for better performance
    const wordsPattern = vocabularyWords.map(word => 
      word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') // Escape special regex characters
    ).join('|');
    
    if (!wordsPattern) return text;
    
    const regex = new RegExp(`\\b(${wordsPattern})\\b`, 'gi');
    
    highlighted = highlighted.replace(regex, (match, word) => {
      const lowerWord = word.toLowerCase();
      const difficultyClass = showDifficultyColors 
        ? 'vocabulary-word-difficulty' 
        : 'vocabulary-word-simple';
      
      return `<mark class="vocabulary-word cursor-pointer rounded px-1 border transition-all duration-200 hover:shadow-sm hover:scale-105 ${difficultyClass}" data-word="${lowerWord}">${match}</mark>`;
    });

    return highlighted;
  }, [text, vocabularyWords, showDifficultyColors]);

  // Memoize click handler to avoid creating new functions
  const handleClick = useCallback((event: React.MouseEvent<HTMLElement>) => {
    const target = event.target as HTMLElement;
    if (target.classList.contains('vocabulary-word')) {
      const word = target.getAttribute('data-word');
      if (word) {
        onWordClick(word);
        // Add visual feedback
        target.classList.add('animate-pulse');
        setTimeout(() => target.classList.remove('animate-pulse'), 300);
      }
    }
  }, [onWordClick]);

  return (
    <div
      className="prose prose-gray dark:prose-invert max-w-none leading-relaxed select-text"
      dangerouslySetInnerHTML={{ __html: highlightedHTML }}
      onClick={handleClick}
    />
  );
});

OptimizedTextHighlighter.displayName = 'OptimizedTextHighlighter';

// Virtual scrolling for large vocabulary lists
export const VirtualizedVocabularyList = memo<{
  vocabulary: any[];
  itemHeight: number;
  maxHeight: number;
  renderItem: (item: any, index: number) => React.ReactNode;
}>(({ vocabulary, itemHeight, maxHeight, renderItem }) => {
  const [scrollTop, setScrollTop] = React.useState(0);
  const containerRef = React.useRef<HTMLDivElement>(null);

  const visibleCount = Math.ceil(maxHeight / itemHeight);
  const startIndex = Math.floor(scrollTop / itemHeight);
  const endIndex = Math.min(startIndex + visibleCount + 1, vocabulary.length);

  const visibleItems = useMemo(() => {
    return vocabulary.slice(startIndex, endIndex).map((item, index) => ({
      item,
      index: startIndex + index,
      top: (startIndex + index) * itemHeight,
    }));
  }, [vocabulary, startIndex, endIndex, itemHeight]);

  const handleScroll = useCallback((event: React.UIEvent<HTMLDivElement>) => {
    setScrollTop(event.currentTarget.scrollTop);
  }, []);

  return (
    <div
      ref={containerRef}
      className="relative overflow-auto"
      style={{ height: maxHeight }}
      onScroll={handleScroll}
    >
      <div style={{ height: vocabulary.length * itemHeight, position: 'relative' }}>
        {visibleItems.map(({ item, index, top }) => (
          <div
            key={index}
            style={{
              position: 'absolute',
              top: top,
              height: itemHeight,
              width: '100%',
            }}
          >
            {renderItem(item, index)}
          </div>
        ))}
      </div>
    </div>
  );
});

VirtualizedVocabularyList.displayName = 'VirtualizedVocabularyList';

// Efficient text chunking for streaming
export class StreamingTextProcessor {
  private buffer: string = '';
  private callbacks: Set<(chunk: string) => void> = new Set();
  private processingTimeout: NodeJS.Timeout | null = null;

  addChunk(chunk: string): void {
    this.buffer += chunk;
    this.scheduleProcessing();
  }

  onChunk(callback: (chunk: string) => void): () => void {
    this.callbacks.add(callback);
    return () => this.callbacks.delete(callback);
  }

  private scheduleProcessing(): void {
    if (this.processingTimeout) {
      clearTimeout(this.processingTimeout);
    }

    // Batch process chunks to avoid excessive re-renders
    this.processingTimeout = setTimeout(() => {
      this.processBuffer();
    }, 16); // ~60fps
  }

  private processBuffer(): void {
    if (this.buffer.length === 0) return;

    // Find complete sentences or paragraphs to emit
    const sentences = this.buffer.match(/[^.!?]*[.!?]/g) || [];
    
    if (sentences.length > 0) {
      const completeText = sentences.join('');
      this.buffer = this.buffer.slice(completeText.length);
      
      this.callbacks.forEach(callback => callback(completeText));
    }
  }

  flush(): void {
    if (this.buffer.length > 0) {
      this.callbacks.forEach(callback => callback(this.buffer));
      this.buffer = '';
    }

    if (this.processingTimeout) {
      clearTimeout(this.processingTimeout);
      this.processingTimeout = null;
    }
  }

  clear(): void {
    this.buffer = '';
    this.callbacks.clear();
    if (this.processingTimeout) {
      clearTimeout(this.processingTimeout);
      this.processingTimeout = null;
    }
  }
}

// Performance monitoring hook
export const usePerformanceMetrics = () => {
  const [metrics, setMetrics] = React.useState({
    renderTime: 0,
    memoryUsage: 0,
    vocabularyProcessingTime: 0,
    textHighlightingTime: 0,
  });

  const measureRender = useCallback((name: string, fn: () => void) => {
    const start = performance.now();
    fn();
    const end = performance.now();
    
    setMetrics(prev => ({
      ...prev,
      [name]: end - start,
    }));
  }, []);

  const measureMemory = useCallback(() => {
    if ('memory' in performance) {
      const memory = (performance as any).memory;
      setMetrics(prev => ({
        ...prev,
        memoryUsage: memory.usedJSHeapSize,
      }));
    }
  }, []);

  return { metrics, measureRender, measureMemory };
};

// Optimized context provider for description generation
export const DescriptionOptimizationContext = React.createContext({
  enableVirtualization: true,
  chunkSize: 100,
  debounceDelay: 300,
  enablePerformanceMonitoring: false,
});

export const useDescriptionOptimization = () => {
  return React.useContext(DescriptionOptimizationContext);
};