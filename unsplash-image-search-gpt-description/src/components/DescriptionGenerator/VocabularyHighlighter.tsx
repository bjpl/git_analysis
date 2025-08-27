import React, { useState, useCallback, useMemo, useEffect } from 'react';
import { BookOpenIcon, PlusIcon, AcademicCapIcon } from '@heroicons/react/24/outline';
import { StreamingText } from './StreamingText';
import { VocabularyWord } from '../../types';

interface VocabularyHighlighterProps {
  text: string;
  extractedVocabulary?: VocabularyWord[];
  onWordSelect: (word: string, definition: string) => void;
  isStreaming?: boolean;
  showDifficultyColors?: boolean;
  enableRealTimeExtraction?: boolean;
  className?: string;
}

interface WordDefinition {
  word: string;
  definition: string;
  difficulty: number;
}

// Mock vocabulary database for demo
const mockVocabulary: Record<string, WordDefinition> = {
  sophisticated: {
    word: 'sophisticated',
    definition: 'Having a refined knowledge of the ways of the world; complex or advanced',
    difficulty: 4,
  },
  compositional: {
    word: 'compositional',
    definition: 'Relating to the arrangement of elements in a work of art',
    difficulty: 5,
  },
  interplay: {
    word: 'interplay',
    definition: 'The way in which two or more things have an effect on each other',
    difficulty: 3,
  },
  hierarchy: {
    word: 'hierarchy',
    definition: 'A system in which members are ranked according to relative status or authority',
    difficulty: 4,
  },
  systematically: {
    word: 'systematically',
    definition: 'According to a fixed plan or system; methodically',
    difficulty: 4,
  },
  contextual: {
    word: 'contextual',
    definition: 'Relating to or depending on the context or circumstances',
    difficulty: 4,
  },
  harmonizes: {
    word: 'harmonizes',
    definition: 'To combine in a pleasing or effective way; to be in agreement',
    difficulty: 3,
  },
  suspended: {
    word: 'suspended',
    definition: 'Temporarily prevented from continuing; hanging from something',
    difficulty: 2,
  },
  symphony: {
    word: 'symphony',
    definition: 'An elaborate musical composition or something regarded as having a harmonious whole',
    difficulty: 3,
  },
  yearning: {
    word: 'yearning',
    definition: 'A feeling of intense longing for something',
    difficulty: 3,
  },
  bokeh: {
    word: 'bokeh',
    definition: 'The visual quality of the out-of-focus areas in a photograph',
    difficulty: 5,
  },
  aperture: {
    word: 'aperture',
    definition: 'A hole or opening through which light travels in a camera lens',
    difficulty: 4,
  },
  retention: {
    word: 'retention',
    definition: 'The ability to keep or continue to have something',
    difficulty: 3,
  },
  optimal: {
    word: 'optimal',
    definition: 'Best or most favorable; optimum',
    difficulty: 3,
  },
  transcends: {
    word: 'transcends',
    definition: 'To go beyond the range or limits of something',
    difficulty: 4,
  },
  narrative: {
    word: 'narrative',
    definition: 'A spoken or written account of connected events; a story',
    difficulty: 3,
  },
};

export const VocabularyHighlighter: React.FC<VocabularyHighlighterProps> = ({
  text,
  extractedVocabulary = [],
  onWordSelect,
  isStreaming = false,
  showDifficultyColors = true,
  enableRealTimeExtraction = true,
  className = '',
}) => {
  const [hoveredWord, setHoveredWord] = useState<string | null>(null);
  const [popoverPosition, setPopoverPosition] = useState<{ x: number; y: number } | null>(null);
  const [realtimeVocabulary, setRealtimeVocabulary] = useState<VocabularyWord[]>([]);
  const [isExtracting, setIsExtracting] = useState(false);

  // Combine extracted vocabulary with mock vocabulary and real-time extraction
  const allVocabulary = useMemo(() => {
    const combined: Record<string, VocabularyWord> = {};
    
    // Add mock vocabulary (for fallback)
    Object.entries(mockVocabulary).forEach(([word, data]) => {
      combined[word.toLowerCase()] = {
        id: `mock_${word}`,
        word: data.word,
        definition: data.definition,
        language: 'en',
        difficulty_level: data.difficulty as 1 | 2 | 3 | 4 | 5,
        context: 'Generated from text analysis',
        learned: false,
        review_count: 0,
        created_at: new Date().toISOString(),
      };
    });
    
    // Add extracted vocabulary (from AI)
    extractedVocabulary.forEach(word => {
      combined[word.word.toLowerCase()] = word;
    });
    
    // Add real-time vocabulary
    realtimeVocabulary.forEach(word => {
      combined[word.word.toLowerCase()] = word;
    });
    
    return combined;
  }, [extractedVocabulary, realtimeVocabulary]);
  
  // Extract vocabulary words present in text
  const vocabularyWords = useMemo(() => {
    const words = new Set<string>();
    const textLower = text.toLowerCase();
    
    Object.keys(allVocabulary).forEach(word => {
      // Use word boundary regex to match whole words only
      const regex = new RegExp(`\\b${word}\\b`, 'gi');
      if (regex.test(textLower)) {
        words.add(word);
      }
    });
    
    return Array.from(words);
  }, [text, allVocabulary]);
  
  // Real-time vocabulary extraction as user types/streams
  useEffect(() => {
    if (!enableRealTimeExtraction || !text || text.length < 50) return;
    
    const extractVocabulary = async () => {
      setIsExtracting(true);
      
      // Simulate API call for vocabulary extraction
      // In production, this would call your vocabulary extraction API
      try {
        const words = text.match(/\b[A-Za-z]{6,}\b/g) || [];
        const sophisticatedWords = words.filter(word => {
          const lowerWord = word.toLowerCase();
          return (
            !['the', 'and', 'that', 'have', 'for', 'not', 'with', 'you', 'this', 'but', 'his', 'from', 'they'].includes(lowerWord) &&
            word.length >= 6 &&
            !allVocabulary[lowerWord]
          );
        });
        
        const newVocab: VocabularyWord[] = sophisticatedWords.slice(0, 3).map((word, index) => ({
          id: `realtime_${word}_${Date.now()}_${index}`,
          word: word.toLowerCase(),
          definition: `Advanced term: ${word}`, // In production, get real definition
          language: 'en',
          difficulty_level: Math.min(5, Math.max(3, Math.floor(word.length / 2))) as 1 | 2 | 3 | 4 | 5,
          context: `Extracted from: "${text.substring(0, 100)}..."`,
          learned: false,
          review_count: 0,
          created_at: new Date().toISOString(),
        }));
        
        setRealtimeVocabulary(prev => {
          const combined = [...prev, ...newVocab];
          // Keep only unique words
          const unique = combined.filter((word, index, arr) => 
            arr.findIndex(w => w.word === word.word) === index
          );
          return unique.slice(0, 10); // Limit to 10 words
        });
      } catch (error) {
        console.error('Real-time vocabulary extraction failed:', error);
      } finally {
        setIsExtracting(false);
      }
    };
    
    const timeoutId = setTimeout(extractVocabulary, 2000); // Extract after 2 seconds of text stability
    
    return () => clearTimeout(timeoutId);
  }, [text, enableRealTimeExtraction, allVocabulary]);

  // Highlight vocabulary words in text
  const highlightText = useCallback((content: string) => {
    if (!vocabularyWords.length || !content) {
      return content;
    }

    let highlightedText = content;
    
    vocabularyWords.forEach(word => {
      const regex = new RegExp(`\\b(${word})\\b`, 'gi');
      highlightedText = highlightedText.replace(regex, (match) => {
        const wordData = allVocabulary[word.toLowerCase()];
        const difficulty = wordData?.difficulty_level || 3;
        
        let difficultyColor = 'bg-gray-100 text-gray-800 border-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600';
        
        if (showDifficultyColors) {
          const colors = {
            1: 'bg-green-100 text-green-800 border-green-200 dark:bg-green-900/20 dark:text-green-300 dark:border-green-700',
            2: 'bg-blue-100 text-blue-800 border-blue-200 dark:bg-blue-900/20 dark:text-blue-300 dark:border-blue-700',
            3: 'bg-yellow-100 text-yellow-800 border-yellow-200 dark:bg-yellow-900/20 dark:text-yellow-300 dark:border-yellow-700',
            4: 'bg-orange-100 text-orange-800 border-orange-200 dark:bg-orange-900/20 dark:text-orange-300 dark:border-orange-700',
            5: 'bg-red-100 text-red-800 border-red-200 dark:bg-red-900/20 dark:text-red-300 dark:border-red-700',
          };
          difficultyColor = colors[difficulty] || difficultyColor;
        } else {
          // Single color for all vocabulary words when difficulty colors are disabled
          difficultyColor = 'bg-indigo-100 text-indigo-800 border-indigo-200 dark:bg-indigo-900/20 dark:text-indigo-300 dark:border-indigo-700';
        }

        return `<mark class="vocabulary-word cursor-pointer rounded px-1 border transition-all duration-200 hover:shadow-sm hover:scale-105 ${difficultyColor}" data-word="${word.toLowerCase()}">${match}</mark>`;
      });
    });

    return highlightedText;
  }, [vocabularyWords]);

  const handleWordHover = useCallback((event: React.MouseEvent<HTMLElement>) => {
    const target = event.target as HTMLElement;
    if (target.classList.contains('vocabulary-word')) {
      const word = target.getAttribute('data-word');
      if (word) {
        setHoveredWord(word);
        const rect = target.getBoundingClientRect();
        setPopoverPosition({
          x: rect.left + rect.width / 2,
          y: rect.top - 10,
        });
      }
    }
  }, []);

  const handleWordLeave = useCallback(() => {
    setHoveredWord(null);
    setPopoverPosition(null);
  }, []);

  const handleWordClick = useCallback((event: React.MouseEvent<HTMLElement>) => {
    const target = event.target as HTMLElement;
    if (target.classList.contains('vocabulary-word')) {
      const word = target.getAttribute('data-word');
      if (word && allVocabulary[word]) {
        const wordData = allVocabulary[word];
        onWordSelect(wordData.word, wordData.definition);
        
        // Add visual feedback for successful selection
        target.classList.add('animate-pulse');
        setTimeout(() => target.classList.remove('animate-pulse'), 600);
      }
    }
  }, [onWordSelect, allVocabulary]);

  if (isStreaming) {
    return (
      <StreamingText
        content={text}
        isStreaming={isStreaming}
        className={className}
      />
    );
  }

  return (
    <div className={`relative ${className}`}>
      {/* Vocabulary stats */}
      {(vocabularyWords.length > 0 || isExtracting) && (
        <div className="mb-4 space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
              <BookOpenIcon className="w-4 h-4" />
              <span>
                {vocabularyWords.length} vocabulary {vocabularyWords.length === 1 ? 'word' : 'words'} found
              </span>
              {extractedVocabulary.length > 0 && (
                <>
                  <span className="text-gray-400 dark:text-gray-500">•</span>
                  <span className="flex items-center space-x-1">
                    <AcademicCapIcon className="w-3 h-3" />
                    <span>{extractedVocabulary.length} from AI</span>
                  </span>
                </>
              )}
              {realtimeVocabulary.length > 0 && (
                <>
                  <span className="text-gray-400 dark:text-gray-500">•</span>
                  <span className="flex items-center space-x-1">
                    <span className="w-2 h-2 bg-purple-500 rounded-full animate-pulse" />
                    <span>{realtimeVocabulary.length} real-time</span>
                  </span>
                </>
              )}
            </div>
            
            {isExtracting && (
              <div className="flex items-center space-x-1 text-xs text-purple-600 dark:text-purple-400">
                <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" />
                <span>Extracting...</span>
              </div>
            )}
          </div>
          
          <div className="text-xs text-gray-500 dark:text-gray-400">
            Click highlighted words to add to your vocabulary collection
          </div>
        </div>
      )}

      {/* Highlighted text */}
      <div
        className="prose prose-gray dark:prose-invert max-w-none leading-relaxed"
        dangerouslySetInnerHTML={{ __html: highlightText(text) }}
        onMouseOver={handleWordHover}
        onMouseLeave={handleWordLeave}
        onClick={handleWordClick}
      />

      {/* Word definition popover */}
      {hoveredWord && popoverPosition && allVocabulary[hoveredWord] && (
        <div
          className="fixed z-50 max-w-sm p-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 
                   rounded-lg shadow-xl transform -translate-x-1/2 -translate-y-full pointer-events-none
                   backdrop-blur-sm bg-white/95 dark:bg-gray-800/95"
          style={{
            left: popoverPosition.x,
            top: popoverPosition.y,
          }}
        >
          <div className="space-y-3">
            <div className="flex items-start justify-between">
              <div>
                <div className="font-semibold text-gray-900 dark:text-gray-100 text-lg">
                  {allVocabulary[hoveredWord].word}
                </div>
                <div className="flex items-center space-x-2 mt-1">
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    showDifficultyColors ? {
                      1: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300',
                      2: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300',
                      3: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300',
                      4: 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-300',
                      5: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300',
                    }[allVocabulary[hoveredWord].difficulty_level] || 'bg-gray-100 text-gray-700'
                    : 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-300'
                  }`}>
                    Level {allVocabulary[hoveredWord].difficulty_level}
                  </span>
                  {allVocabulary[hoveredWord].id.startsWith('realtime_') && (
                    <span className="text-xs px-2 py-1 rounded-full bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300">
                      Real-time
                    </span>
                  )}
                </div>
              </div>
              <PlusIcon className="w-5 h-5 text-indigo-500 flex-shrink-0" />
            </div>
            
            <div className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
              {allVocabulary[hoveredWord].definition}
            </div>
            
            {allVocabulary[hoveredWord].context && (
              <div className="text-xs text-gray-500 dark:text-gray-400 italic border-l-2 border-gray-200 dark:border-gray-600 pl-2">
                Context: {allVocabulary[hoveredWord].context}
              </div>
            )}
            
            <div className="text-xs text-indigo-600 dark:text-indigo-400 font-medium">
              Click to add to your vocabulary collection
            </div>
          </div>
          
          {/* Arrow */}
          <div 
            className="absolute top-full left-1/2 transform -translate-x-1/2 w-3 h-3 
                     bg-white dark:bg-gray-800 border-r border-b border-gray-200 dark:border-gray-700 
                     rotate-45"
          />
        </div>
      )}

      {/* Difficulty legend */}
      {vocabularyWords.length > 0 && (
        <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
          <div className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Difficulty Levels:
          </div>
          <div className="flex flex-wrap gap-2 text-xs">
            <div className="flex items-center space-x-1">
              <div className="w-3 h-3 rounded bg-green-100 border border-green-200" />
              <span>Beginner</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-3 h-3 rounded bg-blue-100 border border-blue-200" />
              <span>Elementary</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-3 h-3 rounded bg-yellow-100 border border-yellow-200" />
              <span>Intermediate</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-3 h-3 rounded bg-orange-100 border border-orange-200" />
              <span>Advanced</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-3 h-3 rounded bg-red-100 border border-red-200" />
              <span>Expert</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};