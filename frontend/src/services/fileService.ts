import api from './api';

export interface File {
  id: string;
  name: string;
  type: string; // file extension: PDF, DOCX, etc.
  size: number; // in bytes
  description?: string;
  project_id?: string | null; // null for unattached documents
  created_at: string;
  updated_at?: string;
  filepath: string;
  processed: boolean; // Indicates if the file has been processed into vector DB
  processing_failed?: boolean; // If processing failed
  chunk_count?: number; // Number of chunks if processed
  active: boolean;
}

export interface FileWithMetadata extends File {
  meta_data?: Record<string, any>; // Additional metadata extracted from the file
  tags?: string[];
}

export interface FileUploadRequest {
  file: File | Blob;
  name?: string;
  description?: string;
  project_id?: string;
  tags?: string[];
}

export interface FileProcessRequest {
  file_id: string;
  chunk_size?: number; // Optional custom chunk size
  chunk_overlap?: number; // Optional overlap between chunks
}

export interface FileSearchRequest {
  query: string;
  project_id?: string; // Limit search to specific project
  file_types?: string[]; // Filter by file types
  date_range?: {
    start?: string;
    end?: string;
  };
  limit?: number;
  include_content?: boolean; // Whether to include content snippets in results
}

export interface FileSearchResult extends File {
  relevance: number; // 0-100 relevance score
  content_snippets?: string[]; // Relevant text snippets from the document
}

export interface FileFilterOptions {
  project_id?: string | null; // null gets unattached, undefined gets all
  file_types?: string[];
  processed_only?: boolean;
  active_only?: boolean;
  date_range?: {
    start?: string;
    end?: string;
  };
  tags?: string[];
  processing_status?: 'all' | 'processed' | 'unprocessed' | 'failed';
}

export interface FileSortOptions {
  field: 'name' | 'size' | 'created_at' | 'updated_at' | 'type' | 'project_id' | 'processed';
  direction: 'asc' | 'desc';
}

export interface FileLinkRequest {
  file_ids: string[];
  project_id: string;
}

export interface FileUpdateRequest {
  name?: string;
  description?: string;
  active?: boolean;
  tags?: string[];
}

export interface FileBulkOperationResult {
  success: string[]; // Array of file IDs that were successfully processed
  failed: {
    id: string;
    error: string;
  }[];
}

export interface ProcessingStats {
  total_files: number;
  processed_files: number;
  failed_files: number;
  processing_files: number;
  total_chunks: number;
  gpu_usage?: number; // Current GPU usage percentage if available
  eta?: number; // Estimated time in seconds for current processing queue to complete
}

const fileService = {
  /**
   * Get all files with optional filtering and sorting
   */
  getAllFiles: async (
    filterOptions?: FileFilterOptions,
    sortOptions?: FileSortOptions
  ): Promise<File[]> => {
    // Build query parameters
    const params = new URLSearchParams();
    
    if (filterOptions) {
      if (filterOptions.project_id !== undefined) {
        params.append('project_id', filterOptions.project_id || 'null');
      }
      
      if (filterOptions.file_types?.length) {
        filterOptions.file_types.forEach(type => {
          params.append('file_type', type);
        });
      }
      
      if (filterOptions.processed_only) {
        params.append('processed', 'true');
      }
      
      if (filterOptions.active_only) {
        params.append('active', 'true');
      }
      
      if (filterOptions.date_range?.start) {
        params.append('date_start', filterOptions.date_range.start);
      }
      
      if (filterOptions.date_range?.end) {
        params.append('date_end', filterOptions.date_range.end);
      }
      
      if (filterOptions.tags?.length) {
        filterOptions.tags.forEach(tag => {
          params.append('tag', tag);
        });
      }
      
      if (filterOptions.processing_status && filterOptions.processing_status !== 'all') {
        params.append('processing_status', filterOptions.processing_status);
      }
    }
    
    if (sortOptions) {
      params.append('sort_field', sortOptions.field);
      params.append('sort_direction', sortOptions.direction);
    }
    
    const response = await api.get('/files', { params });
    return response.data;
  },

  /**
   * Get a single file by ID
   */
  getFile: async (id: string): Promise<FileWithMetadata> => {
    const response = await api.get(`/files/${id}`);
    return response.data;
  },

  /**
   * Upload a new file with optional metadata
   */
  uploadFile: async (fileData: FileUploadRequest): Promise<File> => {
    // Use FormData for file uploads
    const formData = new FormData();
    formData.append('file', fileData.file);
    
    if (fileData.name) {
      formData.append('name', fileData.name);
    }
    
    if (fileData.description) {
      formData.append('description', fileData.description);
    }
    
    if (fileData.project_id) {
      formData.append('project_id', fileData.project_id);
    }
    
    if (fileData.tags?.length) {
      fileData.tags.forEach(tag => {
        formData.append('tags', tag);
      });
    }
    
    const response = await api.post('/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },

  /**
   * Download a file
   */
  downloadFile: async (id: string): Promise<Blob> => {
    const response = await api.get(`/files/${id}/download`, {
      responseType: 'blob',
    });
    
    return response.data;
  },

  /**
   * Process a file into vector embeddings
   */
  processFile: async (processRequest: FileProcessRequest): Promise<File> => {
    const response = await api.post('/files/process', processRequest);
    return response.data;
  },

  /**
   * Retry processing for a file that failed
   */
  retryProcessing: async (fileId: string): Promise<File> => {
    const response = await api.post(`/files/${fileId}/retry-processing`);
    return response.data;
  },

  /**
   * Update file metadata
   */
  updateFile: async (id: string, updateData: FileUpdateRequest): Promise<File> => {
    const response = await api.patch(`/files/${id}`, updateData);
    return response.data;
  },

  /**
   * Delete a file
   */
  deleteFile: async (id: string): Promise<{ success: boolean }> => {
    const response = await api.delete(`/files/${id}`);
    return response.data;
  },

  /**
   * Delete multiple files
   */
  bulkDeleteFiles: async (ids: string[]): Promise<FileBulkOperationResult> => {
    const response = await api.post('/files/bulk-delete', { file_ids: ids });
    return response.data;
  },

  /**
   * Link one or more files to a project
   */
  linkFilesToProject: async (linkRequest: FileLinkRequest): Promise<FileBulkOperationResult> => {
    const response = await api.post('/files/link', linkRequest);
    return response.data;
  },

  /**
   * Unlink one or more files from a project
   */
  unlinkFilesFromProject: async (fileIds: string[], projectId: string): Promise<FileBulkOperationResult> => {
    const response = await api.post('/files/unlink', {
      file_ids: fileIds,
      project_id: projectId,
    });
    
    return response.data;
  },

  /**
   * Search within file contents
   */
  searchFileContents: async (searchRequest: FileSearchRequest): Promise<FileSearchResult[]> => {
    const response = await api.post('/files/search', searchRequest);
    return response.data;
  },

  /**
   * Get a preview of file contents
   */
  getFilePreview: async (id: string, maxLength?: number): Promise<{ content: string }> => {
    const params = new URLSearchParams();
    
    if (maxLength) {
      params.append('max_length', maxLength.toString());
    }
    
    const response = await api.get(`/files/${id}/preview`, { params });
    return response.data;
  },

  /**
   * Get current processing status for all files
   */
  getProcessingStatus: async (): Promise<ProcessingStats> => {
    const response = await api.get('/files/processing-status');
    return response.data;
  },

  /**
   * Get all file tags in the system
   */
  getAllTags: async (): Promise<string[]> => {
    const response = await api.get('/files/tags');
    return response.data;
  },
};

export default fileService;