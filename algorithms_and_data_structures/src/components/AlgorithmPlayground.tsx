import React, { useState, useEffect, useCallback } from 'react';
import { AlgorithmStep, VisualizationData } from '../types/learning-types';
import { PlaygroundVisualization } from './PlaygroundVisualization';
import { PlaygroundControls } from './PlaygroundControls';
import { CodePanel } from './CodePanel';

interface AlgorithmPlaygroundProps {
  algorithm: string;
  initialData: any[];
  onStepComplete?: (step: number) => void;
}

export const AlgorithmPlayground: React.FC<AlgorithmPlaygroundProps> = ({
  algorithm,
  initialData,
  onStepComplete
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [speed, setSpeed] = useState(1000); // ms between steps
  const [data, setData] = useState(initialData);
  const [steps, setSteps] = useState<AlgorithmStep[]>([]);
  const [history, setHistory] = useState<VisualizationData[]>([]);

  // Load algorithm steps based on algorithm type
  useEffect(() => {
    const loadAlgorithmSteps = async () => {
      const algorithmSteps = await getAlgorithmSteps(algorithm, initialData);
      setSteps(algorithmSteps);
    };
    
    loadAlgorithmSteps();
  }, [algorithm, initialData]);

  // Auto-play functionality
  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (isPlaying && currentStep < steps.length - 1) {
      interval = setInterval(() => {
        setCurrentStep(prev => {
          const next = prev + 1;
          if (next >= steps.length - 1) {
            setIsPlaying(false);
          }
          return next;
        });
      }, speed);
    }
    
    return () => clearInterval(interval);
  }, [isPlaying, currentStep, steps.length, speed]);

  // Execute current step
  useEffect(() => {
    if (steps[currentStep]) {
      const step = steps[currentStep];
      if (step.visualization) {
        setData(step.visualization.data);
        setHistory(prev => [...prev, step.visualization!]);
      }
      onStepComplete?.(currentStep);
    }
  }, [currentStep, steps, onStepComplete]);

  const handlePlay = useCallback(() => {
    setIsPlaying(!isPlaying);
  }, [isPlaying]);

  const handleStep = useCallback((direction: 'next' | 'prev') => {
    setIsPlaying(false);
    setCurrentStep(prev => {
      if (direction === 'next') {
        return Math.min(prev + 1, steps.length - 1);
      } else {
        return Math.max(prev - 1, 0);
      }
    });
  }, [steps.length]);

  const handleReset = useCallback(() => {
    setIsPlaying(false);
    setCurrentStep(0);
    setData(initialData);
    setHistory([]);
  }, [initialData]);

  const handleSpeedChange = useCallback((newSpeed: number) => {
    setSpeed(newSpeed);
  }, []);

  const currentVisualization: VisualizationData = {
    type: 'array',
    data,
    highlights: steps[currentStep]?.visualization?.highlights || [],
    annotations: steps[currentStep]?.visualization?.annotations || []
  };

  return (
    <div className="algorithm-playground">
      <div className="playground-header">
        <h2 className="algorithm-title">
          {algorithm.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
        </h2>
        <div className="step-indicator">
          Step {currentStep + 1} of {steps.length}
        </div>
      </div>

      <div className="playground-content">
        <div className="visualization-section">
          <PlaygroundVisualization 
            data={currentVisualization}
            width={800}
            height={400}
          />
          
          {steps[currentStep] && (
            <div className="step-description">
              <h3>{steps[currentStep].title}</h3>
              <p>{steps[currentStep].description}</p>
            </div>
          )}
        </div>

        <div className="code-section">
          <CodePanel 
            code={steps[currentStep]?.code || ''}
            language="javascript"
            highlightedLines={[]}
          />
        </div>
      </div>

      <PlaygroundControls
        isPlaying={isPlaying}
        currentStep={currentStep}
        totalSteps={steps.length}
        speed={speed}
        onPlay={handlePlay}
        onStep={handleStep}
        onReset={handleReset}
        onSpeedChange={handleSpeedChange}
      />
    </div>
  );
};

// Helper function to generate algorithm steps
async function getAlgorithmSteps(algorithm: string, data: any[]): Promise<AlgorithmStep[]> {
  // This would typically fetch from an API or generate dynamically
  switch (algorithm) {
    case 'bubbleSort':
      return generateBubbleSortSteps(data);
    case 'quickSort':
      return generateQuickSortSteps(data);
    case 'binarySearch':
      return generateBinarySearchSteps(data);
    default:
      return [];
  }
}

function generateBubbleSortSteps(data: number[]): AlgorithmStep[] {
  const steps: AlgorithmStep[] = [];
  const arr = [...data];
  let stepCount = 0;

  for (let i = 0; i < arr.length; i++) {
    for (let j = 0; j < arr.length - i - 1; j++) {
      // Compare step
      steps.push({
        id: `step-${stepCount++}`,
        title: `Compare ${arr[j]} and ${arr[j + 1]}`,
        description: `Comparing adjacent elements at positions ${j} and ${j + 1}`,
        code: `if (arr[${j}] > arr[${j + 1}]) {\n  swap(arr, ${j}, ${j + 1});\n}`,
        visualization: {
          type: 'array',
          data: [...arr],
          highlights: [j, j + 1],
          annotations: [{
            position: { x: j * 60 + 30, y: -20 },
            text: 'Comparing',
            type: 'info'
          }]
        }
      });

      if (arr[j] > arr[j + 1]) {
        // Swap step
        [arr[j], arr[j + 1]] = [arr[j + 1], arr[j]];
        steps.push({
          id: `step-${stepCount++}`,
          title: `Swap ${arr[j + 1]} and ${arr[j]}`,
          description: `Swapping elements because ${arr[j + 1]} > ${arr[j]}`,
          code: `swap(arr, ${j}, ${j + 1});`,
          visualization: {
            type: 'array',
            data: [...arr],
            highlights: [j, j + 1],
            annotations: [{
              position: { x: j * 60 + 30, y: -20 },
              text: 'Swapped!',
              type: 'success'
            }]
          }
        });
      }
    }
  }

  return steps;
}

function generateQuickSortSteps(data: number[]): AlgorithmStep[] {
  // Implementation for QuickSort steps
  return [];
}

function generateBinarySearchSteps(data: number[]): AlgorithmStep[] {
  // Implementation for Binary Search steps
  return [];
}