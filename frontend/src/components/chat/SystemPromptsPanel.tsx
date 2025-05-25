import React, { useState } from 'react';
import { useSelector } from 'react-redux';
import {
  Box,
  Collapse,
  Paper,
  Typography,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  ChevronRight as ChevronRightIcon,
  ChevronLeft as ChevronLeftIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';
import SystemPromptManager from './SystemPromptManager';
import { RootState } from '../../store';
import { promptPanelStyles, promptColors } from '../common/promptStyles';

interface SystemPromptsPanelProps {
  expanded?: boolean;
  onToggleExpand?: () => void;
}

const SystemPromptsPanel: React.FC<SystemPromptsPanelProps> = ({
  expanded = false,
  onToggleExpand
}) => {
  const { activePrompt } = useSelector((state: RootState) => state.systemPrompts);
  
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
                <SettingsIcon fontSize="small" />
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
                <ChevronRightIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
      )}

      {/* Active prompt indicator (when collapsed) */}
      {!isExpanded && activePrompt && (
        <Box sx={{ 
          mb: 1.5, 
          px: 1, 
          py: 0.5, 
          backgroundColor: 'rgba(212, 175, 55, 0.1)', 
          borderRadius: 1,
          border: `1px solid ${promptColors.gold}`,
        }}>
          <Typography sx={{ 
            fontSize: '0.75rem', 
            color: promptColors.gold,
            display: 'flex',
            alignItems: 'center',
            gap: 0.5
          }}>
            <Box component="span" sx={{ fontWeight: 'bold' }}>Active:</Box>
            {activePrompt.name}
            {activePrompt.category && (
              <Box 
                component="span" 
                sx={{ 
                  fontSize: '0.65rem', 
                  opacity: 0.8,
                  ml: 0.5 
                }}
              >
                ({activePrompt.category})
              </Box>
            )}
          </Typography>
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
                <ChevronLeftIcon />
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