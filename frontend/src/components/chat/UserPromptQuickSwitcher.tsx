import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import {
  Box,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Radio,
  Divider,
  ClickAwayListener,
  Popper,
  Typography
} from '@mui/material';
import { RootState } from '../../store';
import { setActiveUserPrompt } from '../../store/chatSettingsSlice';
import { activatePrompt, deactivatePrompt } from '../../store/userPromptsSlice';
import { userPromptService } from '../../services';
import type { UserPrompt } from '../../services/userPromptService';

interface UserPromptQuickSwitcherProps {
  isOpen: boolean;
  anchorEl: HTMLElement | null;
  onClose: () => void;
  activeUserPromptName?: string;
  isUserPromptEnabled?: boolean;
  onManagePrompts?: () => void;
}

const UserPromptQuickSwitcher: React.FC<UserPromptQuickSwitcherProps> = ({
  isOpen,
  anchorEl,
  onClose,
  onManagePrompts
}) => {
  const dispatch = useDispatch();
  const { prompts, activePromptId } = useSelector((state: RootState) => state.userPrompts);
  const currentChatId = useSelector((state: RootState) => state.chatSettings.currentChatId);

  const handleSelectPrompt = async (prompt: UserPrompt) => {
    try {
      // Activate this prompt
      await userPromptService.activateUserPrompt(prompt.id);
      
      // Update Redux state
      dispatch(activatePrompt(prompt.id));
      
      // Update chat settings if we're in a chat
      if (currentChatId) {
        dispatch(setActiveUserPrompt({
          id: prompt.id,
          name: prompt.name
        }));
      }
      
      onClose();
    } catch (error) {
      console.error('Failed to activate user prompt:', error);
    }
  };

  const handleDisableUserPrompt = async () => {
    try {
      // Deactivate current prompt if any
      if (activePromptId) {
        await userPromptService.updateUserPrompt(activePromptId, {
          is_active: false
        });
        
        // Update Redux state
        dispatch(deactivatePrompt(activePromptId));
      }
      
      // Clear from chat settings if we're in a chat
      if (currentChatId) {
        dispatch(setActiveUserPrompt({
          id: null,
          name: null
        }));
      }
      
      onClose();
    } catch (error) {
      console.error('Failed to disable user prompt:', error);
    }
  };

  if (!isOpen || !anchorEl) return null;

  return (
    <Popper
      open={isOpen}
      anchorEl={anchorEl}
      placement="top"
      style={{ zIndex: 1300 }}
    >
      <ClickAwayListener onClickAway={onClose}>
        <Paper
          elevation={8}
          sx={{
            backgroundColor: '#0a0f1c', // Much darker background to match Context Controls
            border: '1px solid rgba(212, 175, 55, 0.3)', // Subtle gold border
            borderRadius: '8px',
            minWidth: '280px',
            maxWidth: '380px',
            maxHeight: '450px',
            overflow: 'hidden',
            boxShadow: '0 4px 20px rgba(0, 0, 0, 0.5)' // Dark shadow
          }}
        >
          <Box sx={{ 
            padding: '16px 20px', 
            borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
            backgroundColor: 'transparent'
          }}>
            <Typography 
              variant="h6" 
              sx={{ 
                color: '#d4af37',
                fontWeight: 600,
                fontSize: '1.1rem',
                letterSpacing: '0.02em'
              }}
            >
              User Prompt Selection
            </Typography>
          </Box>
          
          <List sx={{ padding: 0, maxHeight: '300px', overflow: 'auto' }}>
            {/* Disable option */}
            <ListItem
              onClick={handleDisableUserPrompt}
              sx={{
                padding: '12px 20px',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                '&:hover': {
                  backgroundColor: 'rgba(255, 255, 255, 0.05)'
                }
              }}
            >
              <ListItemIcon sx={{ minWidth: 36 }}>
                <Radio
                  edge="start"
                  checked={!activePromptId}
                  sx={{
                    padding: '4px',
                    color: 'rgba(255, 255, 255, 0.4)',
                    '&.Mui-checked': {
                      color: '#d4af37',
                    },
                  }}
                />
              </ListItemIcon>
              <ListItemText 
                primary="Disable User Prompt"
                sx={{ 
                  '& .MuiListItemText-primary': { 
                    color: 'rgba(255, 255, 255, 0.7)',
                    fontSize: '0.95rem',
                    fontWeight: 500
                  } 
                }}
              />
            </ListItem>
            
            {prompts.length > 0 && <Divider sx={{ backgroundColor: 'rgba(255, 255, 255, 0.1)', margin: '0' }} />}
            
            {/* User prompts */}
            {prompts.map((prompt) => (
              <ListItem
                key={prompt.id}
                onClick={() => handleSelectPrompt(prompt)}
                sx={{
                  padding: '12px 20px',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  backgroundColor: prompt.id === activePromptId ? 'rgba(255, 255, 255, 0.05)' : 'transparent',
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.05)'
                  }
                }}
              >
                <ListItemIcon sx={{ minWidth: 36 }}>
                  <Radio
                    edge="start"
                    checked={prompt.id === activePromptId}
                    sx={{
                      padding: '4px',
                      color: 'rgba(255, 255, 255, 0.4)',
                      '&.Mui-checked': {
                        color: '#d4af37',
                      },
                    }}
                  />
                </ListItemIcon>
                <ListItemText 
                  primary={prompt.name}
                  secondary={prompt.description ? prompt.description.substring(0, 50) + '...' : ''}
                  sx={{ 
                    '& .MuiListItemText-primary': { 
                      color: '#ffffff',
                      fontSize: '0.95rem',
                      fontWeight: prompt.id === activePromptId ? 600 : 400
                    },
                    '& .MuiListItemText-secondary': { 
                      color: 'rgba(255, 255, 255, 0.6)',
                      fontSize: '0.8rem',
                      marginTop: '2px'
                    }
                  }}
                />
              </ListItem>
            ))}
            
            {prompts.length === 0 && (
              <ListItem sx={{ padding: '24px' }}>
                <ListItemText 
                  primary="No user prompts created"
                  secondary="Click 'Manage User Prompts' below to create one"
                  sx={{ 
                    textAlign: 'center',
                    '& .MuiListItemText-primary': { 
                      color: 'rgba(255, 255, 255, 0.6)',
                      fontSize: '0.95rem',
                      fontWeight: 500
                    },
                    '& .MuiListItemText-secondary': { 
                      color: 'rgba(255, 255, 255, 0.4)',
                      fontSize: '0.85rem',
                      marginTop: '4px'
                    }
                  }}
                />
              </ListItem>
            )}
          </List>
          
          {/* Footer with manage prompts link */}
          {onManagePrompts && (
            <>
              <Divider sx={{ backgroundColor: 'rgba(255, 255, 255, 0.1)' }} />
              <Box 
                sx={{ 
                  padding: '12px 20px',
                  backgroundColor: 'transparent',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.05)'
                  }
                }}
                onClick={() => {
                  onManagePrompts();
                  onClose();
                }}
              >
                <Typography 
                  sx={{ 
                    color: '#d4af37',
                    fontSize: '0.875rem',
                    fontWeight: 500,
                    textAlign: 'center',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '6px'
                  }}
                >
                  Manage User Prompts
                  <span style={{ fontSize: '1rem' }}>→</span>
                </Typography>
              </Box>
            </>
          )}
        </Paper>
      </ClickAwayListener>
    </Popper>
  );
};

export default UserPromptQuickSwitcher;