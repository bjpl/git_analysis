/**
 * Queues: Waiting in Line at a Coffee Shop
 * 
 * Just like customers waiting in line at a coffee shop where the first person
 * to arrive is the first person served, queues follow First-In-First-Out (FIFO).
 */

class CoffeeShopQueue {
  constructor(maxCapacity = 20) {
    this.customers = [];                  // Array to store customers
    this.maxCapacity = maxCapacity;       // Maximum line capacity
    this.customerCounter = 0;             // Unique ID for each customer
    this.totalServed = 0;                 // Track total customers served
    this.averageWaitTime = 0;             // Performance metric
  }

  /**
   * Enqueue: Customer joins the line (add to rear)
   * Time Complexity: O(1)
   */
  joinLine(customerName, orderType = 'coffee', priority = 'regular') {
    if (this.isFull()) {
      console.log(`🚨 ${customerName} couldn't join - line is full! (${this.maxCapacity} max)`);
      return false;
    }
    
    const customer = {
      id: ++this.customerCounter,
      name: customerName,
      orderType,
      priority,
      joinTime: Date.now(),
      position: this.size() + 1
    };
    
    this.customers.push(customer);
    console.log(`👤 ${customerName} joined the line for ${orderType} (Position ${customer.position})`);
    
    if (this.size() === this.maxCapacity) {
      console.log('⚠️  Coffee shop line is now at capacity!');
    }
    
    return true;
  }

  /**
   * Dequeue: Serve the next customer (remove from front)
   * Time Complexity: O(n) for array implementation
   */
  serveCustomer() {
    if (this.isEmpty()) {
      console.log('🚨 No customers to serve - line is empty!');
      return null;
    }
    
    const customer = this.customers.shift(); // Remove from front
    const waitTime = (Date.now() - customer.joinTime) / 1000; // Convert to seconds
    
    this.totalServed++;
    this.updateAverageWaitTime(waitTime);
    
    console.log(`☕ Serving ${customer.name} - ${customer.orderType} (waited ${waitTime.toFixed(1)}s)`);
    
    // Update positions for remaining customers
    this.updatePositions();
    
    return customer;
  }

  /**
   * Peek: See who's next without serving them
   * Time Complexity: O(1)
   */
  peekNext() {
    if (this.isEmpty()) {
      console.log('No customers in line to peek at');
      return null;
    }
    
    const nextCustomer = this.customers[0];
    console.log(`👀 Next customer: ${nextCustomer.name} (${nextCustomer.orderType})`);
    return nextCustomer;
  }

  /**
   * Check if queue is empty
   * Time Complexity: O(1)
   */
  isEmpty() {
    return this.customers.length === 0;
  }

  /**
   * Check if queue is full
   * Time Complexity: O(1)
   */
  isFull() {
    return this.customers.length >= this.maxCapacity;
  }

  /**
   * Get current number of customers
   * Time Complexity: O(1)
   */
  size() {
    return this.customers.length;
  }

  /**
   * Find a customer in line
   * Time Complexity: O(n)
   */
  findCustomer(customerName) {
    for (let i = 0; i < this.customers.length; i++) {
      if (this.customers[i].name === customerName) {
        const customer = this.customers[i];
        console.log(`🔍 Found ${customerName} at position ${i + 1}`);
        return { customer, position: i + 1 };
      }
    }
    
    console.log(`❌ ${customerName} is not in line`);
    return null;
  }

  /**
   * Estimate wait time for new customer
   * Time Complexity: O(1)
   */
  estimateWaitTime(serviceTimePerCustomer = 2) {
    const estimatedTime = this.size() * serviceTimePerCustomer;
    console.log(`⏱️  Estimated wait time: ${estimatedTime} minutes`);
    return estimatedTime;
  }

  /**
   * Display current line status
   */
  displayLine() {
    console.log(`\n☕ Coffee Shop Queue Status:`);
    console.log(`Line: ${this.size()}/${this.maxCapacity} customers`);
    console.log(`Total served today: ${this.totalServed}`);
    console.log(`Average wait time: ${this.averageWaitTime.toFixed(1)}s`);
    
    if (this.isEmpty()) {
      console.log('\n👀 [EMPTY LINE - No customers waiting]');
    } else {
      console.log('\n👥 Current line (Front to Back):');
      
      this.customers.forEach((customer, index) => {
        const waitTime = ((Date.now() - customer.joinTime) / 1000).toFixed(1);
        const arrow = index === 0 ? '➡️ ' : '   ';
        const priority = customer.priority === 'priority' ? '⭐' : '';
        
        console.log(`${arrow}${index + 1}. ${customer.name} - ${customer.orderType} ${priority}(${waitTime}s)`);
      });
      
      console.log('\n   [👨‍🍳 Barista serving here]');
    }
    
    console.log('\n');
  }

  /**
   * Simulate rush hour service
   */
  simulateRushHour(newCustomers, serviceSpeed = 2000) {
    console.log(`🎆 Rush hour! ${newCustomers.length} customers arriving...`);
    
    // Add all customers to line
    newCustomers.forEach(customer => {
      this.joinLine(customer.name, customer.order, customer.priority || 'regular');
    });
    
    this.displayLine();
    
    // Serve customers at intervals
    const servingInterval = setInterval(() => {
      if (!this.isEmpty()) {
        this.serveCustomer();
        
        if (this.size() % 3 === 0) {
          this.displayLine();
        }
      } else {
        clearInterval(servingInterval);
        console.log('✅ Rush hour complete! All customers served.');
        this.displayPerformanceStats();
      }
    }, serviceSpeed);
    
    // Auto-clear interval after reasonable time
    setTimeout(() => clearInterval(servingInterval), newCustomers.length * serviceSpeed + 5000);
  }

  /**
   * Helper methods
   */
  updatePositions() {
    this.customers.forEach((customer, index) => {
      customer.position = index + 1;
    });
  }

  updateAverageWaitTime(newWaitTime) {
    this.averageWaitTime = ((this.averageWaitTime * (this.totalServed - 1)) + newWaitTime) / this.totalServed;
  }

  displayPerformanceStats() {
    console.log('\n📊 Performance Statistics:');
    console.log(`- Total customers served: ${this.totalServed}`);
    console.log(`- Average wait time: ${this.averageWaitTime.toFixed(1)} seconds`);
    console.log(`- Current line length: ${this.size()}`);
  }

  /**
   * Clear the entire line (end of day)
   */
  clearLine() {
    const count = this.customers.length;
    this.customers = [];
    console.log(`🧹 Cleared line - ${count} customers sent home`);
    return count;
  }

  /**
   * Real-world applications demonstration
   */
  static demonstrateApplications() {
    console.log(`\n🌟 Real-World Applications of Queues:\n\n` +
      `1. 📱 Print Queue: Documents waiting to print\n` +
      `2. 🌐 Web Server Requests: HTTP requests processing\n` +
      `3. 🎮 CPU Scheduling: Process execution order\n` +
      `4. 🎵 Music Streaming: Song playback buffer\n` +
      `5. 🚗 Traffic Systems: Cars at traffic lights\n` +
      `6. 🏥 Hospital Triage: Patient treatment order\n` +
      `7. 📦 Package Delivery: Order fulfillment\n`);
  }
}

/**
 * Priority Queue: VIP Coffee Service
 * Customers with higher priority get served first
 */
class PriorityQueue {
  constructor(maxCapacity = 15) {
    this.customers = [];              // Array of priority queues
    this.maxCapacity = maxCapacity;
    this.priorities = ['vip', 'regular', 'student'];  // Highest to lowest
  }

  /**
   * Add customer with priority
   * Time Complexity: O(log n) for heap, O(n) for array
   */
  enqueue(customerName, orderType, priority = 'regular') {
    if (this.size() >= this.maxCapacity) {
      console.log(`🚨 ${customerName} - Priority line full!`);
      return false;
    }
    
    const customer = {
      name: customerName,
      orderType,
      priority,
      joinTime: Date.now(),
      id: Math.random().toString(36).substr(2, 9)
    };
    
    // Insert customer in correct position based on priority
    let inserted = false;
    for (let i = 0; i < this.customers.length; i++) {
      if (this.getPriorityValue(priority) < this.getPriorityValue(this.customers[i].priority)) {
        this.customers.splice(i, 0, customer);
        inserted = true;
        break;
      }
    }
    
    if (!inserted) {
      this.customers.push(customer);
    }
    
    const priorityEmoji = priority === 'vip' ? '🌟' : priority === 'student' ? '🎓' : '👤';
    console.log(`${priorityEmoji} ${customerName} (${priority}) joined priority line`);
    
    return true;
  }

  /**
   * Serve highest priority customer
   * Time Complexity: O(1)
   */
  dequeue() {
    if (this.isEmpty()) {
      console.log('No customers in priority line');
      return null;
    }
    
    const customer = this.customers.shift();
    const waitTime = (Date.now() - customer.joinTime) / 1000;
    
    const priorityEmoji = customer.priority === 'vip' ? '🌟' : 
                         customer.priority === 'student' ? '🎓' : '👤';
    
    console.log(`☕ Priority served: ${priorityEmoji} ${customer.name} (${waitTime.toFixed(1)}s)`);
    return customer;
  }

  getPriorityValue(priority) {
    return this.priorities.indexOf(priority);
  }

  isEmpty() {
    return this.customers.length === 0;
  }

  size() {
    return this.customers.length;
  }

  displayPriorityLine() {
    console.log('\n🌟 Priority Coffee Line:');
    
    if (this.isEmpty()) {
      console.log('[EMPTY PRIORITY LINE]');
      return;
    }
    
    const priorityCounts = { vip: 0, regular: 0, student: 0 };
    
    this.customers.forEach((customer, index) => {
      priorityCounts[customer.priority]++;
      const emoji = customer.priority === 'vip' ? '🌟' : 
                   customer.priority === 'student' ? '🎓' : '👤';
      const arrow = index === 0 ? '➡️ ' : '   ';
      
      console.log(`${arrow}${index + 1}. ${emoji} ${customer.name} (${customer.priority})`);
    });
    
    console.log(`\nPriority breakdown: 🌟 ${priorityCounts.vip} VIP, 👤 ${priorityCounts.regular} Regular, 🎓 ${priorityCounts.student} Student`);
  }
}

/**
 * Circular Queue: Drive-Through Coffee Service
 * Fixed-size queue that reuses empty spaces
 */
class DriveThruQueue {
  constructor(capacity = 8) {
    this.queue = new Array(capacity);
    this.front = 0;
    this.rear = 0;
    this.size = 0;
    this.capacity = capacity;
    this.orderCounter = 0;
  }

  /**
   * Add car to drive-through
   * Time Complexity: O(1)
   */
  addCar(carModel, orderType) {
    if (this.isFull()) {
      console.log(`🚨 Drive-through full! ${carModel} needs to wait.`);
      return false;
    }
    
    const order = {
      id: ++this.orderCounter,
      carModel,
      orderType,
      arrivalTime: Date.now()
    };
    
    this.queue[this.rear] = order;
    this.rear = (this.rear + 1) % this.capacity;
    this.size++;
    
    console.log(`🚗 ${carModel} entered drive-through (Order #${order.id})`);
    return true;
  }

  /**
   * Serve car at front window
   * Time Complexity: O(1)
   */
  serveCar() {
    if (this.isEmpty()) {
      console.log('No cars in drive-through');
      return null;
    }
    
    const order = this.queue[this.front];
    this.queue[this.front] = null; // Clear spot
    this.front = (this.front + 1) % this.capacity;
    this.size--;
    
    const serviceTime = (Date.now() - order.arrivalTime) / 1000;
    console.log(`☕ Served ${order.carModel} - Order #${order.id} (${serviceTime.toFixed(1)}s)`);
    
    return order;
  }

  isEmpty() {
    return this.size === 0;
  }

  isFull() {
    return this.size === this.capacity;
  }

  displayDriveThru() {
    console.log('\n🚗 Drive-Through Queue:');
    console.log(`Cars: ${this.size}/${this.capacity}`);
    
    if (this.isEmpty()) {
      console.log('[EMPTY DRIVE-THROUGH]');
      return;
    }
    
    console.log('\nQueue positions:');
    let current = this.front;
    for (let i = 0; i < this.size; i++) {
      const order = this.queue[current];
      const position = i === 0 ? '➡️  [SERVICE WINDOW]' : `   Position ${i + 1}`;
      console.log(`${position} ${order.carModel} - ${order.orderType}`);
      current = (current + 1) % this.capacity;
    }
  }
}

/**
 * Queue Practice Problems
 */
class QueuePracticeProblems {
  /**
   * Problem 1: Generate binary numbers using queue
   * Print binary representation of numbers 1 to n
   */
  static generateBinaryNumbers(n) {
    console.log(`🔢 Generating binary numbers 1 to ${n}:`);
    
    const queue = ['1'];
    const results = [];
    
    for (let i = 1; i <= n; i++) {
      const binary = queue.shift();
      results.push(`${i}: ${binary}`);
      console.log(`  ${i}: ${binary}`);
      
      // Generate next level
      queue.push(binary + '0');
      queue.push(binary + '1');
    }
    
    return results;
  }

  /**
   * Problem 2: Sliding window maximum
   * Find maximum in each window of k consecutive elements
   */
  static slidingWindowMaximum(arr, k) {
    console.log(`📊 Sliding window maximum (k=${k}): [${arr.join(', ')}]`);
    
    const result = [];
    const deque = []; // Store indices
    
    for (let i = 0; i < arr.length; i++) {
      // Remove indices outside current window
      while (deque.length && deque[0] <= i - k) {
        deque.shift();
      }
      
      // Remove smaller elements from rear
      while (deque.length && arr[deque[deque.length - 1]] <= arr[i]) {
        deque.pop();
      }
      
      deque.push(i);
      
      // Add maximum of current window to result
      if (i >= k - 1) {
        result.push(arr[deque[0]]);
        console.log(`  Window [${i-k+1}, ${i}]: max = ${arr[deque[0]]}`);
      }
    }
    
    console.log(`  Result: [${result.join(', ')}]`);
    return result;
  }

  /**
   * Problem 3: Hot Potato (Josephus Problem)
   * People in circle, eliminate every kth person
   */
  static hotPotato(names, num) {
    console.log(`🥔 Hot Potato game with ${names.length} people, count ${num}:`);
    
    const queue = [...names];
    const eliminated = [];
    
    while (queue.length > 1) {
      // Pass the potato (rotate queue)
      for (let i = 0; i < num - 1; i++) {
        queue.push(queue.shift());
      }
      
      // Eliminate current person
      const eliminated_person = queue.shift();
      eliminated.push(eliminated_person);
      console.log(`  Eliminated: ${eliminated_person}`);
      console.log(`  Remaining: [${queue.join(', ')}]`);
    }
    
    console.log(`  🏆 Winner: ${queue[0]}`);
    return { winner: queue[0], eliminationOrder: eliminated };
  }

  /**
   * Problem 4: Implement stack using queues
   * Show how to implement LIFO using FIFO operations
   */
  static stackUsingQueues() {
    console.log('🔄 Implementing Stack using Two Queues:');
    
    class StackWithQueues {
      constructor() {
        this.queue1 = [];
        this.queue2 = [];
      }
      
      push(item) {
        this.queue1.push(item);
        console.log(`  Pushed ${item}, queue1: [${this.queue1.join(', ')}]`);
      }
      
      pop() {
        if (this.queue1.length === 0) {
          console.log('  Stack is empty!');
          return null;
        }
        
        // Move all but last element to queue2
        while (this.queue1.length > 1) {
          this.queue2.push(this.queue1.shift());
        }
        
        // Last element is our stack top
        const popped = this.queue1.shift();
        
        // Swap queues
        [this.queue1, this.queue2] = [this.queue2, this.queue1];
        
        console.log(`  Popped ${popped}, queue1: [${this.queue1.join(', ')}]`);
        return popped;
      }
    }
    
    const stack = new StackWithQueues();
    stack.push(1);
    stack.push(2);
    stack.push(3);
    stack.pop();
    stack.pop();
    
    return stack;
  }
}

// Export for use in other modules
export { 
  CoffeeShopQueue, 
  PriorityQueue, 
  DriveThruQueue, 
  QueuePracticeProblems 
};

import { fileURLToPath } from 'url';
import { argv } from 'process';
const __filename = fileURLToPath(import.meta.url);

// Example usage and demonstration
if (argv[1] === __filename) {
  console.log('☕ Welcome to the Coffee Shop Queue Learning Module!\n');
  
  // Create a coffee shop queue
  const coffeeShop = new CoffeeShopQueue(8);
  
  // Customers join the line
  console.log('👥 Customers joining the line:');
  coffeeShop.joinLine('Alice', 'latte');
  coffeeShop.joinLine('Bob', 'espresso');
  coffeeShop.joinLine('Charlie', 'cappuccino');
  coffeeShop.joinLine('Diana', 'americano');
  
  coffeeShop.displayLine();
  
  // Peek at next customer
  console.log('👀 Checking who\'s next:');
  coffeeShop.peekNext();
  
  // Serve some customers
  console.log('\n☕ Serving customers:');
  coffeeShop.serveCustomer();
  coffeeShop.serveCustomer();
  
  coffeeShop.displayLine();
  
  // Find a customer
  console.log('🔍 Looking for customers:');
  coffeeShop.findCustomer('Charlie');
  coffeeShop.findCustomer('Alice');
  
  // Estimate wait time
  console.log('\n⏱️  Wait time estimation:');
  coffeeShop.estimateWaitTime(3);
  
  // Priority queue demonstration
  console.log('\n🌟 Priority Queue Demo:');
  const priorityShop = new PriorityQueue(10);
  
  priorityShop.enqueue('Regular Joe', 'coffee', 'regular');
  priorityShop.enqueue('VIP Sarah', 'latte', 'vip');
  priorityShop.enqueue('Student Mike', 'coffee', 'student');
  priorityShop.enqueue('VIP John', 'cappuccino', 'vip');
  
  priorityShop.displayPriorityLine();
  
  console.log('\nServing by priority:');
  priorityShop.dequeue();
  priorityShop.dequeue();
  
  // Drive-through queue
  console.log('\n🚗 Drive-Through Demo:');
  const driveThru = new DriveThruQueue(4);
  
  driveThru.addCar('Honda Civic', 'coffee and donut');
  driveThru.addCar('Toyota Camry', 'latte');
  driveThru.addCar('Ford F-150', 'espresso');
  
  driveThru.displayDriveThru();
  
  console.log('\nServing drive-through:');
  driveThru.serveCar();
  driveThru.displayDriveThru();
  
  // Show real-world applications
  CoffeeShopQueue.demonstrateApplications();
  
  // Practice problems
  console.log('\n🧠 Practice Problems:');
  
  console.log('\n1. Binary Numbers:');
  QueuePracticeProblems.generateBinaryNumbers(5);
  
  console.log('\n2. Sliding Window Maximum:');
  QueuePracticeProblems.slidingWindowMaximum([1, 3, -1, -3, 5, 3, 6, 7], 3);
  
  console.log('\n3. Hot Potato:');
  QueuePracticeProblems.hotPotato(['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'], 3);
  
  console.log('\n4. Stack using Queues:');
  QueuePracticeProblems.stackUsingQueues();
}