import { EventEmitter } from 'events';
import { v4 as uuidv4 } from 'uuid';
import * as yaml from 'js-yaml';
import { WorkflowDefinition, WorkflowTask, WorkflowTrigger, WorkflowCondition } from './WorkflowEngine';

export interface NodePosition {
  x: number;
  y: number;
}

export interface WorkflowNode {
  id: string;
  type: 'task' | 'condition' | 'trigger' | 'start' | 'end' | 'fork' | 'join';
  position: NodePosition;
  data: any;
  inputs: Connection[];
  outputs: Connection[];
  validation?: ValidationResult;
}

export interface Connection {
  id: string;
  sourceNodeId: string;
  targetNodeId: string;
  sourceHandle?: string;
  targetHandle?: string;
  condition?: string;
}

export interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

export interface WorkflowTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  tags: string[];
  nodes: WorkflowNode[];
  connections: Connection[];
  variables: Record<string, any>;
  metadata: Record<string, any>;
  thumbnail?: string;
}

export interface BuilderState {
  nodes: WorkflowNode[];
  connections: Connection[];
  variables: Record<string, any>;
  metadata: Record<string, any>;
  zoom: number;
  pan: { x: number; y: number };
  selection: string[];
  clipboard?: { nodes: WorkflowNode[]; connections: Connection[] };
}

export class AutomationBuilder extends EventEmitter {
  private state: BuilderState = {
    nodes: [],
    connections: [],
    variables: {},
    metadata: {},
    zoom: 1,
    pan: { x: 0, y: 0 },
    selection: []
  };
  
  private templates = new Map<string, WorkflowTemplate>();
  private taskLibrary = new Map<string, TaskDefinition>();
  private undoStack: BuilderState[] = [];
  private redoStack: BuilderState[] = [];
  private maxUndoSteps = 50;

  constructor() {
    super();
    this.initializeTaskLibrary();
    this.loadDefaultTemplates();
  }

  /**
   * Initialize task library with built-in tasks
   */
  private initializeTaskLibrary(): void {
    const builtInTasks: TaskDefinition[] = [
      {
        type: 'file:read',
        name: 'Read File',
        description: 'Read content from a file',
        category: 'File Operations',
        icon: 'file-text',
        inputs: [
          { name: 'path', type: 'string', required: true, description: 'File path' },
          { name: 'encoding', type: 'string', default: 'utf8', description: 'File encoding' }
        ],
        outputs: [
          { name: 'content', type: 'string', description: 'File content' }
        ]
      },
      {
        type: 'file:write',
        name: 'Write File',
        description: 'Write content to a file',
        category: 'File Operations',
        icon: 'save',
        inputs: [
          { name: 'path', type: 'string', required: true, description: 'File path' },
          { name: 'content', type: 'string', required: true, description: 'Content to write' },
          { name: 'encoding', type: 'string', default: 'utf8', description: 'File encoding' }
        ],
        outputs: [
          { name: 'bytesWritten', type: 'number', description: 'Bytes written' }
        ]
      },
      {
        type: 'http:request',
        name: 'HTTP Request',
        description: 'Make an HTTP request',
        category: 'Network',
        icon: 'globe',
        inputs: [
          { name: 'url', type: 'string', required: true, description: 'Request URL' },
          { name: 'method', type: 'select', options: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'], default: 'GET', description: 'HTTP method' },
          { name: 'headers', type: 'object', description: 'Request headers' },
          { name: 'data', type: 'object', description: 'Request body' },
          { name: 'timeout', type: 'number', default: 30000, description: 'Timeout in ms' }
        ],
        outputs: [
          { name: 'status', type: 'number', description: 'Response status code' },
          { name: 'headers', type: 'object', description: 'Response headers' },
          { name: 'data', type: 'object', description: 'Response data' }
        ]
      },
      {
        type: 'shell:exec',
        name: 'Execute Command',
        description: 'Execute a shell command',
        category: 'System',
        icon: 'terminal',
        inputs: [
          { name: 'command', type: 'string', required: true, description: 'Command to execute' },
          { name: 'cwd', type: 'string', description: 'Working directory' },
          { name: 'env', type: 'object', description: 'Environment variables' }
        ],
        outputs: [
          { name: 'stdout', type: 'string', description: 'Standard output' },
          { name: 'stderr', type: 'string', description: 'Standard error' },
          { name: 'exitCode', type: 'number', description: 'Exit code' }
        ]
      },
      {
        type: 'data:transform',
        name: 'Transform Data',
        description: 'Transform data using JavaScript',
        category: 'Data',
        icon: 'code',
        inputs: [
          { name: 'data', type: 'any', required: true, description: 'Input data' },
          { name: 'expression', type: 'text', required: true, description: 'Transformation expression' }
        ],
        outputs: [
          { name: 'result', type: 'any', description: 'Transformed data' }
        ]
      },
      {
        type: 'util:wait',
        name: 'Wait',
        description: 'Wait for specified duration',
        category: 'Utility',
        icon: 'clock',
        inputs: [
          { name: 'duration', type: 'number', required: true, description: 'Wait duration' },
          { name: 'unit', type: 'select', options: ['ms', 's', 'm', 'h'], default: 'ms', description: 'Time unit' }
        ],
        outputs: [
          { name: 'waited', type: 'number', description: 'Actual wait time' }
        ]
      }
    ];

    builtInTasks.forEach(task => {
      this.taskLibrary.set(task.type, task);
    });
  }

  /**
   * Load default workflow templates
   */
  private loadDefaultTemplates(): void {
    const defaultTemplates: WorkflowTemplate[] = [
      {
        id: 'simple-automation',
        name: 'Simple Automation',
        description: 'Basic file processing workflow',
        category: 'Getting Started',
        tags: ['basic', 'file'],
        nodes: [
          {
            id: 'start',
            type: 'start',
            position: { x: 100, y: 100 },
            data: {},
            inputs: [],
            outputs: []
          },
          {
            id: 'read-file',
            type: 'task',
            position: { x: 300, y: 100 },
            data: {
              taskType: 'file:read',
              config: {
                path: '{{inputFile}}',
                encoding: 'utf8'
              }
            },
            inputs: [],
            outputs: []
          },
          {
            id: 'transform-data',
            type: 'task',
            position: { x: 500, y: 100 },
            data: {
              taskType: 'data:transform',
              config: {
                data: '{{read-file.content}}',
                expression: 'data.toUpperCase()'
              }
            },
            inputs: [],
            outputs: []
          },
          {
            id: 'write-file',
            type: 'task',
            position: { x: 700, y: 100 },
            data: {
              taskType: 'file:write',
              config: {
                path: '{{outputFile}}',
                content: '{{transform-data.result}}'
              }
            },
            inputs: [],
            outputs: []
          },
          {
            id: 'end',
            type: 'end',
            position: { x: 900, y: 100 },
            data: {},
            inputs: [],
            outputs: []
          }
        ],
        connections: [
          { id: 'c1', sourceNodeId: 'start', targetNodeId: 'read-file' },
          { id: 'c2', sourceNodeId: 'read-file', targetNodeId: 'transform-data' },
          { id: 'c3', sourceNodeId: 'transform-data', targetNodeId: 'write-file' },
          { id: 'c4', sourceNodeId: 'write-file', targetNodeId: 'end' }
        ],
        variables: {
          inputFile: 'input.txt',
          outputFile: 'output.txt'
        },
        metadata: {
          author: 'System',
          version: '1.0.0'
        }
      }
    ];

    defaultTemplates.forEach(template => {
      this.templates.set(template.id, template);
    });
  }

  /**
   * Create new workflow node
   */
  addNode(type: string, position: NodePosition, data: any = {}): string {
    this.saveState();
    
    const nodeId = uuidv4();
    const node: WorkflowNode = {
      id: nodeId,
      type: type as any,
      position,
      data,
      inputs: [],
      outputs: []
    };

    this.state.nodes.push(node);
    this.validateWorkflow();
    this.emit('node:added', node);
    
    return nodeId;
  }

  /**
   * Update node data
   */
  updateNode(nodeId: string, data: Partial<WorkflowNode>): boolean {
    const node = this.state.nodes.find(n => n.id === nodeId);
    if (!node) return false;

    this.saveState();
    Object.assign(node, data);
    this.validateWorkflow();
    this.emit('node:updated', node);
    
    return true;
  }

  /**
   * Remove node and its connections
   */
  removeNode(nodeId: string): boolean {
    const nodeIndex = this.state.nodes.findIndex(n => n.id === nodeId);
    if (nodeIndex === -1) return false;

    this.saveState();
    
    // Remove node
    this.state.nodes.splice(nodeIndex, 1);
    
    // Remove associated connections
    this.state.connections = this.state.connections.filter(
      conn => conn.sourceNodeId !== nodeId && conn.targetNodeId !== nodeId
    );
    
    this.validateWorkflow();
    this.emit('node:removed', nodeId);
    
    return true;
  }

  /**
   * Add connection between nodes
   */
  addConnection(
    sourceNodeId: string, 
    targetNodeId: string, 
    sourceHandle?: string, 
    targetHandle?: string
  ): string {
    // Prevent self-connections and duplicate connections
    if (sourceNodeId === targetNodeId) {
      throw new Error('Cannot connect node to itself');
    }

    const existingConnection = this.state.connections.find(
      conn => conn.sourceNodeId === sourceNodeId && conn.targetNodeId === targetNodeId
    );
    
    if (existingConnection) {
      throw new Error('Connection already exists');
    }

    this.saveState();
    
    const connectionId = uuidv4();
    const connection: Connection = {
      id: connectionId,
      sourceNodeId,
      targetNodeId,
      sourceHandle,
      targetHandle
    };

    this.state.connections.push(connection);
    this.validateWorkflow();
    this.emit('connection:added', connection);
    
    return connectionId;
  }

  /**
   * Remove connection
   */
  removeConnection(connectionId: string): boolean {
    const connectionIndex = this.state.connections.findIndex(c => c.id === connectionId);
    if (connectionIndex === -1) return false;

    this.saveState();
    
    const connection = this.state.connections[connectionIndex];
    this.state.connections.splice(connectionIndex, 1);
    
    this.validateWorkflow();
    this.emit('connection:removed', connection);
    
    return true;
  }

  /**
   * Validate entire workflow
   */
  validateWorkflow(): ValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];

    // Check for start and end nodes
    const startNodes = this.state.nodes.filter(n => n.type === 'start');
    const endNodes = this.state.nodes.filter(n => n.type === 'end');
    
    if (startNodes.length === 0) {
      errors.push('Workflow must have a start node');
    }
    if (startNodes.length > 1) {
      warnings.push('Workflow has multiple start nodes');
    }
    if (endNodes.length === 0) {
      warnings.push('Workflow should have an end node');
    }

    // Check for disconnected nodes
    const connectedNodes = new Set();
    this.state.connections.forEach(conn => {
      connectedNodes.add(conn.sourceNodeId);
      connectedNodes.add(conn.targetNodeId);
    });

    const disconnectedNodes = this.state.nodes.filter(
      node => !connectedNodes.has(node.id) && node.type !== 'start' && node.type !== 'end'
    );
    
    if (disconnectedNodes.length > 0) {
      warnings.push(`${disconnectedNodes.length} nodes are not connected`);
    }

    // Check for circular dependencies
    if (this.hasCircularDependency()) {
      errors.push('Workflow contains circular dependencies');
    }

    // Validate individual nodes
    this.state.nodes.forEach(node => {
      const nodeValidation = this.validateNode(node);
      if (nodeValidation.errors.length > 0) {
        errors.push(...nodeValidation.errors.map(err => `Node ${node.id}: ${err}`));
      }
      if (nodeValidation.warnings.length > 0) {
        warnings.push(...nodeValidation.warnings.map(warn => `Node ${node.id}: ${warn}`));
      }
      
      node.validation = nodeValidation;
    });

    const result: ValidationResult = {
      isValid: errors.length === 0,
      errors,
      warnings
    };

    this.emit('validation:completed', result);
    return result;
  }

  /**
   * Validate individual node
   */
  private validateNode(node: WorkflowNode): ValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];

    if (node.type === 'task') {
      const taskDef = this.taskLibrary.get(node.data.taskType);
      if (!taskDef) {
        errors.push(`Unknown task type: ${node.data.taskType}`);
      } else {
        // Validate required inputs
        const config = node.data.config || {};
        taskDef.inputs.forEach(input => {
          if (input.required && !(input.name in config)) {
            errors.push(`Missing required input: ${input.name}`);
          }
        });
      }
    }

    if (node.type === 'condition' && !node.data.expression) {
      errors.push('Condition node requires an expression');
    }

    return { isValid: errors.length === 0, errors, warnings };
  }

  /**
   * Check for circular dependencies
   */
  private hasCircularDependency(): boolean {
    const visited = new Set<string>();
    const recursionStack = new Set<string>();

    const hasCycle = (nodeId: string): boolean => {
      if (recursionStack.has(nodeId)) return true;
      if (visited.has(nodeId)) return false;

      visited.add(nodeId);
      recursionStack.add(nodeId);

      const outgoingConnections = this.state.connections.filter(
        conn => conn.sourceNodeId === nodeId
      );

      for (const conn of outgoingConnections) {
        if (hasCycle(conn.targetNodeId)) return true;
      }

      recursionStack.delete(nodeId);
      return false;
    };

    return this.state.nodes.some(node => hasCycle(node.id));
  }

  /**
   * Generate workflow definition from visual workflow
   */
  generateWorkflowDefinition(): WorkflowDefinition {
    const validation = this.validateWorkflow();
    if (!validation.isValid) {
      throw new Error(`Cannot generate workflow with validation errors: ${validation.errors.join(', ')}`);
    }

    const tasks: WorkflowTask[] = [];
    const triggers: WorkflowTrigger[] = [];

    // Convert nodes to tasks
    this.state.nodes.forEach(node => {
      if (node.type === 'task') {
        const dependencies = this.getNodeDependencies(node.id);
        
        const task: WorkflowTask = {
          id: node.id,
          name: node.data.name || node.data.taskType,
          type: node.data.taskType,
          config: node.data.config || {},
          dependsOn: dependencies.length > 0 ? dependencies : undefined,
          condition: node.data.condition,
          parallel: node.data.parallel,
          timeout: node.data.timeout,
          retries: node.data.retries,
          continueOnError: node.data.continueOnError,
          variables: node.data.variables
        };

        tasks.push(task);
      } else if (node.type === 'trigger') {
        const trigger: WorkflowTrigger = {
          type: node.data.triggerType,
          config: node.data.config || {},
          conditions: node.data.conditions
        };
        
        triggers.push(trigger);
      }
    });

    const workflowDefinition: WorkflowDefinition = {
      name: this.state.metadata.name || 'Generated Workflow',
      version: this.state.metadata.version || '1.0.0',
      description: this.state.metadata.description,
      variables: this.state.variables,
      triggers: triggers.length > 0 ? triggers : undefined,
      tasks,
      timeout: this.state.metadata.timeout,
      retries: this.state.metadata.retries
    };

    return workflowDefinition;
  }

  /**
   * Get dependencies for a node
   */
  private getNodeDependencies(nodeId: string): string[] {
    return this.state.connections
      .filter(conn => conn.targetNodeId === nodeId)
      .map(conn => conn.sourceNodeId)
      .filter(id => this.state.nodes.find(n => n.id === id)?.type === 'task');
  }

  /**
   * Load workflow from definition
   */
  loadWorkflowDefinition(definition: WorkflowDefinition): void {
    this.saveState();
    this.clearWorkflow();

    let yPosition = 100;
    const xSpacing = 200;
    let xPosition = 100;

    // Add start node
    const startNodeId = this.addNode('start', { x: xPosition, y: yPosition });
    xPosition += xSpacing;

    // Add task nodes
    const nodeIdMap = new Map<string, string>();
    definition.tasks.forEach(task => {
      const nodeId = this.addNode('task', { x: xPosition, y: yPosition }, {
        name: task.name,
        taskType: task.type,
        config: task.config,
        condition: task.condition,
        parallel: task.parallel,
        timeout: task.timeout,
        retries: task.retries,
        continueOnError: task.continueOnError,
        variables: task.variables
      });
      
      nodeIdMap.set(task.id, nodeId);
      xPosition += xSpacing;
    });

    // Add end node
    const endNodeId = this.addNode('end', { x: xPosition, y: yPosition });

    // Add connections based on dependencies
    definition.tasks.forEach(task => {
      const nodeId = nodeIdMap.get(task.id);
      if (!nodeId) return;

      if (task.dependsOn) {
        task.dependsOn.forEach(depId => {
          const depNodeId = nodeIdMap.get(depId);
          if (depNodeId) {
            this.addConnection(depNodeId, nodeId);
          }
        });
      } else {
        // Connect to start node if no dependencies
        this.addConnection(startNodeId, nodeId);
      }
    });

    // Connect last tasks to end node
    const tasksWithNoDependents = definition.tasks.filter(task => {
      return !definition.tasks.some(t => t.dependsOn?.includes(task.id));
    });

    tasksWithNoDependents.forEach(task => {
      const nodeId = nodeIdMap.get(task.id);
      if (nodeId) {
        this.addConnection(nodeId, endNodeId);
      }
    });

    // Set workflow metadata
    this.state.variables = definition.variables || {};
    this.state.metadata = {
      name: definition.name,
      version: definition.version,
      description: definition.description,
      timeout: definition.timeout,
      retries: definition.retries
    };

    this.emit('workflow:loaded', definition);
  }

  /**
   * Clear workflow
   */
  clearWorkflow(): void {
    this.saveState();
    this.state.nodes = [];
    this.state.connections = [];
    this.state.variables = {};
    this.state.metadata = {};
    this.state.selection = [];
    
    this.emit('workflow:cleared');
  }

  /**
   * Export workflow as YAML
   */
  exportAsYAML(): string {
    const definition = this.generateWorkflowDefinition();
    return yaml.dump(definition, { indent: 2, lineWidth: -1 });
  }

  /**
   * Export workflow as JSON
   */
  exportAsJSON(): string {
    const definition = this.generateWorkflowDefinition();
    return JSON.stringify(definition, null, 2);
  }

  /**
   * Save current state for undo
   */
  private saveState(): void {
    this.undoStack.push(JSON.parse(JSON.stringify(this.state)));
    if (this.undoStack.length > this.maxUndoSteps) {
      this.undoStack.shift();
    }
    this.redoStack = []; // Clear redo stack when new action is performed
  }

  /**
   * Undo last action
   */
  undo(): boolean {
    if (this.undoStack.length === 0) return false;

    this.redoStack.push(JSON.parse(JSON.stringify(this.state)));
    this.state = this.undoStack.pop()!;
    
    this.emit('state:undo');
    return true;
  }

  /**
   * Redo last undone action
   */
  redo(): boolean {
    if (this.redoStack.length === 0) return false;

    this.undoStack.push(JSON.parse(JSON.stringify(this.state)));
    this.state = this.redoStack.pop()!;
    
    this.emit('state:redo');
    return true;
  }

  /**
   * Copy selected nodes
   */
  copy(): void {
    const selectedNodes = this.state.nodes.filter(n => this.state.selection.includes(n.id));
    const selectedConnections = this.state.connections.filter(c => 
      this.state.selection.includes(c.sourceNodeId) && this.state.selection.includes(c.targetNodeId)
    );

    this.state.clipboard = {
      nodes: JSON.parse(JSON.stringify(selectedNodes)),
      connections: JSON.parse(JSON.stringify(selectedConnections))
    };

    this.emit('clipboard:copy', this.state.clipboard);
  }

  /**
   * Paste from clipboard
   */
  paste(offset: NodePosition = { x: 50, y: 50 }): void {
    if (!this.state.clipboard) return;

    this.saveState();

    const idMap = new Map<string, string>();
    
    // Paste nodes with new IDs
    this.state.clipboard.nodes.forEach(node => {
      const newId = uuidv4();
      idMap.set(node.id, newId);
      
      const newNode: WorkflowNode = {
        ...node,
        id: newId,
        position: {
          x: node.position.x + offset.x,
          y: node.position.y + offset.y
        }
      };
      
      this.state.nodes.push(newNode);
    });

    // Paste connections with updated node IDs
    this.state.clipboard.connections.forEach(conn => {
      const newConnection: Connection = {
        ...conn,
        id: uuidv4(),
        sourceNodeId: idMap.get(conn.sourceNodeId)!,
        targetNodeId: idMap.get(conn.targetNodeId)!
      };
      
      this.state.connections.push(newConnection);
    });

    // Update selection to pasted nodes
    this.state.selection = Array.from(idMap.values());
    
    this.validateWorkflow();
    this.emit('clipboard:paste', { nodes: idMap.size, connections: this.state.clipboard.connections.length });
  }

  /**
   * Auto-layout workflow
   */
  autoLayout(): void {
    this.saveState();

    // Simple hierarchical layout
    const levels = this.calculateNodeLevels();
    const levelWidth = 250;
    const nodeHeight = 80;
    const levelHeight = 150;

    levels.forEach((nodeIds, level) => {
      const x = 100 + (level * levelWidth);
      nodeIds.forEach((nodeId, index) => {
        const y = 100 + (index * levelHeight);
        const node = this.state.nodes.find(n => n.id === nodeId);
        if (node) {
          node.position = { x, y };
        }
      });
    });

    this.emit('layout:auto');
  }

  /**
   * Calculate node levels for layout
   */
  private calculateNodeLevels(): Map<number, string[]> {
    const levels = new Map<number, string[]>();
    const nodeLevel = new Map<string, number>();

    // Find start nodes
    const startNodes = this.state.nodes
      .filter(n => n.type === 'start')
      .map(n => n.id);

    if (startNodes.length === 0) {
      // If no start nodes, use nodes with no incoming connections
      const nodesWithIncoming = new Set(this.state.connections.map(c => c.targetNodeId));
      startNodes.push(...this.state.nodes
        .filter(n => !nodesWithIncoming.has(n.id))
        .map(n => n.id)
      );
    }

    // BFS to assign levels
    const queue = startNodes.map(id => ({ id, level: 0 }));
    const visited = new Set<string>();

    while (queue.length > 0) {
      const { id, level } = queue.shift()!;
      
      if (visited.has(id)) continue;
      visited.add(id);

      nodeLevel.set(id, level);
      
      if (!levels.has(level)) {
        levels.set(level, []);
      }
      levels.get(level)!.push(id);

      // Add child nodes to queue
      const childConnections = this.state.connections.filter(c => c.sourceNodeId === id);
      childConnections.forEach(conn => {
        if (!visited.has(conn.targetNodeId)) {
          queue.push({ id: conn.targetNodeId, level: level + 1 });
        }
      });
    }

    return levels;
  }

  // Public API methods

  getState(): BuilderState {
    return JSON.parse(JSON.stringify(this.state));
  }

  setState(state: BuilderState): void {
    this.saveState();
    this.state = JSON.parse(JSON.stringify(state));
    this.validateWorkflow();
    this.emit('state:changed');
  }

  getTaskLibrary(): Map<string, TaskDefinition> {
    return new Map(this.taskLibrary);
  }

  addTaskToLibrary(definition: TaskDefinition): void {
    this.taskLibrary.set(definition.type, definition);
    this.emit('library:task:added', definition);
  }

  getTemplates(): Map<string, WorkflowTemplate> {
    return new Map(this.templates);
  }

  addTemplate(template: WorkflowTemplate): void {
    this.templates.set(template.id, template);
    this.emit('library:template:added', template);
  }

  loadTemplate(templateId: string): boolean {
    const template = this.templates.get(templateId);
    if (!template) return false;

    this.saveState();
    this.state.nodes = JSON.parse(JSON.stringify(template.nodes));
    this.state.connections = JSON.parse(JSON.stringify(template.connections));
    this.state.variables = JSON.parse(JSON.stringify(template.variables));
    this.state.metadata = JSON.parse(JSON.stringify(template.metadata));

    this.validateWorkflow();
    this.emit('template:loaded', template);
    
    return true;
  }

  setSelection(nodeIds: string[]): void {
    this.state.selection = [...nodeIds];
    this.emit('selection:changed', this.state.selection);
  }

  setZoom(zoom: number): void {
    this.state.zoom = Math.max(0.1, Math.min(3, zoom));
    this.emit('view:zoom', this.state.zoom);
  }

  setPan(pan: { x: number; y: number }): void {
    this.state.pan = { ...pan };
    this.emit('view:pan', this.state.pan);
  }

  searchNodes(query: string): WorkflowNode[] {
    const lowercaseQuery = query.toLowerCase();
    return this.state.nodes.filter(node => 
      node.data.name?.toLowerCase().includes(lowercaseQuery) ||
      node.type.toLowerCase().includes(lowercaseQuery) ||
      node.data.taskType?.toLowerCase().includes(lowercaseQuery)
    );
  }

  getNodeById(nodeId: string): WorkflowNode | undefined {
    return this.state.nodes.find(n => n.id === nodeId);
  }

  getConnectionById(connectionId: string): Connection | undefined {
    return this.state.connections.find(c => c.id === connectionId);
  }

  canUndo(): boolean {
    return this.undoStack.length > 0;
  }

  canRedo(): boolean {
    return this.redoStack.length > 0;
  }
}

// Supporting interfaces for task library
export interface TaskDefinition {
  type: string;
  name: string;
  description: string;
  category: string;
  icon?: string;
  inputs: TaskInputDefinition[];
  outputs: TaskOutputDefinition[];
}

export interface TaskInputDefinition {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'object' | 'array' | 'select' | 'text' | 'any';
  required?: boolean;
  default?: any;
  options?: string[];
  description?: string;
}

export interface TaskOutputDefinition {
  name: string;
  type: string;
  description?: string;
}