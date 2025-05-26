import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
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
  Button,
  Tooltip,
  CircularProgress,
  Chip,
} from '@mui/material';
import { Icon } from '../common/Icon';
import { RootState, AppDispatch } from '../../store';
import {
  fetchSystemPrompts,
  activateSystemPrompt,
  createSystemPrompt,
  updateSystemPrompt,
  deleteSystemPrompt,
  seedDefaultSystemPrompts,
} from '../../store/systemPromptsSlice';
import SystemPromptModal from '../modals/SystemPromptModal';
import { promptPanelStyles, promptColors } from '../common/promptStyles';

const SystemPromptManager: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { prompts, activePrompt, loading, error } = useSelector(
    (state: RootState) => state.systemPrompts
  );
  
  const [modalOpen, setModalOpen] = useState(false);
  const [editingPrompt, setEditingPrompt] = useState<any>(null);
  const [savingPrompt, setSavingPrompt] = useState(false);

  useEffect(() => {
    // Fetch system prompts on mount
    dispatch(fetchSystemPrompts());
    
    // Seed defaults if no prompts exist
    if (prompts.length === 0) {
      dispatch(seedDefaultSystemPrompts());
    }
  }, [dispatch]);

  const handleOpenAddModal = () => {
    setEditingPrompt(null);
    setModalOpen(true);
  };

  const handleOpenEditModal = (prompt: any) => {
    setEditingPrompt(prompt);
    setModalOpen(true);
  };

  const handleCloseModal = () => {
    setModalOpen(false);
    setEditingPrompt(null);
  };

  const handleSavePrompt = async (
    name: string,
    content: string,
    description?: string,
    category?: string
  ) => {
    setSavingPrompt(true);
    try {
      if (editingPrompt) {
        await dispatch(
          updateSystemPrompt({
            id: editingPrompt.id,
            data: { name, content, description, category },
          })
        ).unwrap();
      } else {
        await dispatch(
          createSystemPrompt({ name, content, description, category })
        ).unwrap();
      }
      handleCloseModal();
    } catch (err) {
      console.error('Error saving system prompt:', err);
    } finally {
      setSavingPrompt(false);
    }
  };

  const handleDeletePrompt = async () => {
    if (!editingPrompt) return;
    
    try {
      await dispatch(deleteSystemPrompt(editingPrompt.id)).unwrap();
      handleCloseModal();
    } catch (err) {
      console.error('Error deleting system prompt:', err);
    }
  };

  const handleActivatePrompt = async (promptId: string) => {
    try {
      await dispatch(activateSystemPrompt(promptId)).unwrap();
    } catch (err) {
      console.error('Error activating system prompt:', err);
    }
  };

  return (
    <Box>
      <Paper elevation={3} sx={promptPanelStyles.paper}>
        <Box sx={promptPanelStyles.panelHeader}>
          <Typography sx={promptPanelStyles.headerTitle}>System Prompts</Typography>
          <Tooltip title="Add Prompt">
            <IconButton
              onClick={handleOpenAddModal}
              sx={{ ...promptPanelStyles.iconButton, color: promptColors.gold }}
            >
              <Icon name="add" size={20} />
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
                      No system prompts created yet
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
                        checked={prompt.is_active}
                        onChange={() => handleActivatePrompt(prompt.id)}
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
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography 
                            sx={{ 
                              ...promptPanelStyles.listItemPrimary,
                              fontWeight: prompt.is_active ? 'bold' : 'normal',
                              color: prompt.is_active ? promptColors.gold : '#ffffff'
                            }}
                          >
                            {prompt.name}
                          </Typography>
                          {prompt.is_default && (
                            <Chip 
                              label="Default" 
                              size="small" 
                              sx={{ 
                                height: '18px',
                                fontSize: '0.65rem',
                                backgroundColor: 'rgba(212, 175, 55, 0.2)',
                                color: promptColors.gold,
                                border: `1px solid ${promptColors.gold}`,
                              }} 
                            />
                          )}
                        </Box>
                      }
                      secondary={
                        prompt.description && (
                          <Typography sx={promptPanelStyles.listItemSecondary}>
                            {prompt.description}
                          </Typography>
                        )
                      }
                    />
                  </ListItem>
                </React.Fragment>
              ))
            )}
          </List>
        )}
      </Paper>

      <SystemPromptModal
        open={modalOpen}
        onClose={handleCloseModal}
        onSave={handleSavePrompt}
        initialName={editingPrompt?.name || ''}
        initialContent={editingPrompt?.content || ''}
        initialDescription={editingPrompt?.description || ''}
        initialCategory={editingPrompt?.category || 'general'}
        editMode={!!editingPrompt}
        isDefault={editingPrompt?.is_default || false}
        onDelete={editingPrompt && !editingPrompt.is_default ? handleDeletePrompt : undefined}
        isSaving={savingPrompt}
      />
    </Box>
  );
};

export default SystemPromptManager;