/**
 * Dark Theme
 * Modern dark theme optimized for extended coding sessions
 */

import { ThemeDefinition } from './ThemeManager';

export const darkTheme: ThemeDefinition = {
  name: 'dark',
  displayName: 'Dark Professional',
  description: 'Modern dark theme optimized for extended coding sessions and low-light environments',
  author: 'CLI Team',
  version: '1.0.0',
  palette: {
    // Primary colors - Bright blue for dark backgrounds
    primary: {
      hex: '#0EA5E9',
      ansi256: 39,
      ansi16: 36,
      ansi8: 6,
      name: 'Sky Blue Primary'
    },
    secondary: {
      hex: '#0284C7',
      ansi256: 32,
      ansi16: 34,
      ansi8: 4,
      name: 'Dark Sky Blue Secondary'
    },
    tertiary: {
      hex: '#7DD3FC',
      ansi256: 117,
      ansi16: 36,
      ansi8: 6,
      name: 'Light Sky Blue Tertiary'
    },
    
    // Status colors - Vibrant for dark backgrounds
    success: {
      hex: '#10B981',
      ansi256: 42,
      ansi16: 32,
      ansi8: 2,
      name: 'Emerald Green Success'
    },
    warning: {
      hex: '#F59E0B',
      ansi256: 214,
      ansi16: 33,
      ansi8: 3,
      name: 'Amber Warning'
    },
    error: {
      hex: '#EF4444',
      ansi256: 203,
      ansi16: 31,
      ansi8: 1,
      name: 'Red Error'
    },
    info: {
      hex: '#06B6D4',
      ansi256: 44,
      ansi16: 36,
      ansi8: 6,
      name: 'Cyan Info'
    },
    
    // Neutral colors - Dark theme palette
    background: {
      hex: '#0F172A',
      ansi256: 235,
      ansi16: 30,
      ansi8: 0,
      name: 'Slate 900 Background'
    },
    surface: {
      hex: '#1E293B',
      ansi256: 237,
      ansi16: 30,
      ansi8: 0,
      name: 'Slate 800 Surface'
    },
    text: {
      hex: '#F1F5F9',
      ansi256: 15,
      ansi16: 37,
      ansi8: 7,
      name: 'Slate 100 Text'
    },
    textSecondary: {
      hex: '#94A3B8',
      ansi256: 248,
      ansi16: 37,
      ansi8: 7,
      name: 'Slate 400 Secondary Text'
    },
    textDisabled: {
      hex: '#64748B',
      ansi256: 243,
      ansi16: 37,
      ansi8: 7,
      name: 'Slate 500 Disabled Text'
    },
    border: {
      hex: '#334155',
      ansi256: 239,
      ansi16: 37,
      ansi8: 7,
      name: 'Slate 700 Border'
    },
    
    // Semantic colors
    accent: {
      hex: '#8B5CF6',
      ansi256: 141,
      ansi16: 35,
      ansi8: 5,
      name: 'Violet Accent'
    },
    highlight: {
      hex: '#374151',
      ansi256: 239,
      ansi16: 33,
      ansi8: 3,
      name: 'Gray 700 Highlight'
    },
    muted: {
      hex: '#475569',
      ansi256: 241,
      ansi16: 37,
      ansi8: 7,
      name: 'Slate 600 Muted'
    },
    
    // Syntax highlighting - Optimized for dark backgrounds
    syntax: {
      keyword: {
        hex: '#C792EA',
        ansi256: 177,
        ansi16: 35,
        ansi8: 5,
        name: 'Purple Keywords'
      },
      string: {
        hex: '#C3E88D',
        ansi256: 150,
        ansi16: 32,
        ansi8: 2,
        name: 'Green Strings'
      },
      number: {
        hex: '#F78C6C',
        ansi256: 209,
        ansi16: 31,
        ansi8: 1,
        name: 'Orange Numbers'
      },
      comment: {
        hex: '#546E7A',
        ansi256: 243,
        ansi16: 37,
        ansi8: 7,
        name: 'Blue Gray Comments'
      },
      operator: {
        hex: '#89DDFF',
        ansi256: 117,
        ansi16: 36,
        ansi8: 6,
        name: 'Cyan Operators'
      },
      function: {
        hex: '#82AAFF',
        ansi256: 111,
        ansi16: 34,
        ansi8: 4,
        name: 'Blue Functions'
      },
      variable: {
        hex: '#EEFFFF',
        ansi256: 15,
        ansi16: 37,
        ansi8: 7,
        name: 'White Variables'
      },
      type: {
        hex: '#FFCB6B',
        ansi256: 221,
        ansi16: 33,
        ansi8: 3,
        name: 'Yellow Types'
      }
    }
  },
  
  colorBlindSupport: {
    protanopia: {
      // Red-green colorblind adjustments for dark theme
      error: {
        hex: '#FB923C',
        ansi256: 215,
        ansi16: 33,
        ansi8: 3,
        name: 'Orange Error (Protanopia)'
      },
      success: {
        hex: '#60A5FA',
        ansi256: 75,
        ansi16: 34,
        ansi8: 4,
        name: 'Blue Success (Protanopia)'
      }
    },
    deuteranopia: {
      error: {
        hex: '#FBBF24',
        ansi256: 220,
        ansi16: 33,
        ansi8: 3,
        name: 'Yellow Error (Deuteranopia)'
      },
      success: {
        hex: '#3B82F6',
        ansi256: 69,
        ansi16: 34,
        ansi8: 4,
        name: 'Blue Success (Deuteranopia)'
      }
    },
    tritanopia: {
      warning: {
        hex: '#EC4899',
        ansi256: 205,
        ansi16: 31,
        ansi8: 1,
        name: 'Pink Warning (Tritanopia)'
      },
      info: {
        hex: '#34D399',
        ansi256: 77,
        ansi16: 32,
        ansi8: 2,
        name: 'Green Info (Tritanopia)'
      }
    },
    highContrast: {
      text: {
        hex: '#FFFFFF',
        ansi256: 15,
        ansi16: 37,
        ansi8: 7,
        name: 'Pure White Text'
      },
      background: {
        hex: '#000000',
        ansi256: 0,
        ansi16: 30,
        ansi8: 0,
        name: 'Pure Black Background'
      },
      primary: {
        hex: '#00FFFF',
        ansi256: 51,
        ansi16: 36,
        ansi8: 6,
        name: 'Cyan Primary'
      }
    }
  },
  
  terminalRequirements: {
    minColors: 256,
    requiresTrueColor: false,
    requiresUnicode: false
  }
};