import React, { useEffect, useState } from 'react';
import { StreamingTextProps } from '../../types';
import { cn } from '../../utils/cn';

export const StreamingText: React.FC<StreamingTextProps> = ({
  content,
  isStreaming,
  onComplete,
  className = '',
}) => {
  const [displayedContent, setDisplayedContent] = useState('');
  const [showCursor, setShowCursor] = useState(true);

  // Animate the text streaming in
  useEffect(() => {
    if (isStreaming && content.length > displayedContent.length) {
      const timeoutId = setTimeout(() => {
        setDisplayedContent(content.slice(0, displayedContent.length + 1));
      }, 20); // Adjust speed as needed

      return () => clearTimeout(timeoutId);
    } else if (!isStreaming) {
      // When streaming stops, immediately show full content
      setDisplayedContent(content);
      
      // Call onComplete callback after a brief delay
      if (onComplete && displayedContent !== content) {
        const timeoutId = setTimeout(onComplete, 100);
        return () => clearTimeout(timeoutId);
      }
    }
  }, [content, displayedContent, isStreaming, onComplete]);

  // Cursor blinking effect
  useEffect(() => {
    if (isStreaming) {
      const interval = setInterval(() => {
        setShowCursor(prev => !prev);
      }, 530);

      return () => clearInterval(interval);
    } else {
      setShowCursor(false);
    }
  }, [isStreaming]);

  // Reset when content changes completely (new generation)
  useEffect(() => {
    if (content.length < displayedContent.length) {
      setDisplayedContent('');
    }
  }, [content.length, displayedContent.length]);

  const formatText = (text: string) => {
    // Split text into paragraphs
    const paragraphs = text.split('\n').filter(p => p.trim());
    
    return paragraphs.map((paragraph, index) => (
      <p key={index} className={index > 0 ? 'mt-4' : ''}>
        {paragraph}
      </p>
    ));
  };

  return (
    <div className={cn('relative', className)}>
      <div className="prose prose-gray dark:prose-invert max-w-none">
        {displayedContent ? (
          formatText(displayedContent)
        ) : isStreaming ? (
          <div className="text-gray-400 dark:text-gray-500 italic">
            Generating description...
          </div>
        ) : (
          <div className="text-gray-400 dark:text-gray-500 italic">
            Click "Generate Description" to start
          </div>
        )}
      </div>
      
      {/* Streaming cursor */}
      {isStreaming && (
        <span
          className={cn(
            'inline-block w-0.5 h-5 bg-indigo-600 dark:bg-indigo-400 ml-1 transition-opacity',
            showCursor ? 'opacity-100' : 'opacity-0'
          )}
          aria-hidden="true"
        />
      )}
      
      {/* Progress indicator */}
      {isStreaming && (
        <div className="mt-4 flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
          <div className="flex space-x-1">
            <div className="w-2 h-2 bg-indigo-600 rounded-full animate-bounce" />
            <div className="w-2 h-2 bg-indigo-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
            <div className="w-2 h-2 bg-indigo-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
          </div>
          <span>AI is thinking...</span>
        </div>
      )}
    </div>
  );
};