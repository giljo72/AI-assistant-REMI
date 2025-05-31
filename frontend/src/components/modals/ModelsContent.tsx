import React, { useState, useEffect } from 'react';
import { modelService } from '../../services/modelService';
import { Icon } from '../common/Icon';

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
const MODEL_DETAILS: Record<string, { description: string; useCase: string; capabilities: string[]; fullName: string; modelType: 'llm' | 'document-handler' }> = {
  'qwen2.5:32b-instruct-q4_K_M': {
    fullName: 'Qwen 2.5 32B Instruct Q4_K_M',
    description: 'Primary workhorse with full RAG support',
    useCase: 'Best for: Daily driver, general AI tasks, document analysis, multi-turn chats',
    capabilities: ['reasoning', 'analysis', 'chat', 'documents', 'rag-support'],
    modelType: 'llm'
  },
  'mistral-nemo:latest': {
    fullName: 'Mistral Nemo 12B Latest',
    description: 'Lightning-fast responses',
    useCase: 'Best for: Quick queries, chat, summarization, low VRAM usage',
    capabilities: ['fast-response', 'chat', 'efficiency', 'speed'],
    modelType: 'llm'
  },
  'deepseek-coder-v2:16b-lite-instruct-q4_K_M': {
    fullName: 'DeepSeek Coder V2 16B Lite Instruct Q4_K_M',
    description: 'Specialized programming assistant',
    useCase: 'Best for: Code generation, debugging, technical documentation, code review',
    capabilities: ['coding', 'debugging', 'code-analysis', 'self-aware'],
    modelType: 'llm'
  },
  'nvidia/nv-embedqa-e5-v5': {
    fullName: 'NVIDIA NV-EmbedQA E5 V5',
    description: 'Required for document embedding',
    useCase: 'Powers document search and retrieval',
    capabilities: ['embeddings', 'rag', 'search'],
    modelType: 'document-handler'
  },
  'nv-embedqa-e5-v5': {
    fullName: 'NVIDIA NV-EmbedQA E5 V5',
    description: 'Required for document embedding',
    useCase: 'Powers document search and retrieval',
    capabilities: ['embeddings', 'rag', 'search'],
    modelType: 'document-handler'
  }
};

export const ModelsContent: React.FC = () => {
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  useEffect(() => {
    fetchModels();
  }, []);

  const fetchModels = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await modelService.getModelsStatus();
      // Extract models from the response
      const allModels: ModelInfo[] = [];
      
      // Convert models object to array
      if (data.models) {
        Object.entries(data.models).forEach(([modelName, modelData]: [string, any]) => {
          const details = MODEL_DETAILS[modelName] || {};
          allModels.push({
            name: modelName,
            type: modelData.backend === 'nim' ? 'nvidia-nim' : 'ollama' as const,
            status: modelData.status,
            size: `${modelData.memory_gb}GB`,
            parameters: modelData.description?.match(/\d+B/)?.[0] || 'Unknown',
            memory_usage: modelData.memory_gb * 1024 * 1024 * 1024, // Convert GB to bytes
            description: details.description || modelData.description,
            useCase: details.useCase,
            capabilities: details.capabilities
          });
        });
      }
      
      setModels(allModels);
    } catch (error) {
      console.error('Failed to fetch models:', error);
      setError('Failed to load models. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleLoadModel = async (modelName: string) => {
    setActionLoading(modelName);
    try {
      await modelService.loadModel(modelName);
      await fetchModels();
    } catch (error) {
      console.error('Failed to load model:', error);
      setError(`Failed to load ${modelName}`);
    } finally {
      setActionLoading(null);
    }
  };

  const handleUnloadModel = async (modelName: string) => {
    setActionLoading(modelName);
    try {
      await modelService.unloadModel(modelName);
      await fetchModels();
    } catch (error) {
      console.error('Failed to unload model:', error);
      setError(`Failed to unload ${modelName}`);
    } finally {
      setActionLoading(null);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'loaded': return '#4CAF50';
      case 'loading': return '#FFC107';
      case 'error': return '#f44336';
      default: return '#666666';
    }
  };

  const getCapabilityLabel = (capability: string) => {
    switch (capability) {
      case 'reasoning': return 'Reasoning';
      case 'analysis': return 'Analysis';
      case 'chat': return 'Chat';
      case 'documents': return 'Documents';
      case 'rag-support': return 'RAG Support';
      case 'fast-response': return 'Fast Response';
      case 'efficiency': return 'Efficient';
      case 'speed': return 'High Speed';
      case 'coding': return 'Coding';
      case 'debugging': return 'Debugging';
      case 'code-analysis': return 'Code Analysis';
      case 'self-aware': return 'Self-Aware';
      case 'embeddings': return 'Embeddings';
      case 'rag': return 'RAG';
      case 'search': return 'Search';
      default: return capability;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-gold">Loading models...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4">
        <div className="bg-red-900 bg-opacity-20 p-4 rounded-md border border-red-600">
          <p className="text-red-400">{error}</p>
          <button 
            onClick={fetchModels}
            className="mt-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // Extract parameters from model name
  const extractParams = (modelName: string) => {
    const match = modelName.match(/(\d+)b/i);
    return match ? `${match[1]}B` : 'Unknown';
  };

  // Group models by type
  const llmModels = models.filter(m => MODEL_DETAILS[m.name]?.modelType === 'llm');
  const documentHandlers = models.filter(m => MODEL_DETAILS[m.name]?.modelType === 'document-handler');

  return (
    <div className="space-y-6">
      {/* LLM Models Section */}
      {llmModels.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gold mb-3">Large Language Models (LLMs)</h3>
          <div className="space-y-3">
            {llmModels.map((model) => {
              const details = MODEL_DETAILS[model.name];
              return (
                <div 
                  key={model.name}
                  className="bg-navy p-4 rounded-lg border border-navy-lighter hover:border-gold transition-colors"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold text-white">
                          {details?.fullName || model.name}
                        </h3>
                        <span 
                          className={`px-3 py-1 rounded-full text-xs font-medium ${
                            model.status === 'loaded'
                              ? model.type === 'nvidia-nim'
                                ? 'bg-green-900/30 text-green-400 border border-green-500/30'
                                : 'bg-blue-900/30 text-blue-400 border border-blue-500/30'
                              : 'bg-gray-800 text-gray-400 border border-gray-600'
                          }`}
                        >
                          {model.status.toUpperCase()}
                        </span>
                        <span className={`text-xs px-2 py-1 rounded-full ${
                          model.type === 'ollama' 
                            ? 'bg-blue-900/20 text-blue-400 border border-blue-500/20'
                            : 'bg-green-900/20 text-green-400 border border-green-500/20'
                        }`}>
                          {model.type === 'ollama' ? 'OLLAMA' : 'NVIDIA NIM'}
                        </span>
                      </div>
                      
                      {model.description && (
                        <p className="text-sm text-gray-300 mb-2">{model.description}</p>
                      )}
                      
                      {model.useCase && (
                        <p className="text-xs text-gold mb-2">{model.useCase}</p>
                      )}
                      
                      {model.capabilities && (
                        <div className="flex flex-wrap gap-2 mb-2">
                          {model.capabilities.map((cap) => (
                            <span 
                              key={cap}
                              className="text-xs px-2 py-1 bg-navy-lighter rounded-full text-gray-300"
                            >
                              {getCapabilityLabel(cap)}
                            </span>
                          ))}
                        </div>
                      )}
                      
                      <div className="flex items-center gap-4 text-xs">
                        <span><span className="text-yellow-400">Size:</span> <span className="text-white">{model.size}</span></span>
                        <span><span className="text-yellow-400">Params:</span> <span className="text-white">{extractParams(model.name)}</span></span>
                        {model.memory_usage && (
                          <span><span className="text-yellow-400">VRAM:</span> <span className="text-white">{(model.memory_usage / 1024 / 1024 / 1024).toFixed(1)}GB</span></span>
                        )}
                      </div>
                    </div>
                    
                    <div className="ml-4">
                      {model.status === 'loaded' ? (
                        <button
                          onClick={() => handleUnloadModel(model.name)}
                          disabled={actionLoading === model.name}
                          className="px-4 py-1.5 bg-red-900/30 text-red-400 border border-red-500/30 hover:bg-red-900/50 hover:border-red-500/50 disabled:bg-gray-800 disabled:text-gray-500 disabled:border-gray-700 rounded-full text-sm transition-all duration-200"
                        >
                          {actionLoading === model.name ? 'Processing...' : 'Unload'}
                        </button>
                      ) : (
                        <button
                          onClick={() => handleLoadModel(model.name)}
                          disabled={actionLoading === model.name}
                          className="px-4 py-1.5 bg-green-900/30 text-green-400 border border-green-500/30 hover:bg-green-900/50 hover:border-green-500/50 disabled:bg-gray-800 disabled:text-gray-500 disabled:border-gray-700 rounded-full text-sm transition-all duration-200"
                        >
                          {actionLoading === model.name ? 'Processing...' : 'Load'}
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Document Handler Section */}
      {documentHandlers.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gold mb-3">Document Handlers</h3>
          <div className="space-y-3">
            {documentHandlers.map((model) => {
              const details = MODEL_DETAILS[model.name];
              return (
                <div 
                  key={model.name}
                  className="bg-navy p-4 rounded-lg border border-navy-lighter hover:border-gold transition-colors"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold text-white">
                          {details?.fullName || model.name}
                        </h3>
                        <span 
                          className={`px-3 py-1 rounded-full text-xs font-medium ${
                            model.status === 'loaded'
                              ? 'bg-green-900/30 text-green-400 border border-green-500/30'
                              : 'bg-gray-800 text-gray-400 border border-gray-600'
                          }`}
                        >
                          {model.status.toUpperCase()}
                        </span>
                        <span className="text-xs px-2 py-1 rounded-full bg-green-900/20 text-green-400 border border-green-500/20">
                          NVIDIA NIM
                        </span>
                      </div>
                      
                      {model.description && (
                        <p className="text-sm text-gray-300 mb-2">{model.description}</p>
                      )}
                      
                      <p className="text-xs text-red-300 mb-2">
                        Recommended to stay active
                      </p>
                      
                      {model.capabilities && (
                        <div className="flex flex-wrap gap-2 mb-2">
                          {model.capabilities.map((cap) => (
                            <span 
                              key={cap}
                              className="text-xs px-2 py-1 bg-navy-lighter rounded-full text-gray-300"
                            >
                              {getCapabilityLabel(cap)}
                            </span>
                          ))}
                        </div>
                      )}
                      
                      <div className="flex items-center gap-4 text-xs">
                        <span><span className="text-yellow-400">Type:</span> <span className="text-white">Embedding Model</span></span>
                        {model.memory_usage && (
                          <span><span className="text-yellow-400">VRAM:</span> <span className="text-white">{(model.memory_usage / 1024 / 1024 / 1024).toFixed(1)}GB</span></span>
                        )}
                      </div>
                    </div>
                    
                    <div className="ml-4">
                      <span className="px-4 py-1.5 bg-gray-800 text-gray-500 border border-gray-700 rounded-full text-sm">
                        Always On
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
      
      {/* Document Processing Services Section */}
      <div>
        <h3 className="text-lg font-semibold text-gold mb-3">Document Processing Services</h3>
        <div className="bg-navy p-4 rounded-lg border border-navy-lighter">
          <p className="text-sm text-gray-300 mb-3">
            These services automatically extract text from uploaded documents. They run as part of the backend and don't require separate loading.
          </p>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-navy-lighter p-3 rounded-lg">
              <h4 className="text-white font-medium mb-2">PDF Documents</h4>
              <p className="text-xs text-gray-400 mb-1">Service: PyPDF2</p>
              <p className="text-xs text-gray-300">Extracts text from PDF files including multi-page documents</p>
            </div>
            <div className="bg-navy-lighter p-3 rounded-lg">
              <h4 className="text-white font-medium mb-2">Word Documents</h4>
              <p className="text-xs text-gray-400 mb-1">Service: python-docx</p>
              <p className="text-xs text-gray-300">Processes .docx files and extracts formatted text</p>
            </div>
            <div className="bg-navy-lighter p-3 rounded-lg">
              <h4 className="text-white font-medium mb-2">Spreadsheets</h4>
              <p className="text-xs text-gray-400 mb-1">Service: pandas</p>
              <p className="text-xs text-gray-300">Handles .xlsx and .xls files, converts to searchable text</p>
            </div>
            <div className="bg-navy-lighter p-3 rounded-lg">
              <h4 className="text-white font-medium mb-2">Plain Text</h4>
              <p className="text-xs text-gray-400 mb-1">Service: Built-in</p>
              <p className="text-xs text-gray-300">Direct reading of .txt, .md, and code files</p>
            </div>
          </div>
          <div className="mt-3 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-green-400"></span>
            <span className="text-xs text-green-400">All services active and ready</span>
          </div>
        </div>
      </div>
      
      <div className="flex justify-end mt-4">
        <button 
          onClick={fetchModels}
          className="px-4 py-2 bg-navy hover:bg-navy-lighter text-white rounded-md flex items-center gap-2"
        >
          <Icon name="refresh" size={16} />
          Refresh
        </button>
      </div>
    </div>
  );
};