import React, { useState, useCallback } from 'react';
import { 
  XMarkIcon, 
  SparklesIcon, 
  ArrowPathIcon, 
  SpeakerWaveIcon,
  DocumentArrowDownIcon,
  ClipboardIcon,
  TrashIcon
} from '@heroicons/react/24/outline';
import { Image, DescriptionStyle } from '../../types';
import { Button } from '../Shared/Button/Button';
import { StreamingText } from './StreamingText';
import { StyleSelector } from './StyleSelector';
import { VocabularyHighlighter } from './VocabularyHighlighter';
import { ContextInput } from './ContextInput';
import { useAIGeneration } from '../../hooks/useAIGeneration';
import { useVocabulary } from '../../hooks/useVocabulary';
import toast from 'react-hot-toast';

interface DescriptionPanelProps {
  image: Image | null;
  onClose: () => void;
  isOpen: boolean;
  className?: string;
}

export const DescriptionPanel: React.FC<DescriptionPanelProps> = ({
  image,
  onClose,
  isOpen,
  className = '',
}) => {
  const [selectedStyle, setSelectedStyle] = useState<DescriptionStyle>('academic');
  const [showVocabularyHighlight, setShowVocabularyHighlight] = useState(true);
  const [contextNotes, setContextNotes] = useState('');
  const [focusAreas, setFocusAreas] = useState<string[]>([]);
  const [vocabularyLevel, setVocabularyLevel] = useState<1 | 2 | 3 | 4 | 5>(3);
  const [isSpeaking, setIsSpeaking] = useState(false);
  
  const { 
    description, 
    vocabulary, 
    isGenerating, 
    error, 
    tokenCount, 
    processingTime, 
    progress, 
    generate, 
    cancel,
    clearCache
  } = useAIGeneration();
  const { addWord } = useVocabulary();

  const handleGenerate = useCallback(() => {
    if (!image) return;
    generate(image.id, selectedStyle, {
      context: contextNotes,
      focusAreas,
      vocabularyLevel,
      forceRefresh: false,
    });
  }, [image, selectedStyle, contextNotes, focusAreas, vocabularyLevel, generate]);

  const handleRegenerateWithNewSettings = useCallback(() => {
    if (!image) return;
    generate(image.id, selectedStyle, {
      context: contextNotes,
      focusAreas,
      vocabularyLevel,
      forceRefresh: true, // Force refresh to get new content
    });
  }, [image, selectedStyle, contextNotes, focusAreas, vocabularyLevel, generate]);

  const handleWordSelect = useCallback(async (word: string, definition: string) => {
    if (!image) return;
    
    try {
      await addWord({
        word,
        definition,
        language: 'en',
        difficulty_level: vocabularyLevel,
        context: description.substring(0, 200),
        image_id: image.id,
        learned: false,
        review_count: 0,
      });
      toast.success(`Added "${word}" to vocabulary`);
    } catch (error) {
      console.error('Failed to add word:', error);
      toast.error('Failed to add word to vocabulary');
    }
  }, [image, description, vocabularyLevel, addWord]);

  const handleSpeakDescription = useCallback(() => {
    if (!description || isSpeaking) return;
    
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(description);
      utterance.rate = 0.8;
      utterance.volume = 0.8;
      utterance.onstart = () => setIsSpeaking(true);
      utterance.onend = () => setIsSpeaking(false);
      utterance.onerror = () => {
        setIsSpeaking(false);
        toast.error('Speech synthesis failed');
      };
      
      speechSynthesis.speak(utterance);
    } else {
      toast.error('Speech synthesis not supported in this browser');
    }
  }, [description, isSpeaking]);

  const handleStopSpeaking = useCallback(() => {
    if ('speechSynthesis' in window) {
      speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  }, []);

  const handleCopyToClipboard = useCallback(() => {
    if (!description) return;
    
    navigator.clipboard.writeText(description).then(() => {
      toast.success('Description copied to clipboard');
    }).catch(() => {
      toast.error('Failed to copy to clipboard');
    });
  }, [description]);

  const handleExportDescription = useCallback((format: 'txt' | 'md' | 'pdf') => {
    if (!description || !image) return;
    
    let content = '';
    let mimeType = '';
    let extension = '';
    
    switch (format) {
      case 'txt':
        content = description;
        mimeType = 'text/plain';
        extension = 'txt';
        break;
      case 'md':
        content = `# Image Description\n\n![Image](${image.urls.regular})\n\n**Style:** ${selectedStyle}\n**Generated:** ${new Date().toLocaleString()}\n\n## Description\n\n${description}\n\n## Vocabulary\n\n${vocabulary.map(word => `- **${word.word}**: ${word.definition}`).join('\n')}`;
        mimeType = 'text/markdown';
        extension = 'md';
        break;
      case 'pdf':
        toast.info('PDF export coming soon!');
        return;
    }
    
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `description-${image.id}-${selectedStyle}.${extension}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    toast.success(`Description exported as ${format.toUpperCase()}`);
  }, [description, vocabulary, image, selectedStyle]);

  // Reset state when image changes
  React.useEffect(() => {
    if (image && isOpen) {
      // Auto-generate description when panel opens with new image
      handleGenerate();
    }
    // Stop speaking when image changes
    if ('speechSynthesis' in window) {
      speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  }, [image?.id, isOpen]);

  // Stop speaking when panel closes
  React.useEffect(() => {
    if (!isOpen && 'speechSynthesis' in window) {
      speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  }, [isOpen]);

  if (!isOpen || !image) {
    return null;
  }

  return (
    <div className={`fixed inset-0 z-50 overflow-hidden ${className}`}>
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
        aria-hidden="true"
      />
      
      {/* Panel */}
      <div className="absolute right-0 top-0 h-full w-full max-w-2xl bg-white dark:bg-gray-900 shadow-2xl">
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center space-x-3">
              <SparklesIcon className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
              <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                AI Description
              </h2>
            </div>
            
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="p-2"
              aria-label="Close description panel"
            >
              <XMarkIcon className="w-5 h-5" />
            </Button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-6">
            {/* Image Preview */}
            <div className="mb-6">
              <div className="relative aspect-video rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-800">
                <img
                  src={image.urls.regular}
                  alt={image.alt_description || 'Selected image'}
                  className="w-full h-full object-cover"
                />
                {/* Image info overlay */}
                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-4">
                  <div className="text-white text-sm">
                    <div className="font-medium">
                      by {image.user?.name || image.user?.username}
                    </div>
                    <div className="text-gray-300">
                      {image.width} × {image.height}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Style Selector */}
            <div className="mb-6">
              <StyleSelector
                selectedStyle={selectedStyle}
                onStyleChange={setSelectedStyle}
                vocabularyLevel={vocabularyLevel}
                onVocabularyLevelChange={setVocabularyLevel}
                disabled={isGenerating}
              />
            </div>

            {/* Context Input */}
            <div className="mb-6">
              <ContextInput
                value={contextNotes}
                onChange={setContextNotes}
                focusAreas={focusAreas}
                onFocusAreasChange={setFocusAreas}
                disabled={isGenerating}
                suggestions={[
                  "Focus on the emotional impact and mood",
                  "Analyze the technical photography aspects",
                  "Describe for a beginner audience",
                  "Emphasize the artistic composition",
                  "Include historical or cultural context"
                ]}
              />
            </div>

            {/* Generate Controls */}
            <div className="mb-6 space-y-3">
              <div className="flex space-x-3">
                <Button
                  onClick={handleGenerate}
                  disabled={isGenerating}
                  loading={isGenerating}
                  className="flex-1"
                >
                  {isGenerating ? 'Generating...' : 'Generate Description'}
                </Button>
                
                {isGenerating && (
                  <Button
                    variant="outline"
                    onClick={cancel}
                    className="px-4"
                  >
                    Cancel
                  </Button>
                )}
                
                {description && !isGenerating && (
                  <Button
                    variant="outline"
                    onClick={handleRegenerateWithNewSettings}
                    className="px-4"
                    aria-label="Regenerate with current settings"
                  >
                    <ArrowPathIcon className="w-4 h-4" />
                  </Button>
                )}
                
                {!isGenerating && (
                  <Button
                    variant="ghost"
                    onClick={clearCache}
                    className="px-4 text-gray-500"
                    aria-label="Clear cache"
                  >
                    <TrashIcon className="w-4 h-4" />
                  </Button>
                )}
              </div>
              
              {/* Progress bar */}
              {isGenerating && (
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div 
                    className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              )}
              
              {/* Generation stats */}
              {(tokenCount > 0 || processingTime > 0) && !isGenerating && (
                <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400">
                  <span>{tokenCount} tokens</span>
                  <span>{processingTime}ms processing time</span>
                </div>
              )}
            </div>

            {/* Error Display */}
            {error && (
              <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                <div className="text-red-700 dark:text-red-400 text-sm">
                  <strong>Error:</strong> {error.message}
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleGenerate}
                  className="mt-2"
                >
                  Try Again
                </Button>
              </div>
            )}

            {/* Description Display */}
            {(description || isGenerating) && (
              <div className="space-y-4">
                {/* Vocabulary Toggle */}
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
                    Description
                  </h3>
                  <label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={showVocabularyHighlight}
                      onChange={(e) => setShowVocabularyHighlight(e.target.checked)}
                      className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700"
                    />
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      Highlight vocabulary
                    </span>
                  </label>
                </div>

                {/* Streaming Description */}
                <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 bg-gray-50 dark:bg-gray-800/50">
                  {showVocabularyHighlight ? (
                    <VocabularyHighlighter
                      text={description}
                      onWordSelect={handleWordSelect}
                      isStreaming={isGenerating}
                    />
                  ) : (
                    <StreamingText
                      content={description}
                      isStreaming={isGenerating}
                      className="text-gray-900 dark:text-gray-100 leading-relaxed"
                    />
                  )}
                </div>

                {/* Description Stats & Actions */}
                {description && !isGenerating && (
                  <div className="space-y-3">
                    <div className="flex justify-between text-sm text-gray-500 dark:text-gray-400">
                      <span>
                        {description.split(/\s+/).length} words
                      </span>
                      <span>
                        ~{Math.ceil(description.split(/\s+/).length / 200)} min read
                      </span>
                    </div>
                    
                    {/* Quick action buttons */}
                    <div className="flex space-x-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={handleCopyToClipboard}
                        className="flex items-center space-x-1"
                      >
                        <ClipboardIcon className="w-4 h-4" />
                        <span>Copy</span>
                      </Button>
                      
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={isSpeaking ? handleStopSpeaking : handleSpeakDescription}
                        className="flex items-center space-x-1"
                      >
                        <SpeakerWaveIcon className="w-4 h-4" />
                        <span>{isSpeaking ? 'Stop' : 'Listen'}</span>
                      </Button>
                      
                      <div className="relative group">
                        <Button
                          variant="outline"
                          size="sm"
                          className="flex items-center space-x-1"
                        >
                          <DocumentArrowDownIcon className="w-4 h-4" />
                          <span>Export</span>
                        </Button>
                        
                        {/* Export dropdown */}
                        <div className="absolute bottom-full left-0 mb-2 w-32 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                          <button
                            onClick={() => handleExportDescription('txt')}
                            className="block w-full px-3 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-t-lg"
                          >
                            Text (.txt)
                          </button>
                          <button
                            onClick={() => handleExportDescription('md')}
                            className="block w-full px-3 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-b-lg"
                          >
                            Markdown (.md)
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                
                {/* Vocabulary Statistics */}
                {vocabulary.length > 0 && !isGenerating && (
                  <div className="mt-4 p-4 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg">
                    <div className="text-sm font-medium text-indigo-800 dark:text-indigo-200 mb-2">
                      Vocabulary Extracted: {vocabulary.length} words
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {vocabulary.slice(0, 5).map((word, index) => (
                        <span
                          key={index}
                          className="px-2 py-1 text-xs bg-indigo-100 dark:bg-indigo-800/50 text-indigo-700 dark:text-indigo-300 rounded-full"
                        >
                          {word.word}
                        </span>
                      ))}
                      {vocabulary.length > 5 && (
                        <span className="px-2 py-1 text-xs text-indigo-600 dark:text-indigo-400">
                          +{vocabulary.length - 5} more
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Tips when no description */}
            {!description && !isGenerating && !error && (
              <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                <SparklesIcon className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p className="text-lg mb-2">Ready to generate!</p>
                <p className="text-sm">
                  Choose a style and click "Generate Description" to create an AI-powered 
                  description of this image.
                </p>
              </div>
            )}
          </div>

          {/* Footer Actions */}
          {description && !isGenerating && (
            <div className="border-t border-gray-200 dark:border-gray-700 p-6">
              <div className="grid grid-cols-2 gap-3">
                <Button
                  variant="outline"
                  onClick={handleCopyToClipboard}
                  className="flex items-center justify-center space-x-2"
                >
                  <ClipboardIcon className="w-4 h-4" />
                  <span>Copy Text</span>
                </Button>
                <Button
                  variant="outline"
                  onClick={() => handleExportDescription('txt')}
                  className="flex items-center justify-center space-x-2"
                >
                  <DocumentArrowDownIcon className="w-4 h-4" />
                  <span>Save File</span>
                </Button>
              </div>
              
              {/* Vocabulary summary for footer */}
              {vocabulary.length > 0 && (
                <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <div className="text-center text-sm text-gray-600 dark:text-gray-400">
                    <span className="font-medium">{vocabulary.length}</span> vocabulary words extracted
                    <span className="mx-2">•</span>
                    <span>Click words above to add to your collection</span>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};