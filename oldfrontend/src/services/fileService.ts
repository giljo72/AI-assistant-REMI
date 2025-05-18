import api from './api';

// Add a global mock files array to window
declare global {
  interface Window {
    mockFiles?: any[];
  }
}

// Initialize global mock files if not existing
if (typeof window !== 'undefined') {
  if (!window.mockFiles) {
    // Try to load from localStorage first if available
    try {
      const storedFiles = localStorage.getItem('mockFiles');
      window.mockFiles = storedFiles ? JSON.parse(storedFiles) : [];
      console.log('[GLOBAL] Initialized window.mockFiles from localStorage:', window.mockFiles.length);
    } catch (e) {
      window.mockFiles = [];
      console.log('[GLOBAL] Initialized empty window.mockFiles array');
    }
  }
}

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
  // tags removed per requirements
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
    console.log("[FILES] Getting all files with options:", { filterOptions, sortOptions });
    console.log("[FILES] Caller:", new Error().stack?.split('\n')[2]?.trim());
    
    try {
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
      
      // ALWAYS refresh mockFiles from localStorage to ensure we have the most up-to-date data
      const mockFilesStr = localStorage.getItem('mockFiles');
      let mockFiles: File[] = [];
      
      if (mockFilesStr) {
        try {
          const storedFiles = JSON.parse(mockFilesStr);
          if (storedFiles && Array.isArray(storedFiles)) {
            mockFiles = storedFiles;
            // Always update the global variable to ensure consistency
            window.mockFiles = storedFiles;
            console.log(`[FILES] Refreshed mockFiles from localStorage: ${mockFiles.length}`);
          }
        } catch (e) {
          console.error('[FILES] Error parsing mockFiles from localStorage', e);
          // Fall back to global variable if localStorage parsing fails
          mockFiles = window.mockFiles || [];
        }
      } else {
        // If nothing in localStorage, use global variable
        mockFiles = window.mockFiles || [];
        console.log(`[FILES] No mockFiles in localStorage, using global variable: ${mockFiles.length}`);
      }
      
      // Ensure global variable is always in sync
      if (window.mockFiles !== mockFiles) {
        window.mockFiles = mockFiles;
      }
      
      // Check for last uploaded file ID for debugging
      const lastUploadedId = window.localStorage.getItem('lastUploadedFileId');
      if (lastUploadedId) {
        console.log(`[FILES] Checking for last uploaded file ID: ${lastUploadedId}`);
        const foundFile = mockFiles.find(f => f.id === lastUploadedId);
        if (foundFile) {
          console.log(`[FILES] Found last uploaded file in localStorage:`, foundFile);
        } else {
          console.log(`[FILES] Last uploaded file NOT found in localStorage`);
        }
      }
      
      // Try to get API files
      try {
        const response = await api.get('/files', { params });
        
        // Filter mock files based on options
        let filteredMockFiles = [...mockFiles];
        
        console.log(`[FILES] PROJECT ID FILTER: ${filterOptions?.project_id}`);
        if (filterOptions?.project_id !== undefined) {
          // Filter to include only files for this project (or no project if project_id is null)
          console.log(`[FILES] Filtering files with project_id filter=${filterOptions.project_id}, typeof=${typeof filterOptions.project_id}`);
          console.log(`[FILES] File project_ids before filtering:`, filteredMockFiles.map(f => f.project_id));
          
          // Special handling for empty string in filter - treat as null (global files)
          if (filterOptions.project_id === "") {
            console.log("[FILES] Empty string project_id in filter - treating as null (global files)");
            filterOptions.project_id = null;
          }
          
          filteredMockFiles = filteredMockFiles.filter(file => {
            // Handle empty strings in file project_id as null
            if (file.project_id === "") {
              file.project_id = null;
              console.log(`[FILES] Converting empty project_id to null for file ${file.id}`);
            }
            
            // Handle the "Standard" issue - replace with null for global files
            if (file.project_id === "Standard") {
              file.project_id = null;
              console.log(`[FILES] Converting "Standard" project_id to null for file ${file.id}`);
            }
            
            if (filterOptions.project_id === null) {
              const isUnlinked = file.project_id === null;
              console.log(`[FILES] File ${file.id} project_id=${file.project_id}, is unlinked=${isUnlinked}`);
              return isUnlinked;
            }
            const isLinked = file.project_id === filterOptions.project_id;
            console.log(`[FILES] File ${file.id} project_id=${file.project_id} (type: ${typeof file.project_id}), comparing to filter=${filterOptions.project_id} (type: ${typeof filterOptions.project_id}), matches=${isLinked}`);
            return isLinked;
          });
        } else {
          // If no project filter, get all files (Main File Manager)
          console.log(`[FILES] No project filter, getting all files`);
        }
        
        // If we're getting all files and have mock files, log them
        if (!filterOptions?.project_id && mockFiles.length > 0) {
          console.log(`[FILES] All mock files being returned:`, mockFiles);
        }
        
        const combinedFiles = [...response.data, ...filteredMockFiles];
        console.log(`[FILES] Combined ${response.data.length} API files with ${filteredMockFiles.length} mock files`);
        
        // Apply sorting if needed
        if (sortOptions) {
          // Sort by the appropriate field
          return combinedFiles.sort((a, b) => {
            let aValue = a[sortOptions.field];
            let bValue = b[sortOptions.field];
            
            // Special case for date fields
            if (sortOptions.field === 'created_at' || sortOptions.field === 'updated_at') {
              aValue = new Date(aValue || 0).getTime();
              bValue = new Date(bValue || 0).getTime();
            }
            
            // Compare values
            if (aValue < bValue) {
              return sortOptions.direction === 'asc' ? -1 : 1;
            }
            if (aValue > bValue) {
              return sortOptions.direction === 'asc' ? 1 : -1;
            }
            return 0;
          });
        }
        
        return combinedFiles;
      } catch (apiError) {
        console.warn("[FILES] API call failed, using only mock files", apiError);
        
        // CRITICAL: Reload mock files from localStorage
        // This ensures we always get the latest mock files, even if the original mockFiles variable
        // was loaded before new files were added
        const freshMockFiles = JSON.parse(localStorage.getItem('mockFiles') || '[]');
        console.log(`[FILES] Reloaded fresh mock files: ${freshMockFiles.length}`);
        
        // Filter mock files based on options
        let filteredMockFiles = [...freshMockFiles];
        
        if (filterOptions?.project_id !== undefined) {
          // Filter to include only files for this project (or no project if project_id is null)
          filteredMockFiles = filteredMockFiles.filter(file => {
            if (filterOptions.project_id === null) {
              return file.project_id === null;
            }
            return file.project_id === filterOptions.project_id;
          });
        }
        
        console.log(`[FILES-FALLBACK] Filtered to ${filteredMockFiles.length} mock files`);
        
        // If we're returning all files (Main File Manager), log them
        if (!filterOptions?.project_id && filteredMockFiles.length > 0) {
          console.log(`[FILES-FALLBACK] All mock files:`, filteredMockFiles);
        }
        
        // Apply sorting if needed
        if (sortOptions) {
          // Sort by the appropriate field
          return filteredMockFiles.sort((a, b) => {
            let aValue = a[sortOptions.field];
            let bValue = b[sortOptions.field];
            
            // Special case for date fields
            if (sortOptions.field === 'created_at' || sortOptions.field === 'updated_at') {
              aValue = new Date(aValue || 0).getTime();
              bValue = new Date(bValue || 0).getTime();
            }
            
            // Compare values
            if (aValue < bValue) {
              return sortOptions.direction === 'asc' ? -1 : 1;
            }
            if (aValue > bValue) {
              return sortOptions.direction === 'asc' ? 1 : -1;
            }
            return 0;
          });
        }
        
        return filteredMockFiles;
      }
    } catch (error) {
      console.error("[FILES] Error in getAllFiles:", error);
      
      // In case of any error, reload fresh mock files from localStorage
      const freshMockFiles: File[] = JSON.parse(localStorage.getItem('mockFiles') || '[]');
      console.log(`[FILES-ERROR] Loaded ${freshMockFiles.length} mock files as last resort`);
      
      // Filter mock files based on options
      let filteredMockFiles = [...freshMockFiles];
      
      if (filterOptions?.project_id !== undefined) {
        // Filter to include only files for this project (or no project if project_id is null)
        filteredMockFiles = filteredMockFiles.filter(file => {
          if (filterOptions.project_id === null) {
            return file.project_id === null;
          }
          return file.project_id === filterOptions.project_id;
        });
      }
      
      console.log(`[FILES-ERROR] Returning ${filteredMockFiles.length} mock files after error`);
      return filteredMockFiles;
    }
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
    console.log("[UPLOAD] Attempting to upload file:", fileData.name);
    console.log("[UPLOAD] File details:", {
      name: fileData.name,
      size: (fileData.file as any).size,
      type: (fileData.file as any).type,
      project_id: fileData.project_id
    });
    
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
      
      // Try real API call first
      try {
        const response = await api.post('/files/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        
        console.log("[UPLOAD] API upload successful, response:", response.data);
        return response.data;
      } catch (apiError) {
        console.warn("[UPLOAD] API endpoint not available, using mock implementation", apiError);
        
        // MOCK IMPLEMENTATION
        // Add detailed debugging to verify project ID and check if it's "Standard"
        console.log("[UPLOAD] Creating mock file with project_id:", fileData.project_id, 
                   "type:", typeof fileData.project_id, 
                   "isStandard:", fileData.project_id === "Standard",
                   "isNull:", fileData.project_id === null,
                   "isEmptyString:", fileData.project_id === "");
        
        // Fix for empty string project ID - should be null
        if (fileData.project_id === "") {
          console.log("[UPLOAD] Empty string project_id found - setting to null for 'None' selection");
          fileData.project_id = null;
        }
        // Fix for "Standard" project ID - this should never happen, but just in case
        else if (fileData.project_id === "Standard") {
          console.warn("[UPLOAD] WARNING: 'Standard' found as project_id - this is likely incorrect!");
          // Try to get the stored project ID from localStorage as a fallback
          const storedProjectId = localStorage.getItem('selectedProjectId');
          if (storedProjectId && storedProjectId !== "Standard") {
            console.log("[UPLOAD] Using storedProjectId from localStorage instead:", storedProjectId);
            fileData.project_id = storedProjectId;
          }
        }
        
        // Ensure we explicitly log if this is a global file (no project)
        if (fileData.project_id === null) {
          console.log("[UPLOAD] Creating a global file (no project attachment)");
        }
        
        // Create a mock file response
        const fileExtension = (fileData.file as any).name?.split('.').pop()?.toLowerCase() || 'pdf';
        const mockId = `mock-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
        
        const mockFile: File = {
          id: mockId,
          name: fileData.name || (fileData.file as any).name || 'Unknown file',
          type: fileExtension.toUpperCase(),
          size: (fileData.file as any).size || 1024,
          description: fileData.description || '',
          project_id: fileData.project_id || null, // Uses the exact project ID passed in
          created_at: new Date().toISOString(),
          filepath: '/mock/path/to/file',
          processed: true,
          chunk_count: 10,
          active: true
        };
        
        // Save to both global variable and localStorage for persistence
        console.log("[UPLOAD] Current mockFiles count before adding:", window.mockFiles?.length || 0);
        
        // First, ALWAYS reload from localStorage to make sure we have the most recent data
        let currentFiles: File[] = [];
        try {
          const storedFiles = localStorage.getItem('mockFiles');
          if (storedFiles) {
            currentFiles = JSON.parse(storedFiles);
            console.log("[UPLOAD] Loaded existing files from localStorage:", currentFiles.length);
          }
        } catch (e) {
          console.error("[UPLOAD] Error loading existing files from localStorage:", e);
          // Fall back to window.mockFiles
          currentFiles = window.mockFiles || [];
        }
        
        // Add the new file
        currentFiles.push(mockFile);
        
        // Update both global and localStorage
        window.mockFiles = currentFiles;
        localStorage.setItem('mockFiles', JSON.stringify(currentFiles));
        
        // Direct verification of global variable
        console.log("[UPLOAD] New mockFiles count:", window.mockFiles.length);
        console.log("[UPLOAD] Latest mock file in global array:", 
                   window.mockFiles[window.mockFiles.length - 1]);
        
        console.log("[UPLOAD] Mock file created with ID:", mockId);
        window.localStorage.setItem('lastUploadedFileId', mockId);
        
        // Show alert
        alert(`File ${mockFile.name} has been uploaded (MOCK)`);
        
        // Force a refresh to ensure UI updates
        const refreshEvent = new CustomEvent('mockFileAdded', { detail: mockFile });
        window.dispatchEvent(refreshEvent);
        
        // Simulate network delay
        await new Promise(resolve => setTimeout(resolve, 500));
        
        return mockFile;
      }
    } catch (error) {
      console.error("Error in uploadFile:", error);
      throw error;
    }
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
    try {
      // Attempt real API call first
      const response = await api.delete(`/files/${id}`);
      return response.data;
    } catch (error) {
      console.warn("API endpoint for deletion not available, using mock implementation");
      
      // MOCK IMPLEMENTATION
      console.log(`[DELETE] Deleting mock file with ID: ${id}`);
      
      // Remove from global variable
      if (window.mockFiles) {
        const fileToDelete = window.mockFiles.find(file => file.id === id);
        window.mockFiles = window.mockFiles.filter(file => file.id !== id);
        console.log(`[DELETE] Removed file from global variable. Remaining: ${window.mockFiles.length}`);
        
        if (fileToDelete) {
          console.log(`[DELETE] Deleted file: ${fileToDelete.name}`);
        }
      }
      
      // Also update localStorage for persistence
      localStorage.setItem('mockFiles', JSON.stringify(window.mockFiles || []));
      
      // Force a refresh to ensure UI updates
      const refreshEvent = new CustomEvent('mockFileDeleted', { detail: { id } });
      window.dispatchEvent(refreshEvent);
      
      // Return mock success response
      return { success: true };
    }
  },

  /**
   * Delete multiple files
   */
  bulkDeleteFiles: async (ids: string[]): Promise<FileBulkOperationResult> => {
    try {
      // Attempt real API call first
      const response = await api.post('/files/bulk-delete', { file_ids: ids });
      return response.data;
    } catch (error) {
      console.warn("API endpoint for bulk deletion not available, using mock implementation");
      
      // MOCK IMPLEMENTATION
      const success: string[] = [];
      const failed: { id: string; error: string }[] = [];
      
      // Find and remove each file from localStorage
      const mockFiles: File[] = JSON.parse(localStorage.getItem('mockFiles') || '[]');
      
      for (const id of ids) {
        try {
          // Check if file exists
          const fileExists = mockFiles.some(file => file.id === id);
          
          if (fileExists) {
            // Remove from mock files
            success.push(id);
          } else {
            failed.push({ id, error: 'File not found' });
          }
        } catch (err) {
          failed.push({ id, error: String(err) });
        }
      }
      
      // Update localStorage with remaining files
      const updatedMockFiles = mockFiles.filter(file => !ids.includes(file.id));
      localStorage.setItem('mockFiles', JSON.stringify(updatedMockFiles));
      
      console.log(`Mock bulk delete: ${success.length} files deleted, ${failed.length} failed`);
      
      // Return mock result
      return { success, failed };
    }
  },

  /**
   * Link one or more files to a project
   */
  linkFilesToProject: async (linkRequest: FileLinkRequest): Promise<FileBulkOperationResult> => {
    console.log("Linking files to project:", linkRequest);
    
    try {
      const response = await api.post('/files/link', linkRequest);
      return response.data;
    } catch (error) {
      console.warn("API endpoint for linking not available, using mock implementation");
      
      // MOCK IMPLEMENTATION
      // Update the mock files in localStorage
      const mockFiles: File[] = JSON.parse(localStorage.getItem('mockFiles') || '[]');
      const updatedMockFiles = mockFiles.map(file => {
        if (linkRequest.file_ids.includes(file.id)) {
          console.log(`Linking mock file ${file.id} to project ${linkRequest.project_id}`);
          return {
            ...file,
            project_id: linkRequest.project_id
          };
        }
        return file;
      });
      
      // Save updated files
      localStorage.setItem('mockFiles', JSON.stringify(updatedMockFiles));
      console.log("Mock files after linking:", updatedMockFiles);
      
      // Return mock result
      return {
        success: linkRequest.file_ids,
        failed: []
      };
    }
  },

  /**
   * Unlink one or more files from a project
   */
  unlinkFilesFromProject: async (fileIds: string[], projectId: string): Promise<FileBulkOperationResult> => {
    console.log(`Unlinking files ${fileIds.join(', ')} from project ${projectId}`);
    
    try {
      const response = await api.post('/files/unlink', {
        file_ids: fileIds,
        project_id: projectId,
      });
      
      return response.data;
    } catch (error) {
      console.warn("API endpoint for unlinking not available, using mock implementation");
      
      // MOCK IMPLEMENTATION
      // Update the mock files in localStorage
      const mockFiles: File[] = JSON.parse(localStorage.getItem('mockFiles') || '[]');
      const updatedMockFiles = mockFiles.map(file => {
        if (fileIds.includes(file.id) && file.project_id === projectId) {
          console.log(`Unlinking mock file ${file.id} from project ${projectId}`);
          return {
            ...file,
            project_id: null
          };
        }
        return file;
      });
      
      // Save updated files
      localStorage.setItem('mockFiles', JSON.stringify(updatedMockFiles));
      console.log("Mock files after unlinking:", updatedMockFiles);
      
      // Return mock result
      return {
        success: fileIds,
        failed: []
      };
    }
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
    try {
      const response = await api.get('/files/processing-status');
      return response.data;
    } catch (error) {
      // Return a default object instead of propagating the error
      console.log('[PROCESSING] Processing status endpoint not available, using defaults');
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
    const response = await api.get('/files/tags');
    return response.data;
  },
};

export default fileService;