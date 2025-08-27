import React, { useState, useCallback } from 'react';
import { 
  Edit, 
  Trash2, 
  Volume2, 
  Play, 
  Star, 
  Clock, 
  Tag, 
  Image, 
  MoreVertical,
  CheckCircle,
  AlertCircle,
  BookOpen,
  Brain
} from 'lucide-react';
import { VocabularyItem, MasteryLevel } from '../../types';
import { useVocabulary } from '../../hooks/useVocabulary';
import { Button } from '../Shared/Button/Button';
import { Card } from '../Shared/Card/Card';

interface VocabularyItemProps {
  item: VocabularyItem;
  compactMode?: boolean;
  isSelected?: boolean;
  onSelect?: () => void;
  showSelection?: boolean;
  onEdit?: (item: VocabularyItem) => void;
}

export function VocabularyItem({
  item,
  compactMode = false,
  isSelected = false,
  onSelect,
  showSelection = false,
  onEdit
}: VocabularyItemProps) {
  const { updateVocabularyItem, deleteVocabularyItem } = useVocabulary();
  const [isEditing, setIsEditing] = useState(false);
  const [showExamples, setShowExamples] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [showActionsMenu, setShowActionsMenu] = useState(false);

  // Get mastery level styling
  const getMasteryLevelStyle = (level: MasteryLevel) => {
    switch (level) {
      case MasteryLevel.NEW:
        return 'bg-gray-100 text-gray-700 border-gray-200';
      case MasteryLevel.LEARNING:
        return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      case MasteryLevel.REVIEW:
        return 'bg-blue-100 text-blue-700 border-blue-200';
      case MasteryLevel.MASTERED:
        return 'bg-green-100 text-green-700 border-green-200';
      default:
        return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  // Get mastery level icon
  const getMasteryLevelIcon = (level: MasteryLevel) => {
    switch (level) {
      case MasteryLevel.NEW:
        return <AlertCircle className="w-3 h-3" />;
      case MasteryLevel.LEARNING:
        return <BookOpen className="w-3 h-3" />;
      case MasteryLevel.REVIEW:
        return <Clock className="w-3 h-3" />;
      case MasteryLevel.MASTERED:
        return <CheckCircle className="w-3 h-3" />;
      default:
        return <AlertCircle className="w-3 h-3" />;
    }
  };

  // Calculate accuracy percentage
  const accuracy = item.timesReviewed > 0 
    ? Math.round((item.timesCorrect / item.timesReviewed) * 100)
    : 0;

  // Handle text-to-speech
  const handlePlayAudio = useCallback(async () => {
    if (!('speechSynthesis' in window)) {
      alert('Text-to-speech is not supported in your browser');
      return;
    }

    if (isPlaying) {
      speechSynthesis.cancel();
      setIsPlaying(false);
      return;
    }

    setIsPlaying(true);
    
    const utterance = new SpeechSynthesisUtterance(item.word);
    utterance.lang = 'es-ES'; // Spanish
    utterance.rate = 0.8;
    utterance.pitch = 1;
    
    utterance.onend = () => setIsPlaying(false);
    utterance.onerror = () => setIsPlaying(false);
    
    speechSynthesis.speak(utterance);
  }, [item.word, isPlaying]);

  // Handle mastery level change
  const handleMasteryLevelChange = useCallback(async (newLevel: MasteryLevel) => {
    await updateVocabularyItem(item.id, { masteryLevel: newLevel });
    setShowActionsMenu(false);
  }, [item.id, updateVocabularyItem]);

  // Handle delete
  const handleDelete = useCallback(async () => {
    if (confirm(`Are you sure you want to delete "${item.word}"?`)) {
      await deleteVocabularyItem(item.id);
    }
    setShowActionsMenu(false);
  }, [item.id, item.word, deleteVocabularyItem]);

  // Handle difficulty adjustment
  const handleDifficultyChange = useCallback(async (newDifficulty: number) => {
    await updateVocabularyItem(item.id, { difficulty: newDifficulty });
  }, [item.id, updateVocabularyItem]);

  // Format time remaining until next review
  const formatNextReview = () => {
    if (!item.nextReviewAt) return 'Not scheduled';
    
    const now = new Date();
    const nextReview = new Date(item.nextReviewAt);
    const diffMs = nextReview.getTime() - now.getTime();
    
    if (diffMs < 0) return 'Overdue';
    
    const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24));
    if (diffDays === 1) return 'Tomorrow';
    if (diffDays < 7) return `${diffDays} days`;
    if (diffDays < 30) return `${Math.ceil(diffDays / 7)} weeks`;
    return `${Math.ceil(diffDays / 30)} months`;
  };

  if (compactMode) {
    return (
      <Card className={`p-3 hover:shadow-md transition-all duration-200 ${isSelected ? 'ring-2 ring-blue-500 bg-blue-50' : ''}`}>
        <div className="flex items-center justify-between">
          {showSelection && (
            <input
              type="checkbox"
              checked={isSelected}
              onChange={onSelect}
              className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
            />
          )}
          
          <div className="flex-1 min-w-0 mx-3">
            <div className="flex items-center gap-2">
              <span className="font-medium text-gray-900 truncate">{item.word}</span>
              <span className="text-gray-500 text-sm truncate">→ {item.translation}</span>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <div className={`inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded-full border ${getMasteryLevelStyle(item.masteryLevel)}`}>
              {getMasteryLevelIcon(item.masteryLevel)}
              {item.masteryLevel}
            </div>
            
            <Button
              variant="ghost"
              size="sm"
              onClick={handlePlayAudio}
              disabled={isPlaying}
            >
              {isPlaying ? <Play className="w-4 h-4 animate-pulse" /> : <Volume2 className="w-4 h-4" />}
            </Button>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <Card className={`overflow-hidden hover:shadow-lg transition-all duration-200 ${isSelected ? 'ring-2 ring-blue-500 bg-blue-50' : ''}`}>
      {/* Header */}
      <div className="p-4 pb-2">
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-3 flex-1">
            {showSelection && (
              <input
                type="checkbox"
                checked={isSelected}
                onChange={onSelect}
                className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 mt-1"
              />
            )}
            
            {/* Image preview */}
            {item.imageUrl && (
              <div className="w-16 h-16 rounded-lg overflow-hidden bg-gray-100 flex-shrink-0">
                <img
                  src={item.imageUrl}
                  alt={`Context for ${item.word}`}
                  className="w-full h-full object-cover"
                  loading="lazy"
                />
              </div>
            )}
            
            <div className="flex-1 min-w-0">
              {/* Word and translation */}
              <div className="flex items-center gap-3 mb-2">
                <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                  {item.word}
                </h3>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handlePlayAudio}
                  disabled={isPlaying}
                  className="p-1"
                >
                  {isPlaying ? 
                    <Play className="w-4 h-4 text-blue-500 animate-pulse" /> : 
                    <Volume2 className="w-4 h-4 text-gray-500 hover:text-blue-500" />
                  }
                </Button>
              </div>
              
              <p className="text-gray-700 dark:text-gray-300 mb-2">
                {item.translation}
              </p>
              
              {/* Context */}
              {item.context && (
                <p className="text-sm text-gray-600 dark:text-gray-400 italic mb-2">
                  "{item.context}"
                </p>
              )}
              
              {/* Notes */}
              {item.notes && (
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  {item.notes}
                </p>
              )}
            </div>
          </div>
          
          {/* Actions menu */}
          <div className="relative">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowActionsMenu(!showActionsMenu)}
              className="p-1"
            >
              <MoreVertical className="w-4 h-4" />
            </Button>
            
            {showActionsMenu && (
              <div className="absolute right-0 top-8 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-10">
                <div className="py-1">
                  <button
                    onClick={() => {
                      onEdit?.(item);
                      setShowActionsMenu(false);
                    }}
                    className="flex items-center gap-2 w-full px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    <Edit className="w-4 h-4" />
                    Edit
                  </button>
                  
                  <div className="border-t border-gray-200 dark:border-gray-600 my-1"></div>
                  
                  <div className="px-3 py-1 text-xs font-medium text-gray-500 uppercase tracking-wide">
                    Mastery Level
                  </div>
                  
                  {Object.values(MasteryLevel).map(level => (
                    <button
                      key={level}
                      onClick={() => handleMasteryLevelChange(level)}
                      className={`flex items-center gap-2 w-full px-3 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700 ${
                        item.masteryLevel === level ? 'bg-blue-50 text-blue-700' : 'text-gray-700 dark:text-gray-300'
                      }`}
                    >
                      {getMasteryLevelIcon(level)}
                      {level}
                    </button>
                  ))}
                  
                  <div className="border-t border-gray-200 dark:border-gray-600 my-1"></div>
                  
                  <button
                    onClick={handleDelete}
                    className="flex items-center gap-2 w-full px-3 py-2 text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-900"
                  >
                    <Trash2 className="w-4 h-4" />
                    Delete
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Tags */}
      {item.tags.length > 0 && (
        <div className="px-4 pb-2">
          <div className="flex flex-wrap gap-1">
            {item.tags.map((tag, index) => (
              <span
                key={index}
                className="inline-flex items-center gap-1 px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded-full dark:bg-gray-700 dark:text-gray-400"
              >
                <Tag className="w-3 h-3" />
                {tag}
              </span>
            ))}
          </div>
        </div>
      )}
      
      {/* Examples */}
      {item.examples.length > 0 && (
        <div className="px-4 pb-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowExamples(!showExamples)}
            className="text-sm text-blue-600 hover:text-blue-700"
          >
            {showExamples ? 'Hide' : 'Show'} examples ({item.examples.length})
          </Button>
          
          {showExamples && (
            <div className="mt-2 space-y-2">
              {item.examples.map((example) => (
                <div key={example.id} className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3">
                  <p className="text-sm text-gray-700 dark:text-gray-300 mb-1">
                    {example.sentence}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {example.translation}
                  </p>
                  {example.source && (
                    <p className="text-xs text-gray-400 mt-1">
                      Source: {example.source}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
      
      {/* Footer with stats */}
      <div className="bg-gray-50 dark:bg-gray-800 px-4 py-3">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center gap-4">
            {/* Mastery Level */}
            <div className={`inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded-full border ${getMasteryLevelStyle(item.masteryLevel)}`}>
              {getMasteryLevelIcon(item.masteryLevel)}
              {item.masteryLevel}
            </div>
            
            {/* Category */}
            {item.category && (
              <span className="text-gray-600 dark:text-gray-400">
                {item.category}
              </span>
            )}
            
            {/* Difficulty */}
            <div className="flex items-center gap-1">
              <Brain className="w-3 h-3 text-gray-500" />
              <span className="text-gray-600 dark:text-gray-400">
                Level {item.difficulty}
              </span>
            </div>
          </div>
          
          <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
            {/* Review stats */}
            <span>
              {item.timesReviewed} reviews
            </span>
            
            {/* Accuracy */}
            <span className={accuracy >= 80 ? 'text-green-600' : accuracy >= 60 ? 'text-yellow-600' : 'text-red-600'}>
              {accuracy}% accuracy
            </span>
            
            {/* Streak */}
            {item.streak > 0 && (
              <span className="text-orange-600">
                🔥 {item.streak} streak
              </span>
            )}
            
            {/* Next review */}
            <span>
              Next: {formatNextReview()}
            </span>
            
            {/* Added date */}
            <span>
              Added {new Date(item.createdAt).toLocaleDateString()}
            </span>
          </div>
        </div>
      </div>
    </Card>
  );
}