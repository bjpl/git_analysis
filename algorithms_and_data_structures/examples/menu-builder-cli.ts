#!/usr/bin/env ts-node

/**
 * Interactive Menu Builder CLI Tool
 * 
 * Features:
 * - Visual menu designer with live preview
 * - Export to JSON/YAML formats
 * - Import existing menu configurations
 * - Validation and testing capabilities
 * - Code generation for menu integration
 * - Template system for quick setup
 */

import * as readline from 'readline';
import * as fs from 'fs';
import * as path from 'path';
import * as yaml from 'js-yaml';

interface MenuItem {
  id: string;
  label: string;
  description?: string;
  shortcut?: string;
  icon?: string;
  category?: string;
  action?: string;
  submenu?: MenuItem[];
  disabled?: boolean;
  hidden?: boolean;
  conditions?: {
    timeRange?: { start: string; end: string };
    userRole?: string[];
    feature?: string;
  };
}

interface MenuSchema {
  name: string;
  version: string;
  description?: string;
  theme: string;
  settings: {
    searchable: boolean;
    showIcons: boolean;
    showShortcuts: boolean;
    animationsEnabled: boolean;
    maxDisplayItems: number;
  };
  items: MenuItem[];
  metadata: {
    created: string;
    author?: string;
    tags: string[];
  };
}

class MenuBuilderCLI {
  private rl: readline.Interface;
  private currentMenu: MenuSchema;
  private previewMode: boolean = false;
  private editingPath: string[] = [];

  constructor() {
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
    });

    this.currentMenu = this.createEmptyMenu();
  }

  private createEmptyMenu(): MenuSchema {
    return {
      name: 'Untitled Menu',
      version: '1.0.0',
      description: 'A new menu created with Menu Builder CLI',
      theme: 'default',
      settings: {
        searchable: true,
        showIcons: true,
        showShortcuts: true,
        animationsEnabled: true,
        maxDisplayItems: 10
      },
      items: [],
      metadata: {
        created: new Date().toISOString(),
        tags: []
      }
    };
  }

  private clearScreen(): void {
    process.stdout.write('\x1Bc');
  }

  private displayHeader(): void {
    console.log('╔═══════════════════════════════════════════════════════════════╗');
    console.log('║                    🛠️  Menu Builder CLI                        ║');
    console.log('║                   Visual Menu Designer                        ║');
    console.log('╚═══════════════════════════════════════════════════════════════╝');
    console.log('');
  }

  private displayMainMenu(): void {
    this.clearScreen();
    this.displayHeader();

    console.log(`📋 Current Menu: ${this.currentMenu.name} (v${this.currentMenu.version})`);
    console.log(`📊 Items: ${this.countTotalItems(this.currentMenu.items)}`);
    console.log('');

    console.log('🎛️  Main Actions:');
    console.log('1. 📝 Edit Menu Properties');
    console.log('2. 🔧 Manage Menu Items');
    console.log('3. 👁️  Preview Menu');
    console.log('4. 💾 Save/Export Menu');
    console.log('5. 📂 Load/Import Menu');
    console.log('6. 🧪 Validate & Test Menu');
    console.log('7. 🏗️  Generate Integration Code');
    console.log('8. 📚 Menu Templates');
    console.log('9. ⚙️  Settings & Configuration');
    console.log('10. 🚪 Exit Builder');
    console.log('');
    console.log('Enter your choice (1-10): ');
  }

  private countTotalItems(items: MenuItem[]): number {
    let count = items.length;
    for (const item of items) {
      if (item.submenu) {
        count += this.countTotalItems(item.submenu);
      }
    }
    return count;
  }

  private async editMenuProperties(): Promise<void> {
    this.clearScreen();
    console.log('📝 Editing Menu Properties\n');

    const name = await this.askQuestion(`Menu Name (${this.currentMenu.name}): `);
    if (name.trim()) this.currentMenu.name = name.trim();

    const version = await this.askQuestion(`Version (${this.currentMenu.version}): `);
    if (version.trim()) this.currentMenu.version = version.trim();

    const description = await this.askQuestion(`Description (${this.currentMenu.description || 'None'}): `);
    if (description.trim()) this.currentMenu.description = description.trim();

    const theme = await this.askQuestion(`Theme [default|dark|light] (${this.currentMenu.theme}): `);
    if (['default', 'dark', 'light'].includes(theme.trim())) {
      this.currentMenu.theme = theme.trim();
    }

    const author = await this.askQuestion(`Author (${this.currentMenu.metadata.author || 'None'}): `);
    if (author.trim()) this.currentMenu.metadata.author = author.trim();

    console.log('✅ Menu properties updated!');
    await this.sleep(2000);
  }

  private async manageMenuItems(): Promise<void> {
    while (true) {
      this.clearScreen();
      console.log('🔧 Menu Items Management\n');

      const currentItems = this.getCurrentItems();
      const breadcrumb = this.getBreadcrumb();
      
      console.log(`📍 Current location: ${breadcrumb}`);
      console.log('');

      if (currentItems.length === 0) {
        console.log('📭 No items in this menu level.');
      } else {
        console.log('🗂️  Current Items:');
        currentItems.forEach((item, index) => {
          const submenuIndicator = item.submenu ? ' 📁' : '';
          const disabledIndicator = item.disabled ? ' ❌' : '';
          const hiddenIndicator = item.hidden ? ' 👁️‍🗨️' : '';
          console.log(`${index + 1}. ${item.icon || '📄'} ${item.label}${submenuIndicator}${disabledIndicator}${hiddenIndicator}`);
        });
      }

      console.log('');
      console.log('Actions:');
      console.log('a) ➕ Add New Item');
      console.log('e) ✏️  Edit Item (enter number)');
      console.log('d) 🗑️  Delete Item (enter number)');
      console.log('m) 📦 Move Item');
      console.log('n) 📁 Navigate to Submenu (enter number)');
      console.log('b) ⬆️  Go Back/Up Level');
      console.log('x) 🚪 Return to Main Menu');

      const choice = await this.askQuestion('Choice: ');

      if (choice === 'a') {
        await this.addNewItem();
      } else if (choice === 'e') {
        const index = await this.askQuestion('Enter item number to edit: ');
        await this.editItem(parseInt(index) - 1);
      } else if (choice === 'd') {
        const index = await this.askQuestion('Enter item number to delete: ');
        await this.deleteItem(parseInt(index) - 1);
      } else if (choice === 'm') {
        await this.moveItem();
      } else if (choice === 'n') {
        const index = await this.askQuestion('Enter item number to navigate to: ');
        await this.navigateToSubmenu(parseInt(index) - 1);
      } else if (choice === 'b') {
        if (this.editingPath.length > 0) {
          this.editingPath.pop();
        }
      } else if (choice === 'x') {
        break;
      }
    }
  }

  private getCurrentItems(): MenuItem[] {
    let current = this.currentMenu.items;
    for (const pathSegment of this.editingPath) {
      const index = parseInt(pathSegment);
      if (current[index] && current[index].submenu) {
        current = current[index].submenu!;
      }
    }
    return current;
  }

  private getBreadcrumb(): string {
    if (this.editingPath.length === 0) {
      return 'Root Menu';
    }
    
    let breadcrumb = 'Root';
    let current = this.currentMenu.items;
    
    for (const pathSegment of this.editingPath) {
      const index = parseInt(pathSegment);
      if (current[index]) {
        breadcrumb += ` > ${current[index].label}`;
        if (current[index].submenu) {
          current = current[index].submenu!;
        }
      }
    }
    
    return breadcrumb;
  }

  private async addNewItem(): Promise<void> {
    this.clearScreen();
    console.log('➕ Adding New Menu Item\n');

    const item: MenuItem = {
      id: '',
      label: ''
    };

    item.label = await this.askQuestion('Item Label: ');
    item.id = await this.askQuestion(`Item ID (${this.generateId(item.label)}): `) || this.generateId(item.label);
    
    const description = await this.askQuestion('Description (optional): ');
    if (description.trim()) item.description = description.trim();

    const icon = await this.askQuestion('Icon/Emoji (optional): ');
    if (icon.trim()) item.icon = icon.trim();

    const shortcut = await this.askQuestion('Keyboard Shortcut (optional): ');
    if (shortcut.trim()) item.shortcut = shortcut.trim();

    const category = await this.askQuestion('Category (optional): ');
    if (category.trim()) item.category = category.trim();

    const actionType = await this.askQuestion('Action type [function|submenu|none] (none): ');
    
    if (actionType === 'function') {
      item.action = await this.askQuestion('Function name: ');
    } else if (actionType === 'submenu') {
      item.submenu = [];
    }

    const disabled = await this.askQuestion('Disabled? [y/n] (n): ');
    if (disabled.toLowerCase() === 'y') item.disabled = true;

    const hidden = await this.askQuestion('Hidden? [y/n] (n): ');
    if (hidden.toLowerCase() === 'y') item.hidden = true;

    // Add conditions
    const hasConditions = await this.askQuestion('Add conditions? [y/n] (n): ');
    if (hasConditions.toLowerCase() === 'y') {
      item.conditions = await this.configureConditions();
    }

    const currentItems = this.getCurrentItems();
    currentItems.push(item);

    console.log('✅ Item added successfully!');
    await this.sleep(1500);
  }

  private generateId(label: string): string {
    return label.toLowerCase()
      .replace(/[^a-z0-9]/g, '-')
      .replace(/-+/g, '-')
      .replace(/^-|-$/g, '');
  }

  private async configureConditions(): Promise<any> {
    const conditions: any = {};

    const timeCondition = await this.askQuestion('Time-based condition? [y/n] (n): ');
    if (timeCondition.toLowerCase() === 'y') {
      const start = await this.askQuestion('Start time (HH:MM): ');
      const end = await this.askQuestion('End time (HH:MM): ');
      conditions.timeRange = { start, end };
    }

    const roleCondition = await this.askQuestion('User role condition? [y/n] (n): ');
    if (roleCondition.toLowerCase() === 'y') {
      const roles = await this.askQuestion('Allowed roles (comma-separated): ');
      conditions.userRole = roles.split(',').map(r => r.trim());
    }

    const featureCondition = await this.askQuestion('Feature flag condition? [y/n] (n): ');
    if (featureCondition.toLowerCase() === 'y') {
      conditions.feature = await this.askQuestion('Feature flag name: ');
    }

    return conditions;
  }

  private async editItem(index: number): Promise<void> {
    const currentItems = this.getCurrentItems();
    if (index < 0 || index >= currentItems.length) {
      console.log('❌ Invalid item number!');
      await this.sleep(1500);
      return;
    }

    const item = currentItems[index];
    this.clearScreen();
    console.log(`✏️  Editing Item: ${item.label}\n`);

    const label = await this.askQuestion(`Label (${item.label}): `);
    if (label.trim()) item.label = label.trim();

    const description = await this.askQuestion(`Description (${item.description || 'None'}): `);
    if (description.trim()) item.description = description.trim();

    const icon = await this.askQuestion(`Icon (${item.icon || 'None'}): `);
    if (icon.trim()) item.icon = icon.trim();

    // ... more edit options ...

    console.log('✅ Item updated successfully!');
    await this.sleep(1500);
  }

  private async deleteItem(index: number): Promise<void> {
    const currentItems = this.getCurrentItems();
    if (index < 0 || index >= currentItems.length) {
      console.log('❌ Invalid item number!');
      await this.sleep(1500);
      return;
    }

    const item = currentItems[index];
    const confirm = await this.askQuestion(`Delete "${item.label}"? [y/n]: `);
    
    if (confirm.toLowerCase() === 'y') {
      currentItems.splice(index, 1);
      console.log('✅ Item deleted successfully!');
    } else {
      console.log('❌ Deletion cancelled.');
    }
    
    await this.sleep(1500);
  }

  private async navigateToSubmenu(index: number): Promise<void> {
    const currentItems = this.getCurrentItems();
    if (index < 0 || index >= currentItems.length) {
      console.log('❌ Invalid item number!');
      await this.sleep(1500);
      return;
    }

    const item = currentItems[index];
    if (!item.submenu) {
      console.log('❌ This item has no submenu!');
      await this.sleep(1500);
      return;
    }

    this.editingPath.push(index.toString());
  }

  private async previewMenu(): Promise<void> {
    this.clearScreen();
    console.log('👁️  Menu Preview\n');
    
    console.log('╔═══════════════════════════════════════════════════════════════╗');
    console.log(`║ ${this.currentMenu.name.padEnd(61)} ║`);
    console.log('╚═══════════════════════════════════════════════════════════════╝');
    console.log('');

    this.renderMenuItems(this.currentMenu.items, 0);

    console.log('\n📊 Menu Statistics:');
    console.log(`Total Items: ${this.countTotalItems(this.currentMenu.items)}`);
    console.log(`Theme: ${this.currentMenu.theme}`);
    console.log(`Searchable: ${this.currentMenu.settings.searchable ? 'Yes' : 'No'}`);
    console.log(`Icons: ${this.currentMenu.settings.showIcons ? 'Enabled' : 'Disabled'}`);
    console.log(`Shortcuts: ${this.currentMenu.settings.showShortcuts ? 'Enabled' : 'Disabled'}`);

    await this.askQuestion('\nPress Enter to continue...');
  }

  private renderMenuItems(items: MenuItem[], depth: number): void {
    const indent = '  '.repeat(depth);
    
    items.forEach((item, index) => {
      const icon = item.icon || '📄';
      const shortcut = item.shortcut ? ` (${item.shortcut})` : '';
      const submenuIndicator = item.submenu ? ' ►' : '';
      const statusIndicators = [
        item.disabled ? ' [DISABLED]' : '',
        item.hidden ? ' [HIDDEN]' : '',
        item.conditions ? ' [CONDITIONAL]' : ''
      ].join('');

      console.log(`${indent}${index + 1}. ${icon} ${item.label}${shortcut}${submenuIndicator}${statusIndicators}`);
      
      if (item.description && depth < 2) {
        console.log(`${indent}   ${item.description}`);
      }

      if (item.submenu && depth < 3) {
        this.renderMenuItems(item.submenu, depth + 1);
      }
    });
  }

  private async saveExportMenu(): Promise<void> {
    this.clearScreen();
    console.log('💾 Save/Export Menu\n');

    console.log('Export Format:');
    console.log('1. JSON (Recommended)');
    console.log('2. YAML');
    console.log('3. TypeScript Interface');
    console.log('4. JavaScript Module');

    const format = await this.askQuestion('Choose format (1-4): ');
    const filename = await this.askQuestion('Filename (without extension): ') || 'menu';

    try {
      switch (format) {
        case '1':
          await this.exportAsJSON(filename);
          break;
        case '2':
          await this.exportAsYAML(filename);
          break;
        case '3':
          await this.exportAsTypeScript(filename);
          break;
        case '4':
          await this.exportAsJavaScript(filename);
          break;
        default:
          console.log('❌ Invalid format selection!');
          await this.sleep(1500);
          return;
      }
      
      console.log('✅ Menu exported successfully!');
    } catch (error) {
      console.log(`❌ Export failed: ${error}`);
    }
    
    await this.sleep(2000);
  }

  private async exportAsJSON(filename: string): Promise<void> {
    const filepath = path.join(process.cwd(), `${filename}.json`);
    const content = JSON.stringify(this.currentMenu, null, 2);
    fs.writeFileSync(filepath, content, 'utf8');
    console.log(`📄 Exported to: ${filepath}`);
  }

  private async exportAsYAML(filename: string): Promise<void> {
    const filepath = path.join(process.cwd(), `${filename}.yaml`);
    const content = yaml.dump(this.currentMenu);
    fs.writeFileSync(filepath, content, 'utf8');
    console.log(`📄 Exported to: ${filepath}`);
  }

  private async exportAsTypeScript(filename: string): Promise<void> {
    const filepath = path.join(process.cwd(), `${filename}.ts`);
    const content = this.generateTypeScriptCode();
    fs.writeFileSync(filepath, content, 'utf8');
    console.log(`📄 Exported to: ${filepath}`);
  }

  private async exportAsJavaScript(filename: string): Promise<void> {
    const filepath = path.join(process.cwd(), `${filename}.js`);
    const content = this.generateJavaScriptCode();
    fs.writeFileSync(filepath, content, 'utf8');
    console.log(`📄 Exported to: ${filepath}`);
  }

  private generateTypeScriptCode(): string {
    return `// Generated by Menu Builder CLI
// Created: ${new Date().toISOString()}

export interface MenuItem {
  id: string;
  label: string;
  description?: string;
  shortcut?: string;
  icon?: string;
  category?: string;
  action?: string;
  submenu?: MenuItem[];
  disabled?: boolean;
  hidden?: boolean;
}

export const menuConfig = ${JSON.stringify(this.currentMenu, null, 2)} as const;

export default menuConfig;
`;
  }

  private generateJavaScriptCode(): string {
    return `// Generated by Menu Builder CLI
// Created: ${new Date().toISOString()}

const menuConfig = ${JSON.stringify(this.currentMenu, null, 2)};

module.exports = menuConfig;
`;
  }

  private async loadImportMenu(): Promise<void> {
    this.clearScreen();
    console.log('📂 Load/Import Menu\n');

    const filename = await this.askQuestion('Enter filename to import: ');
    
    try {
      const filepath = path.resolve(filename);
      if (!fs.existsSync(filepath)) {
        console.log('❌ File not found!');
        await this.sleep(2000);
        return;
      }

      const content = fs.readFileSync(filepath, 'utf8');
      const extension = path.extname(filename).toLowerCase();

      let importedMenu: MenuSchema;
      
      if (extension === '.json') {
        importedMenu = JSON.parse(content);
      } else if (extension === '.yaml' || extension === '.yml') {
        importedMenu = yaml.load(content) as MenuSchema;
      } else {
        console.log('❌ Unsupported file format! Use .json or .yaml/.yml');
        await this.sleep(2000);
        return;
      }

      // Validate imported menu
      if (this.validateMenuSchema(importedMenu)) {
        this.currentMenu = importedMenu;
        console.log('✅ Menu imported successfully!');
      } else {
        console.log('❌ Invalid menu format!');
      }
    } catch (error) {
      console.log(`❌ Import failed: ${error}`);
    }
    
    await this.sleep(2000);
  }

  private validateMenuSchema(menu: any): menu is MenuSchema {
    return menu &&
           typeof menu.name === 'string' &&
           typeof menu.version === 'string' &&
           Array.isArray(menu.items) &&
           menu.settings &&
           menu.metadata;
  }

  private async validateTestMenu(): Promise<void> {
    this.clearScreen();
    console.log('🧪 Menu Validation & Testing\n');

    const issues: string[] = [];

    // Check for duplicate IDs
    const ids = new Set<string>();
    const checkDuplicateIds = (items: MenuItem[]) => {
      for (const item of items) {
        if (ids.has(item.id)) {
          issues.push(`Duplicate ID: ${item.id}`);
        }
        ids.add(item.id);
        if (item.submenu) {
          checkDuplicateIds(item.submenu);
        }
      }
    };
    checkDuplicateIds(this.currentMenu.items);

    // Check for empty labels
    const checkEmptyLabels = (items: MenuItem[]) => {
      for (const item of items) {
        if (!item.label.trim()) {
          issues.push(`Empty label for ID: ${item.id}`);
        }
        if (item.submenu) {
          checkEmptyLabels(item.submenu);
        }
      }
    };
    checkEmptyLabels(this.currentMenu.items);

    // Check for orphaned shortcuts
    const shortcuts = new Set<string>();
    const checkShortcuts = (items: MenuItem[]) => {
      for (const item of items) {
        if (item.shortcut) {
          if (shortcuts.has(item.shortcut)) {
            issues.push(`Duplicate shortcut: ${item.shortcut}`);
          }
          shortcuts.add(item.shortcut);
        }
        if (item.submenu) {
          checkShortcuts(item.submenu);
        }
      }
    };
    checkShortcuts(this.currentMenu.items);

    console.log('📊 Validation Results:');
    if (issues.length === 0) {
      console.log('✅ No issues found! Menu is valid.');
    } else {
      console.log(`❌ Found ${issues.length} issues:`);
      issues.forEach(issue => console.log(`  • ${issue}`));
    }

    console.log('\n📈 Menu Statistics:');
    console.log(`Total Items: ${this.countTotalItems(this.currentMenu.items)}`);
    console.log(`Maximum Depth: ${this.getMaxDepth(this.currentMenu.items)}`);
    console.log(`Items with Actions: ${this.countItemsWithActions(this.currentMenu.items)}`);
    console.log(`Items with Shortcuts: ${shortcuts.size}`);

    await this.askQuestion('\nPress Enter to continue...');
  }

  private getMaxDepth(items: MenuItem[], currentDepth: number = 1): number {
    let maxDepth = currentDepth;
    for (const item of items) {
      if (item.submenu) {
        const depth = this.getMaxDepth(item.submenu, currentDepth + 1);
        maxDepth = Math.max(maxDepth, depth);
      }
    }
    return maxDepth;
  }

  private countItemsWithActions(items: MenuItem[]): number {
    let count = 0;
    for (const item of items) {
      if (item.action) count++;
      if (item.submenu) {
        count += this.countItemsWithActions(item.submenu);
      }
    }
    return count;
  }

  private async generateIntegrationCode(): Promise<void> {
    this.clearScreen();
    console.log('🏗️  Generate Integration Code\n');

    console.log('Choose integration type:');
    console.log('1. React Component');
    console.log('2. Vue Component');
    console.log('3. Angular Component');
    console.log('4. Plain JavaScript Class');
    console.log('5. CLI Implementation');

    const type = await this.askQuestion('Choose type (1-5): ');
    const componentName = await this.askQuestion('Component/Class name: ') || 'GeneratedMenu';

    let code = '';
    switch (type) {
      case '1':
        code = this.generateReactComponent(componentName);
        break;
      case '2':
        code = this.generateVueComponent(componentName);
        break;
      case '3':
        code = this.generateAngularComponent(componentName);
        break;
      case '4':
        code = this.generateJavaScriptClass(componentName);
        break;
      case '5':
        code = this.generateCLIImplementation(componentName);
        break;
      default:
        console.log('❌ Invalid selection!');
        await this.sleep(1500);
        return;
    }

    const filename = await this.askQuestion('Save as filename (without extension): ') || componentName;
    const extension = type === '1' ? '.tsx' : type === '2' ? '.vue' : type === '3' ? '.ts' : '.js';
    
    fs.writeFileSync(`${filename}${extension}`, code, 'utf8');
    console.log(`✅ Integration code generated: ${filename}${extension}`);
    await this.sleep(2000);
  }

  private generateReactComponent(name: string): string {
    return `// Generated React Component
import React, { useState, useCallback } from 'react';

interface MenuProps {
  onAction?: (actionName: string) => void;
}

const ${name}: React.FC<MenuProps> = ({ onAction }) => {
  const [currentPath, setCurrentPath] = useState<string[]>([]);
  
  const menuConfig = ${JSON.stringify(this.currentMenu, null, 2)};
  
  const handleItemClick = useCallback((item: any) => {
    if (item.action && onAction) {
      onAction(item.action);
    } else if (item.submenu) {
      setCurrentPath(prev => [...prev, item.id]);
    }
  }, [onAction]);
  
  const goBack = useCallback(() => {
    setCurrentPath(prev => prev.slice(0, -1));
  }, []);
  
  // Component implementation...
  return (
    <div className="menu-component">
      <h1>{menuConfig.name}</h1>
      {/* Menu rendering logic */}
    </div>
  );
};

export default ${name};
`;
  }

  private generateVueComponent(name: string): string {
    return `<!-- Generated Vue Component -->
<template>
  <div class="menu-component">
    <h1>{{ menuConfig.name }}</h1>
    <!-- Menu rendering logic -->
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: '${name}',
  setup() {
    const currentPath = ref<string[]>([]);
    const menuConfig = ${JSON.stringify(this.currentMenu, null, 2)};
    
    return {
      currentPath,
      menuConfig
    };
  }
});
</script>

<style scoped>
.menu-component {
  /* Component styles */
}
</style>
`;
  }

  private generateAngularComponent(name: string): string {
    return `// Generated Angular Component
import { Component } from '@angular/core';

@Component({
  selector: 'app-${name.toLowerCase()}',
  template: \`
    <div class="menu-component">
      <h1>{{ menuConfig.name }}</h1>
      <!-- Menu rendering logic -->
    </div>
  \`,
  styleUrls: ['./${name.toLowerCase()}.component.css']
})
export class ${name}Component {
  currentPath: string[] = [];
  menuConfig = ${JSON.stringify(this.currentMenu, null, 2)};
  
  onItemClick(item: any): void {
    if (item.action) {
      // Handle action
    } else if (item.submenu) {
      this.currentPath.push(item.id);
    }
  }
  
  goBack(): void {
    this.currentPath.pop();
  }
}
`;
  }

  private generateJavaScriptClass(name: string): string {
    return `// Generated JavaScript Class
class ${name} {
  constructor(container, options = {}) {
    this.container = container;
    this.options = options;
    this.currentPath = [];
    this.menuConfig = ${JSON.stringify(this.currentMenu, null, 2)};
    
    this.init();
  }
  
  init() {
    this.render();
  }
  
  render() {
    // Render menu implementation
    this.container.innerHTML = \`
      <div class="menu-component">
        <h1>\${this.menuConfig.name}</h1>
        <!-- Menu rendering logic -->
      </div>
    \`;
  }
  
  handleItemClick(item) {
    if (item.action && this.options.onAction) {
      this.options.onAction(item.action);
    } else if (item.submenu) {
      this.currentPath.push(item.id);
      this.render();
    }
  }
  
  goBack() {
    this.currentPath.pop();
    this.render();
  }
}

// Usage: new ${name}(document.getElementById('menu'));
`;
  }

  private generateCLIImplementation(name: string): string {
    return `// Generated CLI Implementation
#!/usr/bin/env node

const readline = require('readline');

class ${name} {
  constructor() {
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
    });
    
    this.currentPath = [];
    this.menuConfig = ${JSON.stringify(this.currentMenu, null, 2)};
  }
  
  start() {
    this.displayMenu();
  }
  
  displayMenu() {
    console.clear();
    console.log(\`\${this.menuConfig.name}\\n\`);
    
    const currentItems = this.getCurrentItems();
    currentItems.forEach((item, index) => {
      const icon = item.icon || '•';
      const submenuIndicator = item.submenu ? ' →' : '';
      console.log(\`\${index + 1}. \${icon} \${item.label}\${submenuIndicator}\`);
    });
    
    console.log('\\nEnter choice: ');
  }
  
  getCurrentItems() {
    let current = this.menuConfig.items;
    for (const path of this.currentPath) {
      current = current.find(item => item.id === path)?.submenu || [];
    }
    return current;
  }
  
  // Implementation continues...
}

if (require.main === module) {
  const menu = new ${name}();
  menu.start();
}

module.exports = ${name};
`;
  }

  private async showMenuTemplates(): Promise<void> {
    this.clearScreen();
    console.log('📚 Menu Templates\n');

    const templates = [
      { id: 'dashboard', name: 'Dashboard Menu', description: 'Admin dashboard navigation' },
      { id: 'wizard', name: 'Wizard Menu', description: 'Step-by-step wizard interface' },
      { id: 'command-palette', name: 'Command Palette', description: 'VS Code style command menu' },
      { id: 'mobile', name: 'Mobile Menu', description: 'Touch-optimized mobile menu' },
      { id: 'settings', name: 'Settings Menu', description: 'Application settings interface' }
    ];

    console.log('Available Templates:');
    templates.forEach((template, index) => {
      console.log(`${index + 1}. ${template.name}`);
      console.log(`   ${template.description}`);
      console.log('');
    });

    const choice = await this.askQuestion('Select template (1-5) or 0 to cancel: ');
    const templateIndex = parseInt(choice) - 1;

    if (templateIndex >= 0 && templateIndex < templates.length) {
      const confirm = await this.askQuestion('This will replace current menu. Continue? [y/n]: ');
      if (confirm.toLowerCase() === 'y') {
        this.currentMenu = this.loadTemplate(templates[templateIndex].id);
        console.log('✅ Template loaded successfully!');
      }
    }

    await this.sleep(2000);
  }

  private loadTemplate(templateId: string): MenuSchema {
    // Template data would normally be loaded from files
    const templates: { [key: string]: MenuSchema } = {
      'dashboard': {
        name: 'Admin Dashboard',
        version: '1.0.0',
        description: 'Main dashboard navigation menu',
        theme: 'dark',
        settings: {
          searchable: true,
          showIcons: true,
          showShortcuts: true,
          animationsEnabled: true,
          maxDisplayItems: 10
        },
        items: [
          {
            id: 'overview',
            label: 'Overview',
            icon: '📊',
            shortcut: 'Ctrl+O',
            action: 'showOverview'
          },
          {
            id: 'users',
            label: 'User Management',
            icon: '👥',
            shortcut: 'Ctrl+U',
            submenu: [
              { id: 'user-list', label: 'User List', action: 'showUsers' },
              { id: 'add-user', label: 'Add User', action: 'addUser' },
              { id: 'user-roles', label: 'Roles & Permissions', action: 'manageRoles' }
            ]
          },
          {
            id: 'analytics',
            label: 'Analytics',
            icon: '📈',
            shortcut: 'Ctrl+A',
            action: 'showAnalytics'
          },
          {
            id: 'settings',
            label: 'Settings',
            icon: '⚙️',
            shortcut: 'Ctrl+,',
            action: 'showSettings'
          }
        ],
        metadata: {
          created: new Date().toISOString(),
          author: 'Menu Builder CLI',
          tags: ['dashboard', 'admin']
        }
      }
    };

    return templates[templateId] || this.createEmptyMenu();
  }

  private async askQuestion(question: string): Promise<string> {
    return new Promise(resolve => {
      this.rl.question(question, resolve);
    });
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private async moveItem(): Promise<void> {
    console.log('📦 Move Item feature - Implementation pending');
    await this.sleep(1500);
  }

  private async showSettings(): Promise<void> {
    this.clearScreen();
    console.log('⚙️  Settings & Configuration\n');

    console.log('Current Settings:');
    console.log(`Searchable: ${this.currentMenu.settings.searchable}`);
    console.log(`Show Icons: ${this.currentMenu.settings.showIcons}`);
    console.log(`Show Shortcuts: ${this.currentMenu.settings.showShortcuts}`);
    console.log(`Animations: ${this.currentMenu.settings.animationsEnabled}`);
    console.log(`Max Display Items: ${this.currentMenu.settings.maxDisplayItems}`);

    const setting = await this.askQuestion('\nWhich setting to change? [searchable|icons|shortcuts|animations|maxitems]: ');
    
    switch (setting.toLowerCase()) {
      case 'searchable':
        this.currentMenu.settings.searchable = !this.currentMenu.settings.searchable;
        break;
      case 'icons':
        this.currentMenu.settings.showIcons = !this.currentMenu.settings.showIcons;
        break;
      case 'shortcuts':
        this.currentMenu.settings.showShortcuts = !this.currentMenu.settings.showShortcuts;
        break;
      case 'animations':
        this.currentMenu.settings.animationsEnabled = !this.currentMenu.settings.animationsEnabled;
        break;
      case 'maxitems':
        const max = await this.askQuestion('Enter max display items: ');
        this.currentMenu.settings.maxDisplayItems = parseInt(max) || 10;
        break;
    }

    console.log('✅ Setting updated!');
    await this.sleep(1500);
  }

  public async start(): Promise<void> {
    while (true) {
      this.displayMainMenu();
      
      const choice = await this.askQuestion('');
      
      switch (choice) {
        case '1':
          await this.editMenuProperties();
          break;
        case '2':
          await this.manageMenuItems();
          break;
        case '3':
          await this.previewMenu();
          break;
        case '4':
          await this.saveExportMenu();
          break;
        case '5':
          await this.loadImportMenu();
          break;
        case '6':
          await this.validateTestMenu();
          break;
        case '7':
          await this.generateIntegrationCode();
          break;
        case '8':
          await this.showMenuTemplates();
          break;
        case '9':
          await this.showSettings();
          break;
        case '10':
          console.log('👋 Thank you for using Menu Builder CLI!');
          process.exit(0);
        default:
          console.log('❌ Invalid choice. Please try again.');
          await this.sleep(1000);
      }
    }
  }
}

// Start the CLI
if (require.main === module) {
  const builder = new MenuBuilderCLI();
  builder.start().catch(console.error);
}

export default MenuBuilderCLI;