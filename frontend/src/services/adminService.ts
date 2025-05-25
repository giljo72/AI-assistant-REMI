import api from './api';

/**
 * System information returned by the admin API
 */
export interface SystemInfo {
  database: {
    table_count: number;
    document_count: number;
    project_count: number;
    chunk_count: number;
    embedding_count: number;
  };
  files: {
    upload_count: number;
    upload_size_bytes: number;
    processed_count: number;
    processed_size_bytes: number;
    total_count: number;
    total_size_bytes: number;
  };
}

/**
 * Reset options for the database
 */
export interface DatabaseResetOptions {
  tables?: string[];
}

/**
 * Response format for admin operations
 */
export interface AdminOperationResponse {
  success: boolean;
  message: string;
}

/**
 * Service for admin functionality
 */
const adminService = {
  /**
   * Get system information
   */
  getSystemInfo: async (): Promise<SystemInfo> => {
    try {
      const response = await api.get('/admin/system-info');
      return response.data;
    } catch (error) {
      console.error('[ADMIN] Error getting system info:', error);
      throw error;
    }
  },
  
  /**
   * Reset database tables
   */
  resetDatabase: async (preservePrompts: boolean = true): Promise<AdminOperationResponse> => {
    try {
      const response = await api.post('/admin/reset/database', null, {
        params: { preserve_prompts: preservePrompts }
      });
      return response.data;
    } catch (error) {
      console.error('[ADMIN] Error resetting database:', error);
      throw error;
    }
  },
  
  /**
   * Reset vector store
   */
  resetVectorStore: async (): Promise<AdminOperationResponse> => {
    try {
      const response = await api.post('/admin/reset/vector-store');
      return response.data;
    } catch (error) {
      console.error('[ADMIN] Error resetting vector store:', error);
      throw error;
    }
  },
  
  /**
   * Reset files
   */
  resetFiles: async (): Promise<AdminOperationResponse> => {
    try {
      const response = await api.post('/admin/reset/files');
      return response.data;
    } catch (error) {
      console.error('[ADMIN] Error resetting files:', error);
      throw error;
    }
  },
  
  /**
   * Reset everything (database, vector store, and files)
   */
  resetEverything: async (): Promise<AdminOperationResponse> => {
    try {
      const response = await api.post('/admin/reset/all');
      return response.data;
    } catch (error) {
      console.error('[ADMIN] Error resetting everything:', error);
      throw error;
    }
  }
};

export default adminService;