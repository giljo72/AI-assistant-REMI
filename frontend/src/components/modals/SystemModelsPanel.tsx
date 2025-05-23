import React, { useState, useEffect } from 'react';
import systemService, { SystemStatus, ServiceStatus, ModelInfo, EnvironmentInfo } from '../../services/systemService';

interface SystemModelsPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

const SystemModelsPanel: React.FC<SystemModelsPanelProps> = ({ isOpen, onClose }) => {
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'services' | 'models' | 'environment'>('services');
  const [operationStatus, setOperationStatus] = useState<{message: string, type: 'success' | 'error'} | null>(null);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  // Auto-refresh interval
  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (isOpen) {
      fetchSystemStatus();
      // Refresh every 30 seconds
      interval = setInterval(fetchSystemStatus, 30000);
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isOpen]);

  const fetchSystemStatus = async () => {
    setLoading(true);
    setError(null);
    try {
      console.log('🔍 SystemModelsPanel: Fetching status...');
      const status = await systemService.getSystemStatus();
      console.log('✅ SystemModelsPanel: Status received:', status);
      setSystemStatus(status);
    } catch (err) {
      console.error('❌ SystemModelsPanel: Error fetching system status:', err);
      setError(`Backend Connection Failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  const handleServiceControl = async (serviceName: string, action: 'start' | 'stop' | 'restart') => {
    setActionLoading(`${serviceName}-${action}`);
    setOperationStatus(null);
    
    try {
      const response = await systemService.controlService({
        service_name: serviceName,
        action
      });
      
      setOperationStatus({
        message: response.message,
        type: response.success ? 'success' : 'error'
      });
      
      // Refresh status after action
      setTimeout(fetchSystemStatus, 2000);
    } catch (err: any) {
      setOperationStatus({
        message: err.message || 'Operation failed',
        type: 'error'
      });
    } finally {
      setActionLoading(null);
    }
  };

  const handleModelAction = async (modelName: string, action: 'load' | 'unload' | 'switch') => {
    setActionLoading(`${modelName}-${action}`);
    setOperationStatus(null);
    
    try {
      let response;
      const modelType = systemStatus?.models.find(m => m.name === modelName)?.type || 'ollama';
      
      switch (action) {
        case 'load':
          response = await systemService.loadModel({
            model_name: modelName,
            model_type: modelType as 'ollama' | 'nvidia-nim' | 'nemo' | 'transformers'
          });
          break;
        case 'unload':
          response = await systemService.unloadModel(modelName, modelType);
          break;
        case 'switch':
          response = await systemService.switchModel(modelName, modelType);
          break;
      }
      
      setOperationStatus({
        message: response.message,
        type: response.success ? 'success' : 'error'
      });
      
      // Refresh status after action
      setTimeout(fetchSystemStatus, 3000);
    } catch (err: any) {
      console.error('Model action error:', err);
      setOperationStatus({
        message: err.message || 'Operation failed',
        type: 'error'
      });
    } finally {
      setActionLoading(null);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
      case 'loaded':
        return 'text-green-400';
      case 'stopped':
      case 'unloaded':
        return 'text-gray-400';
      case 'loading':
        return 'text-yellow-400';
      case 'error':
        return 'text-red-400';
      default:
        return 'text-gray-500';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
      case 'loaded':
        return '●';
      case 'stopped':
      case 'unloaded':
        return '○';
      case 'loading':
        return '◐';
      case 'error':
        return '✕';
      default:
        return '?';
    }
  };

  const formatMemory = (mb: number) => {
    if (mb >= 1024) {
      return `${(mb / 1024).toFixed(1)} GB`;
    }
    return `${mb} MB`;
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-navy w-full max-w-6xl h-5/6 rounded-lg flex flex-col">
        {/* Header */}
        <div className="bg-navy-light p-4 rounded-t-lg border-b border-gold">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-bold text-gold">System & Models</h2>
            <div className="flex items-center space-x-4">
              <button 
                onClick={fetchSystemStatus}
                disabled={loading}
                className="text-gray-400 hover:text-white disabled:opacity-50"
                title="Refresh"
              >
                🔄
              </button>
              <button 
                onClick={onClose}
                className="text-gray-400 hover:text-white"
              >
                ✕
              </button>
            </div>
          </div>
          
          {systemStatus && (
            <div className="mt-2 text-sm text-gray-400">
              Last updated: {new Date(systemStatus.last_updated).toLocaleTimeString()}
            </div>
          )}
        </div>

        {/* Navigation Tabs */}
        <div className="flex border-b border-navy-lighter">
          <button
            onClick={() => setActiveTab('services')}
            className={`px-6 py-3 text-sm font-medium ${
              activeTab === 'services' 
                ? 'text-gold border-b-2 border-gold bg-navy-light' 
                : 'text-gray-400 hover:text-white'
            }`}
          >
            System Services
          </button>
          <button
            onClick={() => setActiveTab('models')}
            className={`px-6 py-3 text-sm font-medium ${
              activeTab === 'models' 
                ? 'text-gold border-b-2 border-gold bg-navy-light' 
                : 'text-gray-400 hover:text-white'
            }`}
          >
            AI Models
          </button>
          <button
            onClick={() => setActiveTab('environment')}
            className={`px-6 py-3 text-sm font-medium ${
              activeTab === 'environment' 
                ? 'text-gold border-b-2 border-gold bg-navy-light' 
                : 'text-gray-400 hover:text-white'
            }`}
          >
            Environment
          </button>
        </div>

        {/* Status Messages */}
        {operationStatus && (
          <div className={`p-3 mx-4 mt-4 rounded ${
            operationStatus.type === 'success' 
              ? 'bg-green-900/20 border border-green-700 text-green-400'
              : 'bg-red-900/20 border border-red-700 text-red-400'
          }`}>
            {operationStatus.message}
          </div>
        )}

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4">
          {loading && !systemStatus ? (
            <div className="text-center text-gray-400 mt-8">
              <p>Loading system status...</p>
            </div>
          ) : error ? (
            <div className="text-center text-red-400 mt-8">
              <p>{error}</p>
            </div>
          ) : systemStatus ? (
            <>
              {/* Services Tab */}
              {activeTab === 'services' && (
                <div className="space-y-4">
                  <h3 className="text-lg font-bold text-gold mb-4">System Services</h3>
                  <div className="grid gap-4">
                    {systemStatus.services.map((service, index) => (
                      <div key={index} className="bg-navy-light p-4 rounded-lg">
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <div className="flex items-center space-x-3 mb-2">
                              <span className={`text-lg ${getStatusColor(service.status)}`}>
                                {getStatusIcon(service.status)}
                              </span>
                              <h4 className="font-medium text-white">{service.name}</h4>
                              {service.version && (
                                <span className="text-xs px-2 py-1 bg-navy rounded text-gray-300">
                                  v{service.version}
                                </span>
                              )}
                            </div>
                            
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs text-gray-400">
                              {service.port && (
                                <div>Port: <span className="text-white">{service.port}</span></div>
                              )}
                              {service.uptime && (
                                <div>Uptime: <span className="text-white">{service.uptime}</span></div>
                              )}
                              {service.memory_usage && (
                                <div>Memory: <span className="text-white">{formatMemory(service.memory_usage)}</span></div>
                              )}
                              {service.cpu_usage && (
                                <div>CPU: <span className="text-white">{service.cpu_usage}%</span></div>
                              )}
                            </div>
                          </div>
                          
                          <div className="flex space-x-2">
                            {service.status === 'stopped' ? (
                              <button
                                onClick={() => handleServiceControl(service.name, 'start')}
                                disabled={actionLoading === `${service.name}-start`}
                                className="px-3 py-1 bg-green-600 hover:bg-green-700 rounded text-sm text-white disabled:opacity-50"
                              >
                                {actionLoading === `${service.name}-start` ? 'Starting...' : 'Start'}
                              </button>
                            ) : (
                              <>
                                <button
                                  onClick={() => handleServiceControl(service.name, 'restart')}
                                  disabled={actionLoading === `${service.name}-restart`}
                                  className="px-3 py-1 bg-yellow-600 hover:bg-yellow-700 rounded text-sm text-white disabled:opacity-50"
                                >
                                  {actionLoading === `${service.name}-restart` ? 'Restarting...' : 'Restart'}
                                </button>
                                <button
                                  onClick={() => handleServiceControl(service.name, 'stop')}
                                  disabled={actionLoading === `${service.name}-stop`}
                                  className="px-3 py-1 bg-red-600 hover:bg-red-700 rounded text-sm text-white disabled:opacity-50"
                                >
                                  {actionLoading === `${service.name}-stop` ? 'Stopping...' : 'Stop'}
                                </button>
                              </>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Models Tab */}
              {activeTab === 'models' && (
                <div className="space-y-4">
                  <h3 className="text-lg font-bold text-gold mb-4">AI Models</h3>
                  <div className="grid gap-4">
                    {systemStatus.models.map((model, index) => (
                      <div key={index} className="bg-navy-light p-4 rounded-lg">
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <div className="flex items-center space-x-3 mb-2">
                              <span className={`text-lg ${getStatusColor(model.status)}`}>
                                {getStatusIcon(model.status)}
                              </span>
                              <h4 className="font-medium text-white">{model.name}</h4>
                              <span className={`text-xs px-2 py-1 rounded ${
                                model.type === 'ollama' ? 'bg-blue-600/20 text-blue-400' :
                                model.type === 'nemo' ? 'bg-green-600/20 text-green-400' :
                                'bg-purple-600/20 text-purple-400'
                              }`}>
                                {model.type}
                              </span>
                            </div>
                            
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs text-gray-400">
                              {model.size && (
                                <div>Size: <span className="text-white">{model.size}</span></div>
                              )}
                              {model.parameters && (
                                <div>Parameters: <span className="text-white">{model.parameters}</span></div>
                              )}
                              {model.memory_usage && (
                                <div>Memory: <span className="text-white">{formatMemory(model.memory_usage)}</span></div>
                              )}
                              {model.last_used && (
                                <div>Last used: <span className="text-white">{model.last_used}</span></div>
                              )}
                            </div>
                          </div>
                          
                          <div className="flex space-x-2">
                            {model.status === 'unloaded' ? (
                              <button
                                onClick={() => handleModelAction(model.name, 'load')}
                                disabled={actionLoading === `${model.name}-load`}
                                className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm text-white disabled:opacity-50"
                              >
                                {actionLoading === `${model.name}-load` ? 'Loading...' : 'Load'}
                              </button>
                            ) : (
                              <>
                                <button
                                  onClick={() => handleModelAction(model.name, 'switch')}
                                  disabled={actionLoading === `${model.name}-switch`}
                                  className="px-3 py-1 bg-gold/20 hover:bg-gold/30 rounded text-sm text-gold disabled:opacity-50"
                                >
                                  {actionLoading === `${model.name}-switch` ? 'Switching...' : 'Switch To'}
                                </button>
                                <button
                                  onClick={() => handleModelAction(model.name, 'unload')}
                                  disabled={actionLoading === `${model.name}-unload`}
                                  className="px-3 py-1 bg-gray-600 hover:bg-gray-700 rounded text-sm text-white disabled:opacity-50"
                                >
                                  {actionLoading === `${model.name}-unload` ? 'Unloading...' : 'Unload'}
                                </button>
                              </>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Environment Tab */}
              {activeTab === 'environment' && (
                <div className="space-y-6">
                  <h3 className="text-lg font-bold text-gold mb-4">Environment Information</h3>
                  
                  {/* Software Versions */}
                  <div className="bg-navy-light p-4 rounded-lg">
                    <h4 className="font-medium text-gold mb-3">Software Versions</h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="text-gray-400">Python:</span>
                        <span className="text-white ml-2">{systemStatus.environment.python_version}</span>
                      </div>
                      <div>
                        <span className="text-gray-400">Node.js:</span>
                        <span className="text-white ml-2">{systemStatus.environment.node_version}</span>
                      </div>
                      {systemStatus.environment.cuda_version && (
                        <div>
                          <span className="text-gray-400">CUDA:</span>
                          <span className="text-white ml-2">{systemStatus.environment.cuda_version}</span>
                        </div>
                      )}
                      {systemStatus.environment.pytorch_version && (
                        <div>
                          <span className="text-gray-400">PyTorch:</span>
                          <span className="text-white ml-2">{systemStatus.environment.pytorch_version}</span>
                        </div>
                      )}
                      {systemStatus.environment.pgvector_version && (
                        <div>
                          <span className="text-gray-400">pgvector:</span>
                          <span className="text-white ml-2">{systemStatus.environment.pgvector_version}</span>
                        </div>
                      )}
                      <div>
                        <span className="text-gray-400">OS:</span>
                        <span className="text-white ml-2">{systemStatus.environment.os_info}</span>
                      </div>
                    </div>
                  </div>

                  {/* System Resources */}
                  <div className="bg-navy-light p-4 rounded-lg">
                    <h4 className="font-medium text-gold mb-3">System Resources</h4>
                    <div className="space-y-3">
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-gray-400">System Memory</span>
                          <span className="text-white">
                            {formatMemory(systemStatus.environment.available_memory)} / {formatMemory(systemStatus.environment.total_memory)}
                          </span>
                        </div>
                        <div className="w-full bg-gray-700 rounded-full h-2">
                          <div 
                            className="bg-blue-500 h-2 rounded-full" 
                            style={{ 
                              width: `${((systemStatus.environment.total_memory - systemStatus.environment.available_memory) / systemStatus.environment.total_memory) * 100}%` 
                            }}
                          ></div>
                        </div>
                      </div>

                      {systemStatus.environment.gpu_info && (
                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <span className="text-gray-400">{systemStatus.environment.gpu_info.name}</span>
                            <span className="text-white">
                              {formatMemory(systemStatus.environment.gpu_info.memory_used)} / {formatMemory(systemStatus.environment.gpu_info.memory_total)}
                            </span>
                          </div>
                          <div className="w-full bg-gray-700 rounded-full h-2">
                            <div 
                              className="bg-green-500 h-2 rounded-full" 
                              style={{ 
                                width: `${(systemStatus.environment.gpu_info.memory_used / systemStatus.environment.gpu_info.memory_total) * 100}%` 
                              }}
                            ></div>
                          </div>
                          <div className="flex justify-between text-xs text-gray-400 mt-1">
                            <span>GPU Utilization: {systemStatus.environment.gpu_info.gpu_utilization}%</span>
                            {systemStatus.environment.gpu_info.temperature && (
                              <span>Temperature: {systemStatus.environment.gpu_info.temperature}°C</span>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </>
          ) : null}
        </div>
      </div>
    </div>
  );
};

export default SystemModelsPanel;