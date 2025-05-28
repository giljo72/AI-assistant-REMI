import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  LinearProgress,
  IconButton,
  Chip,
  Grid,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  CircularProgress,
  Tooltip,
  Paper
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import CircleIcon from '@mui/icons-material/Circle';
import { systemService } from '../../services/systemService';
import { modelService } from '../../services/modelService';

interface ModelStatus {
  name: string;
  backend: 'nim' | 'ollama';
  purpose: 'chat' | 'reasoning' | 'coding' | 'embeddings';
  status: 'loaded' | 'loading' | 'unloaded' | 'error';
  memory_gb: number;
  max_context: number;
  last_used: string | null;
  tokens_per_second: number;
  current_requests: number;
}

interface MemoryStatus {
  total_vram_gb: number;
  used_vram_gb: number;
  allocated_vram_gb: number;
  available_vram_gb: number;
  loaded_models: string[];
}

export const EnhancedSystemModelsPanel: React.FC = () => {
  const [models, setModels] = useState<ModelStatus[]>([]);
  const [memory, setMemory] = useState<MemoryStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState('balanced');
  const [switching, setSwitching] = useState(false);

  const fetchModelStatus = async () => {
    setLoading(true);
    try {
      const [modelStatus, memoryStatus] = await Promise.all([
        modelService.getModelsStatus(),
        modelService.getMemoryStatus()
      ]);
      setModels(modelStatus);
      setMemory(memoryStatus);
    } catch (error) {
      console.error('Failed to fetch model status:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchModelStatus();
    const interval = setInterval(fetchModelStatus, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const handleModeSwitch = async (newMode: string) => {
    setSwitching(true);
    try {
      await modelService.switchMode(newMode);
      setMode(newMode);
      await fetchModelStatus();
    } catch (error) {
      console.error('Failed to switch mode:', error);
    } finally {
      setSwitching(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'loaded':
        return <CheckCircleIcon sx={{ color: '#4caf50' }} />;
      case 'loading':
        return <CircularProgress size={20} />;
      case 'error':
        return <ErrorIcon sx={{ color: '#f44336' }} />;
      default:
        return <CircleIcon sx={{ color: '#ccc' }} />;
    }
  };

  const getBackendColor = (backend: string) => {
    return backend === 'nim' ? '#4caf50' : '#2196f3'; // Green for NIM, Blue for Ollama
  };

  const getPurposeLabel = (purpose: string) => {
    const labels = {
      chat: 'Quick Chat & Drafting',
      reasoning: 'Business Analysis & Strategy',
      coding: 'Code Analysis & Development',
      embeddings: 'Document Processing & RAG'
    };
    return labels[purpose] || purpose;
  };

  const formatLastUsed = (lastUsed: string | null) => {
    if (!lastUsed) return 'Never';
    const date = new Date(lastUsed);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Active';
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${Math.floor(diffHours / 24)}d ago`;
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h6">Model Management</Typography>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <FormControl size="small" sx={{ minWidth: 200 }}>
            <InputLabel>Mode</InputLabel>
            <Select
              value={mode}
              onChange={(e) => handleModeSwitch(e.target.value)}
              disabled={switching}
              label="Mode"
            >
              <MenuItem value="business_fast">Business Fast (Qwen 32B)</MenuItem>
              <MenuItem value="development">Development (DeepSeek)</MenuItem>
              <MenuItem value="quick">Quick Response (Mistral)</MenuItem>
              <MenuItem value="balanced">Balanced</MenuItem>
            </Select>
          </FormControl>
          <IconButton onClick={fetchModelStatus} disabled={loading}>
            <RefreshIcon />
          </IconButton>
        </Box>
      </Box>

      {memory && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="subtitle2" gutterBottom>VRAM Usage</Typography>
            <Box sx={{ mb: 1 }}>
              <LinearProgress 
                variant="determinate" 
                value={(memory.used_vram_gb / memory.total_vram_gb) * 100}
                sx={{ height: 10, borderRadius: 5 }}
              />
            </Box>
            <Typography variant="body2" color="text.secondary">
              {memory.used_vram_gb.toFixed(1)} GB / {memory.total_vram_gb} GB 
              ({memory.available_vram_gb.toFixed(1)} GB available)
            </Typography>
          </CardContent>
        </Card>
      )}

      <Grid container spacing={2}>
        {models.map((model) => (
          <Grid item xs={12} key={model.name}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Box sx={{ flex: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      {getStatusIcon(model.status)}
                      <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                        {model.name}
                      </Typography>
                      <Chip 
                        label={model.backend.toUpperCase()} 
                        size="small"
                        sx={{ 
                          backgroundColor: getBackendColor(model.backend),
                          color: 'white'
                        }}
                      />
                    </Box>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {getPurposeLabel(model.purpose)}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 2, mt: 1 }}>
                      <Typography variant="caption" color="text.secondary">
                        Memory: {model.memory_gb} GB
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Context: {(model.max_context / 1000).toFixed(0)}K
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Last Used: {formatLastUsed(model.last_used)}
                      </Typography>
                      {model.tokens_per_second > 0 && (
                        <Typography variant="caption" color="text.secondary">
                          Speed: {model.tokens_per_second} tok/s
                        </Typography>
                      )}
                      {model.current_requests > 0 && (
                        <Typography variant="caption" color="primary">
                          Active: {model.current_requests} requests
                        </Typography>
                      )}
                    </Box>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};