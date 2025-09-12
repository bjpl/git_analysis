import React, { useState, useEffect, useCallback } from 'react';
import { SimulationScenario, SimulationResult } from '../types/simulation-types';
import { ScenarioSelector } from './ScenarioSelector';
import { SimulationCanvas } from './SimulationCanvas';
import { SimulationControls } from './SimulationControls';
import { ResultsPanel } from './ResultsPanel';

interface RealWorldSimulatorProps {
  onSimulationComplete?: (result: SimulationResult) => void;
  onAlgorithmApplied?: (algorithm: string, scenario: string) => void;
}

export const RealWorldSimulator: React.FC<RealWorldSimulatorProps> = ({
  onSimulationComplete,
  onAlgorithmApplied
}) => {
  const [selectedScenario, setSelectedScenario] = useState<SimulationScenario | null>(null);
  const [selectedAlgorithm, setSelectedAlgorithm] = useState<string>('');
  const [simulationState, setSimulationState] = useState<'setup' | 'running' | 'paused' | 'completed'>('setup');
  const [currentStep, setCurrentStep] = useState(0);
  const [simulationData, setSimulationData] = useState<any>(null);
  const [results, setResults] = useState<SimulationResult | null>(null);
  const [speed, setSpeed] = useState(1000);
  const [showComparison, setShowComparison] = useState(false);

  // Available scenarios
  const scenarios: SimulationScenario[] = [
    {
      id: 'traffic-optimization',
      title: 'Traffic Light Optimization',
      description: 'Optimize traffic flow at busy intersections using different algorithms',
      category: 'optimization',
      difficulty: 'intermediate',
      applicableAlgorithms: ['greedy', 'dynamic-programming', 'graph-shortest-path'],
      initialData: {
        intersections: 4,
        trafficDensity: 'medium',
        peakHours: [8, 17],
        constraints: ['emergency-vehicles', 'pedestrian-crossings']
      },
      metrics: ['average-wait-time', 'throughput', 'fuel-consumption', 'emissions']
    },
    {
      id: 'delivery-routing',
      title: 'Package Delivery Routing',
      description: 'Find optimal routes for package delivery trucks in urban areas',
      category: 'optimization',
      difficulty: 'advanced',
      applicableAlgorithms: ['traveling-salesman', 'dijkstra', 'genetic-algorithm', 'ant-colony'],
      initialData: {
        deliveryPoints: 20,
        truckCapacity: 50,
        timeWindows: true,
        trafficConditions: 'variable'
      },
      metrics: ['total-distance', 'delivery-time', 'fuel-cost', 'customer-satisfaction']
    },
    {
      id: 'network-packet-routing',
      title: 'Network Packet Routing',
      description: 'Route data packets through network nodes efficiently',
      category: 'networking',
      difficulty: 'intermediate',
      applicableAlgorithms: ['dijkstra', 'bellman-ford', 'flooding', 'load-balancing'],
      initialData: {
        nodes: 15,
        connections: 30,
        packetLoad: 'high',
        nodeFailures: true
      },
      metrics: ['latency', 'throughput', 'packet-loss', 'load-distribution']
    },
    {
      id: 'resource-scheduling',
      title: 'Hospital Resource Scheduling',
      description: 'Schedule medical resources and staff efficiently in a hospital',
      category: 'scheduling',
      difficulty: 'advanced',
      applicableAlgorithms: ['priority-queue', 'greedy', 'constraint-satisfaction', 'genetic-algorithm'],
      initialData: {
        resources: ['OR-rooms', 'ICU-beds', 'staff', 'equipment'],
        patients: 50,
        priorities: ['emergency', 'urgent', 'scheduled'],
        constraints: ['staff-hours', 'equipment-availability', 'patient-preferences']
      },
      metrics: ['resource-utilization', 'patient-wait-time', 'staff-workload', 'cost-efficiency']
    },
    {
      id: 'social-media-feed',
      title: 'Social Media Feed Ranking',
      description: 'Rank posts in a social media feed based on user engagement',
      category: 'ranking',
      difficulty: 'intermediate',
      applicableAlgorithms: ['machine-learning', 'collaborative-filtering', 'content-based', 'trending-algorithm'],
      initialData: {
        users: 1000,
        posts: 5000,
        interactions: ['likes', 'shares', 'comments', 'time-spent'],
        userPreferences: 'diverse'
      },
      metrics: ['engagement-rate', 'time-on-feed', 'user-satisfaction', 'content-diversity']
    },
    {
      id: 'inventory-management',
      title: 'Warehouse Inventory Management',
      description: 'Optimize inventory levels and restocking schedules',
      category: 'optimization',
      difficulty: 'beginner',
      applicableAlgorithms: ['abc-analysis', 'economic-order-quantity', 'just-in-time', 'predictive-analytics'],
      initialData: {
        products: 500,
        demandPatterns: 'seasonal',
        storageCapacity: 10000,
        supplierLeadTimes: 'variable'
      },
      metrics: ['inventory-turnover', 'stockout-rate', 'carrying-cost', 'service-level']
    }
  ];

  // Start simulation
  const startSimulation = useCallback(async () => {
    if (!selectedScenario || !selectedAlgorithm) return;

    setSimulationState('running');
    setCurrentStep(0);
    setResults(null);

    // Initialize simulation based on scenario and algorithm
    const initialState = await initializeSimulation(selectedScenario, selectedAlgorithm);
    setSimulationData(initialState);
    
    onAlgorithmApplied?.(selectedAlgorithm, selectedScenario.id);
  }, [selectedScenario, selectedAlgorithm, onAlgorithmApplied]);

  // Run simulation step
  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (simulationState === 'running' && simulationData) {
      interval = setInterval(() => {
        setCurrentStep(prev => {
          const newStep = prev + 1;
          
          // Update simulation state
          const newData = runSimulationStep(simulationData, selectedAlgorithm!, newStep);
          setSimulationData(newData);
          
          // Check if simulation is complete
          if (isSimulationComplete(newData, selectedScenario!)) {
            setSimulationState('completed');
            generateResults(newData, selectedScenario!, selectedAlgorithm!);
          }
          
          return newStep;
        });
      }, speed);
    }
    
    return () => clearInterval(interval);
  }, [simulationState, simulationData, selectedScenario, selectedAlgorithm, speed]);

  // Generate results when simulation completes
  const generateResults = useCallback((data: any, scenario: SimulationScenario, algorithm: string) => {
    const result: SimulationResult = {
      scenarioId: scenario.id,
      algorithm,
      metrics: calculateMetrics(data, scenario),
      steps: currentStep,
      duration: currentStep * speed,
      success: true,
      insights: generateInsights(data, scenario, algorithm)
    };
    
    setResults(result);
    onSimulationComplete?.(result);
  }, [currentStep, speed, onSimulationComplete]);

  const handlePauseResume = useCallback(() => {
    setSimulationState(prev => prev === 'running' ? 'paused' : 'running');
  }, []);

  const handleReset = useCallback(() => {
    setSimulationState('setup');
    setCurrentStep(0);
    setSimulationData(null);
    setResults(null);
  }, []);

  const handleScenarioSelect = useCallback((scenario: SimulationScenario) => {
    setSelectedScenario(scenario);
    setSelectedAlgorithm('');
    handleReset();
  }, [handleReset]);

  const handleAlgorithmSelect = useCallback((algorithm: string) => {
    setSelectedAlgorithm(algorithm);
  }, []);

  const handleSpeedChange = useCallback((newSpeed: number) => {
    setSpeed(newSpeed);
  }, []);

  const handleComparisonToggle = useCallback(() => {
    setShowComparison(!showComparison);
  }, [showComparison]);

  return (
    <div className="real-world-simulator">
      <div className="simulator-header">
        <h2>Real-World Algorithm Simulator</h2>
        <p>Apply algorithms to solve everyday problems and see their impact</p>
      </div>

      <div className="simulator-content">
        <div className="scenario-section">
          <ScenarioSelector
            scenarios={scenarios}
            selectedScenario={selectedScenario}
            onScenarioSelect={handleScenarioSelect}
          />
          
          {selectedScenario && (
            <div className="algorithm-selector">
              <h3>Choose Algorithm</h3>
              <div className="algorithm-options">
                {selectedScenario.applicableAlgorithms.map(algorithm => (
                  <button
                    key={algorithm}
                    className={selectedAlgorithm === algorithm ? 'active' : ''}
                    onClick={() => handleAlgorithmSelect(algorithm)}
                  >
                    {formatAlgorithmName(algorithm)}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="simulation-section">
          {selectedScenario && selectedAlgorithm && (
            <>
              <SimulationCanvas
                scenario={selectedScenario}
                algorithm={selectedAlgorithm}
                data={simulationData}
                step={currentStep}
                state={simulationState}
              />
              
              <SimulationControls
                state={simulationState}
                step={currentStep}
                speed={speed}
                onStart={startSimulation}
                onPauseResume={handlePauseResume}
                onReset={handleReset}
                onSpeedChange={handleSpeedChange}
                canStart={!!selectedScenario && !!selectedAlgorithm}
              />
            </>
          )}
        </div>

        <div className="results-section">
          {results && (
            <ResultsPanel
              results={results}
              scenario={selectedScenario!}
              onComparisonToggle={handleComparisonToggle}
              showComparison={showComparison}
            />
          )}
          
          {showComparison && selectedScenario && (
            <ComparisonPanel
              scenario={selectedScenario}
              baseResults={results}
            />
          )}
        </div>
      </div>

      <div className="educational-content">
        <div className="algorithm-explanation">
          {selectedAlgorithm && selectedScenario && (
            <AlgorithmExplanation
              algorithm={selectedAlgorithm}
              scenario={selectedScenario}
              currentStep={currentStep}
              data={simulationData}
            />
          )}
        </div>

        <div className="real-world-connections">
          <h3>Real-World Applications</h3>
          <div className="application-examples">
            {selectedScenario && (
              <div className="scenario-applications">
                <h4>{selectedScenario.title}</h4>
                <ul>
                  {getRealWorldApplications(selectedScenario.id).map((application, index) => (
                    <li key={index}>{application}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Supporting Components
interface ComparisonPanelProps {
  scenario: SimulationScenario;
  baseResults: SimulationResult | null;
}

const ComparisonPanel: React.FC<ComparisonPanelProps> = ({ scenario, baseResults }) => {
  const [comparisonResults, setComparisonResults] = useState<SimulationResult[]>([]);
  
  useEffect(() => {
    // Run simulations for all applicable algorithms
    const runComparisons = async () => {
      const results: SimulationResult[] = [];
      
      for (const algorithm of scenario.applicableAlgorithms) {
        if (baseResults && algorithm === baseResults.algorithm) {
          results.push(baseResults);
        } else {
          // Simulate other algorithms (this would be actual simulation in practice)
          const result = await simulateAlgorithm(scenario, algorithm);
          results.push(result);
        }
      }
      
      setComparisonResults(results);
    };
    
    runComparisons();
  }, [scenario, baseResults]);

  return (
    <div className="comparison-panel">
      <h3>Algorithm Comparison</h3>
      <div className="comparison-chart">
        <ComparisonChart results={comparisonResults} metrics={scenario.metrics} />
      </div>
      
      <div className="comparison-table">
        <table>
          <thead>
            <tr>
              <th>Algorithm</th>
              {scenario.metrics.map(metric => (
                <th key={metric}>{formatMetricName(metric)}</th>
              ))}
              <th>Overall Score</th>
            </tr>
          </thead>
          <tbody>
            {comparisonResults.map(result => (
              <tr key={result.algorithm}>
                <td>{formatAlgorithmName(result.algorithm)}</td>
                {scenario.metrics.map(metric => (
                  <td key={metric}>
                    {formatMetricValue(result.metrics[metric], metric)}
                  </td>
                ))}
                <td>{calculateOverallScore(result.metrics)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// Helper functions would be imported from separate modules
async function initializeSimulation(scenario: SimulationScenario, algorithm: string): Promise<any> {
  // Initialize simulation state based on scenario and algorithm
  return {
    scenario: scenario.id,
    algorithm,
    step: 0,
    state: scenario.initialData,
    metrics: {},
    history: []
  };
}

function runSimulationStep(data: any, algorithm: string, step: number): any {
  // Execute one step of the simulation
  return {
    ...data,
    step,
    // Update state based on algorithm logic
  };
}

function isSimulationComplete(data: any, scenario: SimulationScenario): boolean {
  // Check if simulation has reached completion criteria
  return data.step >= 100; // Example completion condition
}

function calculateMetrics(data: any, scenario: SimulationScenario): Record<string, number> {
  // Calculate performance metrics
  const metrics: Record<string, number> = {};
  
  scenario.metrics.forEach(metric => {
    metrics[metric] = Math.random() * 100; // Placeholder calculation
  });
  
  return metrics;
}

function generateInsights(data: any, scenario: SimulationScenario, algorithm: string): string[] {
  // Generate educational insights
  return [
    `The ${algorithm} algorithm performed well in this ${scenario.category} scenario`,
    `Key factors affecting performance: ${scenario.initialData}`,
    'Consider trade-offs between different metrics'
  ];
}

function formatAlgorithmName(algorithm: string): string {
  return algorithm
    .split('-')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

function formatMetricName(metric: string): string {
  return metric
    .split('-')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

function formatMetricValue(value: number, metric: string): string {
  if (metric.includes('time')) {
    return `${value.toFixed(1)}s`;
  } else if (metric.includes('cost') || metric.includes('distance')) {
    return `$${value.toFixed(2)}`;
  } else if (metric.includes('rate') || metric.includes('efficiency')) {
    return `${value.toFixed(1)}%`;
  }
  return value.toFixed(2);
}

function calculateOverallScore(metrics: Record<string, number>): number {
  const values = Object.values(metrics);
  return values.reduce((sum, val) => sum + val, 0) / values.length;
}

function getRealWorldApplications(scenarioId: string): string[] {
  const applications: Record<string, string[]> = {
    'traffic-optimization': [
      'Smart city traffic management systems',
      'Highway interchange optimization',
      'Emergency vehicle routing',
      'Public transit scheduling'
    ],
    'delivery-routing': [
      'Amazon delivery optimization',
      'FedEx route planning',
      'Uber Eats delivery routing',
      'Supply chain logistics'
    ],
    'network-packet-routing': [
      'Internet routing protocols',
      'Content delivery networks',
      'Telecommunications switching',
      'Data center networking'
    ],
    'resource-scheduling': [
      'Hospital operating room scheduling',
      'Manufacturing resource planning',
      'Cloud computing resource allocation',
      'University course scheduling'
    ],
    'social-media-feed': [
      'Facebook news feed algorithm',
      'Twitter timeline ranking',
      'LinkedIn professional updates',
      'TikTok recommendation engine'
    ],
    'inventory-management': [
      'Walmart inventory optimization',
      'Amazon warehouse management',
      'Pharmaceutical supply chains',
      'Automotive parts management'
    ]
  };
  
  return applications[scenarioId] || [];
}

async function simulateAlgorithm(scenario: SimulationScenario, algorithm: string): Promise<SimulationResult> {
  // This would run an actual simulation - simplified for demo
  return {
    scenarioId: scenario.id,
    algorithm,
    metrics: calculateMetrics({}, scenario),
    steps: Math.floor(Math.random() * 100) + 50,
    duration: Math.floor(Math.random() * 5000) + 1000,
    success: true,
    insights: generateInsights({}, scenario, algorithm)
  };
}

// Additional type definitions would be in simulation-types.ts
interface SimulationScenario {
  id: string;
  title: string;
  description: string;
  category: string;
  difficulty: string;
  applicableAlgorithms: string[];
  initialData: any;
  metrics: string[];
}

interface SimulationResult {
  scenarioId: string;
  algorithm: string;
  metrics: Record<string, number>;
  steps: number;
  duration: number;
  success: boolean;
  insights: string[];
}