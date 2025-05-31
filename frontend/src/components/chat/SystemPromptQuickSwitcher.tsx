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
  Typography,
  Chip
} from '@mui/material';
import { RootState } from '../../store';
import { setActiveSystemPrompt } from '../../store/systemPromptsSlice';

interface SystemPromptQuickSwitcherProps {
  isOpen: boolean;
  anchorEl: HTMLElement | null;
  onClose: () => void;
  onManagePrompts?: () => void;
}

const SystemPromptQuickSwitcher: React.FC<SystemPromptQuickSwitcherProps> = ({
  isOpen,
  anchorEl,
  onClose,
  onManagePrompts
}) => {
  const dispatch = useDispatch();
  const { prompts, activePrompt } = useSelector((state: RootState) => state.systemPrompts);

  const handleSelectPrompt = (promptId: string) => {
    dispatch(setActiveSystemPrompt(promptId));
    onClose();
  };

  const handleDisableSystemPrompt = () => {
    dispatch(setActiveSystemPrompt(null));
    onClose();
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
            backgroundColor: '#0a0f1c',
            border: '1px solid rgba(212, 175, 55, 0.3)',
            borderRadius: '8px',
            minWidth: '280px',
            maxWidth: '380px',
            maxHeight: '450px',
            overflow: 'hidden',
            boxShadow: '0 4px 20px rgba(0, 0, 0, 0.5)'
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
              System Prompt Selection
            </Typography>
          </Box>
          
          <List sx={{ padding: 0, maxHeight: '300px', overflow: 'auto' }}>
            {/* Disable option */}
            <ListItem
              onClick={handleDisableSystemPrompt}
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
                  checked={!activePrompt}
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
                primary="Disable System Prompt"
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
            
            {/* System prompts */}
            {prompts.map((prompt) => (
              <ListItem
                key={prompt.id}
                onClick={() => handleSelectPrompt(prompt.id)}
                sx={{
                  padding: '12px 20px',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  backgroundColor: activePrompt?.id === prompt.id ? 'rgba(255, 255, 255, 0.05)' : 'transparent',
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.05)'
                  }
                }}
              >
                <ListItemIcon sx={{ minWidth: 36 }}>
                  <Radio
                    edge="start"
                    checked={activePrompt?.id === prompt.id}
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
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <span>{prompt.name}</span>
                      {prompt.is_default && (
                        <Chip 
                          label="Default" 
                          size="small"
                          sx={{
                            height: '20px',
                            fontSize: '0.7rem',
                            backgroundColor: 'rgba(212, 175, 55, 0.2)',
                            color: '#d4af37',
                            border: '1px solid rgba(212, 175, 55, 0.5)',
                          }} 
                        />
                      )}
                    </Box>
                  }
                  secondary={prompt.description || ''}
                  sx={{ 
                    '& .MuiListItemText-primary': { 
                      color: '#ffffff',
                      fontSize: '0.95rem',
                      fontWeight: activePrompt?.id === prompt.id ? 600 : 400
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
                  Manage System Prompts
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

export default SystemPromptQuickSwitcher;