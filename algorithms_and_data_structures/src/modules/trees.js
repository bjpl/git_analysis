/**
 * Trees: Company Organization Charts
 * 
 * Just like a company organization chart where each employee can have
 * subordinates, trees have nodes with parent-child relationships.
 */

class Employee {
  constructor(name, position, department, salary = 0) {
    this.name = name;                    // Employee name
    this.position = position;            // Job title
    this.department = department;        // Department
    this.salary = salary;               // Salary for calculations
    this.subordinates = [];             // Array of direct reports
    this.manager = null;                // Reference to manager (parent)
    this.employeeId = Math.random().toString(36).substr(2, 9);
  }

  /**
   * Add a subordinate (child node)
   * Time Complexity: O(1)
   */
  addSubordinate(employee) {
    employee.manager = this;
    this.subordinates.push(employee);
    console.log(`👥 ${employee.name} (${employee.position}) now reports to ${this.name}`);
  }

  /**
   * Remove a subordinate
   * Time Complexity: O(n) where n is number of subordinates
   */
  removeSubordinate(employeeName) {
    const index = this.subordinates.findIndex(emp => emp.name === employeeName);
    if (index !== -1) {
      const removed = this.subordinates.splice(index, 1)[0];
      removed.manager = null;
      console.log(`🚨 ${employeeName} no longer reports to ${this.name}`);
      return removed;
    }
    console.log(`${employeeName} is not a direct subordinate of ${this.name}`);
    return null;
  }

  /**
   * Check if this employee has subordinates
   */
  hasSubordinates() {
    return this.subordinates.length > 0;
  }

  /**
   * Get total number of people in this person's organization
   * Time Complexity: O(n) where n is total nodes in subtree
   */
  getTotalTeamSize() {
    let count = 1; // Count self
    for (const subordinate of this.subordinates) {
      count += subordinate.getTotalTeamSize();
    }
    return count;
  }

  /**
   * Calculate total salary budget for this manager's organization
   */
  getTotalSalaryBudget() {
    let total = this.salary;
    for (const subordinate of this.subordinates) {
      total += subordinate.getTotalSalaryBudget();
    }
    return total;
  }

  toString() {
    return `${this.name} (${this.position}) - ${this.department}`;
  }
}

class CompanyOrganizationChart {
  constructor(ceoName, companyName = 'Tech Corp') {
    this.ceo = new Employee(ceoName, 'CEO', 'Executive', 500000);
    this.companyName = companyName;
    this.totalEmployees = 1;
  }

  /**
   * Find an employee by name (Depth-First Search)
   * Time Complexity: O(n)
   */
  findEmployee(name, currentNode = this.ceo) {
    if (currentNode.name === name) {
      return currentNode;
    }
    
    for (const subordinate of currentNode.subordinates) {
      const found = this.findEmployee(name, subordinate);
      if (found) {
        return found;
      }
    }
    
    return null;
  }

  /**
   * Add employee under a specific manager
   */
  addEmployee(managerName, newEmployeeName, position, department, salary) {
    const manager = this.findEmployee(managerName);
    if (!manager) {
      console.log(`❌ Manager ${managerName} not found`);
      return false;
    }
    
    const newEmployee = new Employee(newEmployeeName, position, department, salary);
    manager.addSubordinate(newEmployee);
    this.totalEmployees++;
    
    console.log(`✅ Added ${newEmployeeName} to ${this.companyName}`);
    return true;
  }

  /**
   * Display organization chart (Tree Traversal)
   * Using pre-order traversal (root, then children)
   */
  displayOrganizationChart(employee = this.ceo, level = 0, isLast = true, prefix = '') {
    if (level === 0) {
      console.log(`\n🏢 ${this.companyName} Organization Chart:`);
      console.log(`Total Employees: ${this.totalEmployees}`);
      console.log('\n' + employee.toString() + ' 👑');
    } else {
      const connector = isLast ? '└── ' : '├── ';
      console.log(prefix + connector + employee.toString());
    }
    
    const newPrefix = level === 0 ? '' : prefix + (isLast ? '    ' : '│   ');
    
    for (let i = 0; i < employee.subordinates.length; i++) {
      const isLastChild = i === employee.subordinates.length - 1;
      this.displayOrganizationChart(
        employee.subordinates[i], 
        level + 1, 
        isLastChild, 
        newPrefix
      );
    }
  }

  /**
   * Find all employees at a specific level (Breadth-First Search)
   * Time Complexity: O(n)
   */
  getEmployeesAtLevel(targetLevel) {
    const employees = [];
    const queue = [{ employee: this.ceo, level: 0 }];
    
    console.log(`🔍 Finding employees at level ${targetLevel}:`);
    
    while (queue.length > 0) {
      const { employee, level } = queue.shift();
      
      if (level === targetLevel) {
        employees.push(employee);
        console.log(`  - ${employee.toString()}`);
      }
      
      // Add children to queue
      for (const subordinate of employee.subordinates) {
        queue.push({ employee: subordinate, level: level + 1 });
      }
    }
    
    console.log(`Found ${employees.length} employees at level ${targetLevel}`);
    return employees;
  }

  /**
   * Get reporting chain from employee to CEO
   * Time Complexity: O(h) where h is height/depth
   */
  getReportingChain(employeeName) {
    const employee = this.findEmployee(employeeName);
    if (!employee) {
      console.log(`${employeeName} not found`);
      return [];
    }
    
    const chain = [];
    let current = employee;
    
    while (current) {
      chain.push(current);
      current = current.manager;
    }
    
    console.log(`\n📈 Reporting chain for ${employeeName}:`);
    for (let i = 0; i < chain.length; i++) {
      const arrow = i < chain.length - 1 ? ' → ' : '';
      process.stdout.write(chain[i].name + ' (' + chain[i].position + ')' + arrow);
    }
    console.log('\n');
    
    return chain;
  }

  /**
   * Calculate organization depth (tree height)
   * Time Complexity: O(n)
   */
  getOrganizationDepth(employee = this.ceo) {
    if (employee.subordinates.length === 0) {
      return 1;
    }
    
    let maxDepth = 0;
    for (const subordinate of employee.subordinates) {
      const depth = this.getOrganizationDepth(subordinate);
      maxDepth = Math.max(maxDepth, depth);
    }
    
    return maxDepth + 1;
  }

  /**
   * Find all managers (internal nodes)
   */
  getAllManagers(employee = this.ceo, managers = []) {
    if (employee.hasSubordinates()) {
      managers.push(employee);
    }
    
    for (const subordinate of employee.subordinates) {
      this.getAllManagers(subordinate, managers);
    }
    
    return managers;
  }

  /**
   * Find all individual contributors (leaf nodes)
   */
  getAllIndividualContributors(employee = this.ceo, ics = []) {
    if (!employee.hasSubordinates()) {
      ics.push(employee);
    }
    
    for (const subordinate of employee.subordinates) {
      this.getAllIndividualContributors(subordinate, ics);
    }
    
    return ics;
  }

  /**
   * Display department summary
   */
  getDepartmentSummary() {
    const departments = {};
    
    const analyzeDepartment = (employee) => {
      const dept = employee.department;
      if (!departments[dept]) {
        departments[dept] = { count: 0, totalSalary: 0, employees: [] };
      }
      
      departments[dept].count++;
      departments[dept].totalSalary += employee.salary;
      departments[dept].employees.push(employee.name);
      
      for (const subordinate of employee.subordinates) {
        analyzeDepartment(subordinate);
      }
    };
    
    analyzeDepartment(this.ceo);
    
    console.log(`\n📁 Department Summary for ${this.companyName}:`);
    for (const [dept, info] of Object.entries(departments)) {
      console.log(`\n${dept}:`);
      console.log(`  Employees: ${info.count}`);
      console.log(`  Total Salary Budget: $${info.totalSalary.toLocaleString()}`);
      console.log(`  Average Salary: $${Math.round(info.totalSalary / info.count).toLocaleString()}`);
    }
  }

  /**
   * Reorganize: Move employee and their team to new manager
   */
  reorganize(employeeName, newManagerName) {
    const employee = this.findEmployee(employeeName);
    const newManager = this.findEmployee(newManagerName);
    
    if (!employee || !newManager) {
      console.log('❌ Employee or manager not found');
      return false;
    }
    
    if (employee === this.ceo) {
      console.log('❌ Cannot move the CEO');
      return false;
    }
    
    // Remove from current manager
    if (employee.manager) {
      employee.manager.removeSubordinate(employee.name);
    }
    
    // Add to new manager
    newManager.addSubordinate(employee);
    
    console.log(`✅ Reorganized: ${employeeName} now reports to ${newManagerName}`);
    return true;
  }

  /**
   * Real-world applications demonstration
   */
  static demonstrateApplications() {
    console.log(`\n🌟 Real-World Applications of Trees:\n\n` +
      `1. 📁 File Systems: Folders and subfolders\n` +
      `2. 🌐 HTML DOM: Web page element hierarchy\n` +
      `3. 🧠 Decision Trees: AI/ML decision making\n` +
      `4. 📊 Database Indexes: B-trees for fast lookups\n` +
      `5. 📝 Expression Trees: Mathematical expressions\n` +
      `6. 🌲 Family Trees: Genealogy and ancestry\n` +
      `7. 🗺️  Game Trees: Chess moves and strategies\n`);
  }
}

/**
 * Binary Search Tree: Employee Performance Ranking
 */
class PerformanceRankingBST {
  constructor() {
    this.root = null;
  }

  /**
   * Insert employee by performance score
   * Time Complexity: O(log n) average, O(n) worst case
   */
  insert(name, performanceScore) {
    const newNode = {
      name,
      performanceScore,
      left: null,
      right: null
    };
    
    if (this.root === null) {
      this.root = newNode;
      console.log(`🌟 ${name} added as root (score: ${performanceScore})`);
      return;
    }
    
    this.insertRecursive(this.root, newNode);
  }

  insertRecursive(node, newNode) {
    if (newNode.performanceScore < node.performanceScore) {
      if (node.left === null) {
        node.left = newNode;
        console.log(`⬅️  ${newNode.name} added to left of ${node.name}`);
      } else {
        this.insertRecursive(node.left, newNode);
      }
    } else {
      if (node.right === null) {
        node.right = newNode;
        console.log(`➡️  ${newNode.name} added to right of ${node.name}`);
      } else {
        this.insertRecursive(node.right, newNode);
      }
    }
  }

  /**
   * Find employee by performance score
   * Time Complexity: O(log n) average
   */
  search(performanceScore, node = this.root) {
    if (node === null) {
      console.log(`No employee with score ${performanceScore}`);
      return null;
    }
    
    if (performanceScore === node.performanceScore) {
      console.log(`✅ Found ${node.name} with score ${performanceScore}`);
      return node;
    }
    
    if (performanceScore < node.performanceScore) {
      console.log(`Searching left of ${node.name}...`);
      return this.search(performanceScore, node.left);
    } else {
      console.log(`Searching right of ${node.name}...`);
      return this.search(performanceScore, node.right);
    }
  }

  /**
   * Get all employees in performance order (In-order traversal)
   * Time Complexity: O(n)
   */
  getPerformanceRanking(node = this.root, ranking = []) {
    if (node !== null) {
      this.getPerformanceRanking(node.left, ranking);
      ranking.push({ name: node.name, score: node.performanceScore });
      this.getPerformanceRanking(node.right, ranking);
    }
    
    return ranking;
  }

  /**
   * Display performance ranking
   */
  displayRanking() {
    console.log('\n🏆 Employee Performance Ranking:');
    const ranking = this.getPerformanceRanking();
    
    ranking.forEach((employee, index) => {
      const medal = index < 3 ? ['🥇', '🥈', '🥉'][index] : '🏅';
      console.log(`${medal} ${index + 1}. ${employee.name} - Score: ${employee.score}`);
    });
  }

  /**
   * Find employees within performance range
   */
  findInRange(minScore, maxScore, node = this.root, result = []) {
    if (node === null) return result;
    
    if (node.performanceScore >= minScore && node.performanceScore <= maxScore) {
      result.push(node);
    }
    
    if (minScore < node.performanceScore) {
      this.findInRange(minScore, maxScore, node.left, result);
    }
    
    if (maxScore > node.performanceScore) {
      this.findInRange(minScore, maxScore, node.right, result);
    }
    
    return result;
  }
}

/**
 * Tree Practice Problems
 */
class TreePracticeProblems {
  /**
   * Problem 1: Calculate tree height (depth)
   */
  static calculateTreeHeight(node) {
    if (node === null) return 0;
    
    const leftHeight = this.calculateTreeHeight(node.left);
    const rightHeight = this.calculateTreeHeight(node.right);
    
    return Math.max(leftHeight, rightHeight) + 1;
  }

  /**
   * Problem 2: Check if organization is balanced
   * (No manager has too many direct reports)
   */
  static isOrganizationBalanced(employee, maxDirectReports = 7) {
    if (employee.subordinates.length > maxDirectReports) {
      console.log(`⚠️  ${employee.name} has too many direct reports: ${employee.subordinates.length}`);
      return false;
    }
    
    for (const subordinate of employee.subordinates) {
      if (!this.isOrganizationBalanced(subordinate, maxDirectReports)) {
        return false;
      }
    }
    
    return true;
  }

  /**
   * Problem 3: Find lowest common manager
   */
  static findLowestCommonManager(org, employee1Name, employee2Name) {
    const emp1Chain = org.getReportingChain(employee1Name);
    const emp2Chain = org.getReportingChain(employee2Name);
    
    if (emp1Chain.length === 0 || emp2Chain.length === 0) {
      return null;
    }
    
    // Convert to sets for easier lookup
    const emp1Managers = new Set(emp1Chain.map(emp => emp.name));
    
    // Find first common manager in emp2's chain
    for (const manager of emp2Chain) {
      if (emp1Managers.has(manager.name)) {
        console.log(`🤝 Lowest common manager: ${manager.name}`);
        return manager;
      }
    }
    
    return null;
  }

  /**
   * Problem 4: Serialize and deserialize organization chart
   */
  static serializeOrganization(employee) {
    if (!employee) return 'null';
    
    const serialized = {
      name: employee.name,
      position: employee.position,
      department: employee.department,
      salary: employee.salary,
      subordinates: employee.subordinates.map(sub => this.serializeOrganization(sub))
    };
    
    return JSON.stringify(serialized);
  }

  static deserializeOrganization(serializedData) {
    if (serializedData === 'null') return null;
    
    const data = JSON.parse(serializedData);
    const employee = new Employee(data.name, data.position, data.department, data.salary);
    
    data.subordinates.forEach(subData => {
      if (subData !== 'null') {
        const subordinate = this.deserializeOrganization(subData);
        if (subordinate) {
          employee.addSubordinate(subordinate);
        }
      }
    });
    
    return employee;
  }
}

// Export for use in other modules
export { 
  Employee, 
  CompanyOrganizationChart, 
  PerformanceRankingBST, 
  TreePracticeProblems 
};

import { fileURLToPath } from 'url';
import { argv } from 'process';
const __filename = fileURLToPath(import.meta.url);

// Example usage and demonstration
if (argv[1] === __filename) {
  console.log('🏢 Welcome to the Company Organization Chart Learning Module!\n');
  
  // Create company organization
  const techCorp = new CompanyOrganizationChart('Sarah Johnson', 'TechCorp Inc.');
  
  // Build organization structure
  console.log('🏢 Building organization structure:');
  
  // Add VPs
  techCorp.addEmployee('Sarah Johnson', 'Mike Chen', 'VP Engineering', 'Engineering', 250000);
  techCorp.addEmployee('Sarah Johnson', 'Lisa Rodriguez', 'VP Sales', 'Sales', 240000);
  techCorp.addEmployee('Sarah Johnson', 'David Kim', 'VP Marketing', 'Marketing', 220000);
  
  // Add engineering managers
  techCorp.addEmployee('Mike Chen', 'Alex Thompson', 'Engineering Manager', 'Engineering', 180000);
  techCorp.addEmployee('Mike Chen', 'Emily Davis', 'Engineering Manager', 'Engineering', 185000);
  
  // Add engineers
  techCorp.addEmployee('Alex Thompson', 'John Smith', 'Senior Engineer', 'Engineering', 140000);
  techCorp.addEmployee('Alex Thompson', 'Jane Wilson', 'Software Engineer', 'Engineering', 120000);
  techCorp.addEmployee('Emily Davis', 'Bob Brown', 'Senior Engineer', 'Engineering', 145000);
  techCorp.addEmployee('Emily Davis', 'Alice Green', 'Junior Engineer', 'Engineering', 95000);
  
  // Add sales team
  techCorp.addEmployee('Lisa Rodriguez', 'Tom Jackson', 'Sales Manager', 'Sales', 160000);
  techCorp.addEmployee('Tom Jackson', 'Mary White', 'Sales Rep', 'Sales', 80000);
  techCorp.addEmployee('Tom Jackson', 'Chris Lee', 'Sales Rep', 'Sales', 75000);
  
  // Display organization chart
  techCorp.displayOrganizationChart();
  
  // Find employees
  console.log('\n🔍 Finding employees:');
  const alice = techCorp.findEmployee('Alice Green');
  if (alice) {
    console.log(`Found: ${alice.toString()}`);
    console.log(`Team size under Alice: ${alice.getTotalTeamSize()}`);
  }
  
  // Get reporting chain
  techCorp.getReportingChain('Alice Green');
  
  // Find employees at specific level
  techCorp.getEmployeesAtLevel(2);
  
  // Organization metrics
  console.log('\n📊 Organization Metrics:');
  console.log(`Organization depth: ${techCorp.getOrganizationDepth()} levels`);
  console.log(`Total employees: ${techCorp.totalEmployees}`);
  console.log(`Total salary budget: $${techCorp.ceo.getTotalSalaryBudget().toLocaleString()}`);
  
  const managers = techCorp.getAllManagers();
  const ics = techCorp.getAllIndividualContributors();
  console.log(`Managers: ${managers.length}, Individual Contributors: ${ics.length}`);
  
  // Department summary
  techCorp.getDepartmentSummary();
  
  // Reorganization demo
  console.log('\n🔄 Reorganization Demo:');
  techCorp.reorganize('Alice Green', 'Alex Thompson');
  
  // Binary Search Tree for performance ranking
  console.log('\n🏆 Performance Ranking System:');
  const performanceTree = new PerformanceRankingBST();
  
  performanceTree.insert('John Smith', 92);
  performanceTree.insert('Jane Wilson', 88);
  performanceTree.insert('Bob Brown', 95);
  performanceTree.insert('Alice Green', 85);
  performanceTree.insert('Mary White', 90);
  performanceTree.insert('Chris Lee', 82);
  
  performanceTree.displayRanking();
  
  // Search for specific performance score
  console.log('\n🔍 Performance Search:');
  performanceTree.search(90);
  
  // Find employees in performance range
  console.log('\n🎨 Employees in score range 85-93:');
  const midPerformers = performanceTree.findInRange(85, 93);
  midPerformers.forEach(emp => {
    console.log(`  ${emp.name}: ${emp.performanceScore}`);
  });
  
  // Show real-world applications
  CompanyOrganizationChart.demonstrateApplications();
  
  // Practice problems
  console.log('\n🧠 Practice Problems:');
  
  console.log('\n1. Organization Balance Check:');
  const isBalanced = TreePracticeProblems.isOrganizationBalanced(techCorp.ceo, 3);
  console.log(`Organization is balanced: ${isBalanced}`);
  
  console.log('\n2. Lowest Common Manager:');
  TreePracticeProblems.findLowestCommonManager(techCorp, 'Alice Green', 'Jane Wilson');
}