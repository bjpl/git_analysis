# 🤝 Contributing to Interactive Algorithms Learning Platform

Thank you for your interest in contributing to the Interactive Algorithms Learning Platform! This guide will help you get started with contributing effectively.

## Table of Contents
- [Code of Conduct](#-code-of-conduct)
- [Getting Started](#-getting-started)
- [Development Workflow](#-development-workflow)
- [Contribution Types](#-contribution-types)
- [Coding Standards](#-coding-standards)
- [Testing Guidelines](#-testing-guidelines)
- [Documentation Guidelines](#-documentation-guidelines)
- [Review Process](#-review-process)

## 📜 Code of Conduct

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, visible or invisible disability, ethnicity, sex characteristics, gender identity and expression, level of experience, education, socio-economic status, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

**Positive behaviors include:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behaviors include:**
- Trolling, insulting comments, and personal attacks
- Public or private harassment
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

### Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be reported by contacting the project team at [conduct@algorithms-learning.com](mailto:conduct@algorithms-learning.com). All complaints will be reviewed and investigated promptly and fairly.

## 🚀 Getting Started

### Prerequisites

**Required Software:**
```bash
# Node.js 18.0.0 or higher
node --version  # >= 18.0.0
npm --version   # >= 8.0.0

# Git for version control
git --version   # >= 2.30.0

# Recommended tools
code --version  # VS Code (recommended)
```

### Fork and Clone

1. **Fork the Repository**
   - Visit [Interactive Algorithms Learning Platform](https://github.com/your-org/interactive-algorithms-learning)
   - Click the "Fork" button in the top right

2. **Clone Your Fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/interactive-algorithms-learning.git
   cd interactive-algorithms-learning
   ```

3. **Add Upstream Remote**
   ```bash
   git remote add upstream https://github.com/your-org/interactive-algorithms-learning.git
   ```

### Initial Setup

```bash
# Install dependencies
npm install

# Install SPARC workflow tools
npm install -g @claude-flow/cli@alpha

# Setup pre-commit hooks
npx husky install

# Run tests to ensure everything works
npm test

# Start the platform to verify setup
npm start
```

### Development Environment

**Create Development Configuration:**
```bash
# Copy environment template
cp .env.example .env.development

# Edit with your preferences
# Enable debug mode, disable analytics, etc.
```

**Verify Development Setup:**
```bash
# Run in development mode
npm run dev

# Run linting
npm run lint

# Run type checking  
npm run typecheck

# Run full test suite
npm test
```

## 🔄 Development Workflow

### SPARC Methodology Integration

This project uses **SPARC** (Specification, Pseudocode, Architecture, Refinement, Completion) methodology with **Claude-Flow** orchestration for systematic development.

#### Before Starting Development

**Initialize SPARC Workflow:**
```bash
# Start with specification phase
npx claude-flow sparc run spec-pseudocode "Your feature description"

# This will:
# 1. Analyze requirements and create specifications
# 2. Generate pseudocode for the feature  
# 3. Create architecture diagrams
# 4. Set up development environment
```

#### Agent-Based Development

**Use Claude-Flow agents for complex features:**
```bash
# Initialize swarm coordination
npx claude-flow@alpha swarm init --topology mesh --maxAgents 6

# Spawn agents for parallel development
npx claude-flow@alpha agent spawn --type researcher
npx claude-flow@alpha agent spawn --type coder  
npx claude-flow@alpha agent spawn --type tester
npx claude-flow@alpha agent spawn --type reviewer

# Orchestrate the development task
npx claude-flow@alpha task orchestrate "Create new learning module for hash tables"
```

### Branch Strategy

**Branch Naming Convention:**
```bash
feature/module-hashtables     # New learning modules
fix/array-visualization-bug   # Bug fixes
docs/api-reference-update     # Documentation updates
refactor/performance-optimization  # Code improvements
test/module-validation        # Test improvements
```

**Create Feature Branch:**
```bash
# Sync with upstream
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/your-feature-name

# Push branch to your fork
git push origin feature/your-feature-name
```

### Development Process

#### 1. Requirements Analysis (SPARC Specification)
```bash
# Use SPARC to analyze requirements
npx claude-flow sparc run spec-pseudocode "Feature: Interactive Hash Table Module

Requirements:
- Teach hash tables through library card catalog analogy
- Interactive hash function demonstration
- Collision resolution visualization  
- Practice problems with validation
- Performance comparison tools
"
```

#### 2. Design Phase (SPARC Pseudocode & Architecture)
```bash
# Generate pseudocode and architecture
npx claude-flow sparc run architect "Hash table learning module"

# Review generated designs:
# - Module structure and class hierarchy
# - Interactive component designs
# - Practice problem specifications
# - Performance measurement approaches
```

#### 3. Implementation (SPARC Refinement)
```bash
# Use Test-Driven Development
npx claude-flow sparc tdd "hash-table-module"

# This will:
# 1. Generate test cases first
# 2. Implement module step by step
# 3. Ensure code quality and coverage
# 4. Document all public APIs
```

#### 4. Testing & Integration
```bash
# Run comprehensive test suite
npm test

# Test specific module
npm test -- --grep "HashTable"

# Performance testing
npm run benchmark

# Integration testing
npm run test:integration
```

### Commit Guidelines

**Commit Message Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Test additions or updates
- `chore`: Build process or auxiliary tool changes

**Examples:**
```bash
feat(arrays): add interactive bookshelf visualization

- Implement ASCII art bookshelf representation
- Add book insertion/deletion animations
- Include performance metrics display
- Update practice problems with new exercises

Closes #123

fix(linkedlists): resolve train visualization rendering issue

The train cars were not properly connected in the ASCII art
when the list had more than 10 elements.

test(stacks): add comprehensive plate dispenser tests

- Test LIFO operations with edge cases
- Validate visualization output
- Add performance benchmarks
```

## 🎯 Contribution Types

### 1. Learning Module Development

**Create New Learning Modules:**
```bash
# Use module generator
npx claude-flow@alpha agent spawn --type base-template-generator
npx claude-flow@alpha task orchestrate "Create hash table learning module"
```

**Module Requirements:**
- Real-world analogy that makes sense
- Interactive console-based visualization
- Progressive complexity (beginner → advanced)
- Practice problems with automated validation
- Performance analysis tools
- Comprehensive documentation

**Example Module Structure:**
```javascript
// src/modules/hashtables.js
export class LibraryHashTable extends LearningModule {
  constructor() {
    super({
      name: 'Hash Tables: Library Card Catalog',
      analogy: 'Library Card Catalog System',
      icon: '📇',
      prerequisites: ['arrays'],
      estimatedTime: '45 minutes'
    });
  }

  async explainAnalogy() {
    // Use familiar library catalog analogy
  }

  async demonstrateOperations() {
    // Show hash function, collision resolution, etc.
  }
}
```

### 2. Interactive Component Enhancement

**Enhance Visualization:**
```javascript
// Improve ASCII art rendering
class ImprovedRenderer extends ConsoleRenderer {
  renderHashTable(buckets) {
    // Better visual representation
    // Color coding for different states
    // Animation support
  }
}
```

**Add Interactivity:**
```javascript
// More engaging user interactions
async promptWithValidation(question, validator) {
  // Enhanced input validation
  // Better error messages
  // Contextual help
}
```

### 3. Practice Problem Creation

**Problem Categories:**

**Beginner Problems:**
- Word frequency counting
- Simple hash implementations
- Basic collision handling

**Intermediate Problems:**
- Two-sum variations
- Group anagrams
- LRU cache implementation

**Advanced Problems:**
- Consistent hashing
- Bloom filters
- Custom hash functions

**Problem Template:**
```javascript
export const TwoSumProblem = {
  id: 'two-sum-basic',
  title: 'Two Sum Problem',
  difficulty: 'intermediate',
  description: `
Given an array of integers and a target sum, find two numbers
that add up to the target. Return their indices.

Think of this like finding two books whose page counts add up
to your available reading time!
  `,
  template: `
function twoSum(numbers, target) {
  // Your solution here
  // Hint: Use a hash table to store numbers you've seen
  
  return []; // Return [index1, index2]
}
  `,
  testCases: [
    {
      input: [[2, 7, 11, 15], 9],
      expected: [0, 1],
      description: "Basic case: 2 + 7 = 9"
    }
  ],
  hints: [
    "What information do you need to store as you iterate?",
    "For each number, what are you looking for?",
    "How can a hash table help you find the complement?"
  ]
};
```

### 4. Documentation Improvements

**Areas for Documentation:**
- Module API documentation
- Learning path guides
- Troubleshooting guides
- Performance optimization tips
- Accessibility improvements

**Documentation Standards:**
- Clear, beginner-friendly language
- Comprehensive examples
- ASCII diagrams for visual concepts
- Step-by-step tutorials
- FAQ sections

### 5. Performance Optimization

**Optimization Areas:**
- Module loading performance
- Visualization rendering speed
- Memory usage optimization
- Algorithm implementation efficiency

**Benchmarking Requirements:**
```javascript
// Include performance tests
describe('Hash Table Performance', () => {
  it('should maintain O(1) average insertion time', () => {
    // Performance validation
  });
});
```

### 6. Accessibility Improvements

**Accessibility Features:**
- Screen reader compatibility
- Keyboard navigation
- High contrast themes
- Reduced motion options
- Alternative text for visuals

**Testing Requirements:**
- Screen reader testing
- Keyboard-only navigation
- Color blindness compatibility
- Motor accessibility

### 7. Translation and Localization

**Supported Languages:**
- English (en) - Primary
- Spanish (es) 
- French (fr)
- German (de)
- More languages welcome!

**Translation Guidelines:**
- Maintain analogy effectiveness
- Preserve technical accuracy
- Consider cultural context
- Test with native speakers

## 📋 Coding Standards

### JavaScript Style Guide

**ES6+ Modern JavaScript:**
```javascript
// ✅ Good: Use ES6+ features
import { LearningModule } from './base/LearningModule.js';
const results = await Promise.all(tasks);
const { name, difficulty } = moduleConfig;

// ❌ Avoid: Old-style JavaScript
var LearningModule = require('./base/LearningModule.js');
```

**Function Declarations:**
```javascript
// ✅ Good: Clear, descriptive names
async function demonstrateHashFunction(key, tableSize) {
  const hash = this.calculateHash(key, tableSize);
  await this.visualizeHashCalculation(key, hash);
  return hash;
}

// ❌ Avoid: Vague or abbreviated names
function doHash(k, s) { /* ... */ }
```

**Error Handling:**
```javascript
// ✅ Good: Specific error handling
try {
  const module = await this.loadModule(moduleName);
  return module;
} catch (error) {
  if (error instanceof ModuleNotFoundError) {
    this.logger.error(`Module ${moduleName} not found`);
    throw new UserFriendlyError(`Sorry, the ${moduleName} module isn't available yet.`);
  }
  throw error;
}
```

### Code Organization

**File Structure:**
```javascript
// File header with description
/**
 * Hash Tables Learning Module
 * 
 * Teaches hash table concepts through library card catalog analogy.
 * Includes interactive demonstrations and practice problems.
 */

// Imports grouped and sorted
import { LearningModule } from './base/LearningModule.js';
import { InteractiveComponent } from './base/InteractiveComponent.js';
import { PracticeEngine } from './base/PracticeEngine.js';

// Constants
const DEFAULT_TABLE_SIZE = 10;
const MAX_COLLISION_ATTEMPTS = 5;

// Main class
export class LibraryHashTable extends LearningModule {
  // Constructor first
  constructor() { /* ... */ }
  
  // Public methods
  async startLearningSession() { /* ... */ }
  
  // Private methods (prefixed with _)
  _calculateHash(key) { /* ... */ }
}
```

**Class Design:**
```javascript
// ✅ Good: Single Responsibility Principle
class HashTableVisualization {
  constructor(renderer) {
    this.renderer = renderer;
  }
  
  renderTable(buckets) {
    // Only handles visualization
  }
}

class HashFunction {
  static djb2(key, tableSize) {
    // Only handles hash calculation
  }
}
```

### Performance Guidelines

**Memory Management:**
```javascript
// ✅ Good: Clean up resources
class LearningSession {
  constructor() {
    this.eventListeners = [];
  }
  
  cleanup() {
    this.eventListeners.forEach(listener => listener.remove());
    this.eventListeners = [];
  }
}
```

**Efficient Algorithms:**
```javascript
// ✅ Good: O(1) average case
class HashTable {
  get(key) {
    const hash = this.hash(key);
    return this.buckets[hash].find(item => item.key === key);
  }
}

// ❌ Avoid: O(n) linear search when hash table should be O(1)
class SlowHashTable {
  get(key) {
    return this.items.find(item => item.key === key);
  }
}
```

### Documentation Standards

**JSDoc Comments:**
```javascript
/**
 * Demonstrates hash table insertion with collision resolution.
 * 
 * @param {string} key - The key to insert
 * @param {any} value - The value to store
 * @param {boolean} [animate=true] - Whether to show animation
 * @returns {Promise<number>} The hash value where item was stored
 * @throws {HashTableFullError} When table is full and can't resize
 * 
 * @example
 * await hashTable.demonstrateInsertion("JavaScript Guide", "Programming");
 */
async demonstrateInsertion(key, value, animate = true) {
  // Implementation
}
```

## 🧪 Testing Guidelines

### Test Structure

**Test File Organization:**
```
tests/
├── unit/                    # Unit tests for individual components
│   ├── modules/            # Module-specific tests
│   ├── utils/              # Utility function tests
│   └── core/               # Core system tests
├── integration/            # Integration tests  
│   ├── module-workflows/   # End-to-end module tests
│   └── sparc-workflows/    # SPARC workflow tests
├── performance/            # Performance benchmarks
└── accessibility/          # Accessibility tests
```

**Test Naming Convention:**
```javascript
// tests/unit/modules/hashtables.test.js
import { describe, it, expect, beforeEach } from 'node:test';

describe('LibraryHashTable Module', () => {
  describe('Hash Function', () => {
    it('should generate consistent hash values for same input', () => {
      // Test implementation
    });
    
    it('should distribute values evenly across buckets', () => {
      // Test implementation  
    });
  });
  
  describe('Interactive Learning', () => {
    it('should progress through learning stages correctly', async () => {
      // Test learning workflow
    });
  });
});
```

### Test Requirements

**Unit Tests:**
- ✅ Test all public methods
- ✅ Test edge cases and error conditions
- ✅ Mock external dependencies
- ✅ Maintain >90% code coverage

**Integration Tests:**
- ✅ Test complete learning workflows
- ✅ Test SPARC agent coordination
- ✅ Test module interactions
- ✅ Test user experience flows

**Performance Tests:**
- ✅ Validate algorithm complexity
- ✅ Test memory usage patterns
- ✅ Benchmark rendering performance
- ✅ Test with large datasets

### Test Data and Mocks

**Create Realistic Test Data:**
```javascript
// tests/fixtures/test-data.js
export const sampleBooks = [
  { title: "JavaScript: The Good Parts", author: "Douglas Crockford" },
  { title: "Clean Code", author: "Robert Martin" },
  { title: "Design Patterns", author: "Gang of Four" }
];

export const hashTableTestCases = [
  {
    input: "test",
    expectedHash: 4,
    description: "Basic string hashing"
  }
];
```

**Mock External Dependencies:**
```javascript
// tests/mocks/console-renderer.js
export class MockConsoleRenderer {
  constructor() {
    this.output = [];
  }
  
  print(content) {
    this.output.push(content);
  }
  
  getOutput() {
    return this.output.join('\n');
  }
}
```

## 📚 Documentation Guidelines

### Documentation Types

**1. Code Documentation (JSDoc)**
- All public APIs must be documented
- Include examples for complex functions
- Document parameters and return values
- Note any side effects or requirements

**2. Module Documentation**
- README for each module explaining its purpose
- Learning objectives and outcomes
- Prerequisites and dependencies
- Usage examples

**3. User Guides**
- Step-by-step tutorials
- Screenshots of CLI output
- Common troubleshooting issues
- Best practices

**4. API Reference**
- Complete API documentation
- Parameter descriptions
- Return value specifications
- Error conditions

### Documentation Standards

**Writing Style:**
- Clear, concise language
- Beginner-friendly explanations
- Active voice when possible
- Consistent terminology

**Code Examples:**
```javascript
// ✅ Good: Complete, runnable examples
/**
 * Example usage:
 * ```javascript
 * const hashTable = new LibraryHashTable();
 * await hashTable.startLearningSession();
 * 
 * // Add a book to the catalog
 * hashTable.addBook("Clean Code", "Robert Martin");
 * 
 * // Find a book
 * const book = hashTable.findBook("Clean Code");
 * console.log(`Found: ${book.title} by ${book.author}`);
 * ```
 */
```

**Visual Elements:**
```
// Use ASCII art for complex concepts
/**
 * Hash table visualization:
 * 
 * ┌─────────────────────────────────────────────┐
 * │  Hash Table (Library Card Catalog)         │
 * ├─────────────────────────────────────────────┤
 * │ 0: [Empty]                                  │
 * │ 1: "Clean Code" → "Design Patterns"        │
 * │ 2: [Empty]                                  │
 * │ 3: "JavaScript Guide"                       │
 * └─────────────────────────────────────────────┘
 */
```

## 🔍 Review Process

### Pull Request Guidelines

**Pull Request Template:**
```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] New learning module
- [ ] Bug fix
- [ ] Feature enhancement  
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Test improvements

## Learning Module Checklist (if applicable)
- [ ] Uses appropriate real-world analogy
- [ ] Includes interactive demonstrations
- [ ] Has practice problems with validation
- [ ] Includes performance analysis
- [ ] Has comprehensive tests (>90% coverage)
- [ ] Documentation is complete and clear

## Testing
- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Manual testing completed
- [ ] Performance tested with large datasets

## Documentation
- [ ] Code is properly commented
- [ ] README updated if needed
- [ ] API documentation updated
- [ ] User guide updated if needed

## Accessibility
- [ ] Keyboard navigation works
- [ ] Screen reader compatible
- [ ] High contrast theme works
- [ ] No motion-only interactions

## Screenshots/Demos
(Include CLI output screenshots for UI changes)
```

### Review Criteria

**Code Quality:**
- ✅ Follows coding standards
- ✅ Includes appropriate error handling
- ✅ Has good test coverage
- ✅ Performance considerations addressed

**Learning Experience:**
- ✅ Uses effective analogies
- ✅ Progressive difficulty
- ✅ Engaging and interactive
- ✅ Clear learning objectives

**Technical Implementation:**
- ✅ Integrates well with existing codebase
- ✅ Follows SPARC methodology
- ✅ Proper agent coordination
- ✅ Efficient algorithms

**Documentation:**
- ✅ Clear and comprehensive
- ✅ Includes examples
- ✅ Beginner-friendly language
- ✅ Visual aids where helpful

### Review Process Steps

1. **Automated Checks**
   - CI/CD pipeline runs
   - Tests pass
   - Linting passes
   - Security scans complete

2. **Peer Review**
   - Code review by maintainers
   - Learning experience review
   - Documentation review
   - Accessibility review

3. **Testing**
   - Manual testing by reviewers
   - User experience validation
   - Performance verification
   - Cross-platform testing

4. **Final Approval**
   - All feedback addressed
   - Tests passing
   - Documentation complete
   - Ready for merge

### Getting Reviews

**Request Reviews:**
- Tag appropriate reviewers
- Provide context in PR description
- Be responsive to feedback
- Ask questions if unclear

**Respond to Feedback:**
- Address all comments
- Explain decisions when needed
- Update code and tests
- Re-request review after changes

## 🎯 Specific Contribution Areas

### High-Priority Contributions

**1. New Learning Modules Needed:**
- Hash Tables (Library Card Catalog)
- Sets (Club Membership)
- Maps/Dictionaries (Phone Directory)
- Heaps (Priority Hospital Triage)
- Graph Algorithms (GPS Navigation)

**2. Interactive Enhancements:**
- Better visualization animations
- Color-coded outputs for different themes
- Progress indicators during long operations
- Interactive algorithm comparisons

**3. Practice Problem Expansion:**
- More beginner-friendly problems
- Real-world application problems
- Interview-style problems
- Creative problem scenarios

**4. Accessibility Improvements:**
- Screen reader compatibility
- Keyboard shortcuts
- High contrast themes
- Motion reduction options

**5. Documentation Needs:**
- Video tutorials (ASCII screen recordings)
- Troubleshooting guides
- Performance tuning guides
- Advanced configuration examples

### Getting Started Suggestions

**For New Contributors:**
1. Start with documentation improvements
2. Add test cases for existing modules
3. Create simple practice problems
4. Fix accessibility issues

**For Experienced Developers:**
1. Create new learning modules
2. Improve SPARC integration
3. Optimize performance bottlenecks
4. Add advanced features

**For Educators:**
1. Review analogies for effectiveness
2. Suggest learning path improvements
3. Create assessment rubrics
4. Test with real learners

**For Designers:**
1. Improve ASCII art visualizations
2. Design better console layouts
3. Create theme variations
4. Enhance user experience flows

## 💬 Communication Channels

### Community Support

**GitHub Discussions:**
- Ask questions about contributing
- Propose new features
- Share ideas and feedback
- Get help with development setup

**Issues:**
- Report bugs
- Request features  
- Suggest improvements
- Track development progress

**Pull Requests:**
- Submit code contributions
- Get code reviews
- Collaborate on implementations
- Track contribution status

### Getting Help

**Development Help:**
- Comment on issues for guidance
- Join GitHub Discussions
- Review existing pull requests for examples
- Check the Developer Guide for detailed instructions

**Learning Module Help:**
- Review existing modules for patterns
- Test analogies with friends/colleagues
- Use SPARC agents for assistance
- Ask for feedback on module concepts

## 🏆 Recognition

### Contributor Recognition

**Ways We Recognize Contributors:**
- Contributor acknowledgments in README
- GitHub contributor graphs
- Special mentions in release notes
- Invitations to join maintainer team
- Conference presentation opportunities

**Contribution Levels:**
- **Module Creator**: Created complete learning module
- **Core Contributor**: Multiple significant contributions
- **Community Helper**: Active in discussions and reviews
- **Accessibility Champion**: Improved platform accessibility
- **Documentation Master**: Excellent documentation contributions

### Maintainer Program

**Becoming a Maintainer:**
1. Consistent high-quality contributions
2. Deep understanding of project goals
3. Active community participation
4. Commitment to project values
5. Technical expertise in relevant areas

**Maintainer Responsibilities:**
- Review pull requests
- Guide new contributors
- Make technical decisions
- Maintain code quality
- Support community

---

## 🚀 Ready to Contribute?

### Quick Start Checklist

- [ ] Read Code of Conduct
- [ ] Fork and clone repository
- [ ] Set up development environment
- [ ] Run tests to verify setup
- [ ] Choose contribution area
- [ ] Create feature branch
- [ ] Make your contribution
- [ ] Add tests and documentation
- [ ] Submit pull request
- [ ] Respond to review feedback

### First Contribution Ideas

**Good First Issues:**
- Add test cases for existing modules
- Fix typos in documentation
- Improve error messages
- Add hints to practice problems
- Create simple ASCII art improvements

**Next Level Contributions:**
- Create new practice problems
- Improve visualization rendering
- Add keyboard shortcuts
- Translate content to other languages
- Optimize performance

**Advanced Contributions:**
- Create complete learning modules
- Integrate new SPARC agents
- Add accessibility features
- Design new interactive components
- Implement advanced algorithms

**Thank you for contributing to making algorithms learning accessible and enjoyable for everyone! 🎉**

**Questions? Join the discussion at [GitHub Discussions](https://github.com/your-org/interactive-algorithms-learning/discussions)**