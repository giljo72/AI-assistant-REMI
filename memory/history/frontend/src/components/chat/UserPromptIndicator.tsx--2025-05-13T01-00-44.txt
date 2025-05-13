import React from 'react';
import {
  Box,
  Typography,
  Chip,
  Tooltip,
  IconButton
} from '@mui/material';
import {
  Description as DescriptionIcon,
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
        backgroundColor: 'rgba(212, 175, 55, 0.1)', // Light gold background
        borderRadius: '4px',
        marginBottom: '16px'
      }}
    >
      <DescriptionIcon sx={{ color: '#d4af37', marginRight: '8px' }} />
      
      <Box sx={{ flexGrow: 1 }}>
        <Typography variant="body2" sx={{ color: '#d4af37', fontWeight: 'bold' }}>
          Active User Prompt:
        </Typography>
        
        <Tooltip title={activePrompt.content} placement="bottom-start">
          <Chip
            label={activePrompt.name}
            sx={{
              backgroundColor: '#d4af37',
              color: '#000000',
              fontWeight: 'bold',
              marginTop: '4px',
              maxWidth: '250px',
              '& .MuiChip-label': {
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap'
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
            color: '#d4af37',
            '&:hover': {
              backgroundColor: 'rgba(212, 175, 55, 0.2)'
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