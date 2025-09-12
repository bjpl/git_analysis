# 📋 API Reference: Interactive Algorithms Learning Platform

## Table of Contents
- [Core Classes](#-core-classes)
- [Learning Modules](#-learning-modules)
- [Interactive Components](#-interactive-components)
- [SPARC Integration](#-sparc-integration)
- [Practice Engine](#-practice-engine)
- [Utility Classes](#-utility-classes)
- [Configuration API](#-configuration-api)
- [Event System](#-event-system)

## 🏗️ Core Classes

### `AlgorithmsDataStructuresLearning`

Main application class that orchestrates the learning platform.

```javascript
class AlgorithmsDataStructuresLearning {
  constructor(config?: PlatformConfig)
  
  // Core methods
  async start(): Promise<void>
  async loadModule(moduleName: string): Promise<LearningModule>
  async showMainMenu(): Promise<void>
  
  // Module management
  getAvailableModules(): Map<string, ModuleConfig>
  isModuleAvailable(moduleName: string): boolean
  
  // Progress tracking
  getOverallProgress(): ProgressStats
  exportLearningData(): LearningData
}
```

**Constructor Parameters:**
```typescript
interface PlatformConfig {
  theme?: 'light' | 'dark' | 'auto';
  language?: 'en' | 'es' | 'fr' | 'de';
  difficulty?: 'beginner' | 'intermediate' | 'advanced';
  analytics?: boolean;
  autoSave?: boolean;
}
```

**Example Usage:**
```javascript
import { AlgorithmsDataStructuresLearning } from './index.js';

const platform = new AlgorithmsDataStructuresLearning({
  theme: 'dark',
  difficulty: 'beginner',
  analytics: true
});

await platform.start();
```

### `ModuleSystem`

Handles loading, registration, and management of learning modules.

```javascript
class ModuleSystem {
  constructor()
  
  // Module management
  registerModule(name: string, config: ModuleConfig): void
  async loadModule(name: string, options?: LoadOptions): Promise<LearningModule>
  unloadModule(name: string): void
  
  // Module discovery
  getModule(name: string): LearningModule | null
  getAllModules(): Map<string, ModuleConfig>
  getModulesByCategory(category: string): ModuleConfig[]
  
  // Dependency management
  resolveDependencies(moduleName: string): string[]
  validatePrerequisites(moduleName: string, completedModules: string[]): boolean
}
```

**Types:**
```typescript
interface ModuleConfig {
  name: string;
  description: string;
  class: typeof LearningModule;
  practiceProblems: typeof PracticeEngine;
  icon: string;
  prerequisites: string[];
  estimatedTime: string;
  category: 'data-structures' | 'algorithms' | 'advanced';
  difficulty: 'beginner' | 'intermediate' | 'advanced';
}

interface LoadOptions {
  lazy?: boolean;
  cache?: boolean;
  timeout?: number;
}
```

### `ProgressTracker`

Tracks and analyzes learning progress across modules.

```javascript
class ProgressTracker {
  constructor(userId?: string)
  
  // Progress recording
  recordActivity(module: string, activity: ActivityType, timestamp?: number): void
  recordCompletion(module: string, score?: number): void
  markConceptCompleted(module: string, concept: string): void
  
  // Progress analysis
  getProgress(module?: string): ProgressStats
  calculateLearningVelocity(): LearningVelocity
  getNextSuggestions(): Suggestion[]
  
  // Analytics
  getTimeSpent(module: string): number
  getStrengthsAndWeaknesses(): AnalysisResult
  generateProgressReport(): ProgressReport
}
```

**Types:**
```typescript
interface ProgressStats {
  totalModules: number;
  completedModules: number;
  completionPercentage: number;
  timeSpent: number;
  conceptsMastered: number;
  averageScore: number;
  lastActivity: Date;
}

interface LearningVelocity {
  conceptsPerHour: number;
  modulesPerWeek: number;
  trend: 'increasing' | 'stable' | 'decreasing';
}

interface Suggestion {
  module: string;
  reason: string;
  confidence: number;
  estimatedTime: string;
}
```

## 📚 Learning Modules

### `LearningModule` (Base Class)

Abstract base class for all learning modules.

```javascript
abstract class LearningModule {
  constructor(config: ModuleConfig)
  
  // Core learning methods
  abstract async startLearningSession(): Promise<void>
  abstract async explainAnalogy(): Promise<void>
  abstract async demonstrateOperations(): Promise<void>
  
  // Progress management
  getProgress(): ModuleProgress
  markConceptCompleted(concept: string): void
  isCompleted(): boolean
  
  // Interactive elements
  showWelcome(): Promise<void>
  waitForUser(message?: string): Promise<void>
  
  // Assessment
  async assessLearning(): Promise<AssessmentResult>
  generateCertificate(): Certificate
}
```

**Types:**
```typescript
interface ModuleProgress {
  startTime: Date;
  completedConcepts: string[];
  totalConcepts: number;
  interactiveSessionsCompleted: number;
  practiceProblemsAttempted: number;
  practiceProblemsCompleted: number;
  currentDifficulty: 'beginner' | 'intermediate' | 'advanced';
}

interface AssessmentResult {
  score: number;
  conceptScores: Map<string, number>;
  recommendations: string[];
  certificate?: Certificate;
  nextSteps: string[];
}
```

### `BookshelfArray` (Arrays Module)

Learn arrays through bookshelf organization analogy.

```javascript
class BookshelfArray extends LearningModule {
  constructor()
  
  // Array-specific methods
  async demonstrateIndexing(): Promise<void>
  async demonstrateInsertion(): Promise<void>
  async demonstrateDeletion(): Promise<void>
  async demonstrateSearch(): Promise<void>
  
  // Interactive bookshelf
  createBookshelf(size: number): BookshelfVisualization
  addBook(title: string, position?: number): void
  removeBook(position: number): string | null
  findBook(title: string): number
  
  // Performance analysis
  analyzePerformance(operation: ArrayOperation, size: number): PerformanceMetrics
}
```

**Example Usage:**
```javascript
const arrayModule = new BookshelfArray();
await arrayModule.startLearningSession();

// Direct interaction with bookshelf
const bookshelf = arrayModule.createBookshelf(10);
arrayModule.addBook("JavaScript Guide", 0);
const position = arrayModule.findBook("JavaScript Guide");
```

### `TrainLinkedList` (Linked Lists Module)

Learn linked lists through train car analogy.

```javascript
class TrainLinkedList extends LearningModule {
  constructor()
  
  // Linked list operations
  async demonstrateTraversation(): Promise<void>
  async demonstrateInsertion(): Promise<void>
  async demonstrateDeletion(): Promise<void>
  
  // Train visualization
  createTrain(): TrainVisualization
  addCar(cargo: string, position?: number): void
  removeCar(position: number): TrainCar | null
  reverseTrain(): void
  
  // Advanced operations
  mergeTwoTrains(otherTrain: TrainLinkedList): void
  detectLoop(): boolean
  findMiddleCar(): TrainCar | null
}
```

### `CafeteriaPlateStack` (Stacks Module)

Learn stacks through cafeteria plate dispenser analogy.

```javascript
class CafeteriaPlateStack extends LearningModule {
  constructor()
  
  // Stack operations
  push(plate: Plate): void
  pop(): Plate | null
  peek(): Plate | null
  isEmpty(): boolean
  size(): number
  
  // Stack applications
  demonstrateUndoOperation(): Promise<void>
  demonstrateFunctionCalls(): Promise<void>
  demonstrateExpressionEvaluation(): Promise<void>
  
  // Visualization
  renderPlateStack(): string
  animatePushPop(): Promise<void>
}
```

## 🎮 Interactive Components

### `InteractiveComponent` (Base Class)

Base class for interactive learning components.

```javascript
abstract class InteractiveComponent {
  constructor(config: InteractiveConfig)
  
  // Core interaction methods
  abstract async start(): Promise<void>
  abstract async showCurrentState(): Promise<void>
  
  // User input handling
  async prompt(question: string, options?: PromptOptions): Promise<string>
  async promptChoice(question: string, choices: Choice[]): Promise<string>
  async promptAction(): Promise<Action>
  
  // State management
  saveState(): ComponentState
  loadState(state: ComponentState): void
  
  // Performance tracking
  startPerformanceTimer(): void
  endPerformanceTimer(): PerformanceMetrics
}
```

**Types:**
```typescript
interface InteractiveConfig {
  name: string;
  description: string;
  maxAttempts?: number;
  showHints?: boolean;
  trackPerformance?: boolean;
}

interface PromptOptions {
  validate?: (input: string) => boolean | string;
  transform?: (input: string) => any;
  default?: string;
}

interface Choice {
  name: string;
  value: string;
  description?: string;
}
```

### `AlgorithmPlayground`

Interactive algorithm visualization and experimentation.

```javascript
class AlgorithmPlayground extends InteractiveComponent {
  constructor()
  
  // Algorithm visualization
  async visualizeAlgorithm(algorithm: Algorithm, data: any[]): Promise<void>
  async stepThroughAlgorithm(algorithm: Algorithm, data: any[]): Promise<void>
  
  // Performance comparison
  async compareAlgorithms(algorithms: Algorithm[], datasets: any[][]): Promise<ComparisonResult>
  async benchmarkAlgorithm(algorithm: Algorithm, sizes: number[]): Promise<BenchmarkResult>
  
  // Interactive testing
  async customDatasetTest(): Promise<void>
  async parameterTuning(): Promise<void>
}
```

### `DataStructureBuilder`

Interactive data structure construction and manipulation.

```javascript
class DataStructureBuilder extends InteractiveComponent {
  constructor()
  
  // Structure building
  async buildStructure(type: DataStructureType): Promise<DataStructure>
  async manipulateStructure(structure: DataStructure, operations: Operation[]): Promise<void>
  
  // Visualization
  renderStructure(structure: DataStructure): string
  animateOperation(structure: DataStructure, operation: Operation): Promise<void>
  
  // Export/Import
  exportStructure(structure: DataStructure, format: ExportFormat): string
  importStructure(data: string, format: ExportFormat): DataStructure
}
```

## 🤖 SPARC Integration

### `SPARCOrchestrator`

Main orchestration class for SPARC methodology integration.

```javascript
class SPARCOrchestrator {
  constructor(config: SPARCConfig)
  
  // Workflow execution
  async executeWorkflow(phase: SPARCPhase, task: string): Promise<SPARCResult>
  async runFullPipeline(projectSpec: ProjectSpecification): Promise<ProjectResult>
  
  // Agent management
  async spawnAgent(type: AgentType, config?: AgentConfig): Promise<Agent>
  async coordinateAgents(agents: Agent[], task: string): Promise<CoordinationResult>
  
  // Phase execution
  async specification(requirements: Requirements): Promise<SpecificationResult>
  async pseudocode(specification: SpecificationResult): Promise<PseudocodeResult>
  async architecture(pseudocode: PseudocodeResult): Promise<ArchitectureResult>
  async refinement(architecture: ArchitectureResult): Promise<RefinementResult>
  async completion(refinement: RefinementResult): Promise<CompletionResult>
}
```

### `BaseAgent`

Base class for SPARC agents.

```javascript
abstract class BaseAgent {
  constructor(config: AgentConfig)
  
  // Core agent methods
  abstract async processTask(task: Task): Promise<TaskResult>
  
  // Communication
  async sendMessage(recipient: Agent, message: Message): Promise<void>
  async receiveMessage(sender: Agent, message: Message): Promise<void>
  
  // Coordination
  async coordinateWith(otherAgents: Agent[]): Promise<void>
  async shareKnowledge(knowledge: Knowledge): Promise<void>
  
  // Performance
  getPerformanceMetrics(): AgentMetrics
  optimizePerformance(): Promise<void>
}
```

**Agent Types:**
```typescript
type AgentType = 
  | 'specification'    // Requirements analysis
  | 'pseudocode'      // Algorithm design
  | 'architecture'    // System design
  | 'coder'          // Implementation
  | 'tester'         // Testing
  | 'reviewer'       // Code review
  | 'researcher'     // Research tasks
  | 'documenter'     // Documentation
  | 'optimizer';     // Performance optimization
```

### Agent Implementations

#### `SpecificationAgent`

```javascript
class SpecificationAgent extends BaseAgent {
  async analyzeRequirements(input: string): Promise<RequirementsAnalysis>
  async identifyConstraints(requirements: Requirements): Promise<Constraint[]>
  async generateAcceptanceCriteria(requirements: Requirements): Promise<AcceptanceCriteria[]>
}
```

#### `PseudocodeAgent`

```javascript
class PseudocodeAgent extends BaseAgent {
  async generatePseudocode(specification: SpecificationResult): Promise<PseudocodeResult>
  async optimizeAlgorithm(pseudocode: string): Promise<string>
  async validateLogic(pseudocode: string): Promise<ValidationResult>
}
```

#### `ArchitectureAgent`

```javascript
class ArchitectureAgent extends BaseAgent {
  async designSystemArchitecture(requirements: Requirements): Promise<SystemArchitecture>
  async selectDataStructures(requirements: Requirements): Promise<DataStructureSelection>
  async defineInterfaces(architecture: SystemArchitecture): Promise<Interface[]>
}
```

## 🧪 Practice Engine

### `PracticeEngine` (Base Class)

Base class for practice problem engines.

```javascript
abstract class PracticeEngine {
  constructor(config: PracticeConfig)
  
  // Problem management
  abstract getProblems(): Problem[]
  abstract getProblem(id: string): Problem | null
  
  // Solution validation
  async validateSolution(solution: string, problem: Problem): Promise<ValidationResult>
  async runTests(solution: string, testCases: TestCase[]): Promise<TestResult[]>
  
  // Adaptive difficulty
  adjustDifficulty(performance: PerformanceMetrics): void
  suggestNextProblem(completedProblems: string[]): Problem | null
  
  // Hints and guidance
  getHint(problem: Problem, attemptCount: number): Hint | null
  provideFeedback(solution: string, result: ValidationResult): Feedback
}
```

**Types:**
```typescript
interface Problem {
  id: string;
  title: string;
  description: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  category: string;
  template: string;
  testCases: TestCase[];
  hints: Hint[];
  timeLimit?: number;
  memoryLimit?: number;
}

interface TestCase {
  input: any[];
  expected: any;
  description: string;
  points: number;
}

interface ValidationResult {
  passed: boolean;
  score: number;
  testResults: TestResult[];
  feedback: Feedback;
  executionTime: number;
  memoryUsage: number;
}
```

### `ArrayPracticeProblems`

Practice problems for array data structure.

```javascript
class ArrayPracticeProblems extends PracticeEngine {
  constructor()
  
  // Array-specific problems
  getRotateArrayProblem(): Problem
  getReverseProblem(): Problem
  getTwoSumProblem(): Problem
  getMaxSubarrayProblem(): Problem
  
  // Solution templates
  getRotateArrayTemplate(): string
  getTwoSumTemplate(): string
}
```

### `SolutionValidator`

Validates user solutions against test cases.

```javascript
class SolutionValidator {
  constructor(config: ValidatorConfig)
  
  // Validation methods
  async validate(solution: string, testCases: TestCase[]): Promise<ValidationResult>
  async runSingleTest(solution: string, testCase: TestCase): Promise<TestResult>
  
  // Security
  sanitizeSolution(solution: string): string
  checkForForbiddenPatterns(solution: string): SecurityIssue[]
  
  // Performance analysis
  measurePerformance(solution: string, input: any[]): PerformanceMetrics
  analyzeComplexity(solution: string): ComplexityAnalysis
}
```

## 🛠️ Utility Classes

### `ConsoleRenderer`

Handles console output rendering and formatting.

```javascript
class ConsoleRenderer {
  constructor(config: RendererConfig)
  
  // Basic rendering
  print(content: string, options?: PrintOptions): void
  println(content: string, options?: PrintOptions): void
  clear(): void
  
  // Structured output
  table(data: any[][], headers?: string[]): void
  list(items: string[], type?: 'ordered' | 'unordered'): void
  tree(data: TreeData): void
  
  // Visual elements
  progressBar(current: number, total: number, options?: ProgressOptions): void
  separator(char?: string, length?: number): void
  box(content: string, options?: BoxOptions): void
  
  // Colors and formatting
  colorize(text: string, color: Color): string
  bold(text: string): string
  italic(text: string): string
  underline(text: string): string
}
```

### `InputHandler`

Handles user input and validation.

```javascript
class InputHandler {
  constructor(config: InputConfig)
  
  // Input methods
  async readLine(prompt?: string): Promise<string>
  async readChoice(choices: Choice[], prompt?: string): Promise<string>
  async readNumber(prompt?: string, options?: NumberOptions): Promise<number>
  async readConfirm(prompt: string, defaultValue?: boolean): Promise<boolean>
  
  // Validation
  validate(input: string, validator: Validator): ValidationResult
  sanitize(input: string): string
  
  // Special inputs
  async readPassword(prompt: string): Promise<string>
  async readMultiline(prompt: string): Promise<string[]>
}
```

### `PerformanceProfiler`

Measures and analyzes performance metrics.

```javascript
class PerformanceProfiler {
  constructor()
  
  // Timing
  startTimer(name: string): void
  endTimer(name: string): number
  measureAsync<T>(name: string, fn: () => Promise<T>): Promise<T>
  
  // Memory tracking
  getMemoryUsage(): MemoryUsage
  trackMemoryDelta(name: string, fn: () => void): MemoryDelta
  
  // Algorithm analysis
  measureComplexity(fn: Function, inputs: any[][]): ComplexityResult
  benchmarkComparison(functions: Function[], inputs: any[][]): BenchmarkResult
  
  // Reporting
  generateReport(): PerformanceReport
  exportMetrics(format: 'json' | 'csv'): string
}
```

## ⚙️ Configuration API

### `ConfigManager`

Manages application configuration and settings.

```javascript
class ConfigManager {
  constructor(configPath?: string)
  
  // Configuration loading
  loadConfig(): PlatformConfig
  saveConfig(config: PlatformConfig): void
  
  // Settings management
  get<T>(key: string, defaultValue?: T): T
  set<T>(key: string, value: T): void
  
  // Environment handling
  getEnvironment(): 'development' | 'production' | 'test'
  isProduction(): boolean
  isDevelopment(): boolean
  
  // Validation
  validateConfig(config: PlatformConfig): ValidationResult
}
```

**Configuration Schema:**
```typescript
interface PlatformConfig {
  // User preferences
  user: {
    name?: string;
    preferredLanguage: 'en' | 'es' | 'fr' | 'de';
    theme: 'light' | 'dark' | 'auto';
    difficulty: 'beginner' | 'intermediate' | 'advanced';
  };
  
  // Learning settings
  learning: {
    enableHints: boolean;
    enableAnalytics: boolean;
    autoSaveProgress: boolean;
    reminderInterval: number; // minutes
  };
  
  // Display settings
  display: {
    colorOutput: boolean;
    animationSpeed: 'slow' | 'normal' | 'fast';
    pageSize: number;
    showProgressBars: boolean;
  };
  
  // Advanced settings
  advanced: {
    debugMode: boolean;
    logLevel: 'error' | 'warn' | 'info' | 'debug';
    cacheSize: number;
    performanceTracking: boolean;
  };
  
  // SPARC settings
  sparc: {
    enableAgents: boolean;
    maxConcurrentAgents: number;
    agentTimeout: number; // seconds
    coordinationMode: 'mesh' | 'hierarchical' | 'star';
  };
}
```

## 🔔 Event System

### `EventEmitter`

Handles application-wide event communication.

```javascript
class EventEmitter {
  constructor()
  
  // Event management
  on(event: string, listener: EventListener): void
  off(event: string, listener: EventListener): void
  once(event: string, listener: EventListener): void
  
  // Event emission
  emit(event: string, ...args: any[]): void
  emitAsync(event: string, ...args: any[]): Promise<any[]>
  
  // Event querying
  listeners(event: string): EventListener[]
  listenerCount(event: string): number
  eventNames(): string[]
}
```

**Event Types:**
```typescript
// Learning events
type LearningEvent = 
  | 'module:started'
  | 'module:completed'
  | 'concept:mastered'
  | 'practice:attempted'
  | 'practice:completed';

// Progress events
type ProgressEvent =
  | 'progress:updated'
  | 'level:achieved'
  | 'milestone:reached'
  | 'streak:broken';

// System events
type SystemEvent =
  | 'system:ready'
  | 'system:shutdown'
  | 'config:changed'
  | 'error:occurred';
```

### Usage Examples

**Module Event Handling:**
```javascript
const eventEmitter = new EventEmitter();

// Listen for module completion
eventEmitter.on('module:completed', (moduleName, score) => {
  console.log(`🎉 Completed ${moduleName} with score: ${score}`);
});

// Listen for concept mastery
eventEmitter.on('concept:mastered', (module, concept) => {
  console.log(`✅ Mastered concept: ${concept} in ${module}`);
});

// Start a module (this will emit events)
const arrayModule = new BookshelfArray();
await arrayModule.startLearningSession();
```

**Progress Tracking:**
```javascript
const progressTracker = new ProgressTracker();

// Track when user completes practice problems
eventEmitter.on('practice:completed', (problemId, score) => {
  progressTracker.recordActivity('practice', score);
});

// Auto-save progress
eventEmitter.on('progress:updated', () => {
  configManager.set('lastProgress', progressTracker.getProgress());
});
```

## 🔧 Error Handling

### Custom Error Types

```typescript
class LearningPlatformError extends Error {
  constructor(message: string, public code: string) {
    super(message);
    this.name = 'LearningPlatformError';
  }
}

class ModuleNotFoundError extends LearningPlatformError {
  constructor(moduleName: string) {
    super(`Module "${moduleName}" not found`, 'MODULE_NOT_FOUND');
  }
}

class InvalidSolutionError extends LearningPlatformError {
  constructor(reason: string) {
    super(`Invalid solution: ${reason}`, 'INVALID_SOLUTION');
  }
}

class PrerequisiteError extends LearningPlatformError {
  constructor(module: string, missing: string[]) {
    super(`Cannot start ${module}. Missing prerequisites: ${missing.join(', ')}`, 'PREREQUISITE_ERROR');
  }
}
```

## 📊 Type Definitions

### Core Types

```typescript
// Learning data
interface LearningData {
  userId: string;
  modules: ModuleProgress[];
  overallProgress: ProgressStats;
  preferences: UserPreferences;
  achievements: Achievement[];
}

// Module data
interface ModuleProgress {
  name: string;
  status: 'not-started' | 'in-progress' | 'completed';
  score?: number;
  timeSpent: number;
  conceptsCompleted: string[];
  practiceProblems: ProblemAttempt[];
}

// Performance data
interface PerformanceMetrics {
  executionTime: number;
  memoryUsage: number;
  cpuUsage: number;
  complexity: ComplexityAnalysis;
}

interface ComplexityAnalysis {
  timeComplexity: string; // e.g., "O(n)", "O(log n)"
  spaceComplexity: string;
  bestCase: string;
  averageCase: string;
  worstCase: string;
}
```

---

## 📚 Quick Reference

### Most Used Classes
```javascript
// Core platform
const platform = new AlgorithmsDataStructuresLearning();

// Specific modules
const arrays = new BookshelfArray();
const linkedLists = new TrainLinkedList();
const stacks = new CafeteriaPlateStack();

// Interactive components
const playground = new AlgorithmPlayground();
const builder = new DataStructureBuilder();

// SPARC integration
const sparc = new SPARCOrchestrator();
const agent = await sparc.spawnAgent('coder');

// Utilities
const renderer = new ConsoleRenderer();
const profiler = new PerformanceProfiler();
```

### Common Patterns
```javascript
// Module execution pattern
const module = new SomeModule();
await module.startLearningSession();

// Practice problem pattern
const practiceEngine = new SomePracticeProblems();
const problems = practiceEngine.getProblems();
const result = await practiceEngine.validateSolution(solution, problem);

// Event handling pattern
eventEmitter.on('module:completed', (name, score) => {
  // Handle completion
});

// SPARC workflow pattern
const result = await sparc.executeWorkflow('specification', 'Create new feature');
```

**For complete examples and tutorials, see the [User Guide](USER_GUIDE.md) and [Developer Guide](DEVELOPER_GUIDE.md).**