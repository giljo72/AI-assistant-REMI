import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Typography,
  IconButton
} from '@mui/material';
import { promptColors } from '../common/promptStyles';
import { Icon } from '../common/Icon';

interface SystemPromptModalProps {
  open: boolean;
  onClose: () => void;
  onSave: (name: string, content: string, description?: string) => Promise<void>;
  initialName?: string;
  initialContent?: string;
  initialDescription?: string;
  editMode?: boolean;
  isDefault?: boolean;
  onDelete?: () => Promise<void>;
  isSaving?: boolean;
}

const SystemPromptModal: React.FC<SystemPromptModalProps> = ({
  open,
  onClose,
  onSave,
  initialName = '',
  initialContent = '',
  initialDescription = '',
  editMode = false,
  isDefault = false,
  onDelete,
  isSaving = false,
}) => {
  const [name, setName] = useState(initialName);
  const [content, setContent] = useState(initialContent);
  const [description, setDescription] = useState(initialDescription);
  const [errors, setErrors] = useState<{ name?: string; content?: string }>({});
  const [showPromptHelp, setShowPromptHelp] = useState(false);

  useEffect(() => {
    if (open) {
      setName(initialName);
      setContent(initialContent);
      setDescription(initialDescription);
      setErrors({});
    }
  }, [open, initialName, initialContent, initialDescription]);

  const validate = () => {
    const newErrors: { name?: string; content?: string } = {};
    
    if (!name.trim()) {
      newErrors.name = 'Name is required';
    }
    
    if (!content.trim()) {
      newErrors.content = 'Content is required';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSave = async () => {
    if (validate()) {
      await onSave(name.trim(), content.trim(), description.trim() || undefined);
    }
  };

  const handleDelete = async () => {
    if (onDelete && window.confirm(`Are you sure you want to delete "${name}"?`)) {
      await onDelete();
    }
  };

  const handleCancel = () => {
    // Only show confirmation if there are changes and we're not currently saving
    if (!isSaving && (name !== initialName || content !== initialContent || description !== initialDescription)) {
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
        },
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
          {editMode ? 'Modify System Prompt' : 'Add System Prompt'}
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
            onChange={(e) => {
              setName(e.target.value);
              if (e.target.value.trim()) {
                setErrors(prev => ({ ...prev, name: undefined }));
              }
            }}
            error={!!errors.name}
            helperText={errors.name}
            disabled={isDefault}
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
                '&.Mui-disabled': {
                  '& input': {
                    color: '#706E6E',
                    WebkitTextFillColor: '#706E6E',
                  },
                },
              },
              '& .MuiFormHelperText-root': {
                color: 'error.main',
              },
            }}
          />
        </Box>

        <Box sx={{ mb: 3 }}>
          <Typography 
            variant="subtitle1" 
            sx={{ 
              mb: 1, 
              color: '#FFC000', // Gold from tailwind
              fontWeight: 500
            }}
          >
            Description (optional)
          </Typography>
          <TextField
            fullWidth
            placeholder="Enter description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            disabled={isDefault}
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
                '&.Mui-disabled': {
                  '& input': {
                    color: '#706E6E',
                    WebkitTextFillColor: '#706E6E',
                  },
                },
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
              {showPromptHelp ? 'Hide Help' : 'What are System Prompts?'}
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
                <strong>System Prompts</strong> define the AI's core behavior and personality:
              </Typography>
              <Box component="ul" sx={{ color: '#d0d0d0', fontSize: '0.875rem', pl: 2, mb: 0 }}>
                <li>Set the AI's role and expertise level</li>
                <li>Define response style and tone</li>
                <li>Establish behavioral guidelines</li>
                <li>Configure output formatting preferences</li>
              </Box>
              <Typography variant="body2" sx={{ color: '#ffffff', mt: 1 }}>
                <strong>System vs User Prompts:</strong> System prompts establish the AI's fundamental behavior, while User prompts add personal preferences on top.
              </Typography>
            </Box>
          )}
          
          <TextField
            fullWidth
            multiline
            rows={10}
            placeholder="Enter your system prompt here..."
            value={content}
            onChange={(e) => {
              setContent(e.target.value);
              if (e.target.value.trim()) {
                setErrors(prev => ({ ...prev, content: undefined }));
              }
            }}
            error={!!errors.content}
            helperText={errors.content}
            disabled={isDefault}
            sx={{
              '& .MuiOutlinedInput-root': {
                backgroundColor: '#080d13', // Navy default
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
                '&.Mui-disabled': {
                  '& textarea': {
                    color: '#706E6E',
                    WebkitTextFillColor: '#706E6E',
                  },
                },
              },
            }}
          />
        </Box>

        {isDefault && (
          <Box sx={{ mt: 2, p: 2, backgroundColor: 'rgba(212, 175, 55, 0.1)', borderRadius: 1 }}>
            <Typography variant="caption" sx={{ color: promptColors.gold }}>
              This is a default system prompt and cannot be edited or deleted.
            </Typography>
          </Box>
        )}
      </DialogContent>

      <DialogActions sx={{ 
        padding: '16px 24px',
        borderTop: '1px solid rgba(255, 255, 255, 0.1)',
        backgroundColor: '#152238', // Darker navy for footer
        display: 'flex',
        justifyContent: 'space-between'
      }}>
        <Box>
          {editMode && !isDefault && onDelete && (
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
          {!isDefault && (
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
          )}
        </Box>
      </DialogActions>
    </Dialog>
  );
};

export default SystemPromptModal;