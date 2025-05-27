import api from './api';

interface ModelInfo {
  name: string;
  type: string;
  status: string;
  size: string;
  parameters: string;
  quantization: string;
  context_length: number;
  memory_usage: number;
  last_used: string;
}

interface AvailableModel {
  id: string;
  name: string;
  description: string;
  size: number;
  parameters: string;
  context_length: number;
  requirements: string;
  status: 'loaded' | 'available' | 'loading';
  model_type: 'general' | 'coding' | 'reasoning';
}

interface AdminPanelData {
  current_model: string;
  total_vram: number;
  used_vram: number;
  models: ModelInfo[];
  available_models: AvailableModel[];
  gpu_name: string;
  warnings: string[];
}

interface LoadModelResponse {
  success: boolean;
  message: string;
  model_name?: string;
  error?: string;
}

interface UnloadModelResponse {
  success: boolean;
  message: string;
  model_name?: string;
  error?: string;
}

class SystemService {
  private activeModelCache: { model: string | null; timestamp: number } | null = null;
  private availableModelsCache: { models: AvailableModel[]; timestamp: number } | null = null;
  private readonly CACHE_DURATION = 5000; // 5 seconds

  async getActiveModelQuick(): Promise<string> {
    // Check cache first
    const now = Date.now();
    if (this.activeModelCache && (now - this.activeModelCache.timestamp) < this.CACHE_DURATION) {
      return this.activeModelCache.model || 'qwen2.5:32b-instruct-q4_K_M';
    }

    try {
      // Try the fast endpoint first
      const response = await api.get('/system/active-model-quick');
      const activeModel = response.data.active_model || 'qwen2.5:32b-instruct-q4_K_M';
      
      // Update cache
      this.activeModelCache = { model: activeModel, timestamp: now };
      
      return activeModel;
    } catch (error) {
      console.error('Error fetching active model:', error);
      // Fall back to default
      return 'qwen2.5:32b-instruct-q4_K_M';
    }
  }

  /**
   * Get admin panel data for model management
   */
  async getAdminPanelData(): Promise<AdminPanelData> {
    try {
      const response = await api.get<AdminPanelData>('/admin/panel');
      return response.data;
    } catch (error) {
      console.error('Error fetching admin panel data:', error);
      throw error;
    }
  }

  /**
   * Load a specific model
   */
  async loadModel(modelName: string): Promise<LoadModelResponse> {
    try {
      console.log(`Loading model: ${modelName}`);
      const response = await api.post<LoadModelResponse>('/admin/load-model', { model_name: modelName });
      
      // Clear caches when model changes
      this.activeModelCache = null;
      this.availableModelsCache = null;
      
      return response.data;
    } catch (error: any) {
      console.error('Error loading model:', error);
      
      // Extract error message from response if available
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to load model';
      
      return {
        success: false,
        message: errorMessage,
        error: errorMessage
      };
    }
  }

  /**
   * Unload a specific model
   */
  async unloadModel(modelName: string): Promise<UnloadModelResponse> {
    try {
      console.log(`Unloading model: ${modelName}`);
      const response = await api.post<UnloadModelResponse>('/admin/unload-model', { model_name: modelName });
      
      // Clear caches when model changes
      this.activeModelCache = null;
      this.availableModelsCache = null;
      
      return response.data;
    } catch (error: any) {
      console.error('Error unloading model:', error);
      
      // Extract error message from response if available
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to unload model';
      
      return {
        success: false,
        message: errorMessage,
        error: errorMessage
      };
    }
  }

  /**
   * Restart a model (unload and reload)
   */
  async restartModel(modelName: string): Promise<LoadModelResponse> {
    try {
      console.log(`Restarting model: ${modelName}`);
      
      // First unload
      const unloadResult = await this.unloadModel(modelName);
      if (!unloadResult.success) {
        return {
          success: false,
          message: `Failed to unload model: ${unloadResult.message}`,
          error: unloadResult.error
        };
      }
      
      // Then load again
      return await this.loadModel(modelName);
    } catch (error: any) {
      console.error('Error restarting model:', error);
      return {
        success: false,
        message: 'Failed to restart model',
        error: error.message
      };
    }
  }

  /**
   * Get available models from the system
   */
  async getAvailableModels(): Promise<AvailableModel[]> {
    // Check cache first
    const now = Date.now();
    if (this.availableModelsCache && (now - this.availableModelsCache.timestamp) < this.CACHE_DURATION) {
      return this.availableModelsCache.models;
    }

    try {
      console.log('📋 Fetching available models from real API...');
      const response = await api.get<AvailableModel[]>('/system/models/available');
      console.log('✅ Available models received:', response.data);
      
      // Update cache
      this.availableModelsCache = { models: response.data, timestamp: now };
      
      return response.data;
    } catch (error) {
      console.error('❌ Error fetching available models:', error);
      throw error;
    }
  }

  /**
   * Get VRAM usage quickly
   */
  async getVramUsageQuick(): Promise<{ used_gb: number; total_gb: number; free_gb: number }> {
    try {
      const response = await api.get('/system/vram-usage-quick');
      return response.data;
    } catch (error) {
      console.error('Error fetching VRAM usage:', error);
      return { used_gb: 0, total_gb: 24, free_gb: 24 };
    }
  }

  /**
   * Get system resources (CPU, RAM, Disk)
   */
  async getSystemResources(): Promise<any> {
    try {
      const response = await api.get('/system/resources');
      return response.data;
    } catch (error) {
      console.error('Error fetching system resources:', error);
      throw error;
    }
  }
}

// Export singleton instance
export default new SystemService();
export const systemService = new SystemService();