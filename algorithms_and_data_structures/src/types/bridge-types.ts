// Code-to-Concept Bridge Types
export interface ConceptMapping {
  concepts: Concept[];
  codeToConceptMap: Record<string, string[]>; // code block ID to concept IDs
  conceptToCodeMap: Record<string, string[]>; // concept ID to code block IDs
  relationships: ConceptRelationship[];
  metadata: {
    complexity: number;
    language: string;
    analysisTimestamp: Date;
  };
}

export interface Concept {
  id: string;
  name: string;
  category: 'control-flow' | 'data-structure' | 'algorithm' | 'pattern' | 'optimization';
  description: string;
  difficulty: 1 | 2 | 3 | 4 | 5;
  codeTemplate: string;
  examples: string[];
  relatedConcepts: string[];
  visualRepresentation?: VisualElement;
}

export interface ConceptRelationship {
  source: string;
  target: string;
  type: 'depends-on' | 'composed-of' | 'similar-to' | 'alternative-to';
  strength: number; // 0-1
}

export interface CodeBlock {
  id: string;
  startLine: number;
  endLine: number;
  code: string;
  concepts: string[];
  metadata?: {
    complexity?: number;
    executionTime?: number;
    memoryUsage?: number;
  };
}

export interface VisualElement {
  type: 'flowchart' | 'diagram' | 'animation' | 'graph';
  data: any;
  layout: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
}

export type VisualizationMode = 'simplified' | 'flowchart' | 'detailed' | 'interactive';