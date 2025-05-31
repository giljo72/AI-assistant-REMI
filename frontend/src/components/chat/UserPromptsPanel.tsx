import React, { useState } from 'react';
import {
  Box,
  Collapse,
  Paper,
  Typography,
  IconButton,
  Tooltip
} from '@mui/material';
import UserPromptManager from './UserPromptManager';
import { Icon } from '../common/Icon';
import { promptPanelStyles, promptColors } from '../common/promptStyles';

interface UserPromptsPanelProps {
  expanded?: boolean;
  onToggleExpand?: () => void;
}

const UserPromptsPanel: React.FC<UserPromptsPanelProps> = ({
  expanded = false,
  onToggleExpand
}) => {
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
            <UserPromptManager />
          </Box>
        </Paper>
      </Collapse>
    </Box>
  );
};

export default UserPromptsPanel;