import React, { useState, useCallback, useEffect } from 'react';
import {
  AcademicCapIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  FireIcon,
  ChartBarIcon,
  PlayIcon,
  PauseIcon,
  ForwardIcon,
} from '@heroicons/react/24/outline';
import { Button } from '../Shared/Button/Button';
import { useSpacedRepetition } from '../../hooks/useSpacedRepetition';
import { VocabularyWord } from '../../types';

interface SpacedRepetitionQuizProps {
  onClose: () => void;
  isOpen: boolean;
  className?: string;
}

interface QuizCard {
  word: VocabularyWord;
  showAnswer: boolean;
}

const qualityLabels = {
  0: { label: "Blackout", description: "Complete blackout", color: "bg-red-600" },
  1: { label: "Incorrect", description: "Incorrect response", color: "bg-red-500" },
  2: { label: "Difficult", description: "Correct but very difficult", color: "bg-orange-500" },
  3: { label: "Hesitant", description: "Correct with some hesitation", color: "bg-yellow-500" },
  4: { label: "Easy", description: "Correct with little hesitation", color: "bg-green-500" },
  5: { label: "Perfect", description: "Perfect response", color: "bg-green-600" },
};

export const SpacedRepetitionQuiz: React.FC<SpacedRepetitionQuizProps> = ({
  onClose,
  isOpen,
  className = '',
}) => {
  const [showAnswer, setShowAnswer] = useState(false);
  const [sessionStarted, setSessionStarted] = useState(false);
  const [cardLimit, setCardLimit] = useState(20);
  
  const {
    currentSession,
    currentCard,
    cardsRemaining,
    sessionProgress,
    dueCount,
    newCount,
    reviewedToday,
    accuracy,
    streak,
    startReviewSession,
    submitReview,
    endSession,
    isLoading,
    error,
  } = useSpacedRepetition();

  const handleStartSession = useCallback(async () => {
    try {
      await startReviewSession(cardLimit);
      setSessionStarted(true);
      setShowAnswer(false);
    } catch (error) {
      console.error('Failed to start session:', error);
    }
  }, [startReviewSession, cardLimit]);

  const handleShowAnswer = useCallback(() => {
    setShowAnswer(true);
  }, []);

  const handleQualitySubmit = useCallback(async (quality: 0 | 1 | 2 | 3 | 4 | 5) => {
    try {
      await submitReview(quality);
      setShowAnswer(false);
      
      // End session if no more cards
      if (cardsRemaining <= 1) {
        setSessionStarted(false);
      }
    } catch (error) {
      console.error('Failed to submit review:', error);
    }
  }, [submitReview, cardsRemaining]);

  const handleEndSession = useCallback(async () => {
    try {
      await endSession();
      setSessionStarted(false);
      setShowAnswer(false);
    } catch (error) {
      console.error('Failed to end session:', error);
    }
  }, [endSession]);

  // Reset state when quiz closes
  useEffect(() => {
    if (!isOpen) {
      setSessionStarted(false);
      setShowAnswer(false);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  if (isLoading) {
    return (
      <div className={`fixed inset-0 z-50 overflow-hidden ${className}`}>
        <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" />
        <div className="absolute inset-4 bg-white dark:bg-gray-900 rounded-lg flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto mb-4" />
            <div className="text-gray-600 dark:text-gray-400">Loading spaced repetition data...</div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`fixed inset-0 z-50 overflow-hidden ${className}`}>
        <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" />
        <div className="absolute inset-4 bg-white dark:bg-gray-900 rounded-lg flex items-center justify-center">
          <div className="text-center">
            <XCircleIcon className="w-12 h-12 text-red-500 mx-auto mb-4" />
            <div className="text-red-600 dark:text-red-400 mb-4">{error.message}</div>
            <Button onClick={onClose}>Close</Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`fixed inset-0 z-50 overflow-hidden ${className}`}>
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
        aria-hidden="true"
      />
      
      {/* Quiz Panel */}
      <div className="absolute inset-4 bg-white dark:bg-gray-900 rounded-lg shadow-2xl overflow-hidden">
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="bg-gradient-to-r from-indigo-600 to-purple-600 px-6 py-4 text-white">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <AcademicCapIcon className="w-6 h-6" />
                <h2 className="text-xl font-semibold">
                  {sessionStarted ? 'Spaced Repetition Quiz' : 'Review Session'}
                </h2>
              </div>
              <Button variant="ghost" onClick={onClose} className="text-white hover:text-gray-200">
                ×
              </Button>
            </div>
            
            {/* Progress bar for active session */}
            {sessionStarted && currentSession && (
              <div className="mt-4">
                <div className="flex justify-between text-sm mb-2">
                  <span>{currentSession.cards_completed} / {currentSession.total_cards}</span>
                  <span>{Math.round(sessionProgress)}% complete</span>
                </div>
                <div className="w-full bg-white/20 rounded-full h-2">
                  <div 
                    className="bg-white rounded-full h-2 transition-all duration-300"
                    style={{ width: `${sessionProgress}%` }}
                  />
                </div>
              </div>
            )}
          </div>

          {/* Content */}
          <div className="flex-1 p-6 overflow-y-auto">
            {!sessionStarted ? (
              /* Session Setup */
              <div className="max-w-2xl mx-auto space-y-6">
                {/* Statistics */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 text-center">
                    <ClockIcon className="w-6 h-6 text-blue-600 mx-auto mb-2" />
                    <div className="text-2xl font-bold text-blue-600">{dueCount}</div>
                    <div className="text-sm text-blue-600/80">Due</div>
                  </div>
                  
                  <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4 text-center">
                    <AcademicCapIcon className="w-6 h-6 text-green-600 mx-auto mb-2" />
                    <div className="text-2xl font-bold text-green-600">{newCount}</div>
                    <div className="text-sm text-green-600/80">New</div>
                  </div>
                  
                  <div className="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4 text-center">
                    <CheckCircleIcon className="w-6 h-6 text-purple-600 mx-auto mb-2" />
                    <div className="text-2xl font-bold text-purple-600">{reviewedToday}</div>
                    <div className="text-sm text-purple-600/80">Today</div>
                  </div>
                  
                  <div className="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4 text-center">
                    <FireIcon className="w-6 h-6 text-orange-600 mx-auto mb-2" />
                    <div className="text-2xl font-bold text-orange-600">{streak}</div>
                    <div className="text-sm text-orange-600/80">Streak</div>
                  </div>
                </div>

                {/* Accuracy Chart */}
                {accuracy > 0 && (
                  <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
                    <div className="flex items-center space-x-2 mb-2">
                      <ChartBarIcon className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                      <span className="font-medium text-gray-900 dark:text-gray-100">Today's Accuracy</span>
                    </div>
                    <div className="flex items-center space-x-4">
                      <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-4">
                        <div 
                          className="bg-gradient-to-r from-green-500 to-blue-500 h-4 rounded-full transition-all duration-500"
                          style={{ width: `${accuracy}%` }}
                        />
                      </div>
                      <span className="text-lg font-bold text-gray-900 dark:text-gray-100">
                        {Math.round(accuracy)}%
                      </span>
                    </div>
                  </div>
                )}

                {/* Session Configuration */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                    Start Review Session
                  </h3>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Number of cards to review
                    </label>
                    <select
                      value={cardLimit}
                      onChange={(e) => setCardLimit(Number(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                               bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100
                               focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value={5}>5 cards (Quick)</option>
                      <option value={10}>10 cards (Short)</option>
                      <option value={20}>20 cards (Standard)</option>
                      <option value={50}>50 cards (Extended)</option>
                      <option value={100}>100 cards (Marathon)</option>
                    </select>
                  </div>

                  <div className="flex space-x-4">
                    <Button 
                      onClick={handleStartSession}
                      disabled={dueCount + newCount === 0}
                      className="flex-1"
                    >
                      <PlayIcon className="w-4 h-4 mr-2" />
                      Start Review
                    </Button>
                    <Button variant="outline" onClick={onClose}>
                      Cancel
                    </Button>
                  </div>

                  {dueCount + newCount === 0 && (
                    <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                      <AcademicCapIcon className="w-12 h-12 mx-auto mb-4 opacity-50" />
                      <p>No cards available for review.</p>
                      <p className="text-sm">Add some vocabulary words first!</p>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              /* Active Quiz */
              <div className="max-w-2xl mx-auto space-y-6">
                {currentCard ? (
                  <div className="space-y-6">
                    {/* Card counter */}
                    <div className="text-center text-sm text-gray-500 dark:text-gray-400">
                      Card {(currentSession?.cards_completed || 0) + 1} of {currentSession?.total_cards}
                    </div>

                    {/* Vocabulary Card */}
                    <div className="bg-white dark:bg-gray-800 rounded-lg border-2 border-gray-200 dark:border-gray-700 p-8 text-center min-h-[300px] flex flex-col justify-center">
                      <div className="space-y-4">
                        <div className="text-3xl font-bold text-gray-900 dark:text-gray-100">
                          {currentCard.vocabulary_word.word}
                        </div>
                        
                        {currentCard.is_new && (
                          <div className="inline-block px-3 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 rounded-full text-sm">
                            New Word
                          </div>
                        )}
                        
                        {showAnswer ? (
                          <div className="mt-6 space-y-4">
                            <div className="text-lg text-gray-700 dark:text-gray-300 border-t border-gray-200 dark:border-gray-700 pt-4">
                              {currentCard.vocabulary_word.definition}
                            </div>
                            
                            {currentCard.vocabulary_word.context && (
                              <div className="text-sm text-gray-500 dark:text-gray-400 italic">
                                Context: {currentCard.vocabulary_word.context}
                              </div>
                            )}
                          </div>
                        ) : (
                          <div className="mt-6 text-gray-500 dark:text-gray-400">
                            Think of the definition...
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Action buttons */}
                    {!showAnswer ? (
                      <div className="flex justify-center">
                        <Button onClick={handleShowAnswer} size="lg">
                          Show Answer
                        </Button>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        <div className="text-center text-sm text-gray-600 dark:text-gray-400">
                          How well did you know this word?
                        </div>
                        
                        {/* Quality buttons */}
                        <div className="grid grid-cols-3 gap-3">
                          {Object.entries(qualityLabels).map(([quality, info]) => (
                            <button
                              key={quality}
                              onClick={() => handleQualitySubmit(Number(quality) as 0 | 1 | 2 | 3 | 4 | 5)}
                              className={`p-4 rounded-lg text-white text-center transition-all duration-200 hover:scale-105 ${info.color}`}
                            >
                              <div className="font-medium">{info.label}</div>
                              <div className="text-xs opacity-90">{info.description}</div>
                            </button>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Session controls */}
                    <div className="flex justify-center space-x-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                      <Button variant="outline" onClick={handleEndSession}>
                        <PauseIcon className="w-4 h-4 mr-2" />
                        End Session
                      </Button>
                      
                      {showAnswer && (
                        <Button
                          variant="outline"
                          onClick={() => handleQualitySubmit(3)}
                          title="Skip with default score"
                        >
                          <ForwardIcon className="w-4 h-4 mr-2" />
                          Skip
                        </Button>
                      )}
                    </div>
                  </div>
                ) : (
                  /* Session completed */
                  <div className="text-center space-y-6">
                    <CheckCircleIcon className="w-16 h-16 text-green-500 mx-auto" />
                    <div>
                      <h3 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                        Session Complete!
                      </h3>
                      <p className="text-gray-600 dark:text-gray-400">
                        You've reviewed {currentSession?.total_cards} cards.
                      </p>
                    </div>
                    
                    <div className="flex space-x-4 justify-center">
                      <Button onClick={() => setSessionStarted(false)}>
                        Start Another Session
                      </Button>
                      <Button variant="outline" onClick={onClose}>
                        Close
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};