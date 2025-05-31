import api from './api';
import { ProjectId, normalizeProjectId, isValidProjectId } from '../types/common';

/**
 * File interface representing file metadata
 */
export interface File {
  id: string;
  name: string;
  type: string; // file extension: PDF, DOCX, etc.
  size: number; // in bytes
  description?: string;
  project_id?: ProjectId; 
  project_name?: string; // Name of the project this file is linked to
  created_at: string;
  updated_at?: string;
  filepath: string;
  processed: boolean; // Indicates if the file has been processed into vector DB
  processing_failed?: boolean; // If processing failed
  chunk_count?: number; // Number of chunks if processed
  active: boolean;
}

/**
 * Extended file interface with metadata and tags
 */
export interface FileWithMetadata extends File {
  meta_data?: Record<string, any>; // Additional metadata extracted from the file
  tags?: string[];
}

/**
 * Request parameters for file upload
 */
export interface FileUploadRequest {
  file: File | Blob;
  name?: string;
  description?: string;
  project_id?: string;
}

/**
 * Request parameters for file processing
 */
export interface FileProcessRequest {
  file_id: string;
  chunk_size?: number; // Optional custom chunk size
  chunk_overlap?: number; // Optional overlap between chunks
}

/**
 * Request parameters for file search
 */
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

/**
 * File search result with relevance score and content snippets
 */
export interface FileSearchResult extends File {
  relevance: number; // 0-100 relevance score
  content_snippets?: string[]; // Relevant text snippets from the document
  project_name?: string; // Name of the project this file is linked to
}

/**
 * Options for filtering files
 */
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

/**
 * Options for sorting files
 */
export interface FileSortOptions {
  field: 'name' | 'size' | 'created_at' | 'updated_at' | 'type' | 'project_id' | 'processed';
  direction: 'asc' | 'desc';
}

/**
 * Request parameters for linking files to projects
 */
export interface FileLinkRequest {
  file_ids: string[];
  project_id: string;
}

/**
 * Request parameters for updating file metadata
 */
export interface FileUpdateRequest {
  name?: string;
  description?: string;
  active?: boolean;
  tags?: string[];
  project_id?: string;
}

/**
 * Response format for bulk file operations
 */
export interface FileBulkOperationResult {
  success: string[]; // Array of file IDs that were successfully processed
  failed: {
    id: string;
    error: string;
  }[];
  project_id?: string; // The project ID involved in the operation
  project_name?: string; // The project name involved in the operation
}

/**
 * Processing statistics for all files
 */
export interface ProcessingStats {
  total_files: number;
  processed_files: number;
  failed_files: number;
  processing_files: number;
  total_chunks: number;
  gpu_usage?: number; // Current GPU usage percentage if available
  eta?: number; // Estimated time in seconds for current processing queue to complete
}

// Central event dispatcher for file-related events
const fileEvents = {
  dispatchFileChange: () => {
    const event = new CustomEvent('file-change');
    window.dispatchEvent(event);
  },
  
  dispatchFileUpload: (file: File) => {
    const event = new CustomEvent('file-upload', { detail: file });
    window.dispatchEvent(event);
  },
  
  dispatchFileDelete: (fileId: string) => {
    const event = new CustomEvent('file-delete', { detail: { id: fileId } });
    window.dispatchEvent(event);
  },
  
  dispatchFileLinkChange: (fileIds: string[], projectId: ProjectId, projectName?: string) => {
    const event = new CustomEvent('file-link-change', { 
      detail: { fileIds, projectId, projectName } 
    });
    window.dispatchEvent(event);
  }
};

/**
 * File service for interacting with the backend API
 */
const fileService = {
  /**
   * Get all files with optional filtering and sorting
   */
  getAllFiles: async (
    filterOptions?: FileFilterOptions,
    sortOptions?: FileSortOptions
  ): Promise<File[]> => {
    console.log("[FILES] Getting all files with options:", { filterOptions, sortOptions });
    
    try {
      // Build query parameters
      const params = new URLSearchParams();
      
      if (filterOptions) {
        if (filterOptions.project_id !== undefined) {
          // When project_id is null, we want to send 'null' string to indicate global files
          params.append('project_id', filterOptions.project_id === null ? 'null' : filterOptions.project_id);
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
      
      // Make API call to get files
      const response = await api.get('/files/', { params });
      
      // Normalize project IDs to ensure consistent types
      const files = response.data.map((file: any) => ({
        ...file,
        project_id: normalizeProjectId(file.project_id)
      }));
      
      console.log(`[FILES] Retrieved ${files.length} files from backend`);
      return files;
      
    } catch (error) {
      console.error("[FILES] Error getting files:", error);
      throw error;
    }
  },

  /**
   * Get a single file by ID
   */
  getFile: async (id: string): Promise<FileWithMetadata> => {
    try {
      const response = await api.get(`/files/${id}`);
      
      // Normalize project ID
      const file = {
        ...response.data,
        project_id: normalizeProjectId(response.data.project_id)
      };
      
      return file;
    } catch (error) {
      console.error(`[FILES] Error getting file ${id}:`, error);
      throw error;
    }
  },

  /**
   * Upload a new file with optional metadata
   */
  uploadFile: async (fileData: FileUploadRequest): Promise<File> => {
    console.log("[UPLOAD] Uploading file:", fileData.name);
    
    try {
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
      
      const response = await api.post('/files/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      // Normalize the returned file's project ID
      const file = {
        ...response.data,
        project_id: normalizeProjectId(response.data.project_id)
      };
      
      // Dispatch event to notify components about the new file
      fileEvents.dispatchFileUpload(file);
      
      console.log("[UPLOAD] File uploaded successfully:", file.id);
      return file;
    } catch (error) {
      console.error("Error uploading file:", error);
      throw error;
    }
  },

  /**
   * Download a file
   */
  downloadFile: async (id: string): Promise<Blob> => {
    try {
      const response = await api.get(`/files/${id}/download`, {
        responseType: 'blob',
      });
      
      return response.data;
    } catch (error) {
      console.error(`[FILES] Error downloading file ${id}:`, error);
      throw error;
    }
  },

  /**
   * Process a file into vector embeddings
   */
  processFile: async (processRequest: FileProcessRequest): Promise<File> => {
    try {
      const response = await api.post('/files/process', processRequest);
      
      const file = {
        ...response.data,
        project_id: normalizeProjectId(response.data.project_id)
      };
      
      // Trigger file change event
      fileEvents.dispatchFileChange();
      
      return file;
    } catch (error) {
      console.error(`[FILES] Error processing file ${processRequest.file_id}:`, error);
      throw error;
    }
  },

  /**
   * Retry processing for a file that failed
   */
  retryProcessing: async (fileId: string): Promise<File> => {
    try {
      const response = await api.post(`/files/${fileId}/retry-processing`);
      
      const file = {
        ...response.data,
        project_id: normalizeProjectId(response.data.project_id)
      };
      
      // Trigger file change event
      fileEvents.dispatchFileChange();
      
      return file;
    } catch (error) {
      console.error(`[FILES] Error retrying processing for file ${fileId}:`, error);
      throw error;
    }
  },

  /**
   * Update file metadata
   */
  updateFile: async (id: string, updateData: FileUpdateRequest): Promise<File> => {
    try {
      const response = await api.patch(`/files/${id}`, updateData);
      
      const file = {
        ...response.data,
        project_id: normalizeProjectId(response.data.project_id)
      };
      
      // Trigger file change event
      fileEvents.dispatchFileChange();
      
      return file;
    } catch (error) {
      console.error(`[FILES] Error updating file ${id}:`, error);
      throw error;
    }
  },

  /**
   * Delete a file
   */
  deleteFile: async (id: string): Promise<{ success: boolean }> => {
    try {
      const response = await api.delete(`/files/${id}`);
      
      // Dispatch event to notify components
      fileEvents.dispatchFileDelete(id);
      
      return response.data;
    } catch (error) {
      console.error(`[FILES] Error deleting file ${id}:`, error);
      throw error;
    }
  },

  /**
   * Delete multiple files
   */
  bulkDeleteFiles: async (ids: string[]): Promise<FileBulkOperationResult> => {
    try {
      const response = await api.post('/files/bulk-delete', { file_ids: ids });
      
      // For each successfully deleted file, dispatch an event
      response.data.success.forEach((fileId: string) => {
        fileEvents.dispatchFileDelete(fileId);
      });
      
      return response.data;
    } catch (error) {
      console.error(`[FILES] Error deleting multiple files:`, error);
      throw error;
    }
  },

  /**
   * Link one or more files to a project
   */
  linkFilesToProject: async (linkRequest: FileLinkRequest): Promise<FileBulkOperationResult> => {
    try {
      const response = await api.post('/files/link', linkRequest);
      
      // Normalize the project ID for consistency
      const normalizedProjectId = normalizeProjectId(linkRequest.project_id);
      
      // Dispatch event for successful links
      if (response.data.success.length > 0) {
        fileEvents.dispatchFileLinkChange(
          response.data.success, 
          normalizedProjectId,
          response.data.project_name
        );
      }
      
      return response.data;
    } catch (error) {
      console.error(`[FILES] Error linking files to project:`, error);
      throw error;
    }
  },

  /**
   * Unlink one or more files from a project
   */
  unlinkFilesFromProject: async (fileIds: string[], projectId: string): Promise<FileBulkOperationResult> => {
    try {
      const response = await api.post('/files/unlink', {
        file_ids: fileIds,
        project_id: projectId,
      });
      
      // Dispatch event for successful unlinks
      if (response.data.success.length > 0) {
        fileEvents.dispatchFileLinkChange(
          response.data.success, 
          null,
          null // No project name when unlinking
        );
      }
      
      return response.data;
    } catch (error) {
      console.error(`[FILES] Error unlinking files from project:`, error);
      throw error;
    }
  },

  /**
   * Search within file contents
   */
  searchFileContents: async (searchRequest: FileSearchRequest): Promise<FileSearchResult[]> => {
    try {
      // Normalize project ID if provided
      const normalizedSearchRequest = {
        ...searchRequest,
        project_id: searchRequest.project_id ? searchRequest.project_id : undefined
      };
      
      const response = await api.post('/files/search', normalizedSearchRequest);
      
      // Normalize project IDs in the response
      const results = response.data.map((file: any) => ({
        ...file,
        project_id: normalizeProjectId(file.project_id)
      }));
      
      return results;
    } catch (error) {
      console.error(`[FILES] Error searching files:`, error);
      throw error;
    }
  },

  /**
   * Get a preview of file contents
   */
  getFilePreview: async (id: string, maxLength?: number): Promise<{ content: string }> => {
    try {
      const params = new URLSearchParams();
      
      if (maxLength) {
        params.append('max_length', maxLength.toString());
      }
      
      const response = await api.get(`/files/${id}/preview`, { params });
      return response.data;
    } catch (error) {
      console.error(`[FILES] Error getting file preview for ${id}:`, error);
      throw error;
    }
  },

  /**
   * Get current processing status for all files
   */
  getProcessingStatus: async (): Promise<ProcessingStats> => {
    try {
      const response = await api.get('/files/processing-status');
      return response.data;
    } catch (error) {
      console.error(`[FILES] Error getting processing status:`, error);
      
      // Return a default object instead of propagating the error
      // This makes GPU monitoring more resilient
      return {
        total_files: 0,
        processed_files: 0,
        failed_files: 0,
        processing_files: 0,
        total_chunks: 0,
        gpu_usage: 0,
        eta: 0
      };
    }
  },

  /**
   * Get all file tags in the system
   */
  getAllTags: async (): Promise<string[]> => {
    try {
      const response = await api.get('/files/tags');
      return response.data;
    } catch (error) {
      console.error(`[FILES] Error getting file tags:`, error);
      throw error;
    }
  },
};

export default fileService;