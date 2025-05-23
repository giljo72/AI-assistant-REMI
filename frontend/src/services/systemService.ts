import api from './api';

/**
 * System service status information
 */
export interface ServiceStatus {
  name: string;
  status: 'running' | 'stopped' | 'error' | 'unknown';
  version?: string;
  port?: number;
  pid?: number;
  uptime?: string;
  memory_usage?: number;
  cpu_usage?: number;
}

/**
 * AI Model information - Updated for real multi-model system
 */
export interface ModelInfo {
  name: string;
  type: 'ollama' | 'nvidia-nim' | 'nemo' | 'transformers';
  status: 'loaded' | 'unloaded' | 'loading' | 'error';
  size?: string;
  parameters?: string;
  quantization?: string;
  memory_usage?: number;
  context_length?: number;
  last_used?: string;
}

/**
 * Environment information
 */
export interface EnvironmentInfo {
  python_version: string;
  node_version: string;
  cuda_version?: string;
  pytorch_version?: string;
  pgvector_version?: string;
  os_info: string;
  total_memory: number;
  available_memory: number;
  gpu_info?: {
    name: string;
    memory_total: number;
    memory_used: number;
    gpu_utilization: number;
    temperature?: number;
  };
}

/**
 * Complete system status
 */
export interface SystemStatus {
  services: ServiceStatus[];
  models: ModelInfo[];
  environment: EnvironmentInfo;
  last_updated: string;
}

/**
 * Model loading request
 */
export interface ModelLoadRequest {
  model_name: string;
  model_type: 'ollama' | 'nvidia-nim' | 'nemo' | 'transformers';
  force_reload?: boolean;
}

/**
 * Service control request
 */
export interface ServiceControlRequest {
  service_name: string;
  action: 'start' | 'stop' | 'restart';
}

/**
 * Response format for system operations
 */
export interface SystemOperationResponse {
  success: boolean;
  message: string;
  data?: any;
}

/**
 * Service for system and model management - NO MORE MOCK DATA
 */
const systemService = {
  /**
   * Get complete system status - REAL DATA ONLY
   */
  getSystemStatus: async (): Promise<SystemStatus> => {
    try {
      console.log('🔍 Fetching real system status from backend...');
      const response = await api.get('/system/status');
      console.log('✅ Real system status received:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Failed to fetch system status:', error);
      // Instead of mock data, throw error to show real connection issues
      throw new Error(`Cannot connect to backend API: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  },

  /**
   * Load a specific model - REAL API ONLY
   */
  loadModel: async (request: ModelLoadRequest): Promise<SystemOperationResponse> => {
    try {
      console.log('🚀 Loading model via real API:', request);
      const response = await api.post('/system/models/load', request);
      console.log('✅ Model load response:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Failed to load model:', error);
      throw new Error(`Failed to load model: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  },

  /**
   * Unload a specific model - REAL API ONLY
   */
  unloadModel: async (model_name: string, model_type: string): Promise<SystemOperationResponse> => {
    try {
      console.log('🛑 Unloading model via real API:', model_name, model_type);
      const response = await api.post('/system/models/unload', { 
        model_name, 
        model_type 
      });
      console.log('✅ Model unload response:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Failed to unload model:', error);
      throw new Error(`Failed to unload model: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  },

  /**
   * Switch active model - REAL API ONLY
   */
  switchModel: async (model_name: string, model_type: string): Promise<SystemOperationResponse> => {
    try {
      console.log('🔄 Switching model via real API:', model_name, model_type);
      const response = await api.post('/system/models/switch', { 
        model_name,
        model_type 
      });
      console.log('✅ Model switch response:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Failed to switch model:', error);
      throw new Error(`Failed to switch model: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  },

  /**
   * Control system services - REAL API ONLY
   */
  controlService: async (request: ServiceControlRequest): Promise<SystemOperationResponse> => {
    try {
      console.log('⚙️ Controlling service via real API:', request);
      const response = await api.post('/system/services/control', request);
      console.log('✅ Service control response:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Failed to control service:', error);
      throw new Error(`Failed to control service: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  },

  /**
   * Get available models - REAL API ONLY
   */
  getAvailableModels: async (): Promise<ModelInfo[]> => {
    try {
      console.log('📋 Fetching available models from real API...');
      const response = await api.get('/system/models/available');
      console.log('✅ Available models received:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Failed to fetch available models:', error);
      throw new Error(`Failed to fetch models: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }
};

export default systemService;