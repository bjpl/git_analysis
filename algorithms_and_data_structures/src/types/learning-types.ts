// Learning Component Types
export interface AlgorithmStep {
  id: string;
  title: string;
  description: string;
  code?: string;
  visualization?: VisualizationData;
  timing?: number;
}

export interface VisualizationData {
  type: 'array' | 'tree' | 'graph' | 'list' | 'stack' | 'queue';
  data: any[];
  highlights?: number[];
  annotations?: Annotation[];
}

export interface Annotation {
  position: { x: number; y: number };
  text: string;
  type: 'info' | 'warning' | 'success' | 'error';
}

export interface DataStructureNode {
  id: string;
  value: any;
  type: 'node' | 'edge' | 'root';
  position: { x: number; y: number };
  children?: DataStructureNode[];
  metadata?: Record<string, any>;
}

export interface ComplexityAnalysis {
  timeComplexity: {
    best: string;
    average: string;
    worst: string;
  };
  spaceComplexity: string;
  operations: ComplexityOperation[];
}

export interface ComplexityOperation {
  name: string;
  complexity: string;
  description: string;
  examples: number[];
}

export interface LearningPattern {
  id: string;
  name: string;
  category: 'sorting' | 'searching' | 'graph' | 'dynamic' | 'greedy';
  difficulty: 1 | 2 | 3 | 4 | 5;
  signature: string[];
  examples: string[];
}

export interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: string;
  criteria: AchievementCriteria;
  unlocked: boolean;
  unlockedAt?: Date;
}

export interface AchievementCriteria {
  type: 'completion' | 'streak' | 'time' | 'accuracy';
  target: number;
  current: number;
}

export interface UserProgress {
  userId: string;
  completedModules: string[];
  achievements: Achievement[];
  stats: {
    algorithmsCompleted: number;
    patternsRecognized: number;
    collaborationPoints: number;
    streakDays: number;
  };
}

export interface CollaborationSession {
  id: string;
  participants: string[];
  algorithm: string;
  status: 'active' | 'paused' | 'completed';
  createdAt: Date;
  messages: CollaborationMessage[];
}

export interface CollaborationMessage {
  id: string;
  userId: string;
  content: string;
  type: 'text' | 'code' | 'annotation';
  timestamp: Date;
}