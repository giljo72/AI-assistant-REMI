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
    mb: 1.5
  },
  
  // Title typography
  title: {
    fontSize: '0.875rem', // 14px - reduced from default
    fontWeight: 'bold',
    marginRight: 1
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
    backgroundColor: '#1a2b47',
    color: '#ffffff',
    borderRadius: '8px',
    overflow: 'hidden',
    mb: 2
  },
  
  // Panel header
  panelHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#152238',
    padding: '8px 12px', // Reduced from 12px 16px
    borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
  },
  
  // Header title
  headerTitle: {
    fontSize: '1rem', // 16px - reduced from h6
    fontWeight: 600
  },
  
  // Add button
  addButton: {
    fontSize: '0.75rem', // 12px
    padding: '4px 12px',
    backgroundColor: '#d4af37',
    color: '#000000',
    '&:hover': {
      backgroundColor: '#b4941f'
    }
  },
  
  // List container
  list: {
    maxHeight: '250px', // Reduced from 300px
    overflow: 'auto',
    padding: 0
  },
  
  // List item
  listItem: {
    padding: '8px 12px' // Reduced padding
  },
  
  // List item text
  listItemPrimary: {
    fontSize: '0.875rem', // 14px
    lineHeight: 1.4
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
    padding: '4px',
    '& svg': {
      fontSize: '1.2rem' // Smaller icons
    }
  },
  
  // Checkbox
  checkbox: {
    padding: '4px',
    color: 'rgba(255, 255, 255, 0.7)',
    '&.Mui-checked': {
      color: '#d4af37'
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