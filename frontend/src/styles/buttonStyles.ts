/**
 * Button style utilities based on color system
 * Provides consistent hover, active, disabled, and focus states
 */

import { colors } from './colors';

// Helper function to lighten a hex color
const lightenColor = (hex: string, percent: number = 10): string => {
  const num = parseInt(hex.replace('#', ''), 16);
  const amt = Math.round(2.55 * percent);
  const R = (num >> 16) + amt;
  const G = (num >> 8 & 0x00FF) + amt;
  const B = (num & 0x0000FF) + amt;
  return '#' + (0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 +
    (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 +
    (B < 255 ? B < 1 ? 0 : B : 255)).toString(16).slice(1);
};

// Helper function to darken a hex color
const darkenColor = (hex: string, percent: number = 10): string => {
  const num = parseInt(hex.replace('#', ''), 16);
  const amt = Math.round(2.55 * percent);
  const R = (num >> 16) - amt;
  const G = (num >> 8 & 0x00FF) - amt;
  const B = (num & 0x0000FF) - amt;
  return '#' + (0x1000000 + (R > 0 ? R : 0) * 0x10000 +
    (G > 0 ? G : 0) * 0x100 +
    (B > 0 ? B : 0)).toString(16).slice(1);
};

// Button style generator
export const getButtonStyles = (baseColor: string, textColor: string = '#000') => ({
  base: {
    backgroundColor: baseColor,
    color: textColor,
    transition: 'all 0.2s ease',
  },
  hover: {
    backgroundColor: lightenColor(baseColor, 10),
  },
  active: {
    backgroundColor: darkenColor(baseColor, 10),
  },
  disabled: {
    backgroundColor: baseColor + '4D', // 30% opacity
    color: textColor + '80', // 50% opacity
    cursor: 'not-allowed',
  },
  focus: {
    outline: `2px solid ${baseColor}`,
    outlineOffset: '2px',
  }
});

// Pre-defined button styles for common colors
export const buttonStyles = {
  yellow: getButtonStyles(colors.yellow, '#000'),
  green: getButtonStyles(colors.green, '#fff'),
  purple: getButtonStyles(colors.purple, '#fff'),
  orange: getButtonStyles(colors.orange, '#fff'),
  blue: getButtonStyles(colors.brightBlue, '#000'),
  red: getButtonStyles(colors.red, '#fff'),
  gray: getButtonStyles(colors.darkGray, '#fff'),
};

// MUI sx prop style objects
export const muiButtonStyles = {
  yellow: {
    backgroundColor: colors.yellow,
    color: '#000',
    '&:hover': {
      backgroundColor: lightenColor(colors.yellow, 10),
    },
    '&:active': {
      backgroundColor: darkenColor(colors.yellow, 10),
    },
    '&:disabled': {
      backgroundColor: colors.yellow + '4D',
      color: '#00000080',
    },
    '&:focus': {
      outline: `2px solid ${colors.yellow}`,
      outlineOffset: '2px',
    }
  },
  // Add more as needed
};