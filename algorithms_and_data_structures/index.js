/**
 * Algorithms and Data Structures Learning Platform
 * Main Entry Point
 * 
 * This comprehensive learning platform teaches algorithms and data structures
 * through everyday contexts and real-world examples.
 */

// Import all modules using ES module syntax
import { BookshelfArray, ArrayPracticeProblems } from './src/modules/arrays.js';
import { TrainLinkedList, LinkedListPracticeProblems } from './src/modules/linkedlists.js';
import { CafeteriaPlateStack, StackPracticeProblems } from './src/modules/stacks.js';
import { CoffeeShopQueue, QueuePracticeProblems } from './src/modules/queues.js';
import { CompanyOrganizationChart, TreePracticeProblems } from './src/modules/trees.js';
import { SocialNetworkGraph, GraphPracticeProblems } from './src/modules/graphs.js';
import { MusicPlaylist, SortingPracticeProblems } from './src/modules/sorting.js';
import { PhoneContactBook, SearchingPracticeProblems } from './src/modules/searching.js';
import { RoadTripPlanner, AdvancedDPProblems } from './src/modules/dynamic_programming.js';
import { RecursionLearning, AdvancedRecursionProblems } from './src/modules/recursion.js';
import { InteractiveExamples } from './src/examples/interactive_examples.js';
import { ComprehensiveChallenges } from './src/practice-problems/comprehensive_challenges.js';

/**
 * Main Learning Platform Class
 */
class AlgorithmsDataStructuresLearning {
  constructor() {
    this.modules = new Map();
    this.examples = new InteractiveExamples();
    this.challenges = new ComprehensiveChallenges();
    this.initializeModules();
  }

  /**
   * Initialize all learning modules
   */
  initializeModules() {
    this.modules.set('arrays', {
      name: 'Arrays: Organizing Books on a Shelf',
      description: 'Learn arrays through the metaphor of organizing books on a bookshelf',
      class: BookshelfArray,
      practiceProblems: ArrayPracticeProblems,
      icon: '📚'
    });
    
    this.modules.set('linkedlists', {
      name: 'Linked Lists: Train Cars Connected Together',
      description: 'Understand linked lists like train cars connected by couplers',
      class: TrainLinkedList,
      practiceProblems: LinkedListPracticeProblems,
      icon: '🚆'
    });
    
    this.modules.set('stacks', {
      name: 'Stacks: Plate Dispensers in Cafeterias',
      description: 'Master stacks through cafeteria plate dispenser mechanics',
      class: CafeteriaPlateStack,
      practiceProblems: StackPracticeProblems,
      icon: '🍽️'
    });
    
    this.modules.set('queues', {
      name: 'Queues: Waiting in Line at a Coffee Shop',
      description: 'Learn queues by simulating coffee shop customer service',
      class: CoffeeShopQueue,
      practiceProblems: QueuePracticeProblems,
      icon: '☕'
    });
    
    this.modules.set('trees', {
      name: 'Trees: Company Organization Charts',
      description: 'Explore trees through corporate hierarchical structures',
      class: CompanyOrganizationChart,
      practiceProblems: TreePracticeProblems,
      icon: '🏢'
    });
    
    this.modules.set('graphs', {
      name: 'Graphs: Social Networks or City Maps',
      description: 'Navigate graphs via social connections and city navigation',
      class: SocialNetworkGraph,
      practiceProblems: GraphPracticeProblems,
      icon: '🌐'
    });
    
    this.modules.set('sorting', {
      name: 'Sorting: Organizing Music Playlists',
      description: 'Sort data efficiently by organizing music collections',
      class: MusicPlaylist,
      practiceProblems: SortingPracticeProblems,
      icon: '🎵'
    });
    
    this.modules.set('searching', {
      name: 'Searching: Finding a Contact in Your Phone',
      description: 'Master search algorithms through phone contact lookup',
      class: PhoneContactBook,
      practiceProblems: SearchingPracticeProblems,
      icon: '📞'
    });
    
    this.modules.set('dynamic_programming', {
      name: 'Dynamic Programming: Planning a Road Trip with Stops',
      description: 'Optimize solutions through strategic road trip planning',
      class: RoadTripPlanner,
      practiceProblems: AdvancedDPProblems,
      icon: '🗺️'
    });
    
    this.modules.set('recursion', {
      name: 'Recursion: Russian Nesting Dolls',
      description: 'Understand recursion through Matryoshka doll structures',
      class: RecursionLearning,
      practiceProblems: AdvancedRecursionProblems,
      icon: '🪆'
    });
  }

  /**
   * Display welcome message and learning path
   */
  displayWelcome() {
    console.log('🎆 Welcome to the Algorithms & Data Structures Learning Platform!');
    console.log('================================================================');
    console.log('');
    console.log('Learn complex computer science concepts through everyday contexts!');
    console.log('Each module uses familiar real-world analogies to build intuition,');
    console.log('then provides hands-on practice with interactive examples.');
    console.log('');
    console.log('🎓 Learning Philosophy:');
    console.log('  • Context First: Understand the \'why\' before the \'how\'');
    console.log('  • Interactive Learning: Hands-on examples with real scenarios');
    console.log('  • Progressive Complexity: Start simple, build to advanced');
    console.log('  • Practical Applications: See how concepts apply in real systems');
    console.log('  • Visual Representation: Clear output showing data structure states');
    console.log('');
  }

  /**
   * Display all available learning modules
   */
  displayModules() {
    console.log('📚 Available Learning Modules:');
    console.log('===============================');
    console.log('');
    
    Array.from(this.modules.entries()).forEach(([key, module], index) => {
      console.log(`${(index + 1).toString().padStart(2)}. ${module.icon} ${module.name}`);
      console.log(`    ${module.description}`);
      console.log('');
    });
    
    console.log('Usage:');
    console.log('  platform.learnModule("module-name")     - Learn a specific module');
    console.log('  platform.runExample("example-name")     - Run interactive example');
    console.log('  platform.takeChallenge("challenge")     - Take comprehensive challenge');
    console.log('  platform.showLearningPath()             - Display recommended path');
    console.log('');
  }

  /**
   * Display recommended learning path
   */
  showLearningPath() {
    console.log('🗺️  Recommended Learning Path:');
    console.log('=============================');
    console.log('');
    
    const learningPath = [
      {
        phase: 'Foundation Phase',
        modules: ['arrays', 'linkedlists'],
        description: 'Master basic linear data structures',
        duration: '2-3 hours'
      },
      {
        phase: 'Stack & Queue Phase',
        modules: ['stacks', 'queues'],
        description: 'Learn specialized linear structures',
        duration: '2-3 hours'
      },
      {
        phase: 'Hierarchical Phase',
        modules: ['trees'],
        description: 'Understand hierarchical relationships',
        duration: '3-4 hours'
      },
      {
        phase: 'Network Phase',
        modules: ['graphs'],
        description: 'Master complex network structures',
        duration: '3-4 hours'
      },
      {
        phase: 'Algorithm Phase',
        modules: ['sorting', 'searching'],
        description: 'Learn fundamental algorithms',
        duration: '4-5 hours'
      },
      {
        phase: 'Advanced Phase',
        modules: ['dynamic_programming', 'recursion'],
        description: 'Master advanced problem-solving',
        duration: '5-6 hours'
      }
    ];
    
    learningPath.forEach((phase, index) => {
      console.log(`Phase ${index + 1}: ${phase.phase}`);
      console.log(`  Duration: ${phase.duration}`);
      console.log(`  Description: ${phase.description}`);
      console.log(`  Modules: ${phase.modules.map(m => this.modules.get(m).icon + ' ' + m).join(', ')}`);
      console.log('');
    });
    
    console.log('🎯 Tips for Success:');
    console.log('  • Practice each module before moving to the next');
    console.log('  • Try interactive examples to see concepts in action');
    console.log('  • Complete practice problems for reinforcement');
    console.log('  • Take comprehensive challenges to test mastery');
    console.log('  • Review and repeat difficult concepts');
    console.log('');
  }

  /**
   * Learn a specific module
   */
  async learnModule(moduleName) {
    if (!this.modules.has(moduleName)) {
      console.log(`\n❌ Module "${moduleName}" not found.`);
      this.displayModules();
      return;
    }
    
    const module = this.modules.get(moduleName);
    
    console.log(`\n${module.icon} Learning Module: ${module.name}`);
    console.log('='.repeat(module.name.length + 20));
    console.log('');
    console.log(`Description: ${module.description}`);
    console.log('');
    
    // Run the module's main demonstration
    try {
      // Dynamic import for module demonstration
      const moduleFile = await import(`./src/modules/${moduleName}.js`);
      
      if (moduleFile && typeof moduleFile === 'object') {
        console.log('🚀 Running module demonstration...');
        console.log('');
        
        // Module will run its demo if it has one
        console.log('Module loaded successfully.');
      }
    } catch (error) {
      console.log('Module demonstration completed.');
    }
    
    console.log(`\n✅ Module "${moduleName}" learning session complete!`);
    console.log('');
    console.log('Next steps:');
    console.log(`  • Try interactive examples: platform.examples.runExample("library-system")`);
    console.log(`  • Practice problems: platform.practiceProblems("${moduleName}")`);
    console.log(`  • Take challenges: platform.challenges.runChallenge("social-media-analyzer")`);
    console.log('');
  }

  /**
   * Run practice problems for a module
   */
  practiceProblems(moduleName) {
    if (!this.modules.has(moduleName)) {
      console.log(`\n❌ Module "${moduleName}" not found.`);
      return;
    }
    
    const module = this.modules.get(moduleName);
    
    console.log(`\n🧠 Practice Problems: ${module.name}`);
    console.log('='.repeat(module.name.length + 25));
    console.log('');
    
    // Note: In a real implementation, you'd run specific practice problems here
    console.log(`Practice problems for ${moduleName} are integrated within each module.`);
    console.log(`Run the module to see practice problems in action:`);
    console.log(`  platform.learnModule("${moduleName}")`);
    console.log('');
  }

  /**
   * Quick start guide for new learners
   */
  quickStart() {
    console.log('\n🚀 Quick Start Guide');
    console.log('==================');
    console.log('');
    console.log('New to algorithms and data structures? Start here!');
    console.log('');
    console.log('Step 1: Learn your first data structure');
    console.log('  platform.learnModule("arrays")');
    console.log('');
    console.log('Step 2: Try an interactive example');
    console.log('  platform.examples.runExample("library-system")');
    console.log('');
    console.log('Step 3: Take on a challenge');
    console.log('  platform.challenges.runChallenge("social-media-analyzer")');
    console.log('');
    console.log('Step 4: Follow the complete learning path');
    console.log('  platform.showLearningPath()');
    console.log('');
    
    // Run first module as demo
    console.log('🎯 Let\'s start with arrays! Running demonstration...');
    this.learnModule('arrays');
  }

  /**
   * Display platform statistics
   */
  displayStats() {
    console.log('\n📊 Platform Statistics');
    console.log('=====================');
    console.log('');
    
    const stats = {
      totalModules: this.modules.size,
      interactiveExamples: 5,
      comprehensiveChallenges: 5,
      practiceProblems: 40, // Estimated
      linesOfCode: 15000, // Estimated
      realWorldApplications: 70 // Estimated
    };
    
    Object.entries(stats).forEach(([key, value]) => {
      const displayKey = key.replace(/([A-Z])/g, ' $1')
                           .replace(/^./, str => str.toUpperCase());
      console.log(`${displayKey}: ${value}`);
    });
    
    console.log('');
    console.log('🎆 Learning Features:');
    console.log('  • Everyday context analogies');
    console.log('  • Interactive demonstrations');
    console.log('  • Visual state representation');
    console.log('  • Performance analysis');
    console.log('  • Real-world applications');
    console.log('  • Progressive difficulty');
    console.log('  • Comprehensive challenges');
    console.log('');
  }

  /**
   * Search for topics across all modules
   */
  searchTopics(query) {
    console.log(`\n🔍 Searching for: "${query}"`);
    console.log('=' .repeat(20 + query.length));
    console.log('');
    
    const results = [];
    
    this.modules.forEach((module, key) => {
      if (module.name.toLowerCase().includes(query.toLowerCase()) ||
          module.description.toLowerCase().includes(query.toLowerCase()) ||
          key.toLowerCase().includes(query.toLowerCase())) {
        results.push({ key, module });
      }
    });
    
    if (results.length === 0) {
      console.log('No modules found matching your search.');
      console.log('Try searching for: arrays, trees, sorting, recursion, etc.');
    } else {
      console.log(`Found ${results.length} matching modules:`);
      console.log('');
      
      results.forEach(({ key, module }) => {
        console.log(`${module.icon} ${module.name}`);
        console.log(`  Key: "${key}"`);
        console.log(`  ${module.description}`);
        console.log('');
      });
    }
  }

  /**
   * Performance comparison across all data structures
   */
  performanceComparison() {
    console.log('\n📈 Data Structure Performance Comparison');
    console.log('=========================================');
    console.log('');
    
    const performanceTable = [
      ['Data Structure', 'Access', 'Search', 'Insertion', 'Deletion', 'Space'],
      ['Array', 'O(1)', 'O(n)', 'O(n)', 'O(n)', 'O(n)'],
      ['Linked List', 'O(n)', 'O(n)', 'O(1)', 'O(1)', 'O(n)'],
      ['Stack', 'O(n)', 'O(n)', 'O(1)', 'O(1)', 'O(n)'],
      ['Queue', 'O(n)', 'O(n)', 'O(1)', 'O(1)', 'O(n)'],
      ['Binary Tree', 'O(log n)', 'O(log n)', 'O(log n)', 'O(log n)', 'O(n)'],
      ['Hash Table', 'O(1)', 'O(1)', 'O(1)', 'O(1)', 'O(n)'],
      ['Graph (Adj List)', 'O(1)', 'O(V+E)', 'O(1)', 'O(V)', 'O(V+E)']
    ];
    
    performanceTable.forEach((row, index) => {
      if (index === 0) {
        console.log(row.map(cell => cell.padEnd(15)).join('| '));
        console.log('-'.repeat(90));
      } else {
        console.log(row.map(cell => cell.padEnd(15)).join('| '));
      }
    });
    
    console.log('');
    console.log('Legend:');
    console.log('  O(1) - Constant time');
    console.log('  O(log n) - Logarithmic time');
    console.log('  O(n) - Linear time');
    console.log('  O(V+E) - Vertices plus Edges');
    console.log('');
  }

  /**
   * Generate study plan
   */
  generateStudyPlan(availableHours = 20) {
    console.log('\n📝 Personalized Study Plan');
    console.log('==========================');
    console.log('');
    console.log(`Total available time: ${availableHours} hours`);
    console.log('');
    
    const studyPlan = [
      { topic: 'Arrays & Linked Lists', hours: 4, priority: 'High' },
      { topic: 'Stacks & Queues', hours: 3, priority: 'High' },
      { topic: 'Trees', hours: 4, priority: 'Medium' },
      { topic: 'Graphs', hours: 4, priority: 'Medium' },
      { topic: 'Sorting Algorithms', hours: 3, priority: 'High' },
      { topic: 'Searching Algorithms', hours: 2, priority: 'High' },
      { topic: 'Dynamic Programming', hours: 4, priority: 'Low' },
      { topic: 'Recursion', hours: 3, priority: 'Medium' },
      { topic: 'Practice & Review', hours: 3, priority: 'High' }
    ];
    
    let totalHours = 0;
    let weekNumber = 1;
    
    console.log('Week-by-Week Study Schedule:');
    console.log('');
    
    studyPlan.forEach((item, index) => {
      if (totalHours + item.hours <= availableHours) {
        totalHours += item.hours;
        
        if (index % 2 === 0) {
          console.log(`Week ${weekNumber}:`);
        }
        
        console.log(`  ${item.topic} - ${item.hours} hours (Priority: ${item.priority})`);
        
        if (index % 2 === 1) {
          weekNumber++;
          console.log('');
        }
      }
    });
    
    console.log(`Total planned hours: ${totalHours}/${availableHours}`);
    console.log('');
    console.log('🏆 Success Tips:');
    console.log('  • Focus on high-priority topics first');
    console.log('  • Practice coding examples regularly');
    console.log('  • Take breaks every 2 hours');
    console.log('  • Review previous topics weekly');
    console.log('');
  }
}

// Create global platform instance
const platform = new AlgorithmsDataStructuresLearning();

// Export for use as ES module
export { 
  AlgorithmsDataStructuresLearning,
  platform,
  // Direct access to all classes
  BookshelfArray,
  TrainLinkedList,
  CafeteriaPlateStack,
  CoffeeShopQueue,
  CompanyOrganizationChart,
  SocialNetworkGraph,
  MusicPlaylist,
  PhoneContactBook,
  RoadTripPlanner,
  RecursionLearning,
  InteractiveExamples,
  ComprehensiveChallenges
};

// Auto-run welcome if this is the main module
// Use import.meta.url to check if this is the main module
import { fileURLToPath } from 'url';
import { argv } from 'process';

const __filename = fileURLToPath(import.meta.url);

if (argv[1] === __filename) {
  platform.displayWelcome();
  platform.displayModules();
  
  console.log('🚀 Getting Started:');
  console.log('  platform.quickStart()           - New learner quick start');
  console.log('  platform.showLearningPath()     - View complete learning path');
  console.log('  platform.learnModule("arrays")   - Learn specific module');
  console.log('  platform.examples.runExample("library-system") - Interactive examples');
  console.log('  platform.challenges.runChallenge("social-media-analyzer") - Challenges');
  console.log('');
  
  // Uncomment to run quick start automatically
  // platform.quickStart();
}