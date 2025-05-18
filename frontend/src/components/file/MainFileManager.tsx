import React, { useState, useEffect } from 'react';
import { fileService, projectService } from '../../services';
import { File, FileFilterOptions, FileSortOptions, ProcessingStats, FileSearchResult } from '../../services/fileService';

// Local interface for mapped files from API response
interface LocalFile {
  id: string;
  name: string;
  type: string;
  size: string;
  active: boolean;
  projectId: string | null; // null for unattached documents
  addedAt: string;
  processed: boolean; // Indicates if the file has been processed into vector DB
  processingFailed?: boolean; // If processing failed
  chunks?: number; // Number of chunks if processed
  description?: string;
  relevance?: number; // For search results
}

// Define types for projects
interface Project {
  id: string;
  name: string;
}

// Get file type badge color
const getFileTypeColor = (type: string): string => {
  switch (type.toLowerCase()) {
    case 'pdf':
      return 'red';
    case 'docx':
    case 'doc':
      return 'blue';
    case 'xlsx':
    case 'xls':
      return 'green';
    case 'png':
    case 'jpg':
    case 'jpeg':
      return 'purple';
    case 'txt':
      return 'gray';
    default:
      return 'gray';
  }
};

// Helper to format bytes to human-readable size
const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return bytes + ' B';
  const units = ['KB', 'MB', 'GB', 'TB'];
  let size = bytes / 1024;
  let unitIndex = 0;
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }
  
  return size.toFixed(1) + ' ' + units[unitIndex];
};

// Map API File to LocalFile format
const mapApiFileToLocal = (apiFile: File): LocalFile => ({
  id: apiFile.id,
  name: apiFile.name,
  type: apiFile.type.toUpperCase(),
  size: formatFileSize(apiFile.size),
  active: apiFile.active,
  projectId: apiFile.project_id,
  addedAt: apiFile.created_at.split('T')[0], // Format date
  processed: apiFile.processed,
  processingFailed: apiFile.processing_failed,
  chunks: apiFile.chunk_count,
  description: apiFile.description,
  // Add relevance if this is a search result
  relevance: (apiFile as any).relevance
});

type MainFileManagerProps = {
  onReturn: () => void; // Function to return to previous view
  onSelectProject?: (projectId: string) => void; // Function to navigate to a project
  projectId?: string | null; // Current project ID if coming from a project
};

const MainFileManager: React.FC<MainFileManagerProps> = ({ 
  onReturn, 
  onSelectProject,
  projectId 
}) => {
  // Files state
  const [files, setFiles] = useState<LocalFile[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Project state
  const [projects, setProjects] = useState<Project[]>([]);
  
  // UI state
  const [searchTerm, setSearchTerm] = useState('');
  const [sortField, setSortField] = useState<'name' | 'date' | 'size' | 'status' | 'processed'>('date');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');
  const [showAddTagModal, setShowAddTagModal] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);
  const [searchResults, setSearchResults] = useState<LocalFile[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [droppedFiles, setDroppedFiles] = useState<File[]>([]);
  
  // Processing state
  const [processingStats, setProcessingStats] = useState<ProcessingStats | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  // Function to fetch files based on current filters
  const fetchFiles = async () => {
    setIsLoading(true);
    setError(null);
    
    // Set up API filters
    const filterOptions: FileFilterOptions = {};
    if (projectId !== undefined) {
      filterOptions.project_id = projectId;
    }
    
    // Set up API sort
    const sortOptions: FileSortOptions = {
      field: sortField === 'date' ? 'created_at' : 
             sortField === 'status' ? 'project_id' : sortField,
      direction: sortDirection
    };
    
    try {
      console.log("[MAINFILEMANAGER] Fetching files with options:", { filterOptions, sortOptions });
      
      // Force reload window.mockFiles from localStorage to ensure we have the latest data
      try {
        const storedFiles = localStorage.getItem('mockFiles');
        if (storedFiles) {
          window.mockFiles = JSON.parse(storedFiles);
          console.log("[MAINFILEMANAGER] Refreshed mockFiles from localStorage:", window.mockFiles.length);
        }
      } catch (e) {
        console.error('[MAINFILEMANAGER] Error refreshing mockFiles from localStorage', e);
      }
      
      // Fetch files
      const apiFiles = await fileService.getAllFiles(filterOptions, sortOptions);
      console.log("[MAINFILEMANAGER] Received", apiFiles.length, "files from API/mock");
      
      const localFiles = apiFiles.map(mapApiFileToLocal);
      console.log("[MAINFILEMANAGER] Mapped files:", localFiles.length);
      
      setFiles(localFiles);
      
      // Debug output for global mock files
      console.log("[MAINFILEMANAGER] Current global mock files:", window.mockFiles?.length || 0, "files");
      
      return true;
    } catch (err) {
      console.error('[MAINFILEMANAGER] Error fetching files:', err);
      setError('Failed to load files. Please try again.');
      return false;
    } finally {
      setIsLoading(false);
    }
  };
  
  // Function to refresh additional data (projects, processing stats)
  const fetchAdditionalData = async () => {
    try {
      // Fetch projects for linking info
      const projectsData = await projectService.getAllProjects();
      setProjects(projectsData);
      console.log("[MAINFILEMANAGER] Loaded projects:", projectsData);
      
      // Try to fetch processing stats once (may not be available)
      try {
        const stats = await fileService.getProcessingStatus();
        setProcessingStats(stats);
      } catch (err) {
        console.log('[MAINFILEMANAGER] Processing status endpoint not available - skipping');
      }
    } catch (err) {
      console.error('[MAINFILEMANAGER] Error fetching additional data:', err);
    }
  };
  
  // Function to handle after a file is uploaded
  const handleUploadSuccess = async () => {
    console.log("[MAINFILEMANAGER] Manually refreshing files after upload");
    await fetchFiles();
  };
  
  // Effect to load all files and projects on component mount and when filters change
  useEffect(() => {
    // Load initial data
    const loadInitialData = async () => {
      await fetchFiles();
      await fetchAdditionalData();
    };
    
    loadInitialData();
    
    // Define event handlers for our custom events
    const handleFileAdded = async () => {
      console.log("[MAINFILEMANAGER] File added event detected, refreshing file list");
      await fetchFiles();
    };
    
    const handleFileDeleted = async () => {
      console.log("[MAINFILEMANAGER] File deleted event detected, refreshing file list");
      await fetchFiles();
    };
    
    // Add event listeners for our custom events
    window.addEventListener('mockFileAdded', handleFileAdded);
    window.addEventListener('mockFileDeleted', handleFileDeleted);
    
    // Clean up event listeners when component unmounts
    return () => {
      window.removeEventListener('mockFileAdded', handleFileAdded);
      window.removeEventListener('mockFileDeleted', handleFileDeleted);
    };
  }, [projectId, sortField, sortDirection]); // Dependencies trigger re-fetch when they change

  // Handle search
  const handleSearch = async () => {
    if (!searchTerm.trim()) {
      setIsSearching(false);
      setSearchResults([]);
      return;
    }
    
    setIsSearching(true);
    setIsLoading(true);
    
    try {
      // Build search request
      const searchRequest = {
        query: searchTerm,
        project_id: projectId,
        include_content: true
      };
      
      // Call API for search
      const results = await fileService.searchFileContents(searchRequest);
      setSearchResults(results.map(mapApiFileToLocal));
    } catch (err) {
      console.error('Error searching files:', err);
      setError('Search failed. Please try again.');
      // Fall back to local search if API fails
      const results = files
        .filter(file => 
          file.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
          (file.description && file.description.toLowerCase().includes(searchTerm.toLowerCase()))
        )
        .map(file => ({
          ...file,
          relevance: 70 // Default relevance for local search
        }));
      
      setSearchResults(results);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle file selection for bulk operations
  const toggleFileSelection = (fileId: string) => {
    setSelectedFiles(prev => 
      prev.includes(fileId) 
        ? prev.filter(id => id !== fileId) 
        : [...prev, fileId]
    );
  };

  // Handle attaching selected files to current project
  const handleAttachToProject = async () => {
    if (!projectId || selectedFiles.length === 0) return;
    
    try {
      // Call API to link files
      await fileService.linkFilesToProject({
        file_ids: selectedFiles,
        project_id: projectId
      });
      
      // Update local state
      setFiles(prev => 
        prev.map(file => 
          selectedFiles.includes(file.id) 
            ? { ...file, projectId } 
            : file
        )
      );
      
      // Clear selection
      setSelectedFiles([]);
    } catch (err) {
      console.error('Error attaching files to project:', err);
      setError('Failed to attach files to project. Please try again.');
    }
  };

  // Handle retry processing for failed files
  const handleRetryProcessing = async (fileId: string) => {
    try {
      // Update local state to show processing starting
      setFiles(prev => 
        prev.map(file => 
          file.id === fileId 
            ? { ...file, processed: false, processingFailed: false } 
            : file
        )
      );
      
      // Call API to retry processing
      const updatedFile = await fileService.retryProcessing(fileId);
      
      // Update file in local state
      setFiles(prev => 
        prev.map(file => 
          file.id === fileId 
            ? mapApiFileToLocal(updatedFile)
            : file
        )
      );
    } catch (err) {
      console.error('Error retrying file processing:', err);
      setError('Failed to retry processing. Please try again.');
      
      // Reset file to failed state
      setFiles(prev => 
        prev.map(file => 
          file.id === fileId 
            ? { ...file, processed: false, processingFailed: true } 
            : file
        )
      );
    }
  };

  // Handle file deletion
  const handleDeleteFile = async (fileId: string) => {
    try {
      // Call API to delete file
      await fileService.deleteFile(fileId);
      
      // Update local state
      setFiles(prev => prev.filter(file => file.id !== fileId));
      setSelectedFiles(prev => prev.filter(id => id !== fileId));
    } catch (err) {
      console.error('Error deleting file:', err);
      setError('Failed to delete file. Please try again.');
    }
  };

  // Sort files based on current sort field and direction
  const getSortedFiles = () => {
    let filesToSort = isSearching ? searchResults : files;
    
    return [...filesToSort].sort((a, b) => {
      if (sortField === 'name') {
        return sortDirection === 'asc' 
          ? a.name.localeCompare(b.name) 
          : b.name.localeCompare(a.name);
      } else if (sortField === 'date') {
        return sortDirection === 'asc' 
          ? a.addedAt.localeCompare(b.addedAt) 
          : b.addedAt.localeCompare(a.addedAt);
      } else if (sortField === 'size') {
        // Simple implementation - in reality would parse the size properly
        return sortDirection === 'asc' 
          ? a.size.localeCompare(b.size) 
          : b.size.localeCompare(a.size);
      } else if (sortField === 'status') {
        // Sort by projectId (linked status)
        if (sortDirection === 'asc') {
          return (a.projectId === null) === (b.projectId === null) 
            ? 0 
            : a.projectId === null ? 1 : -1;
        } else {
          return (a.projectId === null) === (b.projectId === null) 
            ? 0 
            : a.projectId === null ? -1 : 1;
        }
      } else if (sortField === 'processed') {
        // Sort by processed status
        if (sortDirection === 'asc') {
          return a.processed === b.processed ? 0 : a.processed ? 1 : -1;
        } else {
          return a.processed === b.processed ? 0 : a.processed ? -1 : 1;
        }
      }
      return 0;
    });
  };

  // Handle sort field change
  const handleSortChange = (field: 'name' | 'date' | 'size' | 'status' | 'processed') => {
    if (field === sortField) {
      setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="bg-navy-light p-4 mb-4 rounded-lg flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-gold">Main File Manager</h2>
          <p className="text-gray-400 text-sm">Manage all system files</p>
        </div>
        <div className="flex space-x-2">
          <button 
            onClick={onReturn}
            className="px-3 py-1 bg-navy hover:bg-navy-lighter rounded text-sm"
          >
            Return
          </button>
        </div>
      </div>
      
      {/* File Upload Area */}
      <div className="bg-navy-light p-4 mb-4 rounded-lg">
        <div 
          className="border-2 border-dashed border-navy-lighter rounded-lg p-6 text-center"
          onDragOver={(e) => {
            e.preventDefault();
            e.stopPropagation();
            e.currentTarget.classList.add('border-gold');
          }}
          onDragLeave={(e) => {
            e.preventDefault();
            e.stopPropagation();
            e.currentTarget.classList.remove('border-gold');
          }}
          onDrop={(e) => {
            e.preventDefault();
            e.stopPropagation();
            e.currentTarget.classList.remove('border-gold');
            
            // Get dropped files
            if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
              // Handle file upload with the files
              const filesToUpload = Array.from(e.dataTransfer.files);
              console.log('Files dropped:', filesToUpload);
              
              // Store files in state
              setDroppedFiles(filesToUpload);
              
              // Open tagging modal with the dropped files
              setShowAddTagModal(true);
            }
          }}
        >
          <div className="mb-4">
            <div className="mx-auto w-12 h-12 bg-navy-lighter rounded-full flex items-center justify-center">
              <span className="text-gold text-2xl">+</span>
            </div>
          </div>
          <p className="text-gray-400 mb-2">Drag and drop files here</p>
          <p className="text-gray-500 text-sm mb-4">or</p>
          <button 
            className="px-4 py-2 bg-gold text-navy font-medium rounded hover:bg-gold/90"
            onClick={() => setShowAddTagModal(true)}
            disabled={isUploading}
          >
            {isUploading ? 'Uploading...' : 'Browse Files'}
          </button>
        </div>
      </div>
      
      {/* Processing Stats Indicator - Only show if endpoint is working */}
      {processingStats && Object.keys(processingStats).length > 0 && (
        <div className="bg-navy-light p-4 mb-4 rounded-lg">
          <div className="flex flex-col space-y-3">
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Processing Status:</span>
              <span className="text-gold">
                {processingStats.processing_files ?? 0} processing, 
                {processingStats.processed_files ?? 0} complete, 
                {processingStats.failed_files ?? 0} failed
              </span>
            </div>
            
            {processingStats.gpu_usage !== undefined && (
              <div className="flex items-center">
                <div className="mr-3 text-gray-400">GPU Usage:</div>
                <div className="flex-1 bg-navy rounded-full h-2.5">
                  <div 
                    className="bg-gold h-2.5 rounded-full" 
                    style={{ width: `${processingStats.gpu_usage}%` }}
                  ></div>
                </div>
                <div className="ml-3 text-gold">{processingStats.gpu_usage}%</div>
              </div>
            )}
            
            {processingStats.eta !== undefined && processingStats.eta > 0 && (
              <div className="text-sm text-gray-400">
                Estimated time remaining: {Math.ceil(processingStats.eta / 60)} minutes
              </div>
            )}
          </div>
        </div>
      )}
      
      {/* Search and Controls */}
      <div className="bg-navy-light p-4 mb-4 rounded-lg flex flex-wrap gap-2 justify-between items-center">
        <div className="flex space-x-2 items-center">
          <input
            type="text"
            placeholder="Search files..."
            className="bg-navy p-2 rounded focus:outline-none focus:ring-1 focus:ring-gold"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button 
            className="p-2 bg-navy hover:bg-navy-lighter rounded"
            onClick={handleSearch}
          >
            <span className="text-gold">🔍</span>
          </button>
        </div>
        
        <div className="flex space-x-3">
          {/* Sort Controls */}
          <button 
            className={`px-3 py-1 rounded text-sm ${sortField === 'name' ? 'bg-gold/20 text-gold' : 'bg-navy hover:bg-navy-lighter'}`}
            onClick={() => handleSortChange('name')}
          >
            Name {sortField === 'name' && (sortDirection === 'asc' ? '↑' : '↓')}
          </button>
          <button 
            className={`px-3 py-1 rounded text-sm ${sortField === 'size' ? 'bg-gold/20 text-gold' : 'bg-navy hover:bg-navy-lighter'}`}
            onClick={() => handleSortChange('size')}
          >
            Size {sortField === 'size' && (sortDirection === 'asc' ? '↑' : '↓')}
          </button>
          <button 
            className={`px-3 py-1 rounded text-sm ${sortField === 'date' ? 'bg-gold/20 text-gold' : 'bg-navy hover:bg-navy-lighter'}`}
            onClick={() => handleSortChange('date')}
          >
            Date {sortField === 'date' && (sortDirection === 'asc' ? '↑' : '↓')}
          </button>
          <button 
            className={`px-3 py-1 rounded text-sm ${sortField === 'status' ? 'bg-gold/20 text-gold' : 'bg-navy hover:bg-navy-lighter'}`}
            onClick={() => handleSortChange('status')}
          >
            Linked {sortField === 'status' && (sortDirection === 'asc' ? '↑' : '↓')}
          </button>
          <button 
            className={`px-3 py-1 rounded text-sm ${sortField === 'processed' ? 'bg-gold/20 text-gold' : 'bg-navy hover:bg-navy-lighter'}`}
            onClick={() => handleSortChange('processed')}
          >
            Processed {sortField === 'processed' && (sortDirection === 'asc' ? '↑' : '↓')}
          </button>
        </div>
        
        {selectedFiles.length > 0 && projectId && (
          <button 
            onClick={handleAttachToProject}
            className="px-3 py-1 bg-gold/20 hover:bg-gold/30 text-gold rounded text-sm"
          >
            Attach Selected ({selectedFiles.length})
          </button>
        )}
      </div>
      
      {/* Files List */}
      <div className="flex-1 bg-navy-light p-4 rounded-lg overflow-y-auto">
        <h3 className="text-lg font-medium text-gold mb-3 pb-2 border-b border-navy flex justify-between items-center">
          <span>
            {isSearching ? 'Search Results' : 'All Files'} 
            {isSearching && ` (${searchResults.length})`}
          </span>
          {isSearching && (
            <button 
              onClick={() => {
                setIsSearching(false);
                setSearchTerm('');
              }}
              className="text-xs px-2 py-1 bg-navy hover:bg-navy-lighter rounded"
            >
              Clear Search
            </button>
          )}
        </h3>
        
        {isLoading ? (
          <div className="p-6 text-center">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-gold border-r-transparent align-[-0.125em]" role="status">
              <span className="!absolute !-m-px !h-px !w-px !overflow-hidden !whitespace-nowrap !border-0 !p-0 ![clip:rect(0,0,0,0)]">Loading...</span>
            </div>
            <div className="mt-2 text-gray-400">Loading files...</div>
          </div>
        ) : error ? (
          <div className="p-6 text-center text-red-400">
            <div className="text-lg mb-2">⚠️</div>
            <div>{error}</div>
            <button 
              onClick={() => window.location.reload()}
              className="mt-4 px-4 py-2 bg-navy hover:bg-navy-lighter rounded text-sm"
            >
              Retry
            </button>
          </div>
        ) : getSortedFiles().length > 0 ? (
          <div className="space-y-2">
            {getSortedFiles().map(file => {
              const isLinked = file.projectId !== null;
              const linkedProject = isLinked && projects.find(p => p.id === file.projectId);
              
              return (
                <div key={file.id} className="p-3 bg-navy hover:bg-navy-lighter rounded-lg flex items-center justify-between">
                  <div className="flex items-center">
                    {/* Checkbox for selection */}
                    <div className="mr-3">
                      <input
                        type="checkbox"
                        checked={selectedFiles.includes(file.id)}
                        onChange={() => toggleFileSelection(file.id)}
                        className="w-4 h-4 accent-gold bg-navy border-gold/30 rounded focus:ring-gold"
                      />
                    </div>
                    
                    {/* File type icon */}
                    <div className={`w-10 h-10 bg-${getFileTypeColor(file.type)}-500/20 rounded flex items-center justify-center mr-3`}>
                      <span className={`text-${getFileTypeColor(file.type)}-400 text-xs`}>{file.type}</span>
                    </div>
                    
                    {/* File info */}
                    <div>
                      <h4 className="font-medium flex items-center">
                        {file.name}
                        {/* Search relevance if available */}
                        {file.relevance !== undefined && (
                          <span className="ml-2 text-xs px-1.5 py-0.5 bg-gold/20 text-gold rounded">
                            {file.relevance}%
                          </span>
                        )}
                      </h4>
                      <div className="flex text-xs text-gray-400 space-x-2 flex-wrap">
                        <span>Added {file.addedAt}</span>
                        <span>•</span>
                        <span>{file.size}</span>
                        
                        {/* Processing status */}
                        {file.processed ? (
                          <>
                            <span>•</span>
                            <span className="text-green-400">Processed</span>
                            {file.chunks && (
                              <>
                                <span>•</span>
                                <span>{file.chunks} chunks</span>
                              </>
                            )}
                          </>
                        ) : file.processingFailed ? (
                          <>
                            <span>•</span>
                            <span className="text-red-400">Processing Failed</span>
                          </>
                        ) : (
                          <>
                            <span>•</span>
                            <span className="text-yellow-400">Processing...</span>
                          </>
                        )}
                        
                        {/* Linked status */}
                        <span>•</span>
                        <span className={isLinked ? "text-blue-400" : "text-gray-500"}>
                          {isLinked ? "Linked" : "Unlinked"}
                        </span>
                        
                        {/* Linked project */}
                        {isLinked && linkedProject && (
                          <>
                            <span>•</span>
                            <button 
                              className="text-blue-400 hover:underline"
                              onClick={() => onSelectProject && onSelectProject(linkedProject.id)}
                            >
                              {linkedProject.name}
                            </button>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  {/* Action buttons */}
                  <div className="flex space-x-2 items-center">
                    {/* Show retry processing button for failed files */}
                    {file.processingFailed && (
                      <button 
                        onClick={() => handleRetryProcessing(file.id)}
                        className="text-xs px-2 py-1 bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 rounded"
                      >
                        Retry
                      </button>
                    )}
                    
                    <button 
                      onClick={() => window.open(`/api/files/${file.id}/preview`, '_blank')}
                      className="text-xs px-2 py-1 bg-navy-light hover:bg-navy rounded"
                    >
                      View
                    </button>
                    <button 
                      onClick={async () => {
                        try {
                          const blob = await fileService.downloadFile(file.id);
                          const url = window.URL.createObjectURL(blob);
                          const a = document.createElement('a');
                          a.href = url;
                          a.download = file.name;
                          document.body.appendChild(a);
                          a.click();
                          window.URL.revokeObjectURL(url);
                          a.remove();
                        } catch (err) {
                          console.error('Error downloading file:', err);
                          setError('Failed to download file. Please try again.');
                        }
                      }}
                      className="text-xs px-2 py-1 bg-navy-light hover:bg-navy rounded"
                    >
                      Download
                    </button>
                    <button 
                      className="text-xs px-2 py-1 bg-red-700/30 hover:bg-red-700/50 text-red-400 rounded"
                      onClick={() => handleDeleteFile(file.id)}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="p-3 text-center text-gray-400">
            {isSearching ? 'No files match your search criteria.' : 'No files have been added yet.'}
          </div>
        )}
      </div>
      
      {/* File Upload Modal with tagging */}
      {showAddTagModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-navy-light rounded-lg p-6 max-w-md w-full">
            <h3 className="text-lg font-medium text-gold mb-4">Upload and Tag Files</h3>
            
            <div className="mb-4">
              <label className="block text-sm text-gray-400 mb-1">Files</label>
              {droppedFiles.length > 0 ? (
                <div className="w-full bg-navy p-2 rounded text-gray-300">
                  <div className="text-sm text-gold mb-2">Dropped files:</div>
                  <ul className="max-h-24 overflow-y-auto">
                    {droppedFiles.map((file, index) => (
                      <li key={index} className="text-sm text-gray-300 mb-1">
                        {file.name} ({(file.size / 1024).toFixed(1)} KB)
                      </li>
                    ))}
                  </ul>
                </div>
              ) : (
                <input 
                  type="file" 
                  multiple
                  className="w-full bg-navy p-2 rounded text-gray-300"
                  onChange={(e) => {
                    if (e.target.files && e.target.files.length > 0) {
                      setDroppedFiles(Array.from(e.target.files));
                    }
                  }}
                />
              )}
            </div>
            
            <div className="mb-4">
              <label className="block text-sm text-gray-400 mb-1">Description</label>
              <textarea 
                className="w-full bg-navy p-2 rounded text-gray-300 h-20"
                placeholder="Add a description for these files..."
              />
            </div>
            
            <div className="mb-4">
              <label className="block text-sm text-gray-400 mb-1">Link to Project (Optional)</label>
              <select 
                className="w-full bg-navy p-2 rounded text-gray-300"
                defaultValue={projectId || ""}
                onChange={(e) => {
                  console.log("Selected project ID changed to:", e.target.value);
                  const selectedProjectId = e.target.value || undefined;
                  
                  // Store the selected project ID for later use
                  window.localStorage.setItem('selectedProjectId', selectedProjectId || '');
                }}
              >
                <option value="">None (Keep in Global Knowledge)</option>
                {projects.length > 0 ? 
                  projects.map(project => (
                    <option 
                      key={project.id} 
                      value={project.id}
                    >
                      {project.name}
                    </option>
                  ))
                  : 
                  <option value="" disabled>Loading projects...</option>
                }
              </select>
              <div className="text-xs text-gray-500 mt-1">Available projects: {projects.length} {projects.length > 0 ? `(${projects.map(p => p.name).join(', ')})` : ''}</div>
            </div>
            
            
            <div className="flex justify-end">
              <button 
                onClick={() => {
                  setShowAddTagModal(false);
                  setDroppedFiles([]);
                }}
                className="px-3 py-1 bg-navy hover:bg-navy-lighter rounded text-sm mr-2"
              >
                Cancel
              </button>
              <button 
                onClick={async () => {
                  console.log("Upload button clicked");
                  try {
                    // Get the description and project
                    const descriptionInput = document.querySelector('textarea') as HTMLTextAreaElement;
                    const projectSelect = document.querySelector('select') as HTMLSelectElement;
                    
                    // Determine which files to use - either dropped files or from file input
                    let filesToProcess: File[] = [];
                    
                    if (droppedFiles.length > 0) {
                      // Use dropped files
                      filesToProcess = droppedFiles;
                    } else {
                      // Check for files from input
                      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
                      if (fileInput?.files?.length) {
                        filesToProcess = Array.from(fileInput.files);
                      }
                    }
                    
                    console.log("Files to process:", filesToProcess);
                    
                    if (filesToProcess.length > 0) {
                      setShowAddTagModal(false);
                      setIsUploading(true);
                      
                      // Process each file
                      for (let i = 0; i < filesToProcess.length; i++) {
                        const file = filesToProcess[i];
                        // Get the selected project ID from the dropdown
                        const selectedProjectId = projectSelect?.value;
                        
                        // Handle empty selection ("None")
                        if (selectedProjectId === "") {
                          console.log("None (Keep in Global Knowledge) selected - setting project_id to null");
                          // Use null specifically for "None" selection
                          var finalProjectId = null;
                        }
                        // Important: Check if selectedProjectId is "Standard" and replace with actual projectId
                        else if (selectedProjectId === "Standard") {
                          console.log("Replacing 'Standard' with actual project ID:", projectId);
                          var finalProjectId = projectId;
                        } else {
                          const storedProjectId = window.localStorage.getItem('selectedProjectId');
                          var finalProjectId = selectedProjectId || storedProjectId || projectId || undefined;
                        }
                        
                        console.log("File upload details:", {
                          filename: file.name,
                          dropdown_project_id: selectedProjectId,
                          current_prop_projectId: projectId,
                          localStorage_project_id: window.localStorage.getItem('selectedProjectId'),
                          final_project_id: finalProjectId
                        });
                        
                        const uploadRequest = {
                          file,
                          name: file.name,
                          description: descriptionInput?.value || '',
                          project_id: finalProjectId || undefined
                        };
                        
                        try {
                          // Try to upload the file
                          await fileService.uploadFile(uploadRequest);
                          console.log(`Successfully uploaded file: ${file.name} with project_id: ${finalProjectId || 'null'}`);
                        } catch (uploadError) {
                          console.error(`Error uploading file ${file.name}:`, uploadError);
                          // If the API endpoint doesn't exist yet, show a mock success message
                          alert(`Mock upload: File ${file.name} uploaded successfully (API endpoint not available)`);
                        }
                      }
                      
                      // Clear dropped files first
                      setDroppedFiles([]);
                      
                      console.log("[MAINFILEMANAGER] Upload complete");
                      
                      // Check global mock files after upload
                      console.log(`[MAINFILEMANAGER] Mock files in global variable after upload: ${window.mockFiles?.length || 0}`);
                      
                      // Reset UI state
                      setShowAddTagModal(false); 
                      setIsUploading(false);
                      
                      // Manually trigger a refresh of the file list after upload
                      await handleUploadSuccess();
                    }
                  } catch (err) {
                    console.error('Error uploading files:', err);
                    setError('Failed to upload files. Please try again.');
                    setIsUploading(false);
                  }
                }}
                className="px-3 py-1 bg-gold text-navy font-medium rounded hover:bg-gold/90"
                disabled={isUploading || (droppedFiles.length === 0 && !document.querySelector('input[type="file"]')?.files?.length)}
              >
                {isUploading ? 'Uploading...' : 'Upload & Process Files'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MainFileManager;