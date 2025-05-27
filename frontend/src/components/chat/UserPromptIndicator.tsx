import React from 'react';
import {
  Box,
  Typography,
  Chip,
  Tooltip,
  IconButton
} from '@mui/material';
import {
  Close as CloseIcon
} from '@mui/icons-material';
import { UserPrompt } from './UserPromptManager';

interface UserPromptIndicatorProps {
  activePrompt: UserPrompt | null;
  onDeactivate: () => void;
}

const UserPromptIndicator: React.FC<UserPromptIndicatorProps> = ({
  activePrompt,
  onDeactivate
}) => {
  if (!activePrompt) {
    return null;
  }

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        padding: '8px 16px',
        backgroundColor: 'rgba(156, 163, 175, 0.1)', // Light gray background
        borderRadius: '8px',
        marginBottom: '16px',
        border: '1px solid rgba(156, 163, 175, 0.3)'
      }}
    >
      <Box sx={{ flexGrow: 1 }}>
        <Typography variant="body2" sx={{ color: '#9ca3af', fontWeight: 'bold', fontSize: '0.75rem' }}>
          Active User Prompt:
        </Typography>
        
        <Tooltip title={activePrompt.content} placement="bottom-start">
          <Chip
            label={activePrompt.name}
            sx={{
              backgroundColor: 'rgba(156, 163, 175, 0.5)',
              color: '#1a1a1a',
              fontWeight: 'bold',
              marginTop: '4px',
              maxWidth: '250px',
              height: '24px',
              '& .MuiChip-label': {
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
                padding: '0 8px'
              }
            }}
          />
        </Tooltip>
      </Box>
      
      <Tooltip title="Deactivate Prompt">
        <IconButton 
          size="small" 
          onClick={onDeactivate}
          sx={{ 
            color: '#9ca3af',
            '&:hover': {
              backgroundColor: 'rgba(156, 163, 175, 0.2)'
            }
          }}
        >
          <CloseIcon fontSize="small" />
        </IconButton>
      </Tooltip>
    </Box>
  );
};

export default UserPromptIndicator;