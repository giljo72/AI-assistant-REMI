// Common styles for prompt panels to ensure consistency and better UI/UX

export const promptPanelStyles = {
  // Main container
  container: {
    marginBottom: 2
  },
  
  // Collapsed state header
  collapsedHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    mb: 1.5,
    padding: '10px 14px',
    backgroundColor: '#0a0f1c',
    borderRadius: '6px',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    transition: 'all 0.2s ease',
    '&:hover': {
      backgroundColor: '#0d1220',
      borderColor: 'rgba(212, 175, 55, 0.3)'
    }
  },
  
  // Title typography
  title: {
    fontSize: '0.95rem',
    fontWeight: 600,
    marginRight: 1,
    color: '#d4af37'
  },
  
  // Active indicator dot
  activeDot: {
    width: 6,
    height: 6,
    borderRadius: '50%',
    display: 'inline-block',
    marginRight: 1
  },
  
  // Panel paper
  paper: {
    backgroundColor: '#0a0f1c', // Very dark background
    color: '#ffffff',
    borderRadius: '8px',
    border: '1px solid rgba(255, 255, 255, 0.1)', // Subtle border
    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)', // Dark shadow
    overflow: 'hidden',
    mb: 2
  },
  
  // Panel header
  panelHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: 'transparent',
    padding: '14px 18px',
    borderBottom: '1px solid rgba(255, 255, 255, 0.1)' // Subtle border
  },
  
  // Header title
  headerTitle: {
    fontSize: '1.1rem',
    fontWeight: 700,
    color: '#d4af37' // gold color for headers
  },
  
  // Add button
  addButton: {
    fontSize: '0.875rem',
    padding: '6px 16px',
    backgroundColor: 'transparent',
    color: '#d4af37',
    border: '1px solid rgba(212, 175, 55, 0.5)',
    transition: 'all 0.2s ease',
    '&:hover': {
      backgroundColor: 'rgba(212, 175, 55, 0.1)',
      borderColor: '#d4af37'
    }
  },
  
  // List container
  list: {
    maxHeight: '300px',
    overflow: 'auto',
    padding: '4px 0',
    '&::-webkit-scrollbar': {
      width: '6px',
    },
    '&::-webkit-scrollbar-track': {
      backgroundColor: 'rgba(255, 255, 255, 0.02)',
    },
    '&::-webkit-scrollbar-thumb': {
      backgroundColor: 'rgba(255, 255, 255, 0.2)',
      borderRadius: '3px',
      '&:hover': {
        backgroundColor: 'rgba(255, 255, 255, 0.3)',
      }
    }
  },
  
  // List item
  listItem: {
    padding: '10px 16px',
    transition: 'all 0.2s ease',
    '&:hover': {
      backgroundColor: 'rgba(255, 255, 255, 0.05)'
    }
  },
  
  // List item text
  listItemPrimary: {
    fontSize: '0.95rem',
    lineHeight: 1.5,
    fontWeight: 500
  },
  
  // List item secondary text
  listItemSecondary: {
    fontSize: '0.75rem', // 12px
    color: 'rgba(255, 255, 255, 0.7)',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    display: '-webkit-box',
    WebkitLineClamp: 1,
    WebkitBoxOrient: 'vertical',
    lineHeight: 1.3
  },
  
  // Icon buttons
  iconButton: {
    padding: '6px',
    color: 'rgba(255, 255, 255, 0.5)',
    transition: 'all 0.2s ease',
    '&:hover': {
      color: '#d4af37',
      backgroundColor: 'rgba(255, 255, 255, 0.05)'
    },
    '& svg': {
      fontSize: '1.25rem'
    }
  },
  
  // Checkbox
  checkbox: {
    padding: '6px',
    color: 'rgba(255, 255, 255, 0.3)',
    transition: 'all 0.2s ease',
    '&.Mui-checked': {
      color: '#d4af37'
    },
    '&:hover': {
      backgroundColor: 'rgba(255, 255, 255, 0.05)'
    }
  },
  
  // Modal styles
  modalTitle: {
    fontSize: '1.25rem' // Reduced modal title size
  },
  
  modalTextField: {
    '& .MuiInputBase-root': {
      fontSize: '0.875rem' // Smaller input text
    },
    '& .MuiInputLabel-root': {
      fontSize: '0.875rem' // Smaller label
    }
  }
};

// Color constants
export const promptColors = {
  gold: '#d4af37',
  goldHover: '#b4941f',
  navy: '#1a2b47',
  darkNavy: '#152238',
  white: '#ffffff',
  danger: '#f44336'
};