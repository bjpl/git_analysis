/**
 * Linked Lists: Train Cars Connected Together
 * 
 * Like train cars connected by couplers, each node in a linked list
 * contains data (passengers/cargo) and a link to the next car.
 */

class TrainCar {
  constructor(carType, passengers = 0) {
    this.carType = carType;           // Data: type of car
    this.passengers = passengers;     // Data: number of passengers
    this.nextCar = null;             // Link: pointer to next car
    this.carNumber = null;           // For identification
  }

  toString() {
    return `[${this.carType}(${this.passengers})]`;
  }
}

class TrainLinkedList {
  constructor(locomotiveName = 'Express Train') {
    this.locomotive = null;          // Head: front of the train
    this.caboose = null;            // Tail: end of the train
    this.trainLength = 0;           // Size: number of cars
    this.trainName = locomotiveName;
  }

  /**
   * Add a car to the front of the train (like adding locomotive)
   * Time Complexity: O(1)
   */
  addCarToFront(carType, passengers = 0) {
    const newCar = new TrainCar(carType, passengers);
    newCar.carNumber = this.trainLength + 1;
    
    if (this.locomotive === null) {
      // First car becomes both locomotive and caboose
      this.locomotive = newCar;
      this.caboose = newCar;
    } else {
      // Connect new car to current front
      newCar.nextCar = this.locomotive;
      this.locomotive = newCar;
    }
    
    this.trainLength++;
    console.log(`🚂 Added ${carType} car to front. Train length: ${this.trainLength}`);
  }

  /**
   * Add a car to the end of the train (most common operation)
   * Time Complexity: O(1) with tail pointer
   */
  addCarToEnd(carType, passengers = 0) {
    const newCar = new TrainCar(carType, passengers);
    newCar.carNumber = this.trainLength + 1;
    
    if (this.caboose === null) {
      // First car
      this.locomotive = newCar;
      this.caboose = newCar;
    } else {
      // Connect to current end
      this.caboose.nextCar = newCar;
      this.caboose = newCar;
    }
    
    this.trainLength++;
    console.log(`🚃 Added ${carType} car to end. Train length: ${this.trainLength}`);
  }

  /**
   * Insert a car at specific position
   * Time Complexity: O(n)
   */
  insertCarAt(position, carType, passengers = 0) {
    if (position < 0 || position > this.trainLength) {
      throw new Error('Invalid position for train car!');
    }
    
    if (position === 0) {
      this.addCarToFront(carType, passengers);
      return;
    }
    
    if (position === this.trainLength) {
      this.addCarToEnd(carType, passengers);
      return;
    }
    
    const newCar = new TrainCar(carType, passengers);
    newCar.carNumber = this.trainLength + 1;
    
    let current = this.locomotive;
    for (let i = 0; i < position - 1; i++) {
      current = current.nextCar;
    }
    
    newCar.nextCar = current.nextCar;
    current.nextCar = newCar;
    
    this.trainLength++;
    console.log(`🚄 Inserted ${carType} car at position ${position}`);
  }

  /**
   * Remove car from front (detach locomotive)
   * Time Complexity: O(1)
   */
  removeCarFromFront() {
    if (this.locomotive === null) {
      console.log('No cars to remove - train is empty!');
      return null;
    }
    
    const removedCar = this.locomotive;
    
    if (this.locomotive === this.caboose) {
      // Only one car
      this.locomotive = null;
      this.caboose = null;
    } else {
      this.locomotive = this.locomotive.nextCar;
    }
    
    this.trainLength--;
    console.log(`🚨 Removed ${removedCar.carType} from front`);
    return removedCar;
  }

  /**
   * Remove car from end (detach caboose)
   * Time Complexity: O(n) - need to find second-to-last
   */
  removeCarFromEnd() {
    if (this.caboose === null) {
      console.log('No cars to remove - train is empty!');
      return null;
    }
    
    if (this.locomotive === this.caboose) {
      // Only one car
      const removedCar = this.locomotive;
      this.locomotive = null;
      this.caboose = null;
      this.trainLength--;
      console.log(`🚨 Removed ${removedCar.carType} (last car)`);
      return removedCar;
    }
    
    // Find second-to-last car
    let current = this.locomotive;
    while (current.nextCar.nextCar !== null) {
      current = current.nextCar;
    }
    
    const removedCar = current.nextCar;
    current.nextCar = null;
    this.caboose = current;
    
    this.trainLength--;
    console.log(`🚨 Removed ${removedCar.carType} from end`);
    return removedCar;
  }

  /**
   * Find a specific car type
   * Time Complexity: O(n)
   */
  findCar(carType) {
    console.log(`🔍 Searching for ${carType} car...`);
    
    let current = this.locomotive;
    let position = 0;
    
    while (current !== null) {
      if (current.carType === carType) {
        console.log(`✅ Found ${carType} at position ${position}`);
        return { car: current, position };
      }
      current = current.nextCar;
      position++;
    }
    
    console.log(`❌ ${carType} not found in train`);
    return null;
  }

  /**
   * Count total passengers on train
   * Time Complexity: O(n)
   */
  getTotalPassengers() {
    let total = 0;
    let current = this.locomotive;
    
    while (current !== null) {
      total += current.passengers;
      current = current.nextCar;
    }
    
    return total;
  }

  /**
   * Reverse the train (turn it around)
   * Time Complexity: O(n)
   */
  reverseTrain() {
    console.log('🔄 Reversing the train...');
    
    let previous = null;
    let current = this.locomotive;
    this.caboose = this.locomotive;  // Old front becomes new back
    
    while (current !== null) {
      const next = current.nextCar;
      current.nextCar = previous;
      previous = current;
      current = next;
    }
    
    this.locomotive = previous;  // New front
    console.log('✅ Train reversed!');
  }

  /**
   * Display the entire train
   */
  displayTrain() {
    console.log(`\n🚆 ${this.trainName} (${this.trainLength} cars, ${this.getTotalPassengers()} passengers):`);
    
    if (this.locomotive === null) {
      console.log('Empty train - no cars attached\n');
      return;
    }
    
    let trainVisualization = '';
    let current = this.locomotive;
    let position = 0;
    
    while (current !== null) {
      trainVisualization += current.toString();
      if (current.nextCar !== null) {
        trainVisualization += '===';
      }
      current = current.nextCar;
      position++;
    }
    
    console.log(trainVisualization);
    console.log(`Direction: ➡️  (Front: ${this.locomotive.carType}, Back: ${this.caboose.carType})\n`);
  }

  /**
   * Connect two trains together
   */
  static connectTrains(train1, train2) {
    if (train1.caboose === null) {
      console.log('Cannot connect to empty train');
      return;
    }
    
    if (train2.locomotive === null) {
      console.log('Cannot connect empty train');
      return;
    }
    
    console.log(`🔗 Connecting ${train1.trainName} with ${train2.trainName}`);
    
    train1.caboose.nextCar = train2.locomotive;
    train1.caboose = train2.caboose;
    train1.trainLength += train2.trainLength;
    train1.trainName += ' + ' + train2.trainName;
    
    // Clear the second train
    train2.locomotive = null;
    train2.caboose = null;
    train2.trainLength = 0;
    
    console.log('✅ Trains connected!');
  }

  /**
   * Real-world applications demonstration
   */
  static demonstrateApplications() {
    console.log(`\n🌟 Real-World Applications of Linked Lists:\n\n` +
      `1. 🎵 Music Playlist: Songs linked to next song\n` +
      `2. 🌐 Browser History: Pages linked forward/backward\n` +
      `3. 📱 Contact Lists: Scrollable phone contacts\n` +
      `4. 🎮 Game Levels: Progression through levels\n` +
      `5. 📊 Undo Functionality: Operations linked in sequence\n` +
      `6. 📦 Package Delivery: Routes linked together\n` +
      `7. 🧠 Memory Management: Free memory blocks\n`);
  }
}

/**
 * Double Linked List: Train Cars with Front and Back Connections
 */
class DoubleTrainCar {
  constructor(carType, passengers = 0) {
    this.carType = carType;
    this.passengers = passengers;
    this.nextCar = null;      // Link to car behind
    this.previousCar = null;  // Link to car in front
  }

  toString() {
    return `[${this.carType}(${this.passengers})]`;
  }
}

class DoublyLinkedTrain {
  constructor(trainName = 'Double Express') {
    this.locomotive = null;
    this.caboose = null;
    this.trainLength = 0;
    this.trainName = trainName;
  }

  /**
   * Add car to end with bidirectional links
   * Time Complexity: O(1)
   */
  addCar(carType, passengers = 0) {
    const newCar = new DoubleTrainCar(carType, passengers);
    
    if (this.locomotive === null) {
      this.locomotive = newCar;
      this.caboose = newCar;
    } else {
      newCar.previousCar = this.caboose;
      this.caboose.nextCar = newCar;
      this.caboose = newCar;
    }
    
    this.trainLength++;
    console.log(`🚅 Added ${carType} with bidirectional links`);
  }

  /**
   * Traverse train backwards (caboose to locomotive)
   * Time Complexity: O(n)
   */
  displayTrainReverse() {
    console.log(`\n🔙 ${this.trainName} (Reverse View):`);
    
    let trainVisualization = '';
    let current = this.caboose;
    
    while (current !== null) {
      trainVisualization += current.toString();
      if (current.previousCar !== null) {
        trainVisualization += '===';
      }
      current = current.previousCar;
    }
    
    console.log(trainVisualization);
    console.log(`Direction: ⬅️  (Back to Front)\n`);
  }
}

/**
 * Practice Problems for Linked Lists
 */
class LinkedListPracticeProblems {
  /**
   * Problem 1: Detect if train has a loop (circular track)
   * Floyd's Cycle Detection Algorithm
   */
  static detectLoop(train) {
    if (!train.locomotive) return false;
    
    let tortoise = train.locomotive;  // Slow pointer
    let hare = train.locomotive;      // Fast pointer
    
    // Move pointers at different speeds
    while (hare && hare.nextCar) {
      tortoise = tortoise.nextCar;
      hare = hare.nextCar.nextCar;
      
      if (tortoise === hare) {
        return true;  // Loop detected!
      }
    }
    
    return false;
  }

  /**
   * Problem 2: Find the middle car of the train
   * Two-pointer technique
   */
  static findMiddleCar(train) {
    if (!train.locomotive) return null;
    
    let slow = train.locomotive;
    let fast = train.locomotive;
    
    while (fast && fast.nextCar) {
      slow = slow.nextCar;
      fast = fast.nextCar.nextCar;
    }
    
    return slow;
  }

  /**
   * Problem 3: Merge two sorted trains
   */
  static mergeSortedTrains(train1, train2) {
    const mergedTrain = new TrainLinkedList('Merged Express');
    let current1 = train1.locomotive;
    let current2 = train2.locomotive;
    
    while (current1 && current2) {
      if (current1.passengers <= current2.passengers) {
        mergedTrain.addCarToEnd(current1.carType, current1.passengers);
        current1 = current1.nextCar;
      } else {
        mergedTrain.addCarToEnd(current2.carType, current2.passengers);
        current2 = current2.nextCar;
      }
    }
    
    // Add remaining cars
    while (current1) {
      mergedTrain.addCarToEnd(current1.carType, current1.passengers);
      current1 = current1.nextCar;
    }
    
    while (current2) {
      mergedTrain.addCarToEnd(current2.carType, current2.passengers);
      current2 = current2.nextCar;
    }
    
    return mergedTrain;
  }
}

// Export for use in other modules
export { 
  TrainCar, 
  TrainLinkedList, 
  DoubleTrainCar, 
  DoublyLinkedTrain, 
  LinkedListPracticeProblems 
};

import { fileURLToPath } from 'url';
import { argv } from 'process';
const __filename = fileURLToPath(import.meta.url);

// Example usage and demonstration
if (argv[1] === __filename) {
  console.log('🚆 Welcome to the Train Linked List Learning Module!\n');
  
  // Create a train
  const expressTrain = new TrainLinkedList('City Express');
  
  // Add cars
  console.log('🚂 Building the train:');
  expressTrain.addCarToEnd('Passenger', 45);
  expressTrain.addCarToEnd('Dining', 20);
  expressTrain.addCarToEnd('Cargo', 0);
  expressTrain.addCarToEnd('Passenger', 38);
  
  expressTrain.displayTrain();
  
  // Insert a car in the middle
  console.log('🚄 Adding a car in the middle:');
  expressTrain.insertCarAt(2, 'Sleeper', 12);
  expressTrain.displayTrain();
  
  // Search for a car
  console.log('🔍 Searching for cars:');
  expressTrain.findCar('Dining');
  expressTrain.findCar('Luxury');
  
  // Remove cars
  console.log('\n🚨 Removing cars:');
  expressTrain.removeCarFromFront();
  expressTrain.removeCarFromEnd();
  expressTrain.displayTrain();
  
  // Reverse the train
  console.log('🔄 Reversing train direction:');
  expressTrain.reverseTrain();
  expressTrain.displayTrain();
  
  // Demonstrate doubly linked train
  console.log('🚅 Creating a doubly-linked train:');
  const doubleTrain = new DoublyLinkedTrain('Bi-Directional Express');
  doubleTrain.addCar('Engine', 0);
  doubleTrain.addCar('First Class', 20);
  doubleTrain.addCar('Economy', 60);
  doubleTrain.displayTrainReverse();
  
  // Show real-world applications
  TrainLinkedList.demonstrateApplications();
  
  // Practice problems
  console.log('\n🧠 Practice Problems:');
  const middleCar = LinkedListPracticeProblems.findMiddleCar(expressTrain);
  console.log('Middle car:', middleCar ? middleCar.carType : 'None');
  
  console.log('Loop detection:', LinkedListPracticeProblems.detectLoop(expressTrain));
}