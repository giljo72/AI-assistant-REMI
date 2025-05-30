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
  CircularProgress
} from '@mui/material';
import { Icon } from '../common/Icon';

interface UserPromptModalProps {
  open: boolean;
  onClose: () => void;
  onSave: (name: string, prompt: string) => void;
  initialName?: string;
  initialPrompt?: string;
  editMode?: boolean;
  onDelete?: () => void;
  isSaving?: boolean;
}

const UserPromptModal: React.FC<UserPromptModalProps> = ({
  open,
  onClose,
  onSave,
  initialName = '',
  initialPrompt = '',
  editMode = false,
  onDelete,
  isSaving = false
}) => {
  const [name, setName] = useState(initialName);
  const [prompt, setPrompt] = useState(initialPrompt);
  const [nameError, setNameError] = useState('');
  const [showPromptHelp, setShowPromptHelp] = useState(false);

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
  };

  const handleDelete = () => {
    if (onDelete) {
      onDelete();
    }
  };

  const handleCancel = () => {
    // Only show confirmation if there are changes and we're not currently saving
    if (!isSaving && (name !== initialName || prompt !== initialPrompt)) {
      if (window.confirm('Are you sure you want to discard your changes?')) {
        onClose();
      }
    } else if (!isSaving) {
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
          borderRadius: '16px',
          backgroundColor: '#121922', // Navy-light from tailwind
          color: '#ffffff',
          border: '2px solid #FFC000', // 2px yellow border
        }
      }}
    >
      <DialogTitle sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        borderBottom: '1px solid #FFC000', // Gold border to match design
        backgroundColor: '#1e2735', // Navy-lighter from tailwind
        padding: '16px 24px'
      }}>
        <Typography variant="h6" component="div" sx={{ color: '#FFC000', fontWeight: 'bold' }}>
          {editMode ? 'Modify User Prompt' : 'Add User Prompt'}
        </Typography>
        <IconButton 
          edge="end" 
          color="inherit" 
          onClick={handleCancel} 
          aria-label="close"
          disabled={isSaving}
          sx={{ color: '#ffffff' }}
        >
          <Icon name="close" size={24} />
        </IconButton>
      </DialogTitle>

      <DialogContent sx={{ 
        padding: '24px',
        backgroundColor: '#121922' // Navy-light from tailwind
      }}>
        <Box sx={{ mb: 3 }}>
          <Typography 
            variant="subtitle1" 
            sx={{ 
              mb: 1, 
              color: '#FFC000', // Gold from tailwind
              fontWeight: 500
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
            disabled={isSaving}
            sx={{
              '& .MuiOutlinedInput-root': {
                backgroundColor: '#080d13', // Navy default
                '& fieldset': {
                  borderColor: 'rgba(255, 192, 0, 0.3)', // Transparent gold
                },
                '&:hover fieldset': {
                  borderColor: '#FFC000',
                },
                '&.Mui-focused fieldset': {
                  borderColor: '#FFC000',
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
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
            <Typography 
              variant="subtitle1" 
              sx={{ 
                color: '#FFC000', // Gold from tailwind
              fontWeight: 500
              }}
            >
              Prompt Content
            </Typography>
            <Button
              size="small"
              onClick={() => setShowPromptHelp(!showPromptHelp)}
              sx={{ color: '#FFC000', textTransform: 'none', fontSize: '0.875rem' }}
            >
              {showPromptHelp ? 'Hide Help' : 'What are Prompts?'}
            </Button>
          </Box>
          
          {showPromptHelp && (
            <Box sx={{ 
              mb: 2, 
              p: 2, 
              backgroundColor: '#080d13', // Navy default
              borderRadius: 1,
              border: '1px solid rgba(255, 192, 0, 0.3)' // Transparent gold
            }}>
              <Typography variant="body2" sx={{ color: '#ffffff', mb: 1 }}>
                <strong>Prompts</strong> guide the AI's personality, tone, and response style:
              </Typography>
              <Box component="ul" sx={{ color: '#d0d0d0', fontSize: '0.875rem', pl: 2, mb: 0 }}>
                <li>Set communication style (formal, casual, technical)</li>
                <li>Define response format (concise, detailed, step-by-step)</li>
                <li>Add domain expertise (act as a Python expert, creative writer)</li>
                <li>Control behavior (be helpful, avoid certain topics)</li>
              </Box>
              <Typography variant="body2" sx={{ color: '#ffffff', mt: 1 }}>
                <strong>Prompts vs Context:</strong> Prompts shape HOW the AI responds, while Context (in Mode settings) determines WHAT information it can access.
              </Typography>
            </Box>
          )}
          
          <TextField
            fullWidth
            multiline
            rows={10}
            placeholder="Enter your prompt here..."
            value={prompt}
            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setPrompt(e.target.value)}
            disabled={isSaving}
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
              startIcon={<Icon name="trash" size={16} />}
              onClick={handleDelete}
              disabled={isSaving}
              sx={{
                borderColor: 'rgba(244, 67, 54, 0.5)',
                color: '#ff6b6b',
                backgroundColor: 'transparent',
                '&:hover': {
                  backgroundColor: 'rgba(244, 67, 54, 0.1)',
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
            disabled={isSaving}
            sx={{ 
              color: '#ffffff',
              marginRight: 2,
              backgroundColor: 'transparent',
              border: '1px solid rgba(255, 255, 255, 0.3)',
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 0.05)',
                borderColor: 'rgba(255, 255, 255, 0.5)',
              }
            }}
          >
            Cancel
          </Button>
          <Button 
            onClick={handleSave}
            variant="contained"
            disabled={isSaving}
            startIcon={isSaving ? <CircularProgress size={20} color="inherit" /> : null}
            sx={{ 
              backgroundColor: '#FFC000', // Gold from tailwind
              color: '#080d13', // Navy text on gold
              fontWeight: 'medium',
              '&:hover': {
                backgroundColor: '#e6ac00', // Darker gold on hover
              },
              '&:disabled': {
                backgroundColor: 'rgba(255, 192, 0, 0.5)',
              }
            }}
          >
            {isSaving 
              ? (editMode ? 'Updating...' : 'Adding...') 
              : (editMode ? 'Update' : 'Add')
            }
          </Button>
        </Box>
      </DialogActions>
    </Dialog>
  );
};

export default UserPromptModal;