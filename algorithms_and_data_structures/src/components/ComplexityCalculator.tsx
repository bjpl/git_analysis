import React, { useState, useEffect, useMemo } from 'react';
import { ComplexityAnalysis, ComplexityOperation } from '../types/learning-types';
import { ComplexityChart } from './ComplexityChart';
import { OperationSelector } from './OperationSelector';

interface ComplexityCalculatorProps {
  algorithm?: string;
  dataStructure?: string;
  onAnalysisChange?: (analysis: ComplexityAnalysis) => void;
}

export const ComplexityCalculator: React.FC<ComplexityCalculatorProps> = ({
  algorithm,
  dataStructure,
  onAnalysisChange
}) => {
  const [inputSize, setInputSize] = useState(100);
  const [selectedOperation, setSelectedOperation] = useState<string>('');
  const [customComplexity, setCustomComplexity] = useState<string>('');
  const [showComparison, setShowComparison] = useState(false);
  const [comparisonFunctions, setComparisonFunctions] = useState<string[]>(['O(1)', 'O(log n)', 'O(n)', 'O(n log n)', 'O(n²)']);

  // Get complexity analysis for the current algorithm/data structure
  const analysis = useMemo(() => {
    return getComplexityAnalysis(algorithm, dataStructure);
  }, [algorithm, dataStructure]);

  // Calculate actual operation counts for different input sizes
  const operationCounts = useMemo(() => {
    const sizes = [1, 10, 100, 1000, 10000];
    const operations = analysis.operations;
    
    return sizes.map(n => ({
      inputSize: n,
      operations: operations.map(op => ({
        name: op.name,
        count: calculateOperationCount(op.complexity, n)
      }))
    }));
  }, [analysis]);

  // Generate chart data for visualization
  const chartData = useMemo(() => {
    const sizes = Array.from({length: 50}, (_, i) => (i + 1) * (inputSize / 50));
    
    return sizes.map(n => {
      const dataPoint: any = { inputSize: n };
      
      // Add data for each complexity function
      if (showComparison) {
        comparisonFunctions.forEach(complexity => {
          dataPoint[complexity] = calculateOperationCount(complexity, n);
        });
      } else {
        analysis.operations.forEach(op => {
          dataPoint[op.name] = calculateOperationCount(op.complexity, n);
        });
      }
      
      return dataPoint;
    });
  }, [inputSize, analysis, showComparison, comparisonFunctions]);

  useEffect(() => {
    onAnalysisChange?.(analysis);
  }, [analysis, onAnalysisChange]);

  const handleInputSizeChange = (size: number) => {
    setInputSize(Math.max(1, Math.min(100000, size)));
  };

  const handleAddComparison = () => {
    if (customComplexity && !comparisonFunctions.includes(customComplexity)) {
      setComparisonFunctions(prev => [...prev, customComplexity]);
      setCustomComplexity('');
    }
  };

  const handleRemoveComparison = (complexity: string) => {
    setComparisonFunctions(prev => prev.filter(c => c !== complexity));
  };

  return (
    <div className="complexity-calculator">
      <div className="calculator-header">
        <h2>Complexity Calculator</h2>
        <p>Explore how algorithm performance scales with input size</p>
      </div>

      <div className="calculator-controls">
        <div className="input-controls">
          <div className="control-group">
            <label>Input Size (n):</label>
            <input
              type="range"
              min="1"
              max="10000"
              value={inputSize}
              onChange={(e) => handleInputSizeChange(parseInt(e.target.value))}
            />
            <input
              type="number"
              value={inputSize}
              onChange={(e) => handleInputSizeChange(parseInt(e.target.value))}
              min="1"
              max="100000"
            />
          </div>

          <div className="control-group">
            <label>Analysis Mode:</label>
            <select 
              value={showComparison ? 'comparison' : 'algorithm'}
              onChange={(e) => setShowComparison(e.target.value === 'comparison')}
            >
              <option value="algorithm">Algorithm Analysis</option>
              <option value="comparison">Complexity Comparison</option>
            </select>
          </div>
        </div>

        {showComparison && (
          <div className="comparison-controls">
            <h3>Compare Complexities</h3>
            <div className="add-complexity">
              <input
                type="text"
                placeholder="e.g., O(2^n), O(n!)"
                value={customComplexity}
                onChange={(e) => setCustomComplexity(e.target.value)}
              />
              <button onClick={handleAddComparison}>Add</button>
            </div>
            
            <div className="complexity-list">
              {comparisonFunctions.map(complexity => (
                <div key={complexity} className="complexity-item">
                  <span>{complexity}</span>
                  <button 
                    onClick={() => handleRemoveComparison(complexity)}
                    className="remove-btn"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="calculator-content">
        <div className="chart-section">
          <ComplexityChart
            data={chartData}
            width={800}
            height={400}
            showComparison={showComparison}
            comparisonFunctions={comparisonFunctions}
          />
        </div>

        <div className="analysis-section">
          {!showComparison && (
            <>
              <div className="complexity-summary">
                <h3>Time Complexity</h3>
                <div className="complexity-cases">
                  <div className="case best">
                    <span className="label">Best Case:</span>
                    <span className="value">{analysis.timeComplexity.best}</span>
                  </div>
                  <div className="case average">
                    <span className="label">Average Case:</span>
                    <span className="value">{analysis.timeComplexity.average}</span>
                  </div>
                  <div className="case worst">
                    <span className="label">Worst Case:</span>
                    <span className="value">{analysis.timeComplexity.worst}</span>
                  </div>
                </div>
                
                <div className="space-complexity">
                  <span className="label">Space Complexity:</span>
                  <span className="value">{analysis.spaceComplexity}</span>
                </div>
              </div>

              <div className="operations-breakdown">
                <h3>Operations at n = {inputSize}</h3>
                {analysis.operations.map(operation => (
                  <div key={operation.name} className="operation-item">
                    <div className="operation-header">
                      <span className="name">{operation.name}</span>
                      <span className="complexity">{operation.complexity}</span>
                    </div>
                    <div className="operation-count">
                      {calculateOperationCount(operation.complexity, inputSize).toLocaleString()} operations
                    </div>
                    <div className="operation-description">
                      {operation.description}
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}

          <div className="scaling-table">
            <h3>Scaling Analysis</h3>
            <table>
              <thead>
                <tr>
                  <th>Input Size</th>
                  {showComparison ? (
                    comparisonFunctions.map(complexity => (
                      <th key={complexity}>{complexity}</th>
                    ))
                  ) : (
                    analysis.operations.map(op => (
                      <th key={op.name}>{op.name}</th>
                    ))
                  )}
                </tr>
              </thead>
              <tbody>
                {operationCounts.slice(0, 5).map(row => (
                  <tr key={row.inputSize}>
                    <td>{row.inputSize.toLocaleString()}</td>
                    {showComparison ? (
                      comparisonFunctions.map(complexity => (
                        <td key={complexity}>
                          {calculateOperationCount(complexity, row.inputSize).toLocaleString()}
                        </td>
                      ))
                    ) : (
                      row.operations.map(op => (
                        <td key={op.name}>
                          {op.count.toLocaleString()}
                        </td>
                      ))
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div className="insights-section">
        <h3>Key Insights</h3>
        <div className="insights">
          <ComplexityInsights
            analysis={analysis}
            inputSize={inputSize}
            showComparison={showComparison}
            comparisonFunctions={comparisonFunctions}
          />
        </div>
      </div>
    </div>
  );
};

interface ComplexityInsightsProps {
  analysis: ComplexityAnalysis;
  inputSize: number;
  showComparison: boolean;
  comparisonFunctions: string[];
}

const ComplexityInsights: React.FC<ComplexityInsightsProps> = ({
  analysis,
  inputSize,
  showComparison,
  comparisonFunctions
}) => {
  const insights: string[] = [];

  if (!showComparison) {
    // Generate insights based on the algorithm's complexity
    const worstCase = analysis.timeComplexity.worst;
    
    if (worstCase.includes('O(1)')) {
      insights.push("🚀 Constant time - Performance doesn't change with input size!");
    } else if (worstCase.includes('O(log n)')) {
      insights.push("📈 Logarithmic time - Very efficient even for large inputs");
    } else if (worstCase.includes('O(n)')) {
      insights.push("📊 Linear time - Performance scales proportionally with input");
    } else if (worstCase.includes('O(n log n)')) {
      insights.push("⚖️ Linearithmic time - Good balance for sorting algorithms");
    } else if (worstCase.includes('O(n²)')) {
      insights.push("⚠️ Quadratic time - Performance degrades quickly with larger inputs");
    } else if (worstCase.includes('O(2^n)')) {
      insights.push("🐌 Exponential time - Only practical for small inputs");
    }

    if (inputSize > 1000 && worstCase.includes('O(n²)')) {
      insights.push("💡 Consider optimization - Quadratic algorithms can be slow for large datasets");
    }
  } else {
    // Generate comparison insights
    const fastestAt1000 = comparisonFunctions.reduce((fastest, current) => {
      const currentCount = calculateOperationCount(current, 1000);
      const fastestCount = calculateOperationCount(fastest, 1000);
      return currentCount < fastestCount ? current : fastest;
    });

    insights.push(`🏃‍♂️ Most efficient at n=1000: ${fastestAt1000}`);
    
    const exponentialFunctions = comparisonFunctions.filter(c => 
      c.includes('2^n') || c.includes('n!')
    );
    
    if (exponentialFunctions.length > 0) {
      insights.push("⚠️ Exponential complexities become impractical very quickly");
    }
  }

  return (
    <div className="complexity-insights">
      {insights.map((insight, index) => (
        <div key={index} className="insight-item">
          {insight}
        </div>
      ))}
    </div>
  );
};

// Helper functions
function getComplexityAnalysis(algorithm?: string, dataStructure?: string): ComplexityAnalysis {
  if (algorithm === 'bubbleSort') {
    return {
      timeComplexity: {
        best: 'O(n)',
        average: 'O(n²)',
        worst: 'O(n²)'
      },
      spaceComplexity: 'O(1)',
      operations: [
        {
          name: 'Comparisons',
          complexity: 'O(n²)',
          description: 'Compare adjacent elements',
          examples: [1, 4, 9, 16, 25]
        },
        {
          name: 'Swaps',
          complexity: 'O(n²)',
          description: 'Exchange elements when out of order',
          examples: [0, 2, 4, 8, 12]
        }
      ]
    };
  }

  // Default analysis
  return {
    timeComplexity: {
      best: 'O(n)',
      average: 'O(n)',
      worst: 'O(n)'
    },
    spaceComplexity: 'O(1)',
    operations: [
      {
        name: 'Basic Operations',
        complexity: 'O(n)',
        description: 'Linear operations',
        examples: [1, 10, 100, 1000, 10000]
      }
    ]
  };
}

function calculateOperationCount(complexity: string, n: number): number {
  // Parse complexity notation and calculate operation count
  const cleanComplexity = complexity.replace(/O\(|\)/g, '').trim();
  
  switch (cleanComplexity) {
    case '1':
      return 1;
    case 'log n':
      return Math.log2(n);
    case 'n':
      return n;
    case 'n log n':
      return n * Math.log2(n);
    case 'n²':
    case 'n^2':
      return n * n;
    case 'n³':
    case 'n^3':
      return n * n * n;
    case '2^n':
      return Math.min(Math.pow(2, n), Number.MAX_SAFE_INTEGER);
    case 'n!':
      return Math.min(factorial(n), Number.MAX_SAFE_INTEGER);
    default:
      // Try to evaluate simple expressions
      try {
        const expression = cleanComplexity
          .replace(/n/g, n.toString())
          .replace(/\^/g, '**')
          .replace(/log/g, 'Math.log2');
        return eval(expression) || n;
      } catch {
        return n;
      }
  }
}

function factorial(n: number): number {
  if (n <= 1) return 1;
  if (n > 20) return Number.MAX_SAFE_INTEGER; // Prevent overflow
  return n * factorial(n - 1);
}