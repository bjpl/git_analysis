/**
 * Stacks: Plate Dispensers in Cafeterias
 * 
 * Just like a plate dispenser where you can only add or remove plates from the top,
 * stacks follow the Last-In-First-Out (LIFO) principle.
 */

class CafeteriaPlateStack {
  constructor(maxCapacity = 50) {
    this.plates = [];                    // Array to store plates
    this.maxCapacity = maxCapacity;      // Maximum plates the dispenser can hold
    this.plateCounter = 0;               // Unique ID for each plate
  }

  /**
   * Push a plate onto the stack (add to top)
   * Time Complexity: O(1)
   */
  addPlate(plateType = 'dinner', isClean = true) {
    if (this.isFull()) {
      console.log('🚨 Plate dispenser is full! Cannot add more plates.');
      return false;
    }
    
    const plate = {
      id: ++this.plateCounter,
      type: plateType,
      isClean,
      addedAt: new Date().toLocaleTimeString()
    };
    
    this.plates.push(plate);
    console.log(`🍽️  Added ${plateType} plate #${plate.id} to top of stack`);
    
    if (this.plates.length === this.maxCapacity) {
      console.log('⚠️  Plate dispenser is now full!');
    }
    
    return true;
  }

  /**
   * Pop a plate from the stack (remove from top)
   * Time Complexity: O(1)
   */
  takePlate() {
    if (this.isEmpty()) {
      console.log('🚨 No plates available! Dispenser is empty.');
      return null;
    }
    
    const plate = this.plates.pop();
    console.log(`🍽️  Took ${plate.type} plate #${plate.id} from top`);
    
    if (!plate.isClean) {
      console.log('⚠️  Warning: This plate needs cleaning!');
    }
    
    return plate;
  }

  /**
   * Peek at the top plate without removing it
   * Time Complexity: O(1)
   */
  peekAtTopPlate() {
    if (this.isEmpty()) {
      console.log('No plates to peek at - dispenser is empty');
      return null;
    }
    
    const topPlate = this.plates[this.plates.length - 1];
    console.log(`👀 Top plate: ${topPlate.type} #${topPlate.id} (${topPlate.isClean ? 'Clean' : 'Dirty'})`);
    return topPlate;
  }

  /**
   * Check if the stack is empty
   * Time Complexity: O(1)
   */
  isEmpty() {
    return this.plates.length === 0;
  }

  /**
   * Check if the stack is full
   * Time Complexity: O(1)
   */
  isFull() {
    return this.plates.length >= this.maxCapacity;
  }

  /**
   * Get current number of plates
   * Time Complexity: O(1)
   */
  size() {
    return this.plates.length;
  }

  /**
   * Clear all plates (for cleaning/maintenance)
   * Time Complexity: O(1)
   */
  clearStack() {
    const removedCount = this.plates.length;
    this.plates = [];
    console.log(`🧹 Cleared ${removedCount} plates for cleaning`);
    return removedCount;
  }

  /**
   * Display current state of the plate dispenser
   */
  displayStack() {
    console.log(`\n🍽️  Cafeteria Plate Dispenser Status:`);
    console.log(`Capacity: ${this.size()}/${this.maxCapacity} plates`);
    
    if (this.isEmpty()) {
      console.log('\u2b07️  [EMPTY DISPENSER]');
    } else {
      console.log('\n  Stack (Top to Bottom):');
      
      // Show plates from top to bottom
      for (let i = this.plates.length - 1; i >= 0; i--) {
        const plate = this.plates[i];
        const isTop = i === this.plates.length - 1;
        const arrow = isTop ? '⬇️  ' : '   ';
        const status = plate.isClean ? '✅' : '❌';
        
        console.log(`${arrow}[${plate.type} #${plate.id} ${status}]`);
        
        // Only show top 5 plates for readability
        if (this.plates.length - i > 5 && i > 0) {
          console.log(`   ... (${i + 1} more plates below)`);
          break;
        }
      }
    }
    console.log('\n');
  }

  /**
   * Simulate rush hour - rapid plate usage
   */
  simulateRushHour(customers = 10) {
    console.log(`🎆 Rush hour starting! ${customers} customers incoming...`);
    
    const startingPlates = this.size();
    let platesServed = 0;
    
    for (let i = 1; i <= customers; i++) {
      const plate = this.takePlate();
      if (plate) {
        platesServed++;
        console.log(`Customer ${i} served with plate #${plate.id}`);
      } else {
        console.log(`🚨 Customer ${i} couldn't get a plate!`);
        break;
      }
      
      // Simulate random restocking during rush
      if (Math.random() < 0.3 && !this.isFull()) {
        this.addPlate('dinner', true);
        console.log('👨‍🍳 Kitchen staff restocked a plate!');
      }
    }
    
    console.log(`\n📊 Rush hour summary:`);
    console.log(`- Started with: ${startingPlates} plates`);
    console.log(`- Customers served: ${platesServed}`);
    console.log(`- Plates remaining: ${this.size()}`);
  }

  /**
   * Real-world applications demonstration
   */
  static demonstrateApplications() {
    console.log(`\n🌟 Real-World Applications of Stacks:\n\n` +
      `1. 📱 Function Call Stack: Method calls in programming\n` +
      `2. ⬅️  Undo Operations: Ctrl+Z in text editors\n` +
      `3. 🌐 Browser History: Back button navigation\n` +
      `4. 🧠 Expression Evaluation: Mathematical expressions\n` +
      `5. 📚 Book Stack: Physical books piled up\n` +
      `6. 🎮 Game States: Save/load game positions\n` +
      `7. 🎨 Photoshop Layers: Image editing layers\n`);
  }
}

/**
 * Advanced Stack: Multi-Stack Plate Dispenser System
 */
class MultiPlateDispenser {
  constructor(numberOfStacks = 3, capacityPerStack = 20) {
    this.stacks = [];
    this.stackNames = ['Dinner Plates', 'Salad Plates', 'Dessert Plates'];
    
    for (let i = 0; i < numberOfStacks; i++) {
      this.stacks.push(new CafeteriaPlateStack(capacityPerStack));
    }
  }

  /**
   * Add plate to appropriate stack
   */
  addPlateToStack(stackIndex, plateType, isClean = true) {
    if (stackIndex < 0 || stackIndex >= this.stacks.length) {
      console.log('Invalid stack index!');
      return false;
    }
    
    console.log(`🍽️  Adding to ${this.stackNames[stackIndex]}:`);
    return this.stacks[stackIndex].addPlate(plateType, isClean);
  }

  /**
   * Get plate from specific stack
   */
  getPlateFromStack(stackIndex) {
    if (stackIndex < 0 || stackIndex >= this.stacks.length) {
      console.log('Invalid stack index!');
      return null;
    }
    
    console.log(`🍽️  Taking from ${this.stackNames[stackIndex]}:`);
    return this.stacks[stackIndex].takePlate();
  }

  /**
   * Find stack with available plates
   */
  findAvailableStack() {
    for (let i = 0; i < this.stacks.length; i++) {
      if (!this.stacks[i].isEmpty()) {
        return i;
      }
    }
    return -1; // All stacks empty
  }

  /**
   * Display all stacks
   */
  displayAllStacks() {
    console.log('\n🏢 Multi-Stack Plate Dispenser System:');
    
    for (let i = 0; i < this.stacks.length; i++) {
      console.log(`\n${this.stackNames[i]}:`);
      const stack = this.stacks[i];
      console.log(`  ${stack.size()}/${stack.maxCapacity} plates`);
      
      if (stack.isEmpty()) {
        console.log('  [EMPTY]');
      } else {
        const topPlate = stack.plates[stack.plates.length - 1];
        console.log(`  Top: ${topPlate.type} #${topPlate.id}`);
      }
    }
  }
}

/**
 * Stack Practice Problems
 */
class StackPracticeProblems {
  /**
   * Problem 1: Balanced Parentheses (like checking plate stacking)
   * Check if parentheses are properly nested
   */
  static isBalanced(expression) {
    const stack = [];
    const pairs = { '(': ')', '[': ']', '{': '}' };
    
    console.log(`🔍 Checking if expression is balanced: ${expression}`);
    
    for (const char of expression) {
      if (pairs[char]) {
        // Opening bracket - push to stack
        stack.push(char);
        console.log(`  Pushed '${char}' onto stack`);
      } else if (Object.values(pairs).includes(char)) {
        // Closing bracket - check if matches
        if (stack.length === 0) {
          console.log(`  ❌ No matching opening bracket for '${char}'`);
          return false;
        }
        
        const lastOpening = stack.pop();
        if (pairs[lastOpening] !== char) {
          console.log(`  ❌ '${lastOpening}' doesn't match '${char}'`);
          return false;
        }
        console.log(`  Matched '${lastOpening}' with '${char}'`);
      }
    }
    
    const result = stack.length === 0;
    console.log(`  Result: ${result ? '✅ Balanced' : '❌ Unbalanced'}`);
    return result;
  }

  /**
   * Problem 2: Evaluate Postfix Expression (Reverse Polish Notation)
   * Like calculating ingredients needed based on plate stack
   */
  static evaluatePostfix(expression) {
    const stack = [];
    const tokens = expression.split(' ');
    
    console.log(`🧠 Evaluating postfix: ${expression}`);
    
    for (const token of tokens) {
      if (!isNaN(token)) {
        // Number - push to stack
        stack.push(parseFloat(token));
        console.log(`  Pushed ${token} onto stack: [${stack.join(', ')}]`);
      } else {
        // Operator - pop two operands
        if (stack.length < 2) {
          console.log(`  ❌ Not enough operands for ${token}`);
          return null;
        }
        
        const b = stack.pop();
        const a = stack.pop();
        let result;
        
        switch (token) {
          case '+':
            result = a + b;
            break;
          case '-':
            result = a - b;
            break;
          case '*':
            result = a * b;
            break;
          case '/':
            result = a / b;
            break;
          default:
            console.log(`  ❌ Unknown operator: ${token}`);
            return null;
        }
        
        stack.push(result);
        console.log(`  ${a} ${token} ${b} = ${result}, stack: [${stack.join(', ')}]`);
      }
    }
    
    if (stack.length !== 1) {
      console.log(`  ❌ Invalid expression - stack has ${stack.length} elements`);
      return null;
    }
    
    console.log(`  ✅ Result: ${stack[0]}`);
    return stack[0];
  }

  /**
   * Problem 3: Convert Infix to Postfix
   * Like organizing plate orders for kitchen efficiency
   */
  static infixToPostfix(infix) {
    const stack = [];
    const output = [];
    const precedence = { '+': 1, '-': 1, '*': 2, '/': 2 };
    
    console.log(`🔄 Converting infix to postfix: ${infix}`);
    
    for (const char of infix) {
      if (!isNaN(char) || char.match(/[a-zA-Z]/)) {
        // Operand
        output.push(char);
        console.log(`  Added '${char}' to output: ${output.join(' ')}`);
      } else if (char === '(') {
        stack.push(char);
        console.log(`  Pushed '(' to stack`);
      } else if (char === ')') {
        while (stack.length && stack[stack.length - 1] !== '(') {
          const op = stack.pop();
          output.push(op);
          console.log(`  Popped '${op}' to output: ${output.join(' ')}`);
        }
        stack.pop(); // Remove '('
        console.log(`  Removed '(' from stack`);
      } else if (precedence[char]) {
        while (stack.length && 
               precedence[stack[stack.length - 1]] >= precedence[char]) {
          const op = stack.pop();
          output.push(op);
          console.log(`  Popped '${op}' to output: ${output.join(' ')}`);
        }
        stack.push(char);
        console.log(`  Pushed '${char}' to stack`);
      }
    }
    
    while (stack.length) {
      const op = stack.pop();
      output.push(op);
      console.log(`  Final pop '${op}' to output: ${output.join(' ')}`);
    }
    
    const result = output.join(' ');
    console.log(`  ✅ Postfix: ${result}`);
    return result;
  }

  /**
   * Problem 4: Find next greater element
   * Like finding when taller plates are stacked
   */
  static nextGreaterElement(arr) {
    const stack = [];
    const result = new Array(arr.length).fill(-1);
    
    console.log(`📈 Finding next greater elements for: [${arr.join(', ')}]`);
    
    for (let i = 0; i < arr.length; i++) {
      while (stack.length && arr[i] > arr[stack[stack.length - 1]]) {
        const index = stack.pop();
        result[index] = arr[i];
        console.log(`  Next greater for ${arr[index]} at index ${index} is ${arr[i]}`);
      }
      stack.push(i);
    }
    
    console.log(`  ✅ Result: [${result.join(', ')}]`);
    return result;
  }
}

// Export for use in other modules
export { 
  CafeteriaPlateStack, 
  MultiPlateDispenser, 
  StackPracticeProblems 
};

import { fileURLToPath } from 'url';
import { argv } from 'process';
const __filename = fileURLToPath(import.meta.url);

// Example usage and demonstration
if (argv[1] === __filename) {
  console.log('🍽️  Welcome to the Cafeteria Plate Stack Learning Module!\n');
  
  // Create a plate dispenser
  const plateDispenser = new CafeteriaPlateStack(10);
  
  // Add some plates
  console.log('🍽️  Stocking the plate dispenser:');
  plateDispenser.addPlate('dinner', true);
  plateDispenser.addPlate('dinner', true);
  plateDispenser.addPlate('salad', true);
  plateDispenser.addPlate('dinner', false); // Dirty plate
  plateDispenser.addPlate('dessert', true);
  
  plateDispenser.displayStack();
  
  // Peek at top plate
  console.log('👀 Checking top plate:');
  plateDispenser.peekAtTopPlate();
  
  // Serve some customers
  console.log('\n👥 Serving customers:');
  for (let i = 1; i <= 3; i++) {
    console.log(`Customer ${i}:`);
    const plate = plateDispenser.takePlate();
    if (plate) {
      console.log(`  Received ${plate.type} plate #${plate.id}`);
    }
  }
  
  plateDispenser.displayStack();
  
  // Simulate rush hour
  console.log('🎆 Simulating rush hour:');
  // Add more plates first
  for (let i = 0; i < 5; i++) {
    plateDispenser.addPlate('dinner', true);
  }
  plateDispenser.simulateRushHour(8);
  
  // Demonstrate multi-stack system
  console.log('\n🏢 Multi-Stack System Demo:');
  const multiDispenser = new MultiPlateDispenser(3, 5);
  
  // Stock different stacks
  multiDispenser.addPlateToStack(0, 'dinner', true);
  multiDispenser.addPlateToStack(1, 'salad', true);
  multiDispenser.addPlateToStack(2, 'dessert', true);
  
  multiDispenser.displayAllStacks();
  
  // Show real-world applications
  CafeteriaPlateStack.demonstrateApplications();
  
  // Practice problems
  console.log('\n🧠 Practice Problems:');
  
  console.log('\n1. Balanced Parentheses:');
  StackPracticeProblems.isBalanced('({[]})');
  StackPracticeProblems.isBalanced('({[}])');
  
  console.log('\n2. Postfix Evaluation:');
  StackPracticeProblems.evaluatePostfix('3 4 + 2 * 7 /');
  
  console.log('\n3. Infix to Postfix:');
  StackPracticeProblems.infixToPostfix('A+B*C');
  
  console.log('\n4. Next Greater Element:');
  StackPracticeProblems.nextGreaterElement([4, 5, 2, 25, 7, 8]);
}