/**
 * Comprehensive Challenges: Advanced Practice Problems
 * 
 * This module contains challenging problems that combine multiple
 * algorithms and data structures concepts.
 */

// Import all modules for comprehensive challenges
import { BookshelfArray } from '../modules/arrays.js';
import { TrainLinkedList } from '../modules/linkedlists.js';
import { CafeteriaPlateStack } from '../modules/stacks.js';
import { CoffeeShopQueue } from '../modules/queues.js';
import { CompanyOrganizationChart } from '../modules/trees.js';
import { SocialNetworkGraph } from '../modules/graphs.js';
import { MusicPlaylist } from '../modules/sorting.js';
import { PhoneContactBook } from '../modules/searching.js';
import { RoadTripPlanner } from '../modules/dynamic_programming.js';
import { RecursionLearning } from '../modules/recursion.js';

class ComprehensiveChallenges {
  constructor() {
    this.challenges = new Map();
    this.results = [];
    this.initializeChallenges();
  }

  /**
   * Initialize all comprehensive challenges
   */
  initializeChallenges() {
    this.challenges.set('social-media-analyzer', this.socialMediaAnalyzer.bind(this));
    this.challenges.set('logistics-optimizer', this.logisticsOptimizer.bind(this));
    this.challenges.set('task-scheduler', this.taskScheduler.bind(this));
    this.challenges.set('data-structure-zoo', this.dataStructureZoo.bind(this));
    this.challenges.set('algorithm-race', this.algorithmRace.bind(this));
  }

  /**
   * Challenge 1: Social Media Analyzer
   * Combines graphs, queues, trees, and searching
   */
  socialMediaAnalyzer() {
    console.log('\n📊 Challenge 1: Social Media Analytics Platform');
    console.log('=' .repeat(55));
    
    const startTime = Date.now();
    let score = 0;
    
    // Create social network
    const platform = new SocialNetworkGraph('AnalyticsPlatform');
    
    console.log('\n🌐 Building social network for analysis:');
    
    // Add influencers and regular users
    const users = [
      { name: 'TechInfluencer_Mike', interests: ['technology', 'innovation', 'startups'], type: 'influencer' },
      { name: 'FoodBlogger_Sarah', interests: ['cooking', 'restaurants', 'travel'], type: 'influencer' },
      { name: 'FitnessGuru_John', interests: ['fitness', 'health', 'motivation'], type: 'influencer' },
      { name: 'Alice_23', interests: ['technology', 'gaming', 'music'], type: 'regular' },
      { name: 'Bob_Writer', interests: ['writing', 'books', 'travel'], type: 'regular' },
      { name: 'Carol_Designer', interests: ['design', 'art', 'photography'], type: 'regular' },
      { name: 'David_Student', interests: ['technology', 'learning', 'coding'], type: 'regular' },
      { name: 'Eva_Marketer', interests: ['marketing', 'startups', 'networking'], type: 'regular' },
      { name: 'Frank_Chef', interests: ['cooking', 'innovation', 'creativity'], type: 'regular' },
      { name: 'Grace_Photographer', interests: ['photography', 'art', 'travel'], type: 'regular' }
    ];
    
    users.forEach(user => {
      platform.addPerson(user.name, user.interests);
    });
    
    // Create strategic connections
    const connections = [
      // Influencers connecting to interested users
      ['TechInfluencer_Mike', 'Alice_23'],
      ['TechInfluencer_Mike', 'David_Student'],
      ['TechInfluencer_Mike', 'Eva_Marketer'],
      
      ['FoodBlogger_Sarah', 'Frank_Chef'],
      ['FoodBlogger_Sarah', 'Bob_Writer'],
      
      ['FitnessGuru_John', 'Eva_Marketer'],
      
      // Cross-connections based on shared interests
      ['Alice_23', 'David_Student'],     // Technology
      ['Bob_Writer', 'Grace_Photographer'], // Travel
      ['Carol_Designer', 'Grace_Photographer'], // Art/Photography
      ['Frank_Chef', 'TechInfluencer_Mike'], // Innovation
      ['Eva_Marketer', 'David_Student'],   // Networking/Learning
    ];
    
    connections.forEach(([user1, user2]) => {
      platform.createFriendship(user1, user2);
    });
    
    // Analysis Task 1: Find influencers and their reach
    console.log('\n🌟 Task 1: Influencer Analysis');
    const influencers = platform.findInfluencers(5);
    score += influencers.length * 10;
    
    // Analysis Task 2: Find communities
    console.log('\n🏠 Task 2: Community Detection');
    const communities = platform.findCommunities();
    score += communities.length * 15;
    
    // Analysis Task 3: Viral content spread simulation
    console.log('\n📱 Task 3: Content Spread Analysis');
    const contentQueue = new CoffeeShopQueue(20);
    
    // Simulate viral content spreading
    const viralContent = [
      { content: 'AI breakthrough announced!', source: 'TechInfluencer_Mike' },
      { content: 'New restaurant review posted', source: 'FoodBlogger_Sarah' },
      { content: 'Fitness challenge launched', source: 'FitnessGuru_John' }
    ];
    
    viralContent.forEach(item => {
      // Find people within 2 degrees who might see this content
      const reach = platform.findPeopleWithinDegrees(item.source, 2);
      contentQueue.joinLine(`Content: ${item.content}`, `Reach: ${reach.length} users`, 'viral');
      score += reach.length * 5;
    });
    
    contentQueue.displayLine();
    
    // Analysis Task 4: Recommendation engine
    console.log('\n🤖 Task 4: Friend Recommendation Engine');
    const recommendations = platform.suggestFriends('Carol_Designer', 3);
    score += recommendations.length * 8;
    
    // Analysis Task 5: Network path analysis
    console.log('\n🔍 Task 5: Connection Path Analysis');
    const pathExists = platform.findShortestPath('Alice_23', 'Frank_Chef');
    if (pathExists) score += 25;
    
    const endTime = Date.now();
    const executionTime = endTime - startTime;
    
    console.log(`\n✅ Challenge 1 Complete!`);
    console.log(`Score: ${score} points`);
    console.log(`Execution time: ${executionTime}ms`);
    
    this.results.push({
      challenge: 'Social Media Analyzer',
      score,
      executionTime,
      metrics: {
        users: users.length,
        connections: connections.length,
        communities: communities.length,
        influencers: influencers.length
      }
    });
    
    return { score, executionTime };
  }

  /**
   * Challenge 2: Logistics Optimizer
   * Combines dynamic programming, graphs, and sorting
   */
  logisticsOptimizer() {
    console.log('\n🚚 Challenge 2: Logistics & Supply Chain Optimizer');
    console.log('=' .repeat(55));
    
    const startTime = Date.now();
    let score = 0;
    
    // Create trip planner for logistics
    const logistics = new RoadTripPlanner();
    
    // Task 1: Optimize delivery routes
    console.log('\n🗺️  Task 1: Multi-City Delivery Route Optimization');
    
    const warehouses = ['Central', 'North', 'South', 'East', 'West'];
    const deliveryDistances = [
      [0, 45, 60, 38, 55],
      [45, 0, 85, 42, 70],
      [60, 85, 0, 65, 40],
      [38, 42, 65, 0, 48],
      [55, 70, 40, 48, 0]
    ];
    
    const shortestRoutes = logistics.findAllShortestPaths(warehouses, deliveryDistances);
    score += 50;
    
    // Task 2: Optimize truck loading (knapsack problem)
    console.log('\n📦 Task 2: Truck Loading Optimization');
    
    const packages = [
      { name: 'Electronics Package', weight: 15, value: 200 },
      { name: 'Medical Supplies', weight: 8, value: 180 },
      { name: 'Books Shipment', weight: 25, value: 150 },
      { name: 'Clothing Bundle', weight: 12, value: 120 },
      { name: 'Food Products', weight: 20, value: 100 },
      { name: 'Toys Collection', weight: 18, value: 90 },
      { name: 'Sports Equipment', weight: 30, value: 160 },
      { name: 'Home Appliances', weight: 35, value: 220 },
      { name: 'Art Supplies', weight: 5, value: 80 },
      { name: 'Garden Tools', weight: 22, value: 110 }
    ];
    
    const truckCapacity = 80; // kg
    const optimalLoad = logistics.packRoadTripBag(packages, truckCapacity);
    score += optimalLoad.maxValue / 5; // Score based on value optimization
    
    // Task 3: Delivery scheduling with constraints
    console.log('\n⏰ Task 3: Delivery Schedule Optimization');
    
    // Create a queue system for delivery scheduling
    const deliveryQueue = new CoffeeShopQueue(30);
    
    const deliveries = [
      { customer: 'ABC Corp', priority: 'urgent', timeWindow: '9-11 AM' },
      { customer: 'XYZ Ltd', priority: 'standard', timeWindow: '1-3 PM' },
      { customer: 'Tech Startup', priority: 'urgent', timeWindow: '10-12 PM' },
      { customer: 'Retail Store', priority: 'standard', timeWindow: '2-4 PM' },
      { customer: 'Hospital', priority: 'critical', timeWindow: '8-10 AM' },
      { customer: 'School District', priority: 'standard', timeWindow: '11-1 PM' },
      { customer: 'Restaurant Chain', priority: 'urgent', timeWindow: '7-9 AM' }
    ];
    
    // Add to priority queue (simulated)
    deliveries
      .sort((a, b) => {
        const priorityOrder = { critical: 3, urgent: 2, standard: 1 };
        return priorityOrder[b.priority] - priorityOrder[a.priority];
      })
      .forEach(delivery => {
        deliveryQueue.joinLine(
          delivery.customer, 
          delivery.timeWindow, 
          delivery.priority
        );
      });
    
    deliveryQueue.displayLine();
    score += deliveries.length * 5;
    
    // Task 4: Route similarity analysis
    console.log('\n🔄 Task 4: Route Pattern Analysis');
    
    const route1 = ['Central', 'North', 'East', 'South', 'West'];
    const route2 = ['Central', 'East', 'South', 'North', 'West'];
    
    const routeComparison = logistics.compareRoutePlans(route1, route2);
    score += routeComparison.length * 3;
    
    // Task 5: Fuel cost optimization
    console.log('\n⛽ Task 5: Fuel Cost Optimization');
    
    // Simulate fuel costs at different stops
    const fuelStops = [2.85, 3.12, 2.98, 3.05, 2.91]; // Price per gallon
    const fuelChange = logistics.makeChangeForTolls(45.67, [1, 5, 10, 25]);
    
    if (fuelChange) {
      score += 20;
    }
    
    // Task 6: Performance tracking
    console.log('\n📊 Task 6: Performance Metrics');
    
    const deliveryPerformance = [8, -2, 7, 9, -1, 6, 8, -3, 9, 7, 8, 6];
    const bestPeriod = logistics.findBestTravelStreak(deliveryPerformance);
    score += bestPeriod.maxSum;
    
    const endTime = Date.now();
    const executionTime = endTime - startTime;
    
    console.log(`\n✅ Challenge 2 Complete!`);
    console.log(`Score: ${score} points`);
    console.log(`Execution time: ${executionTime}ms`);
    
    this.results.push({
      challenge: 'Logistics Optimizer',
      score,
      executionTime,
      metrics: {
        warehouses: warehouses.length,
        packages: packages.length,
        deliveries: deliveries.length,
        truckUtilization: (optimalLoad.totalWeight / truckCapacity * 100).toFixed(1) + '%'
      }
    });
    
    return { score, executionTime };
  }

  /**
   * Challenge 3: Advanced Task Scheduler
   * Combines trees, queues, stacks, and recursion
   */
  taskScheduler() {
    console.log('\n📅 Challenge 3: Advanced Task Scheduler');
    console.log('=' .repeat(45));
    
    const startTime = Date.now();
    let score = 0;
    
    // Create project hierarchy using organization chart
    console.log('\n🏢 Task 1: Project Hierarchy Setup');
    
    const project = new CompanyOrganizationChart('Main Project', 'Software Development');
    
    // Build task hierarchy
    project.addEmployee('Main Project', 'Frontend Development', 'Phase', 'Development', 40);
    project.addEmployee('Main Project', 'Backend Development', 'Phase', 'Development', 60);
    project.addEmployee('Main Project', 'Database Design', 'Phase', 'Development', 30);
    project.addEmployee('Main Project', 'Testing', 'Phase', 'QA', 25);
    
    // Add subtasks
    project.addEmployee('Frontend Development', 'UI Components', 'Task', 'Development', 16);
    project.addEmployee('Frontend Development', 'State Management', 'Task', 'Development', 12);
    project.addEmployee('Frontend Development', 'Responsive Design', 'Task', 'Development', 12);
    
    project.addEmployee('Backend Development', 'API Development', 'Task', 'Development', 24);
    project.addEmployee('Backend Development', 'Authentication', 'Task', 'Development', 16);
    project.addEmployee('Backend Development', 'Data Processing', 'Task', 'Development', 20);
    
    project.addEmployee('Database Design', 'Schema Design', 'Task', 'Development', 12);
    project.addEmployee('Database Design', 'Data Migration', 'Task', 'Development', 18);
    
    project.addEmployee('Testing', 'Unit Testing', 'Task', 'QA', 12);
    project.addEmployee('Testing', 'Integration Testing', 'Task', 'QA', 13);
    
    project.displayOrganizationChart();
    score += 30;
    
    // Task 2: Priority queue for task scheduling
    console.log('\n⏱️  Task 2: Priority-Based Task Queue');
    
    const taskQueue = new CoffeeShopQueue(25);
    
    const tasks = [
      { name: 'Critical Bug Fix', priority: 'critical', estimatedHours: 4 },
      { name: 'Feature Implementation', priority: 'high', estimatedHours: 16 },
      { name: 'Code Review', priority: 'medium', estimatedHours: 2 },
      { name: 'Documentation Update', priority: 'low', estimatedHours: 3 },
      { name: 'Security Audit', priority: 'critical', estimatedHours: 8 },
      { name: 'Performance Optimization', priority: 'high', estimatedHours: 12 },
      { name: 'UI Polish', priority: 'medium', estimatedHours: 6 },
      { name: 'Testing Automation', priority: 'high', estimatedHours: 10 }
    ];
    
    // Sort by priority and add to queue
    const priorityOrder = { critical: 4, high: 3, medium: 2, low: 1 };
    tasks
      .sort((a, b) => priorityOrder[b.priority] - priorityOrder[a.priority])
      .forEach(task => {
        taskQueue.joinLine(task.name, `${task.estimatedHours}h`, task.priority);
      });
    
    taskQueue.displayLine();
    score += tasks.length * 3;
    
    // Task 3: Undo/Redo system with stacks
    console.log('\n⬅️  Task 3: Undo/Redo System Implementation');
    
    const undoStack = new CafeteriaPlateStack(20);
    const redoStack = new CafeteriaPlateStack(20);
    
    // Simulate operations that can be undone
    const operations = [
      'Created new task: Login Feature',
      'Updated task priority: High',
      'Assigned task to: John Doe',
      'Added comment: Needs review',
      'Changed status: In Progress',
      'Updated estimate: 8 hours'
    ];
    
    console.log('  Performing operations:');
    operations.forEach(op => {
      undoStack.addPlate(op, true);
      console.log(`    ✅ ${op}`);
    });
    
    score += operations.length * 2;
    
    // Simulate undo operations
    console.log('\n  Undoing last 3 operations:');
    for (let i = 0; i < 3; i++) {
      const undone = undoStack.takePlate();
      if (undone) {
        redoStack.addPlate(undone.type, true);
        console.log(`    ⬅️  Undid: ${undone.type}`);
        score += 3;
      }
    }
    
    // Task 4: Recursive task breakdown
    console.log('\n🔄 Task 4: Recursive Task Breakdown');
    
    const recursion = new RecursionLearning();
    
    // Calculate total complexity using factorial-like growth
    const taskComplexity = recursion.factorialDolls(5, false);
    console.log(`  Task complexity factor: ${taskComplexity}`);
    score += Math.floor(taskComplexity / 10);
    
    // Task 5: Task dependency resolution
    console.log('\n🔗 Task 5: Dependency Resolution');
    
    // Use depth-first traversal to resolve dependencies
    const dependencyTree = recursion.createDollCollection();
    console.log('  Resolving task dependencies:');
    const resolvedOrder = recursion.postOrderTraversal(dependencyTree);
    console.log(`  Resolution order: [${resolvedOrder.join(' → ')}]`);
    score += resolvedOrder.length * 4;
    
    // Task 6: Performance metrics and reporting
    console.log('\n📊 Task 6: Project Performance Analysis');
    
    const totalProjectHours = project.ceo.getTotalSalaryBudget();
    const completedTasks = Math.floor(resolvedOrder.length * 0.7);
    const efficiency = ((completedTasks / resolvedOrder.length) * 100).toFixed(1);
    
    console.log(`  Total estimated hours: ${totalProjectHours}`);
    console.log(`  Completed tasks: ${completedTasks}/${resolvedOrder.length}`);
    console.log(`  Project efficiency: ${efficiency}%`);
    
    score += Math.floor(parseFloat(efficiency));
    
    const endTime = Date.now();
    const executionTime = endTime - startTime;
    
    console.log(`\n✅ Challenge 3 Complete!`);
    console.log(`Score: ${score} points`);
    console.log(`Execution time: ${executionTime}ms`);
    
    this.results.push({
      challenge: 'Task Scheduler',
      score,
      executionTime,
      metrics: {
        totalTasks: project.totalEmployees,
        queuedTasks: tasks.length,
        operations: operations.length,
        efficiency: parseFloat(efficiency)
      }
    });
    
    return { score, executionTime };
  }

  /**
   * Challenge 4: Data Structure Zoo
   * Combines all data structures in a simulation
   */
  dataStructureZoo() {
    console.log('\n🦁 Challenge 4: Data Structure Zoo Simulation');
    console.log('=' .repeat(50));
    
    const startTime = Date.now();
    let score = 0;
    
    console.log('\n🏠 Building the Data Structure Zoo...');
    
    // Arrays: Animal enclosures
    const animalEnclosures = new BookshelfArray(15);
    const animals = ['Lion', 'Tiger', 'Elephant', 'Giraffe', 'Zebra', 'Monkey', 'Penguin', 'Dolphin'];
    
    animals.forEach((animal, index) => {
      animalEnclosures.addBook(index, animal);
    });
    
    console.log('\n🦁 Animal Enclosures (Array):');
    animalEnclosures.displayShelf();
    score += animals.length * 2;
    
    // Linked Lists: Animal train for tours
    const animalTrain = new TrainLinkedList('Zoo Express');
    
    console.log('\n🚂 Zoo Tour Train (Linked List):');
    ['Engine Car', 'Lion Car', 'Elephant Car', 'Giraffe Car', 'Caboose'].forEach(car => {
      animalTrain.addCarToEnd(car, Math.floor(Math.random() * 50));
    });
    
    animalTrain.displayTrain();
    score += animalTrain.trainLength * 3;
    
    // Stacks: Food dispensers
    const foodStack = new CafeteriaPlateStack(12);
    
    console.log('\n🍽️  Animal Food Dispenser (Stack):');
    const foods = ['Fish', 'Hay', 'Meat', 'Fruits', 'Vegetables'];
    foods.forEach(food => {
      foodStack.addPlate(food, true);
    });
    
    foodStack.displayStack();
    score += foods.length * 2;
    
    // Queues: Visitor line
    const visitorQueue = new CoffeeShopQueue(20);
    
    console.log('\n👥 Visitor Queue (Queue):');
    const visitors = [
      'Smith Family', 'Johnson Group', 'Brown Kids', 'Davis Couple',
      'Wilson Class', 'Garcia Family', 'Miller Group', 'Taylor Kids'
    ];
    
    visitors.forEach(visitor => {
      visitorQueue.joinLine(visitor, 'Zoo Tour', 'visitor');
    });
    
    visitorQueue.displayLine();
    score += visitors.length * 2;
    
    // Trees: Zoo staff organization
    const zooStaff = new CompanyOrganizationChart('Director Sarah Johnson', 'Metropolitan Zoo');
    
    console.log('\n🏢 Zoo Staff Organization (Tree):');
    zooStaff.addEmployee('Director Sarah Johnson', 'Mike Chen', 'Animal Care Manager', 'Animals', 65000);
    zooStaff.addEmployee('Director Sarah Johnson', 'Lisa Rodriguez', 'Visitor Services Manager', 'Services', 58000);
    
    zooStaff.addEmployee('Mike Chen', 'John Smith', 'Mammal Keeper', 'Animals', 45000);
    zooStaff.addEmployee('Mike Chen', 'Alice Green', 'Bird Keeper', 'Animals', 42000);
    
    zooStaff.addEmployee('Lisa Rodriguez', 'Bob Wilson', 'Tour Guide', 'Services', 38000);
    zooStaff.addEmployee('Lisa Rodriguez', 'Emma Davis', 'Gift Shop Manager', 'Services', 40000);
    
    zooStaff.displayOrganizationChart();
    score += zooStaff.totalEmployees * 3;
    
    // Graphs: Animal habitat connections
    const habitatGraph = new SocialNetworkGraph('Zoo Habitat Network');
    
    console.log('\n🌳 Habitat Network (Graph):');
    const habitats = ['Savanna', 'Jungle', 'Arctic', 'Aquarium', 'Aviary', 'Reptile House'];
    
    habitats.forEach(habitat => {
      habitatGraph.addPerson(habitat, ['animals', 'nature'], 'habitat');
    });
    
    // Connect habitats that share walkways
    const connections = [
      ['Savanna', 'Jungle'],
      ['Jungle', 'Aviary'],
      ['Arctic', 'Aquarium'],
      ['Aquarium', 'Reptile House'],
      ['Savanna', 'Arctic'],
      ['Aviary', 'Reptile House']
    ];
    
    connections.forEach(([hab1, hab2]) => {
      habitatGraph.createFriendship(hab1, hab2);
    });
    
    habitatGraph.displayNetwork();
    score += connections.length * 4;
    
    // Find optimal visitor path
    console.log('\n🗺️  Finding optimal visitor path:');
    const path = habitatGraph.findShortestPath('Savanna', 'Reptile House');
    if (path) score += path.length * 5;
    
    // Sorting: Organize animals by popularity
    console.log('\n🌟 Animal Popularity Ranking (Sorting):');
    const playlist = new MusicPlaylist('Animal Popularity');
    
    const animalPopularity = [
      ['Lion', 'King of Jungle', 'Mammals', 2020, 300, 5],
      ['Penguin', 'Cute Waddle', 'Birds', 2019, 280, 5],
      ['Elephant', 'Gentle Giant', 'Mammals', 2021, 250, 4],
      ['Dolphin', 'Smart Marine', 'Aquatic', 2022, 270, 5],
      ['Giraffe', 'Tall Friend', 'Mammals', 2020, 200, 4]
    ];
    
    animalPopularity.forEach(([name, desc, category, year, visits, rating]) => {
      playlist.addSong(name, desc, category, 'Animal', year, visits, rating);
    });
    
    // Sort by rating
    playlist.multiCriteriaSort('rating', 'playCount');
    playlist.displayPlaylist();
    score += animalPopularity.length * 3;
    
    // Searching: Animal information lookup
    console.log('\n🔍 Animal Information Search (Searching):');
    const animalDatabase = new PhoneContactBook('Zoo Animal Database');
    
    animalPopularity.forEach(([name, desc, category, year, visits, rating]) => {
      animalDatabase.addContact(name, visits.toString(), `${name.toLowerCase()}@zoo.com`, category, rating >= 5);
    });
    
    animalDatabase.displayContacts();
    
    // Search for specific animals
    animalDatabase.binarySearchByName('Lion');
    animalDatabase.searchByCategory('Mammals');
    score += 20;
    
    const endTime = Date.now();
    const executionTime = endTime - startTime;
    
    console.log(`\n✅ Challenge 4 Complete!`);
    console.log(`Score: ${score} points`);
    console.log(`Execution time: ${executionTime}ms`);
    
    this.results.push({
      challenge: 'Data Structure Zoo',
      score,
      executionTime,
      metrics: {
        animals: animals.length,
        visitors: visitors.length,
        staff: zooStaff.totalEmployees,
        habitats: habitats.length,
        connections: connections.length
      }
    });
    
    return { score, executionTime };
  }

  /**
   * Challenge 5: Algorithm Performance Race
   * Compare different algorithms on same problems
   */
  algorithmRace() {
    console.log('\n🏁 Challenge 5: Algorithm Performance Race');
    console.log('=' .repeat(45));
    
    const startTime = Date.now();
    let score = 0;
    
    // Race 1: Sorting Algorithm Competition
    console.log('\n🏆 Race 1: Sorting Algorithm Speed Test');
    
    const playlist = new MusicPlaylist('Race Playlist');
    
    // Add test data
    const testSongs = [];
    for (let i = 0; i < 20; i++) {
      testSongs.push([
        `Song ${i}`,
        `Artist ${String.fromCharCode(65 + (i % 26))}`,
        'Album',
        'Genre',
        2000 + (i % 24),
        180 + (i * 10),
        1 + (i % 5)
      ]);
    }
    
    testSongs.forEach(([title, artist, album, genre, year, duration, rating]) => {
      playlist.addSong(title, artist, album, genre, year, duration, rating);
    });
    
    // Test different sorting algorithms
    const bubbleTime = Date.now();
    const bubblePlaylist = new MusicPlaylist('Bubble Sort Test');
    bubblePlaylist.songs = [...playlist.songs];
    bubblePlaylist.bubbleSortByTitle();
    const bubbleEndTime = Date.now();
    
    const quickTime = Date.now();
    const quickPlaylist = new MusicPlaylist('Quick Sort Test');
    quickPlaylist.songs = [...playlist.songs];
    quickPlaylist.quickSortByYear();
    const quickEndTime = Date.now();
    
    console.log(`\n📈 Sorting Performance Results:`);
    console.log(`  Bubble Sort: ${bubbleEndTime - bubbleTime}ms`);
    console.log(`  Quick Sort: ${quickEndTime - quickTime}ms`);
    
    // Award points for efficiency
    const bubbleDuration = bubbleEndTime - bubbleTime;
    const quickDuration = quickEndTime - quickTime;
    
    if (quickDuration < bubbleDuration) {
      score += 25;
      console.log(`  ✅ Quick Sort wins! (+25 points)`);
    } else {
      score += 15;
      console.log(`  ✅ Bubble Sort performed well! (+15 points)`);
    }
    
    // Race 2: Searching Algorithm Competition
    console.log('\n🔍 Race 2: Search Algorithm Speed Test');
    
    const contactBook = new PhoneContactBook('Race Contacts');
    
    // Add test contacts
    for (let i = 0; i < 50; i++) {
      const name = `Contact ${String.fromCharCode(65 + (i % 26))}${i}`;
      contactBook.addContact(name, `555-${(1000 + i).toString()}`, `${name.toLowerCase()}@test.com`);
    }
    
    // Linear search test
    const linearStart = Date.now();
    contactBook.linearSearchByName('Contact M25');
    const linearEnd = Date.now();
    
    // Binary search test
    const binaryStart = Date.now();
    contactBook.binarySearchByName('Contact M25');
    const binaryEnd = Date.now();
    
    console.log(`\n📈 Search Performance Results:`);
    console.log(`  Linear Search: ${linearEnd - linearStart}ms`);
    console.log(`  Binary Search: ${binaryEnd - binaryStart}ms`);
    
    score += 30; // Points for implementing both searches
    
    // Race 3: Data Structure Access Speed
    console.log('\n⚡ Race 3: Data Structure Access Speed');
    
    const arrayAccess = Date.now();
    const shelf = new BookshelfArray(100);
    for (let i = 0; i < 50; i++) {
      shelf.addBook(i, `Book ${i}`);
    }
    // Access elements
    for (let i = 0; i < 25; i++) {
      shelf.getBookAt(i);
    }
    const arrayEnd = Date.now();
    
    const linkedAccess = Date.now();
    const train = new TrainLinkedList('Speed Test');
    for (let i = 0; i < 50; i++) {
      train.addCarToEnd(`Car ${i}`, 0);
    }
    // Access elements (simulate traversal)
    let current = train.locomotive;
    for (let i = 0; i < 25 && current; i++) {
      current = current.nextCar;
    }
    const linkedEnd = Date.now();
    
    console.log(`\n📈 Data Structure Performance:`);
    console.log(`  Array access: ${arrayEnd - arrayAccess}ms`);
    console.log(`  Linked List traversal: ${linkedEnd - linkedAccess}ms`);
    
    score += 40; // Points for performance comparison
    
    // Race 4: Algorithm Complexity Analysis
    console.log('\n📊 Race 4: Complexity Analysis');
    
    const recursion = new RecursionLearning();
    
    // Test recursive vs iterative
    const fibRecursiveStart = Date.now();
    const fibRecursive = recursion.fibonacciDollFamily(15, false);
    const fibRecursiveEnd = Date.now();
    
    // Simulate iterative fibonacci
    const fibIterativeStart = Date.now();
    let a = 0, b = 1, temp;
    for (let i = 2; i <= 15; i++) {
      temp = a + b;
      a = b;
      b = temp;
    }
    const fibIterative = b;
    const fibIterativeEnd = Date.now();
    
    console.log(`\n📈 Algorithm Complexity Results:`);
    console.log(`  Recursive Fibonacci: ${fibRecursiveEnd - fibRecursiveStart}ms (result: ${fibRecursive})`);
    console.log(`  Iterative Fibonacci: ${fibIterativeEnd - fibIterativeStart}ms (result: ${fibIterative})`);
    
    if (fibIterativeEnd - fibIterativeStart < fibRecursiveEnd - fibRecursiveStart) {
      score += 35;
      console.log(`  ✅ Iterative approach is more efficient! (+35 points)`);
    } else {
      score += 20;
      console.log(`  ✅ Both approaches work! (+20 points)`);
    }
    
    const endTime = Date.now();
    const executionTime = endTime - startTime;
    
    console.log(`\n✅ Challenge 5 Complete!`);
    console.log(`Score: ${score} points`);
    console.log(`Execution time: ${executionTime}ms`);
    
    this.results.push({
      challenge: 'Algorithm Race',
      score,
      executionTime,
      metrics: {
        sortingTests: 2,
        searchingTests: 2,
        accessTests: 2,
        complexityTests: 2,
        totalContacts: 50,
        totalSongs: 20
      }
    });
    
    return { score, executionTime };
  }

  /**
   * Run a specific challenge
   */
  runChallenge(challengeName) {
    if (this.challenges.has(challengeName)) {
      return this.challenges.get(challengeName)();
    } else {
      console.log(`\n❌ Challenge "${challengeName}" not found.`);
      this.listChallenges();
      return null;
    }
  }

  /**
   * List all available challenges
   */
  listChallenges() {
    console.log('\n🏆 Available Comprehensive Challenges:');
    console.log('======================================');
    console.log('1. social-media-analyzer - Social Media Analytics Platform');
    console.log('2. logistics-optimizer   - Supply Chain & Logistics Optimization');
    console.log('3. task-scheduler        - Advanced Project Task Scheduler');
    console.log('4. data-structure-zoo    - Interactive Zoo Simulation');
    console.log('5. algorithm-race        - Algorithm Performance Competition');
    console.log('\nUsage: runChallenge("challenge-name")');
  }

  /**
   * Run all challenges and display final scores
   */
  runAllChallenges() {
    console.log('\n🏆 Running All Comprehensive Challenges');
    console.log('=========================================');
    
    this.results = []; // Clear previous results
    
    const challengeNames = Array.from(this.challenges.keys());
    
    challengeNames.forEach((name, index) => {
      console.log(`\n\n[${'='.repeat(15)} Challenge ${index + 1}/${challengeNames.length} ${'='.repeat(15)}]`);
      this.runChallenge(name);
      
      if (index < challengeNames.length - 1) {
        console.log('\n' + '-'.repeat(80));
      }
    });
    
    // Display final results
    this.displayFinalResults();
  }

  /**
   * Display comprehensive results and analysis
   */
  displayFinalResults() {
    console.log('\n\n🏆 COMPREHENSIVE CHALLENGE RESULTS');
    console.log('================================');
    
    let totalScore = 0;
    let totalTime = 0;
    
    console.log('\nChallenge Results:');
    console.log('Challenge Name              Score    Time (ms)   Efficiency');
    console.log('----------------------------------------------------------');
    
    this.results.forEach(result => {
      const efficiency = (result.score / result.executionTime * 1000).toFixed(2);
      console.log(`${result.challenge.padEnd(25)} ${result.score.toString().padStart(6)} ${result.executionTime.toString().padStart(10)} ${efficiency.padStart(10)}`);
      totalScore += result.score;
      totalTime += result.executionTime;
    });
    
    console.log('----------------------------------------------------------');
    console.log(`Total                       ${totalScore.toString().padStart(6)} ${totalTime.toString().padStart(10)} ${(totalScore / totalTime * 1000).toFixed(2).padStart(10)}`);
    
    // Performance analysis
    console.log('\n📊 Performance Analysis:');
    console.log(`• Total Score: ${totalScore} points`);
    console.log(`• Total Execution Time: ${(totalTime / 1000).toFixed(2)} seconds`);
    console.log(`• Average Score per Challenge: ${(totalScore / this.results.length).toFixed(1)}`);
    console.log(`• Average Time per Challenge: ${(totalTime / this.results.length).toFixed(1)}ms`);
    
    // Best performing challenge
    const bestChallenge = this.results.reduce((best, current) => 
      (current.score / current.executionTime) > (best.score / best.executionTime) ? current : best
    );
    
    console.log(`• Most Efficient Challenge: ${bestChallenge.challenge}`);
    
    // Grade assignment
    const grade = this.calculateGrade(totalScore);
    console.log(`\n🎓 Overall Grade: ${grade.letter} (${grade.percentage}%)`);
    console.log(`🏅 ${grade.comment}`);
    
    // Detailed metrics
    console.log('\n📈 Detailed Metrics:');
    this.results.forEach(result => {
      console.log(`\n${result.challenge}:`);
      Object.entries(result.metrics).forEach(([key, value]) => {
        console.log(`  • ${key}: ${value}`);
      });
    });
    
    console.log('\n🎆 Congratulations on completing all challenges!');
    console.log('You have successfully demonstrated mastery of:');
    console.log('  • Arrays, Linked Lists, Stacks, and Queues');
    console.log('  • Trees, Graphs, and Network Analysis');
    console.log('  • Sorting and Searching Algorithms');
    console.log('  • Dynamic Programming Optimization');
    console.log('  • Recursive Problem Solving');
    console.log('  • Performance Analysis and Optimization');
  }

  /**
   * Calculate grade based on total score
   */
  calculateGrade(totalScore) {
    const maxPossibleScore = 1000; // Estimated maximum
    const percentage = Math.min(100, (totalScore / maxPossibleScore * 100)).toFixed(1);
    
    if (percentage >= 90) {
      return { letter: 'A+', percentage, comment: 'Outstanding mastery of algorithms and data structures!' };
    } else if (percentage >= 85) {
      return { letter: 'A', percentage, comment: 'Excellent understanding and implementation!' };
    } else if (percentage >= 80) {
      return { letter: 'A-', percentage, comment: 'Very good grasp of the concepts!' };
    } else if (percentage >= 75) {
      return { letter: 'B+', percentage, comment: 'Good understanding with room for optimization!' };
    } else if (percentage >= 70) {
      return { letter: 'B', percentage, comment: 'Solid foundation, keep practicing!' };
    } else if (percentage >= 65) {
      return { letter: 'B-', percentage, comment: 'Good effort, focus on efficiency!' };
    } else if (percentage >= 60) {
      return { letter: 'C+', percentage, comment: 'Fair understanding, more practice needed!' };
    } else {
      return { letter: 'C', percentage, comment: 'Keep learning and practicing - you\'re on the right track!' };
    }
  }
}

// Export for use in other modules
export { ComprehensiveChallenges };

import { fileURLToPath } from 'url';
import { argv } from 'process';
const __filename = fileURLToPath(import.meta.url);

// Example usage and demonstration
if (argv[1] === __filename) {
  console.log('🏆 Welcome to Comprehensive Algorithm & Data Structure Challenges!\n');
  
  const challenges = new ComprehensiveChallenges();
  
  // Show available challenges
  challenges.listChallenges();
  
  // Run a specific challenge for demonstration
  console.log('\n🏆 Running Social Media Analyzer Challenge:');
  challenges.runChallenge('social-media-analyzer');
  
  console.log('\n\n🏆 Running Data Structure Zoo Challenge:');
  challenges.runChallenge('data-structure-zoo');
  
  console.log('\n\n🏆 Final Challenge Results:');
  challenges.displayFinalResults();
  
  console.log('\n\nTo run all challenges: challenges.runAllChallenges()');
}