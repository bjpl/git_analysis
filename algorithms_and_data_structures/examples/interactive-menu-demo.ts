#!/usr/bin/env ts-node

/**
 * Interactive Menu System Demonstration
 * 
 * This comprehensive demo showcases:
 * - Main menu with multiple sections
 * - Nested submenus (3+ levels deep)
 * - Search functionality demonstration
 * - Keyboard shortcut showcase
 * - Theme switching live demo
 * - Performance stress test with 100+ items
 * - Animation showcase
 */

import * as readline from 'readline';
import { EventEmitter } from 'events';

// Color themes
const themes = {
  default: {
    primary: '\x1b[36m',      // Cyan
    secondary: '\x1b[33m',    // Yellow
    success: '\x1b[32m',      // Green
    error: '\x1b[31m',        // Red
    info: '\x1b[34m',         // Blue
    reset: '\x1b[0m',         // Reset
    dim: '\x1b[2m',           // Dim
    bold: '\x1b[1m',          // Bold
    underline: '\x1b[4m',     // Underline
  },
  dark: {
    primary: '\x1b[95m',      // Light Magenta
    secondary: '\x1b[93m',    // Light Yellow
    success: '\x1b[92m',      // Light Green
    error: '\x1b[91m',        // Light Red
    info: '\x1b[94m',         // Light Blue
    reset: '\x1b[0m',
    dim: '\x1b[2m',
    bold: '\x1b[1m',
    underline: '\x1b[4m',
  },
  light: {
    primary: '\x1b[35m',      // Magenta
    secondary: '\x1b[33m',    // Yellow
    success: '\x1b[32m',      // Green
    error: '\x1b[31m',        // Red
    info: '\x1b[34m',         // Blue
    reset: '\x1b[0m',
    dim: '\x1b[2m',
    bold: '\x1b[1m',
    underline: '\x1b[4m',
  }
};

interface MenuOption {
  id: string;
  label: string;
  description?: string;
  shortcut?: string;
  action?: () => Promise<void> | void;
  submenu?: MenuOption[];
  hidden?: boolean;
  disabled?: boolean;
  icon?: string;
  category?: string;
}

interface MenuConfig {
  title: string;
  subtitle?: string;
  options: MenuOption[];
  searchable?: boolean;
  showShortcuts?: boolean;
  showIcons?: boolean;
  maxDisplayItems?: number;
  animationsEnabled?: boolean;
}

class InteractiveMenu extends EventEmitter {
  private rl: readline.Interface;
  private currentTheme: string = 'default';
  private searchTerm: string = '';
  private currentLevel: MenuOption[][] = [];
  private animationsEnabled: boolean = true;
  private performanceMode: boolean = false;

  constructor() {
    super();
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
    });

    this.setupKeyboardHandlers();
  }

  private get theme() {
    return themes[this.currentTheme as keyof typeof themes] || themes.default;
  }

  private setupKeyboardHandlers(): void {
    process.stdin.setRawMode(true);
    process.stdin.resume();
    process.stdin.setEncoding('utf8');

    process.stdin.on('data', (key: string) => {
      const code = key.charCodeAt(0);
      
      // Handle special keys
      if (key === '\u0003') { // Ctrl+C
        this.exit();
      } else if (key === '\u001b') { // ESC
        this.goBack();
      } else if (key === '\r' || key === '\n') { // Enter
        this.selectCurrentOption();
      } else if (key === '\u007f') { // Backspace
        this.handleBackspace();
      } else if (key.startsWith('\u001b[')) { // Arrow keys
        this.handleArrowKeys(key);
      } else if (code >= 32 && code <= 126) { // Printable characters
        this.handleSearch(key);
      }
    });
  }

  private handleArrowKeys(key: string): void {
    // Arrow key handling would be implemented here
    // For demo purposes, we'll use number selection
  }

  private handleSearch(char: string): void {
    this.searchTerm += char;
    this.redrawMenu();
  }

  private handleBackspace(): void {
    if (this.searchTerm.length > 0) {
      this.searchTerm = this.searchTerm.slice(0, -1);
      this.redrawMenu();
    }
  }

  private selectCurrentOption(): void {
    // Implementation for option selection
  }

  private goBack(): void {
    if (this.currentLevel.length > 1) {
      this.currentLevel.pop();
      this.redrawMenu();
    } else if (this.searchTerm) {
      this.searchTerm = '';
      this.redrawMenu();
    }
  }

  private exit(): void {
    this.clearScreen();
    console.log(`${this.theme.success}Thank you for using the Interactive Menu Demo!${this.theme.reset}`);
    process.exit(0);
  }

  private clearScreen(): void {
    process.stdout.write('\x1Bc');
  }

  private redrawMenu(): void {
    this.clearScreen();
    const currentMenu = this.currentLevel[this.currentLevel.length - 1] || this.getMainMenu().options;
    this.displayMenu({
      title: 'Interactive Menu Demo',
      subtitle: 'Navigate with numbers, search by typing, ESC to go back',
      options: currentMenu,
      searchable: true,
      showShortcuts: true,
      showIcons: true,
      animationsEnabled: this.animationsEnabled
    });
  }

  private displayMenu(config: MenuConfig): void {
    const { theme } = this;
    
    // Header
    console.log(`${theme.bold}${theme.primary}╔${'═'.repeat(60)}╗${theme.reset}`);
    console.log(`${theme.bold}${theme.primary}║${' '.repeat(20)}${config.title}${' '.repeat(20)}║${theme.reset}`);
    if (config.subtitle) {
      console.log(`${theme.primary}║${theme.dim}${config.subtitle.padEnd(60)}${theme.reset}${theme.primary}║${theme.reset}`);
    }
    console.log(`${theme.primary}╠${'═'.repeat(60)}╣${theme.reset}`);

    // Search bar
    if (config.searchable && this.searchTerm) {
      console.log(`${theme.primary}║ ${theme.secondary}Search: ${theme.bold}${this.searchTerm}${theme.reset}${' '.repeat(60 - this.searchTerm.length - 9)}${theme.primary}║${theme.reset}`);
      console.log(`${theme.primary}╠${'═'.repeat(60)}╣${theme.reset}`);
    }

    // Filter options based on search
    let filteredOptions = config.options.filter(option => {
      if (option.hidden) return false;
      if (!this.searchTerm) return true;
      return option.label.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
             (option.description && option.description.toLowerCase().includes(this.searchTerm.toLowerCase()));
    });

    // Display options
    filteredOptions.forEach((option, index) => {
      const icon = config.showIcons && option.icon ? `${option.icon} ` : '';
      const shortcut = config.showShortcuts && option.shortcut ? ` (${option.shortcut})` : '';
      const disabled = option.disabled ? theme.dim : '';
      const submenuIndicator = option.submenu ? ' ►' : '';
      
      let line = `${theme.primary}║ ${disabled}${index + 1}. ${icon}${option.label}${shortcut}${submenuIndicator}${theme.reset}`;
      const padding = 60 - this.stripAnsi(line).length + 1;
      line += ' '.repeat(Math.max(0, padding)) + `${theme.primary}║${theme.reset}`;
      
      console.log(line);
      
      if (option.description && !this.performanceMode) {
        const descLine = `${theme.primary}║    ${theme.dim}${option.description}${theme.reset}`;
        const descPadding = 60 - this.stripAnsi(descLine).length + 1;
        console.log(descLine + ' '.repeat(Math.max(0, descPadding)) + `${theme.primary}║${theme.reset}`);
      }
    });

    console.log(`${theme.primary}╚${'═'.repeat(60)}╝${theme.reset}`);

    // Status bar
    const breadcrumb = this.getBreadcrumb();
    const status = `Level: ${this.currentLevel.length} | Theme: ${this.currentTheme} | ${breadcrumb}`;
    console.log(`${theme.dim}${status}${theme.reset}`);
    console.log('');
  }

  private stripAnsi(str: string): string {
    return str.replace(/\x1b\[[0-9;]*m/g, '');
  }

  private getBreadcrumb(): string {
    return this.currentLevel.length > 0 ? 'Menu > Submenu' : 'Main Menu';
  }

  private async animateText(text: string, delay: number = 50): Promise<void> {
    if (!this.animationsEnabled) {
      console.log(text);
      return;
    }

    for (const char of text) {
      process.stdout.write(char);
      await this.sleep(delay);
    }
    console.log('');
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private getMainMenu(): MenuConfig {
    return {
      title: 'Interactive Menu System Demo',
      subtitle: 'Comprehensive showcase of menu capabilities',
      options: [
        {
          id: 'basic-demo',
          label: 'Basic Menu Operations',
          description: 'Simple navigation and selection',
          icon: '📋',
          shortcut: 'Ctrl+B',
          submenu: this.getBasicDemoSubmenu()
        },
        {
          id: 'advanced-demo',
          label: 'Advanced Features',
          description: 'Search, themes, and animations',
          icon: '⚡',
          shortcut: 'Ctrl+A',
          submenu: this.getAdvancedDemoSubmenu()
        },
        {
          id: 'nested-demo',
          label: 'Deep Nested Menus',
          description: 'Multi-level navigation (3+ levels)',
          icon: '🏗️',
          shortcut: 'Ctrl+N',
          submenu: this.getNestedDemoSubmenu()
        },
        {
          id: 'performance-test',
          label: 'Performance Stress Test',
          description: 'Test with 100+ menu items',
          icon: '🚀',
          shortcut: 'Ctrl+P',
          action: () => this.performanceStressTest()
        },
        {
          id: 'search-demo',
          label: 'Search Functionality',
          description: 'Live search and filtering',
          icon: '🔍',
          shortcut: 'Ctrl+S',
          action: () => this.searchDemo()
        },
        {
          id: 'theme-switcher',
          label: 'Theme Switcher',
          description: 'Switch between color themes',
          icon: '🎨',
          shortcut: 'Ctrl+T',
          submenu: this.getThemeSubmenu()
        },
        {
          id: 'animation-demo',
          label: 'Animation Showcase',
          description: 'Text animations and transitions',
          icon: '✨',
          shortcut: 'Ctrl+M',
          action: () => this.animationDemo()
        },
        {
          id: 'keyboard-shortcuts',
          label: 'Keyboard Shortcuts Guide',
          description: 'Learn all available shortcuts',
          icon: '⌨️',
          shortcut: 'Ctrl+K',
          action: () => this.showKeyboardShortcuts()
        },
        {
          id: 'settings',
          label: 'Settings & Configuration',
          description: 'Customize menu behavior',
          icon: '⚙️',
          shortcut: 'Ctrl+,',
          submenu: this.getSettingsSubmenu()
        },
        {
          id: 'exit',
          label: 'Exit Demo',
          description: 'Close the menu demonstration',
          icon: '🚪',
          shortcut: 'Ctrl+Q',
          action: () => this.exit()
        }
      ],
      searchable: true,
      showShortcuts: true,
      showIcons: true,
      animationsEnabled: this.animationsEnabled
    };
  }

  private getBasicDemoSubmenu(): MenuOption[] {
    return [
      {
        id: 'simple-action',
        label: 'Simple Action',
        description: 'Execute a basic menu action',
        icon: '▶️',
        action: async () => {
          await this.animateText('🎯 Basic action executed successfully!');
          await this.sleep(2000);
          this.redrawMenu();
        }
      },
      {
        id: 'input-demo',
        label: 'User Input Demo',
        description: 'Demonstrate user input handling',
        icon: '📝',
        action: () => this.inputDemo()
      },
      {
        id: 'validation-demo',
        label: 'Input Validation',
        description: 'Show input validation features',
        icon: '✅',
        action: () => this.validationDemo()
      }
    ];
  }

  private getAdvancedDemoSubmenu(): MenuOption[] {
    return [
      {
        id: 'dynamic-menu',
        label: 'Dynamic Menu Generation',
        description: 'Menus that change based on context',
        icon: '🔄',
        action: () => this.dynamicMenuDemo()
      },
      {
        id: 'conditional-items',
        label: 'Conditional Menu Items',
        description: 'Items that show/hide based on state',
        icon: '👁️',
        submenu: this.getConditionalSubmenu()
      },
      {
        id: 'async-actions',
        label: 'Async Action Demo',
        description: 'Demonstrate asynchronous operations',
        icon: '⏳',
        action: () => this.asyncActionDemo()
      }
    ];
  }

  private getNestedDemoSubmenu(): MenuOption[] {
    return [
      {
        id: 'level-2',
        label: 'Level 2 Menu',
        description: 'Second level of nesting',
        icon: '2️⃣',
        submenu: [
          {
            id: 'level-3',
            label: 'Level 3 Menu',
            description: 'Third level of nesting',
            icon: '3️⃣',
            submenu: [
              {
                id: 'level-4',
                label: 'Level 4 (Deep!)',
                description: 'Fourth level - very deep nesting',
                icon: '4️⃣',
                action: async () => {
                  await this.animateText('🏆 You reached level 4! Impressive navigation skills.');
                  await this.sleep(3000);
                  this.redrawMenu();
                }
              },
              {
                id: 'level-3-action',
                label: 'Level 3 Action',
                description: 'Action at the third level',
                icon: '🎯',
                action: async () => {
                  await this.animateText('✨ Level 3 action completed!');
                  await this.sleep(2000);
                  this.redrawMenu();
                }
              }
            ]
          }
        ]
      }
    ];
  }

  private getThemeSubmenu(): MenuOption[] {
    return [
      {
        id: 'default-theme',
        label: 'Default Theme',
        description: 'Standard color scheme',
        icon: '🎨',
        action: () => this.setTheme('default')
      },
      {
        id: 'dark-theme',
        label: 'Dark Theme',
        description: 'Dark color scheme',
        icon: '🌙',
        action: () => this.setTheme('dark')
      },
      {
        id: 'light-theme',
        label: 'Light Theme',
        description: 'Light color scheme',
        icon: '☀️',
        action: () => this.setTheme('light')
      }
    ];
  }

  private getSettingsSubmenu(): MenuOption[] {
    return [
      {
        id: 'toggle-animations',
        label: `${this.animationsEnabled ? 'Disable' : 'Enable'} Animations`,
        description: 'Toggle text animations on/off',
        icon: this.animationsEnabled ? '⏸️' : '▶️',
        action: () => this.toggleAnimations()
      },
      {
        id: 'toggle-performance',
        label: `${this.performanceMode ? 'Disable' : 'Enable'} Performance Mode`,
        description: 'Toggle performance optimizations',
        icon: this.performanceMode ? '🐌' : '🚀',
        action: () => this.togglePerformanceMode()
      }
    ];
  }

  private getConditionalSubmenu(): MenuOption[] {
    const currentTime = new Date().getHours();
    const isWorkingHours = currentTime >= 9 && currentTime <= 17;
    
    return [
      {
        id: 'always-visible',
        label: 'Always Visible Item',
        description: 'This item is always shown',
        icon: '👁️',
        action: async () => {
          await this.animateText('This item is always available!');
          await this.sleep(2000);
          this.redrawMenu();
        }
      },
      {
        id: 'working-hours-only',
        label: 'Working Hours Only',
        description: 'Only visible during 9 AM - 5 PM',
        icon: '🕘',
        hidden: !isWorkingHours,
        action: async () => {
          await this.animateText('This item is only available during working hours!');
          await this.sleep(2000);
          this.redrawMenu();
        }
      },
      {
        id: 'evening-only',
        label: 'Evening Only Item',
        description: 'Only visible after 5 PM',
        icon: '🌆',
        hidden: currentTime <= 17,
        action: async () => {
          await this.animateText('This evening-only item is now available!');
          await this.sleep(2000);
          this.redrawMenu();
        }
      }
    ];
  }

  // Demo action implementations
  private async performanceStressTest(): Promise<void> {
    this.clearScreen();
    await this.animateText('🚀 Generating 100+ menu items for stress test...');
    
    const stressTestOptions: MenuOption[] = [];
    for (let i = 1; i <= 150; i++) {
      stressTestOptions.push({
        id: `stress-item-${i}`,
        label: `Performance Test Item ${i}`,
        description: `Auto-generated item ${i} for stress testing`,
        icon: i % 10 === 0 ? '🎯' : '📄',
        action: async () => {
          await this.animateText(`Item ${i} executed!`);
          await this.sleep(1000);
          this.redrawMenu();
        }
      });
    }

    this.currentLevel.push(stressTestOptions);
    this.performanceMode = true;
    this.redrawMenu();
  }

  private async searchDemo(): Promise<void> {
    this.clearScreen();
    await this.animateText('🔍 Search Demo - Start typing to filter menu items!');
    await this.animateText('💡 Try searching for: "theme", "performance", "animation"');
    await this.sleep(3000);
    this.redrawMenu();
  }

  private async animationDemo(): Promise<void> {
    this.clearScreen();
    await this.animateText('✨ Animation Showcase', 100);
    await this.animateText('🌟 Text can be animated character by character...', 50);
    await this.animateText('⚡ Creating smooth, engaging user experiences!', 30);
    
    // Simulate loading animation
    process.stdout.write('📊 Loading');
    for (let i = 0; i < 10; i++) {
      await this.sleep(200);
      process.stdout.write('.');
    }
    console.log(' Complete!');
    
    await this.sleep(2000);
    this.redrawMenu();
  }

  private async showKeyboardShortcuts(): Promise<void> {
    this.clearScreen();
    const { theme } = this;
    
    console.log(`${theme.bold}${theme.primary}⌨️  Keyboard Shortcuts Guide${theme.reset}\n`);
    
    const shortcuts = [
      ['Numbers 1-9', 'Select menu option'],
      ['Type text', 'Search/filter menu items'],
      ['ESC', 'Go back or clear search'],
      ['Ctrl+C', 'Exit application'],
      ['Ctrl+B', 'Basic operations'],
      ['Ctrl+A', 'Advanced features'],
      ['Ctrl+N', 'Nested menus'],
      ['Ctrl+P', 'Performance test'],
      ['Ctrl+S', 'Search demo'],
      ['Ctrl+T', 'Theme switcher'],
      ['Ctrl+M', 'Animation demo'],
      ['Ctrl+K', 'This shortcuts guide'],
      ['Ctrl+Q', 'Quit application']
    ];

    shortcuts.forEach(([key, desc]) => {
      console.log(`${theme.secondary}${key.padEnd(15)}${theme.reset} ${desc}`);
    });

    console.log(`\n${theme.dim}Press any key to continue...${theme.reset}`);
    
    return new Promise(resolve => {
      const handler = () => {
        process.stdin.removeListener('data', handler);
        this.redrawMenu();
        resolve();
      };
      process.stdin.once('data', handler);
    });
  }

  private setTheme(themeName: string): void {
    this.currentTheme = themeName;
    this.redrawMenu();
  }

  private toggleAnimations(): void {
    this.animationsEnabled = !this.animationsEnabled;
    this.redrawMenu();
  }

  private togglePerformanceMode(): void {
    this.performanceMode = !this.performanceMode;
    this.redrawMenu();
  }

  private async dynamicMenuDemo(): Promise<void> {
    this.clearScreen();
    await this.animateText('🔄 Generating dynamic menu based on current system state...');
    
    const dynamicOptions: MenuOption[] = [
      {
        id: 'current-time',
        label: `Current Time: ${new Date().toLocaleTimeString()}`,
        description: 'This updates based on when the menu was generated',
        icon: '🕒',
        action: async () => {
          await this.animateText(`Current time when clicked: ${new Date().toLocaleTimeString()}`);
          await this.sleep(2000);
          this.redrawMenu();
        }
      },
      {
        id: 'random-item',
        label: `Random Number: ${Math.floor(Math.random() * 1000)}`,
        description: 'This shows a random number each time',
        icon: '🎲',
        action: async () => {
          await this.animateText(`New random number: ${Math.floor(Math.random() * 1000)}`);
          await this.sleep(2000);
          this.redrawMenu();
        }
      }
    ];

    this.currentLevel.push(dynamicOptions);
    this.redrawMenu();
  }

  private async asyncActionDemo(): Promise<void> {
    this.clearScreen();
    await this.animateText('⏳ Starting asynchronous operation...');
    
    // Simulate async API call
    const startTime = Date.now();
    await this.sleep(2000);
    const endTime = Date.now();
    
    await this.animateText(`✅ Async operation completed in ${endTime - startTime}ms`);
    await this.sleep(2000);
    this.redrawMenu();
  }

  private async inputDemo(): Promise<void> {
    this.clearScreen();
    console.log(`${this.theme.primary}📝 User Input Demo${this.theme.reset}\n`);
    
    return new Promise(resolve => {
      this.rl.question('Enter your name: ', async (name) => {
        await this.animateText(`Hello, ${name}! Nice to meet you.`);
        await this.sleep(2000);
        this.redrawMenu();
        resolve();
      });
    });
  }

  private async validationDemo(): Promise<void> {
    this.clearScreen();
    console.log(`${this.theme.primary}✅ Input Validation Demo${this.theme.reset}\n`);
    
    const validateEmail = (email: string): boolean => {
      return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    };

    return new Promise(resolve => {
      const askForEmail = () => {
        this.rl.question('Enter a valid email address: ', async (email) => {
          if (validateEmail(email)) {
            await this.animateText(`✅ Valid email: ${email}`);
            await this.sleep(2000);
            this.redrawMenu();
            resolve();
          } else {
            console.log(`${this.theme.error}❌ Invalid email format. Please try again.${this.theme.reset}`);
            askForEmail();
          }
        });
      };
      askForEmail();
    });
  }

  public async start(): Promise<void> {
    this.clearScreen();
    
    // Welcome animation
    await this.animateText('🎉 Welcome to the Interactive Menu System Demo!');
    await this.animateText('🚀 Preparing comprehensive feature showcase...');
    await this.sleep(1000);

    // Initialize main menu
    this.currentLevel = [this.getMainMenu().options];
    this.redrawMenu();

    // Keep the menu running
    this.rl.on('line', async (input) => {
      const choice = parseInt(input.trim());
      const currentMenu = this.currentLevel[this.currentLevel.length - 1];
      
      if (choice && choice > 0 && choice <= currentMenu.length) {
        const selectedOption = currentMenu[choice - 1];
        
        if (selectedOption.disabled) {
          await this.animateText('❌ This option is currently disabled.');
          await this.sleep(1000);
          return;
        }

        if (selectedOption.action) {
          await selectedOption.action();
        } else if (selectedOption.submenu) {
          this.currentLevel.push(selectedOption.submenu);
          this.redrawMenu();
        }
      } else {
        await this.animateText('❌ Invalid selection. Please try again.');
        await this.sleep(1000);
        this.redrawMenu();
      }
    });
  }
}

// Start the demo
if (require.main === module) {
  const demo = new InteractiveMenu();
  demo.start().catch(console.error);
}

export { InteractiveMenu, MenuOption, MenuConfig };