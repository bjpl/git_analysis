import React, { useState, useEffect, useCallback } from 'react';
import { LearningPattern } from '../types/learning-types';
import { PatternCard } from './PatternCard';
import { CodeSnippet } from './CodeSnippet';
import { ScoreBoard } from './ScoreBoard';

interface PatternMatcherProps {
  onScoreUpdate?: (score: number) => void;
  onPatternLearned?: (pattern: LearningPattern) => void;
}

export const PatternMatcher: React.FC<PatternMatcherProps> = ({
  onScoreUpdate,
  onPatternLearned
}) => {
  const [currentPattern, setCurrentPattern] = useState<LearningPattern | null>(null);
  const [codeOptions, setCodeOptions] = useState<string[]>([]);
  const [selectedOption, setSelectedOption] = useState<string>('');
  const [score, setScore] = useState(0);
  const [streak, setStreak] = useState(0);
  const [timeLeft, setTimeLeft] = useState(30);
  const [gameState, setGameState] = useState<'ready' | 'playing' | 'finished'>('ready');
  const [feedback, setFeedback] = useState<string>('');
  const [difficulty, setDifficulty] = useState<1 | 2 | 3 | 4 | 5>(1);
  const [learnedPatterns, setLearnedPatterns] = useState<Set<string>>(new Set());

  // Load patterns based on difficulty
  const patterns = getPatternsByDifficulty(difficulty);

  // Game timer
  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (gameState === 'playing' && timeLeft > 0) {
      timer = setTimeout(() => setTimeLeft(prev => prev - 1), 1000);
    } else if (timeLeft === 0) {
      setGameState('finished');
    }
    return () => clearTimeout(timer);
  }, [gameState, timeLeft]);

  // Generate new question when game starts or after correct answer
  useEffect(() => {
    if (gameState === 'playing' && !currentPattern) {
      generateNewQuestion();
    }
  }, [gameState]);

  const startGame = useCallback(() => {
    setGameState('playing');
    setScore(0);
    setStreak(0);
    setTimeLeft(30 + difficulty * 10); // More time for harder difficulties
    setLearnedPatterns(new Set());
    generateNewQuestion();
  }, [difficulty]);

  const generateNewQuestion = useCallback(() => {
    const availablePatterns = patterns.filter(p => !learnedPatterns.has(p.id));
    if (availablePatterns.length === 0) {
      setGameState('finished');
      return;
    }

    const randomPattern = availablePatterns[Math.floor(Math.random() * availablePatterns.length)];
    setCurrentPattern(randomPattern);

    // Generate multiple choice options
    const correctCode = randomPattern.examples[0];
    const incorrectCodes = generateIncorrectOptions(randomPattern, patterns);
    const allOptions = [correctCode, ...incorrectCodes].sort(() => Math.random() - 0.5);
    
    setCodeOptions(allOptions);
    setSelectedOption('');
    setFeedback('');
  }, [patterns, learnedPatterns]);

  const handleOptionSelect = useCallback((option: string) => {
    if (gameState !== 'playing' || !currentPattern) return;
    
    setSelectedOption(option);
    const isCorrect = currentPattern.examples.includes(option);
    
    if (isCorrect) {
      const points = 10 * difficulty + streak * 2;
      setScore(prev => {
        const newScore = prev + points;
        onScoreUpdate?.(newScore);
        return newScore;
      });
      setStreak(prev => prev + 1);
      setFeedback(`Correct! +${points} points`);
      setLearnedPatterns(prev => new Set([...prev, currentPattern.id]));
      onPatternLearned?.(currentPattern);
      
      // Generate new question after a short delay
      setTimeout(() => {
        generateNewQuestion();
      }, 1500);
    } else {
      setStreak(0);
      setFeedback(`Incorrect. This is a ${getPatternDescription(currentPattern)} pattern.`);
      setTimeLeft(prev => Math.max(0, prev - 5)); // Penalty: lose 5 seconds
    }
  }, [gameState, currentPattern, difficulty, streak, onScoreUpdate, onPatternLearned]);

  const handleDifficultyChange = useCallback((newDifficulty: 1 | 2 | 3 | 4 | 5) => {
    setDifficulty(newDifficulty);
    if (gameState === 'playing') {
      startGame(); // Restart with new difficulty
    }
  }, [gameState, startGame]);

  const resetGame = useCallback(() => {
    setGameState('ready');
    setCurrentPattern(null);
    setFeedback('');
  }, []);

  return (
    <div className="pattern-matcher">
      <div className="game-header">
        <h2>Pattern Matcher Game</h2>
        <p>Match code snippets with their algorithmic patterns</p>
      </div>

      <div className="game-controls">
        <div className="difficulty-selector">
          <label>Difficulty:</label>
          {[1, 2, 3, 4, 5].map(level => (
            <button
              key={level}
              className={difficulty === level ? 'active' : ''}
              onClick={() => handleDifficultyChange(level as 1 | 2 | 3 | 4 | 5)}
              disabled={gameState === 'playing'}
            >
              {level}
            </button>
          ))}
        </div>

        <ScoreBoard
          score={score}
          streak={streak}
          timeLeft={timeLeft}
          patternsLearned={learnedPatterns.size}
        />
      </div>

      <div className="game-content">
        {gameState === 'ready' && (
          <div className="game-start">
            <h3>Ready to start?</h3>
            <p>You'll see algorithm patterns and need to match them with code examples.</p>
            <p>Difficulty {difficulty} - {getDifficultyDescription(difficulty)}</p>
            <button className="start-button" onClick={startGame}>
              Start Game
            </button>
          </div>
        )}

        {gameState === 'playing' && currentPattern && (
          <div className="game-playing">
            <div className="question-section">
              <PatternCard
                pattern={currentPattern}
                showExamples={false}
              />
              
              <div className="question">
                <h3>Which code snippet implements this pattern?</h3>
              </div>
            </div>

            <div className="options-section">
              {codeOptions.map((code, index) => (
                <div
                  key={index}
                  className={`code-option ${selectedOption === code ? 'selected' : ''}`}
                  onClick={() => handleOptionSelect(code)}
                >
                  <div className="option-label">Option {String.fromCharCode(65 + index)}</div>
                  <CodeSnippet
                    code={code}
                    language="javascript"
                    showLineNumbers={false}
                    compact={true}
                  />
                </div>
              ))}
            </div>

            {feedback && (
              <div className={`feedback ${feedback.includes('Correct') ? 'correct' : 'incorrect'}`}>
                {feedback}
              </div>
            )}
          </div>
        )}

        {gameState === 'finished' && (
          <div className="game-finished">
            <h3>Game Over!</h3>
            <div className="final-stats">
              <div className="stat">
                <span className="label">Final Score:</span>
                <span className="value">{score}</span>
              </div>
              <div className="stat">
                <span className="label">Best Streak:</span>
                <span className="value">{streak}</span>
              </div>
              <div className="stat">
                <span className="label">Patterns Learned:</span>
                <span className="value">{learnedPatterns.size}</span>
              </div>
              <div className="stat">
                <span className="label">Accuracy:</span>
                <span className="value">
                  {learnedPatterns.size > 0 ? Math.round((learnedPatterns.size / (learnedPatterns.size + (30 - timeLeft) / 5)) * 100) : 0}%
                </span>
              </div>
            </div>

            <div className="learned-patterns">
              <h4>Patterns You've Mastered:</h4>
              <div className="pattern-list">
                {Array.from(learnedPatterns).map(patternId => {
                  const pattern = patterns.find(p => p.id === patternId);
                  return pattern ? (
                    <div key={patternId} className="learned-pattern">
                      <span className="pattern-name">{pattern.name}</span>
                      <span className="pattern-category">{pattern.category}</span>
                    </div>
                  ) : null;
                })}
              </div>
            </div>

            <div className="game-actions">
              <button onClick={startGame}>Play Again</button>
              <button onClick={resetGame}>Change Difficulty</button>
            </div>
          </div>
        )}
      </div>

      <div className="pattern-reference">
        <h3>Pattern Reference</h3>
        <div className="pattern-categories">
          {['sorting', 'searching', 'graph', 'dynamic', 'greedy'].map(category => (
            <div key={category} className="category-section">
              <h4>{category.charAt(0).toUpperCase() + category.slice(1)} Patterns</h4>
              <div className="patterns-grid">
                {patterns
                  .filter(p => p.category === category)
                  .map(pattern => (
                    <div
                      key={pattern.id}
                      className={`pattern-ref ${learnedPatterns.has(pattern.id) ? 'learned' : ''}`}
                    >
                      <span className="pattern-name">{pattern.name}</span>
                      <span className="pattern-difficulty">★{pattern.difficulty}</span>
                    </div>
                  ))
                }
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Helper functions
function getPatternsByDifficulty(difficulty: number): LearningPattern[] {
  const allPatterns: LearningPattern[] = [
    // Difficulty 1 - Basic patterns
    {
      id: 'linear-search',
      name: 'Linear Search',
      category: 'searching',
      difficulty: 1,
      signature: ['for loop', 'array access', 'comparison'],
      examples: [
        'for (let i = 0; i < arr.length; i++) { if (arr[i] === target) return i; }',
        'let i = 0; while (i < arr.length) { if (arr[i] === target) return i; i++; }'
      ]
    },
    {
      id: 'bubble-sort',
      name: 'Bubble Sort',
      category: 'sorting',
      difficulty: 1,
      signature: ['nested loops', 'adjacent comparison', 'swap'],
      examples: [
        'for (let i = 0; i < n; i++) { for (let j = 0; j < n-i-1; j++) { if (arr[j] > arr[j+1]) swap(arr, j, j+1); } }'
      ]
    },
    // Difficulty 2-3 patterns
    {
      id: 'binary-search',
      name: 'Binary Search',
      category: 'searching',
      difficulty: 2,
      signature: ['divide and conquer', 'middle calculation', 'range reduction'],
      examples: [
        'let mid = Math.floor((left + right) / 2); if (arr[mid] === target) return mid; else if (arr[mid] < target) left = mid + 1; else right = mid - 1;'
      ]
    },
    {
      id: 'merge-sort',
      name: 'Merge Sort',
      category: 'sorting',
      difficulty: 3,
      signature: ['divide and conquer', 'recursive calls', 'merge function'],
      examples: [
        'if (left < right) { let mid = Math.floor((left + right) / 2); mergeSort(arr, left, mid); mergeSort(arr, mid + 1, right); merge(arr, left, mid, right); }'
      ]
    },
    // Difficulty 4-5 patterns
    {
      id: 'dijkstra',
      name: "Dijkstra's Algorithm",
      category: 'graph',
      difficulty: 4,
      signature: ['priority queue', 'distance array', 'relaxation'],
      examples: [
        'while (!pq.isEmpty()) { let u = pq.extractMin(); for (let v of adj[u]) { if (dist[u] + weight[u][v] < dist[v]) { dist[v] = dist[u] + weight[u][v]; pq.decreaseKey(v, dist[v]); } } }'
      ]
    },
    {
      id: 'dynamic-programming',
      name: 'Dynamic Programming',
      category: 'dynamic',
      difficulty: 5,
      signature: ['memoization', 'optimal substructure', 'overlapping subproblems'],
      examples: [
        'if (memo[n] !== undefined) return memo[n]; memo[n] = fibonacci(n-1) + fibonacci(n-2); return memo[n];'
      ]
    }
  ];

  return allPatterns.filter(pattern => pattern.difficulty <= difficulty);
}

function generateIncorrectOptions(correctPattern: LearningPattern, allPatterns: LearningPattern[]): string[] {
  // Get patterns from different categories or with different signatures
  const incorrectPatterns = allPatterns.filter(p => 
    p.id !== correctPattern.id && 
    (p.category !== correctPattern.category || Math.abs(p.difficulty - correctPattern.difficulty) <= 1)
  );

  const options: string[] = [];
  
  // Add some similar but incorrect examples
  for (let i = 0; i < Math.min(3, incorrectPatterns.length); i++) {
    const pattern = incorrectPatterns[i];
    if (pattern.examples.length > 0) {
      options.push(pattern.examples[0]);
    }
  }

  // Fill remaining slots with modified versions of correct code
  while (options.length < 3) {
    const baseCode = correctPattern.examples[0];
    const modifiedCode = introduceCodeError(baseCode);
    if (!options.includes(modifiedCode)) {
      options.push(modifiedCode);
    }
  }

  return options.slice(0, 3);
}

function introduceCodeError(code: string): string {
  const modifications = [
    // Off-by-one errors
    (c: string) => c.replace(/< (\w+)\.length/g, '<= $1.length'),
    (c: string) => c.replace(/\+ 1/g, ''),
    (c: string) => c.replace(/- 1/g, ''),
    // Wrong comparison operators
    (c: string) => c.replace(/</g, '<='),
    (c: string) => c.replace(/>/g, '>='),
    // Variable name changes
    (c: string) => c.replace(/arr\[i\]/g, 'arr[j]'),
    (c: string) => c.replace(/left/g, 'right'),
  ];

  const randomMod = modifications[Math.floor(Math.random() * modifications.length)];
  return randomMod(code);
}

function getPatternDescription(pattern: LearningPattern): string {
  const descriptions: Record<string, string> = {
    'linear-search': 'sequential search through elements',
    'binary-search': 'divide-and-conquer search on sorted data',
    'bubble-sort': 'comparison-based sorting with adjacent swaps',
    'merge-sort': 'divide-and-conquer sorting with merging',
    'dijkstra': 'shortest path algorithm using priority queue',
    'dynamic-programming': 'optimization using memoization'
  };
  
  return descriptions[pattern.id] || pattern.category;
}

function getDifficultyDescription(difficulty: number): string {
  const descriptions = {
    1: 'Basic patterns (loops, simple algorithms)',
    2: 'Intermediate patterns (binary search, recursion)',
    3: 'Advanced patterns (divide & conquer, complex sorting)',
    4: 'Expert patterns (graph algorithms, optimization)',
    5: 'Master patterns (dynamic programming, advanced optimization)'
  };
  
  return descriptions[difficulty as keyof typeof descriptions];
}