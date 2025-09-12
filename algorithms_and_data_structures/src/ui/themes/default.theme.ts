/**
 * Default Light Theme
 * Clean, professional theme suitable for most environments
 */

import { ThemeDefinition } from './ThemeManager';

export const defaultTheme: ThemeDefinition = {
  name: 'default',
  displayName: 'Default Light',
  description: 'Clean, professional light theme with excellent readability',
  author: 'CLI Team',
  version: '1.0.0',
  palette: {
    // Primary colors - Modern blue palette
    primary: {
      hex: '#007ACC',
      ansi256: 32,
      ansi16: 34,
      ansi8: 4,
      name: 'Primary Blue'
    },
    secondary: {
      hex: '#005A9B',
      ansi256: 25,
      ansi16: 34,
      ansi8: 4,
      name: 'Secondary Blue'
    },
    tertiary: {
      hex: '#40A9FF',
      ansi256: 75,
      ansi16: 36,
      ansi8: 6,
      name: 'Tertiary Light Blue'
    },
    
    // Status colors
    success: {
      hex: '#28A745',
      ansi256: 34,
      ansi16: 32,
      ansi8: 2,
      name: 'Success Green'
    },
    warning: {
      hex: '#FFC107',
      ansi256: 220,
      ansi16: 33,
      ansi8: 3,
      name: 'Warning Yellow'
    },
    error: {
      hex: '#DC3545',
      ansi256: 196,
      ansi16: 31,
      ansi8: 1,
      name: 'Error Red'
    },
    info: {
      hex: '#17A2B8',
      ansi256: 37,
      ansi16: 36,
      ansi8: 6,
      name: 'Info Cyan'
    },
    
    // Neutral colors
    background: {
      hex: '#FFFFFF',
      ansi256: 15,
      ansi16: 37,
      ansi8: 7,
      name: 'White Background'
    },
    surface: {
      hex: '#F8F9FA',
      ansi256: 255,
      ansi16: 37,
      ansi8: 7,
      name: 'Light Surface'
    },
    text: {
      hex: '#212529',
      ansi256: 0,
      ansi16: 30,
      ansi8: 0,
      name: 'Dark Text'
    },
    textSecondary: {
      hex: '#6C757D',
      ansi256: 242,
      ansi16: 37,
      ansi8: 7,
      name: 'Secondary Text'
    },
    textDisabled: {
      hex: '#ADB5BD',
      ansi256: 249,
      ansi16: 37,
      ansi8: 7,
      name: 'Disabled Text'
    },
    border: {
      hex: '#DEE2E6',
      ansi256: 253,
      ansi16: 37,
      ansi8: 7,
      name: 'Border Gray'
    },
    
    // Semantic colors
    accent: {
      hex: '#6F42C1',
      ansi256: 97,
      ansi16: 35,
      ansi8: 5,
      name: 'Purple Accent'
    },
    highlight: {
      hex: '#FFF3CD',
      ansi256: 230,
      ansi16: 33,
      ansi8: 3,
      name: 'Yellow Highlight'
    },
    muted: {
      hex: '#E9ECEF',
      ansi256: 252,
      ansi16: 37,
      ansi8: 7,
      name: 'Muted Gray'
    },
    
    // Syntax highlighting
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
        hex: '#FF6600',
        ansi256: 202,
        ansi16: 31,
        ansi8: 1,
        name: 'Orange Numbers'
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
        hex: '#795E26',
        ansi256: 130,
        ansi16: 33,
        ansi8: 3,
        name: 'Brown Functions'
      },
      variable: {
        hex: '#001080',
        ansi256: 18,
        ansi16: 34,
        ansi8: 4,
        name: 'Dark Blue Variables'
      },
      type: {
        hex: '#267F99',
        ansi256: 31,
        ansi16: 36,
        ansi8: 6,
        name: 'Teal Types'
      }
    }
  },
  
  colorBlindSupport: {
    protanopia: {
      // Red-green colorblind adjustments
      error: {
        hex: '#FF8C00',
        ansi256: 208,
        ansi16: 33,
        ansi8: 3,
        name: 'Orange Error (Protanopia)'
      },
      success: {
        hex: '#4169E1',
        ansi256: 62,
        ansi16: 34,
        ansi8: 4,
        name: 'Royal Blue Success (Protanopia)'
      }
    },
    deuteranopia: {
      // Red-green colorblind adjustments (different variant)
      error: {
        hex: '#FF4500',
        ansi256: 202,
        ansi16: 31,
        ansi8: 1,
        name: 'Orange Red Error (Deuteranopia)'
      },
      success: {
        hex: '#1E90FF',
        ansi256: 33,
        ansi16: 36,
        ansi8: 6,
        name: 'Dodger Blue Success (Deuteranopia)'
      }
    },
    tritanopia: {
      // Blue-yellow colorblind adjustments
      warning: {
        hex: '#FF1493',
        ansi256: 198,
        ansi16: 31,
        ansi8: 1,
        name: 'Deep Pink Warning (Tritanopia)'
      },
      info: {
        hex: '#32CD32',
        ansi256: 46,
        ansi16: 32,
        ansi8: 2,
        name: 'Lime Green Info (Tritanopia)'
      }
    },
    highContrast: {
      // High contrast versions
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
      },
      primary: {
        hex: '#0000FF',
        ansi256: 21,
        ansi16: 34,
        ansi8: 4,
        name: 'Pure Blue Primary'
      }
    }
  },
  
  terminalRequirements: {
    minColors: 16,
    requiresTrueColor: false,
    requiresUnicode: false
  }
};