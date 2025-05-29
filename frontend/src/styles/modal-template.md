# Modal/Popup Window Styling Guide

## Default Modal Template

This guide defines the standard styling for all modal/popup windows in the AI Assistant application, based on the Contacts modal design.

### Complete Color Palette
```scss
// Primary Colors
$background: #0E1C2D;        // Main background
$white: #FFFFFF;             // Pure white
$white-gray: #C2C1C1;        // White-gray
$dark-gray: #706E6E;         // Dark gray

// Yellows
$yellow: #FCC000;            // Primary yellow
$dark-yellow: #66500E;       // Dark yellow

// Blues
$faded-blue: #315074;        // Faded blue
$faded-blue-2: #182739;      // Faded blue 2
$faded-blue-3: #1E3147;      // Faded blue 3
$faded-bright-blue: #8F97B7; // Faded bright blue
$bright-blue: #32CEFF;       // Bright blue
$dark-bright-blue: #2b38dd;  // Dark bright blue

// Greens
$green: #67BD6D;             // Green
$dark-green: #3A703E;        // Dark green

// Reds
$red: #CF5362;               // Red
$dark-red: #79202B;          // Dark red

// Oranges
$orange: #FF8B21;            // Orange
$dark-orange: #8F520C;       // Dark orange

// Purples
$purple: #BD46EF;            // Purple
$dark-purple: #6C238B;       // Dark purple

// Legacy Colors (for compatibility)
$modal-bg: #080d13;          // Main modal background (darkest navy)
$header-bg: #121922;         // Header/title bar background (sidebar color)
$card-bg: #121922;           // Card/content block background
$form-bg: #121922;           // Form container background
$text-primary: #fff;         // Primary text (white)
$text-secondary: #888;       // Secondary text (gray)
$text-accent: #d4af37;       // Accent text (gold)
$text-description: #3E5B8F;  // Description text (muted blue)
$border-primary: #1a2b47;    // Primary border color
$border-accent: #FFC300;     // Accent border (yellow)
```

### Font Information

#### Font Colors
- **Headlines/Titles**: Yellow (#FCC000)
- **Body Text**: White-gray (#C2C1C1)
- **Button Labels**: Yellow (#FCC000)
- **Code/Monospace**: Keep existing styling
- **Disabled Text**: Dark Gray (#706E6E)

#### Font Sizes & Weights
- Keep all existing font sizes and weights as currently implemented
- Maintain consistency across the application

### Button States

For all buttons, define hover/active states based on their base color:

```scss
// Yellow buttons (#FCC000)
.btn-yellow {
  background: #FCC000;
  &:hover { background: lighten(#FCC000, 10%); }
  &:active { background: darken(#FCC000, 10%); }
  &:disabled { background: rgba(#FCC000, 0.3); color: rgba(#000, 0.5); }
  &:focus { outline: 2px solid #FCC000; outline-offset: 2px; }
}

// Apply same pattern for other colored buttons:
// Green (#67BD6D), Purple (#BD46EF), Orange (#FF8B21)
// Blue (#32CEFF), Gray (#706E6E), Red (#CF5362)
```

### Form Styling

#### Input Fields
- **Borders**: Use defined blues (Faded Blue #315074, Faded Blue 3 #1E3147)
- **Border Radius**: 1px for input fields
- **Error Messages**: 
  - Text: Red (#CF5362)
  - Background (if needed): Dark Red (#79202B)

### Link Colors

#### Internal Navigation Links
- **Default**: Yellow (#FCC000)
- **Hover**: Lighter yellow
- **Visited**: Yellow (#FCC000) - stays consistent
- **Active**: Yellow (#FCC000)

#### External Website Links
- **Default**: Bright Blue (#32CEFF)
- **Hover**: Purple (#BD46EF)
- **Visited**: Dark Bright Blue (#2b38dd)
- **Active**: Bright Blue (#32CEFF)

### Border Radius Standards
- **Buttons**: 2px
- **Cards/Panels**: 2px
- **Input Fields**: 1px
- **Modals**: 2px

### Status Colors
- **Success**: Green (#67BD6D)
- **Warning**: Orange (#FF8B21)
- **Error**: Red (#CF5362)
- **Info**: White (#FFFFFF)

### Loading States
- **Spinners**: Yellow (#FCC000)
- **Progress Bars**: Keep existing performance dashboard styling
- **Skeleton Screens**: Use Faded Blue 2 (#182739) with shimmer effect

### Icon Guidelines
- **Primary Icon Color**: Yellow (#FCC000)
- **Disabled Icons**: Dark Gray (#706E6E)
- **Sizes**: Keep existing (16px small, 20-24px medium, 32-48px large)
- **Hover Effects**: Keep existing implementation

### Modal Structure Template

```tsx
const StandardModal = ({ open, onClose, title, description }) => {
  return (
    <Modal open={open} onClose={onClose} aria-labelledby="modal-title">
      <Box sx={{
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        width: '90%',
        maxWidth: 800,
        maxHeight: '90vh',
        bgcolor: '#080d13',              // Darkest navy background
        border: '2px solid #1a2b47',
        borderRadius: 2,
        boxShadow: 24,
        display: 'flex',
        flexDirection: 'column',
      }}>
        {/* Fixed Header - Non-scrollable */}
        <Box sx={{ 
          p: 3, 
          borderBottom: '1px solid #1a2b47',
          backgroundColor: '#121922'     // Sidebar color
        }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: description ? 2 : 0 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Typography variant="h5" sx={{ color: '#d4af37', fontWeight: 'bold' }}>
                {title}
              </Typography>
              {/* Action buttons go here - e.g., Add button */}
              <IconButton
                size="small"
                onClick={handleAction}
                sx={{ color: '#d4af37', '&:hover': { backgroundColor: 'rgba(212, 175, 55, 0.1)' } }}
                title="Action tooltip"
              >
                <Icon name="add" size={20} />
              </IconButton>
            </Box>
            <IconButton
              aria-label="close"
              onClick={onClose}
              sx={{ color: '#d4af37' }}
            >
              <Icon name="close" size={24} />
            </IconButton>
          </Box>
          {description && (
            <Typography variant="body2" sx={{ color: '#3E5B8F', fontSize: '13px' }}>
              {description}
            </Typography>
          )}
        </Box>
        
        {/* Scrollable Content */}
        <Box sx={{ p: 3, overflowY: 'auto', flex: 1, backgroundColor: '#080d13' }}>
          {/* Content goes here */}
        </Box>
      </Box>
    </Modal>
  );
};
```

### Component Styling Guidelines

#### Cards/Content Blocks
```tsx
<Card sx={{ 
  mb: 2, 
  backgroundColor: '#121922',      // Same as sidebar
  border: '1px solid #1a2b47' 
}}>
```

#### Form Containers
```tsx
<Box sx={{ 
  mt: 2, 
  p: 2, 
  backgroundColor: '#121922', 
  borderRadius: 2, 
  border: '1px solid #1a2b47' 
}}>
```

#### Primary Buttons
```tsx
<Button
  variant="contained"
  sx={{
    backgroundColor: '#d4af37',
    color: '#000',
    '&:hover': {
      backgroundColor: '#b8941c'
    },
    '&:disabled': {
      backgroundColor: 'rgba(212, 175, 55, 0.3)',
      color: 'rgba(0, 0, 0, 0.5)'
    }
  }}
>
```

#### Secondary Buttons
```tsx
<Button
  variant="outlined"
  sx={{ 
    color: '#fff',
    borderColor: '#d4af37',
    '&:hover': {
      borderColor: '#d4af37',
      backgroundColor: 'rgba(212, 175, 55, 0.1)'
    }
  }}
>
```

#### Badges/Chips
```tsx
// Standard badge with yellow outline
<Chip 
  label={label} 
  size="small" 
  sx={{ 
    backgroundColor: '#1a2b47',
    border: '2px solid #FFC300',
    color: '#FFC300'
  }}
/>

// Visibility/status badges
<Chip 
  label={label} 
  icon={<Icon name={iconName} size={14} />}
  size="small" 
  sx={{ 
    backgroundColor: color + '22',  // 22 = ~13% opacity
    color: color
  }}
/>
```

#### Form Fields
```tsx
const fieldStyles = {
  '& .MuiInputLabel-root': { color: '#d4af37' },
  '& .MuiOutlinedInput-root': {
    color: '#fff',
    '& fieldset': { borderColor: '#1a2b47' },
    '&:hover fieldset': { borderColor: '#d4af37' },
    '&.Mui-focused fieldset': { borderColor: '#d4af37' }
  },
  '& .MuiSelect-icon': { color: '#d4af37' }
};

<TextField sx={{ mb: 2, ...fieldStyles }} />
```

#### Icon Buttons
```tsx
<IconButton
  size="small"
  onClick={handleAction}
  sx={{ 
    color: '#d4af37',
    '&:hover': { 
      backgroundColor: 'rgba(212, 175, 55, 0.1)' 
    }
  }}
>
  <Icon name="iconName" size={18} />
</IconButton>
```

### Icon Usage Guidelines

1. **Prefer SVG Icons**: Use the custom Icon component with SVG files
2. **Standard Sizes**: 
   - Small actions: 16px
   - Normal actions: 18-20px
   - Close button: 24px
3. **Hover Effects**: All icon buttons should have subtle hover backgrounds
4. **Tooltips**: Always include title attributes for accessibility

### Typography Guidelines

```tsx
// Modal Title
<Typography variant="h5" sx={{ color: '#d4af37', fontWeight: 'bold' }}>

// Section Headers
<Typography variant="h6" sx={{ color: '#d4af37' }}>

// Descriptions
<Typography variant="body2" sx={{ color: '#3E5B8F', fontSize: '13px' }}>

// Primary Text
<Typography sx={{ color: '#fff' }}>

// Secondary Text
<Typography sx={{ color: '#888' }}>

// Accent Text (e.g., "Currently:")
<Typography sx={{ color: '#d4af37' }}>
```

### Spacing Guidelines

- **Modal padding**: `p: 3` (24px)
- **Card spacing**: `mb: 2` (16px)
- **Section dividers**: `<Divider sx={{ my: 1 }} />`
- **Tight spacing**: Use `0.25` (2px) to `0.5` (4px) for minimal gaps
- **Form field spacing**: `mb: 2` (16px)

### Best Practices

1. **Fixed Headers**: Keep titles, descriptions, and primary actions in non-scrollable areas
2. **Dark Backgrounds**: Use `#080d13` for main backgrounds, `#121922` for content blocks
3. **Gold Accents**: Use `#d4af37` for interactive elements and important text
4. **Consistent Borders**: Use `#1a2b47` for subtle borders
5. **Icon-First**: Prefer icons with tooltips over text-only buttons
6. **Hover States**: Always provide visual feedback on interactive elements

### Example Implementation

See `/frontend/src/components/modals/PersonalProfilesModal.tsx` for a complete implementation following these guidelines.