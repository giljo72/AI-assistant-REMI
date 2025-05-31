import React, { useState } from 'react';
import {
  Box,
  Collapse,
  Paper,
  Typography,
  IconButton,
  Tooltip
} from '@mui/material';
import SystemPromptManager from './SystemPromptManager';
import { promptPanelStyles, promptColors } from '../common/promptStyles';
import { Icon } from '../common/Icon';

interface SystemPromptsPanelProps {
  expanded?: boolean;
  onToggleExpand?: () => void;
}

const SystemPromptsPanel: React.FC<SystemPromptsPanelProps> = ({
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
              System Prompts
            </Typography>
          </Box>
          
          <Box>
            <Tooltip title="Configure System Prompts">
              <IconButton
                size="small"
                onClick={handleToggleExpand}
                sx={{ 
                  ...promptPanelStyles.iconButton,
                  color: promptColors.gold,
                  marginRight: 0.5
                }}
              >
                <Icon name="add" size={18} />
              </IconButton>
            </Tooltip>
            
            <Tooltip title="Expand System Prompts Panel">
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
              System Prompts
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
            <SystemPromptManager />
          </Box>
        </Paper>
      </Collapse>
    </Box>
  );
};

export default SystemPromptsPanel;