import React from 'react';
import { 
  AcademicCapIcon, 
  PaintBrushIcon, 
  CogIcon, 
  ChatBubbleLeftRightIcon,
  SparklesIcon 
} from '@heroicons/react/24/outline';
import { DescriptionStyle } from '../../types';
import { Button } from '../Shared/Button/Button';

interface StyleSelectorProps {
  selectedStyle: DescriptionStyle;
  onStyleChange: (style: DescriptionStyle) => void;
  vocabularyLevel: 1 | 2 | 3 | 4 | 5;
  onVocabularyLevelChange: (level: 1 | 2 | 3 | 4 | 5) => void;
  disabled?: boolean;
}

const styleOptions = [
  {
    value: 'academic' as const,
    label: 'Academic',
    description: 'Scholarly, analytical tone with precise terminology',
    icon: AcademicCapIcon,
    example: 'This photograph demonstrates the principles of compositional balance through...',
  },
  {
    value: 'poetic' as const,
    label: 'Poetic',
    description: 'Lyrical, expressive language with vivid imagery',
    icon: PaintBrushIcon,
    example: 'Golden light dances across the weathered surface, whispering stories of...',
  },
  {
    value: 'technical' as const,
    label: 'Technical',
    description: 'Detailed technical analysis of visual elements',
    icon: CogIcon,
    example: 'Shot at f/2.8 aperture with shallow depth of field, the subject exhibits...',
  },
  {
    value: 'casual' as const,
    label: 'Casual',
    description: 'Conversational, accessible tone for general audiences',
    icon: ChatBubbleLeftRightIcon,
    example: "This is a beautiful shot that really captures the mood. You can see how...",
  },
  {
    value: 'creative' as const,
    label: 'Creative',
    description: 'Imaginative storytelling with emotional depth',
    icon: SparklesIcon,
    example: 'In this moment frozen in time, we witness the silent conversation between...',
  },
] as const;

export const StyleSelector: React.FC<StyleSelectorProps> = ({
  selectedStyle,
  onStyleChange,
  vocabularyLevel,
  onVocabularyLevelChange,
  disabled = false,
}) => {
  
  const vocabularyLevels = [
    { value: 1, label: 'Beginner', description: 'Simple, everyday words' },
    { value: 2, label: 'Elementary', description: 'Basic vocabulary with some descriptive terms' },
    { value: 3, label: 'Intermediate', description: 'Moderate complexity, balanced vocabulary' },
    { value: 4, label: 'Advanced', description: 'Sophisticated terms and concepts' },
    { value: 5, label: 'Expert', description: 'Specialized, technical terminology' },
  ] as const;
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
          Description Style
        </h3>
        <span className="text-sm text-gray-500 dark:text-gray-400">
          Choose your preferred tone
        </span>
      </div>

      {/* Style Options Grid */}
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        {styleOptions.map((style) => {
          const Icon = style.icon;
          const isSelected = selectedStyle === style.value;

          return (
            <button
              key={style.value}
              onClick={() => onStyleChange(style.value)}
              disabled={disabled}
              className={`relative p-4 text-left border rounded-lg transition-all duration-200 
                         hover:shadow-md focus:outline-none focus:ring-2 focus:ring-indigo-500 
                         disabled:opacity-50 disabled:cursor-not-allowed group
                         ${isSelected
                           ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20 dark:border-indigo-400'
                           : 'border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:border-gray-300 dark:hover:border-gray-600'
                         }`}
            >
              {/* Selection indicator */}
              {isSelected && (
                <div className="absolute -top-2 -right-2 w-5 h-5 bg-indigo-500 rounded-full flex items-center justify-center">
                  <div className="w-2 h-2 bg-white rounded-full" />
                </div>
              )}

              <div className="flex items-start space-x-3">
                <div className={`p-2 rounded-lg ${
                  isSelected 
                    ? 'bg-indigo-100 dark:bg-indigo-800/50' 
                    : 'bg-gray-100 dark:bg-gray-700 group-hover:bg-gray-200 dark:group-hover:bg-gray-600'
                }`}>
                  <Icon className={`w-5 h-5 ${
                    isSelected 
                      ? 'text-indigo-600 dark:text-indigo-400' 
                      : 'text-gray-600 dark:text-gray-400'
                  }`} />
                </div>

                <div className="flex-1 min-w-0">
                  <div className={`font-medium text-sm ${
                    isSelected 
                      ? 'text-indigo-900 dark:text-indigo-100' 
                      : 'text-gray-900 dark:text-gray-100'
                  }`}>
                    {style.label}
                  </div>
                  <div className={`text-xs mt-1 line-clamp-2 ${
                    isSelected 
                      ? 'text-indigo-700 dark:text-indigo-300' 
                      : 'text-gray-600 dark:text-gray-400'
                  }`}>
                    {style.description}
                  </div>
                </div>
              </div>
            </button>
          );
        })}
      </div>

      {/* Selected style preview */}
      {selectedStyle && (
        <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-lg">
          <div className="text-sm text-gray-600 dark:text-gray-400 mb-2 font-medium">
            Example output:
          </div>
          <div className="text-sm text-gray-800 dark:text-gray-200 italic leading-relaxed">
            "{styleOptions.find(s => s.value === selectedStyle)?.example}"
          </div>
        </div>
      )}

      {/* Vocabulary Level Selector */}
      <div className="mt-6 space-y-4">
        <div className="flex items-center justify-between">
          <h4 className="text-md font-medium text-gray-900 dark:text-gray-100">
            Vocabulary Level
          </h4>
          <span className="text-sm text-gray-500 dark:text-gray-400">
            Difficulty: {vocabularyLevel}/5
          </span>
        </div>
        
        {/* Level slider */}
        <div className="space-y-3">
          <input
            type="range"
            min={1}
            max={5}
            value={vocabularyLevel}
            onChange={(e) => onVocabularyLevelChange(Number(e.target.value) as 1 | 2 | 3 | 4 | 5)}
            disabled={disabled}
            className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer
                     slider:bg-indigo-600 slider:rounded-lg
                     disabled:opacity-50 disabled:cursor-not-allowed"
          />
          
          <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400">
            <span>Simple</span>
            <span>Moderate</span>
            <span>Advanced</span>
          </div>
          
          {/* Current level description */}
          <div className="p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {vocabularyLevels.find(l => l.value === vocabularyLevel)?.label}
            </div>
            <div className="text-xs text-gray-600 dark:text-gray-400">
              {vocabularyLevels.find(l => l.value === vocabularyLevel)?.description}
            </div>
          </div>
        </div>
      </div>
      
      {/* Quick style tips */}
      <div className="mt-6 text-xs text-gray-500 dark:text-gray-400 space-y-1">
        <div className="flex items-center space-x-2">
          <div className="w-1 h-1 bg-indigo-500 rounded-full" />
          <span>Academic: Best for educational content and analysis</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-1 h-1 bg-indigo-500 rounded-full" />
          <span>Poetic: Perfect for artistic and creative projects</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-1 h-1 bg-indigo-500 rounded-full" />
          <span>Technical: Ideal for professional photography analysis</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-1 h-1 bg-indigo-500 rounded-full" />
          <span>Vocabulary level affects word complexity and descriptions</span>
        </div>
      </div>
    </div>
  );
};