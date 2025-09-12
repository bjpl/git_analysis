/**
 * Recursion: Russian Nesting Dolls (Matryoshka)
 * 
 * Just like Russian nesting dolls where each doll contains a smaller version
 * of itself, recursion is when a function calls itself with a smaller problem.
 */

class MatryoshkaDoll {
  constructor(name, size, color, contents = null) {
    this.name = name;
    this.size = size;           // Size from 1 (smallest) to n (largest)
    this.color = color;
    this.contents = contents;   // Smaller doll inside (recursive structure)
    this.decorations = [];
  }

  /**
   * Add decoration to this doll
   */
  addDecoration(decoration) {
    this.decorations.push(decoration);
  }

  /**
   * Check if this doll can contain another doll
   */
  canContain(otherDoll) {
    return this.size > otherDoll.size;
  }

  /**
   * Place a smaller doll inside this one
   */
  placeDollInside(smallerDoll) {
    if (!this.canContain(smallerDoll)) {
      console.log(`❌ ${this.name} (size ${this.size}) cannot contain ${smallerDoll.name} (size ${smallerDoll.size})`);
      return false;
    }
    
    this.contents = smallerDoll;
    console.log(`🪆 Placed ${smallerDoll.name} inside ${this.name}`);
    return true;
  }

  toString() {
    const decorationsStr = this.decorations.length > 0 ? 
      ` [${this.decorations.join(', ')}]` : '';
    return `${this.name} (${this.color}, size ${this.size})${decorationsStr}`;
  }
}

class RecursionLearning {
  constructor() {
    this.recursionDepth = 0;
    this.maxDepth = 0;
    this.callCount = 0;
  }

  /**
   * Problem 1: Building Nested Dolls (Basic Recursion)
   * Demonstrate the concept of recursion with visual nesting
   */
  buildNestedDolls(dolls, currentIndex = 0) {
    console.log(`\n🪆 Building nested dolls - Step ${currentIndex + 1}:`);
    
    this.recursionDepth++;
    this.maxDepth = Math.max(this.maxDepth, this.recursionDepth);
    this.callCount++;
    
    const indent = '  '.repeat(this.recursionDepth - 1);
    
    // Base case: no more dolls to nest
    if (currentIndex >= dolls.length) {
      console.log(`${indent}✅ Base case reached - no more dolls to nest`);
      this.recursionDepth--;
      return null;
    }
    
    const currentDoll = dolls[currentIndex];
    console.log(`${indent}🪆 Processing ${currentDoll.toString()}`);
    
    // Recursive case: nest the remaining dolls
    const innerDoll = this.buildNestedDolls(dolls, currentIndex + 1);
    
    if (innerDoll) {
      currentDoll.placeDollInside(innerDoll);
    }
    
    console.log(`${indent}⬅️  Returning ${currentDoll.name} to previous level`);
    this.recursionDepth--;
    
    return currentDoll;
  }

  /**
   * Problem 2: Factorial (N! Dolls)
   * Calculate factorial using recursion
   * Time Complexity: O(n), Space Complexity: O(n) for call stack
   */
  factorialDolls(n, showSteps = true) {
    if (showSteps) {
      console.log(`\n🔢 Calculating ${n}! (${n} factorial dolls):`);
      this.callCount = 0;
    }
    
    this.callCount++;
    const indent = '  '.repeat(this.callCount - 1);
    
    if (showSteps) {
      console.log(`${indent}factorial(${n}) called`);
    }
    
    // Base case
    if (n <= 1) {
      if (showSteps) {
        console.log(`${indent}✅ Base case: factorial(${n}) = 1`);
      }
      this.callCount--;
      return 1;
    }
    
    // Recursive case
    if (showSteps) {
      console.log(`${indent}Computing ${n} * factorial(${n - 1})...`);
    }
    
    const result = n * this.factorialDolls(n - 1, showSteps);
    
    if (showSteps) {
      console.log(`${indent}⬅️  factorial(${n}) = ${result}`);
    }
    
    this.callCount--;
    return result;
  }

  /**
   * Problem 3: Tower of Hanoi (Moving Nested Dolls)
   * Classic recursive problem - move all dolls to destination
   * Time Complexity: O(2^n)
   */
  towerOfHanoi(n, source = 'A', destination = 'C', auxiliary = 'B', showSteps = true) {
    if (showSteps && n === arguments[0]) {
      console.log(`\n🗼 Tower of Hanoi: Moving ${n} nested dolls from ${source} to ${destination}`);
      this.callCount = 0;
    }
    
    this.callCount++;
    
    // Base case: only one doll to move
    if (n === 1) {
      if (showSteps) {
        console.log(`  Move smallest doll from ${source} to ${destination}`);
      }
      this.callCount--;
      return 1; // Number of moves
    }
    
    // Recursive case: move n dolls
    let totalMoves = 0;
    
    if (showSteps) {
      console.log(`\n  Step 1: Move top ${n - 1} dolls from ${source} to ${auxiliary}`);
    }
    totalMoves += this.towerOfHanoi(n - 1, source, auxiliary, destination, showSteps);
    
    if (showSteps) {
      console.log(`\n  Step 2: Move largest doll from ${source} to ${destination}`);
    }
    totalMoves += 1;
    
    if (showSteps) {
      console.log(`\n  Step 3: Move ${n - 1} dolls from ${auxiliary} to ${destination}`);
    }
    totalMoves += this.towerOfHanoi(n - 1, auxiliary, destination, source, showSteps);
    
    if (showSteps && n === arguments[0]) {
      console.log(`\n✅ Total moves required: ${totalMoves}`);
      console.log(`Formula: 2^${n} - 1 = ${Math.pow(2, n) - 1} moves`);
    }
    
    this.callCount--;
    return totalMoves;
  }

  /**
   * Problem 4: Binary Tree Traversal (Exploring Doll Collections)
   * Traverse a tree structure recursively
   */
  createDollCollection() {
    // Create a binary tree of dolls
    const rootDoll = new MatryoshkaDoll('Babushka', 10, 'red');
    rootDoll.addDecoration('golden stars');
    
    const leftChild = new MatryoshkaDoll('Dedushka', 8, 'blue');
    leftChild.addDecoration('silver moons');
    
    const rightChild = new MatryoshkaDoll('Mama', 7, 'green');
    rightChild.addDecoration('wooden flowers');
    
    const leftLeftChild = new MatryoshkaDoll('Uncle Ivan', 6, 'yellow');
    const leftRightChild = new MatryoshkaDoll('Aunt Olga', 5, 'purple');
    
    const rightLeftChild = new MatryoshkaDoll('Son Dmitri', 4, 'orange');
    const rightRightChild = new MatryoshkaDoll('Daughter Katya', 3, 'pink');
    
    // Build tree structure (not actual nesting, just tree relationships)
    rootDoll.left = leftChild;
    rootDoll.right = rightChild;
    
    leftChild.left = leftLeftChild;
    leftChild.right = leftRightChild;
    
    rightChild.left = rightLeftChild;
    rightChild.right = rightRightChild;
    
    return rootDoll;
  }

  /**
   * Pre-order traversal (Root -> Left -> Right)
   */
  preOrderTraversal(dollNode, visited = [], depth = 0) {
    if (!dollNode) return visited;
    
    const indent = '  '.repeat(depth);
    console.log(`${indent}🪆 Visit: ${dollNode.toString()}`);
    visited.push(dollNode.name);
    
    // Recursively visit left subtree
    this.preOrderTraversal(dollNode.left, visited, depth + 1);
    
    // Recursively visit right subtree
    this.preOrderTraversal(dollNode.right, visited, depth + 1);
    
    return visited;
  }

  /**
   * In-order traversal (Left -> Root -> Right)
   */
  inOrderTraversal(dollNode, visited = [], depth = 0) {
    if (!dollNode) return visited;
    
    // Recursively visit left subtree
    this.inOrderTraversal(dollNode.left, visited, depth + 1);
    
    const indent = '  '.repeat(depth);
    console.log(`${indent}🪆 Visit: ${dollNode.toString()}`);
    visited.push(dollNode.name);
    
    // Recursively visit right subtree
    this.inOrderTraversal(dollNode.right, visited, depth + 1);
    
    return visited;
  }

  /**
   * Post-order traversal (Left -> Right -> Root)
   */
  postOrderTraversal(dollNode, visited = [], depth = 0) {
    if (!dollNode) return visited;
    
    // Recursively visit left subtree
    this.postOrderTraversal(dollNode.left, visited, depth + 1);
    
    // Recursively visit right subtree
    this.postOrderTraversal(dollNode.right, visited, depth + 1);
    
    const indent = '  '.repeat(depth);
    console.log(`${indent}🪆 Visit: ${dollNode.toString()}`);
    visited.push(dollNode.name);
    
    return visited;
  }

  /**
   * Problem 5: Fibonacci with Recursion (Doll Family Growth)
   * Classic example showing exponential time complexity
   */
  fibonacciDollFamily(generation, showCalls = false) {
    if (showCalls && generation === arguments[0]) {
      console.log(`\n👪 Fibonacci Doll Family - Generation ${generation}:`);
      this.callCount = 0;
    }
    
    this.callCount++;
    
    if (showCalls) {
      const indent = '  '.repeat(this.callCount - 1);
      console.log(`${indent}Computing generation ${generation}...`);
    }
    
    // Base cases
    if (generation <= 1) {
      if (showCalls) {
        const indent = '  '.repeat(this.callCount - 1);
        console.log(`${indent}✅ Base case: generation ${generation} = ${generation}`);
      }
      this.callCount--;
      return generation;
    }
    
    // Recursive case
    const result = this.fibonacciDollFamily(generation - 1, showCalls) + 
                  this.fibonacciDollFamily(generation - 2, showCalls);
    
    if (showCalls) {
      const indent = '  '.repeat(this.callCount - 1);
      console.log(`${indent}⬅️  Generation ${generation} = ${result}`);
    }
    
    this.callCount--;
    return result;
  }

  /**
   * Problem 6: Generate All Permutations (Arranging Dolls)
   * Find all possible arrangements of dolls
   */
  generatePermutations(dolls, currentPermutation = [], allPermutations = []) {
    if (currentPermutation.length === 0) {
      console.log(`\n🔀 Generating all arrangements of ${dolls.length} dolls:`);
      console.log(`Expected permutations: ${this.factorialDolls(dolls.length, false)}`);
    }
    
    // Base case: we have a complete permutation
    if (currentPermutation.length === dolls.length) {
      const arrangement = [...currentPermutation];
      allPermutations.push(arrangement);
      
      console.log(`  Arrangement ${allPermutations.length}: [${arrangement.join(', ')}]`);
      return allPermutations;
    }
    
    // Recursive case: try adding each unused doll
    for (let i = 0; i < dolls.length; i++) {
      const doll = dolls[i];
      
      // Skip if doll is already used
      if (currentPermutation.includes(doll)) {
        continue;
      }
      
      // Add doll to current permutation
      currentPermutation.push(doll);
      
      // Recursively generate remaining permutations
      this.generatePermutations(dolls, currentPermutation, allPermutations);
      
      // Backtrack: remove the doll for next iteration
      currentPermutation.pop();
    }
    
    return allPermutations;
  }

  /**
   * Problem 7: Subset Generation (Selecting Dolls for Display)
   * Generate all possible subsets of dolls
   */
  generateSubsets(dolls, currentIndex = 0, currentSubset = [], allSubsets = []) {
    if (currentIndex === 0) {
      console.log(`\n🎨 Generating all subsets of ${dolls.length} dolls:`);
      console.log(`Expected subsets: ${Math.pow(2, dolls.length)}`);
    }
    
    // Base case: processed all dolls
    if (currentIndex === dolls.length) {
      const subset = [...currentSubset];
      allSubsets.push(subset);
      
      const subsetStr = subset.length === 0 ? '(empty set)' : `[${subset.join(', ')}]`;
      console.log(`  Subset ${allSubsets.length}: ${subsetStr}`);
      return allSubsets;
    }
    
    const currentDoll = dolls[currentIndex];
    
    // Recursive case 1: Don't include current doll
    this.generateSubsets(dolls, currentIndex + 1, currentSubset, allSubsets);
    
    // Recursive case 2: Include current doll
    currentSubset.push(currentDoll);
    this.generateSubsets(dolls, currentIndex + 1, currentSubset, allSubsets);
    
    // Backtrack: remove current doll
    currentSubset.pop();
    
    return allSubsets;
  }

  /**
   * Problem 8: Palindrome Check (Symmetric Doll Names)
   * Check if a string is a palindrome recursively
   */
  isPalindromeRecursive(str, left = 0, right = null) {
    if (right === null) {
      right = str.length - 1;
      console.log(`\n🔄 Checking if "${str}" is a palindrome:`);
    }
    
    const indent = '  '.repeat((str.length - (right - left + 1)) / 2);
    console.log(`${indent}Comparing '${str[left]}' and '${str[right]}' at positions ${left} and ${right}`);
    
    // Base case: pointers meet or cross
    if (left >= right) {
      console.log(`${indent}✅ Base case reached - palindrome confirmed`);
      return true;
    }
    
    // If characters don't match
    if (str[left].toLowerCase() !== str[right].toLowerCase()) {
      console.log(`${indent}❌ Characters don't match - not a palindrome`);
      return false;
    }
    
    // Recursive case: check inner substring
    console.log(`${indent}Characters match - checking inner substring...`);
    return this.isPalindromeRecursive(str, left + 1, right - 1);
  }

  /**
   * Problem 9: Quick Sort (Organizing Dolls by Size)
   * Recursive divide-and-conquer sorting
   */
  quickSortDolls(dolls, low = 0, high = null, level = 0) {
    if (high === null) {
      high = dolls.length - 1;
      console.log(`\n🔄 Quick Sort: Organizing ${dolls.length} dolls by size`);
      console.log(`Initial order: [${dolls.map(d => d.size).join(', ')}]`);
    }
    
    const indent = '  '.repeat(level);
    
    // Base case: array has 1 or 0 elements
    if (low >= high) {
      console.log(`${indent}✅ Base case: subarray [${low}:${high}] is sorted`);
      return;
    }
    
    console.log(`${indent}Sorting subarray [${low}:${high}] = [${dolls.slice(low, high + 1).map(d => d.size).join(', ')}]`);
    
    // Partition the array
    const pivotIndex = this.partitionDolls(dolls, low, high, level);
    
    console.log(`${indent}Pivot placed at index ${pivotIndex} (size ${dolls[pivotIndex].size})`);
    console.log(`${indent}Array after partitioning: [${dolls.map(d => d.size).join(', ')}]`);
    
    // Recursively sort left and right subarrays
    console.log(`${indent}Recursively sorting left subarray [${low}:${pivotIndex - 1}]`);
    this.quickSortDolls(dolls, low, pivotIndex - 1, level + 1);
    
    console.log(`${indent}Recursively sorting right subarray [${pivotIndex + 1}:${high}]`);
    this.quickSortDolls(dolls, pivotIndex + 1, high, level + 1);
    
    console.log(`${indent}✅ Subarray [${low}:${high}] is now sorted`);
  }

  partitionDolls(dolls, low, high, level) {
    const pivot = dolls[high].size;
    let i = low - 1;
    
    const indent = '  '.repeat(level + 1);
    console.log(`${indent}Using pivot: ${pivot} (rightmost element)`);
    
    for (let j = low; j < high; j++) {
      if (dolls[j].size <= pivot) {
        i++;
        if (i !== j) {
          [dolls[i], dolls[j]] = [dolls[j], dolls[i]];
          console.log(`${indent}Swapped ${dolls[j].size} and ${dolls[i].size}`);
        }
      }
    }
    
    [dolls[i + 1], dolls[high]] = [dolls[high], dolls[i + 1]];
    console.log(`${indent}Placed pivot ${pivot} at final position ${i + 1}`);
    
    return i + 1;
  }

  /**
   * Problem 10: N-Queens (Placing Non-Attacking Dolls)
   * Classic backtracking problem
   */
  solveNQueens(n, board = null, row = 0, solutions = []) {
    if (board === null) {
      board = Array(n).fill().map(() => Array(n).fill('.'));
      console.log(`\n👑 N-Queens Problem: Placing ${n} non-attacking dolls on ${n}x${n} board`);
    }
    
    // Base case: all queens placed
    if (row === n) {
      const solution = board.map(row => row.slice());
      solutions.push(solution);
      
      console.log(`\n✅ Solution ${solutions.length}:`);
      this.printBoard(board);
      return solutions;
    }
    
    const indent = '  '.repeat(row);
    console.log(`${indent}Placing doll in row ${row}...`);
    
    // Try placing queen in each column of current row
    for (let col = 0; col < n; col++) {
      console.log(`${indent}  Trying column ${col}...`);
      
      if (this.isSafe(board, row, col, n)) {
        console.log(`${indent}  ✅ Safe position found at (${row}, ${col})`);
        
        // Place queen
        board[row][col] = 'Q';
        
        // Recursively place remaining queens
        this.solveNQueens(n, board, row + 1, solutions);
        
        // Backtrack
        board[row][col] = '.';
        console.log(`${indent}  ⬅️  Backtracking from (${row}, ${col})`);
      } else {
        console.log(`${indent}  ❌ Position (${row}, ${col}) is under attack`);
      }
    }
    
    return solutions;
  }

  isSafe(board, row, col, n) {
    // Check column
    for (let i = 0; i < row; i++) {
      if (board[i][col] === 'Q') {
        return false;
      }
    }
    
    // Check upper-left diagonal
    for (let i = row - 1, j = col - 1; i >= 0 && j >= 0; i--, j--) {
      if (board[i][j] === 'Q') {
        return false;
      }
    }
    
    // Check upper-right diagonal
    for (let i = row - 1, j = col + 1; i >= 0 && j < n; i--, j++) {
      if (board[i][j] === 'Q') {
        return false;
      }
    }
    
    return true;
  }

  printBoard(board) {
    board.forEach(row => {
      console.log('    ' + row.join(' '));
    });
  }

  /**
   * Display nested doll structure
   */
  displayNestedDolls(doll, depth = 0) {
    if (!doll) {
      console.log('No dolls to display');
      return;
    }
    
    const indent = '  '.repeat(depth);
    const arrow = depth > 0 ? '→ ' : '';
    console.log(`${indent}${arrow}${doll.toString()}`);
    
    if (doll.contents) {
      this.displayNestedDolls(doll.contents, depth + 1);
    }
  }

  /**
   * Reset counters for clean demonstrations
   */
  resetCounters() {
    this.recursionDepth = 0;
    this.maxDepth = 0;
    this.callCount = 0;
  }

  /**
   * Real-world applications demonstration
   */
  static demonstrateApplications() {
    console.log(`\n🌟 Real-World Applications of Recursion:\n\n` +
      `1. 📁 File System Navigation: Directory traversal\n` +
      `2. 🌐 Web Crawling: Following links recursively\n` +
      `3. 🧬 JSON/XML Parsing: Nested data structures\n` +
      `4. 🎮 Game AI: Minimax algorithm for games\n` +
      `5. 📊 Fractal Generation: Self-similar patterns\n` +
      `6. 🔍 Compiler Design: Parsing expressions\n` +
      `7. 🗺️  Graph Traversal: DFS and pathfinding\n`);
  }
}

/**
 * Advanced Recursion Problems
 */
class AdvancedRecursionProblems {
  /**
   * Problem 1: Generate Parentheses
   * Generate all valid parentheses combinations
   */
  static generateParentheses(n, current = '', open = 0, close = 0, results = []) {
    if (current.length === 0) {
      console.log(`\n🔗 Generating all valid parentheses combinations for ${n} pairs:`);
    }
    
    // Base case: we have a complete valid combination
    if (current.length === n * 2) {
      results.push(current);
      console.log(`  Valid combination: ${current}`);
      return results;
    }
    
    // Add opening parenthesis if we haven't used all n
    if (open < n) {
      this.generateParentheses(n, current + '(', open + 1, close, results);
    }
    
    // Add closing parenthesis if it won't make the string invalid
    if (close < open) {
      this.generateParentheses(n, current + ')', open, close + 1, results);
    }
    
    return results;
  }

  /**
   * Problem 2: Sudoku Solver
   * Solve Sudoku puzzle using backtracking
   */
  static solveSudoku(board) {
    console.log('\n🔢 Solving Sudoku puzzle using backtracking recursion:');
    console.log('Initial board:');
    this.printSudokuBoard(board);
    
    const solve = () => {
      for (let row = 0; row < 9; row++) {
        for (let col = 0; col < 9; col++) {
          if (board[row][col] === 0) {
            for (let num = 1; num <= 9; num++) {
              if (this.isValidSudoku(board, row, col, num)) {
                board[row][col] = num;
                
                if (solve()) {
                  return true;
                }
                
                // Backtrack
                board[row][col] = 0;
              }
            }
            return false;
          }
        }
      }
      return true;
    };
    
    if (solve()) {
      console.log('\n✅ Sudoku solved:');
      this.printSudokuBoard(board);
      return true;
    } else {
      console.log('\n❌ No solution exists');
      return false;
    }
  }

  static isValidSudoku(board, row, col, num) {
    // Check row
    for (let j = 0; j < 9; j++) {
      if (board[row][j] === num) return false;
    }
    
    // Check column
    for (let i = 0; i < 9; i++) {
      if (board[i][col] === num) return false;
    }
    
    // Check 3x3 box
    const boxRow = Math.floor(row / 3) * 3;
    const boxCol = Math.floor(col / 3) * 3;
    
    for (let i = boxRow; i < boxRow + 3; i++) {
      for (let j = boxCol; j < boxCol + 3; j++) {
        if (board[i][j] === num) return false;
      }
    }
    
    return true;
  }

  static printSudokuBoard(board) {
    for (let i = 0; i < 9; i++) {
      if (i % 3 === 0 && i !== 0) {
        console.log('  ------+-------+------');
      }
      let row = '  ';
      for (let j = 0; j < 9; j++) {
        if (j % 3 === 0 && j !== 0) {
          row += '| ';
        }
        row += (board[i][j] === 0 ? '.' : board[i][j]) + ' ';
      }
      console.log(row);
    }
  }

  /**
   * Problem 3: Word Break
   * Check if string can be segmented into dictionary words
   */
  static wordBreak(str, dictionary, memo = new Map()) {
    console.log(`\n📚 Word Break: Can "${str}" be segmented using dictionary?`);
    console.log(`Dictionary: [${dictionary.join(', ')}]`);
    
    const canBreak = (s, start = 0) => {
      if (start === s.length) {
        return true;
      }
      
      const key = start;
      if (memo.has(key)) {
        return memo.get(key);
      }
      
      for (let end = start + 1; end <= s.length; end++) {
        const word = s.substring(start, end);
        
        if (dictionary.includes(word)) {
          console.log(`  Found word: "${word}" at position ${start}-${end}`);
          
          if (canBreak(s, end)) {
            memo.set(key, true);
            return true;
          }
        }
      }
      
      memo.set(key, false);
      return false;
    };
    
    const result = canBreak(str);
    console.log(`  Result: ${result ? '✅ Can be segmented' : '❌ Cannot be segmented'}`);
    
    return result;
  }
}

// Export for use in other modules
export { 
  MatryoshkaDoll, 
  RecursionLearning, 
  AdvancedRecursionProblems 
};

import { fileURLToPath } from 'url';
import { argv } from 'process';
const __filename = fileURLToPath(import.meta.url);

// Example usage and demonstration
if (argv[1] === __filename) {
  console.log('🪆 Welcome to the Russian Nesting Dolls Recursion Learning Module!\n');
  
  const recursionLearner = new RecursionLearning();
  
  // Create some dolls for demonstrations
  const dolls = [
    new MatryoshkaDoll('Large Doll', 5, 'red'),
    new MatryoshkaDoll('Medium Doll', 3, 'blue'),
    new MatryoshkaDoll('Small Doll', 1, 'green')
  ];
  
  // Problem 1: Building Nested Dolls
  console.log('🪆 Problem 1: Building Nested Dolls (Basic Recursion):');
  recursionLearner.resetCounters();
  const nestedDoll = recursionLearner.buildNestedDolls(dolls);
  
  console.log(`\n✅ Nesting complete! Max recursion depth: ${recursionLearner.maxDepth}`);
  console.log('Final nested structure:');
  recursionLearner.displayNestedDolls(nestedDoll);
  
  // Problem 2: Factorial
  console.log('\n🔢 Problem 2: Factorial Calculation:');
  recursionLearner.resetCounters();
  const factorial5 = recursionLearner.factorialDolls(5);
  console.log(`\n✅ 5! = ${factorial5}`);
  
  // Problem 3: Tower of Hanoi
  console.log('\n🗼 Problem 3: Tower of Hanoi:');
  recursionLearner.resetCounters();
  recursionLearner.towerOfHanoi(3);
  
  // Problem 4: Tree Traversal
  console.log('\n🌳 Problem 4: Binary Tree Traversal:');
  const dollCollection = recursionLearner.createDollCollection();
  
  console.log('\nPre-order traversal (Root → Left → Right):');
  const preOrder = recursionLearner.preOrderTraversal(dollCollection);
  console.log(`Visited order: [${preOrder.join(', ')}]`);
  
  console.log('\nIn-order traversal (Left → Root → Right):');
  const inOrder = recursionLearner.inOrderTraversal(dollCollection);
  console.log(`Visited order: [${inOrder.join(', ')}]`);
  
  console.log('\nPost-order traversal (Left → Right → Root):');
  const postOrder = recursionLearner.postOrderTraversal(dollCollection);
  console.log(`Visited order: [${postOrder.join(', ')}]`);
  
  // Problem 5: Fibonacci (show exponential growth)
  console.log('\n👪 Problem 5: Fibonacci Sequence:');
  recursionLearner.resetCounters();
  console.log('Computing Fibonacci(6) with naive recursion:');
  const fib6 = recursionLearner.fibonacciDollFamily(6, true);
  console.log(`\n✅ Fibonacci(6) = ${fib6}, Total function calls: ${recursionLearner.callCount}`);
  
  // Problem 6: Permutations
  console.log('\n🔀 Problem 6: Generating Permutations:');
  const smallDolls = ['A', 'B', 'C'];
  recursionLearner.generatePermutations(smallDolls);
  
  // Problem 7: Subsets
  console.log('\n🎨 Problem 7: Generating Subsets:');
  const tinyDolls = ['X', 'Y'];
  recursionLearner.generateSubsets(tinyDolls);
  
  // Problem 8: Palindrome Check
  console.log('\n🔄 Problem 8: Palindrome Check:');
  recursionLearner.isPalindromeRecursive('racecar');
  recursionLearner.isPalindromeRecursive('hello');
  
  // Problem 9: Quick Sort
  console.log('\n🔄 Problem 9: Quick Sort:');
  const unsortedDolls = [
    new MatryoshkaDoll('Doll A', 8, 'red'),
    new MatryoshkaDoll('Doll B', 3, 'blue'),
    new MatryoshkaDoll('Doll C', 6, 'green'),
    new MatryoshkaDoll('Doll D', 1, 'yellow'),
    new MatryoshkaDoll('Doll E', 4, 'purple')
  ];
  recursionLearner.quickSortDolls([...unsortedDolls]);
  
  // Problem 10: N-Queens (smaller example)
  console.log('\n👑 Problem 10: N-Queens (4x4 board):');
  recursionLearner.solveNQueens(4);
  
  // Advanced Problems
  console.log('\n🎆 Advanced Recursion Problems:');
  
  // Generate Parentheses
  AdvancedRecursionProblems.generateParentheses(3);
  
  // Word Break
  const dictionary = ['cat', 'cats', 'dog', 'sand', 'and', 'cat'];
  AdvancedRecursionProblems.wordBreak('catsanddog', dictionary);
  
  // Simple Sudoku example (partially filled)
  const sudokuBoard = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9]
  ];
  
  console.log('\n🔢 Sudoku Solver (showing first few steps only):');
  // Note: Full sudoku solving would be too verbose for demo
  
  // Show real-world applications
  RecursionLearning.demonstrateApplications();
  
  console.log('\n✅ Recursion demonstrations complete!');
  console.log('\n📝 Key takeaways about recursion:');
  console.log('  - Every recursive function needs a base case');
  console.log('  - Recursive case should move toward the base case');
  console.log('  - Each recursive call creates a new stack frame');
  console.log('  - Recursion can be elegant but may have performance costs');
  console.log('  - Some problems naturally fit recursive solutions (trees, fractals)');
  console.log('  - Consider iterative alternatives for better space complexity');
}