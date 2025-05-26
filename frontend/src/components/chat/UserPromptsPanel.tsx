import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import {
  Box,
  Collapse,
  Paper,
  Typography,
  IconButton,
  Tooltip
} from '@mui/material';
import UserPromptManager, { UserPrompt } from './UserPromptManager';
import UserPromptIndicator from './UserPromptIndicator';
import { RootState } from '../../store';
import { Icon } from '../common/Icon';
import {
  addPrompt,
  updatePrompt,
  deletePrompt,
  activatePrompt,
  deactivatePrompt
} from '../../store/userPromptsSlice';
import { promptPanelStyles, promptColors } from '../common/promptStyles';

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
    <Box sx={promptPanelStyles.container}>
      {/* Collapsed state header */}
      {!isExpanded && (
        <Box sx={promptPanelStyles.collapsedHeader}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Typography 
              sx={{ 
                ...promptPanelStyles.title,
                color: promptColors.gold,
              }}
            >
              User Prompts
            </Typography>
            
            {activePrompt && (
              <Tooltip title={activePrompt.name}>
                <Box 
                  component="span" 
                  sx={{ 
                    ...promptPanelStyles.activeDot,
                    backgroundColor: promptColors.gold,
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
                  ...promptPanelStyles.iconButton,
                  color: promptColors.gold,
                  marginRight: 0.5
                }}
              >
                <Icon name="add" size={18} />
              </IconButton>
            </Tooltip>
            
            <Tooltip title="Expand User Prompts Panel">
              <IconButton
                size="small"
                onClick={handleToggleExpand}
                sx={{ 
                  ...promptPanelStyles.iconButton,
                  color: promptColors.gold 
                }}
              >
                <Icon name="dropdownClose" size={18} />
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
        <Paper elevation={3} sx={promptPanelStyles.paper}>
          <Box sx={promptPanelStyles.panelHeader}>
            <Typography sx={{ ...promptPanelStyles.headerTitle, color: promptColors.gold }}>
              User Prompts
            </Typography>
            
            <Tooltip title="Collapse Panel">
              <IconButton
                onClick={handleToggleExpand}
                sx={{ ...promptPanelStyles.iconButton, color: promptColors.gold }}
              >
                <Icon name="dropdownOpen" size={18} />
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