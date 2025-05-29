/**
 * AI Assistant Color Palette
 * All colors used throughout the application
 */

export const colors = {
  // Primary Colors
  background: '#0E1C2D',
  white: '#FFFFFF',
  whiteGray: '#C2C1C1',
  darkGray: '#706E6E',
  
  // Yellows
  yellow: '#FCC000',
  darkYellow: '#66500E',
  
  // Blues
  fadedBlue: '#315074',
  fadedBlue2: '#182739',
  fadedBlue3: '#1E3147',
  fadedBrightBlue: '#8F97B7',
  brightBlue: '#32CEFF',
  darkBrightBlue: '#2b38dd',
  darkBrightBlue: '#2b38dd',
  
  // Greens
  green: '#67BD6D',
  darkGreen: '#3A703E',
  
  // Reds
  red: '#CF5362',
  darkRed: '#79202B',
  
  // Oranges
  orange: '#FF8B21',
  darkOrange: '#8F520C',
  
  // Purples
  purple: '#BD46EF',
  darkPurple: '#6C238B',
  
  // Legacy colors for gradual migration
  navy: {
    lighter: '#1e2735',
    light: '#121922',
    DEFAULT: '#080d13',
  },
  gold: {
    DEFAULT: '#d4af37',
  }
} as const;

// Semantic color mappings
export const semanticColors = {
  // Backgrounds
  mainBg: colors.background,
  modalBg: colors.navy.DEFAULT,
  headerBg: colors.navy.light,
  cardBg: colors.navy.light,
  
  // Text
  textPrimary: colors.white,
  textSecondary: colors.whiteGray,
  textMuted: colors.darkGray,
  textAccent: colors.yellow,
  
  // Borders
  borderPrimary: colors.fadedBlue3,
  borderAccent: colors.yellow,
  
  // Status
  success: colors.green,
  warning: colors.orange,
  error: colors.red,
  info: colors.brightBlue,
  
  // Visibility
  private: colors.red,
  shared: colors.brightBlue,
  global: colors.green,
} as const;

// Export type for TypeScript
export type ColorName = keyof typeof colors;
export type SemanticColorName = keyof typeof semanticColors;