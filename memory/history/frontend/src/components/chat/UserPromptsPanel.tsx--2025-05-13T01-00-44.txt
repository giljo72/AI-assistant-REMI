import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import {
  Box,
  // Button, A rem we save for later and address later
  Collapse,
  Paper,
  Typography,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  ChevronRight as ChevronRightIcon,
  ChevronLeft as ChevronLeftIcon,
  Add as AddIcon
} from '@mui/icons-material';
import UserPromptManager, { UserPrompt } from './UserPromptManager';
import UserPromptIndicator from './UserPromptIndicator';
import { RootState } from '../../store';
import {
  addPrompt,
  updatePrompt,
  deletePrompt,
  activatePrompt,
  deactivatePrompt
} from '../../store/userPromptsSlice';

interface UserPromptsPanelProps {
  expanded?: boolean;
  onToggleExpand?: () => void;
}

const UserPromptsPanel: React.FC<UserPromptsPanelProps> = ({
  expanded = false,
  onToggleExpand
}) => {
  const dispatch = useDispatch();
  const { prompts } = useSelector((state: RootState) => state.userPrompts);
  const activePrompt = prompts.find((p: UserPrompt) => p.active) || null;
  
  // Local expanding state if not controlled externally
  const [localExpanded, setLocalExpanded] = useState(expanded);
  const isExpanded = onToggleExpand ? expanded : localExpanded;
  
  const handleToggleExpand = () => {
    if (onToggleExpand) {
      onToggleExpand();
    } else {
      setLocalExpanded(!localExpanded);
    }
  };
  
  const handleAddPrompt = (newPrompt: Omit<typeof prompts[0], 'id'>) => {
    dispatch(addPrompt(newPrompt));
  };
  
  const handleUpdatePrompt = (updatedPrompt: typeof prompts[0]) => {
    dispatch(updatePrompt(updatedPrompt));
  };
  
  const handleDeletePrompt = (id: string) => {
    dispatch(deletePrompt(id));
  };
  
  const handleActivatePrompt = (id: string, active: boolean) => {
    if (active) {
      dispatch(activatePrompt(id));
    } else {
      dispatch(deactivatePrompt(id));
    }
  };
  
  const handleDeactivatePrompt = () => {
    if (activePrompt) {
      dispatch(deactivatePrompt(activePrompt.id));
    }
  };

  return (
    <Box sx={{ marginBottom: 2 }}>
      {/* Collapse button when panel is not expanded */}
      {!isExpanded && (
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Typography 
              variant="subtitle1" 
              sx={{ 
                color: '#d4af37',
                fontWeight: 'bold',
                marginRight: 1
              }}
            >
              User Prompts
            </Typography>
            
            {activePrompt && (
              <Tooltip title={activePrompt.name}>
                <Box 
                  component="span" 
                  sx={{ 
                    width: 8, 
                    height: 8, 
                    backgroundColor: '#d4af37', 
                    borderRadius: '50%',
                    display: 'inline-block',
                    marginRight: 1
                  }} 
                />
              </Tooltip>
            )}
          </Box>
          
          <Box>
            <Tooltip title="Add User Prompt">
              <IconButton
                size="small"
                onClick={() => handleToggleExpand()}
                sx={{ 
                  color: '#d4af37',
                  marginRight: 1
                }}
              >
                <AddIcon fontSize="small" />
              </IconButton>
            </Tooltip>
            
            <Tooltip title="Expand User Prompts Panel">
              <IconButton
                size="small"
                onClick={handleToggleExpand}
                sx={{ color: '#d4af37' }}
              >
                <ChevronRightIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
      )}

      {/* User Prompt Indicator (when not expanded but a prompt is active) */}
      {!isExpanded && activePrompt && (
        <UserPromptIndicator
          activePrompt={activePrompt}
          onDeactivate={handleDeactivatePrompt}
        />
      )}

      {/* Expanded Panel */}
      <Collapse in={isExpanded} timeout="auto">
        <Paper
          elevation={3}
          sx={{
            backgroundColor: '#1a2b47', // Navy background
            color: '#ffffff',
            borderRadius: '8px',
            overflow: 'hidden',
            mb: 2
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
            <Typography variant="h6" sx={{ color: '#d4af37' }}>User Prompts</Typography>
            
            <Tooltip title="Collapse Panel">
              <IconButton
                onClick={handleToggleExpand}
                sx={{ color: '#d4af37' }}
              >
                <ChevronLeftIcon />
              </IconButton>
            </Tooltip>
          </Box>
          
          <Box sx={{ padding: 2 }}>
            <UserPromptManager
              prompts={prompts}
              onAddPrompt={handleAddPrompt}
              onUpdatePrompt={handleUpdatePrompt}
              onDeletePrompt={handleDeletePrompt}
              onActivatePrompt={handleActivatePrompt}
            />
          </Box>
        </Paper>
      </Collapse>
    </Box>
  );
};

export default UserPromptsPanel;