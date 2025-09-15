import chalk from 'chalk';
import inquirer from 'inquirer';
import Table from 'cli-table3';

class ArraysModule {
  constructor() {
    this.bookshelf = [];
    this.operations = 0;
  }

  async run(platform) {
    console.clear();
    console.log(chalk.cyan.bold(`
╔════════════════════════════════════════════════════════════════╗
║                      ARRAYS MODULE                            ║
║              Organizing Books on a Shelf                      ║
╚════════════════════════════════════════════════════════════════╝
    `));

    await this.introduction();
    await this.interactiveBookshelf();
    await this.complexityLesson();
    await this.realWorldApplications();
    await this.challenge();
    await platform.pause();
  }

  async introduction() {
    console.log(chalk.yellow(`
📚 Welcome to Arrays - Your First Data Structure!

Imagine a bookshelf with numbered slots:
  [0] [1] [2] [3] [4] [5] [6] [7] [8] [9]

Each slot can hold exactly one book, and you can:
- Put a book in any empty slot instantly
- Find a book if you know its slot number
- Remove a book from any slot
- Count how many books you have

This is exactly how arrays work in programming!
    `));
    
    await this.pause();
  }

  async interactiveBookshelf() {
    console.log(chalk.green.bold('\n🎮 INTERACTIVE BOOKSHELF\n'));
    console.log(chalk.yellow('Let\'s manage your digital bookshelf!\n'));

    this.bookshelf = new Array(10).fill(null);
    let exploring = true;

    while (exploring) {
      this.displayBookshelf();
      
      const { action } = await inquirer.prompt([{
        type: 'list',
        name: 'action',
        message: 'What would you like to do?',
        choices: [
          { name: '📖 Add a book', value: 'add' },
          { name: '🔍 Find a book', value: 'find' },
          { name: '🗑️  Remove a book', value: 'remove' },
          { name: '📊 See statistics', value: 'stats' },
          { name: '✅ Continue to lesson', value: 'done' }
        ]
      }]);

      switch (action) {
        case 'add':
          await this.addBook();
          break;
        case 'find':
          await this.findBook();
          break;
        case 'remove':
          await this.removeBook();
          break;
        case 'stats':
          this.showStats();
          break;
        case 'done':
          exploring = false;
          break;
      }
    }
  }

  displayBookshelf() {
    console.clear();
    console.log(chalk.cyan('\n📚 Your Bookshelf:\n'));
    
    const table = new Table({
      head: ['Slot', 'Book'],
      colWidths: [8, 30],
      style: { head: ['cyan'] }
    });

    this.bookshelf.forEach((book, index) => {
      table.push([
        chalk.yellow(`[${index}]`),
        book || chalk.dim('(empty)')
      ]);
    });

    console.log(table.toString());
    console.log(chalk.dim(`Operations performed: ${this.operations}`));
  }

  async addBook() {
    const emptySlots = this.bookshelf
      .map((book, i) => book === null ? i : null)
      .filter(i => i !== null);

    if (emptySlots.length === 0) {
      console.log(chalk.red('\n📚 Bookshelf is full!'));
      await this.pause();
      return;
    }

    const { title } = await inquirer.prompt([{
      type: 'input',
      name: 'title',
      message: 'Enter book title:',
      validate: input => input.length > 0 || 'Please enter a title'
    }]);

    const { slot } = await inquirer.prompt([{
      type: 'list',
      name: 'slot',
      message: 'Choose a slot:',
      choices: emptySlots.map(s => ({
        name: `Slot [${s}]`,
        value: s
      }))
    }]);

    this.bookshelf[slot] = title;
    this.operations++;
    
    console.log(chalk.green(`\n✅ Added "${title}" to slot [${slot}]`));
    console.log(chalk.yellow(`This operation took O(1) - instant access!`));
    await this.pause();
  }

  async findBook() {
    const filledSlots = this.bookshelf
      .map((book, i) => book !== null ? i : null)
      .filter(i => i !== null);

    if (filledSlots.length === 0) {
      console.log(chalk.red('\n📚 Bookshelf is empty!'));
      await this.pause();
      return;
    }

    const { method } = await inquirer.prompt([{
      type: 'list',
      name: 'method',
      message: 'How do you want to find the book?',
      choices: [
        { name: 'I know the slot number', value: 'index' },
        { name: 'Search by title', value: 'search' }
      ]
    }]);

    if (method === 'index') {
      const { slot } = await inquirer.prompt([{
        type: 'number',
        name: 'slot',
        message: 'Enter slot number (0-9):',
        validate: input => input >= 0 && input <= 9 || 'Enter 0-9'
      }]);

      this.operations++;
      const book = this.bookshelf[slot];
      
      if (book) {
        console.log(chalk.green(`\n✅ Found: "${book}" in slot [${slot}]`));
        console.log(chalk.yellow(`O(1) - Instant access with index!`));
      } else {
        console.log(chalk.yellow(`\n📭 Slot [${slot}] is empty`));
      }
    } else {
      const { query } = await inquirer.prompt([{
        type: 'input',
        name: 'query',
        message: 'Enter title to search:'
      }]);

      console.log(chalk.dim('\nSearching...'));
      let found = false;
      
      for (let i = 0; i < this.bookshelf.length; i++) {
        this.operations++;
        if (this.bookshelf[i]?.toLowerCase().includes(query.toLowerCase())) {
          console.log(chalk.green(`\n✅ Found: "${this.bookshelf[i]}" in slot [${i}]`));
          console.log(chalk.yellow(`O(n) - Had to check ${i + 1} slots!`));
          found = true;
          break;
        }
      }
      
      if (!found) {
        console.log(chalk.red('\n❌ Book not found'));
        console.log(chalk.yellow(`O(n) - Checked all ${this.bookshelf.length} slots!`));
      }
    }
    
    await this.pause();
  }

  async removeBook() {
    const filledSlots = this.bookshelf
      .map((book, i) => book !== null ? { book, i } : null)
      .filter(item => item !== null);

    if (filledSlots.length === 0) {
      console.log(chalk.red('\n📚 No books to remove!'));
      await this.pause();
      return;
    }

    const { slot } = await inquirer.prompt([{
      type: 'list',
      name: 'slot',
      message: 'Choose book to remove:',
      choices: filledSlots.map(({ book, i }) => ({
        name: `[${i}] ${book}`,
        value: i
      }))
    }]);

    const removed = this.bookshelf[slot];
    this.bookshelf[slot] = null;
    this.operations++;
    
    console.log(chalk.green(`\n✅ Removed "${removed}" from slot [${slot}]`));
    console.log(chalk.yellow(`O(1) - Instant removal by index!`));
    await this.pause();
  }

  showStats() {
    const filled = this.bookshelf.filter(b => b !== null).length;
    const empty = this.bookshelf.length - filled;
    
    console.log(chalk.cyan.bold('\n📊 BOOKSHELF STATISTICS\n'));
    console.log(chalk.white(`Total slots: ${this.bookshelf.length}`));
    console.log(chalk.green(`Books stored: ${filled}`));
    console.log(chalk.yellow(`Empty slots: ${empty}`));
    console.log(chalk.magenta(`Operations performed: ${this.operations}`));
    console.log(chalk.blue(`Efficiency: ${(filled / this.operations * 100).toFixed(1)}%`));
  }

  async complexityLesson() {
    console.clear();
    console.log(chalk.cyan.bold('\n⚡ UNDERSTANDING ARRAY EFFICIENCY\n'));

    const table = new Table({
      head: ['Operation', 'Speed', 'Why?'],
      colWidths: [20, 15, 40],
      style: { head: ['cyan'] },
      wordWrap: true
    });

    table.push(
      ['Access by index', chalk.green('O(1) Instant'), 'Direct address, like knowing the exact shelf slot'],
      ['Add to end', chalk.green('O(1) Instant'), 'Just put it in the next empty slot'],
      ['Search by value', chalk.yellow('O(n) Linear'), 'Must check each slot until found'],
      ['Insert middle', chalk.red('O(n) Linear'), 'Must shift all books after that point'],
      ['Remove middle', chalk.red('O(n) Linear'), 'Must shift books to fill the gap']
    );

    console.log(table.toString());
    
    console.log(chalk.yellow(`
💡 Key Insight: Arrays are PERFECT when you:
   - Know the position (index) of items
   - Need fast access to any item
   - Don't insert/remove from middle often
   
   Like apartment numbers - instant if you know the number!
    `));
    
    await this.pause();
  }

  async realWorldApplications() {
    console.clear();
    console.log(chalk.cyan.bold('\n🌍 ARRAYS IN YOUR DAILY LIFE\n'));

    const examples = [
      {
        title: '📱 Your Phone Contacts',
        description: 'Alphabetically indexed for quick jumps to letters'
      },
      {
        title: '📅 Calendar Days',
        description: 'Days 1-31 in order, instant access to any date'
      },
      {
        title: '🎮 Game High Scores',
        description: 'Top 10 scores in ranked positions'
      },
      {
        title: '🎵 Music Playlist',
        description: 'Songs in order, jump to track #7 instantly'
      },
      {
        title: '📊 Excel Spreadsheet',
        description: 'Cells addressed by row and column numbers'
      }
    ];

    examples.forEach(({ title, description }) => {
      console.log(chalk.green(`\n${title}`));
      console.log(chalk.white(`  ${description}`));
    });

    console.log(chalk.yellow(`
Every time you see numbered or ordered items with instant access,
you're experiencing the power of arrays!
    `));
    
    await this.pause();
  }

  async challenge() {
    console.clear();
    console.log(chalk.green.bold('\n🎯 CHALLENGE: Library Reorganization\n'));
    
    console.log(chalk.yellow(`
The library has 1,000 books in random order.
You need to help visitors find books quickly.

Which strategy would be MOST efficient for repeated searches?
    `));

    const { answer } = await inquirer.prompt([{
      type: 'list',
      name: 'answer',
      message: 'Choose your approach:',
      choices: [
        'Keep them random, search through all each time',
        'Sort once by title, then use alphabetical positions',
        'Memorize where each book is',
        'Create a separate list for each genre'
      ]
    }]);

    const correct = 'Sort once by title, then use alphabetical positions';
    
    if (answer === correct) {
      console.log(chalk.green.bold('\n🎉 Perfect! You understand array optimization!'));
      console.log(chalk.white(`
Sorting once (O(n log n)) then using binary search (O(log n))
is much better than searching randomly (O(n)) every time!

This is why dictionaries, phone books, and databases sort their data.
      `));
    } else {
      console.log(chalk.yellow('\n🤔 Good try! Here\'s the optimal solution:'));
      console.log(chalk.white(`
Sorting once by title is best because:
- One-time cost to sort: O(n log n)
- Every search after: O(log n) with binary search
- Much faster than O(n) random searches!

This is how real databases and search engines work efficiently.
      `));
    }
  }

  async pause() {
    await inquirer.prompt([{
      type: 'input',
      name: 'continue',
      message: chalk.dim('\nPress Enter to continue...')
    }]);
  }
}

export default new ArraysModule();