import React, { useState, useEffect } from 'react';
import { 
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  TextField,
  Typography,
  IconButton,
  // Paper  rem'd out until we need it
} from '@mui/material';
import { 
  Close as CloseIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';

interface UserPromptModalProps {
  open: boolean;
  onClose: () => void;
  onSave: (name: string, prompt: string) => void;
  initialName?: string;
  initialPrompt?: string;
  editMode?: boolean;
  onDelete?: () => void;
}

const UserPromptModal: React.FC<UserPromptModalProps> = ({
  open,
  onClose,
  onSave,
  initialName = '',
  initialPrompt = '',
  editMode = false,
  onDelete
}) => {
  const [name, setName] = useState(initialName);
  const [prompt, setPrompt] = useState(initialPrompt);
  const [nameError, setNameError] = useState('');

  useEffect(() => {
    if (open) {
      setName(initialName);
      setPrompt(initialPrompt);
      setNameError('');
    }
  }, [open, initialName, initialPrompt]);

  const handleSave = () => {
    if (!name.trim()) {
      setNameError('Prompt name is required');
      return;
    }
    
    onSave(name, prompt);
    onClose();
  };

  const handleDelete = () => {
    if (onDelete) {
      onDelete();
      onClose();
    }
  };

  const handleCancel = () => {
    // Show confirmation if there are changes
    if (name !== initialName || prompt !== initialPrompt) {
      if (window.confirm('Are you sure you want to discard your changes?')) {
        onClose();
      }
    } else {
      onClose();
    }
  };

  return (
    <Dialog 
      open={open} 
      onClose={handleCancel}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: '8px',
          backgroundColor: '#1a2b47', // Navy background
          color: '#ffffff'
        }
      }}
    >
      <DialogTitle sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
        backgroundColor: '#152238' // Darker navy for header
      }}>
        <Typography variant="h6" component="div">
          {editMode ? 'Modify User Prompt' : 'Add User Prompt'}
        </Typography>
        <IconButton 
          edge="end" 
          color="inherit" 
          onClick={handleCancel} 
          aria-label="close"
          sx={{ color: '#ffffff' }}
        >
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      <DialogContent sx={{ 
        padding: '24px',
        backgroundColor: '#1a2b47' // Navy background
      }}>
        <Box sx={{ mb: 3 }}>
          <Typography 
            variant="subtitle1" 
            sx={{ 
              mb: 1, 
              color: '#d4af37' // Gold color for labels
            }}
          >
            Prompt Name
          </Typography>
          <TextField
            fullWidth
            placeholder="Enter prompt name"
            value={name}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                setName(e.target.value);
                if (e.target.value.trim()) {
                    setNameError('');
                 }
            }}
            error={!!nameError}
            helperText={nameError}
            sx={{
              '& .MuiOutlinedInput-root': {
                '& fieldset': {
                  borderColor: 'rgba(255, 255, 255, 0.23)',
                },
                '&:hover fieldset': {
                  borderColor: '#d4af37',
                },
                '&.Mui-focused fieldset': {
                  borderColor: '#d4af37',
                },
                '& input': {
                  color: '#ffffff',
                },
              },
              '& .MuiFormHelperText-root': {
                color: 'error.main',
              },
            }}
          />
        </Box>

        <Box>
          <Typography 
            variant="subtitle1" 
            sx={{ 
              mb: 1, 
              color: '#d4af37' // Gold color for labels
            }}
          >
            Prompt Content
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={10}
            placeholder="Enter your prompt here..."
            value={prompt}
            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setPrompt(e.target.value)}
            sx={{
              '& .MuiOutlinedInput-root': {
                '& fieldset': {
                  borderColor: 'rgba(255, 255, 255, 0.23)',
                },
                '&:hover fieldset': {
                  borderColor: '#d4af37',
                },
                '&.Mui-focused fieldset': {
                  borderColor: '#d4af37',
                },
                '& textarea': {
                  color: '#ffffff',
                },
              },
            }}
          />
        </Box>
      </DialogContent>

      <DialogActions sx={{ 
        padding: '16px 24px',
        borderTop: '1px solid rgba(255, 255, 255, 0.1)',
        backgroundColor: '#152238', // Darker navy for footer
        display: 'flex',
        justifyContent: 'space-between'
      }}>
        <Box>
          {editMode && onDelete && (
            <Button
              variant="outlined"
              color="error"
              startIcon={<DeleteIcon />}
              onClick={handleDelete}
              sx={{
                borderColor: '#f44336',
                color: '#f44336',
                '&:hover': {
                  backgroundColor: 'rgba(244, 67, 54, 0.08)',
                  borderColor: '#f44336',
                }
              }}
            >
              Delete Prompt
            </Button>
          )}
        </Box>
        <Box>
          <Button 
            onClick={handleCancel}
            sx={{ 
              color: '#ffffff',
              marginRight: 2,
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 0.08)',
              }
            }}
          >
            Cancel
          </Button>
          <Button 
            onClick={handleSave}
            variant="contained"
            sx={{ 
              backgroundColor: '#d4af37', // Gold button
              color: '#000000',
              '&:hover': {
                backgroundColor: '#b4941f', // Darker gold on hover
              }
            }}
          >
            {editMode ? 'Update' : 'Add'}
          </Button>
        </Box>
      </DialogActions>
    </Dialog>
  );
};

export default UserPromptModal;