/**
 * High Contrast Theme
 * Maximum contrast theme for accessibility and low-vision users
 */

import { ThemeDefinition } from './ThemeManager';

export const highContrastTheme: ThemeDefinition = {
  name: 'high-contrast',
  displayName: 'High Contrast',
  description: 'Maximum contrast theme designed for accessibility and low-vision users',
  author: 'CLI Team',
  version: '1.0.0',
  palette: {
    // Primary colors - High contrast
    primary: {
      hex: '#0000FF',
      ansi256: 21,
      ansi16: 34,
      ansi8: 4,
      name: 'Pure Blue Primary'
    },
    secondary: {
      hex: '#000080',
      ansi256: 18,
      ansi16: 34,
      ansi8: 4,
      name: 'Navy Blue Secondary'
    },
    tertiary: {
      hex: '#4169E1',
      ansi256: 62,
      ansi16: 34,
      ansi8: 4,
      name: 'Royal Blue Tertiary'
    },
    
    // Status colors - Maximum contrast
    success: {
      hex: '#008000',
      ansi256: 28,
      ansi16: 32,
      ansi8: 2,
      name: 'Pure Green Success'
    },
    warning: {
      hex: '#FFD700',
      ansi256: 220,
      ansi16: 33,
      ansi8: 3,
      name: 'Gold Warning'
    },
    error: {
      hex: '#FF0000',
      ansi256: 196,
      ansi16: 31,
      ansi8: 1,
      name: 'Pure Red Error'
    },
    info: {
      hex: '#00FFFF',
      ansi256: 51,
      ansi16: 36,
      ansi8: 6,
      name: 'Cyan Info'
    },
    
    // Neutral colors - Maximum contrast
    background: {
      hex: '#FFFFFF',
      ansi256: 15,
      ansi16: 37,
      ansi8: 7,
      name: 'Pure White Background'
    },
    surface: {
      hex: '#F0F0F0',
      ansi256: 255,
      ansi16: 37,
      ansi8: 7,
      name: 'Light Gray Surface'
    },
    text: {
      hex: '#000000',
      ansi256: 0,
      ansi16: 30,
      ansi8: 0,
      name: 'Pure Black Text'
    },
    textSecondary: {
      hex: '#404040',
      ansi256: 238,
      ansi16: 30,
      ansi8: 0,
      name: 'Dark Gray Secondary Text'
    },
    textDisabled: {
      hex: '#808080',
      ansi256: 244,
      ansi16: 37,
      ansi8: 7,
      name: 'Gray Disabled Text'
    },
    border: {
      hex: '#000000',
      ansi256: 0,
      ansi16: 30,
      ansi8: 0,
      name: 'Black Border'
    },
    
    // Semantic colors - High contrast
    accent: {
      hex: '#800080',
      ansi256: 90,
      ansi16: 35,
      ansi8: 5,
      name: 'Purple Accent'
    },
    highlight: {
      hex: '#FFFF00',
      ansi256: 226,
      ansi16: 33,
      ansi8: 3,
      name: 'Yellow Highlight'
    },
    muted: {
      hex: '#C0C0C0',
      ansi256: 250,
      ansi16: 37,
      ansi8: 7,
      name: 'Silver Muted'
    },
    
    // Syntax highlighting - High contrast
    syntax: {
      keyword: {
        hex: '#0000FF',
        ansi256: 21,
        ansi16: 34,
        ansi8: 4,
        name: 'Blue Keywords'
      },
      string: {
        hex: '#008000',
        ansi256: 28,
        ansi16: 32,
        ansi8: 2,
        name: 'Green Strings'
      },
      number: {
        hex: '#FF0000',
        ansi256: 196,
        ansi16: 31,
        ansi8: 1,
        name: 'Red Numbers'
      },
      comment: {
        hex: '#808080',
        ansi256: 244,
        ansi16: 37,
        ansi8: 7,
        name: 'Gray Comments'
      },
      operator: {
        hex: '#000000',
        ansi256: 0,
        ansi16: 30,
        ansi8: 0,
        name: 'Black Operators'
      },
      function: {
        hex: '#800080',
        ansi256: 90,
        ansi16: 35,
        ansi8: 5,
        name: 'Purple Functions'
      },
      variable: {
        hex: '#000000',
        ansi256: 0,
        ansi16: 30,
        ansi8: 0,
        name: 'Black Variables'
      },
      type: {
        hex: '#008080',
        ansi256: 30,
        ansi16: 36,
        ansi8: 6,
        name: 'Teal Types'
      }
    }
  },
  
  colorBlindSupport: {
    // For high contrast theme, we use distinct patterns and additional indicators
    protanopia: {
      // Use distinct brightness levels instead of color differences
      success: {
        hex: '#000000',
        ansi256: 0,
        ansi16: 30,
        ansi8: 0,
        name: 'Black Success (Protanopia) - Use ✓ symbol'
      },
      error: {
        hex: '#FFFFFF',
        ansi256: 15,
        ansi16: 37,
        ansi8: 7,
        name: 'White Error (Protanopia) - Use ✗ symbol'
      }
    },
    deuteranopia: {
      success: {
        hex: '#000000',
        ansi256: 0,
        ansi16: 30,
        ansi8: 0,
        name: 'Black Success (Deuteranopia) - Use ✓ symbol'
      },
      error: {
        hex: '#FFFFFF',
        ansi256: 15,
        ansi16: 37,
        ansi8: 7,
        name: 'White Error (Deuteranopia) - Use ✗ symbol'
      }
    },
    tritanopia: {
      warning: {
        hex: '#000000',
        ansi256: 0,
        ansi16: 30,
        ansi8: 0,
        name: 'Black Warning (Tritanopia) - Use ⚠ symbol'
      },
      info: {
        hex: '#808080',
        ansi256: 244,
        ansi16: 37,
        ansi8: 7,
        name: 'Gray Info (Tritanopia) - Use ℹ symbol'
      }
    },
    highContrast: {
      // This is already a high contrast theme
      text: {
        hex: '#000000',
        ansi256: 0,
        ansi16: 30,
        ansi8: 0,
        name: 'Pure Black Text'
      },
      background: {
        hex: '#FFFFFF',
        ansi256: 15,
        ansi16: 37,
        ansi8: 7,
        name: 'Pure White Background'
      }
    }
  },
  
  customStyles: {
    // Additional styling for accessibility
    text: {
      default: { color: 'text', bold: true } // Make all text bold for better visibility
    },
    button: {
      default: { color: 'background', backgroundColor: 'text', bold: true },
      hover: { color: 'text', backgroundColor: 'background', bold: true, reverse: true },
      active: { color: 'background', backgroundColor: 'primary', bold: true },
      disabled: { color: 'textDisabled', backgroundColor: 'muted', bold: false }
    },
    success: {
      default: { color: 'success', bold: true, underline: true }
    },
    warning: {
      default: { color: 'warning', bold: true, underline: true }
    },
    error: {
      default: { color: 'error', bold: true, underline: true }
    },
    info: {
      default: { color: 'info', bold: true, underline: true }
    }
  },
  
  terminalRequirements: {
    minColors: 8,
    requiresTrueColor: false,
    requiresUnicode: false
  }
};