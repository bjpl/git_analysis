import chalk from 'chalk';
import inquirer from 'inquirer';
import Table from 'cli-table3';

class FoundationModule {
  constructor() {
    this.concepts = [
      {
        title: 'What Are Algorithms?',
        analogy: 'Recipes for solving problems',
        explanation: `
Imagine you're making your favorite sandwich. You follow steps:
1. Get bread
2. Add ingredients in order
3. Close sandwich
4. Cut if desired

An algorithm is just like this recipe - a step-by-step process
to solve a problem or complete a task. Every app on your phone,
every website you visit, uses thousands of these "recipes".`,
        realWorld: 'GPS navigation finding the fastest route home'
      },
      {
        title: 'What Are Data Structures?',
        analogy: 'Different ways to organize things',
        explanation: `
Think about organizing your closet. You might:
- Hang shirts on hangers (like an Array)
- Stack folded clothes (like a Stack)
- Queue shoes in a line (like a Queue)
- Create sections by type (like a Tree)

Data structures are just different ways to organize information
so computers can use it efficiently.`,
        realWorld: 'Your phone organizing contacts alphabetically'
      },
      {
        title: 'Why Efficiency Matters',
        analogy: 'Finding a book in a library',
        explanation: `
Imagine finding a specific book:
- Random pile: Check every book (slow!)
- Alphabetical shelves: Go to the right section (faster!)
- Digital catalog: Type and find instantly (fastest!)

In programming, efficiency determines if your app responds
in milliseconds or makes users wait. The right algorithm
can be the difference between instant and impossible.`,
        realWorld: 'Instagram showing your feed instantly vs waiting minutes'
      },
      {
        title: 'Pattern Recognition',
        analogy: 'Recognizing faces in a crowd',
        explanation: `
Your brain recognizes patterns constantly:
- Friend's face in a crowd
- Your car in a parking lot
- Favorite song's first notes

Algorithms use patterns too. Once you learn to recognize
common patterns, you'll see them everywhere in technology
and can apply solutions that already exist.`,
        realWorld: 'Spotify recognizing your music taste and suggesting songs'
      }
    ];
  }

  async run(platform) {
    console.clear();
    console.log(chalk.cyan.bold(`
╔════════════════════════════════════════════════════════════════╗
║                    FOUNDATION MODULE                          ║
║              Building Your Mental Models                      ║
╚════════════════════════════════════════════════════════════════╝
    `));

    await this.showIntroduction();
    
    for (let i = 0; i < this.concepts.length; i++) {
      await this.presentConcept(this.concepts[i], i + 1);
      if (i < this.concepts.length - 1) {
        const { continue: shouldContinue } = await inquirer.prompt([{
          type: 'confirm',
          name: 'continue',
          message: 'Ready for the next concept?',
          default: true
        }]);
        if (!shouldContinue) break;
      }
    }

    await this.showSummary();
    await this.interactiveExercise();
    await platform.pause();
  }

  async showIntroduction() {
    console.log(chalk.yellow(`
Welcome to the Foundation Module!

We'll explore algorithms and data structures through familiar,
everyday experiences. No math or programming required yet -
just your natural problem-solving abilities.

Let's build intuition before implementation.
    `));
    
    await this.pause();
  }

  async presentConcept(concept, number) {
    console.clear();
    console.log(chalk.cyan(`\n━━━ Concept ${number}/4 ━━━`));
    console.log(chalk.green.bold(`\n${concept.title}`));
    console.log(chalk.yellow(`\n📖 Everyday Analogy: ${concept.analogy}`));
    console.log(chalk.white(concept.explanation));
    console.log(chalk.magenta(`\n💡 Real-World Example: ${concept.realWorld}\n`));
  }

  async showSummary() {
    console.clear();
    console.log(chalk.cyan.bold('\n🎯 KEY TAKEAWAYS\n'));

    const table = new Table({
      head: ['Concept', 'Remember This'],
      colWidths: [25, 45],
      style: { head: ['cyan'] },
      wordWrap: true
    });

    table.push(
      ['Algorithms', 'Step-by-step recipes for solving problems'],
      ['Data Structures', 'Different ways to organize information'],
      ['Efficiency', 'The right approach saves massive time'],
      ['Patterns', 'Recognize once, apply everywhere']
    );

    console.log(table.toString());
  }

  async interactiveExercise() {
    console.log(chalk.green.bold('\n🎮 INTERACTIVE EXERCISE\n'));
    console.log(chalk.yellow('Let\'s apply what you learned!\n'));

    const scenario = {
      question: 'You need to organize 1000 student records for quick access by name. Which approach would be MOST efficient?',
      choices: [
        'Keep them in a random pile and search through all when needed',
        'Sort them alphabetically once, then use that order to find names quickly',
        'Create a new pile for each letter of the alphabet',
        'Remember where you put each one'
      ],
      correct: 1,
      explanation: `Sorting alphabetically once (Option 2) is most efficient!

Here's why:
- Random pile: You'd check ~500 records on average (very slow!)
- Alphabetical: You can jump to the right section (much faster!)
- Letter piles: Good idea, but sorting within letters is even better
- Memorizing: Impossible for humans, impractical for computers

This is why phone contacts and dictionaries use alphabetical order!`
    };

    const { answer } = await inquirer.prompt([{
      type: 'list',
      name: 'answer',
      message: scenario.question,
      choices: scenario.choices
    }]);

    const selectedIndex = scenario.choices.indexOf(answer);
    
    if (selectedIndex === scenario.correct) {
      console.log(chalk.green.bold('\n✅ Excellent! You\'re thinking algorithmically!'));
    } else {
      console.log(chalk.yellow('\n🤔 Not quite, but great attempt!'));
    }
    
    console.log(chalk.white(scenario.explanation));
  }

  async pause() {
    await inquirer.prompt([{
      type: 'input',
      name: 'continue',
      message: chalk.dim('\nPress Enter to continue...')
    }]);
  }
}

export default new FoundationModule();