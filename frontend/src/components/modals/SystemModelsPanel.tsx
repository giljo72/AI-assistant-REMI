import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Typography,
  IconButton,
  Tabs,
  Tab,
  Button,
  LinearProgress,
  Chip,
  Tooltip,
  CircularProgress,
  Alert,
  Divider,
  Paper
} from '@mui/material';
import {
  Close as CloseIcon,
  Refresh as RefreshIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Memory as MemoryIcon,
  Speed as SpeedIcon,
  Timer as TimerIcon
} from '@mui/icons-material';
import systemService, { SystemStatus, ServiceStatus, ModelInfo, EnvironmentInfo } from '../../services/systemService';

interface SystemModelsPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

interface ModelStatusInfo {
  name: string;
  display_name: string;
  description: string;
  status: 'loaded' | 'loading' | 'unloaded' | 'error' | 'unloading';
  status_color: 'green' | 'blue' | 'yellow' | 'red' | 'gray';
  backend: string;
  purpose: string;
  memory_gb: number;
  last_used: string | null;
  is_active: boolean;
  tokens_per_second: number;
  current_requests: number;
  total_tokens: number;
  average_response_time: number;
  error_message?: string;
}

interface ModelsStatus {
  models: Record<string, ModelStatusInfo>;
  system: {
    total_vram_gb: number;
    used_vram_gb: number;
    available_vram_gb: number;
    reserved_vram_gb: number;
    mode: string;
    active_primary_model: string;
    total_requests_active: number;
  };
}

const getStatusDot = (status: string, statusColor: string) => {
  const colors: Record<string, string> = {
    green: '#4caf50',
    blue: '#2196f3',
    yellow: '#ff9800',
    red: '#f44336',
    gray: '#9e9e9e'
  };

  return (
    <Box
      sx={{
        width: 10,
        height: 10,
        borderRadius: '50%',
        backgroundColor: colors[statusColor] || colors.gray,
        display: 'inline-block',
        mr: 1
      }}
    />
  );
};

const formatLastUsed = (lastUsed: string | null): string => {
  if (!lastUsed) return 'Never';
  
  const date = new Date(lastUsed);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  
  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  
  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays}d ago`;
};

const SystemModelsPanel: React.FC<SystemModelsPanelProps> = ({ isOpen, onClose }) => {
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [modelsStatus, setModelsStatus] = useState<ModelsStatus | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'services' | 'models' | 'environment'>('models');
  const [operationStatus, setOperationStatus] = useState<{message: string, type: 'success' | 'error'} | null>(null);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  // WebSocket connection for real-time updates
  useEffect(() => {
    if (isOpen) {
      // Connect to WebSocket for real-time model status
      const wsHost = window.location.hostname;
      const wsUrl = import.meta.env.VITE_WS_URL || `ws://${wsHost}:8000`;
      const ws = new WebSocket(`${wsUrl}/api/system/ws/model-status`);
      
      ws.onopen = () => {
        console.log('WebSocket connected for model status');
      };
      
      ws.onmessage = (event) => {
        try {
          const status = JSON.parse(event.data);
          setModelsStatus(status);
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e);
        }
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
      
      ws.onclose = () => {
        console.log('WebSocket disconnected');
      };
      
      wsRef.current = ws;
      
      // Also fetch initial data
      fetchSystemStatus();
      fetchModelsStatus();
      
      return () => {
        if (wsRef.current) {
          wsRef.current.close();
        }
      };
    }
  }, [isOpen]);

  const fetchSystemStatus = async () => {
    setLoading(true);
    setError(null);
    try {
      const status = await systemService.getSystemStatus();
      setSystemStatus(status);
    } catch (err) {
      console.error('Error fetching system status:', err);
      setError(`Backend Connection Failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  const fetchModelsStatus = async () => {
    try {
      const response = await fetch('/api/system/models/status');
      if (response.ok) {
        const status = await response.json();
        setModelsStatus(status);
      }
    } catch (err) {
      console.error('Error fetching models status:', err);
    }
  };


  const handleModelAction = async (modelName: string, action: 'load' | 'unload') => {
    setActionLoading(`${modelName}-${action}`);
    try {
      const response = await fetch(`/api/system/models/${action}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model_name: modelName })
      });
      
      if (response.ok) {
        setOperationStatus({ message: `Model ${action}ed successfully`, type: 'success' });
      } else {
        throw new Error(`Failed to ${action} model`);
      }
    } catch (err) {
      setOperationStatus({ message: `Failed to ${action} model`, type: 'error' });
    } finally {
      setActionLoading(null);
    }
  };

  const handleServiceControl = async (serviceName: string, action: 'start' | 'stop' | 'restart') => {
    setActionLoading(`${serviceName}-${action}`);
    setOperationStatus(null);
    try {
      await systemService.controlService(serviceName, action);
      setOperationStatus({
        message: `${serviceName} ${action}ed successfully`,
        type: 'success'
      });
      setTimeout(fetchSystemStatus, 2000);
    } catch (err) {
      setOperationStatus({
        message: `Failed to ${action} ${serviceName}`,
        type: 'error'
      });
    } finally {
      setActionLoading(null);
    }
  };

  const renderModelsTab = () => {
    if (!modelsStatus) {
      return <CircularProgress />;
    }

    const { models, system } = modelsStatus;
    const memoryPercentage = (system.used_vram_gb / system.total_vram_gb) * 100;

    return (
      <Box>

        {/* Memory Usage Bar */}
        <Box sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <MemoryIcon sx={{ mr: 1, color: '#d4af37' }} />
            <Typography variant="subtitle2">
              VRAM Usage: {system.used_vram_gb.toFixed(1)}GB / {system.total_vram_gb}GB
            </Typography>
            <Typography variant="caption" sx={{ ml: 'auto', color: '#666' }}>
              {system.available_vram_gb.toFixed(1)}GB available
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={memoryPercentage}
            sx={{
              height: 10,
              borderRadius: 5,
              backgroundColor: '#152238',
              '& .MuiLinearProgress-bar': {
                backgroundColor: memoryPercentage > 90 ? '#f44336' : 
                                memoryPercentage > 75 ? '#ff9800' : '#4caf50',
                borderRadius: 5,
              }
            }}
          />
        </Box>

        {/* Active Requests */}
        {system.total_requests_active > 0 && (
          <Alert severity="info" sx={{ mb: 2 }}>
            {system.total_requests_active} active request{system.total_requests_active > 1 ? 's' : ''} in progress
          </Alert>
        )}

        {/* Models List */}
        <Box sx={{ maxHeight: '400px', overflowY: 'auto' }}>
          {Object.entries(models).map(([modelName, model]) => (
            <Paper
              key={modelName}
              sx={{
                p: 2,
                mb: 2,
                backgroundColor: '#152238',
                border: model.is_active ? '1px solid #d4af37' : '1px solid transparent',
                opacity: model.status === 'unloaded' ? 0.7 : 1
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
                <Box sx={{ flex: 1 }}>
                  {/* Model Name and Status */}
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    {getStatusDot(model.status, model.status_color)}
                    <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                      {model.display_name}
                    </Typography>
                    {model.backend === 'nim' && (
                      <Chip
                        label="NVIDIA NIM"
                        size="small"
                        sx={{
                          ml: 1,
                          backgroundColor: '#4caf50',
                          color: 'white',
                          fontSize: '0.7rem',
                          height: '20px'
                        }}
                      />
                    )}
                    {model.backend === 'ollama' && (
                      <Chip
                        label="Ollama"
                        size="small"
                        sx={{
                          ml: 1,
                          backgroundColor: '#2196f3',
                          color: 'white',
                          fontSize: '0.7rem',
                          height: '20px'
                        }}
                      />
                    )}
                  </Box>

                  {/* Description */}
                  <Typography variant="caption" sx={{ color: '#999', display: 'block', mb: 1 }}>
                    {model.description}
                  </Typography>

                  {/* Stats Row */}
                  <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                    <Chip
                      icon={<MemoryIcon />}
                      label={`${model.memory_gb}GB`}
                      size="small"
                      variant="outlined"
                      sx={{ fontSize: '0.75rem' }}
                    />
                    
                    {model.status === 'loaded' && model.tokens_per_second > 0 && (
                      <Chip
                        icon={<SpeedIcon />}
                        label={`${model.tokens_per_second.toFixed(1)} tok/s`}
                        size="small"
                        variant="outlined"
                        sx={{ fontSize: '0.75rem' }}
                      />
                    )}
                    
                    {model.average_response_time > 0 && (
                      <Chip
                        icon={<TimerIcon />}
                        label={`~${model.average_response_time.toFixed(1)}s avg`}
                        size="small"
                        variant="outlined"
                        sx={{ fontSize: '0.75rem' }}
                      />
                    )}
                    
                    <Typography variant="caption" sx={{ color: '#666', display: 'flex', alignItems: 'center' }}>
                      Last used: {model.is_active ? (
                        <Chip label="Active" size="small" color="success" sx={{ ml: 0.5, height: '18px' }} />
                      ) : (
                        formatLastUsed(model.last_used)
                      )}
                    </Typography>
                  </Box>

                  {/* Error Message */}
                  {model.error_message && (
                    <Alert severity="error" sx={{ mt: 1, py: 0, fontSize: '0.75rem' }}>
                      {model.error_message}
                    </Alert>
                  )}

                  {/* Current Requests */}
                  {model.current_requests > 0 && (
                    <Box sx={{ mt: 1 }}>
                      <CircularProgress size={16} sx={{ mr: 1 }} />
                      <Typography variant="caption" sx={{ color: '#ff9800' }}>
                        {model.current_requests} request{model.current_requests > 1 ? 's' : ''} in progress
                      </Typography>
                    </Box>
                  )}
                </Box>

                {/* Action Buttons */}
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, ml: 2 }}>
                  {model.status === 'unloaded' && (
                    <Button
                      variant="outlined"
                      size="small"
                      startIcon={<PlayIcon />}
                      onClick={() => handleModelAction(modelName, 'load')}
                      disabled={!!actionLoading}
                      sx={{
                        borderColor: '#d4af37',
                        color: '#d4af37',
                        '&:hover': {
                          borderColor: '#f4d03f',
                          backgroundColor: 'rgba(212, 175, 55, 0.1)'
                        }
                      }}
                    >
                      Load
                    </Button>
                  )}
                  
                  {model.status === 'loaded' && model.backend === 'ollama' && (
                    <Button
                      variant="outlined"
                      size="small"
                      startIcon={<StopIcon />}
                      onClick={() => handleModelAction(modelName, 'unload')}
                      disabled={!!actionLoading || model.current_requests > 0}
                      sx={{
                        borderColor: '#f44336',
                        color: '#f44336',
                        '&:hover': {
                          borderColor: '#d32f2f',
                          backgroundColor: 'rgba(244, 67, 54, 0.1)'
                        }
                      }}
                    >
                      Unload
                    </Button>
                  )}
                  
                  {model.status === 'loading' && (
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <CircularProgress size={20} sx={{ mr: 1 }} />
                      <Typography variant="caption">Loading...</Typography>
                    </Box>
                  )}
                  
                  {model.status === 'unloading' && (
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <CircularProgress size={20} sx={{ mr: 1 }} />
                      <Typography variant="caption">Unloading...</Typography>
                    </Box>
                  )}
                </Box>
              </Box>
            </Paper>
          ))}
        </Box>
      </Box>
    );
  };

  const renderServicesTab = () => {
    if (!systemStatus) {
      return <CircularProgress />;
    }

    return (
      <Box sx={{ maxHeight: '500px', overflowY: 'auto' }}>
        {systemStatus.services.map((service) => (
          <Box
            key={service.name}
            sx={{
              p: 2,
              mb: 2,
              borderRadius: 1,
              backgroundColor: '#152238',
              border: '1px solid #1a2b47'
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Box>
                <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                  {service.name}
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Chip
                    label={service.status}
                    size="small"
                    color={service.status === 'running' ? 'success' : 'error'}
                    sx={{ textTransform: 'capitalize' }}
                  />
                  {service.port && (
                    <Typography variant="caption" sx={{ color: '#999' }}>
                      Port: {service.port}
                    </Typography>
                  )}
                  {service.pid && (
                    <Typography variant="caption" sx={{ color: '#999' }}>
                      PID: {service.pid}
                    </Typography>
                  )}
                </Box>
                {service.uptime && (
                  <Typography variant="caption" sx={{ color: '#666', display: 'block', mt: 0.5 }}>
                    Uptime: {service.uptime}
                  </Typography>
                )}
              </Box>

              <Box sx={{ display: 'flex', gap: 1 }}>
                {service.status === 'stopped' && (
                  <IconButton
                    size="small"
                    onClick={() => handleServiceControl(service.name, 'start')}
                    disabled={!!actionLoading}
                    sx={{ color: '#4caf50' }}
                  >
                    <PlayIcon />
                  </IconButton>
                )}
                {service.status === 'running' && (
                  <>
                    <IconButton
                      size="small"
                      onClick={() => handleServiceControl(service.name, 'restart')}
                      disabled={!!actionLoading}
                      sx={{ color: '#ff9800' }}
                    >
                      <RefreshIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleServiceControl(service.name, 'stop')}
                      disabled={!!actionLoading}
                      sx={{ color: '#f44336' }}
                    >
                      <StopIcon />
                    </IconButton>
                  </>
                )}
              </Box>
            </Box>
          </Box>
        ))}
      </Box>
    );
  };

  const renderEnvironmentTab = () => {
    if (!systemStatus) {
      return <CircularProgress />;
    }

    const env = systemStatus.environment;

    return (
      <Box sx={{ maxHeight: '500px', overflowY: 'auto' }}>
        <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 2 }}>
          {/* System Info */}
          <Box sx={{ p: 2, backgroundColor: '#152238', borderRadius: 1 }}>
            <Typography variant="subtitle2" sx={{ mb: 1, color: '#d4af37' }}>
              System Information
            </Typography>
            <Typography variant="body2">OS: {env.os_info}</Typography>
            <Typography variant="body2">Python: {env.python_version}</Typography>
            <Typography variant="body2">Node: {env.node_version || 'Not detected'}</Typography>
          </Box>

          {/* GPU Info */}
          <Box sx={{ p: 2, backgroundColor: '#152238', borderRadius: 1 }}>
            <Typography variant="subtitle2" sx={{ mb: 1, color: '#d4af37' }}>
              GPU Information
            </Typography>
            <Typography variant="body2">{env.gpu_info || 'No GPU detected'}</Typography>
            <Typography variant="body2">CUDA: {env.cuda_version || 'Not available'}</Typography>
          </Box>

          {/* Memory Info */}
          <Box sx={{ p: 2, backgroundColor: '#152238', borderRadius: 1 }}>
            <Typography variant="subtitle2" sx={{ mb: 1, color: '#d4af37' }}>
              Memory
            </Typography>
            <Typography variant="body2">
              Total: {env.total_memory ? `${(env.total_memory / 1024 / 1024 / 1024).toFixed(1)} GB` : 'Unknown'}
            </Typography>
            <Typography variant="body2">
              Available: {env.available_memory ? `${(env.available_memory / 1024 / 1024 / 1024).toFixed(1)} GB` : 'Unknown'}
            </Typography>
          </Box>

          {/* Framework Versions */}
          <Box sx={{ p: 2, backgroundColor: '#152238', borderRadius: 1 }}>
            <Typography variant="subtitle2" sx={{ mb: 1, color: '#d4af37' }}>
              Frameworks
            </Typography>
            <Typography variant="body2">PyTorch: {env.pytorch_version || 'Not installed'}</Typography>
            <Typography variant="body2">TensorFlow: {env.tensorflow_version || 'Not installed'}</Typography>
            <Typography variant="body2">pgvector: {env.pgvector_version || 'Not installed'}</Typography>
          </Box>
        </Box>
      </Box>
    );
  };

  if (!isOpen) return null;

  return (
    <Box
      sx={{
        position: 'fixed',
        top: 0,
        right: 0,
        width: '800px',
        height: '100vh',
        backgroundColor: '#0a1929',
        boxShadow: '-4px 0 20px rgba(0, 0, 0, 0.5)',
        zIndex: 1300,
        display: 'flex',
        flexDirection: 'column',
        color: '#ffffff'
      }}
    >
      {/* Header */}
      <Box sx={{
        p: 3,
        borderBottom: '1px solid #152238',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
          System & Models
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <IconButton onClick={fetchSystemStatus} disabled={loading} sx={{ color: '#d4af37' }}>
            <RefreshIcon />
          </IconButton>
          <IconButton onClick={onClose} sx={{ color: '#ffffff' }}>
            <CloseIcon />
          </IconButton>
        </Box>
      </Box>

      {/* Tabs */}
      <Box sx={{ borderBottom: '1px solid #152238', px: 3 }}>
        <Tabs
          value={activeTab}
          onChange={(_, newValue) => setActiveTab(newValue)}
          sx={{
            '& .MuiTab-root': {
              color: '#999',
              '&.Mui-selected': {
                color: '#d4af37'
              }
            },
            '& .MuiTabs-indicator': {
              backgroundColor: '#d4af37'
            }
          }}
        >
          <Tab label="AI Models" value="models" />
          <Tab label="Services" value="services" />
          <Tab label="Environment" value="environment" />
        </Tabs>
      </Box>

      {/* Content */}
      <Box sx={{ flex: 1, p: 3, overflowY: 'auto' }}>
        {loading && !systemStatus && !modelsStatus ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
            <CircularProgress sx={{ color: '#d4af37' }} />
          </Box>
        ) : error ? (
          <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>
        ) : (
          <>
            {operationStatus && (
              <Alert 
                severity={operationStatus.type} 
                sx={{ mb: 2 }}
                onClose={() => setOperationStatus(null)}
              >
                {operationStatus.message}
              </Alert>
            )}
            
            {activeTab === 'models' && renderModelsTab()}
            {activeTab === 'services' && renderServicesTab()}
            {activeTab === 'environment' && renderEnvironmentTab()}
          </>
        )}
      </Box>
    </Box>
  );
};

export default SystemModelsPanel;