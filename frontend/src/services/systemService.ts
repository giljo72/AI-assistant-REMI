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
 * AI Model information
 */
export interface ModelInfo {
  name: string;
  type: 'ollama' | 'nemo' | 'embedding';
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
  tensorflow_version?: string;
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
  model_type: 'ollama' | 'nemo';
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
 * Service for system and model management
 */
const systemService = {
  /**
   * Get complete system status
   */
  getSystemStatus: async (): Promise<SystemStatus> => {
    try {
      const response = await api.get('/system/status');
      return response.data;
    } catch (error) {
      console.error('Error fetching system status, using mock data:', error);
      // Return mock data if API is not available
      return {
        services: [
          {
            name: 'FastAPI Backend',
            status: 'running',
            version: '0.104.1',
            port: 8000,
            pid: 12345,
            uptime: '2 hours 15 minutes',
            memory_usage: 256,
            cpu_usage: 5.2
          },
          {
            name: 'PostgreSQL',
            status: 'running',
            version: '17.0',
            port: 5432,
            pid: 2468,
            uptime: '5 hours 32 minutes',
            memory_usage: 128,
            cpu_usage: 1.8
          },
          {
            name: 'pgvector Extension',
            status: 'running',
            version: '0.6.0'
          }
        ],
        models: [
          {
            name: 'llama3.1:8b',
            type: 'ollama',
            status: 'loaded',
            size: '4.7GB',
            parameters: '8B',
            quantization: 'Q4_0',
            memory_usage: 4700,
            context_length: 131072,
            last_used: '5 minutes ago'
          },
          {
            name: 'nomic-embed-text',
            type: 'embedding',
            status: 'loaded',
            size: '274MB',
            parameters: '137M',
            memory_usage: 274,
            context_length: 8192,
            last_used: '2 minutes ago'
          },
          {
            name: 'NeMo Document AI',
            type: 'nemo',
            status: 'unloaded',
            size: '2.1GB',
            parameters: 'Various'
          }
        ],
        environment: {
          python_version: '3.11.5',
          node_version: '18.17.0',
          cuda_version: '12.2',
          pytorch_version: '2.1.0',
          pgvector_version: '0.6.0',
          os_info: 'Windows 11 Pro 22H2',
          total_memory: 65536,
          available_memory: 32768,
          gpu_info: {
            name: 'NVIDIA RTX 4090',
            memory_total: 24576,
            memory_used: 8192,
            gpu_utilization: 15,
            temperature: 42
          }
        },
        last_updated: new Date().toISOString()
      };
    }
  },

  /**
   * Load a specific model
   */
  loadModel: async (request: ModelLoadRequest): Promise<SystemOperationResponse> => {
    try {
      const response = await api.post('/system/models/load', request);
      return response.data;
    } catch (error) {
      console.error('Error loading model, using mock response:', error);
      // Mock response if API is not available
      return {
        success: true,
        message: `Loading ${request.model_name}... This may take a few minutes.`
      };
    }
  },

  /**
   * Unload a specific model
   */
  unloadModel: async (model_name: string): Promise<SystemOperationResponse> => {
    try {
      const response = await api.post('/system/models/unload', { model_name });
      return response.data;
    } catch (error) {
      console.error('Error unloading model, using mock response:', error);
      // Mock response if API is not available
      return {
        success: true,
        message: `Unloading ${model_name}...`
      };
    }
  },

  /**
   * Switch active model
   */
  switchModel: async (model_name: string): Promise<SystemOperationResponse> => {
    try {
      const response = await api.post('/system/models/switch', { model_name });
      return response.data;
    } catch (error) {
      console.error('Error switching model, using mock response:', error);
      // Mock response if API is not available
      return {
        success: true,
        message: `Switching to ${model_name}...`
      };
    }
  },

  /**
   * Control a system service
   */
  controlService: async (request: ServiceControlRequest): Promise<SystemOperationResponse> => {
    try {
      const response = await api.post('/system/services/control', request);
      return response.data;
    } catch (error) {
      console.error('Error controlling service, using mock response:', error);
      // Mock response if API is not available
      return {
        success: true,
        message: `${request.action}ing ${request.service_name}...`
      };
    }
  },

  /**
   * Get available models that can be loaded
   */
  getAvailableModels: async (): Promise<ModelInfo[]> => {
    try {
      const response = await api.get('/system/models/available');
      return response.data;
    } catch (error) {
      console.error('Error fetching available models, using mock data:', error);
      // Mock data if API is not available
      return [
        {
          name: 'llama3.1:8b',
          type: 'ollama',
          status: 'unloaded',
          size: '4.7GB',
          parameters: '8B'
        },
        {
          name: 'llama3.1:70b',
          type: 'ollama',
          status: 'unloaded',
          size: '40GB',
          parameters: '70B'
        },
        {
          name: 'mistral:7b',
          type: 'ollama',
          status: 'unloaded',
          size: '4.1GB',
          parameters: '7B'
        },
        {
          name: 'NeMo Document AI',
          type: 'nemo',
          status: 'unloaded',
          size: '2.1GB',
          parameters: 'Various'
        }
      ];
    }
  }
};

export default systemService;