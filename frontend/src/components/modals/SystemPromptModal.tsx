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

interface SystemPromptModalProps {
  open: boolean;
  onClose: () => void;
  onSave: (name: string, content: string, description?: string, category?: string) => Promise<void>;
  initialName?: string;
  initialContent?: string;
  initialDescription?: string;
  initialCategory?: string;
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
  initialCategory = 'general',
  editMode = false,
  isDefault = false,
  onDelete,
  isSaving = false,
}) => {
  const [name, setName] = useState(initialName);
  const [content, setContent] = useState(initialContent);
  const [description, setDescription] = useState(initialDescription);
  const [category, setCategory] = useState(initialCategory);
  const [errors, setErrors] = useState<{ name?: string; content?: string }>({});

  useEffect(() => {
    if (open) {
      setName(initialName);
      setContent(initialContent);
      setDescription(initialDescription);
      setCategory(initialCategory || 'general');
      setErrors({});
    }
  }, [open, initialName, initialContent, initialDescription, initialCategory]);

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
      await onSave(name.trim(), content.trim(), description.trim() || undefined, category);
    }
  };

  const handleDelete = async () => {
    if (onDelete && window.confirm(`Are you sure you want to delete "${name}"?`)) {
      await onDelete();
    }
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          backgroundColor: '#1a2b47',
          color: '#ffffff',
          '& .Mui-disabled': {
            '& input, & textarea, & .MuiSelect-select': {
              color: 'rgba(255, 255, 255, 0.7) !important',
              WebkitTextFillColor: 'rgba(255, 255, 255, 0.7) !important',
            },
          },
        },
      }}
    >
      <DialogTitle sx={{ 
        backgroundColor: '#152238', 
        borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
        fontSize: '1.25rem',
        color: promptColors.gold
      }}>
        {editMode ? 'Edit System Prompt' : 'Add System Prompt'}
      </DialogTitle>
      
      <DialogContent sx={{ mt: 2, pt: 3 }}>
        <TextField
          fullWidth
          label="Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          error={!!errors.name}
          helperText={errors.name}
          disabled={isDefault}
          sx={{
            mb: 2,
            '& .MuiInputBase-root': {
              color: '#ffffff',
              fontSize: '0.875rem',
              '&.Mui-disabled': {
                color: 'rgba(255, 255, 255, 0.7)',
                WebkitTextFillColor: 'rgba(255, 255, 255, 0.7)',
                '& input': {
                  color: 'rgba(255, 255, 255, 0.7)',
                  WebkitTextFillColor: 'rgba(255, 255, 255, 0.7)',
                },
                '& textarea': {
                  color: 'rgba(255, 255, 255, 0.7)',
                  WebkitTextFillColor: 'rgba(255, 255, 255, 0.7)',
                },
              },
            },
            '& .MuiInputLabel-root': {
              color: promptColors.gold,
              fontSize: '0.875rem',
              '&.Mui-disabled': {
                color: promptColors.gold,
              },
            },
            '& .MuiOutlinedInput-root': {
              '& fieldset': {
                borderColor: '#ffffff',
              },
              '&:hover fieldset': {
                borderColor: promptColors.gold,
              },
              '&.Mui-focused fieldset': {
                borderColor: promptColors.gold,
              },
              '&.Mui-disabled': {
                '& fieldset': {
                  borderColor: 'rgba(255, 255, 255, 0.3)',
                },
                '& input, & textarea': {
                  color: 'rgba(255, 255, 255, 0.7) !important',
                  WebkitTextFillColor: 'rgba(255, 255, 255, 0.7) !important',
                },
              },
            },
          }}
        />

        <FormControl fullWidth sx={{ mb: 2 }}>
          <InputLabel sx={{ 
            color: promptColors.gold,
            fontSize: '0.875rem',
            '&.Mui-focused': {
              color: promptColors.gold,
            },
          }}>
            Category
          </InputLabel>
          <Select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            label="Category"
            disabled={isDefault}
            sx={{
              color: '#ffffff',
              fontSize: '0.875rem',
              '&.Mui-disabled': {
                color: 'rgba(255, 255, 255, 0.7)',
                WebkitTextFillColor: 'rgba(255, 255, 255, 0.7)',
                '& .MuiSelect-select': {
                  color: 'rgba(255, 255, 255, 0.7) !important',
                  WebkitTextFillColor: 'rgba(255, 255, 255, 0.7) !important',
                },
                '& .MuiOutlinedInput-notchedOutline': {
                  borderColor: 'rgba(255, 255, 255, 0.3)',
                },
              },
              '& .MuiOutlinedInput-notchedOutline': {
                borderColor: '#ffffff',
              },
              '&:hover .MuiOutlinedInput-notchedOutline': {
                borderColor: promptColors.gold,
              },
              '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                borderColor: promptColors.gold,
              },
              '& .MuiSvgIcon-root': {
                color: '#ffffff',
              },
              '&.Mui-disabled .MuiSvgIcon-root': {
                color: 'rgba(255, 255, 255, 0.7)',
              },
            }}
          >
            <MenuItem value="general">General</MenuItem>
            <MenuItem value="coding">Coding</MenuItem>
            <MenuItem value="creative">Creative</MenuItem>
            <MenuItem value="technical">Technical</MenuItem>
            <MenuItem value="business">Business</MenuItem>
          </Select>
        </FormControl>

        <TextField
          fullWidth
          label="Description (optional)"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          disabled={isDefault}
          sx={{
            mb: 2,
            '& .MuiInputBase-root': {
              color: '#ffffff',
              fontSize: '0.875rem',
              '&.Mui-disabled': {
                color: 'rgba(255, 255, 255, 0.7)',
                WebkitTextFillColor: 'rgba(255, 255, 255, 0.7)',
                '& input': {
                  color: 'rgba(255, 255, 255, 0.7)',
                  WebkitTextFillColor: 'rgba(255, 255, 255, 0.7)',
                },
                '& textarea': {
                  color: 'rgba(255, 255, 255, 0.7)',
                  WebkitTextFillColor: 'rgba(255, 255, 255, 0.7)',
                },
              },
            },
            '& .MuiInputLabel-root': {
              color: promptColors.gold,
              fontSize: '0.875rem',
              '&.Mui-disabled': {
                color: promptColors.gold,
              },
            },
            '& .MuiOutlinedInput-root': {
              '& fieldset': {
                borderColor: '#ffffff',
              },
              '&:hover fieldset': {
                borderColor: promptColors.gold,
              },
              '&.Mui-focused fieldset': {
                borderColor: promptColors.gold,
              },
              '&.Mui-disabled': {
                '& fieldset': {
                  borderColor: 'rgba(255, 255, 255, 0.3)',
                },
                '& input, & textarea': {
                  color: 'rgba(255, 255, 255, 0.7) !important',
                  WebkitTextFillColor: 'rgba(255, 255, 255, 0.7) !important',
                },
              },
            },
          }}
        />

        <TextField
          fullWidth
          label="System Prompt Content"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          error={!!errors.content}
          helperText={errors.content || 'Define how the AI assistant should behave'}
          multiline
          rows={10}
          disabled={isDefault}
          sx={{
            '& .MuiInputBase-root': {
              color: '#ffffff',
              fontSize: '0.875rem',
              '&.Mui-disabled': {
                color: 'rgba(255, 255, 255, 0.7)',
                WebkitTextFillColor: 'rgba(255, 255, 255, 0.7)',
                '& input': {
                  color: 'rgba(255, 255, 255, 0.7)',
                  WebkitTextFillColor: 'rgba(255, 255, 255, 0.7)',
                },
                '& textarea': {
                  color: 'rgba(255, 255, 255, 0.7)',
                  WebkitTextFillColor: 'rgba(255, 255, 255, 0.7)',
                },
              },
            },
            '& .MuiInputLabel-root': {
              color: promptColors.gold,
              fontSize: '0.875rem',
              '&.Mui-disabled': {
                color: promptColors.gold,
              },
            },
            '& .MuiOutlinedInput-root': {
              '& fieldset': {
                borderColor: '#ffffff',
              },
              '&:hover fieldset': {
                borderColor: promptColors.gold,
              },
              '&.Mui-focused fieldset': {
                borderColor: promptColors.gold,
              },
              '&.Mui-disabled': {
                '& fieldset': {
                  borderColor: 'rgba(255, 255, 255, 0.3)',
                },
                '& input, & textarea': {
                  color: 'rgba(255, 255, 255, 0.7) !important',
                  WebkitTextFillColor: 'rgba(255, 255, 255, 0.7) !important',
                },
              },
            },
            '& .MuiFormHelperText-root': {
              color: 'rgba(255, 255, 255, 0.7)',
              '&.Mui-disabled': {
                color: 'rgba(255, 255, 255, 0.7)',
              },
            },
          }}
        />

        {isDefault && (
          <Box sx={{ mt: 2, p: 2, backgroundColor: 'rgba(212, 175, 55, 0.1)', borderRadius: 1 }}>
            <Typography variant="caption" sx={{ color: promptColors.gold }}>
              This is a default system prompt and cannot be edited or deleted.
            </Typography>
          </Box>
        )}
      </DialogContent>

      <DialogActions sx={{ 
        backgroundColor: '#152238', 
        borderTop: '1px solid rgba(255, 255, 255, 0.1)',
        padding: 2
      }}>
        {editMode && !isDefault && onDelete && (
          <Button
            onClick={handleDelete}
            sx={{ 
              color: promptColors.danger,
              mr: 'auto'
            }}
          >
            Delete
          </Button>
        )}
        
        <Button 
          onClick={onClose}
          sx={{ color: 'rgba(255, 255, 255, 0.7)' }}
        >
          Cancel
        </Button>
        
        {!isDefault && (
          <Button
            onClick={handleSave}
            variant="contained"
            disabled={isSaving}
            sx={{
              backgroundColor: promptColors.gold,
              color: '#000000',
              '&:hover': {
                backgroundColor: promptColors.goldHover,
              },
              '&:disabled': {
                backgroundColor: 'rgba(212, 175, 55, 0.3)',
              },
            }}
          >
            {isSaving ? (
              <CircularProgress size={20} sx={{ color: '#000000' }} />
            ) : (
              editMode ? 'Save' : 'Add'
            )}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default SystemPromptModal;