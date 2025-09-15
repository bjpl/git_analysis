import React, { useState, useCallback, useEffect } from 'react';
import { ConceptMapping, VisualizationMode, CodeBlock } from '../types/bridge-types';
import { CodeEditor } from './CodeEditor';
import { ConceptVisualizer } from './ConceptVisualizer';
import { MappingControls } from './MappingControls';
import { LearningPath } from './LearningPath';

interface CodeConceptBridgeProps {
  initialCode?: string;
  language?: 'javascript' | 'python' | 'java' | 'cpp';
  onMappingChange?: (mapping: ConceptMapping) => void;
  onLearningProgress?: (progress: number) => void;
}

export const CodeConceptBridge: React.FC<CodeConceptBridgeProps> = ({
  initialCode = '',
  language = 'javascript',
  onMappingChange,
  onLearningProgress
}) => {
  const [code, setCode] = useState(initialCode);
  const [currentMapping, setCurrentMapping] = useState<ConceptMapping | null>(null);
  const [visualizationMode, setVisualizationMode] = useState<VisualizationMode>('flowchart');
  const [highlightedConcepts, setHighlightedConcepts] = useState<string[]>([]);
  const [activeCodeBlocks, setActiveCodeBlocks] = useState<CodeBlock[]>([]);
  const [learningLevel, setLearningLevel] = useState<'beginner' | 'intermediate' | 'advanced'>('beginner');
  const [showExplanations, setShowExplanations] = useState(true);
  const [interactionMode, setInteractionMode] = useState<'explore' | 'quiz' | 'build'>('explore');

  // Analyze code and generate concept mapping
  useEffect(() => {
    if (code.trim()) {
      const mapping = analyzeCodeToConcepts(code, language);
      setCurrentMapping(mapping);
      onMappingChange?.(mapping);
    }
  }, [code, language, onMappingChange]);

  // Update visualization when mapping changes
  useEffect(() => {
    if (currentMapping) {
      const blocks = extractCodeBlocks(code, currentMapping);
      setActiveCodeBlocks(blocks);
    }
  }, [code, currentMapping]);

  const handleCodeChange = useCallback((newCode: string) => {
    setCode(newCode);
  }, []);

  const handleConceptHover = useCallback((conceptId: string) => {
    if (currentMapping) {
      const relatedConcepts = findRelatedConcepts(conceptId, currentMapping);
      setHighlightedConcepts([conceptId, ...relatedConcepts]);
    }
  }, [currentMapping]);

  const handleConceptClick = useCallback((conceptId: string) => {
    if (interactionMode === 'explore') {
      // Show detailed explanation
      showConceptExplanation(conceptId);
    } else if (interactionMode === 'quiz') {
      // Start concept quiz
      startConceptQuiz(conceptId);
    } else if (interactionMode === 'build') {
      // Add concept to builder
      addConceptToBuilder(conceptId);
    }
  }, [interactionMode]);

  const handleVisualizationModeChange = useCallback((mode: VisualizationMode) => {
    setVisualizationMode(mode);
  }, []);

  const handleCodeBlockClick = useCallback((blockId: string) => {
    // Highlight corresponding concept
    if (currentMapping) {
      const concepts = currentMapping.codeToConceptMap[blockId] || [];
      setHighlightedConcepts(concepts);
    }
  }, [currentMapping]);

  const generateCodeFromConcepts = useCallback(() => {
    if (currentMapping) {
      const generatedCode = conceptsToCode(currentMapping, language);
      setCode(generatedCode);
    }
  }, [currentMapping, language]);

  const simplifyVisualization = useCallback(() => {
    if (learningLevel === 'beginner') {
      setVisualizationMode('simplified');
      setShowExplanations(true);
    } else if (learningLevel === 'intermediate') {
      setVisualizationMode('flowchart');
      setShowExplanations(true);
    } else {
      setVisualizationMode('detailed');
      setShowExplanations(false);
    }
  }, [learningLevel]);

  return (
    <div className="code-concept-bridge">
      <div className="bridge-header">
        <h2>Code-to-Concept Bridge</h2>
        <p>Translate between code implementation and algorithmic concepts</p>
      </div>

      <div className="bridge-controls">
        <MappingControls
          language={language}
          visualizationMode={visualizationMode}
          learningLevel={learningLevel}
          interactionMode={interactionMode}
          showExplanations={showExplanations}
          onLanguageChange={(lang) => handleCodeChange('')} // Reset code when changing language
          onVisualizationModeChange={handleVisualizationModeChange}
          onLearningLevelChange={setLearningLevel}
          onInteractionModeChange={setInteractionMode}
          onExplanationToggle={setShowExplanations}
          onSimplifyVisualization={simplifyVisualization}
          onGenerateCode={generateCodeFromConcepts}
        />
      </div>

      <div className="bridge-content">
        <div className="code-section">
          <div className="section-header">
            <h3>Code Implementation</h3>
            <div className="code-actions">
              <button onClick={() => setCode('')}>Clear</button>
              <button onClick={() => loadExample()}>Load Example</button>
            </div>
          </div>
          
          <CodeEditor
            code={code}
            language={language}
            onChange={handleCodeChange}
            highlightedBlocks={activeCodeBlocks}
            onBlockClick={handleCodeBlockClick}
            showLineNumbers={true}
            readOnly={interactionMode === 'quiz'}
          />

          {interactionMode === 'build' && (
            <div className="code-builder">
              <CodeBuilder
                language={language}
                concepts={currentMapping?.concepts || []}
                onCodeGenerated={handleCodeChange}
              />
            </div>
          )}
        </div>

        <div className="visualization-section">
          <div className="section-header">
            <h3>Conceptual Visualization</h3>
            <div className="visualization-modes">
              {(['simplified', 'flowchart', 'detailed', 'interactive'] as VisualizationMode[]).map(mode => (
                <button
                  key={mode}
                  className={visualizationMode === mode ? 'active' : ''}
                  onClick={() => handleVisualizationModeChange(mode)}
                >
                  {mode.charAt(0).toUpperCase() + mode.slice(1)}
                </button>
              ))}
            </div>
          </div>

          <ConceptVisualizer
            mapping={currentMapping}
            mode={visualizationMode}
            highlightedConcepts={highlightedConcepts}
            learningLevel={learningLevel}
            showExplanations={showExplanations}
            onConceptHover={handleConceptHover}
            onConceptClick={handleConceptClick}
            width={600}
            height={400}
          />

          {showExplanations && highlightedConcepts.length > 0 && (
            <div className="concept-explanations">
              <ConceptExplanations
                concepts={highlightedConcepts}
                mapping={currentMapping}
                learningLevel={learningLevel}
              />
            </div>
          )}
        </div>

        <div className="learning-section">
          <div className="section-header">
            <h3>Learning Path</h3>
          </div>
          
          <LearningPath
            currentConcepts={currentMapping?.concepts || []}
            learningLevel={learningLevel}
            onConceptSelect={handleConceptClick}
          />

          {interactionMode === 'quiz' && (
            <div className="concept-quiz">
              <ConceptQuiz
                mapping={currentMapping}
                onAnswerCorrect={(conceptId) => {
                  // Update learning progress
                  const progress = calculateLearningProgress(conceptId);
                  onLearningProgress?.(progress);
                }}
              />
            </div>
          )}
        </div>
      </div>

      <div className="mapping-analysis">
        <div className="analysis-header">
          <h3>Mapping Analysis</h3>
        </div>
        
        {currentMapping && (
          <div className="mapping-stats">
            <div className="stat">
              <span className="label">Concepts Identified:</span>
              <span className="value">{currentMapping.concepts.length}</span>
            </div>
            <div className="stat">
              <span className="label">Code Blocks:</span>
              <span className="value">{activeCodeBlocks.length}</span>
            </div>
            <div className="stat">
              <span className="label">Complexity Level:</span>
              <span className="value">{calculateComplexityLevel(currentMapping)}</span>
            </div>
            <div className="stat">
              <span className="label">Learning Progress:</span>
              <span className="value">{calculateUserProgress()}%</span>
            </div>
          </div>
        )}

        <div className="concept-breakdown">
          <h4>Concept Categories</h4>
          <div className="category-list">
            {currentMapping?.concepts.map(concept => (
              <div
                key={concept.id}
                className={`concept-item ${highlightedConcepts.includes(concept.id) ? 'highlighted' : ''}`}
                onMouseEnter={() => handleConceptHover(concept.id)}
                onClick={() => handleConceptClick(concept.id)}
              >
                <span className="concept-name">{concept.name}</span>
                <span className="concept-category">{concept.category}</span>
                <span className="concept-difficulty">
                  {'★'.repeat(concept.difficulty)}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// Supporting Components
interface CodeBuilderProps {
  language: string;
  concepts: Array<{ id: string; name: string; codeTemplate: string }>;
  onCodeGenerated: (code: string) => void;
}

const CodeBuilder: React.FC<CodeBuilderProps> = ({ language, concepts, onCodeGenerated }) => {
  const [selectedConcepts, setSelectedConcepts] = useState<string[]>([]);
  const [buildMode, setBuildMode] = useState<'guided' | 'freeform'>('guided');

  const handleConceptAdd = (conceptId: string) => {
    setSelectedConcepts(prev => [...prev, conceptId]);
  };

  const handleConceptRemove = (conceptId: string) => {
    setSelectedConcepts(prev => prev.filter(id => id !== conceptId));
  };

  const generateCode = () => {
    const code = concepts
      .filter(concept => selectedConcepts.includes(concept.id))
      .map(concept => concept.codeTemplate)
      .join('\n\n');
    
    onCodeGenerated(code);
  };

  return (
    <div className="code-builder">
      <div className="builder-controls">
        <div className="mode-selector">
          <button
            className={buildMode === 'guided' ? 'active' : ''}
            onClick={() => setBuildMode('guided')}
          >
            Guided
          </button>
          <button
            className={buildMode === 'freeform' ? 'active' : ''}
            onClick={() => setBuildMode('freeform')}
          >
            Freeform
          </button>
        </div>
        <button onClick={generateCode}>Generate Code</button>
      </div>

      <div className="concept-palette">
        <h4>Available Concepts</h4>
        <div className="concepts-grid">
          {concepts.map(concept => (
            <div
              key={concept.id}
              className={`concept-card ${selectedConcepts.includes(concept.id) ? 'selected' : ''}`}
              onClick={() => 
                selectedConcepts.includes(concept.id)
                  ? handleConceptRemove(concept.id)
                  : handleConceptAdd(concept.id)
              }
            >
              <span className="concept-name">{concept.name}</span>
              {selectedConcepts.includes(concept.id) && (
                <span className="selected-indicator">✓</span>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="selected-concepts">
        <h4>Selected Concepts</h4>
        <div className="concept-sequence">
          {selectedConcepts.map((conceptId, index) => {
            const concept = concepts.find(c => c.id === conceptId);
            return concept ? (
              <div key={`${conceptId}-${index}`} className="sequence-item">
                <span className="order">{index + 1}</span>
                <span className="name">{concept.name}</span>
                <button onClick={() => handleConceptRemove(conceptId)}>×</button>
              </div>
            ) : null;
          })}
        </div>
      </div>
    </div>
  );
};

interface ConceptQuizProps {
  mapping: ConceptMapping | null;
  onAnswerCorrect: (conceptId: string) => void;
}

const ConceptQuiz: React.FC<ConceptQuizProps> = ({ mapping, onAnswerCorrect }) => {
  const [currentQuestion, setCurrentQuestion] = useState<any>(null);
  const [userAnswer, setUserAnswer] = useState<string>('');
  const [feedback, setFeedback] = useState<string>('');

  useEffect(() => {
    if (mapping) {
      generateQuestion(mapping);
    }
  }, [mapping]);

  const generateQuestion = (mapping: ConceptMapping) => {
    // Generate a question based on the current mapping
    const concepts = mapping.concepts;
    if (concepts.length > 0) {
      const randomConcept = concepts[Math.floor(Math.random() * concepts.length)];
      setCurrentQuestion({
        conceptId: randomConcept.id,
        question: `What does this concept represent: ${randomConcept.name}?`,
        options: generateQuestionOptions(randomConcept, concepts),
        correctAnswer: randomConcept.description
      });
    }
  };

  const handleAnswerSubmit = () => {
    if (currentQuestion && userAnswer === currentQuestion.correctAnswer) {
      setFeedback('Correct!');
      onAnswerCorrect(currentQuestion.conceptId);
      setTimeout(() => {
        generateQuestion(mapping!);
        setUserAnswer('');
        setFeedback('');
      }, 1500);
    } else {
      setFeedback('Try again! Think about the algorithm structure.');
    }
  };

  if (!currentQuestion) return null;

  return (
    <div className="concept-quiz">
      <div className="question">
        <h4>{currentQuestion.question}</h4>
      </div>
      
      <div className="answer-options">
        {currentQuestion.options.map((option: string, index: number) => (
          <button
            key={index}
            className={userAnswer === option ? 'selected' : ''}
            onClick={() => setUserAnswer(option)}
          >
            {option}
          </button>
        ))}
      </div>
      
      <button onClick={handleAnswerSubmit} disabled={!userAnswer}>
        Submit Answer
      </button>
      
      {feedback && (
        <div className={`feedback ${feedback === 'Correct!' ? 'correct' : 'incorrect'}`}>
          {feedback}
        </div>
      )}
    </div>
  );
};

// Helper functions
function analyzeCodeToConcepts(code: string, language: string): ConceptMapping {
  // This would use AST parsing and pattern recognition
  // Simplified implementation for demo
  const concepts = [];
  const codeToConceptMap: Record<string, string[]> = {};
  
  // Detect loops
  if (code.includes('for (') || code.includes('while (')) {
    concepts.push({
      id: 'iteration',
      name: 'Iteration',
      category: 'control-flow',
      description: 'Repeating code execution',
      difficulty: 1,
      codeTemplate: 'for (let i = 0; i < n; i++) { }'
    });
  }
  
  // Detect recursion
  if (code.includes('function') && code.match(/\w+\s*\([^)]*\)\s*{[^}]*\w+\s*\(/)) {
    concepts.push({
      id: 'recursion',
      name: 'Recursion',
      category: 'control-flow',
      description: 'Function calling itself',
      difficulty: 3,
      codeTemplate: 'function recursive(n) { if (base) return; return recursive(n-1); }'
    });
  }
  
  // Detect arrays
  if (code.includes('[') || code.includes('Array')) {
    concepts.push({
      id: 'array',
      name: 'Array Data Structure',
      category: 'data-structure',
      description: 'Sequential collection of elements',
      difficulty: 1,
      codeTemplate: 'const arr = []; arr[index] = value;'
    });
  }
  
  return {
    concepts,
    codeToConceptMap,
    conceptToCodeMap: {},
    relationships: [],
    metadata: {
      complexity: calculateComplexityFromConcepts(concepts),
      language,
      analysisTimestamp: new Date()
    }
  };
}

function extractCodeBlocks(code: string, mapping: ConceptMapping): CodeBlock[] {
  // Extract meaningful code blocks for highlighting
  const lines = code.split('\n');
  const blocks: CodeBlock[] = [];
  
  lines.forEach((line, index) => {
    if (line.trim()) {
      blocks.push({
        id: `block-${index}`,
        startLine: index,
        endLine: index,
        code: line.trim(),
        concepts: [] // Would be populated based on analysis
      });
    }
  });
  
  return blocks;
}

function findRelatedConcepts(conceptId: string, mapping: ConceptMapping): string[] {
  // Find concepts that are related to the given concept
  return mapping.relationships
    .filter(rel => rel.source === conceptId || rel.target === conceptId)
    .map(rel => rel.source === conceptId ? rel.target : rel.source);
}

function conceptsToCode(mapping: ConceptMapping, language: string): string {
  // Generate code from concepts
  return mapping.concepts
    .map(concept => concept.codeTemplate)
    .join('\n\n');
}

function calculateComplexityLevel(mapping: ConceptMapping): string {
  const avgDifficulty = mapping.concepts.reduce((sum, c) => sum + c.difficulty, 0) / mapping.concepts.length;
  
  if (avgDifficulty <= 1.5) return 'Beginner';
  if (avgDifficulty <= 2.5) return 'Intermediate';
  return 'Advanced';
}

function calculateComplexityFromConcepts(concepts: any[]): number {
  return concepts.reduce((sum, c) => sum + c.difficulty, 0) / Math.max(concepts.length, 1);
}

function calculateUserProgress(): number {
  // Would track actual user progress
  return Math.floor(Math.random() * 100);
}

function generateQuestionOptions(concept: any, allConcepts: any[]): string[] {
  const options = [concept.description];
  
  // Add some incorrect options
  const otherConcepts = allConcepts.filter(c => c.id !== concept.id);
  for (let i = 0; i < Math.min(3, otherConcepts.length); i++) {
    options.push(otherConcepts[i].description);
  }
  
  return options.sort(() => Math.random() - 0.5);
}

function showConceptExplanation(conceptId: string) {
  // Show detailed explanation modal
  console.log(`Showing explanation for concept: ${conceptId}`);
}

function startConceptQuiz(conceptId: string) {
  // Start quiz for specific concept
  console.log(`Starting quiz for concept: ${conceptId}`);
}

function addConceptToBuilder(conceptId: string) {
  // Add concept to the code builder
  console.log(`Adding concept to builder: ${conceptId}`);
}

function loadExample() {
  // Load a predefined code example
  const examples = [
    `function bubbleSort(arr) {
  for (let i = 0; i < arr.length; i++) {
    for (let j = 0; j < arr.length - i - 1; j++) {
      if (arr[j] > arr[j + 1]) {
        [arr[j], arr[j + 1]] = [arr[j + 1], arr[j]];
      }
    }
  }
  return arr;
}`,
    `function binarySearch(arr, target) {
  let left = 0;
  let right = arr.length - 1;
  
  while (left <= right) {
    const mid = Math.floor((left + right) / 2);
    if (arr[mid] === target) return mid;
    if (arr[mid] < target) left = mid + 1;
    else right = mid - 1;
  }
  return -1;
}`
  ];
  
  return examples[Math.floor(Math.random() * examples.length)];
}