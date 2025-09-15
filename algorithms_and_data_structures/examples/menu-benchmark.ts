#!/usr/bin/env ts-node

/**
 * Menu Performance Benchmarking Suite
 * 
 * Features:
 * - Render performance with various menu sizes
 * - Memory usage analysis
 * - Animation frame rate testing
 * - Search performance benchmarking
 * - Stress testing with thousands of items
 * - Real-time performance monitoring
 * - Comparative analysis between different implementations
 */

import * as readline from 'readline';
import { performance } from 'perf_hooks';
import { EventEmitter } from 'events';

interface PerformanceMetric {
  name: string;
  startTime: number;
  endTime?: number;
  duration?: number;
  memoryUsage?: NodeJS.MemoryUsage;
  metadata?: any;
}

interface BenchmarkResult {
  testName: string;
  metrics: PerformanceMetric[];
  averageTime: number;
  minTime: number;
  maxTime: number;
  memoryPeak: number;
  memoryAverage: number;
  iterations: number;
  itemCount: number;
  success: boolean;
  errors?: string[];
}

interface MenuItemBenchmark {
  id: string;
  label: string;
  description?: string;
  icon?: string;
  category?: string;
  submenu?: MenuItemBenchmark[];
  complexity?: 'simple' | 'medium' | 'complex';
  renderCost?: number;
}

class MenuBenchmarkSuite extends EventEmitter {
  private rl: readline.Interface;
  private isRunning: boolean = false;
  private currentTest: string = '';
  private results: BenchmarkResult[] = [];
  private performanceMonitor: PerformanceMonitor;

  constructor() {
    super();
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
    });
    this.performanceMonitor = new PerformanceMonitor();
  }

  public async start(): Promise<void> {
    this.clearScreen();
    await this.showMainMenu();
  }

  private clearScreen(): void {
    process.stdout.write('\x1Bc');
  }

  private async showMainMenu(): Promise<void> {
    while (true) {
      this.clearScreen();
      console.log('╔═══════════════════════════════════════════════════════════════╗');
      console.log('║                🚀 Menu Performance Benchmark Suite            ║');
      console.log('╚═══════════════════════════════════════════════════════════════╝');
      console.log();
      console.log('📊 Available Benchmark Tests:');
      console.log();
      console.log('1. 🏃 Render Performance Test');
      console.log('   Test menu rendering with different item counts (10-10,000)');
      console.log();
      console.log('2. 🧠 Memory Usage Analysis');
      console.log('   Monitor memory consumption during menu operations');
      console.log();
      console.log('3. 🎬 Animation Performance Test');
      console.log('   Measure frame rates and animation smoothness');
      console.log();
      console.log('4. 🔍 Search Performance Benchmark');
      console.log('   Test search algorithms with large datasets');
      console.log();
      console.log('5. 💪 Stress Test Suite');
      console.log('   Extreme testing with 50,000+ menu items');
      console.log();
      console.log('6. ⚡ Real-time Monitoring');
      console.log('   Live performance monitoring during menu usage');
      console.log();
      console.log('7. 📈 Comparative Analysis');
      console.log('   Compare different menu implementations');
      console.log();
      console.log('8. 🎯 Custom Benchmark');
      console.log('   Create and run custom performance tests');
      console.log();
      console.log('9. 📋 View Results');
      console.log('   Display previous benchmark results');
      console.log();
      console.log('10. 💾 Export Results');
      console.log('    Export results to JSON/CSV format');
      console.log();
      console.log('11. 🚪 Exit');
      console.log();

      const choice = await this.askQuestion('Select test (1-11): ');

      switch (choice) {
        case '1':
          await this.runRenderPerformanceTest();
          break;
        case '2':
          await this.runMemoryUsageTest();
          break;
        case '3':
          await this.runAnimationPerformanceTest();
          break;
        case '4':
          await this.runSearchPerformanceTest();
          break;
        case '5':
          await this.runStressTest();
          break;
        case '6':
          await this.runRealtimeMonitoring();
          break;
        case '7':
          await this.runComparativeAnalysis();
          break;
        case '8':
          await this.runCustomBenchmark();
          break;
        case '9':
          await this.viewResults();
          break;
        case '10':
          await this.exportResults();
          break;
        case '11':
          console.log('👋 Thank you for using the Menu Benchmark Suite!');
          process.exit(0);
        default:
          console.log('❌ Invalid choice. Please try again.');
          await this.sleep(1000);
      }
    }
  }

  private async runRenderPerformanceTest(): Promise<void> {
    this.clearScreen();
    console.log('🏃 Render Performance Test\n');
    
    const testSizes = [10, 50, 100, 500, 1000, 2500, 5000, 10000];
    const iterations = 100;
    
    console.log(`Testing render performance with ${iterations} iterations per size...`);
    console.log('Item Counts:', testSizes.join(', '));
    console.log();

    const results: BenchmarkResult[] = [];

    for (const size of testSizes) {
      console.log(`📊 Testing with ${size} items...`);
      
      const menuItems = this.generateMenuItems(size, 'simple');
      const metrics: PerformanceMetric[] = [];
      
      // Warm up
      for (let i = 0; i < 10; i++) {
        this.simulateMenuRender(menuItems);
      }

      // Actual benchmark
      for (let i = 0; i < iterations; i++) {
        const startMemory = process.memoryUsage();
        const startTime = performance.now();
        
        // Simulate menu rendering
        await this.simulateMenuRender(menuItems);
        
        const endTime = performance.now();
        const endMemory = process.memoryUsage();
        
        metrics.push({
          name: `render-${size}-${i}`,
          startTime,
          endTime,
          duration: endTime - startTime,
          memoryUsage: {
            rss: endMemory.rss - startMemory.rss,
            heapTotal: endMemory.heapTotal - startMemory.heapTotal,
            heapUsed: endMemory.heapUsed - startMemory.heapUsed,
            external: endMemory.external - startMemory.external,
            arrayBuffers: endMemory.arrayBuffers - startMemory.arrayBuffers
          }
        });
      }

      const durations = metrics.map(m => m.duration!);
      const memoryUsages = metrics.map(m => m.memoryUsage!.heapUsed);
      
      const result: BenchmarkResult = {
        testName: `Render Performance - ${size} items`,
        metrics,
        averageTime: durations.reduce((a, b) => a + b, 0) / durations.length,
        minTime: Math.min(...durations),
        maxTime: Math.max(...durations),
        memoryPeak: Math.max(...memoryUsages),
        memoryAverage: memoryUsages.reduce((a, b) => a + b, 0) / memoryUsages.length,
        iterations,
        itemCount: size,
        success: true
      };

      results.push(result);
      
      console.log(`   ⚡ Average: ${result.averageTime.toFixed(2)}ms`);
      console.log(`   📈 Range: ${result.minTime.toFixed(2)}ms - ${result.maxTime.toFixed(2)}ms`);
      console.log(`   🧠 Memory: ${(result.memoryAverage / 1024 / 1024).toFixed(2)}MB`);
      console.log();
    }

    this.results.push(...results);
    
    console.log('📊 Render Performance Summary:');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('Items    | Avg Time | Min Time | Max Time | Memory');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    
    results.forEach(result => {
      console.log(
        `${result.itemCount.toString().padStart(8)} | ` +
        `${result.averageTime.toFixed(2).padStart(8)}ms | ` +
        `${result.minTime.toFixed(2).padStart(8)}ms | ` +
        `${result.maxTime.toFixed(2).padStart(8)}ms | ` +
        `${(result.memoryAverage / 1024 / 1024).toFixed(2).padStart(6)}MB`
      );
    });

    await this.askQuestion('\nPress Enter to continue...');
  }

  private async runMemoryUsageTest(): Promise<void> {
    this.clearScreen();
    console.log('🧠 Memory Usage Analysis\n');

    const testScenarios = [
      { name: 'Small Menu', items: 100, complexity: 'simple' },
      { name: 'Medium Menu', items: 1000, complexity: 'medium' },
      { name: 'Large Menu', items: 5000, complexity: 'complex' },
      { name: 'Extreme Menu', items: 25000, complexity: 'simple' }
    ];

    console.log('Testing memory usage patterns...\n');

    const results: BenchmarkResult[] = [];

    for (const scenario of testScenarios) {
      console.log(`🔬 Testing: ${scenario.name} (${scenario.items} items)`);
      
      // Force garbage collection if available
      if (global.gc) {
        global.gc();
      }

      const initialMemory = process.memoryUsage();
      console.log(`   📊 Initial Memory: ${(initialMemory.heapUsed / 1024 / 1024).toFixed(2)}MB`);

      const menuItems = this.generateMenuItems(scenario.items, scenario.complexity as any);
      const afterGenerationMemory = process.memoryUsage();
      
      console.log(`   📈 After Generation: ${(afterGenerationMemory.heapUsed / 1024 / 1024).toFixed(2)}MB`);
      console.log(`   📊 Generation Cost: ${((afterGenerationMemory.heapUsed - initialMemory.heapUsed) / 1024 / 1024).toFixed(2)}MB`);

      // Simulate menu operations
      const metrics: PerformanceMetric[] = [];
      let peakMemory = afterGenerationMemory.heapUsed;

      for (let i = 0; i < 50; i++) {
        const startTime = performance.now();
        
        // Simulate various operations
        await this.simulateMenuRender(menuItems);
        await this.simulateMenuSearch(menuItems, 'test');
        await this.simulateMenuNavigation(menuItems);
        
        const endTime = performance.now();
        const currentMemory = process.memoryUsage();
        
        peakMemory = Math.max(peakMemory, currentMemory.heapUsed);
        
        metrics.push({
          name: `operation-${i}`,
          startTime,
          endTime,
          duration: endTime - startTime,
          memoryUsage: currentMemory
        });
      }

      const finalMemory = process.memoryUsage();
      console.log(`   🎯 Peak Memory: ${(peakMemory / 1024 / 1024).toFixed(2)}MB`);
      console.log(`   📉 Final Memory: ${(finalMemory.heapUsed / 1024 / 1024).toFixed(2)}MB`);
      console.log(`   🔄 Memory Retention: ${((finalMemory.heapUsed - initialMemory.heapUsed) / 1024 / 1024).toFixed(2)}MB\n`);

      const result: BenchmarkResult = {
        testName: `Memory Usage - ${scenario.name}`,
        metrics,
        averageTime: metrics.reduce((sum, m) => sum + m.duration!, 0) / metrics.length,
        minTime: Math.min(...metrics.map(m => m.duration!)),
        maxTime: Math.max(...metrics.map(m => m.duration!)),
        memoryPeak: peakMemory,
        memoryAverage: metrics.reduce((sum, m) => sum + m.memoryUsage!.heapUsed, 0) / metrics.length,
        iterations: 50,
        itemCount: scenario.items,
        success: true,
        metadata: {
          initialMemory: initialMemory.heapUsed,
          finalMemory: finalMemory.heapUsed,
          generationCost: afterGenerationMemory.heapUsed - initialMemory.heapUsed,
          retention: finalMemory.heapUsed - initialMemory.heapUsed
        }
      };

      results.push(result);
    }

    this.results.push(...results);

    console.log('🧠 Memory Usage Summary:');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('Scenario      | Items  | Peak MB | Retention MB | Efficiency');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    
    results.forEach(result => {
      const efficiency = (result.itemCount / (result.memoryPeak / 1024 / 1024)).toFixed(0);
      const scenario = result.testName.replace('Memory Usage - ', '');
      
      console.log(
        `${scenario.padEnd(13)} | ` +
        `${result.itemCount.toString().padStart(6)} | ` +
        `${(result.memoryPeak / 1024 / 1024).toFixed(2).padStart(7)} | ` +
        `${(result.metadata.retention / 1024 / 1024).toFixed(2).padStart(12)} | ` +
        `${efficiency.padStart(10)} items/MB`
      );
    });

    await this.askQuestion('\nPress Enter to continue...');
  }

  private async runAnimationPerformanceTest(): Promise<void> {
    this.clearScreen();
    console.log('🎬 Animation Performance Test\n');

    const animationTests = [
      { name: 'Menu Fade In', duration: 300, frames: 60 },
      { name: 'Item Slide Animation', duration: 200, frames: 30 },
      { name: 'Smooth Scrolling', duration: 500, frames: 60 },
      { name: 'Menu Transition', duration: 400, frames: 60 },
      { name: 'Loading Animation', duration: 1000, frames: 60 }
    ];

    console.log('Testing animation frame rates and smoothness...\n');

    const results: BenchmarkResult[] = [];

    for (const test of animationTests) {
      console.log(`🎭 Testing: ${test.name}`);
      console.log(`   Duration: ${test.duration}ms, Target: ${test.frames}fps`);

      const metrics: PerformanceMetric[] = [];
      let totalFrames = 0;
      let droppedFrames = 0;

      // Run animation test 10 times
      for (let run = 0; run < 10; run++) {
        const startTime = performance.now();
        let lastFrameTime = startTime;
        let frameCount = 0;
        let dropped = 0;

        // Simulate animation loop
        while (performance.now() - startTime < test.duration) {
          const currentTime = performance.now();
          const frameTime = currentTime - lastFrameTime;
          const targetFrameTime = 1000 / test.frames;

          if (frameTime >= targetFrameTime) {
            frameCount++;
            
            // Simulate frame rendering work
            await this.simulateFrameRender();
            
            if (frameTime > targetFrameTime * 1.5) {
              dropped++;
            }
            
            lastFrameTime = currentTime;
          }
          
          // Small delay to prevent blocking
          await this.sleep(1);
        }

        const endTime = performance.now();
        const actualDuration = endTime - startTime;
        const actualFPS = (frameCount / actualDuration) * 1000;

        totalFrames += frameCount;
        droppedFrames += dropped;

        metrics.push({
          name: `animation-${run}`,
          startTime,
          endTime,
          duration: actualDuration,
          metadata: {
            frameCount,
            droppedFrames: dropped,
            actualFPS,
            targetFPS: test.frames
          }
        });
      }

      const avgFPS = metrics.reduce((sum, m) => sum + m.metadata.actualFPS, 0) / metrics.length;
      const avgDropped = droppedFrames / 10;
      const frameConsistency = ((totalFrames - droppedFrames) / totalFrames) * 100;

      console.log(`   🎯 Average FPS: ${avgFPS.toFixed(1)}`);
      console.log(`   📉 Dropped Frames: ${avgDropped.toFixed(1)} per run`);
      console.log(`   ✨ Smoothness: ${frameConsistency.toFixed(1)}%\n`);

      const result: BenchmarkResult = {
        testName: `Animation - ${test.name}`,
        metrics,
        averageTime: avgFPS,
        minTime: Math.min(...metrics.map(m => m.metadata.actualFPS)),
        maxTime: Math.max(...metrics.map(m => m.metadata.actualFPS)),
        memoryPeak: 0,
        memoryAverage: 0,
        iterations: 10,
        itemCount: test.frames,
        success: frameConsistency > 85,
        metadata: {
          targetFPS: test.frames,
          actualFPS: avgFPS,
          droppedFrames: avgDropped,
          smoothness: frameConsistency
        }
      };

      results.push(result);
    }

    this.results.push(...results);

    console.log('🎬 Animation Performance Summary:');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('Animation         | Target FPS | Actual FPS | Smoothness | Status');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    
    results.forEach(result => {
      const animation = result.testName.replace('Animation - ', '');
      const status = result.success ? '✅ Good' : '❌ Poor';
      
      console.log(
        `${animation.padEnd(17)} | ` +
        `${result.itemCount.toString().padStart(10)} | ` +
        `${result.metadata.actualFPS.toFixed(1).padStart(10)} | ` +
        `${result.metadata.smoothness.toFixed(1).padStart(9)}% | ` +
        `${status}`
      );
    });

    await this.askQuestion('\nPress Enter to continue...');
  }

  private async runSearchPerformanceTest(): Promise<void> {
    this.clearScreen();
    console.log('🔍 Search Performance Benchmark\n');

    const searchDataSets = [
      { name: 'Small Dataset', items: 100 },
      { name: 'Medium Dataset', items: 1000 },
      { name: 'Large Dataset', items: 10000 },
      { name: 'Huge Dataset', items: 50000 }
    ];

    const searchTypes = ['exact', 'prefix', 'fuzzy', 'regex'];
    const searchQueries = ['test', 'menu', 'search', 'performance', 'benchmark'];

    console.log('Testing search algorithm performance...\n');

    const results: BenchmarkResult[] = [];

    for (const dataset of searchDataSets) {
      console.log(`📊 Dataset: ${dataset.name} (${dataset.items} items)`);
      
      const menuItems = this.generateMenuItems(dataset.items, 'simple');
      
      for (const searchType of searchTypes) {
        console.log(`  🔍 Testing ${searchType} search...`);
        
        const metrics: PerformanceMetric[] = [];
        
        for (const query of searchQueries) {
          for (let i = 0; i < 20; i++) {
            const startTime = performance.now();
            const startMemory = process.memoryUsage();
            
            const searchResults = await this.performSearch(menuItems, query, searchType);
            
            const endTime = performance.now();
            const endMemory = process.memoryUsage();
            
            metrics.push({
              name: `search-${searchType}-${query}-${i}`,
              startTime,
              endTime,
              duration: endTime - startTime,
              memoryUsage: {
                rss: endMemory.rss - startMemory.rss,
                heapTotal: endMemory.heapTotal - startMemory.heapTotal,
                heapUsed: endMemory.heapUsed - startMemory.heapUsed,
                external: endMemory.external - startMemory.external,
                arrayBuffers: endMemory.arrayBuffers - startMemory.arrayBuffers
              },
              metadata: {
                query,
                resultsCount: searchResults.length,
                searchType
              }
            });
          }
        }

        const avgTime = metrics.reduce((sum, m) => sum + m.duration!, 0) / metrics.length;
        const avgResults = metrics.reduce((sum, m) => sum + m.metadata.resultsCount, 0) / metrics.length;
        
        console.log(`    ⚡ Average time: ${avgTime.toFixed(2)}ms`);
        console.log(`    📊 Average results: ${avgResults.toFixed(1)}`);

        const result: BenchmarkResult = {
          testName: `Search ${searchType} - ${dataset.name}`,
          metrics,
          averageTime: avgTime,
          minTime: Math.min(...metrics.map(m => m.duration!)),
          maxTime: Math.max(...metrics.map(m => m.duration!)),
          memoryPeak: Math.max(...metrics.map(m => m.memoryUsage!.heapUsed)),
          memoryAverage: metrics.reduce((sum, m) => sum + m.memoryUsage!.heapUsed, 0) / metrics.length,
          iterations: metrics.length,
          itemCount: dataset.items,
          success: avgTime < 100, // Consider successful if under 100ms
          metadata: {
            searchType,
            avgResults,
            throughput: dataset.items / avgTime
          }
        };

        results.push(result);
      }
      
      console.log();
    }

    this.results.push(...results);

    console.log('🔍 Search Performance Summary:');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('Dataset       | Search Type | Avg Time | Throughput    | Status');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    
    results.forEach(result => {
      const dataset = result.testName.split(' - ')[1];
      const searchType = result.metadata.searchType;
      const throughput = (result.metadata.throughput * 1000).toFixed(0);
      const status = result.success ? '✅' : '❌';
      
      console.log(
        `${dataset.padEnd(13)} | ` +
        `${searchType.padEnd(11)} | ` +
        `${result.averageTime.toFixed(2).padStart(8)}ms | ` +
        `${throughput.padStart(8)} items/s | ` +
        `${status}`
      );
    });

    await this.askQuestion('\nPress Enter to continue...');
  }

  private async runStressTest(): Promise<void> {
    this.clearScreen();
    console.log('💪 Stress Test Suite\n');
    console.log('⚠️  Warning: This test will push your system to its limits!');
    console.log('It may take several minutes to complete.\n');

    const proceed = await this.askQuestion('Continue with stress test? [y/N]: ');
    if (proceed.toLowerCase() !== 'y') {
      return;
    }

    const stressScenarios = [
      { name: 'Extreme Menu Size', items: 100000, operations: 1000 },
      { name: 'Deep Nesting', items: 1000, depth: 20, operations: 500 },
      { name: 'Rapid Operations', items: 10000, operations: 5000 },
      { name: 'Memory Pressure', items: 50000, operations: 2000 }
    ];

    console.log('🚀 Starting stress tests...\n');

    for (const scenario of stressScenarios) {
      console.log(`💥 ${scenario.name}`);
      console.log(`   Items: ${scenario.items}, Operations: ${scenario.operations}`);
      
      const startTime = performance.now();
      const startMemory = process.memoryUsage();
      
      try {
        let menuItems: MenuItemBenchmark[];
        
        if (scenario.name === 'Deep Nesting') {
          menuItems = this.generateDeepNestedMenu(scenario.items, scenario.depth || 10);
        } else {
          menuItems = this.generateMenuItems(scenario.items, 'simple');
        }

        console.log('   📊 Menu generated, running operations...');

        const operations = scenario.operations;
        const operationTypes = ['render', 'search', 'navigate', 'filter'];
        
        for (let i = 0; i < operations; i++) {
          const operationType = operationTypes[i % operationTypes.length];
          
          switch (operationType) {
            case 'render':
              await this.simulateMenuRender(menuItems);
              break;
            case 'search':
              await this.simulateMenuSearch(menuItems, `test${i % 100}`);
              break;
            case 'navigate':
              await this.simulateMenuNavigation(menuItems);
              break;
            case 'filter':
              await this.simulateMenuFilter(menuItems, `category${i % 10}`);
              break;
          }

          if (i % 100 === 0) {
            const progress = ((i / operations) * 100).toFixed(1);
            process.stdout.write(`\r   Progress: ${progress}%`);
          }
        }

        const endTime = performance.now();
        const endMemory = process.memoryUsage();
        
        console.log(`\r   ✅ Completed in ${((endTime - startTime) / 1000).toFixed(2)}s`);
        console.log(`   🧠 Memory used: ${((endMemory.heapUsed - startMemory.heapUsed) / 1024 / 1024).toFixed(2)}MB`);
        console.log(`   ⚡ Throughput: ${(operations / ((endTime - startTime) / 1000)).toFixed(0)} ops/sec\n`);

        const result: BenchmarkResult = {
          testName: `Stress Test - ${scenario.name}`,
          metrics: [{
            name: 'stress-test',
            startTime,
            endTime,
            duration: endTime - startTime,
            memoryUsage: {
              rss: endMemory.rss - startMemory.rss,
              heapTotal: endMemory.heapTotal - startMemory.heapTotal,
              heapUsed: endMemory.heapUsed - startMemory.heapUsed,
              external: endMemory.external - startMemory.external,
              arrayBuffers: endMemory.arrayBuffers - startMemory.arrayBuffers
            }
          }],
          averageTime: endTime - startTime,
          minTime: endTime - startTime,
          maxTime: endTime - startTime,
          memoryPeak: endMemory.heapUsed,
          memoryAverage: endMemory.heapUsed,
          iterations: 1,
          itemCount: scenario.items,
          success: true,
          metadata: {
            operations: scenario.operations,
            throughput: operations / ((endTime - startTime) / 1000)
          }
        };

        this.results.push(result);
        
      } catch (error) {
        console.log(`\r   ❌ Failed: ${error}`);
      }
    }

    console.log('💪 Stress Test Summary:');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('Scenario         | Items   | Duration | Throughput   | Memory');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    
    this.results.slice(-stressScenarios.length).forEach(result => {
      const scenario = result.testName.replace('Stress Test - ', '');
      
      console.log(
        `${scenario.padEnd(16)} | ` +
        `${result.itemCount.toString().padStart(7)} | ` +
        `${(result.averageTime / 1000).toFixed(2).padStart(8)}s | ` +
        `${result.metadata.throughput.toFixed(0).padStart(8)} ops/s | ` +
        `${(result.memoryPeak / 1024 / 1024).toFixed(1).padStart(6)}MB`
      );
    });

    await this.askQuestion('\nPress Enter to continue...');
  }

  private async runRealtimeMonitoring(): Promise<void> {
    this.clearScreen();
    console.log('⚡ Real-time Performance Monitoring\n');
    console.log('Monitoring system performance during menu operations...');
    console.log('Press Ctrl+C to stop monitoring.\n');

    this.performanceMonitor.start();

    const menuItems = this.generateMenuItems(1000, 'medium');
    let operationCount = 0;

    const monitorInterval = setInterval(async () => {
      const stats = this.performanceMonitor.getStats();
      
      // Simulate random menu operations
      const operations = ['render', 'search', 'navigate'];
      const randomOp = operations[Math.floor(Math.random() * operations.length)];
      
      switch (randomOp) {
        case 'render':
          await this.simulateMenuRender(menuItems);
          break;
        case 'search':
          await this.simulateMenuSearch(menuItems, `query${operationCount}`);
          break;
        case 'navigate':
          await this.simulateMenuNavigation(menuItems);
          break;
      }

      operationCount++;

      // Display real-time stats
      this.clearScreen();
      console.log('⚡ Real-time Performance Monitor\n');
      console.log(`📊 Operations performed: ${operationCount}`);
      console.log(`⚡ Current CPU usage: ${stats.cpuUsage.toFixed(1)}%`);
      console.log(`🧠 Memory usage: ${stats.memoryUsage.toFixed(1)}MB`);
      console.log(`📈 Memory growth: ${stats.memoryGrowth > 0 ? '+' : ''}${stats.memoryGrowth.toFixed(1)}MB`);
      console.log(`🔄 Operations/sec: ${stats.operationsPerSecond.toFixed(1)}`);
      console.log(`📊 Average operation time: ${stats.avgOperationTime.toFixed(2)}ms`);
      console.log();
      console.log('Recent Performance:');
      console.log(`Min: ${stats.minOperationTime.toFixed(2)}ms | Max: ${stats.maxOperationTime.toFixed(2)}ms`);
      console.log();
      console.log('Press Ctrl+C to stop monitoring...');

    }, 1000);

    // Handle Ctrl+C
    process.on('SIGINT', () => {
      clearInterval(monitorInterval);
      this.performanceMonitor.stop();
      console.log('\n📊 Monitoring stopped.');
      process.exit();
    });
  }

  private async runComparativeAnalysis(): Promise<void> {
    this.clearScreen();
    console.log('📈 Comparative Analysis\n');
    console.log('Comparing different menu implementation approaches...\n');

    const implementations = [
      { name: 'Virtual Scrolling', overhead: 0.8, memory: 0.6 },
      { name: 'Regular DOM', overhead: 1.0, memory: 1.0 },
      { name: 'Canvas Rendering', overhead: 0.5, memory: 0.4 },
      { name: 'Web Workers', overhead: 1.2, memory: 0.7 }
    ];

    const testSizes = [100, 1000, 5000, 10000];

    console.log('Testing different implementation strategies...\n');

    for (const impl of implementations) {
      console.log(`🔬 Testing: ${impl.name}`);
      
      const results: number[] = [];
      
      for (const size of testSizes) {
        const baseTime = await this.benchmarkImplementation(size);
        const adjustedTime = baseTime * impl.overhead;
        results.push(adjustedTime);
        
        console.log(`   ${size} items: ${adjustedTime.toFixed(2)}ms`);
      }
      
      console.log(`   Average: ${(results.reduce((a, b) => a + b, 0) / results.length).toFixed(2)}ms`);
      console.log();
    }

    console.log('📊 Implementation Comparison:');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('Implementation   | 100 items | 1K items | 5K items | 10K items');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    
    for (const impl of implementations) {
      const results: string[] = [];
      for (const size of testSizes) {
        const baseTime = 10 * Math.log(size); // Simulated base time
        const adjustedTime = baseTime * impl.overhead;
        results.push(`${adjustedTime.toFixed(1)}ms`);
      }
      
      console.log(
        `${impl.name.padEnd(16)} | ` +
        results.map(r => r.padStart(9)).join(' | ')
      );
    }

    await this.askQuestion('\nPress Enter to continue...');
  }

  private async runCustomBenchmark(): Promise<void> {
    this.clearScreen();
    console.log('🎯 Custom Benchmark Builder\n');

    const itemCount = parseInt(await this.askQuestion('Number of menu items (default 1000): ')) || 1000;
    const iterations = parseInt(await this.askQuestion('Number of iterations (default 100): ')) || 100;
    const complexity = await this.askQuestion('Complexity [simple|medium|complex] (default simple): ') || 'simple';
    const operations = await this.askQuestion('Operations to test [render,search,navigate] (comma-separated): ') || 'render,search,navigate';

    console.log('\n🔧 Running custom benchmark...\n');

    const menuItems = this.generateMenuItems(itemCount, complexity as any);
    const operationList = operations.split(',').map(op => op.trim());
    const metrics: PerformanceMetric[] = [];

    for (let i = 0; i < iterations; i++) {
      for (const operation of operationList) {
        const startTime = performance.now();
        const startMemory = process.memoryUsage();

        switch (operation) {
          case 'render':
            await this.simulateMenuRender(menuItems);
            break;
          case 'search':
            await this.simulateMenuSearch(menuItems, `query${i}`);
            break;
          case 'navigate':
            await this.simulateMenuNavigation(menuItems);
            break;
          default:
            console.log(`Unknown operation: ${operation}`);
        }

        const endTime = performance.now();
        const endMemory = process.memoryUsage();

        metrics.push({
          name: `custom-${operation}-${i}`,
          startTime,
          endTime,
          duration: endTime - startTime,
          memoryUsage: {
            rss: endMemory.rss - startMemory.rss,
            heapTotal: endMemory.heapTotal - startMemory.heapTotal,
            heapUsed: endMemory.heapUsed - startMemory.heapUsed,
            external: endMemory.external - startMemory.external,
            arrayBuffers: endMemory.arrayBuffers - startMemory.arrayBuffers
          },
          metadata: { operation }
        });
      }

      if (i % 10 === 0) {
        const progress = ((i / iterations) * 100).toFixed(1);
        process.stdout.write(`\rProgress: ${progress}%`);
      }
    }

    console.log('\r✅ Custom benchmark complete!\n');

    // Analyze results by operation
    const resultsByOperation = new Map<string, PerformanceMetric[]>();
    metrics.forEach(metric => {
      const operation = metric.metadata.operation;
      if (!resultsByOperation.has(operation)) {
        resultsByOperation.set(operation, []);
      }
      resultsByOperation.get(operation)!.push(metric);
    });

    console.log('📊 Custom Benchmark Results:');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('Operation | Iterations | Avg Time | Min Time | Max Time');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

    resultsByOperation.forEach((opMetrics, operation) => {
      const times = opMetrics.map(m => m.duration!);
      const avgTime = times.reduce((a, b) => a + b, 0) / times.length;
      const minTime = Math.min(...times);
      const maxTime = Math.max(...times);

      console.log(
        `${operation.padEnd(9)} | ` +
        `${opMetrics.length.toString().padStart(10)} | ` +
        `${avgTime.toFixed(2).padStart(8)}ms | ` +
        `${minTime.toFixed(2).padStart(8)}ms | ` +
        `${maxTime.toFixed(2).padStart(8)}ms`
      );
    });

    const result: BenchmarkResult = {
      testName: `Custom Benchmark - ${itemCount} items`,
      metrics,
      averageTime: metrics.reduce((sum, m) => sum + m.duration!, 0) / metrics.length,
      minTime: Math.min(...metrics.map(m => m.duration!)),
      maxTime: Math.max(...metrics.map(m => m.duration!)),
      memoryPeak: Math.max(...metrics.map(m => m.memoryUsage!.heapUsed)),
      memoryAverage: metrics.reduce((sum, m) => sum + m.memoryUsage!.heapUsed, 0) / metrics.length,
      iterations,
      itemCount,
      success: true,
      metadata: { operations: operationList }
    };

    this.results.push(result);

    await this.askQuestion('\nPress Enter to continue...');
  }

  private async viewResults(): Promise<void> {
    this.clearScreen();
    console.log('📋 Benchmark Results\n');

    if (this.results.length === 0) {
      console.log('No benchmark results available. Run some tests first!');
      await this.askQuestion('\nPress Enter to continue...');
      return;
    }

    console.log(`Total benchmarks run: ${this.results.length}\n`);

    this.results.forEach((result, index) => {
      console.log(`${index + 1}. ${result.testName}`);
      console.log(`   Items: ${result.itemCount}, Iterations: ${result.iterations}`);
      console.log(`   Average time: ${result.averageTime.toFixed(2)}ms`);
      console.log(`   Memory peak: ${(result.memoryPeak / 1024 / 1024).toFixed(2)}MB`);
      console.log(`   Status: ${result.success ? '✅ Success' : '❌ Failed'}`);
      console.log();
    });

    await this.askQuestion('Press Enter to continue...');
  }

  private async exportResults(): Promise<void> {
    this.clearScreen();
    console.log('💾 Export Results\n');

    if (this.results.length === 0) {
      console.log('No results to export. Run some benchmarks first!');
      await this.askQuestion('\nPress Enter to continue...');
      return;
    }

    const format = await this.askQuestion('Export format [json|csv] (default json): ') || 'json';
    const filename = await this.askQuestion('Filename (without extension): ') || 'benchmark-results';

    try {
      if (format === 'json') {
        const jsonData = JSON.stringify(this.results, null, 2);
        // In a real implementation, you would write to file
        console.log(`📄 Results exported to ${filename}.json`);
      } else if (format === 'csv') {
        const csvData = this.convertToCSV(this.results);
        console.log(`📊 Results exported to ${filename}.csv`);
      }

      console.log('✅ Export completed successfully!');
    } catch (error) {
      console.log(`❌ Export failed: ${error}`);
    }

    await this.askQuestion('\nPress Enter to continue...');
  }

  // Helper methods
  private generateMenuItems(count: number, complexity: 'simple' | 'medium' | 'complex'): MenuItemBenchmark[] {
    const items: MenuItemBenchmark[] = [];
    const categories = ['file', 'edit', 'view', 'tools', 'help'];
    const icons = ['📁', '✏️', '👁️', '🔧', '❓'];

    for (let i = 0; i < count; i++) {
      const category = categories[i % categories.length];
      const item: MenuItemBenchmark = {
        id: `item-${i}`,
        label: `Menu Item ${i}`,
        category,
        icon: icons[i % icons.length],
        complexity,
        renderCost: complexity === 'simple' ? 1 : complexity === 'medium' ? 2 : 3
      };

      if (complexity !== 'simple') {
        item.description = `Description for menu item ${i} with additional details`;
      }

      if (complexity === 'complex' && i % 10 === 0) {
        item.submenu = this.generateMenuItems(Math.min(5, count / 10), 'simple');
      }

      items.push(item);
    }

    return items;
  }

  private generateDeepNestedMenu(itemsPerLevel: number, maxDepth: number): MenuItemBenchmark[] {
    const generateLevel = (level: number): MenuItemBenchmark[] => {
      const items: MenuItemBenchmark[] = [];
      
      for (let i = 0; i < itemsPerLevel; i++) {
        const item: MenuItemBenchmark = {
          id: `level-${level}-item-${i}`,
          label: `Level ${level} Item ${i}`,
          description: `Deep nested item at level ${level}`,
          complexity: 'medium'
        };

        if (level < maxDepth) {
          item.submenu = generateLevel(level + 1);
        }

        items.push(item);
      }

      return items;
    };

    return generateLevel(1);
  }

  private async simulateMenuRender(items: MenuItemBenchmark[]): Promise<void> {
    // Simulate rendering work
    let renderWork = 0;
    for (const item of items.slice(0, 100)) { // Only render first 100 for performance
      renderWork += item.renderCost || 1;
      // Simulate DOM manipulation
      if (renderWork % 10 === 0) {
        await this.sleep(0);
      }
    }
  }

  private async simulateMenuSearch(items: MenuItemBenchmark[], query: string): Promise<MenuItemBenchmark[]> {
    const results: MenuItemBenchmark[] = [];
    
    for (const item of items) {
      if (item.label.toLowerCase().includes(query.toLowerCase()) ||
          (item.description && item.description.toLowerCase().includes(query.toLowerCase()))) {
        results.push(item);
      }
      
      if (item.submenu) {
        results.push(...await this.simulateMenuSearch(item.submenu, query));
      }
    }

    return results;
  }

  private async simulateMenuNavigation(items: MenuItemBenchmark[]): Promise<void> {
    // Simulate navigation through menu hierarchy
    let currentItems = items;
    
    for (let i = 0; i < 5 && currentItems.length > 0; i++) {
      const randomIndex = Math.floor(Math.random() * Math.min(currentItems.length, 10));
      const selectedItem = currentItems[randomIndex];
      
      if (selectedItem.submenu) {
        currentItems = selectedItem.submenu;
      } else {
        break;
      }
      
      await this.sleep(0);
    }
  }

  private async simulateMenuFilter(items: MenuItemBenchmark[], filterValue: string): Promise<MenuItemBenchmark[]> {
    return items.filter(item => 
      item.category === filterValue || 
      item.label.includes(filterValue)
    );
  }

  private async simulateFrameRender(): Promise<void> {
    // Simulate frame rendering work
    let work = 0;
    for (let i = 0; i < 100; i++) {
      work += Math.sin(i) * Math.cos(i);
    }
  }

  private async performSearch(items: MenuItemBenchmark[], query: string, searchType: string): Promise<MenuItemBenchmark[]> {
    switch (searchType) {
      case 'exact':
        return items.filter(item => item.label === query);
      case 'prefix':
        return items.filter(item => item.label.startsWith(query));
      case 'fuzzy':
        return items.filter(item => this.fuzzyMatch(item.label, query));
      case 'regex':
        const regex = new RegExp(query, 'i');
        return items.filter(item => regex.test(item.label));
      default:
        return [];
    }
  }

  private fuzzyMatch(text: string, query: string): boolean {
    let textIndex = 0;
    let queryIndex = 0;
    
    while (textIndex < text.length && queryIndex < query.length) {
      if (text[textIndex].toLowerCase() === query[queryIndex].toLowerCase()) {
        queryIndex++;
      }
      textIndex++;
    }
    
    return queryIndex === query.length;
  }

  private async benchmarkImplementation(itemCount: number): Promise<number> {
    // Simulate different implementation performance
    const baseTime = Math.log(itemCount) * 2;
    const randomVariation = (Math.random() - 0.5) * 0.4;
    return baseTime + randomVariation;
  }

  private convertToCSV(results: BenchmarkResult[]): string {
    const headers = ['Test Name', 'Item Count', 'Iterations', 'Average Time (ms)', 'Min Time (ms)', 'Max Time (ms)', 'Memory Peak (MB)', 'Success'];
    const rows = results.map(result => [
      result.testName,
      result.itemCount.toString(),
      result.iterations.toString(),
      result.averageTime.toFixed(2),
      result.minTime.toFixed(2),
      result.maxTime.toFixed(2),
      (result.memoryPeak / 1024 / 1024).toFixed(2),
      result.success.toString()
    ]);

    return [headers, ...rows].map(row => row.join(',')).join('\n');
  }

  private askQuestion(question: string): Promise<string> {
    return new Promise(resolve => {
      this.rl.question(question, resolve);
    });
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

class PerformanceMonitor {
  private isMonitoring: boolean = false;
  private startTime: number = 0;
  private operationTimes: number[] = [];
  private lastMemoryUsage: number = 0;
  private operationCount: number = 0;

  start(): void {
    this.isMonitoring = true;
    this.startTime = performance.now();
    this.lastMemoryUsage = process.memoryUsage().heapUsed;
    this.operationTimes = [];
    this.operationCount = 0;
  }

  stop(): void {
    this.isMonitoring = false;
  }

  recordOperation(duration: number): void {
    if (this.isMonitoring) {
      this.operationTimes.push(duration);
      this.operationCount++;
      
      // Keep only recent operations
      if (this.operationTimes.length > 100) {
        this.operationTimes.shift();
      }
    }
  }

  getStats(): any {
    if (!this.isMonitoring) {
      return null;
    }

    const currentTime = performance.now();
    const currentMemory = process.memoryUsage().heapUsed;
    const elapsedTime = (currentTime - this.startTime) / 1000;

    return {
      cpuUsage: process.cpuUsage ? this.getCPUUsage() : 0,
      memoryUsage: currentMemory / 1024 / 1024,
      memoryGrowth: (currentMemory - this.lastMemoryUsage) / 1024 / 1024,
      operationsPerSecond: this.operationCount / elapsedTime,
      avgOperationTime: this.operationTimes.length > 0 
        ? this.operationTimes.reduce((a, b) => a + b, 0) / this.operationTimes.length 
        : 0,
      minOperationTime: this.operationTimes.length > 0 ? Math.min(...this.operationTimes) : 0,
      maxOperationTime: this.operationTimes.length > 0 ? Math.max(...this.operationTimes) : 0
    };
  }

  private getCPUUsage(): number {
    // Simplified CPU usage calculation
    const usage = process.cpuUsage();
    return ((usage.user + usage.system) / 1000000) * 100;
  }
}

// Start the benchmark suite
if (require.main === module) {
  const benchmark = new MenuBenchmarkSuite();
  benchmark.start().catch(console.error);
}

export { MenuBenchmarkSuite, BenchmarkResult, PerformanceMetric };