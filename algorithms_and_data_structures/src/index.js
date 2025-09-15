#!/usr/bin/env node
import chalk from 'chalk';
import inquirer from 'inquirer';
import Table from 'cli-table3';
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

class AlgorithmsLearningPlatform {
  constructor() {
    this.userProgress = this.loadProgress();
    this.currentLevel = this.userProgress.level || 'foundation';
  }

  loadProgress() {
    try {
      const data = readFileSync(join(__dirname, '../progress.json'), 'utf8');
      return JSON.parse(data);
    } catch {
      return { level: 'foundation', completed: [], score: 0 };
    }
  }

  async displayWelcome() {
    console.clear();
    console.log(chalk.cyan.bold(`
╔════════════════════════════════════════════════════════════════╗
║     ALGORITHMS & DATA STRUCTURES: INTUITIVE LEARNING          ║
╚════════════════════════════════════════════════════════════════╝
    `));
    
    console.log(chalk.yellow(`
Welcome! This platform teaches algorithms through everyday analogies.
No STEM background required - just curiosity and willingness to learn.
    `));
  }

  async showMainMenu() {
    const modules = [
      { name: '🏗️  Foundation: Mental Models', value: 'foundation' },
      { name: '📚  Arrays: Organizing Books', value: 'arrays' },
      { name: '🚂  Linked Lists: Train Cars', value: 'linkedlists' },
      { name: '🍽️  Stacks: Plate Dispensers', value: 'stacks' },
      { name: '☕  Queues: Coffee Shop Lines', value: 'queues' },
      { name: '🏢  Trees: Organization Charts', value: 'trees' },
      { name: '🗺️  Graphs: City Maps', value: 'graphs' },
      { name: '🎵  Sorting: Music Playlists', value: 'sorting' },
      { name: '📱  Searching: Phone Contacts', value: 'searching' },
      { name: '🪆  Recursion: Nesting Dolls', value: 'recursion' },
      { name: '🚗  Dynamic Programming: Road Trips', value: 'dynamic' },
      new inquirer.Separator(),
      { name: '📊  View Progress', value: 'progress' },
      { name: '🎯  Practice Challenges', value: 'practice' },
      { name: '❌  Exit', value: 'exit' }
    ];

    const { choice } = await inquirer.prompt([
      {
        type: 'list',
        name: 'choice',
        message: 'What would you like to learn today?',
        choices: modules,
        pageSize: 15
      }
    ]);

    return choice;
  }

  async loadModule(moduleName) {
    try {
      const module = await import(`./modules/${moduleName}/index.js`);
      await module.default.run(this);
    } catch (error) {
      console.log(chalk.red(`Module ${moduleName} is under construction.`));
      console.log(chalk.yellow('Check back soon!'));
      await this.pause();
    }
  }

  async showProgress() {
    console.clear();
    console.log(chalk.cyan.bold('\n📊 YOUR LEARNING PROGRESS\n'));

    const table = new Table({
      head: ['Module', 'Status', 'Score'],
      colWidths: [30, 15, 10],
      style: { head: ['cyan'] }
    });

    const modules = [
      'foundation', 'arrays', 'linkedlists', 'stacks', 
      'queues', 'trees', 'graphs', 'sorting', 
      'searching', 'recursion', 'dynamic'
    ];

    modules.forEach(mod => {
      const status = this.userProgress.completed?.includes(mod) 
        ? chalk.green('✓ Complete') 
        : chalk.yellow('In Progress');
      const score = this.userProgress.scores?.[mod] || '-';
      table.push([mod, status, score]);
    });

    console.log(table.toString());
    console.log(chalk.yellow(`\nTotal Score: ${this.userProgress.score || 0}`));
    await this.pause();
  }

  async pause() {
    await inquirer.prompt([{
      type: 'input',
      name: 'continue',
      message: chalk.dim('Press Enter to continue...')
    }]);
  }

  async run() {
    await this.displayWelcome();
    
    while (true) {
      const choice = await this.showMainMenu();
      
      if (choice === 'exit') {
        console.log(chalk.green('\nHappy learning! Come back soon! 🎓\n'));
        process.exit(0);
      } else if (choice === 'progress') {
        await this.showProgress();
      } else if (choice === 'practice') {
        await this.loadModule('practice');
      } else {
        await this.loadModule(choice);
      }
    }
  }
}

// Launch the platform
const platform = new AlgorithmsLearningPlatform();
platform.run().catch(console.error);