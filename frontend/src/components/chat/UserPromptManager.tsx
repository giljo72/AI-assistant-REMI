import React, { useState, useEffect } from 'react';
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
  Tooltip,
  CircularProgress
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon
} from '@mui/icons-material';
import UserPromptModal from '../modals/UserPromptModal';
import { userPromptService, UserPrompt } from '../../services';
import { promptPanelStyles, promptColors } from '../common/promptStyles';

interface UserPromptManagerProps {
  projectId?: string; // Optional project ID for project-specific prompts
  onError?: (message: string) => void;
}

const UserPromptManager: React.FC<UserPromptManagerProps> = ({
  projectId,
  onError
}) => {
  const [prompts, setPrompts] = useState<UserPrompt[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingPrompt, setEditingPrompt] = useState<UserPrompt | null>(null);
  const [savingPrompt, setSavingPrompt] = useState(false);

  // Fetch prompts on component mount and when projectId changes
  useEffect(() => {
    const fetchPrompts = async () => {
      setLoading(true);
      try {
        let fetchedPrompts;
        if (projectId) {
          fetchedPrompts = await userPromptService.getUserPromptsForProject(projectId);
        } else {
          fetchedPrompts = await userPromptService.getAllUserPrompts();
        }
        setPrompts(fetchedPrompts);
      } catch (err) {
        console.error("Error fetching user prompts:", err);
        if (onError) {
          onError("Failed to load user prompts");
        }
      } finally {
        setLoading(false);
      }
    };

    fetchPrompts();
  }, [projectId, onError]);

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

  const handleSavePrompt = async (name: string, content: string) => {
    setSavingPrompt(true);
    try {
      if (editingPrompt) {
        // Update existing prompt
        const updatedPrompt = await userPromptService.updateUserPrompt(editingPrompt.id, {
          name,
          content,
          project_id: projectId
        });
        
        // Update local state
        setPrompts(prevPrompts => 
          prevPrompts.map(p => p.id === updatedPrompt.id ? updatedPrompt : p)
        );
      } else {
        // Add new prompt
        const newPrompt = await userPromptService.createUserPrompt({
          name,
          content,
          project_id: projectId
        });
        
        // Update local state
        setPrompts(prevPrompts => [...prevPrompts, newPrompt]);
      }
      
      // Close modal
      handleCloseModal();
    } catch (err) {
      console.error("Error saving user prompt:", err);
      if (onError) {
        onError("Failed to save user prompt");
      }
    } finally {
      setSavingPrompt(false);
    }
  };

  const handleDeletePrompt = async () => {
    if (!editingPrompt) return;
    
    try {
      await userPromptService.deleteUserPrompt(editingPrompt.id);
      
      // Update local state
      setPrompts(prevPrompts => prevPrompts.filter(p => p.id !== editingPrompt.id));
      
      // Close modal
      handleCloseModal();
    } catch (err) {
      console.error("Error deleting user prompt:", err);
      if (onError) {
        onError("Failed to delete user prompt");
      }
    }
  };

  const handleToggleActive = async (prompt: UserPrompt) => {
    try {
      if (!prompt.is_active) {
        // Activate this prompt
        await userPromptService.activateUserPrompt(prompt.id);
        
        // Update local state - activate this prompt and deactivate all others
        setPrompts(prevPrompts => 
          prevPrompts.map(p => ({
            ...p,
            is_active: p.id === prompt.id
          }))
        );
      } else {
        // Deactivate this prompt (note: backend might not support this)
        // We'll need to handle this differently in a real implementation
        const updatedPrompt = await userPromptService.updateUserPrompt(prompt.id, {
          is_active: false
        });
        
        // Update local state
        setPrompts(prevPrompts => 
          prevPrompts.map(p => p.id === updatedPrompt.id ? updatedPrompt : p)
        );
      }
    } catch (err) {
      console.error("Error toggling user prompt active state:", err);
      if (onError) {
        onError("Failed to update user prompt");
      }
    }
  };

  return (
    <Box>
      <Paper elevation={3} sx={promptPanelStyles.paper}>
        <Box sx={promptPanelStyles.panelHeader}>
          <Typography sx={promptPanelStyles.headerTitle}>User Prompts</Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleOpenAddModal}
            size="small"
            sx={promptPanelStyles.addButton}
          >
            Add Prompt
          </Button>
        </Box>

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', padding: 3 }}>
            <CircularProgress size={24} sx={{ color: promptColors.gold }} />
          </Box>
        ) : (
          <List sx={promptPanelStyles.list}>
            {prompts.length === 0 ? (
              <ListItem sx={promptPanelStyles.listItem}>
                <ListItemText 
                  primary={
                    <Typography sx={{ ...promptPanelStyles.listItemPrimary, color: 'rgba(255, 255, 255, 0.7)' }}>
                      No prompts created yet
                    </Typography>
                  }
                />
              </ListItem>
            ) : (
              prompts.map((prompt, index) => (
                <React.Fragment key={prompt.id}>
                  {index > 0 && <Divider sx={{ backgroundColor: 'rgba(255, 255, 255, 0.1)' }} />}
                  <ListItem
                    sx={promptPanelStyles.listItem}
                    secondaryAction={
                      <Box>
                        <Tooltip title="Edit Prompt">
                          <IconButton 
                            edge="end" 
                            aria-label="edit"
                            onClick={() => handleOpenEditModal(prompt)}
                            sx={{ ...promptPanelStyles.iconButton, color: promptColors.gold }}
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
                                setEditingPrompt(prompt);
                                handleDeletePrompt();
                              }
                            }}
                            sx={{ ...promptPanelStyles.iconButton, color: promptColors.danger }}
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
                        checked={prompt.is_active}
                        onChange={() => handleToggleActive(prompt)}
                        sx={promptPanelStyles.checkbox}
                      />
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Typography 
                          sx={{ 
                            ...promptPanelStyles.listItemPrimary,
                            fontWeight: prompt.is_active ? 'bold' : 'normal',
                            color: prompt.is_active ? promptColors.gold : '#ffffff'
                          }}
                        >
                          {prompt.name}
                        </Typography>
                      }
                      secondary={
                        <Typography sx={promptPanelStyles.listItemSecondary}>
                          {prompt.content}
                        </Typography>
                      }
                    />
                  </ListItem>
                </React.Fragment>
              ))
            )}
          </List>
        )}
      </Paper>

      <UserPromptModal
        open={modalOpen}
        onClose={handleCloseModal}
        onSave={handleSavePrompt}
        initialName={editingPrompt?.name || ''}
        initialPrompt={editingPrompt?.content || ''}
        editMode={!!editingPrompt}
        onDelete={editingPrompt ? handleDeletePrompt : undefined}
        isSaving={savingPrompt}
      />
    </Box>
  );
};

export default UserPromptManager;