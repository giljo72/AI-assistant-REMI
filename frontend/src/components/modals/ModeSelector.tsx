import React from 'react';
import {
  Box,
  FormControl,
  Select,
  MenuItem,
  Typography,
  Chip,
  Tooltip,
  SelectChangeEvent
} from '@mui/material';
import { styled } from '@mui/material/styles';

const ModeChip = styled(Chip)(({ theme }) => ({
  marginLeft: theme.spacing(1),
  fontSize: '0.75rem',
  height: '20px'
}));

const ModeInfo = styled(Typography)(({ theme }) => ({
  fontSize: '0.75rem',
  color: theme.palette.text.secondary,
  marginTop: theme.spacing(0.5),
  fontStyle: 'italic'
}));

export interface OperationalMode {
  id: string;
  name: string;
  description: string;
  models: string[];
  memoryUsage: string;
  speed: 'fast' | 'medium' | 'slow';
}

const MODES: OperationalMode[] = [
  {
    id: 'business_deep',
    name: 'Business Deep Analysis',
    description: 'Llama 70B solo mode for maximum reasoning power',
    models: ['Llama 3.1 70B'],
    memoryUsage: '22GB',
    speed: 'slow'
  },
  {
    id: 'business_fast',
    name: 'Business Fast',
    description: 'Qwen 32B with full document/RAG support',
    models: ['Qwen 2.5 32B', 'NV-Embedqa'],
    memoryUsage: '21GB',
    speed: 'medium'
  },
  {
    id: 'development',
    name: 'Development Mode',
    description: 'DeepSeek Coder with documentation support',
    models: ['DeepSeek Coder', 'NV-Embedqa'],
    memoryUsage: '11GB',
    speed: 'medium'
  },
  {
    id: 'quick',
    name: 'Quick Response',
    description: 'Mistral Nemo for fast responses',
    models: ['Mistral Nemo', 'NV-Embedqa'],
    memoryUsage: '9GB',
    speed: 'fast'
  },
  {
    id: 'balanced',
    name: 'Balanced (Auto)',
    description: 'Smart model selection based on your query',
    models: ['Auto-selected'],
    memoryUsage: 'Variable',
    speed: 'medium'
  }
];

interface ModeSelectorProps {
  currentMode: string;
  onModeChange: (mode: string) => void;
  disabled?: boolean;
}

const getSpeedColor = (speed: string) => {
  switch (speed) {
    case 'fast':
      return 'success';
    case 'medium':
      return 'warning';
    case 'slow':
      return 'error';
    default:
      return 'default';
  }
};

export const ModeSelector: React.FC<ModeSelectorProps> = ({
  currentMode,
  onModeChange,
  disabled = false
}) => {
  const handleChange = (event: SelectChangeEvent) => {
    onModeChange(event.target.value);
  };

  const selectedMode = MODES.find(m => m.id === currentMode) || MODES[4]; // Default to balanced

  return (
    <Box>
      <Typography variant="caption" sx={{ color: '#999', mb: 1, display: 'block' }}>
        Operational Mode
      </Typography>
      
      <FormControl fullWidth size="small" disabled={disabled}>
        <Select
          value={currentMode}
          onChange={handleChange}
          sx={{
            backgroundColor: '#1a2b47',
            color: '#fff',
            fontSize: '0.875rem',
            '& .MuiOutlinedInput-notchedOutline': {
              borderColor: '#152238',
            },
            '&:hover .MuiOutlinedInput-notchedOutline': {
              borderColor: '#d4af37',
            },
            '& .MuiSelect-icon': {
              color: '#d4af37',
            }
          }}
          renderValue={(value) => {
            const mode = MODES.find(m => m.id === value);
            return (
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <span>{mode?.name}</span>
                <ModeChip 
                  label={mode?.memoryUsage} 
                  size="small" 
                  color="primary" 
                  variant="outlined"
                />
                <ModeChip 
                  label={mode?.speed} 
                  size="small" 
                  color={getSpeedColor(mode?.speed || 'medium') as any}
                />
              </Box>
            );
          }}
        >
          {MODES.map((mode) => (
            <MenuItem key={mode.id} value={mode.id}>
              <Box sx={{ width: '100%' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Typography>{mode.name}</Typography>
                  <Box>
                    <Chip 
                      label={mode.memoryUsage} 
                      size="small" 
                      sx={{ ml: 1, height: '20px' }}
                    />
                    <Chip 
                      label={mode.speed} 
                      size="small" 
                      color={getSpeedColor(mode.speed) as any}
                      sx={{ ml: 0.5, height: '20px' }}
                    />
                  </Box>
                </Box>
                <Typography variant="caption" sx={{ color: '#666', display: 'block' }}>
                  {mode.description}
                </Typography>
                <Typography variant="caption" sx={{ color: '#888', display: 'block' }}>
                  Models: {mode.models.join(', ')}
                </Typography>
              </Box>
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      
      {selectedMode && (
        <ModeInfo>
          {selectedMode.description}
        </ModeInfo>
      )}
    </Box>
  );
};