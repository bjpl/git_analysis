import React, { useState, useCallback, useEffect, useMemo } from 'react';
import { 
  XMarkIcon, 
  SparklesIcon, 
  ArrowPathIcon,
  SpeakerWaveIcon,
  DocumentArrowDownIcon,
  ClipboardIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';
import { Image, DescriptionStyle } from '../../types';
import { Button } from '../Shared/Button/Button';
import toast from 'react-hot-toast';

interface EnhancedDescriptionPanelProps {
  image: Image | null;
  onClose: () => void;
  isOpen: boolean;
  className?: string;
}

export const EnhancedDescriptionPanel: React.FC<EnhancedDescriptionPanelProps> = ({
  image,
  onClose,
  isOpen,
  className = '',
}) => {
  const [selectedStyle, setSelectedStyle] = useState<DescriptionStyle>('academic');
  const [description, setDescription] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);

  const handleGenerate = useCallback(async () => {
    if (!image) return;
    
    setIsGenerating(true);
    try {
      // Simulate AI generation
      await new Promise(resolve => setTimeout(resolve, 2000));
      setDescription(`This beautiful image captures the essence of ${image.alt_description || 'the scene'}. The composition demonstrates excellent use of light and shadow, creating a compelling visual narrative that draws the viewer's attention to the key elements within the frame.`);
    } catch (error) {
      toast.error('Failed to generate description');
    } finally {
      setIsGenerating(false);
    }
  }, [image]);

  const handleCopyToClipboard = useCallback(() => {
    if (!description) return;
    
    navigator.clipboard.writeText(description).then(() => {
      toast.success('Description copied to clipboard');
    }).catch(() => {
      toast.error('Failed to copy to clipboard');
    });
  }, [description]);

  useEffect(() => {
    if (image && isOpen) {
      handleGenerate();
    }
  }, [image?.id, isOpen, handleGenerate]);

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
      <div className="absolute right-0 top-0 h-full w-full max-w-4xl bg-white dark:bg-gray-900 shadow-2xl">
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center space-x-3">
              <SparklesIcon className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
              <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                AI Description Generator
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
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Left Column: Image */}
              <div className="space-y-4">
                <div className="relative aspect-video rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-800">
                  <img
                    src={image.urls.regular}
                    alt={image.alt_description || 'Selected image'}
                    className="w-full h-full object-cover"
                    loading="lazy"
                  />
                </div>
              </div>

              {/* Right Column: Description */}
              <div className="space-y-4">
                <div className="flex space-x-3">
                  <Button
                    onClick={handleGenerate}
                    disabled={isGenerating}
                    loading={isGenerating}
                    className="flex-1"
                  >
                    {isGenerating ? 'Generating...' : 'Generate Description'}
                  </Button>
                  
                  {description && !isGenerating && (
                    <Button
                      variant="outline"
                      onClick={handleCopyToClipboard}
                      className="px-4"
                      aria-label="Copy to clipboard"
                    >
                      <ClipboardIcon className="w-4 h-4" />
                    </Button>
                  )}
                </div>

                {(description || isGenerating) && (
                  <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-4 min-h-[200px]">
                    {isGenerating ? (
                      <div className="flex items-center justify-center h-32">
                        <div className="animate-spin rounded-full h-8 w-8 border-2 border-indigo-600 border-t-transparent" />
                      </div>
                    ) : (
                      <p className="text-gray-900 dark:text-gray-100 leading-relaxed">
                        {description}
                      </p>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};