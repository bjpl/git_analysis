// Real-World Simulator Types
export interface SimulationScenario {
  id: string;
  title: string;
  description: string;
  category: 'optimization' | 'networking' | 'scheduling' | 'ranking' | 'routing';
  difficulty: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  applicableAlgorithms: string[];
  initialData: Record<string, any>;
  metrics: string[];
  constraints?: SimulationConstraint[];
  realWorldContext: RealWorldContext;
}

export interface SimulationConstraint {
  id: string;
  name: string;
  type: 'hard' | 'soft';
  description: string;
  validator: (data: any) => boolean;
  penalty?: number;
}

export interface RealWorldContext {
  industry: string;
  company: string;
  stakeholders: string[];
  businessImpact: string;
  technicalChallenges: string[];
}

export interface SimulationResult {
  scenarioId: string;
  algorithm: string;
  metrics: Record<string, number>;
  steps: number;
  duration: number; // milliseconds
  success: boolean;
  insights: string[];
  optimizationSuggestions?: string[];
  comparativeAnalysis?: {
    vsOptimal: number; // percentage
    vsAverage: number; // percentage
  };
}

export interface SimulationStep {
  stepNumber: number;
  timestamp: Date;
  action: string;
  state: any;
  metrics: Record<string, number>;
  visualization?: VisualizationFrame;
}

export interface VisualizationFrame {
  type: 'network' | 'chart' | 'map' | 'timeline' | 'custom';
  data: any;
  highlights?: string[];
  annotations?: Array<{
    position: { x: number; y: number };
    text: string;
    type: 'info' | 'warning' | 'success' | 'error';
  }>;
}

export interface AlgorithmPerformance {
  algorithm: string;
  scenario: string;
  avgPerformance: Record<string, number>;
  bestCase: Record<string, number>;
  worstCase: Record<string, number>;
  reliability: number; // 0-1
  scalability: number; // 0-1
}