import React, { useState, useEffect } from 'react';
import systemService from '../../services/systemService';
import { Icon } from '../common/Icon';

interface ElegantSystemModelsPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

interface ModelInfo {
  name: string;
  type: 'ollama' | 'nvidia-nim' | 'transformers' | 'embedding-fallback';
  status: 'loaded' | 'unloaded' | 'loading' | 'error';
  size: string;
  parameters?: string;
  memory_usage?: number;
  description?: string;
  capabilities?: string[];
  useCase?: string;
}

// Model descriptions and use cases - Optimized set
const MODEL_DETAILS: Record<string, { description: string; useCase: string; capabilities: string[] }> = {
  'qwen2.5:32b-instruct-q4_K_M': {
    description: 'Qwen 2.5 32B - Primary workhorse with full RAG support',
    useCase: 'Best for: Daily driver, general AI tasks, document analysis, multi-turn chats',
    capabilities: ['reasoning', 'analysis', 'chat', 'documents', 'rag-support']
  },
  'mistral-nemo:latest': {
    description: 'Mistral Nemo 12B - Lightning-fast responses',
    useCase: 'Best for: Quick queries, chat, summarization, low VRAM usage (4GB)',
    capabilities: ['fast-response', 'chat', 'efficiency', 'speed']
  },
  'deepseek-coder-v2:16b-lite-instruct-q4_K_M': {
    description: 'DeepSeek Coder V2 16B - Specialized programming assistant',
    useCase: 'Best for: Code generation, debugging, technical documentation, code review',
    capabilities: ['coding', 'debugging', 'code-analysis', 'self-aware']
  },
  'nvidia/nv-embedqa-e5-v5': {
    description: 'NVIDIA Embeddings - Powers document search',
    useCase: 'Best for: Document retrieval, semantic search, RAG operations',
    capabilities: ['embeddings', 'rag', 'search']
  }
};

const ElegantSystemModelsPanel: React.FC<ElegantSystemModelsPanelProps> = ({ isOpen, onClose }) => {
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [operationStatus, setOperationStatus] = useState<{message: string, type: 'success' | 'error'} | null>(null);
  const [activeModel, setActiveModel] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      fetchModels();
      // No auto-refresh - user can manually refresh with the button
    }
  }, [isOpen]);

  const fetchModels = async () => {
    try {
      // Get available models (this already includes status info)
      const availableModels = await systemService.getAvailableModels();
      console.log('Available models from API:', availableModels);
      
      // The backend already returns models with their current status
      // No need for a separate system status call
      // Only consider non-embedding models as potentially active
      const loadedModel = availableModels.find((m: any) => 
        m.status === 'loaded' && 
        !m.name.includes('embedqa') &&  // Exclude embeddings model
        m.last_used !== 'Embeddings'
      );
      setActiveModel(loadedModel?.name || null);
      
      // Transform and enrich the data
      const transformedModels: ModelInfo[] = availableModels.map((model: any) => {
        const details = MODEL_DETAILS[model.name] || {};
        return {
          name: model.name,
          type: model.type === 'nim' ? 'nvidia-nim' : model.type,
          status: model.status || 'unloaded',
          size: model.size || 'Unknown',
          parameters: model.parameters,
          memory_usage: model.memory_usage,
          description: details.description || model.description,
          capabilities: details.capabilities || model.capabilities || [],
          useCase: details.useCase
        };
      });
      
      console.log('Transformed models:', transformedModels);
      
      // Sort models: loaded first, then by type
      transformedModels.sort((a, b) => {
        if (a.status === 'loaded' && b.status !== 'loaded') return -1;
        if (a.status !== 'loaded' && b.status === 'loaded') return 1;
        return 0;
      });
      
      setModels(transformedModels);
      setError(null);
    } catch (err) {
      console.error('Error fetching models:', err);
      setError('Failed to fetch models');
    }
  };

  const getStatusIcon = (status: string, isActive: boolean) => {
    if (isActive) return '●';
    switch (status) {
      case 'loaded': return '●';
      case 'loading': return '◐';
      case 'unloaded': return '○';
      case 'error': return '✕';
      default: return '○';
    }
  };

  const getStatusColor = (status: string, isActive: boolean) => {
    if (isActive) return 'text-green-400';
    switch (status) {
      case 'loaded': return 'text-green-400';
      case 'loading': return 'text-yellow-400';
      case 'unloaded': return 'text-gray-400';
      case 'error': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const handleModelAction = async (modelName: string, modelType: string, action: 'load' | 'unload' | 'switch' | 'restart') => {
    setActionLoading(`${modelName}-${action}`);
    setOperationStatus(null);
    
    try {
      switch (action) {
        case 'load':
          await systemService.loadModel({ model_name: modelName, model_type: modelType as any });
          break;
        case 'unload':
          await systemService.unloadModel(modelName);
          break;
        case 'switch':
          await systemService.switchModel(modelName, modelType);
          break;
        case 'restart':
          await systemService.unloadModel(modelName);
          await new Promise(resolve => setTimeout(resolve, 2000));
          await systemService.loadModel({ model_name: modelName, model_type: modelType as any });
          break;
      }
      
      setOperationStatus({
        message: `Successfully ${action === 'restart' ? 'restarted' : action + 'ed'} ${modelName}`,
        type: 'success'
      });
      
      // Refresh models after action
      setTimeout(fetchModels, 1000);
    } catch (err: any) {
      setOperationStatus({
        message: err.response?.data?.detail || `Failed to ${action} model`,
        type: 'error'
      });
    } finally {
      setActionLoading(null);
    }
  };

  const formatMemory = (mb?: number) => {
    if (!mb) return 'N/A';
    if (mb >= 1024) {
      return `${(mb / 1024).toFixed(1)} GB`;
    }
    return `${mb} MB`;
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-gray-900 w-full max-w-6xl h-5/6 rounded-2xl flex flex-col border-2 border-yellow-500">
        {/* Header */}
        <div className="bg-gray-800 p-4 rounded-t-lg border-b border-gold/30">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-bold text-gold">AI Models</h2>
            <div className="flex items-center space-x-4">
              <span className="text-xs text-gray-400">
                {models.length} models
              </span>
              <button 
                onClick={() => {
                  setLoading(true);
                  fetchModels().then(() => setLoading(false));
                }}
                disabled={loading}
                className="text-gray-400 hover:text-white disabled:opacity-50 transition-colors"
                title="Refresh"
              >
                <Icon name="refresh" size={20} />
              </button>
              <button 
                onClick={onClose}
                className="text-gray-400 hover:text-white transition-colors"
                title="Close"
              >
                <Icon name="close" size={20} />
              </button>
            </div>
          </div>
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
          {loading && models.length === 0 ? (
            <div className="text-center text-gray-400 mt-8">
              <div className="inline-flex flex-col items-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gold mb-4"></div>
                <p>Loading models...</p>
                <p className="text-xs mt-2 text-gray-500">Checking Ollama and NIM containers</p>
              </div>
            </div>
          ) : error ? (
            <div className="text-center text-red-400 mt-8">
              <p>{error}</p>
            </div>
          ) : (
            <div className="space-y-4">
              {models.map((model, index) => {
                const isActive = model.name === activeModel;
                return (
                  <div key={index} className="bg-gray-800 p-4 rounded-lg border border-gray-700 hover:border-gold/30 transition-colors">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <span className={`text-lg ${getStatusColor(model.status, isActive)}`}>
                            {getStatusIcon(model.status, isActive)}
                          </span>
                          <h4 className="font-medium text-white">
                            {model.name}
                            {isActive && <span className="ml-2 text-xs text-green-400">(Active)</span>}
                          </h4>
                          <span className={`text-xs px-2 py-1 rounded ${
                            model.type === 'ollama' ? 'bg-blue-600/20 text-blue-400 border border-blue-600/30' :
                            model.type === 'nvidia-nim' ? 'bg-green-600/20 text-green-400 border border-green-600/30' :
                            model.type === 'embedding-fallback' ? 'bg-orange-600/20 text-orange-400 border border-orange-600/30' :
                            'bg-purple-600/20 text-purple-400 border border-purple-600/30'
                          }`}>
                            {model.type === 'nvidia-nim' ? 'NVIDIA NIM' : 
                             model.type === 'embedding-fallback' ? 'EMBEDDING FALLBACK' :
                             model.type.toUpperCase()}
                          </span>
                        </div>
                        
                        {/* Model Description */}
                        {model.description && (
                          <p className="text-sm text-gray-300 mb-1">{model.description}</p>
                        )}
                        
                        {/* Use Case */}
                        {model.useCase && (
                          <p className="text-xs text-gold/70 mb-2 italic">{model.useCase}</p>
                        )}
                        
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs text-gray-400">
                          {model.size && (
                            <div>VRAM: <span className="text-white">{model.size}</span></div>
                          )}
                          {model.parameters && (
                            <div>Parameters: <span className="text-white">{model.parameters}</span></div>
                          )}
                          {model.capabilities && model.capabilities.length > 0 && (
                            <div className="col-span-2">
                              Capabilities: <span className="text-white">{model.capabilities.join(', ')}</span>
                            </div>
                          )}
                        </div>
                      </div>
                      
                      <div className="flex space-x-2 ml-4">
                        {model.type === 'embedding-fallback' ? (
                          // Embedding models have limited actions
                          <div className="text-xs text-gray-400 px-3 py-1">
                            {model.status === 'loaded' ? 'Active' : 'Standby'}
                          </div>
                        ) : model.status === 'unloaded' ? (
                          <button
                            onClick={() => handleModelAction(model.name, model.type, 'load')}
                            disabled={actionLoading === `${model.name}-load`}
                            className="px-3 py-1 bg-gold/20 hover:bg-gold/30 border border-gold/30 rounded text-sm text-gold disabled:opacity-50 transition-all"
                          >
                            {actionLoading === `${model.name}-load` ? 'Loading...' : 'Load'}
                          </button>
                        ) : (
                          <>
                            {!isActive && (
                              <button
                                onClick={() => handleModelAction(model.name, model.type, 'switch')}
                                disabled={actionLoading === `${model.name}-switch`}
                                className="px-3 py-1 bg-gold/20 hover:bg-gold/30 border border-gold/30 rounded text-sm text-gold disabled:opacity-50 transition-all"
                              >
                                {actionLoading === `${model.name}-switch` ? 'Switching...' : 'Switch To'}
                              </button>
                            )}
                            <button
                              onClick={() => handleModelAction(model.name, model.type, 'restart')}
                              disabled={actionLoading === `${model.name}-restart`}
                              className="px-3 py-1 bg-yellow-600/20 hover:bg-yellow-600/30 border border-yellow-600/30 rounded text-sm text-yellow-600 disabled:opacity-50 transition-all"
                            >
                              {actionLoading === `${model.name}-restart` ? 'Restarting...' : 'Restart'}
                            </button>
                            <button
                              onClick={() => handleModelAction(model.name, model.type, 'unload')}
                              disabled={actionLoading === `${model.name}-unload`}
                              className="px-3 py-1 bg-gray-600 hover:bg-gray-700 rounded text-sm text-white disabled:opacity-50 transition-colors"
                            >
                              {actionLoading === `${model.name}-unload` ? 'Unloading...' : 'Unload'}
                            </button>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ElegantSystemModelsPanel;