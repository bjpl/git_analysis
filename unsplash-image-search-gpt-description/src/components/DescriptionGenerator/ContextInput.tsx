import React, { useState, useCallback, useRef } from 'react';
import { 
  DocumentTextIcon, 
  XMarkIcon,
  LightBulbIcon,
  SparklesIcon,
  MagnifyingGlassIcon
} from '@heroicons/react/24/outline';
import { Button } from '../Shared/Button/Button';
import { useDebounce } from '../../hooks/useDebounce';

interface ContextInputProps {
  value: string;
  onChange: (value: string) => void;
  focusAreas: string[];
  onFocusAreasChange: (areas: string[]) => void;
  suggestions?: string[];
  disabled?: boolean;
  className?: string;
}

interface FocusAreaTag {
  id: string;
  label: string;
  icon?: React.ComponentType<any>;
}

const defaultFocusAreas: FocusAreaTag[] = [
  { id: 'composition', label: 'Composition & Layout', icon: DocumentTextIcon },
  { id: 'lighting', label: 'Lighting & Mood' },
  { id: 'colors', label: 'Color Palette' },
  { id: 'subjects', label: 'Main Subjects' },
  { id: 'emotions', label: 'Emotional Impact' },
  { id: 'technique', label: 'Photography Technique' },
  { id: 'setting', label: 'Setting & Environment' },
  { id: 'details', label: 'Important Details' },
];

export const ContextInput: React.FC<ContextInputProps> = ({
  value,
  onChange,
  focusAreas,
  onFocusAreasChange,
  suggestions = [],
  disabled = false,
  className = '',
}) => {
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [showFocusAreas, setShowFocusAreas] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  
  // Debounce the input to avoid excessive onChange calls
  const debouncedOnChange = useDebounce((newValue: string) => {
    onChange(newValue);
  }, 300);

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value;
    debouncedOnChange(newValue);
  }, [debouncedOnChange]);

  const handleFocusAreaToggle = useCallback((areaId: string) => {
    const updatedAreas = focusAreas.includes(areaId)
      ? focusAreas.filter(id => id !== areaId)
      : [...focusAreas, areaId];
    
    onFocusAreasChange(updatedAreas);
  }, [focusAreas, onFocusAreasChange]);

  const applySuggestion = useCallback((suggestion: string) => {
    const currentValue = textareaRef.current?.value || '';
    const newValue = currentValue + (currentValue ? '\n\n' : '') + suggestion;
    
    if (textareaRef.current) {
      textareaRef.current.value = newValue;
      onChange(newValue);
      textareaRef.current.focus();
    }
    setShowSuggestions(false);
  }, [onChange]);

  const clearInput = useCallback(() => {
    if (textareaRef.current) {
      textareaRef.current.value = '';
      onChange('');
      textareaRef.current.focus();
    }
  }, [onChange]);

  // Auto-resize textarea
  const handleTextareaResize = useCallback(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, []);

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <DocumentTextIcon className="w-5 h-5 text-gray-600 dark:text-gray-400" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
            Context & Notes
          </h3>
        </div>
        
        <div className="flex space-x-2">
          {suggestions.length > 0 && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowSuggestions(!showSuggestions)}
              className="text-xs"
            >
              <LightBulbIcon className="w-4 h-4 mr-1" />
              Suggestions
            </Button>
          )}
          
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowFocusAreas(!showFocusAreas)}
            className="text-xs"
          >
            <SparklesIcon className="w-4 h-4 mr-1" />
            Focus Areas
          </Button>
        </div>
      </div>

      {/* Focus Areas */}
      {showFocusAreas && (
        <div className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              What should the AI focus on?
            </span>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowFocusAreas(false)}
              className="p-1"
            >
              <XMarkIcon className="w-4 h-4" />
            </Button>
          </div>
          
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2">
            {defaultFocusAreas.map((area) => {
              const isSelected = focusAreas.includes(area.id);
              const Icon = area.icon;
              
              return (
                <button
                  key={area.id}
                  onClick={() => handleFocusAreaToggle(area.id)}
                  disabled={disabled}
                  className={`p-3 text-left rounded-lg border transition-all duration-200
                           hover:shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500
                           disabled:opacity-50 disabled:cursor-not-allowed
                           ${isSelected
                             ? 'bg-indigo-50 border-indigo-200 text-indigo-700 dark:bg-indigo-900/20 dark:border-indigo-700 dark:text-indigo-300'
                             : 'bg-white border-gray-200 text-gray-600 hover:border-gray-300 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-400'
                           }`}
                >
                  <div className="flex items-center space-x-2">
                    {Icon && <Icon className="w-4 h-4" />}
                    <span className="text-xs font-medium">{area.label}</span>
                  </div>
                </button>
              );
            })}
          </div>
          
          {focusAreas.length > 0 && (
            <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-600">
              <div className="text-xs text-gray-500 dark:text-gray-400 mb-2">
                Selected focus areas:
              </div>
              <div className="flex flex-wrap gap-1">
                {focusAreas.map(areaId => {
                  const area = defaultFocusAreas.find(a => a.id === areaId);
                  if (!area) return null;
                  
                  return (
                    <span
                      key={areaId}
                      className="inline-flex items-center px-2 py-1 rounded-full text-xs
                               bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-300"
                    >
                      {area.label}
                      <button
                        onClick={() => handleFocusAreaToggle(areaId)}
                        className="ml-1 hover:text-indigo-900 dark:hover:text-indigo-100"
                      >
                        <XMarkIcon className="w-3 h-3" />
                      </button>
                    </span>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Suggestions */}
      {showSuggestions && suggestions.length > 0 && (
        <div className="p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-medium text-amber-800 dark:text-amber-200">
              Suggested prompts:
            </span>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowSuggestions(false)}
              className="p-1 text-amber-600 hover:text-amber-800"
            >
              <XMarkIcon className="w-4 h-4" />
            </Button>
          </div>
          
          <div className="space-y-2">
            {suggestions.map((suggestion, index) => (
              <button
                key={index}
                onClick={() => applySuggestion(suggestion)}
                disabled={disabled}
                className="block w-full p-2 text-left text-sm text-amber-700 dark:text-amber-300
                         hover:bg-amber-100 dark:hover:bg-amber-800/30 rounded
                         transition-colors duration-150
                         disabled:opacity-50 disabled:cursor-not-allowed"
              >
                "{suggestion}"
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Main Input */}
      <div className="relative">
        <textarea
          ref={textareaRef}
          defaultValue={value}
          onChange={handleInputChange}
          onInput={handleTextareaResize}
          placeholder="Add any specific notes or context you'd like the AI to consider...\n\nFor example:\n• Focus on the emotional impact\n• Analyze the technical aspects\n• Describe for a beginner audience\n• Emphasize the historical context"
          disabled={disabled}
          className={`w-full min-h-[120px] max-h-[300px] p-4 rounded-lg border
                   border-gray-200 dark:border-gray-700
                   bg-white dark:bg-gray-800
                   text-gray-900 dark:text-gray-100
                   placeholder-gray-500 dark:placeholder-gray-400
                   focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500
                   disabled:opacity-50 disabled:cursor-not-allowed
                   resize-none transition-all duration-200`}
        />
        
        {/* Character counter and clear button */}
        <div className="absolute bottom-3 right-3 flex items-center space-x-2">
          {value.length > 0 && (
            <>
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {value.length}/1000
              </span>
              <Button
                variant="ghost"
                size="sm"
                onClick={clearInput}
                disabled={disabled}
                className="p-1 text-gray-400 hover:text-gray-600"
                aria-label="Clear input"
              >
                <XMarkIcon className="w-4 h-4" />
              </Button>
            </>
          )}
        </div>
      </div>

      {/* Tips */}
      <div className="text-xs text-gray-500 dark:text-gray-400 space-y-1">
        <div className="flex items-center space-x-2">
          <div className="w-1 h-1 bg-indigo-500 rounded-full" />
          <span>Your notes will guide the AI's analysis and description style</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-1 h-1 bg-indigo-500 rounded-full" />
          <span>Be specific about what aspects interest you most</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-1 h-1 bg-indigo-500 rounded-full" />
          <span>Select focus areas to emphasize particular elements</span>
        </div>
      </div>
    </div>
  );
};