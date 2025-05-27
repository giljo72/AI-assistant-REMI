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
  Radio,
  Divider,
  Tooltip,
  CircularProgress
} from '@mui/material';
import { Icon } from '../common/Icon';
import UserPromptModal from '../modals/UserPromptModal';
import { userPromptService } from '../../services';
import type { UserPrompt } from '../../services/userPromptService';
import { promptPanelStyles, promptColors } from '../common/promptStyles';

import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../../store';
import { setActiveUserPrompt } from '../../store/chatSettingsSlice';
import { 
  setPrompts, 
  activatePrompt as activatePromptAction, 
  deactivatePrompt,
  setLoading as setReduxLoading,
  setError as setReduxError
} from '../../store/userPromptsSlice';

interface UserPromptManagerProps {
  projectId?: string; // Optional project ID for project-specific prompts
  onError?: (message: string) => void;
}

const UserPromptManager: React.FC<UserPromptManagerProps> = ({
  projectId,
  onError
}) => {
  const [modalOpen, setModalOpen] = useState(false);
  const [editingPrompt, setEditingPrompt] = useState<UserPrompt | null>(null);
  const [savingPrompt, setSavingPrompt] = useState(false);
  
  const dispatch = useDispatch();
  const currentChatId = useSelector((state: RootState) => state.chatSettings.currentChatId);
  const prompts = useSelector((state: RootState) => state.userPrompts.prompts);
  const activePromptId = useSelector((state: RootState) => state.userPrompts.activePromptId);
  const loading = useSelector((state: RootState) => state.userPrompts.loading);


  // Fetch prompts on component mount and when projectId changes
  useEffect(() => {
    const fetchPrompts = async () => {
      dispatch(setReduxLoading(true));
      try {
        let fetchedPrompts;
        if (projectId) {
          fetchedPrompts = await userPromptService.getUserPromptsForProject(projectId);
        } else {
          fetchedPrompts = await userPromptService.getAllUserPrompts();
        }
        // Update Redux store
        dispatch(setPrompts(fetchedPrompts));
      } catch (err) {
        console.error("Error fetching user prompts:", err);
        dispatch(setReduxError("Failed to load user prompts"));
        if (onError) {
          onError("Failed to load user prompts");
        }
      } finally {
        dispatch(setReduxLoading(false));
      }
    };

    fetchPrompts();
  }, [projectId, onError, dispatch]);

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
        await userPromptService.updateUserPrompt(editingPrompt.id, {
          name,
          content,
          project_id: projectId
        });
      } else {
        // Add new prompt
        await userPromptService.createUserPrompt({
          name,
          content,
          project_id: projectId
        });
      }
      
      // Re-fetch prompts to ensure sync with backend
      const fetchedPrompts = projectId 
        ? await userPromptService.getUserPromptsForProject(projectId)
        : await userPromptService.getAllUserPrompts();
      dispatch(setPrompts(fetchedPrompts));
      
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
      
      // Re-fetch prompts to ensure sync with backend
      const fetchedPrompts = projectId 
        ? await userPromptService.getUserPromptsForProject(projectId)
        : await userPromptService.getAllUserPrompts();
      dispatch(setPrompts(fetchedPrompts));
      
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
      const isCurrentlyActive = prompt.id === activePromptId;
      
      if (!isCurrentlyActive) {
        // Activate this prompt
        await userPromptService.activateUserPrompt(prompt.id);
        
        // Update Redux state
        dispatch(activatePromptAction(prompt.id));
        
        // Update chat settings if we're in a chat
        if (currentChatId) {
          dispatch(setActiveUserPrompt({
            id: prompt.id,
            name: prompt.name
          }));
        }
      } else {
        // Deactivate this prompt
        await userPromptService.updateUserPrompt(prompt.id, {
          is_active: false
        });
        
        // Update Redux state
        dispatch(deactivatePrompt(prompt.id));
        
        // Clear from chat settings if we're in a chat
        if (currentChatId) {
          dispatch(setActiveUserPrompt({
            id: null,
            name: null
          }));
        }
      }
      
      // Re-fetch prompts to ensure sync with backend
      const fetchedPrompts = projectId 
        ? await userPromptService.getUserPromptsForProject(projectId)
        : await userPromptService.getAllUserPrompts();
      dispatch(setPrompts(fetchedPrompts));
      
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
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'center', 
          padding: '8px 16px',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
        }}>
          <Tooltip title="Add User Prompt">
            <IconButton
              onClick={handleOpenAddModal}
              sx={{ 
                color: promptColors.gold,
                padding: '12px',
                transition: 'all 0.2s ease',
                '&:hover': {
                  backgroundColor: 'rgba(212, 175, 55, 0.1)',
                  transform: 'scale(1.1)'
                },
                '& svg': {
                  fontSize: '2rem' // 50% larger
                }
              }}
            >
              <Icon name="add" size={30} />
            </IconButton>
          </Tooltip>
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
                  >
                    <ListItemIcon sx={{ display: 'flex', alignItems: 'center', minWidth: 'auto', marginRight: 1 }}>
                      <Radio
                        edge="start"
                        checked={prompt.id === activePromptId}
                        onChange={() => handleToggleActive(prompt)}
                        sx={{
                          padding: '4px',
                          color: 'rgba(255, 255, 255, 0.7)',
                          '&.Mui-checked': {
                            color: promptColors.gold,
                          },
                        }}
                      />
                      <Tooltip title="Edit Prompt">
                        <IconButton 
                          size="small"
                          aria-label="edit"
                          onClick={() => handleOpenEditModal(prompt)}
                          sx={{ 
                            ...promptPanelStyles.iconButton, 
                            color: promptColors.gold,
                            padding: '4px',
                            marginLeft: 0.5
                          }}
                        >
                          <Icon name="userEdit" size={21} />
                        </IconButton>
                      </Tooltip>
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Typography 
                          sx={{ 
                            ...promptPanelStyles.listItemPrimary,
                            fontWeight: prompt.id === activePromptId ? 'bold' : 'normal',
                            color: prompt.id === activePromptId ? promptColors.gold : '#ffffff'
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
export type { UserPrompt };