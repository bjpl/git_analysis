/**
 * Interactive Examples: Hands-on Learning with Algorithms and Data Structures
 * 
 * This module provides interactive examples that combine multiple concepts
 * and demonstrate real-world applications.
 */

// Import all modules
import { BookshelfArray, ArrayPracticeProblems } from '../modules/arrays.js';
import { TrainLinkedList, LinkedListPracticeProblems } from '../modules/linkedlists.js';
import { CafeteriaPlateStack, StackPracticeProblems } from '../modules/stacks.js';
import { CoffeeShopQueue, QueuePracticeProblems } from '../modules/queues.js';
import { CompanyOrganizationChart, TreePracticeProblems } from '../modules/trees.js';
import { SocialNetworkGraph, GraphPracticeProblems } from '../modules/graphs.js';
import { MusicPlaylist, SortingPracticeProblems } from '../modules/sorting.js';
import { PhoneContactBook, SearchingPracticeProblems } from '../modules/searching.js';
import { RoadTripPlanner, AdvancedDPProblems } from '../modules/dynamic_programming.js';
import { RecursionLearning, AdvancedRecursionProblems } from '../modules/recursion.js';

class InteractiveExamples {
  constructor() {
    this.examples = new Map();
    this.initializeExamples();
  }

  /**
   * Initialize all interactive examples
   */
  initializeExamples() {
    this.examples.set('library-system', this.createLibrarySystem.bind(this));
    this.examples.set('social-media', this.createSocialMediaPlatform.bind(this));
    this.examples.set('restaurant-system', this.createRestaurantSystem.bind(this));
    this.examples.set('navigation-system', this.createNavigationSystem.bind(this));
    this.examples.set('file-system', this.createFileSystem.bind(this));
  }

  /**
   * Example 1: Digital Library System
   * Combines Arrays, Trees, and Searching
   */
  createLibrarySystem() {
    console.log('\n📚 Interactive Example 1: Digital Library Management System');
    console.log('=' .repeat(60));
    
    // Use BookshelfArray for book storage
    const mainLibrary = new BookshelfArray(20);
    
    console.log('\n📚 Adding books to the digital library:');
    
    // Add diverse collection of books
    const books = [
      { title: 'Data Structures Handbook', author: 'Smith', genre: 'Computer Science', year: 2023 },
      { title: 'The Great Gatsby', author: 'Fitzgerald', genre: 'Literature', year: 1925 },
      { title: 'Python Programming', author: 'Johnson', genre: 'Computer Science', year: 2022 },
      { title: 'To Kill a Mockingbird', author: 'Lee', genre: 'Literature', year: 1960 },
      { title: 'Machine Learning Basics', author: 'Chen', genre: 'Computer Science', year: 2024 },
      { title: '1984', author: 'Orwell', genre: 'Dystopian Fiction', year: 1949 },
      { title: 'Algorithms Unleashed', author: 'Davis', genre: 'Computer Science', year: 2023 },
      { title: 'Pride and Prejudice', author: 'Austen', genre: 'Romance', year: 1813 }
    ];
    
    books.forEach((book, index) => {
      mainLibrary.addBook(index, `"${book.title}" by ${book.author}`);
    });
    
    mainLibrary.displayShelf();
    
    // Demonstrate searching capabilities
    console.log('\n🔍 Library Search System:');
    mainLibrary.findBook('"Python Programming" by Johnson');
    mainLibrary.findBook('"JavaScript Mastery" by Unknown');
    
    // Sort books by title
    console.log('\n📊 Organizing library alphabetically:');
    mainLibrary.sortBooksByTitle();
    mainLibrary.displayShelf();
    
    // Create organization chart for library staff
    console.log('\n🏢 Library Staff Organization:');
    const libraryStaff = new CompanyOrganizationChart('Dr. Margaret Wilson', 'City Public Library');
    
    libraryStaff.addEmployee('Dr. Margaret Wilson', 'Sarah Johnson', 'Head Librarian', 'Administration', 75000);
    libraryStaff.addEmployee('Dr. Margaret Wilson', 'Michael Brown', 'IT Director', 'Technology', 80000);
    
    libraryStaff.addEmployee('Sarah Johnson', 'Emily Davis', 'Reference Librarian', 'Research', 55000);
    libraryStaff.addEmployee('Sarah Johnson', 'John Smith', 'Children\'s Librarian', 'Youth Services', 52000);
    
    libraryStaff.addEmployee('Michael Brown', 'Alice Chen', 'Systems Administrator', 'Technology', 65000);
    
    libraryStaff.displayOrganizationChart();
    
    // Find duplicates in the collection
    console.log('\n🔍 Checking for duplicate books:');
    const allBooks = Array.from({length: mainLibrary.capacity}, (_, i) => mainLibrary.getBookAt(i)).filter(book => book);
    const duplicates = ArrayPracticeProblems.findDuplicates(allBooks);
    
    if (duplicates.length === 0) {
      console.log('✅ No duplicate books found in the library');
    }
    
    console.log('\n✅ Library Management System Demo Complete!');
  }

  /**
   * Example 2: Social Media Platform
   * Combines Graphs, Queues, and Trees
   */
  createSocialMediaPlatform() {
    console.log('\n🌐 Interactive Example 2: Social Media Platform');
    console.log('=' .repeat(60));
    
    // Create social network
    const socialPlatform = new SocialNetworkGraph('ConnectHub');
    
    console.log('\n👥 Building social network:');
    
    // Add users
    const users = [
      { name: 'Alice Cooper', interests: ['photography', 'travel', 'cooking'], location: 'New York' },
      { name: 'Bob Wilson', interests: ['music', 'gaming', 'sports'], location: 'Los Angeles' },
      { name: 'Carol Davis', interests: ['reading', 'cooking', 'yoga'], location: 'Chicago' },
      { name: 'David Lee', interests: ['photography', 'hiking', 'tech'], location: 'Seattle' },
      { name: 'Eva Martinez', interests: ['travel', 'art', 'music'], location: 'Miami' },
      { name: 'Frank Johnson', interests: ['gaming', 'tech', 'fitness'], location: 'Austin' },
      { name: 'Grace Kim', interests: ['yoga', 'reading', 'art'], location: 'Portland' },
      { name: 'Henry Brown', interests: ['sports', 'fitness', 'cooking'], location: 'Denver' }
    ];
    
    users.forEach(user => {
      socialPlatform.addPerson(user.name, user.interests, user.location);
    });
    
    // Create friendships based on common interests or location
    console.log('\n🤝 Creating friendships:');
    const friendships = [
      ['Alice Cooper', 'David Lee'],    // Photography
      ['Alice Cooper', 'Carol Davis'],  // Cooking
      ['Bob Wilson', 'Eva Martinez'],   // Music
      ['Bob Wilson', 'Frank Johnson'], // Gaming
      ['Carol Davis', 'Grace Kim'],     // Reading, Yoga
      ['David Lee', 'Frank Johnson'],  // Tech
      ['Eva Martinez', 'Grace Kim'],    // Art
      ['Frank Johnson', 'Henry Brown'], // Fitness
      ['Alice Cooper', 'Eva Martinez'], // Travel
    ];
    
    friendships.forEach(([person1, person2]) => {
      socialPlatform.createFriendship(person1, person2);
    });
    
    socialPlatform.displayNetwork();
    
    // Demonstrate social features
    console.log('\n🔍 Social Network Analysis:');
    
    // Find path between users
    socialPlatform.findShortestPath('Alice Cooper', 'Henry Brown');
    
    // Find people within degrees of separation
    socialPlatform.findPeopleWithinDegrees('Carol Davis', 2);
    
    // Find mutual friends
    socialPlatform.findMutualFriends('Alice Cooper', 'Eva Martinez');
    
    // Friend suggestions
    socialPlatform.suggestFriends('David Lee');
    
    // Find influencers
    socialPlatform.findInfluencers(3);
    
    // Notification system using queue
    console.log('\n🔔 Social Media Notification System:');
    const notificationQueue = new CoffeeShopQueue(15);
    
    // Simulate notifications
    const notifications = [
      'Alice Cooper liked your photo',
      'Bob Wilson commented on your post',
      'Carol Davis sent you a friend request',
      'David Lee shared your article',
      'Eva Martinez tagged you in a photo',
      'New friend suggestion: Frank Johnson'
    ];
    
    notifications.forEach((notification, index) => {
      notificationQueue.joinLine(`User ${index + 1}`, notification, 'notification');
    });
    
    notificationQueue.displayLine();
    
    // Process notifications
    console.log('\n📱 Processing notifications:');
    for (let i = 0; i < 3; i++) {
      const processed = notificationQueue.serveCustomer();
      if (processed) {
        console.log(`  Notification processed: ${processed.orderType}`);
      }
    }
    
    console.log('\n✅ Social Media Platform Demo Complete!');
  }

  /**
   * Example 3: Restaurant Management System
   * Combines Stacks, Queues, and Trees
   */
  createRestaurantSystem() {
    console.log('\n🍴 Interactive Example 3: Restaurant Management System');
    console.log('=' .repeat(60));
    
    // Order management with stacks and queues
    console.log('\n🍽️  Kitchen Order Management:');
    
    // Plate dispenser (stack)
    const plateStack = new CafeteriaPlateStack(15);
    
    // Stock plates
    const plateTypes = ['dinner', 'salad', 'dessert', 'bread', 'dinner'];
    plateTypes.forEach(type => {
      plateStack.addPlate(type, true);
    });
    
    plateStack.displayStack();
    
    // Customer queue
    const customerQueue = new CoffeeShopQueue(20);
    
    console.log('\n👥 Customer Order Queue:');
    
    const orders = [
      { customer: 'John Smith', order: 'Grilled Salmon with Vegetables' },
      { customer: 'Mary Johnson', order: 'Caesar Salad' },
      { customer: 'Robert Davis', order: 'Beef Steak Medium Rare' },
      { customer: 'Lisa Wilson', order: 'Vegetarian Pasta' },
      { customer: 'Mike Brown', order: 'Fish and Chips' },
      { customer: 'Sarah Lee', order: 'Chicken Parmesan' },
    ];
    
    orders.forEach(({customer, order}) => {
      customerQueue.joinLine(customer, order, 'dining');
    });
    
    customerQueue.displayLine();
    
    // Restaurant staff hierarchy (tree structure)
    console.log('\n🏢 Restaurant Staff Organization:');
    const restaurant = new CompanyOrganizationChart('Chef Antonio Rossi', 'Bella Vista Restaurant');
    
    // Add management
    restaurant.addEmployee('Chef Antonio Rossi', 'Maria Santos', 'Restaurant Manager', 'Management', 65000);
    restaurant.addEmployee('Chef Antonio Rossi', 'Giuseppe Benedetti', 'Sous Chef', 'Kitchen', 55000);
    
    // Add kitchen staff
    restaurant.addEmployee('Giuseppe Benedetti', 'Carlos Rivera', 'Line Cook', 'Kitchen', 42000);
    restaurant.addEmployee('Giuseppe Benedetti', 'Anna Kim', 'Pastry Chef', 'Kitchen', 48000);
    
    // Add front of house
    restaurant.addEmployee('Maria Santos', 'David Thompson', 'Head Waiter', 'Service', 45000);
    restaurant.addEmployee('Maria Santos', 'Elena Rodriguez', 'Host', 'Service', 38000);
    
    // Add service staff
    restaurant.addEmployee('David Thompson', 'James Wilson', 'Waiter', 'Service', 35000);
    restaurant.addEmployee('David Thompson', 'Sophie Martin', 'Waiter', 'Service', 35000);
    
    restaurant.displayOrganizationChart();
    
    // Simulate dinner rush
    console.log('\n🎆 Simulating Dinner Rush:');
    
    // Process some customers
    console.log('Kitchen starts preparing orders...');
    for (let i = 0; i < 3; i++) {
      const customer = customerQueue.serveCustomer();
      if (customer) {
        const plate = plateStack.takePlate();
        if (plate) {
          console.log(`  ✅ Order for ${customer.name} served on ${plate.type} plate`);
        } else {
          console.log(`  ⚠️  No clean plates available for ${customer.name}`);
        }
      }
    }
    
    // Check remaining queue and plates
    customerQueue.displayLine();
    plateStack.displayStack();
    
    // Find the busiest department
    console.log('\n📊 Restaurant Department Analysis:');
    restaurant.getDepartmentSummary();
    
    console.log('\n✅ Restaurant Management System Demo Complete!');
  }

  /**
   * Example 4: GPS Navigation System
   * Combines Graphs and Dynamic Programming
   */
  createNavigationSystem() {
    console.log('\n🗺️  Interactive Example 4: GPS Navigation System');
    console.log('=' .repeat(60));
    
    // Create road trip planner
    const tripPlanner = new RoadTripPlanner();
    
    // Plan optimal route using shortest path algorithms
    console.log('\n🏢 City Network for Navigation:');
    
    const cities = ['Seattle', 'Portland', 'San Francisco', 'Los Angeles', 'Las Vegas'];
    
    // Distance matrix (in miles)
    const distances = [
      [0, 173, 807, 1135, 872],     // Seattle
      [173, 0, 635, 963, 769],      // Portland  
      [807, 635, 0, 382, 569],      // San Francisco
      [1135, 963, 382, 0, 270],     // Los Angeles
      [872, 769, 569, 270, 0]       // Las Vegas
    ];
    
    // Find shortest paths between all cities
    const shortestPaths = tripPlanner.findAllShortestPaths(cities, distances);
    
    // Plan optimal road trip items (knapsack problem)
    console.log('\n🎒 Packing for Cross-Country Road Trip:');
    const roadTripGear = [
      { name: 'Professional Camera', weight: 3, value: 20 },
      { name: 'Laptop Computer', weight: 4, value: 18 },
      { name: 'Camping Tent', weight: 6, value: 15 },
      { name: 'Portable Grill', weight: 5, value: 12 },
      { name: 'First Aid Kit', weight: 2, value: 14 },
      { name: 'Power Bank', weight: 1, value: 10 },
      { name: 'Travel Pillow', weight: 1, value: 6 },
      { name: 'Cooler', weight: 4, value: 8 },
      { name: 'Hiking Boots', weight: 2, value: 9 },
      { name: 'Road Atlas', weight: 1, value: 5 }
    ];
    
    tripPlanner.packRoadTripBag(roadTripGear, 15);
    
    // Compare different route plans (LCS)
    console.log('\n🗺️  Comparing Alternative Routes:');
    const route1 = ['Seattle', 'Portland', 'San Francisco', 'Los Angeles', 'Las Vegas'];
    const route2 = ['Seattle', 'San Francisco', 'Los Angeles', 'Las Vegas', 'Phoenix'];
    
    tripPlanner.compareRoutePlans(route1, route2);
    
    // Calculate toll change (coin change problem)
    console.log('\n💰 Toll Payment System:');
    const usCoinDenominations = [1, 5, 10, 25]; // penny, nickel, dime, quarter
    tripPlanner.makeChangeForTolls(3.47, usCoinDenominations);
    
    // Find best consecutive travel days
    console.log('\n🎆 Analyzing Trip Experience:');
    const dailyRatings = [8, -2, 5, 9, -1, 7, -3, 6, 4, -2, 8, 9];
    tripPlanner.findBestTravelStreak(dailyRatings);
    
    // Advanced: Traveling Salesman for visiting all cities
    console.log('\n🌍 Optimal Tour Planning (Traveling Salesman):');
    const tourCities = ['Start', 'City A', 'City B', 'City C'];
    const tourDistances = [
      [0, 120, 200, 180],
      [120, 0, 150, 100],
      [200, 150, 0, 90],
      [180, 100, 90, 0]
    ];
    
    AdvancedDPProblems.travelingSalesman(tourCities, tourDistances);
    
    console.log('\n✅ GPS Navigation System Demo Complete!');
  }

  /**
   * Example 5: File System Explorer
   * Combines Trees, Recursion, and Searching
   */
  createFileSystem() {
    console.log('\n📁 Interactive Example 5: File System Explorer');
    console.log('=' .repeat(60));
    
    // Create file system using company organization structure
    console.log('\n📂 Building File System Hierarchy:');
    const fileSystem = new CompanyOrganizationChart('Root', 'Computer File System');
    
    // Create directory structure
    fileSystem.addEmployee('Root', 'Documents', 'Folder', 'System', 0);
    fileSystem.addEmployee('Root', 'Pictures', 'Folder', 'System', 0);
    fileSystem.addEmployee('Root', 'Programs', 'Folder', 'System', 0);
    
    // Add subdirectories and files
    fileSystem.addEmployee('Documents', 'Work', 'Folder', 'User', 0);
    fileSystem.addEmployee('Documents', 'Personal', 'Folder', 'User', 0);
    fileSystem.addEmployee('Documents', 'resume.pdf', 'File', 'Document', 2048);
    
    fileSystem.addEmployee('Work', 'project1.docx', 'File', 'Document', 15360);
    fileSystem.addEmployee('Work', 'budget.xlsx', 'File', 'Spreadsheet', 8192);
    fileSystem.addEmployee('Work', 'presentation.pptx', 'File', 'Presentation', 25600);
    
    fileSystem.addEmployee('Personal', 'diary.txt', 'File', 'Text', 512);
    fileSystem.addEmployee('Personal', 'recipes.pdf', 'File', 'Document', 4096);
    
    fileSystem.addEmployee('Pictures', 'Vacation', 'Folder', 'User', 0);
    fileSystem.addEmployee('Pictures', 'Family', 'Folder', 'User', 0);
    
    fileSystem.addEmployee('Vacation', 'beach1.jpg', 'File', 'Image', 204800);
    fileSystem.addEmployee('Vacation', 'sunset.png', 'File', 'Image', 153600);
    
    fileSystem.addEmployee('Family', 'birthday.mp4', 'File', 'Video', 512000);
    
    fileSystem.addEmployee('Programs', 'Calculator', 'Application', 'System', 102400);
    fileSystem.addEmployee('Programs', 'TextEditor', 'Application', 'System', 51200);
    
    fileSystem.displayOrganizationChart();
    
    // File system analysis
    console.log('\n📊 File System Analysis:');
    console.log(`Total items: ${fileSystem.totalEmployees}`);
    console.log(`Directory depth: ${fileSystem.getOrganizationDepth()} levels`);
    console.log(`Total size: ${Math.round(fileSystem.ceo.getTotalSalaryBudget() / 1024)} KB`);
    
    // Find files by type
    console.log('\n🔍 File Type Analysis:');
    const allFolders = fileSystem.getAllManagers();
    const allFiles = fileSystem.getAllIndividualContributors();
    
    console.log(`Folders: ${allFolders.length}`);
    console.log(`Files: ${allFiles.length}`);
    
    fileSystem.getDepartmentSummary();
    
    // Demonstrate recursive file search
    console.log('\n🔍 Recursive File Search:');
    const recursionLearner = new RecursionLearning();
    
    // Search for specific files
    const foundProject = fileSystem.findEmployee('project1.docx');
    if (foundProject) {
      console.log(`✅ Found file: ${foundProject.name} (${foundProject.salary} bytes)`);
      
      // Show path to file
      const path = fileSystem.getReportingChain('project1.docx');
    }
    
    const foundVideo = fileSystem.findEmployee('birthday.mp4');
    if (foundVideo) {
      console.log(`✅ Found file: ${foundVideo.name} (${Math.round(foundVideo.salary / 1024)} KB)`);
    }
    
    // Contact book for file metadata
    console.log('\n📞 File Metadata Search System:');
    const fileContacts = new PhoneContactBook('File Index');
    
    // Add file metadata as "contacts"
    const fileMetadata = [
      ['resume.pdf', '2048', 'resume@docs.sys', 'documents', true],
      ['project1.docx', '15360', 'project1@work.sys', 'work', false],
      ['beach1.jpg', '204800', 'beach1@pics.sys', 'vacation', true],
      ['birthday.mp4', '512000', 'birthday@vids.sys', 'family', true]
    ];
    
    fileMetadata.forEach(([name, size, email, category, favorite]) => {
      fileContacts.addContact(name, size + ' bytes', email, category, favorite);
    });
    
    fileContacts.displayContacts();
    
    // Search for files
    console.log('\n🔍 Searching file metadata:');
    fileContacts.linearSearchByName('beach1.jpg');
    fileContacts.searchByCategory('work');
    fileContacts.multiFieldSearch('204800');
    
    console.log('\n✅ File System Explorer Demo Complete!');
  }

  /**
   * Run a specific interactive example
   */
  runExample(exampleName) {
    if (this.examples.has(exampleName)) {
      this.examples.get(exampleName)();
    } else {
      console.log(`\n❌ Example "${exampleName}" not found.`);
      this.listExamples();
    }
  }

  /**
   * List all available examples
   */
  listExamples() {
    console.log('\n🎆 Available Interactive Examples:');
    console.log('=====================================');
    console.log('1. library-system    - Digital Library Management');
    console.log('2. social-media      - Social Media Platform');
    console.log('3. restaurant-system - Restaurant Management');
    console.log('4. navigation-system - GPS Navigation System');
    console.log('5. file-system       - File System Explorer');
    console.log('\nUsage: runExample("example-name")');
  }

  /**
   * Run all examples in sequence
   */
  runAllExamples() {
    console.log('\n🎆 Running All Interactive Examples');
    console.log('====================================');
    
    const exampleNames = Array.from(this.examples.keys());
    
    exampleNames.forEach((name, index) => {
      console.log(`\n\n[${'='.repeat(10)} Example ${index + 1}/${exampleNames.length} ${'='.repeat(10)}]`);
      this.runExample(name);
      
      if (index < exampleNames.length - 1) {
        console.log('\n' + '-'.repeat(80));
        console.log('Press any key to continue to next example...');
        // In a real interactive environment, you might pause here
      }
    });
    
    console.log('\n\n✅ All Interactive Examples Complete!');
    console.log('\n📝 Summary of Concepts Demonstrated:');
    console.log('  • Arrays: Book storage, file listings');
    console.log('  • Linked Lists: Train-like data connections');
    console.log('  • Stacks: Plate dispensers, undo operations');
    console.log('  • Queues: Customer service, notifications');
    console.log('  • Trees: Organizational charts, file systems');
    console.log('  • Graphs: Social networks, navigation maps');
    console.log('  • Sorting: Organizing data efficiently');
    console.log('  • Searching: Finding information quickly');
    console.log('  • Dynamic Programming: Optimal path planning');
    console.log('  • Recursion: Hierarchical problem solving');
    
    console.log('\n🏆 You\'ve experienced the power of algorithms and data structures!');
  }

  /**
   * Performance comparison across different examples
   */
  performanceComparison() {
    console.log('\n📈 Performance Comparison Across Data Structures');
    console.log('===============================================');
    
    const testSizes = [100, 1000, 5000];
    
    testSizes.forEach(size => {
      console.log(`\n🔍 Testing with ${size} elements:`);
      
      // Array operations
      const array = new BookshelfArray(size);
      const arrayStartTime = Date.now();
      
      for (let i = 0; i < Math.min(size, 100); i++) {
        array.addBook(i, `Book ${i}`);
      }
      
      const arrayEndTime = Date.now();
      console.log(`  Array insertion: ${arrayEndTime - arrayStartTime}ms`);
      
      // Queue operations  
      const queue = new CoffeeShopQueue(size);
      const queueStartTime = Date.now();
      
      for (let i = 0; i < Math.min(size, 100); i++) {
        queue.joinLine(`Customer ${i}`, 'order', 'regular');
      }
      
      const queueEndTime = Date.now();
      console.log(`  Queue insertion: ${queueEndTime - queueStartTime}ms`);
      
      // Stack operations
      const stack = new CafeteriaPlateStack(size);
      const stackStartTime = Date.now();
      
      for (let i = 0; i < Math.min(size, 100); i++) {
        stack.addPlate('dinner', true);
      }
      
      const stackEndTime = Date.now();
      console.log(`  Stack insertion: ${stackEndTime - stackStartTime}ms`);
    });
    
    console.log('\n📊 Key Performance Insights:');
    console.log('  • Arrays: O(1) access, O(n) insertion/deletion in middle');
    console.log('  • Linked Lists: O(1) insertion/deletion, O(n) access');
    console.log('  • Stacks: O(1) push/pop operations');
    console.log('  • Queues: O(1) enqueue/dequeue operations');
    console.log('  • Trees: O(log n) search/insert/delete when balanced');
    console.log('  • Hash Tables: O(1) average case for all operations');
  }
}

// Export for use in other modules
export { InteractiveExamples };

import { fileURLToPath } from 'url';
import { argv } from 'process';
const __filename = fileURLToPath(import.meta.url);

// Example usage and demonstration
if (argv[1] === __filename) {
  console.log('🎆 Welcome to Interactive Examples for Algorithms and Data Structures!\n');
  
  const examples = new InteractiveExamples();
  
  // Show available examples
  examples.listExamples();
  
  // Run a specific example (for demonstration)
  console.log('\n🎆 Running Library System Example:');
  examples.runExample('library-system');
  
  console.log('\n\n🎆 Running Social Media Example:');
  examples.runExample('social-media');
  
  // Performance comparison
  examples.performanceComparison();
  
  console.log('\n\n🏆 Interactive Examples Complete!');
  console.log('\nTo run all examples: examples.runAllExamples()');
  console.log('To run specific example: examples.runExample("example-name")');
}