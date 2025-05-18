import React, { useState, useEffect } from 'react';
import { fileService, projectService } from '../../services';
import { File, FileFilterOptions, FileSortOptions, ProcessingStats, FileSearchResult } from '../../services/fileService';
import { useNavigation } from '../../hooks/useNavigation';

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
  // No props needed since we use the navigation system
};

const MainFileManager: React.FC<MainFileManagerProps> = () => {
  // Use our navigation hook
  const navigation = useNavigation();
  
  // Helper function to handle return to previous view
  const handleReturn = () => {
    if (navigation.activeProjectId) {
      navigation.navigateToView('projectFiles');
    } else {
      navigation.navigateToView('project');
    }
  };
  
  // Helper function to navigate to a project
  const handleSelectProject = (projectId: string) => {
    navigation.navigateToProject(projectId);
  };
  
  // Determine the current project ID
  const projectId = navigation.activeProjectId;
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
    
    // Handler to close project dropdowns when clicking outside
    const handleClickOutside = (event: MouseEvent) => {
      // Close individual file project dropdowns
      const fileDropdowns = document.querySelectorAll('[id^="project-dropdown-"]');
      fileDropdowns.forEach(dropdown => {
        if (!dropdown.contains(event.target as Node) && 
            !(event.target as Element).classList.contains('project-dropdown-toggle')) {
          (dropdown as HTMLElement).classList.add('hidden');
        }
      });
      
      // Close batch project dropdown
      const batchDropdown = document.getElementById('batch-project-dropdown');
      if (batchDropdown && 
          !batchDropdown.contains(event.target as Node) && 
          !(event.target as Element).classList.contains('project-dropdown-toggle')) {
        batchDropdown.classList.add('hidden');
      }
    };
    
    // Add event listeners for our custom events
    window.addEventListener('mockFileAdded', handleFileAdded);
    window.addEventListener('mockFileDeleted', handleFileDeleted);
    document.body.addEventListener('click', handleClickOutside);
    
    // Clean up event listeners when component unmounts
    return () => {
      window.removeEventListener('mockFileAdded', handleFileAdded);
      window.removeEventListener('mockFileDeleted', handleFileDeleted);
      document.body.removeEventListener('click', handleClickOutside);
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
        // Parse sizes correctly for numerical comparison
        const parseSizeToBytes = (sizeStr: string): number => {
          const match = sizeStr.match(/^([\d.]+)\s*([KMGT]?B)$/i);
          if (!match) return 0;
          
          const value = parseFloat(match[1]);
          const unit = match[2].toUpperCase();
          
          switch (unit) {
            case 'B': return value;
            case 'KB': return value * 1024;
            case 'MB': return value * 1024 * 1024;
            case 'GB': return value * 1024 * 1024 * 1024;
            case 'TB': return value * 1024 * 1024 * 1024 * 1024;
            default: return value;
          }
        };
        
        const aBytes = parseSizeToBytes(a.size);
        const bBytes = parseSizeToBytes(b.size);
        
        return sortDirection === 'asc' 
          ? aBytes - bBytes 
          : bBytes - aBytes;
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
    // Update sort state
    let newDirection: 'asc' | 'desc';
    
    if (field === sortField) {
      newDirection = sortDirection === 'asc' ? 'desc' : 'asc';
      setSortDirection(newDirection);
    } else {
      setSortField(field);
      newDirection = 'asc';
      setSortDirection(newDirection);
    }
    
    // Log the change
    console.log(`[MAINFILEMANAGER] Sort changed to ${field} ${newDirection}`);
    
    // Refresh data with new sort
    if (!isSearching) {
      // Only trigger an API refetch if we're not in search mode
      // For searches, we'll just resort the client-side data
      fetchFiles();
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
            onClick={handleReturn}
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
          <div className="flex items-center space-x-1 mr-2">
            <span className="text-xs text-gray-400">Sort by:</span>
          </div>
          <button 
            className={`px-3 py-1 rounded text-sm font-medium border ${sortField === 'name' 
              ? 'bg-gold/20 text-gold border-gold' 
              : 'bg-navy hover:bg-navy-lighter border-transparent'}`}
            onClick={() => handleSortChange('name')}
          >
            Name {sortField === 'name' && (sortDirection === 'asc' ? '↑' : '↓')}
          </button>
          <button 
            className={`px-3 py-1 rounded text-sm font-medium border ${sortField === 'size' 
              ? 'bg-gold/20 text-gold border-gold' 
              : 'bg-navy hover:bg-navy-lighter border-transparent'}`}
            onClick={() => handleSortChange('size')}
          >
            Size {sortField === 'size' && (sortDirection === 'asc' ? '↑' : '↓')}
          </button>
          <button 
            className={`px-3 py-1 rounded text-sm font-medium border ${sortField === 'date' 
              ? 'bg-gold/20 text-gold border-gold' 
              : 'bg-navy hover:bg-navy-lighter border-transparent'}`}
            onClick={() => handleSortChange('date')}
          >
            Date {sortField === 'date' && (sortDirection === 'asc' ? '↑' : '↓')}
          </button>
          <button 
            className={`px-3 py-1 rounded text-sm font-medium border ${sortField === 'status' 
              ? 'bg-gold/20 text-gold border-gold' 
              : 'bg-navy hover:bg-navy-lighter border-transparent'}`}
            onClick={() => handleSortChange('status')}
          >
            Linked {sortField === 'status' && (sortDirection === 'asc' ? '↑' : '↓')}
          </button>
          <button 
            className={`px-3 py-1 rounded text-sm font-medium border ${sortField === 'processed' 
              ? 'bg-gold/20 text-gold border-gold' 
              : 'bg-navy hover:bg-navy-lighter border-transparent'}`}
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
          <div className="flex items-center space-x-2">
            {/* Batch action buttons - only show when files are selected */}
            {selectedFiles.length > 0 && (
              <>
                <span className="text-xs text-gray-400 mr-1">
                  {selectedFiles.length} selected
                </span>
                <button 
                  onClick={async () => {
                    // Implement batch download
                    for (const fileId of selectedFiles) {
                      try {
                        const file = files.find(f => f.id === fileId);
                        if (file) {
                          const blob = await fileService.downloadFile(fileId);
                          const url = window.URL.createObjectURL(blob);
                          const a = document.createElement('a');
                          a.href = url;
                          a.download = file.name;
                          document.body.appendChild(a);
                          a.click();
                          window.URL.revokeObjectURL(url);
                          a.remove();
                        }
                      } catch (err) {
                        console.error(`Error downloading file ${fileId}:`, err);
                      }
                    }
                  }}
                  className="text-xs px-2 py-1 bg-gold/20 hover:bg-gold/30 text-gold rounded"
                >
                  Download Selected
                </button>
                
                <button 
                  onClick={() => {
                    // Show project assignment dropdown for batch assignment
                    const dropdown = document.getElementById('batch-project-dropdown');
                    if (dropdown) {
                      dropdown.classList.toggle('hidden');
                    }
                  }}
                  className="text-xs px-2 py-1 bg-gold/20 hover:bg-gold/30 text-gold rounded project-dropdown-toggle"
                >
                  Assign Selected
                </button>
                
                <button 
                  onClick={async () => {
                    // Implement batch delete with confirmation
                    if (window.confirm(`Are you sure you want to delete ${selectedFiles.length} files? This action cannot be undone.`)) {
                      try {
                        // Delete each file
                        for (const fileId of selectedFiles) {
                          await fileService.deleteFile(fileId);
                        }
                        
                        // Update local state by removing deleted files
                        setFiles(prev => prev.filter(file => !selectedFiles.includes(file.id)));
                        
                        // Clear selection
                        setSelectedFiles([]);
                      } catch (err) {
                        console.error('Error deleting files:', err);
                        setError('Failed to delete some files. Please try again.');
                      }
                    }
                  }}
                  className="text-xs px-2 py-1 bg-red-700/30 hover:bg-red-700/50 text-red-400 rounded"
                >
                  Delete Selected
                </button>
                
                {/* Relative positioned container for dropdown */}
                <div className="relative">
                  {/* Project selection dropdown for batch assignment */}
                  <div 
                    id="batch-project-dropdown"
                    className="absolute right-0 mt-8 bg-navy-light rounded shadow-lg z-10 hidden"
                    style={{ minWidth: '200px' }}
                    onClick={(e) => e.stopPropagation()}
                  >
                    <div className="p-2 border-b border-navy">
                      <div className="text-xs text-gold font-medium mb-1">Assign to Project:</div>
                      {projects.length > 0 ? (
                        <div className="max-h-40 overflow-y-auto">
                          {projects.map(project => (
                            <div 
                              key={project.id} 
                              className="p-1.5 hover:bg-navy rounded text-sm cursor-pointer"
                              onClick={async () => {
                                try {
                                  // Call API to link files to project
                                  await fileService.linkFilesToProject({
                                    file_ids: selectedFiles,
                                    project_id: project.id
                                  });
                                  
                                  // Update local state
                                  setFiles(prev => 
                                    prev.map(file => 
                                      selectedFiles.includes(file.id) 
                                        ? { ...file, projectId: project.id } 
                                        : file
                                    )
                                  );
                                  
                                  // Hide dropdown
                                  const dropdown = document.getElementById('batch-project-dropdown');
                                  if (dropdown) {
                                    dropdown.classList.add('hidden');
                                  }
                                } catch (err) {
                                  console.error('Error assigning files to project:', err);
                                  setError('Failed to assign files to project. Please try again.');
                                }
                              }}
                            >
                              {project.name}
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="text-xs text-gray-400 p-1.5">No projects available</div>
                      )}
                    </div>
                    <div 
                      className="p-2 text-xs hover:bg-red-700/30 text-red-400 rounded cursor-pointer"
                      onClick={async () => {
                        // For each selected file that has a project ID, remove it from that project
                        const filesToProcess = files.filter(
                          file => selectedFiles.includes(file.id) && file.projectId !== null
                        );
                        
                        if (filesToProcess.length > 0 && 
                            window.confirm(`Are you sure you want to remove ${filesToProcess.length} file(s) from their projects?`)) {
                          try {
                            // Group files by project for more efficient unlinking
                            const filesByProject: {[key: string]: string[]} = {};
                            
                            filesToProcess.forEach(file => {
                              if (file.projectId) {
                                if (!filesByProject[file.projectId]) {
                                  filesByProject[file.projectId] = [];
                                }
                                filesByProject[file.projectId].push(file.id);
                              }
                            });
                            
                            // Process each project group
                            for (const [projectId, fileIds] of Object.entries(filesByProject)) {
                              await fileService.unlinkFilesFromProject(fileIds, projectId);
                            }
                            
                            // Update local state
                            setFiles(prev => 
                              prev.map(file => 
                                selectedFiles.includes(file.id) && file.projectId !== null
                                  ? { ...file, projectId: null }
                                  : file
                              )
                            );
                          } catch (err) {
                            console.error('Error removing files from projects:', err);
                            setError('Failed to remove files from projects. Please try again.');
                          }
                        }
                        
                        // Hide dropdown
                        const dropdown = document.getElementById('batch-project-dropdown');
                        if (dropdown) {
                          dropdown.classList.add('hidden');
                        }
                      }}
                    >
                      <span className="text-red-400">Remove from Projects</span>
                    </div>
                  </div>
                </div>
              </>
            )}
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
          </div>
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
                              onClick={() => handleSelectProject(linkedProject.id)}
                            >
                              {linkedProject.name}
                            </button>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  {/* Action buttons */}
                  <div className="flex space-x-2 items-center relative">
                    {/* Show retry processing button for failed files */}
                    {file.processingFailed && (
                      <button 
                        onClick={() => handleRetryProcessing(file.id)}
                        className="text-xs px-2 py-1 bg-gold/20 hover:bg-gold/30 text-gold rounded"
                      >
                        Retry
                      </button>
                    )}
                    
                    <button 
                      onClick={(e) => {
                        e.stopPropagation(); // Prevent clicking from bubbling up to the document
                        // Show project selection dropdown for assignment
                        const dropdown = document.getElementById(`project-dropdown-${file.id}`);
                        if (dropdown) {
                          dropdown.classList.toggle('hidden');
                        }
                      }}
                      className="text-xs px-2 py-1 bg-gold/20 hover:bg-gold/30 text-gold rounded project-dropdown-toggle"
                    >
                      Assign
                    </button>
                    
                    <button 
                      onClick={() => {
                        // Show modify modal for this file
                        // Create a modal if it doesn't exist
                        let modal = document.getElementById(`modify-modal-${file.id}`);
                        if (!modal) {
                          modal = document.createElement('div');
                          modal.id = `modify-modal-${file.id}`;
                          modal.className = 'fixed inset-0 bg-black/50 flex items-center justify-center z-50';
                          modal.innerHTML = `
                            <div class="bg-navy-light rounded-lg p-6 max-w-md w-full">
                              <h3 class="text-lg font-medium text-gold mb-4">Modify File Details</h3>
                              <div class="mb-4">
                                <label class="block text-sm text-gray-400 mb-1">File Name</label>
                                <input type="text" value="${file.name}" 
                                  class="w-full bg-navy p-2 rounded text-gray-300" id="file-name-${file.id}">
                              </div>
                              <div class="mb-4">
                                <label class="block text-sm text-gray-400 mb-1">Description</label>
                                <textarea class="w-full bg-navy p-2 rounded text-gray-300 h-20" 
                                  id="file-description-${file.id}">${file.description || ''}</textarea>
                              </div>
                              <div class="flex justify-end">
                                <button class="px-3 py-1 bg-red-700/30 hover:bg-red-700/50 text-red-400 rounded text-sm mr-2 cancel-btn">
                                  Cancel
                                </button>
                                <button class="px-3 py-1 bg-gold text-navy font-medium rounded hover:bg-gold/90 save-btn">
                                  Save Changes
                                </button>
                              </div>
                            </div>
                          `;
                          
                          document.body.appendChild(modal);
                          
                          // Add event listeners
                          const saveBtn = modal.querySelector('.save-btn');
                          const cancelBtn = modal.querySelector('.cancel-btn');
                          const clickOutside = (e: MouseEvent) => {
                            if (e.target === modal) {
                              if (window.confirm("Are you sure you want to close? Any unsaved changes will be lost.")) {
                                modal?.remove();
                              }
                            }
                          };
                          
                          saveBtn?.addEventListener('click', async () => {
                            try {
                              const nameInput = document.getElementById(`file-name-${file.id}`) as HTMLInputElement;
                              const descInput = document.getElementById(`file-description-${file.id}`) as HTMLTextAreaElement;
                              
                              if (nameInput && descInput) {
                                // Call API to update file
                                await fileService.updateFile(file.id, {
                                  name: nameInput.value,
                                  description: descInput.value
                                });
                                
                                // Update local state
                                setFiles(prev => 
                                  prev.map(f => 
                                    f.id === file.id 
                                      ? { ...f, name: nameInput.value, description: descInput.value } 
                                      : f
                                  )
                                );
                              }
                              
                              // Remove modal
                              modal?.remove();
                            } catch (err) {
                              console.error('Error updating file:', err);
                              setError('Failed to update file. Please try again.');
                            }
                          });
                          
                          cancelBtn?.addEventListener('click', () => {
                            if (window.confirm("Are you sure you want to cancel? Any unsaved changes will be lost.")) {
                              modal?.remove();
                            }
                          });
                          
                          modal.addEventListener('click', clickOutside);
                        } else {
                          // If modal exists, just show it
                          modal.classList.remove('hidden');
                        }
                      }}
                      className="text-xs px-2 py-1 bg-gold/20 hover:bg-gold/30 text-gold rounded"
                    >
                      Modify
                    </button>
                    <div 
                      id={`project-dropdown-${file.id}`}
                      className="absolute mt-8 bg-navy-light rounded shadow-lg z-10 hidden"
                      style={{ minWidth: '180px' }}
                      onClick={(e) => e.stopPropagation()} // Prevent dropdown clicks from closing itself
                    >
                      <div className="p-2 border-b border-navy">
                        <div className="text-xs text-gold font-medium mb-1">Assign to Project:</div>
                        {projects.length > 0 ? (
                          <div className="max-h-40 overflow-y-auto">
                            {projects.map(project => (
                              <div 
                                key={project.id} 
                                className="p-1.5 hover:bg-navy rounded text-sm cursor-pointer"
                                onClick={async () => {
                                  try {
                                    // Call API to link file to project
                                    await fileService.linkFilesToProject({
                                      file_ids: [file.id],
                                      project_id: project.id
                                    });
                                    
                                    // Update local state
                                    setFiles(prev => 
                                      prev.map(f => 
                                        f.id === file.id 
                                          ? { ...f, projectId: project.id } 
                                          : f
                                      )
                                    );
                                    
                                    // Hide dropdown
                                    const dropdown = document.getElementById(`project-dropdown-${file.id}`);
                                    if (dropdown) {
                                      dropdown.classList.add('hidden');
                                    }
                                  } catch (err) {
                                    console.error('Error assigning file to project:', err);
                                    setError('Failed to assign file to project. Please try again.');
                                  }
                                }}
                              >
                                {project.name}
                              </div>
                            ))}
                          </div>
                        ) : (
                          <div className="text-xs text-gray-400 p-1.5">No projects available</div>
                        )}
                      </div>
                      <div 
                        className="p-2 text-xs hover:bg-red-700/30 text-red-400 rounded cursor-pointer"
                        onClick={async () => {
                          // Only attempt to unlink if currently attached to a project
                          if (file.projectId && window.confirm(`Are you sure you want to remove "${file.name}" from its project?`)) {
                            try {
                              // Call API to unlink file
                              await fileService.unlinkFilesFromProject([file.id], file.projectId);
                              
                              // Update local state
                              setFiles(prev => 
                                prev.map(f => 
                                  f.id === file.id 
                                    ? { ...f, projectId: null } 
                                    : f
                                )
                              );
                            } catch (err) {
                              console.error('Error removing file from project:', err);
                              setError('Failed to remove file from project. Please try again.');
                            }
                          }
                          
                          // Hide dropdown
                          const dropdown = document.getElementById(`project-dropdown-${file.id}`);
                          if (dropdown) {
                            dropdown.classList.add('hidden');
                          }
                        }}
                      >
                        <span className={file.projectId ? "text-red-400" : "text-gray-500"}>
                          {file.projectId ? "Remove from Project" : "Not Assigned"}
                        </span>
                      </div>
                    </div>
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
                      className="text-xs px-2 py-1 bg-gold/20 hover:bg-gold/30 text-gold rounded"
                    >
                      Download
                    </button>
                    <button 
                      className="text-xs px-2 py-1 bg-red-700/30 hover:bg-red-700/50 text-red-400 rounded"
                      onClick={() => {
                        if (window.confirm(`Are you sure you want to delete "${file.name}"? This action cannot be undone.`)) {
                          handleDeleteFile(file.id);
                        }
                      }}
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