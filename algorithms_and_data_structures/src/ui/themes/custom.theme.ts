/**
 * Custom Theme Template
 * Base template for user-customizable themes
 */

import { ThemeDefinition } from './ThemeManager';

export const customTheme: ThemeDefinition = {
  name: 'custom',
  displayName: 'Custom User Theme',
  description: 'User-customizable theme template. Modify colors and styles to create your personal theme.',
  author: 'User',
  version: '1.0.0',
  palette: {
    // Primary colors - User customizable
    primary: {
      hex: '#6366F1',
      ansi256: 99,
      ansi16: 35,
      ansi8: 5,
      name: 'Indigo Primary'
    },
    secondary: {
      hex: '#4F46E5',
      ansi256: 63,
      ansi16: 34,
      ansi8: 4,
      name: 'Indigo Secondary'
    },
    tertiary: {
      hex: '#818CF8',
      ansi256: 105,
      ansi16: 35,
      ansi8: 5,
      name: 'Light Indigo Tertiary'
    },
    
    // Status colors - Customizable semantic colors
    success: {
      hex: '#059669',
      ansi256: 29,
      ansi16: 32,
      ansi8: 2,
      name: 'Emerald Success'
    },
    warning: {
      hex: '#D97706',
      ansi256: 172,
      ansi16: 33,
      ansi8: 3,
      name: 'Amber Warning'
    },
    error: {
      hex: '#DC2626',
      ansi256: 160,
      ansi16: 31,
      ansi8: 1,
      name: 'Red Error'
    },
    info: {
      hex: '#0891B2',
      ansi256: 31,
      ansi16: 36,
      ansi8: 6,
      name: 'Cyan Info'
    },
    
    // Neutral colors - Adaptable base
    background: {
      hex: '#FAFAFA',
      ansi256: 15,
      ansi16: 37,
      ansi8: 7,
      name: 'Off-White Background'
    },
    surface: {
      hex: '#F5F5F5',
      ansi256: 255,
      ansi16: 37,
      ansi8: 7,
      name: 'Gray Surface'
    },
    text: {
      hex: '#1F2937',
      ansi256: 0,
      ansi16: 30,
      ansi8: 0,
      name: 'Dark Gray Text'
    },
    textSecondary: {
      hex: '#6B7280',
      ansi256: 242,
      ansi16: 37,
      ansi8: 7,
      name: 'Gray Secondary Text'
    },
    textDisabled: {
      hex: '#9CA3AF',
      ansi256: 248,
      ansi16: 37,
      ansi8: 7,
      name: 'Light Gray Disabled Text'
    },
    border: {
      hex: '#E5E7EB',
      ansi256: 253,
      ansi16: 37,
      ansi8: 7,
      name: 'Light Gray Border'
    },
    
    // Semantic colors - User preferences
    accent: {
      hex: '#EC4899',
      ansi256: 205,
      ansi16: 31,
      ansi8: 1,
      name: 'Pink Accent'
    },
    highlight: {
      hex: '#FEF3C7',
      ansi256: 230,
      ansi16: 33,
      ansi8: 3,
      name: 'Yellow Highlight'
    },
    muted: {
      hex: '#F3F4F6',
      ansi256: 252,
      ansi16: 37,
      ansi8: 7,
      name: 'Very Light Gray Muted'
    },
    
    // Syntax highlighting - Customizable for coding
    syntax: {
      keyword: {
        hex: '#7C3AED',
        ansi256: 129,
        ansi16: 35,
        ansi8: 5,
        name: 'Violet Keywords'
      },
      string: {
        hex: '#059669',
        ansi256: 29,
        ansi16: 32,
        ansi8: 2,
        name: 'Emerald Strings'
      },
      number: {
        hex: '#EA580C',
        ansi256: 166,
        ansi16: 31,
        ansi8: 1,
        name: 'Orange Numbers'
      },
      comment: {
        hex: '#6B7280',
        ansi256: 242,
        ansi16: 37,
        ansi8: 7,
        name: 'Gray Comments'
      },
      operator: {
        hex: '#374151',
        ansi256: 239,
        ansi16: 30,
        ansi8: 0,
        name: 'Dark Gray Operators'
      },
      function: {
        hex: '#2563EB',
        ansi256: 27,
        ansi16: 34,
        ansi8: 4,
        name: 'Blue Functions'
      },
      variable: {
        hex: '#1F2937',
        ansi256: 0,
        ansi16: 30,
        ansi8: 0,
        name: 'Dark Gray Variables'
      },
      type: {
        hex: '#0891B2',
        ansi256: 31,
        ansi16: 36,
        ansi8: 6,
        name: 'Cyan Types'
      }
    }
  },
  
  colorBlindSupport: {
    protanopia: {
      // Customizable red-green colorblind support
      error: {
        hex: '#F59E0B',
        ansi256: 214,
        ansi16: 33,
        ansi8: 3,
        name: 'Amber Error (Protanopia)'
      },
      success: {
        hex: '#3B82F6',
        ansi256: 69,
        ansi16: 34,
        ansi8: 4,
        name: 'Blue Success (Protanopia)'
      }
    },
    deuteranopia: {
      error: {
        hex: '#FB923C',
        ansi256: 215,
        ansi16: 33,
        ansi8: 3,
        name: 'Orange Error (Deuteranopia)'
      },
      success: {
        hex: '#1D4ED8',
        ansi256: 21,
        ansi16: 34,
        ansi8: 4,
        name: 'Blue Success (Deuteranopia)'
      }
    },
    tritanopia: {
      warning: {
        hex: '#F472B6',
        ansi256: 211,
        ansi16: 31,
        ansi8: 1,
        name: 'Pink Warning (Tritanopia)'
      },
      info: {
        hex: '#22C55E',
        ansi256: 41,
        ansi16: 32,
        ansi8: 2,
        name: 'Green Info (Tritanopia)'
      }
    },
    highContrast: {
      text: {
        hex: '#000000',
        ansi256: 0,
        ansi16: 30,
        ansi8: 0,
        name: 'Black Text (High Contrast)'
      },
      background: {
        hex: '#FFFFFF',
        ansi256: 15,
        ansi16: 37,
        ansi8: 7,
        name: 'White Background (High Contrast)'
      },
      primary: {
        hex: '#0000FF',
        ansi256: 21,
        ansi16: 34,
        ansi8: 4,
        name: 'Blue Primary (High Contrast)'
      }
    }
  },
  
  customStyles: {
    // Customizable component styles
    heading: {
      default: { color: 'primary', bold: true, underline: false }
    },
    button: {
      default: { color: 'background', backgroundColor: 'primary' },
      hover: { color: 'background', backgroundColor: 'secondary', italic: true },
      active: { color: 'background', backgroundColor: 'primary', bold: true }
    },
    code: {
      default: { color: 'accent', backgroundColor: 'surface', italic: true }
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
    }
  },
  
  terminalRequirements: {
    minColors: 256,
    requiresTrueColor: true,
    requiresUnicode: true
  }
};

/**
 * Helper function to create a custom theme from user preferences
 */
export function createCustomTheme(
  name: string,
  displayName: string,
  customizations: {
    colors?: Partial<any>;
    styles?: Partial<any>;
    accessibility?: Partial<any>;
  }
): ThemeDefinition {
  const baseTheme = { ...customTheme };
  
  // Override theme metadata
  baseTheme.name = name;
  baseTheme.displayName = displayName;
  baseTheme.description = `Custom theme: ${displayName}`;
  
  // Apply color customizations
  if (customizations.colors) {
    baseTheme.palette = {
      ...baseTheme.palette,
      ...customizations.colors
    };
  }
  
  // Apply style customizations
  if (customizations.styles) {
    baseTheme.customStyles = {
      ...baseTheme.customStyles,
      ...customizations.styles
    };
  }
  
  // Apply accessibility customizations
  if (customizations.accessibility) {
    baseTheme.colorBlindSupport = {
      ...baseTheme.colorBlindSupport,
      ...customizations.accessibility
    };
  }
  
  return baseTheme;
}

/**
 * Preset customization templates
 */
export const customThemePresets = {
  // Warm color scheme
  warm: {
    colors: {
      primary: { hex: '#DC2626', ansi256: 160, ansi16: 31, ansi8: 1, name: 'Red Primary' },
      secondary: { hex: '#EA580C', ansi256: 166, ansi16: 31, ansi8: 1, name: 'Orange Secondary' },
      accent: { hex: '#F59E0B', ansi256: 214, ansi16: 33, ansi8: 3, name: 'Amber Accent' }
    }
  },
  
  // Cool color scheme
  cool: {
    colors: {
      primary: { hex: '#0891B2', ansi256: 31, ansi16: 36, ansi8: 6, name: 'Cyan Primary' },
      secondary: { hex: '#0284C7', ansi256: 32, ansi16: 34, ansi8: 4, name: 'Sky Blue Secondary' },
      accent: { hex: '#7C3AED', ansi256: 129, ansi16: 35, ansi8: 5, name: 'Violet Accent' }
    }
  },
  
  // Monochrome scheme
  monochrome: {
    colors: {
      primary: { hex: '#374151', ansi256: 239, ansi16: 30, ansi8: 0, name: 'Gray Primary' },
      secondary: { hex: '#4B5563', ansi256: 241, ansi16: 30, ansi8: 0, name: 'Dark Gray Secondary' },
      accent: { hex: '#6B7280', ansi256: 242, ansi16: 37, ansi8: 7, name: 'Medium Gray Accent' }
    }
  }
};