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