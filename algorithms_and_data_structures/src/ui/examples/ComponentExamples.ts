/**
 * Component Usage Examples
 * Demonstrates how to use each UI component
 */

import * as terminalKit from 'terminal-kit';
import {
  // Input Components
  createTextInput,
  createSelectInput,
  createMultiSelect,
  createConfirmInput,
  confirmDelete,
  
  // Display Components
  createTable,
  createProgressBar,
  createSpinner,
  withSpinner,
  createAlert,
  createSuccessAlert,
  createErrorAlert,
  
  // Layout Components
  createBox,
  createInfoBox,
  createGrid,
  createDataGrid,
  createDivider,
  createSectionDivider,
  
  // Types
  SelectOption,
  TableData,
  GridCell
} from '../components';

const terminal = terminalKit.terminal;

export class ComponentExamples {
  
  /**
   * TextInput Examples
   */
  static async textInputExamples(): Promise<void> {
    terminal.clear();
    terminal.cyan('=== TextInput Examples ===\n\n');

    // Basic text input
    terminal.yellow('Basic Text Input:\n');
    const basicInput = createTextInput(terminal, {
      placeholder: 'Enter your name...',
      required: true
    });
    
    try {
      const name = await basicInput.input();
      terminal.green(`Hello, ${name}!\n\n`);
    } catch (error) {
      terminal.red('Input cancelled\n\n');
    }

    // Password input with validation
    terminal.yellow('Password Input with Validation:\n');
    const passwordInput = createTextInput(terminal, {
      placeholder: 'Enter password...',
      mask: true,
      validation: [
        {
          test: (value) => value.length >= 8,
          message: 'Password must be at least 8 characters'
        },
        {
          test: (value) => /[A-Z]/.test(value),
          message: 'Password must contain an uppercase letter'
        },
        {
          test: (value) => /\d/.test(value),
          message: 'Password must contain a number'
        }
      ]
    });

    try {
      const password = await passwordInput.input();
      terminal.green('Password accepted!\n\n');
    } catch (error) {
      terminal.red('Password validation failed\n\n');
    }
  }

  /**
   * SelectInput Examples
   */
  static async selectInputExamples(): Promise<void> {
    terminal.yellow('=== SelectInput Examples ===\n\n');

    const options: SelectOption<string>[] = [
      { label: 'JavaScript', value: 'js', icon: '🟨' },
      { label: 'TypeScript', value: 'ts', icon: '🔷', description: 'Strongly typed JavaScript' },
      { label: 'Python', value: 'py', icon: '🐍' },
      { label: 'Rust', value: 'rs', icon: '🦀', description: 'Systems programming language' },
      { label: 'Go', value: 'go', icon: '🐹' }
    ];

    const selectInput = createSelectInput(terminal, {
      options,
      placeholder: 'Choose your favorite language...',
      searchable: true
    });

    try {
      const language = await selectInput.select();
      terminal.green(`You selected: ${language}\n\n`);
    } catch (error) {
      terminal.red('Selection cancelled\n\n');
    }
  }

  /**
   * MultiSelect Examples
   */
  static async multiSelectExamples(): Promise<void> {
    terminal.yellow('=== MultiSelect Examples ===\n\n');

    const features: SelectOption<string>[] = [
      { label: 'Syntax Highlighting', value: 'syntax' },
      { label: 'Code Completion', value: 'completion' },
      { label: 'Debugging', value: 'debugging' },
      { label: 'Git Integration', value: 'git' },
      { label: 'Extensions', value: 'extensions' },
      { label: 'Terminal Integration', value: 'terminal' }
    ];

    const multiSelect = createMultiSelect(terminal, {
      options: features,
      minSelection: 1,
      maxSelection: 4,
      selectAll: true,
      searchable: true
    });

    try {
      const selectedFeatures = await multiSelect.select();
      terminal.green(`Selected features: ${selectedFeatures.join(', ')}\n\n`);
    } catch (error) {
      terminal.red('Selection cancelled\n\n');
    }
  }

  /**
   * ConfirmInput Examples
   */
  static async confirmInputExamples(): Promise<void> {
    terminal.yellow('=== ConfirmInput Examples ===\n\n');

    // Basic confirmation
    const confirmed = await createConfirmInput(terminal, {
      message: 'Do you want to continue?',
      defaultValue: true
    }).confirm();

    if (confirmed) {
      terminal.green('Continuing...\n');
    } else {
      terminal.red('Cancelled\n');
    }

    // Danger confirmation
    const deleteConfirmed = await confirmDelete(terminal, 'important-file.txt');
    
    if (deleteConfirmed) {
      terminal.red('File would be deleted!\n');
    } else {
      terminal.green('File is safe\n');
    }

    terminal('\n');
  }

  /**
   * Table Examples
   */
  static async tableExamples(): Promise<void> {
    terminal.yellow('=== Table Examples ===\n\n');

    const tableData: TableData<any> = {
      columns: [
        { key: 'name', label: 'Name', sortable: true },
        { key: 'language', label: 'Language', sortable: true },
        { key: 'stars', label: 'Stars', align: 'right', sortable: true },
        { key: 'description', label: 'Description' }
      ],
      rows: [
        { name: 'Vue', language: 'JavaScript', stars: 207000, description: 'Progressive framework' },
        { name: 'React', language: 'JavaScript', stars: 225000, description: 'UI library' },
        { name: 'Angular', language: 'TypeScript', stars: 93000, description: 'Full framework' },
        { name: 'Svelte', language: 'JavaScript', stars: 78000, description: 'Compile-time framework' }
      ]
    };

    const table = createTable(terminal, {
      data: tableData,
      selectable: true,
      sortable: true,
      pageSize: 10
    });

    table.render();
    terminal('\n\nPress any key to continue...');
    await terminal.inputField();
    terminal('\n\n');
  }

  /**
   * ProgressBar Examples
   */
  static async progressBarExamples(): Promise<void> {
    terminal.yellow('=== ProgressBar Examples ===\n\n');

    // Animated progress bar
    terminal.cyan('Animated Progress Bar:\n');
    const progressBar = createProgressBar(terminal, {
      value: 0,
      max: 100,
      width: 50,
      label: 'Processing files...',
      showPercentage: true,
      showETA: true,
      animate: true,
      style: 'bar'
    });

    // Simulate progress
    for (let i = 0; i <= 100; i += 5) {
      progressBar.setValue(i);
      await new Promise(resolve => setTimeout(resolve, 100));
    }

    terminal('\n\n');

    // Different styles
    const styles: Array<'bar' | 'dots' | 'blocks' | 'gradient' | 'minimal'> = 
      ['bar', 'dots', 'blocks', 'gradient', 'minimal'];
    
    for (const style of styles) {
      terminal.cyan(`${style} style:\n`);
      const styleBar = createProgressBar(terminal, {
        value: 75,
        max: 100,
        width: 40,
        style,
        showPercentage: true
      });
      styleBar.render();
      terminal('\n');
    }

    terminal('\n');
  }

  /**
   * Spinner Examples
   */
  static async spinnerExamples(): Promise<void> {
    terminal.yellow('=== Spinner Examples ===\n\n');

    // Basic spinner
    const spinner = createSpinner(terminal, {
      text: 'Loading data...',
      style: 'dots'
    });

    spinner.start();
    await new Promise(resolve => setTimeout(resolve, 2000));
    spinner.succeed('Data loaded successfully!');

    // Using withSpinner utility
    await withSpinner(terminal, async () => {
      await new Promise(resolve => setTimeout(resolve, 1500));
    }, { text: 'Processing...', style: 'clock' });

    terminal('\n');
  }

  /**
   * Alert Examples
   */
  static async alertExamples(): Promise<void> {
    terminal.yellow('=== Alert Examples ===\n\n');

    // Success alert
    const successAlert = createSuccessAlert(terminal, 'Operation completed successfully!', {
      duration: 2000,
      showTimestamp: true
    });
    successAlert.show();
    await new Promise(resolve => setTimeout(resolve, 2500));

    // Warning alert
    const warningAlert = createAlert(terminal, {
      type: 'warning',
      message: 'This action cannot be undone. Please review before proceeding.',
      showIcon: true,
      borderStyle: 'double',
      width: 60
    });
    warningAlert.show();
    await new Promise(resolve => setTimeout(resolve, 3000));
    warningAlert.hide();

    // Error alert
    const errorAlert = createErrorAlert(terminal, 'Connection failed: Unable to reach server', {
      dismissible: true,
      multiline: true,
      persistent: true
    });
    errorAlert.show();
    await new Promise(resolve => setTimeout(resolve, 2000));
    errorAlert.dismiss();

    terminal('\n');
  }

  /**
   * Box Examples
   */
  static async boxExamples(): Promise<void> {
    terminal.yellow('=== Box Examples ===\n\n');

    // Basic box
    const basicBox = createBox(terminal, {
      title: 'System Information',
      content: 'Node.js: v18.17.0\nOS: Windows 11\nMemory: 16GB\nCPU: Intel i7',
      width: 40,
      height: 8,
      borderStyle: 'rounded',
      padding: 1
    });
    basicBox.render();

    terminal('\n');

    // Info box with different styling
    const infoBox = createInfoBox(terminal, 
      'Tips & Tricks', 
      'Use Ctrl+C to cancel operations\nUse Tab to autocomplete\nUse arrow keys for navigation', 
      {
        width: 50,
        height: 6,
        shadow: true,
        titleAlign: 'center'
      }
    );
    infoBox.render();

    terminal('\n\n');
  }

  /**
   * Grid Examples
   */
  static async gridExamples(): Promise<void> {
    terminal.yellow('=== Grid Examples ===\n\n');

    // Data grid
    const data = [
      ['Name', 'Age', 'City'],
      ['Alice', '28', 'New York'],
      ['Bob', '32', 'San Francisco'],
      ['Charlie', '25', 'Chicago']
    ];

    const dataGrid = createDataGrid(terminal, data.slice(1), data[0], {
      borderStyle: 'single',
      showRowNumbers: true
    });
    dataGrid.render();

    terminal('\n');

    // Custom grid with styling
    const customGrid = createGrid(terminal, {
      columns: 3,
      rows: 2,
      borderStyle: 'double',
      gap: 1
    });

    customGrid.setCell(0, 0, { 
      content: 'Header 1', 
      style: { color: 'primary', bold: true } 
    });
    customGrid.setCell(0, 1, { 
      content: 'Header 2', 
      style: { color: 'primary', bold: true } 
    });
    customGrid.setCell(0, 2, { 
      content: 'Header 3', 
      style: { color: 'primary', bold: true } 
    });
    
    customGrid.setCell(1, 0, { content: 'Data A' });
    customGrid.setCell(1, 1, { content: 'Data B' });
    customGrid.setCell(1, 2, { content: 'Data C' });

    customGrid.render();

    terminal('\n\n');
  }

  /**
   * Divider Examples
   */
  static async dividerExamples(): Promise<void> {
    terminal.yellow('=== Divider Examples ===\n\n');

    // Section dividers
    createSectionDivider(terminal, 'Configuration').render();
    terminal('App settings and preferences\n');
    
    createSectionDivider(terminal, 'Data Processing').render();
    terminal('File operations and transformations\n');

    // Different styles
    createDivider(terminal, { 
      style: 'double', 
      width: 50, 
      color: 'accent' 
    }).render();
    
    createDivider(terminal, { 
      text: 'OR', 
      style: 'dashed', 
      width: 30, 
      align: 'center' 
    }).render();
    
    createDivider(terminal, { 
      style: 'dotted', 
      width: 40, 
      margin: { top: 1, bottom: 1 } 
    }).render();

    terminal('\n');
  }

  /**
   * Run all examples
   */
  static async runAllExamples(): Promise<void> {
    try {
      await this.textInputExamples();
      await this.selectInputExamples();
      await this.multiSelectExamples();
      await this.confirmInputExamples();
      await this.tableExamples();
      await this.progressBarExamples();
      await this.spinnerExamples();
      await this.alertExamples();
      await this.boxExamples();
      await this.gridExamples();
      await this.dividerExamples();
      
      terminal.green('\n🎉 All component examples completed!\n');
    } catch (error) {
      terminal.red(`\n❌ Example failed: ${error}\n`);
    }
  }
}

// Export for CLI usage
export async function runComponentExamples(): Promise<void> {
  await ComponentExamples.runAllExamples();
}

// Individual example runners
export const examples = {
  textInput: ComponentExamples.textInputExamples,
  select: ComponentExamples.selectInputExamples,
  multiSelect: ComponentExamples.multiSelectExamples,
  confirm: ComponentExamples.confirmInputExamples,
  table: ComponentExamples.tableExamples,
  progress: ComponentExamples.progressBarExamples,
  spinner: ComponentExamples.spinnerExamples,
  alert: ComponentExamples.alertExamples,
  box: ComponentExamples.boxExamples,
  grid: ComponentExamples.gridExamples,
  divider: ComponentExamples.dividerExamples
};

// Demo CLI script
if (require.main === module) {
  const args = process.argv.slice(2);
  const exampleName = args[0];
  
  if (exampleName && exampleName in examples) {
    examples[exampleName as keyof typeof examples]();
  } else {
    ComponentExamples.runAllExamples();
  }
}