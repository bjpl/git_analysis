/**
 * Style Definitions for CLI Components
 * Defines styling rules and formatting for different UI components
 */

import { ColorScheme, TerminalCapabilities } from './ColorScheme';

export interface TextStyle {
  color?: string;
  backgroundColor?: string;
  bold?: boolean;
  italic?: boolean;
  underline?: boolean;
  strikethrough?: boolean;
  dim?: boolean;
  blink?: boolean;
  reverse?: boolean;
}

export interface ComponentStyle {
  default?: TextStyle;
  hover?: TextStyle;
  active?: TextStyle;
  disabled?: TextStyle;
  focused?: TextStyle;
  selected?: TextStyle;
}

export interface LayoutStyle {
  padding?: {
    top?: number;
    right?: number;
    bottom?: number;
    left?: number;
  };
  margin?: {
    top?: number;
    right?: number;
    bottom?: number;
    left?: number;
  };
  border?: {
    style?: 'solid' | 'dashed' | 'dotted' | 'double' | 'thick' | 'rounded';
    color?: string;
    width?: number;
  };
  width?: number | 'auto' | 'full';
  height?: number | 'auto' | 'full';
  alignment?: 'left' | 'center' | 'right' | 'justify';
}

export interface UIComponentStyles {
  // Basic text elements
  text: ComponentStyle;
  heading: ComponentStyle;
  subheading: ComponentStyle;
  caption: ComponentStyle;
  code: ComponentStyle;
  
  // Interactive elements
  button: ComponentStyle;
  input: ComponentStyle;
  select: ComponentStyle;
  checkbox: ComponentStyle;
  
  // Status indicators
  success: ComponentStyle;
  warning: ComponentStyle;
  error: ComponentStyle;
  info: ComponentStyle;
  
  // Layout components
  panel: ComponentStyle;
  card: ComponentStyle;
  list: ComponentStyle;
  listItem: ComponentStyle;
  
  // Progress indicators
  progressBar: ComponentStyle;
  spinner: ComponentStyle;
  badge: ComponentStyle;
  
  // Navigation
  menu: ComponentStyle;
  menuItem: ComponentStyle;
  breadcrumb: ComponentStyle;
  
  // Tables
  table: ComponentStyle;
  tableHeader: ComponentStyle;
  tableRow: ComponentStyle;
  tableCell: ComponentStyle;
}

export interface LayoutStyles {
  container: LayoutStyle;
  row: LayoutStyle;
  column: LayoutStyle;
  section: LayoutStyle;
  sidebar: LayoutStyle;
  header: LayoutStyle;
  footer: LayoutStyle;
}

export interface SyntaxHighlightStyles {
  keyword: TextStyle;
  string: TextStyle;
  number: TextStyle;
  comment: TextStyle;
  operator: TextStyle;
  function: TextStyle;
  variable: TextStyle;
  type: TextStyle;
  constant: TextStyle;
  property: TextStyle;
  punctuation: TextStyle;
}

export class StyleDefinitions {
  private colorScheme: ColorScheme;
  private terminalCapabilities: TerminalCapabilities;
  private componentStyles: UIComponentStyles;
  private layoutStyles: LayoutStyles;
  private syntaxStyles: SyntaxHighlightStyles;

  constructor(
    colorScheme: ColorScheme,
    terminalCapabilities: TerminalCapabilities,
    customStyles?: Partial<UIComponentStyles>
  ) {
    this.colorScheme = colorScheme;
    this.terminalCapabilities = terminalCapabilities;
    this.componentStyles = this.createDefaultComponentStyles();
    this.layoutStyles = this.createDefaultLayoutStyles();
    this.syntaxStyles = this.createDefaultSyntaxStyles();
    
    // Apply custom styles if provided
    if (customStyles) {
      this.componentStyles = { ...this.componentStyles, ...customStyles };
    }
  }

  /**
   * Get style for a specific component and state
   */
  getComponentStyle(component: keyof UIComponentStyles, state: keyof ComponentStyle = 'default'): TextStyle {
    const componentStyle = this.componentStyles[component];
    return componentStyle?.[state] || componentStyle?.default || {};
  }

  /**
   * Get layout style for a component
   */
  getLayoutStyle(layout: keyof LayoutStyles): LayoutStyle {
    return this.layoutStyles[layout] || {};
  }

  /**
   * Get syntax highlighting style
   */
  getSyntaxStyle(element: keyof SyntaxHighlightStyles): TextStyle {
    return this.syntaxStyles[element] || {};
  }

  /**
   * Convert style to ANSI escape sequences
   */
  styleToAnsi(style: TextStyle): string {
    let ansi = '';

    // Handle colors
    if (style.color) {
      ansi += this.colorScheme.getAnsiCode(style.color, this.terminalCapabilities);
    }
    
    if (style.backgroundColor) {
      ansi += this.colorScheme.getBgAnsiCode(style.backgroundColor, this.terminalCapabilities);
    }

    // Handle text decorations
    if (style.bold) ansi += '\x1b[1m';
    if (style.dim) ansi += '\x1b[2m';
    if (style.italic) ansi += '\x1b[3m';
    if (style.underline) ansi += '\x1b[4m';
    if (style.blink) ansi += '\x1b[5m';
    if (style.reverse) ansi += '\x1b[7m';
    if (style.strikethrough) ansi += '\x1b[9m';

    return ansi;
  }

  /**
   * Get reset sequence
   */
  getResetSequence(): string {
    return '\x1b[0m';
  }

  /**
   * Apply style to text
   */
  applyStyle(text: string, style: TextStyle): string {
    const ansiStyle = this.styleToAnsi(style);
    const reset = this.getResetSequence();
    return ansiStyle + text + reset;
  }

  /**
   * Create box drawing characters based on terminal capabilities
   */
  getBoxChars() {
    if (this.terminalCapabilities.unicode) {
      return {
        horizontal: '─',
        vertical: '│',
        topLeft: '┌',
        topRight: '┐',
        bottomLeft: '└',
        bottomRight: '┘',
        cross: '┼',
        teeUp: '┴',
        teeDown: '┬',
        teeLeft: '┤',
        teeRight: '├'
      };
    } else {
      return {
        horizontal: '-',
        vertical: '|',
        topLeft: '+',
        topRight: '+',
        bottomLeft: '+',
        bottomRight: '+',
        cross: '+',
        teeUp: '+',
        teeDown: '+',
        teeLeft: '+',
        teeRight: '+'
      };
    }
  }

  private createDefaultComponentStyles(): UIComponentStyles {
    return {
      text: {
        default: { color: 'text' }
      },
      heading: {
        default: { color: 'primary', bold: true }
      },
      subheading: {
        default: { color: 'secondary', bold: true }
      },
      caption: {
        default: { color: 'textSecondary', dim: true }
      },
      code: {
        default: { color: 'accent', backgroundColor: 'surface' }
      },
      button: {
        default: { color: 'background', backgroundColor: 'primary' },
        hover: { color: 'background', backgroundColor: 'secondary' },
        active: { color: 'background', backgroundColor: 'primary', bold: true },
        disabled: { color: 'textDisabled', backgroundColor: 'muted' }
      },
      input: {
        default: { color: 'text', backgroundColor: 'surface' },
        focused: { color: 'text', backgroundColor: 'surface', underline: true },
        disabled: { color: 'textDisabled', backgroundColor: 'muted' }
      },
      select: {
        default: { color: 'text', backgroundColor: 'surface' },
        focused: { color: 'primary', backgroundColor: 'surface' },
        disabled: { color: 'textDisabled', backgroundColor: 'muted' }
      },
      checkbox: {
        default: { color: 'text' },
        selected: { color: 'success', bold: true },
        disabled: { color: 'textDisabled' }
      },
      success: {
        default: { color: 'success', bold: true }
      },
      warning: {
        default: { color: 'warning', bold: true }
      },
      error: {
        default: { color: 'error', bold: true }
      },
      info: {
        default: { color: 'info', bold: true }
      },
      panel: {
        default: { color: 'text', backgroundColor: 'surface' }
      },
      card: {
        default: { color: 'text', backgroundColor: 'surface' }
      },
      list: {
        default: { color: 'text' }
      },
      listItem: {
        default: { color: 'text' },
        hover: { color: 'primary', backgroundColor: 'surface' },
        selected: { color: 'background', backgroundColor: 'primary' }
      },
      progressBar: {
        default: { color: 'primary', backgroundColor: 'muted' }
      },
      spinner: {
        default: { color: 'primary' }
      },
      badge: {
        default: { color: 'background', backgroundColor: 'accent', bold: true }
      },
      menu: {
        default: { color: 'text', backgroundColor: 'background' }
      },
      menuItem: {
        default: { color: 'text' },
        hover: { color: 'primary', backgroundColor: 'surface' },
        selected: { color: 'background', backgroundColor: 'primary' },
        disabled: { color: 'textDisabled' }
      },
      breadcrumb: {
        default: { color: 'textSecondary' }
      },
      table: {
        default: { color: 'text' }
      },
      tableHeader: {
        default: { color: 'text', bold: true, underline: true }
      },
      tableRow: {
        default: { color: 'text' },
        hover: { color: 'text', backgroundColor: 'surface' }
      },
      tableCell: {
        default: { color: 'text' }
      }
    };
  }

  private createDefaultLayoutStyles(): LayoutStyles {
    return {
      container: {
        padding: { top: 1, right: 2, bottom: 1, left: 2 },
        width: 'full'
      },
      row: {
        width: 'full'
      },
      column: {
        height: 'auto'
      },
      section: {
        margin: { top: 1, bottom: 1 },
        padding: { top: 0, right: 0, bottom: 0, left: 0 }
      },
      sidebar: {
        width: 30,
        padding: { top: 1, right: 1, bottom: 1, left: 1 },
        border: { style: 'solid', color: 'border', width: 1 }
      },
      header: {
        width: 'full',
        padding: { top: 0, right: 0, bottom: 1, left: 0 },
        border: { style: 'solid', color: 'border', width: 1 }
      },
      footer: {
        width: 'full',
        padding: { top: 1, right: 0, bottom: 0, left: 0 },
        border: { style: 'solid', color: 'border', width: 1 }
      }
    };
  }

  private createDefaultSyntaxStyles(): SyntaxHighlightStyles {
    return {
      keyword: { color: 'syntax.keyword', bold: true },
      string: { color: 'syntax.string' },
      number: { color: 'syntax.number' },
      comment: { color: 'syntax.comment', italic: true },
      operator: { color: 'syntax.operator' },
      function: { color: 'syntax.function', bold: true },
      variable: { color: 'syntax.variable' },
      type: { color: 'syntax.type', bold: true },
      constant: { color: 'syntax.number', bold: true },
      property: { color: 'syntax.variable' },
      punctuation: { color: 'text' }
    };
  }
}