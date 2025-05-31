import api from './api';

export interface ModelStatus {
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

export interface MemoryStatus {
  total_vram_gb: number;
  used_vram_gb: number;
  allocated_vram_gb: number;
  available_vram_gb: number;
  loaded_models: string[];
}

class ModelService {
  async getModelsStatus(): Promise<ModelStatus[]> {
    const response = await api.get('/models/status');
    return response.data;
  }

  async getQuickModelStatus(): Promise<any> {
    try {
      const response = await api.get('/models/status/quick');
      return response.data;
    } catch (error) {
      console.error('Error fetching quick model status:', error);
      // Return a default structure when backend is not available
      return {
        models: {},
        system: {
          total_vram_gb: 24,
          used_vram_gb: 0,
          available_vram_gb: 24,
          active_primary_model: null,
          total_requests_active: 0
        }
      };
    }
  }

  async getMemoryStatus(): Promise<MemoryStatus> {
    const response = await api.get('/models/memory');
    return response.data;
  }

  async loadModel(modelName: string): Promise<void> {
    await api.post(`/models/load/${modelName}`);
  }

  async unloadModel(modelName: string): Promise<void> {
    await api.post(`/models/unload/${modelName}`);
  }

  async switchMode(mode: string): Promise<void> {
    await api.post(`/models/switch-mode/${mode}`);
  }
}

export const modelService = new ModelService();