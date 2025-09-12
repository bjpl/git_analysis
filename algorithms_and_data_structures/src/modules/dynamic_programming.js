/**
 * Dynamic Programming: Planning a Road Trip with Stops
 * 
 * Just like planning an efficient road trip where you optimize routes
 * and reuse previously calculated distances, dynamic programming solves
 * problems by breaking them down and storing results to avoid recalculation.
 */

class RoadTripPlanner {
  constructor() {
    this.memoCache = new Map(); // For memoization
    this.calculationCount = 0;   // Track number of calculations
  }

  /**
   * Problem 1: Fibonacci Sequence (Road Trip Day Planning)
   * Like calculating how many ways to plan N days of travel
   * Time Complexity: O(n) with memoization vs O(2^n) naive
   */
  fibonacciTravelDays(days, useMemoization = true) {
    console.log(`\n🗺️  Calculating travel combinations for ${days} days:`);
    
    this.calculationCount = 0;
    const startTime = Date.now();
    
    const result = useMemoization ? 
      this.fibonacciMemo(days) : 
      this.fibonacciNaive(days);
    
    const endTime = Date.now();
    const method = useMemoization ? 'Memoized' : 'Naive Recursive';
    
    console.log(`  ${method} result: ${result}`);
    console.log(`  Calculations: ${this.calculationCount}`);
    console.log(`  Time: ${endTime - startTime}ms`);
    
    return result;
  }

  fibonacciNaive(n) {
    this.calculationCount++;
    
    if (n <= 1) return n;
    return this.fibonacciNaive(n - 1) + this.fibonacciNaive(n - 2);
  }

  fibonacciMemo(n, memo = new Map()) {
    this.calculationCount++;
    
    if (memo.has(n)) return memo.get(n);
    
    if (n <= 1) {
      memo.set(n, n);
      return n;
    }
    
    const result = this.fibonacciMemo(n - 1, memo) + this.fibonacciMemo(n - 2, memo);
    memo.set(n, result);
    
    return result;
  }

  /**
   * Problem 2: Shortest Path Between Cities (Floyd-Warshall)
   * Find shortest distance between all pairs of cities
   * Time Complexity: O(V^3)
   */
  findAllShortestPaths(cities, distances) {
    console.log('\n🏢 Finding shortest paths between all city pairs:');
    
    const n = cities.length;
    const dist = Array(n).fill().map(() => Array(n).fill(Infinity));
    
    // Initialize with direct distances
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) {
        if (i === j) {
          dist[i][j] = 0;
        } else if (distances[i] && distances[i][j] !== undefined) {
          dist[i][j] = distances[i][j];
        }
      }
    }
    
    console.log('\n  Initial distance matrix:');
    this.printDistanceMatrix(cities, dist);
    
    // Floyd-Warshall algorithm
    console.log('\n  Applying Floyd-Warshall algorithm...');
    
    for (let k = 0; k < n; k++) {
      console.log(`\n  Considering ${cities[k]} as intermediate city:`);
      
      for (let i = 0; i < n; i++) {
        for (let j = 0; j < n; j++) {
          if (dist[i][k] + dist[k][j] < dist[i][j]) {
            const oldDist = dist[i][j];
            dist[i][j] = dist[i][k] + dist[k][j];
            
            if (oldDist === Infinity) {
              console.log(`    New path found: ${cities[i]} → ${cities[k]} → ${cities[j]} = ${dist[i][j]}`);
            } else {
              console.log(`    Shorter path: ${cities[i]} → ${cities[j]} via ${cities[k]} = ${dist[i][j]} (was ${oldDist})`);
            }
          }
        }
      }
    }
    
    console.log('\n  Final shortest distances:');
    this.printDistanceMatrix(cities, dist);
    
    return dist;
  }

  /**
   * Problem 3: Knapsack Problem (Packing for Road Trip)
   * What items to pack given weight/value constraints
   * Time Complexity: O(n * capacity)
   */
  packRoadTripBag(items, maxWeight) {
    console.log(`\n🎒 Packing road trip bag (max weight: ${maxWeight}kg):`);
    console.log('\n  Available items:');
    
    items.forEach((item, index) => {
      console.log(`    ${index + 1}. ${item.name}: ${item.weight}kg, value ${item.value}`);
    });
    
    const n = items.length;
    const dp = Array(n + 1).fill().map(() => Array(maxWeight + 1).fill(0));
    
    console.log('\n  Building DP table...');
    
    // Build table dp[][] in bottom-up manner
    for (let i = 1; i <= n; i++) {
      const item = items[i - 1];
      
      for (let w = 1; w <= maxWeight; w++) {
        // If current item's weight is more than capacity, skip it
        if (item.weight > w) {
          dp[i][w] = dp[i - 1][w];
        } else {
          // Max value with or without current item
          const withItem = dp[i - 1][w - item.weight] + item.value;
          const withoutItem = dp[i - 1][w];
          dp[i][w] = Math.max(withItem, withoutItem);
          
          if (withItem > withoutItem && w >= item.weight) {
            console.log(`    Adding ${item.name} at weight ${w} increases value to ${dp[i][w]}`);
          }
        }
      }
    }
    
    // Find which items were selected
    const selectedItems = [];
    let w = maxWeight;
    let totalWeight = 0;
    
    for (let i = n; i > 0 && w > 0; i--) {
      if (dp[i][w] !== dp[i - 1][w]) {
        const item = items[i - 1];
        selectedItems.push(item);
        w -= item.weight;
        totalWeight += item.weight;
      }
    }
    
    console.log(`\n  ✅ Optimal packing (total value: ${dp[n][maxWeight]}, weight: ${totalWeight}kg):`);
    selectedItems.forEach(item => {
      console.log(`    - ${item.name}: ${item.weight}kg (value ${item.value})`);
    });
    
    return {
      maxValue: dp[n][maxWeight],
      selectedItems,
      totalWeight
    };
  }

  /**
   * Problem 4: Longest Common Subsequence (Comparing Route Plans)
   * Find common waypoints between two planned routes
   * Time Complexity: O(m * n)
   */
  compareRoutePlans(route1, route2) {
    console.log(`\n🗺️  Comparing route plans:`);
    console.log(`  Route 1: ${route1.join(' → ')}`);
    console.log(`  Route 2: ${route2.join(' → ')}`);
    
    const m = route1.length;
    const n = route2.length;
    const dp = Array(m + 1).fill().map(() => Array(n + 1).fill(0));
    
    // Build LCS table
    for (let i = 1; i <= m; i++) {
      for (let j = 1; j <= n; j++) {
        if (route1[i - 1] === route2[j - 1]) {
          dp[i][j] = dp[i - 1][j - 1] + 1;
        } else {
          dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);
        }
      }
    }
    
    // Reconstruct the LCS
    const commonRoute = [];
    let i = m, j = n;
    
    while (i > 0 && j > 0) {
      if (route1[i - 1] === route2[j - 1]) {
        commonRoute.unshift(route1[i - 1]);
        i--;
        j--;
      } else if (dp[i - 1][j] > dp[i][j - 1]) {
        i--;
      } else {
        j--;
      }
    }
    
    console.log(`\n  ✅ Common waypoints: ${commonRoute.join(' → ')}`);
    console.log(`  Length: ${dp[m][n]} cities`);
    
    return {
      length: dp[m][n],
      commonRoute
    };
  }

  /**
   * Problem 5: Coin Change (Making Change for Tolls)
   * Find minimum coins needed to make change
   * Time Complexity: O(amount * coins.length)
   */
  makeChangeForTolls(tollAmount, coinDenominations) {
    console.log(`\n💰 Making change for $${tollAmount} toll:`);
    console.log(`  Available coins: [${coinDenominations.join(', ')}] cents`);
    
    const amount = Math.round(tollAmount * 100); // Convert to cents
    const dp = Array(amount + 1).fill(Infinity);
    const coinUsed = Array(amount + 1).fill(-1);
    
    dp[0] = 0; // Base case: 0 coins needed for amount 0
    
    console.log('\n  Building solution table...');
    
    for (let i = 1; i <= amount; i++) {
      for (let coin of coinDenominations) {
        if (coin <= i && dp[i - coin] + 1 < dp[i]) {
          dp[i] = dp[i - coin] + 1;
          coinUsed[i] = coin;
          
          if (i <= 50 || i % 25 === 0) { // Show some intermediate steps
            console.log(`    ${i}¢ can be made with ${dp[i]} coins using ${coin}¢`);
          }
        }
      }
    }
    
    if (dp[amount] === Infinity) {
      console.log(`\n  ❌ Cannot make exact change for $${tollAmount}`);
      return null;
    }
    
    // Reconstruct solution
    const coins = [];
    let currentAmount = amount;
    
    while (currentAmount > 0) {
      const coin = coinUsed[currentAmount];
      coins.push(coin);
      currentAmount -= coin;
    }
    
    // Count each denomination
    const coinCount = {};
    coins.forEach(coin => {
      coinCount[coin] = (coinCount[coin] || 0) + 1;
    });
    
    console.log(`\n  ✅ Minimum coins needed: ${dp[amount]}`);
    console.log('  Breakdown:');
    
    Object.entries(coinCount)
      .sort(([a], [b]) => b - a) // Sort by denomination descending
      .forEach(([coin, count]) => {
        console.log(`    ${count}x ${coin}¢ coins`);
      });
    
    return {
      minCoins: dp[amount],
      coinBreakdown: coinCount
    };
  }

  /**
   * Problem 6: Edit Distance (Comparing City Names)
   * Minimum operations to transform one string to another
   * Time Complexity: O(m * n)
   */
  calculateCityNameSimilarity(city1, city2) {
    console.log(`\n🏢 Calculating similarity between "${city1}" and "${city2}":`);
    
    const m = city1.length;
    const n = city2.length;
    const dp = Array(m + 1).fill().map(() => Array(n + 1).fill(0));
    const operations = Array(m + 1).fill().map(() => Array(n + 1).fill(''));
    
    // Initialize base cases
    for (let i = 0; i <= m; i++) {
      dp[i][0] = i; // Delete all characters
      operations[i][0] = 'delete';
    }
    
    for (let j = 0; j <= n; j++) {
      dp[0][j] = j; // Insert all characters
      operations[0][j] = 'insert';
    }
    
    // Fill the DP table
    for (let i = 1; i <= m; i++) {
      for (let j = 1; j <= n; j++) {
        if (city1[i - 1] === city2[j - 1]) {
          dp[i][j] = dp[i - 1][j - 1]; // No operation needed
          operations[i][j] = 'match';
        } else {
          const insert = dp[i][j - 1] + 1;
          const deleteOp = dp[i - 1][j] + 1;
          const substitute = dp[i - 1][j - 1] + 1;
          
          if (substitute <= insert && substitute <= deleteOp) {
            dp[i][j] = substitute;
            operations[i][j] = 'substitute';
          } else if (deleteOp <= insert) {
            dp[i][j] = deleteOp;
            operations[i][j] = 'delete';
          } else {
            dp[i][j] = insert;
            operations[i][j] = 'insert';
          }
        }
      }
    }
    
    // Trace back the operations
    const transformations = [];
    let i = m, j = n;
    
    while (i > 0 || j > 0) {
      const op = operations[i][j];
      
      switch (op) {
        case 'match':
          i--; j--;
          break;
        case 'substitute':
          transformations.unshift(`Substitute '${city1[i-1]}' with '${city2[j-1]}'`);
          i--; j--;
          break;
        case 'delete':
          transformations.unshift(`Delete '${city1[i-1]}'`);
          i--;
          break;
        case 'insert':
          transformations.unshift(`Insert '${city2[j-1]}'`);
          j--;
          break;
      }
    }
    
    const editDistance = dp[m][n];
    const similarity = ((Math.max(m, n) - editDistance) / Math.max(m, n) * 100).toFixed(1);
    
    console.log(`\n  Edit distance: ${editDistance} operations`);
    console.log(`  Similarity: ${similarity}%`);
    
    if (transformations.length > 0 && transformations.length <= 5) {
      console.log('  Transformations needed:');
      transformations.forEach((op, index) => {
        console.log(`    ${index + 1}. ${op}`);
      });
    }
    
    return {
      editDistance,
      similarity: parseFloat(similarity),
      transformations
    };
  }

  /**
   * Problem 7: Maximum Subarray (Best Consecutive Days of Travel)
   * Find the best consecutive days in terms of experience points
   * Time Complexity: O(n) - Kadane's Algorithm
   */
  findBestTravelStreak(dailyExperiences) {
    console.log(`\n🎆 Finding best consecutive travel days:`);
    console.log(`  Daily experiences: [${dailyExperiences.join(', ')}]`);
    
    let maxSum = dailyExperiences[0];
    let currentSum = dailyExperiences[0];
    let start = 0, end = 0, tempStart = 0;
    
    console.log(`\n  Processing day by day:`);
    console.log(`    Day 1: experience ${dailyExperiences[0]}, current streak: ${currentSum}`);
    
    for (let i = 1; i < dailyExperiences.length; i++) {
      if (currentSum < 0) {
        currentSum = dailyExperiences[i];
        tempStart = i;
      } else {
        currentSum += dailyExperiences[i];
      }
      
      if (currentSum > maxSum) {
        maxSum = currentSum;
        start = tempStart;
        end = i;
      }
      
      console.log(`    Day ${i + 1}: experience ${dailyExperiences[i]}, current streak: ${currentSum}, best so far: ${maxSum}`);
    }
    
    console.log(`\n  ✅ Best travel streak: days ${start + 1} to ${end + 1}`);
    console.log(`  Total experience points: ${maxSum}`);
    console.log(`  Days in streak: ${end - start + 1}`);
    
    return {
      maxSum,
      startDay: start + 1,
      endDay: end + 1,
      streakLength: end - start + 1
    };
  }

  /**
   * Helper method to print distance matrix
   */
  printDistanceMatrix(cities, distances) {
    const n = cities.length;
    
    // Print header
    process.stdout.write('      ');
    cities.forEach(city => {
      process.stdout.write(city.substring(0, 6).padStart(6));
    });
    console.log('');
    
    // Print each row
    for (let i = 0; i < n; i++) {
      process.stdout.write(cities[i].substring(0, 6).padEnd(6));
      for (let j = 0; j < n; j++) {
        const dist = distances[i][j] === Infinity ? '∞' : distances[i][j].toString();
        process.stdout.write(dist.padStart(6));
      }
      console.log('');
    }
  }

  /**
   * Real-world applications demonstration
   */
  static demonstrateApplications() {
    console.log(`\n🌟 Real-World Applications of Dynamic Programming:\n\n` +
      `1. 🗺️  GPS Navigation: Shortest path algorithms\n` +
      `2. 💰 Financial Planning: Portfolio optimization\n` +
      `3. 🧬 Bioinformatics: DNA sequence alignment\n` +
      `4. 📦 Supply Chain: Inventory management\n` +
      `5. 🎮 Game AI: Decision tree optimization\n` +
      `6. 📊 Resource Allocation: Task scheduling\n` +
      `7. 🔍 Text Processing: Spell checkers, diff tools\n`);
  }
}

/**
 * Advanced Dynamic Programming Problems
 */
class AdvancedDPProblems {
  /**
   * Problem 1: Traveling Salesman (Visit All Cities Once)
   * Using bit masking and DP
   * Time Complexity: O(n^2 * 2^n)
   */
  static travelingSalesman(cities, distances) {
    console.log(`\n🌍 Traveling Salesman Problem (${cities.length} cities):`);
    
    const n = cities.length;
    const dp = Array(1 << n).fill().map(() => Array(n).fill(Infinity));
    const parent = Array(1 << n).fill().map(() => Array(n).fill(-1));
    
    // Start from city 0
    dp[1][0] = 0; // mask = 1 (only city 0 visited), current city = 0
    
    console.log('  Building DP table with bitmasks...');
    
    for (let mask = 1; mask < (1 << n); mask++) {
      for (let curr = 0; curr < n; curr++) {
        if (!(mask & (1 << curr))) continue; // Current city not in mask
        
        for (let prev = 0; prev < n; prev++) {
          if (prev === curr || !(mask & (1 << prev))) continue;
          
          const prevMask = mask ^ (1 << curr); // Remove current city from mask
          
          if (dp[prevMask][prev] + distances[prev][curr] < dp[mask][curr]) {
            dp[mask][curr] = dp[prevMask][prev] + distances[prev][curr];
            parent[mask][curr] = prev;
          }
        }
      }
    }
    
    // Find minimum cost to return to start
    let minCost = Infinity;
    let lastCity = -1;
    const finalMask = (1 << n) - 1; // All cities visited
    
    for (let i = 1; i < n; i++) {
      if (dp[finalMask][i] + distances[i][0] < minCost) {
        minCost = dp[finalMask][i] + distances[i][0];
        lastCity = i;
      }
    }
    
    // Reconstruct path
    const path = [0]; // Start city
    let mask = finalMask;
    let curr = lastCity;
    
    while (curr !== -1) {
      path.push(curr);
      const prev = parent[mask][curr];
      mask ^= (1 << curr);
      curr = prev;
    }
    
    path.reverse();
    path.push(0); // Return to start
    
    console.log(`\n  ✅ Minimum tour cost: ${minCost}`);
    console.log(`  Optimal path: ${path.map(i => cities[i]).join(' → ')}`);
    
    return { minCost, path: path.map(i => cities[i]) };
  }

  /**
   * Problem 2: Matrix Chain Multiplication (Optimal Route Calculation Order)
   */
  static matrixChainOrder(matrices) {
    console.log(`\n🔢 Matrix Chain Multiplication (${matrices.length} matrices):`);
    
    const n = matrices.length;
    const dp = Array(n).fill().map(() => Array(n).fill(0));
    const split = Array(n).fill().map(() => Array(n).fill(0));
    
    console.log('  Matrix dimensions:', matrices.map(m => `${m.rows}x${m.cols}`).join(', '));
    
    // Length of chain
    for (let length = 2; length <= n; length++) {
      for (let i = 0; i <= n - length; i++) {
        const j = i + length - 1;
        dp[i][j] = Infinity;
        
        for (let k = i; k < j; k++) {
          const cost = dp[i][k] + dp[k + 1][j] + 
                      matrices[i].rows * matrices[k].cols * matrices[j].cols;
          
          if (cost < dp[i][j]) {
            dp[i][j] = cost;
            split[i][j] = k;
          }
        }
      }
    }
    
    console.log(`  Minimum scalar multiplications: ${dp[0][n - 1]}`);
    
    // Print optimal parenthesization
    const printOptimal = (i, j) => {
      if (i === j) {
        return `M${i + 1}`;
      }
      return `(${printOptimal(i, split[i][j])} x ${printOptimal(split[i][j] + 1, j)})`;
    };
    
    console.log(`  Optimal order: ${printOptimal(0, n - 1)}`);
    
    return dp[0][n - 1];
  }

  /**
   * Problem 3: Palindrome Partitioning (Finding Route Patterns)
   */
  static palindromePartitioning(route) {
    console.log(`\n🔄 Palindrome Partitioning for route "${route}":`);
    
    const n = route.length;
    const isPalindrome = Array(n).fill().map(() => Array(n).fill(false));
    const dp = Array(n).fill(Infinity);
    
    // Precompute palindrome table
    for (let i = 0; i < n; i++) {
      isPalindrome[i][i] = true;
    }
    
    for (let length = 2; length <= n; length++) {
      for (let i = 0; i <= n - length; i++) {
        const j = i + length - 1;
        if (length === 2) {
          isPalindrome[i][j] = route[i] === route[j];
        } else {
          isPalindrome[i][j] = route[i] === route[j] && isPalindrome[i + 1][j - 1];
        }
      }
    }
    
    // Find minimum cuts
    for (let i = 0; i < n; i++) {
      if (isPalindrome[0][i]) {
        dp[i] = 0;
      } else {
        for (let j = 0; j < i; j++) {
          if (isPalindrome[j + 1][i]) {
            dp[i] = Math.min(dp[i], dp[j] + 1);
          }
        }
      }
    }
    
    console.log(`  Minimum cuts needed: ${dp[n - 1]}`);
    
    return dp[n - 1];
  }
}

// Export for use in other modules
export { 
  RoadTripPlanner, 
  AdvancedDPProblems 
};

import { fileURLToPath } from 'url';
import { argv } from 'process';
const __filename = fileURLToPath(import.meta.url);

// Example usage and demonstration
if (argv[1] === __filename) {
  console.log('🗺️  Welcome to the Road Trip Dynamic Programming Learning Module!\n');
  
  const planner = new RoadTripPlanner();
  
  // 1. Fibonacci Travel Days
  console.log('🗺️  Problem 1: Travel Day Combinations (Fibonacci):');
  planner.fibonacciTravelDays(10, false); // Naive
  planner.fibonacciTravelDays(10, true);  // Memoized
  
  // 2. Shortest Paths Between Cities
  console.log('\n🏢 Problem 2: Shortest Paths Between Cities (Floyd-Warshall):');
  const cities = ['NYC', 'LA', 'Chicago', 'Houston'];
  const distances = [
    [0, 2800, 790, 1630],
    [2800, 0, 2000, 1550],
    [790, 2000, 0, 1090],
    [1630, 1550, 1090, 0]
  ];
  planner.findAllShortestPaths(cities, distances);
  
  // 3. Knapsack Problem - Packing for Trip
  console.log('\n🎒 Problem 3: Road Trip Packing (Knapsack):');
  const roadTripItems = [
    { name: 'Camera', weight: 2, value: 15 },
    { name: 'Laptop', weight: 3, value: 10 },
    { name: 'Sleeping Bag', weight: 4, value: 12 },
    { name: 'First Aid Kit', weight: 1, value: 8 },
    { name: 'Portable Charger', weight: 1, value: 9 },
    { name: 'Snacks', weight: 2, value: 6 },
    { name: 'Water Bottles', weight: 3, value: 7 },
    { name: 'Maps', weight: 1, value: 4 }
  ];
  planner.packRoadTripBag(roadTripItems, 10);
  
  // 4. Longest Common Subsequence - Route Comparison
  console.log('\n🗺️  Problem 4: Route Plan Comparison (LCS):');
  const route1 = ['NYC', 'Philadelphia', 'Washington', 'Richmond', 'Raleigh', 'Atlanta'];
  const route2 = ['NYC', 'Baltimore', 'Washington', 'Charlotte', 'Atlanta', 'Jacksonville'];
  planner.compareRoutePlans(route1, route2);
  
  // 5. Coin Change - Making Change for Tolls
  console.log('\n💰 Problem 5: Making Change for Tolls:');
  const coinDenominations = [1, 5, 10, 25]; // penny, nickel, dime, quarter
  planner.makeChangeForTolls(0.67, coinDenominations); // 67 cents
  planner.makeChangeForTolls(1.41, coinDenominations); // $1.41
  
  // 6. Edit Distance - City Name Similarity
  console.log('\n🏢 Problem 6: City Name Similarity (Edit Distance):');
  planner.calculateCityNameSimilarity('San Francisco', 'San Antonio');
  planner.calculateCityNameSimilarity('Philadelphia', 'Pittsburgh');
  
  // 7. Maximum Subarray - Best Travel Streak
  console.log('\n🎆 Problem 7: Best Consecutive Travel Days (Kadane\'s Algorithm):');
  const dailyExperiences = [5, -3, 2, 8, -1, 4, -2, 6, -4, 3];
  planner.findBestTravelStreak(dailyExperiences);
  
  // Advanced Problems
  console.log('\n🎆 Advanced Dynamic Programming Problems:');
  
  // Traveling Salesman Problem
  console.log('\n🌍 Advanced Problem 1: Traveling Salesman:');
  const tspCities = ['Start', 'City A', 'City B', 'City C'];
  const tspDistances = [
    [0, 10, 15, 20],
    [10, 0, 35, 25],
    [15, 35, 0, 30],
    [20, 25, 30, 0]
  ];
  AdvancedDPProblems.travelingSalesman(tspCities, tspDistances);
  
  // Matrix Chain Multiplication
  console.log('\n🔢 Advanced Problem 2: Matrix Chain Order:');
  const matrices = [
    { rows: 40, cols: 20 },
    { rows: 20, cols: 30 },
    { rows: 30, cols: 10 },
    { rows: 10, cols: 30 }
  ];
  AdvancedDPProblems.matrixChainOrder(matrices);
  
  // Palindrome Partitioning
  console.log('\n🔄 Advanced Problem 3: Palindrome Partitioning:');
  AdvancedDPProblems.palindromePartitioning('aabcbaa');
  
  // Show real-world applications
  RoadTripPlanner.demonstrateApplications();
  
  console.log('\n✅ Dynamic Programming demonstrations complete!');
  console.log('\n📝 Key takeaways:');
  console.log('  - Dynamic Programming = Recursion + Memoization');
  console.log('  - Break problems into overlapping subproblems');
  console.log('  - Store results to avoid recalculation');
  console.log('  - Bottom-up (tabulation) vs Top-down (memoization)');
  console.log('  - Optimal substructure is required');
}