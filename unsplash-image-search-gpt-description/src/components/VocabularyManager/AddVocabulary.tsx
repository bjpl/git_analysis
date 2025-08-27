import React, { useState, useCallback } from 'react';
import { Plus, X, Save, Loader, Image as ImageIcon, Tag, BookOpen } from 'lucide-react';
import { VocabularyItem, MasteryLevel, VocabularyExample } from '../../types';
import { useVocabulary } from '../../hooks/useVocabulary';
import { useImageSearch } from '../../hooks/useImageSearch';
import { useAIGeneration } from '../../hooks/useAIGeneration';
import { Button } from '../Shared/Button/Button';
import { Card } from '../Shared/Card/Card';

interface AddVocabularyProps {
  onClose: () => void;
  initialData?: Partial<VocabularyItem>;
  mode?: 'add' | 'edit';
}

export function AddVocabulary({ 
  onClose, 
  initialData,
  mode = 'add' 
}: AddVocabularyProps) {
  const { addVocabularyItem, updateVocabularyItem, isCreating } = useVocabulary();
  const { search: searchImages, images, isLoading: isSearchingImages } = useImageSearch();
  const { generate: generateTranslation, isGenerating } = useAIGeneration();

  // Form state
  const [formData, setFormData] = useState({
    word: initialData?.word || '',
    translation: initialData?.translation || '',
    context: initialData?.context || '',
    notes: initialData?.notes || '',
    category: initialData?.category || '',
    difficulty: initialData?.difficulty || 5,
    masteryLevel: initialData?.masteryLevel || MasteryLevel.NEW,
    tags: initialData?.tags || [],
    imageUrl: initialData?.imageUrl || '',
    searchQuery: initialData?.searchQuery || '',
  });

  const [examples, setExamples] = useState<VocabularyExample[]>(
    initialData?.examples || []
  );
  const [newExample, setNewExample] = useState({
    sentence: '',
    translation: '',
    source: ''
  });
  const [tagInput, setTagInput] = useState('');
  const [showImageSearch, setShowImageSearch] = useState(false);
  const [showExampleForm, setShowExampleForm] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Validation
  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    
    if (!formData.word.trim()) {
      newErrors.word = 'Word is required';
    }
    
    if (!formData.translation.trim()) {
      newErrors.translation = 'Translation is required';
    }
    
    if (formData.difficulty < 1 || formData.difficulty > 10) {
      newErrors.difficulty = 'Difficulty must be between 1 and 10';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle form submission
  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    try {
      const vocabularyItem: Omit<VocabularyItem, 'id' | 'createdAt' | 'updatedAt'> = {
        word: formData.word.trim(),
        translation: formData.translation.trim(),
        context: formData.context.trim() || undefined,
        notes: formData.notes.trim() || undefined,
        category: formData.category.trim() || undefined,
        difficulty: formData.difficulty,
        masteryLevel: formData.masteryLevel,
        tags: formData.tags,
        imageUrl: formData.imageUrl.trim() || undefined,
        searchQuery: formData.searchQuery.trim() || undefined,
        examples,
        
        // Initialize learning data
        timesReviewed: initialData?.timesReviewed || 0,
        timesCorrect: initialData?.timesCorrect || 0,
        streak: initialData?.streak || 0,
        ease: initialData?.ease || 2.5,
        interval: initialData?.interval || 1,
        lastReviewedAt: initialData?.lastReviewedAt,
        nextReviewAt: initialData?.nextReviewAt,
        userId: initialData?.userId,
        isPublic: initialData?.isPublic || false,
        sharedFromUserId: initialData?.sharedFromUserId
      };

      if (mode === 'edit' && initialData?.id) {
        await updateVocabularyItem(initialData.id, vocabularyItem);
      } else {
        await addVocabularyItem(vocabularyItem);
      }
      
      onClose();
    } catch (error) {
      console.error('Failed to save vocabulary item:', error);
    }
  }, [formData, examples, mode, initialData, addVocabularyItem, updateVocabularyItem, onClose]);

  // Handle auto-translation
  const handleAutoTranslate = useCallback(async () => {
    if (!formData.word.trim()) return;
    
    try {
      const translation = await generateTranslation(formData.word, 'translate');
      setFormData(prev => ({ ...prev, translation }));
    } catch (error) {
      console.error('Auto-translation failed:', error);
    }
  }, [formData.word, generateTranslation]);

  // Handle image selection
  const handleImageSelect = useCallback((imageUrl: string, searchQuery: string) => {
    setFormData(prev => ({
      ...prev,
      imageUrl,
      searchQuery
    }));
    setShowImageSearch(false);
  }, []);

  // Handle tag addition
  const handleAddTag = useCallback(() => {
    const tag = tagInput.trim();
    if (tag && !formData.tags.includes(tag)) {
      setFormData(prev => ({
        ...prev,
        tags: [...prev.tags, tag]
      }));
      setTagInput('');
    }
  }, [tagInput, formData.tags]);

  // Handle tag removal
  const handleRemoveTag = useCallback((tagToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }));
  }, []);

  // Handle example addition
  const handleAddExample = useCallback(() => {
    if (!newExample.sentence.trim() || !newExample.translation.trim()) return;
    
    const example: VocabularyExample = {
      id: `example-${Date.now()}`,
      sentence: newExample.sentence.trim(),
      translation: newExample.translation.trim(),
      source: newExample.source.trim() || undefined
    };
    
    setExamples(prev => [...prev, example]);
    setNewExample({ sentence: '', translation: '', source: '' });
    setShowExampleForm(false);
  }, [newExample]);

  // Handle example removal
  const handleRemoveExample = useCallback((exampleId: string) => {
    setExamples(prev => prev.filter(ex => ex.id !== exampleId));
  }, []);

  return (
    <div className="max-w-2xl mx-auto">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Information */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <BookOpen className="w-5 h-5" />
            Basic Information
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Word */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Word (Spanish) *
              </label>
              <input
                type="text"
                value={formData.word}
                onChange={(e) => setFormData(prev => ({ ...prev, word: e.target.value }))}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-600 dark:text-white ${
                  errors.word ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="Enter Spanish word"
                autoComplete="off"
              />
              {errors.word && (
                <p className="text-red-500 text-xs mt-1">{errors.word}</p>
              )}
            </div>
            
            {/* Translation */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Translation (English) *
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={formData.translation}
                  onChange={(e) => setFormData(prev => ({ ...prev, translation: e.target.value }))}
                  className={`flex-1 px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-600 dark:text-white ${
                    errors.translation ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="Enter English translation"
                />
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={handleAutoTranslate}
                  disabled={!formData.word.trim() || isGenerating}
                >
                  {isGenerating ? <Loader className="w-4 h-4 animate-spin" /> : 'Auto'}
                </Button>
              </div>
              {errors.translation && (
                <p className="text-red-500 text-xs mt-1">{errors.translation}</p>
              )}
            </div>
          </div>
          
          {/* Context */}
          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Context
            </label>
            <input
              type="text"
              value={formData.context}
              onChange={(e) => setFormData(prev => ({ ...prev, context: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-600 dark:text-white"
              placeholder="Example sentence or context where this word appears"
            />
          </div>
          
          {/* Notes */}
          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Notes
            </label>
            <textarea
              value={formData.notes}
              onChange={(e) => setFormData(prev => ({ ...prev, notes: e.target.value }))}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-600 dark:text-white"
              placeholder="Additional notes, mnemonics, or related information"
            />
          </div>
        </Card>

        {/* Learning Settings */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Learning Settings</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Category */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Category
              </label>
              <select
                value={formData.category}
                onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-600 dark:text-white"
              >
                <option value="">Select category</option>
                <option value="Nouns">Nouns</option>
                <option value="Verbs">Verbs</option>
                <option value="Adjectives">Adjectives</option>
                <option value="Adverbs">Adverbs</option>
                <option value="Phrases">Phrases</option>
                <option value="Grammar">Grammar</option>
                <option value="Other">Other</option>
              </select>
            </div>
            
            {/* Difficulty */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Difficulty (1-10)
              </label>
              <input
                type="range"
                min="1"
                max="10"
                value={formData.difficulty}
                onChange={(e) => setFormData(prev => ({ ...prev, difficulty: parseInt(e.target.value) }))}
                className="w-full"
              />
              <div className="text-center text-sm text-gray-600 dark:text-gray-400">
                {formData.difficulty}
              </div>
              {errors.difficulty && (
                <p className="text-red-500 text-xs mt-1">{errors.difficulty}</p>
              )}
            </div>
            
            {/* Mastery Level */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Mastery Level
              </label>
              <select
                value={formData.masteryLevel}
                onChange={(e) => setFormData(prev => ({ ...prev, masteryLevel: e.target.value as MasteryLevel }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-600 dark:text-white"
              >
                <option value={MasteryLevel.NEW}>New</option>
                <option value={MasteryLevel.LEARNING}>Learning</option>
                <option value={MasteryLevel.REVIEW}>Review</option>
                <option value={MasteryLevel.MASTERED}>Mastered</option>
              </select>
            </div>
          </div>
        </Card>

        {/* Tags */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Tag className="w-5 h-5" />
            Tags
          </h3>
          
          <div className="flex gap-2 mb-3">
            <input
              type="text"
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddTag())}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-600 dark:text-white"
              placeholder="Add a tag"
            />
            <Button
              type="button"
              variant="outline"
              onClick={handleAddTag}
              disabled={!tagInput.trim()}
            >
              <Plus className="w-4 h-4" />
            </Button>
          </div>
          
          <div className="flex flex-wrap gap-2">
            {formData.tags.map((tag, index) => (
              <span
                key={index}
                className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-sm dark:bg-blue-900 dark:text-blue-300"
              >
                {tag}
                <button
                  type="button"
                  onClick={() => handleRemoveTag(tag)}
                  className="hover:text-blue-600 dark:hover:text-blue-400"
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            ))}
          </div>
        </Card>

        {/* Image */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <ImageIcon className="w-5 h-5" />
            Associated Image
          </h3>
          
          {formData.imageUrl ? (
            <div className="flex items-start gap-4">
              <img
                src={formData.imageUrl}
                alt="Associated with vocabulary"
                className="w-24 h-24 object-cover rounded-lg"
              />
              <div className="flex-1">
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  {formData.searchQuery && `From search: "${formData.searchQuery}"`}
                </p>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setFormData(prev => ({ ...prev, imageUrl: '', searchQuery: '' }))}
                >
                  Remove Image
                </Button>
              </div>
            </div>
          ) : (
            <Button
              type="button"
              variant="outline"
              onClick={() => setShowImageSearch(true)}
            >
              <ImageIcon className="w-4 h-4 mr-2" />
              Add Image
            </Button>
          )}
        </Card>

        {/* Examples */}
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Example Sentences</h3>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => setShowExampleForm(!showExampleForm)}
            >
              <Plus className="w-4 h-4 mr-1" />
              Add Example
            </Button>
          </div>
          
          {showExampleForm && (
            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 mb-4">
              <div className="space-y-3">
                <input
                  type="text"
                  placeholder="Example sentence in Spanish"
                  value={newExample.sentence}
                  onChange={(e) => setNewExample(prev => ({ ...prev, sentence: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                />
                <input
                  type="text"
                  placeholder="English translation"
                  value={newExample.translation}
                  onChange={(e) => setNewExample(prev => ({ ...prev, translation: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                />
                <input
                  type="text"
                  placeholder="Source (optional)"
                  value={newExample.source}
                  onChange={(e) => setNewExample(prev => ({ ...prev, source: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                />
                <div className="flex gap-2">
                  <Button
                    type="button"
                    variant="primary"
                    size="sm"
                    onClick={handleAddExample}
                    disabled={!newExample.sentence.trim() || !newExample.translation.trim()}
                  >
                    Add
                  </Button>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      setShowExampleForm(false);
                      setNewExample({ sentence: '', translation: '', source: '' });
                    }}
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            </div>
          )}
          
          <div className="space-y-3">
            {examples.map((example) => (
              <div key={example.id} className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
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
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => handleRemoveExample(example.id)}
                    className="text-red-500 hover:text-red-700 p-1"
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Action Buttons */}
        <div className="flex justify-end gap-3">
          <Button
            type="button"
            variant="outline"
            onClick={onClose}
            disabled={isCreating}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            variant="primary"
            disabled={isCreating}
          >
            {isCreating ? (
              <>
                <Loader className="w-4 h-4 mr-2 animate-spin" />
                {mode === 'edit' ? 'Updating...' : 'Adding...'}
              </>
            ) : (
              <>
                <Save className="w-4 h-4 mr-2" />
                {mode === 'edit' ? 'Update Word' : 'Add Word'}
              </>
            )}
          </Button>
        </div>
      </form>
    </div>
  );
}