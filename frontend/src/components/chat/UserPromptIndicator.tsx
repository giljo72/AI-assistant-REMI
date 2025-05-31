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
        backgroundColor: 'rgba(252, 192, 0, 0.1)', // Light gold background
        borderRadius: '8px',
        marginBottom: '16px',
        border: '1px solid rgba(252, 192, 0, 0.3)'
      }}
    >
      <Box sx={{ flexGrow: 1 }}>
        <Typography variant="body2" sx={{ color: '#FCC000', fontWeight: 'bold', fontSize: '0.75rem' }}>
          Active User Prompt:
        </Typography>
        
        <Tooltip title={activePrompt.content} placement="bottom-start">
          <Chip
            label={activePrompt.name}
            sx={{
              backgroundColor: 'rgba(252, 192, 0, 0.8)',
              color: '#000000',
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
            color: '#FCC000',
            '&:hover': {
              backgroundColor: 'rgba(252, 192, 0, 0.2)'
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