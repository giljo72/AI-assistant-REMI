import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Checkbox,
  Divider,
  Button,
  Tooltip
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon
} from '@mui/icons-material';
import UserPromptModal from '../modals/UserPromptModal';

// Define the user prompt interface
export interface UserPrompt {
  id: string;
  name: string;
  content: string;
  active: boolean;
}

interface UserPromptManagerProps {
  prompts: UserPrompt[];
  onAddPrompt: (prompt: Omit<UserPrompt, 'id'>) => void;
  onUpdatePrompt: (prompt: UserPrompt) => void;
  onDeletePrompt: (id: string) => void;
  onActivatePrompt: (id: string, active: boolean) => void;
}

const UserPromptManager: React.FC<UserPromptManagerProps> = ({
  prompts,
  onAddPrompt,
  onUpdatePrompt,
  onDeletePrompt,
  onActivatePrompt
}) => {
  const [modalOpen, setModalOpen] = useState(false);
  const [editingPrompt, setEditingPrompt] = useState<UserPrompt | null>(null);

  const handleOpenAddModal = () => {
    setEditingPrompt(null);
    setModalOpen(true);
  };

  const handleOpenEditModal = (prompt: UserPrompt) => {
    setEditingPrompt(prompt);
    setModalOpen(true);
  };

  const handleCloseModal = () => {
    setModalOpen(false);
    setEditingPrompt(null);
  };

  const handleSavePrompt = (name: string, content: string) => {
    if (editingPrompt) {
      // Update existing prompt
      onUpdatePrompt({
        ...editingPrompt,
        name,
        content
      });
    } else {
      // Add new prompt
      onAddPrompt({
        name,
        content,
        active: false
      });
    }
  };

  const handleDeletePrompt = () => {
    if (editingPrompt) {
      onDeletePrompt(editingPrompt.id);
    }
  };

  const handleToggleActive = (prompt: UserPrompt) => {
    // If activating this prompt, deactivate all others
    if (!prompt.active) {
      prompts.forEach(p => {
        if (p.id !== prompt.id && p.active) {
          onActivatePrompt(p.id, false);
        }
      });
    }
    onActivatePrompt(prompt.id, !prompt.active);
  };

  return (
    <Box>
      <Paper
        elevation={3}
        sx={{
          backgroundColor: '#1a2b47', // Navy background
          color: '#ffffff',
          borderRadius: '8px',
          overflow: 'hidden'
        }}
      >
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            backgroundColor: '#152238', // Darker navy for header
            padding: '12px 16px',
            borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
          }}
        >
          <Typography variant="h6">User Prompts</Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleOpenAddModal}
            sx={{
              backgroundColor: '#d4af37', // Gold button
              color: '#000000',
              '&:hover': {
                backgroundColor: '#b4941f', // Darker gold on hover
              }
            }}
          >
            Add Prompt
          </Button>
        </Box>

        <List sx={{ maxHeight: '300px', overflow: 'auto' }}>
          {prompts.length === 0 ? (
            <ListItem>
              <ListItemText 
                primary="No prompts created yet" 
                sx={{ color: 'rgba(255, 255, 255, 0.7)' }}
              />
            </ListItem>
          ) : (
            prompts.map((prompt, index) => (
              <React.Fragment key={prompt.id}>
                {index > 0 && <Divider sx={{ backgroundColor: 'rgba(255, 255, 255, 0.1)' }} />}
                <ListItem
                  secondaryAction={
                    <Box>
                      <Tooltip title="Edit Prompt">
                        <IconButton 
                          edge="end" 
                          aria-label="edit"
                          onClick={() => handleOpenEditModal(prompt)}
                          sx={{ color: '#d4af37' }}
                        >
                          <EditIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete Prompt">
                        <IconButton 
                          edge="end" 
                          aria-label="delete"
                          onClick={() => {
                            if (window.confirm(`Are you sure you want to delete "${prompt.name}"?`)) {
                              onDeletePrompt(prompt.id);
                            }
                          }}
                          sx={{ color: '#f44336' }}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  }
                >
                  <ListItemIcon>
                    <Checkbox
                      edge="start"
                      checked={prompt.active}
                      onChange={() => handleToggleActive(prompt)}
                      sx={{
                        color: 'rgba(255, 255, 255, 0.7)',
                        '&.Mui-checked': {
                          color: '#d4af37',
                        },
                      }}
                    />
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Typography 
                        sx={{ 
                          fontWeight: prompt.active ? 'bold' : 'normal',
                          color: prompt.active ? '#d4af37' : '#ffffff'
                        }}
                      >
                        {prompt.name}
                      </Typography>
                    }
                    secondary={
                      <Typography 
                        variant="body2" 
                        sx={{ 
                          color: 'rgba(255, 255, 255, 0.7)',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          display: '-webkit-box',
                          WebkitLineClamp: 1,
                          WebkitBoxOrient: 'vertical',
                        }}
                      >
                        {prompt.content}
                      </Typography>
                    }
                  />
                </ListItem>
              </React.Fragment>
            ))
          )}
        </List>
      </Paper>

      <UserPromptModal
        open={modalOpen}
        onClose={handleCloseModal}
        onSave={handleSavePrompt}
        initialName={editingPrompt?.name || ''}
        initialPrompt={editingPrompt?.content || ''}
        editMode={!!editingPrompt}
        onDelete={editingPrompt ? handleDeletePrompt : undefined}
      />
    </Box>
  );
};

export default UserPromptManager;