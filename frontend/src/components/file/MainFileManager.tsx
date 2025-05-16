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
  
  // Processing state
  const [processingStats, setProcessingStats] = useState<ProcessingStats | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  // Effect to load all files and processing stats
  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
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
        
        // Fetch files
        const apiFiles = await fileService.getAllFiles(filterOptions, sortOptions);
        const localFiles = apiFiles.map(mapApiFileToLocal);
        setFiles(localFiles);
        
        // Fetch processing stats
        const stats = await fileService.getProcessingStatus();
        setProcessingStats(stats);
        
        // Fetch projects for linking info
        const projectsData = await projectService.getAllProjects();
        setProjects(projectsData);
      } catch (err) {
        console.error('Error fetching files:', err);
        setError('Failed to load files. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchData();
    
    // Set up polling for processing stats
    const statsInterval = setInterval(async () => {
      try {
        const stats = await fileService.getProcessingStatus();
        setProcessingStats(stats);
      } catch (err) {
        console.error('Error fetching processing stats:', err);
      }
    }, 5000); // Poll every 5 seconds
    
    return () => clearInterval(statsInterval);
  }, [projectId, sortField, sortDirection]);

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
        <div className="border-2 border-dashed border-navy-lighter rounded-lg p-6 text-center">
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
      
      {/* Processing Stats Indicator */}
      {processingStats && (
        <div className="bg-navy-light p-4 mb-4 rounded-lg">
          <div className="flex flex-col space-y-3">
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Processing Status:</span>
              <span className="text-gold">
                {processingStats.processing_files} processing, 
                {processingStats.processed_files} complete, 
                {processingStats.failed_files} failed
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
              <input 
                type="file" 
                multiple
                className="w-full bg-navy p-2 rounded text-gray-300"
                onChange={(e) => {
                  // In a real implementation, we'd capture these files for upload
                  console.log('Selected files:', e.target.files);
                }}
              />
            </div>
            
            <div className="mb-4">
              <label className="block text-sm text-gray-400 mb-1">Description</label>
              <textarea 
                className="w-full bg-navy p-2 rounded text-gray-300 h-20"
                placeholder="Add a description for these files..."
              />
            </div>
            
            {projectId ? (
              <div className="mb-4 px-3 py-2 bg-navy rounded">
                <div className="text-sm text-gray-400">Files will be linked to current project</div>
              </div>
            ) : (
              <div className="mb-4">
                <label className="block text-sm text-gray-400 mb-1">Link to Project (Optional)</label>
                <select className="w-full bg-navy p-2 rounded text-gray-300">
                  <option value="">No Project (Keep Unlinked)</option>
                  {projects.map(project => (
                    <option key={project.id} value={project.id}>{project.name}</option>
                  ))}
                </select>
              </div>
            )}
            
            <div className="mb-4">
              <label className="block text-sm text-gray-400 mb-1">Tags (Optional)</label>
              <input 
                type="text" 
                className="w-full bg-navy p-2 rounded text-gray-300"
                placeholder="Add tags separated by commas..."
              />
            </div>
            
            <div className="flex justify-end">
              <button 
                onClick={() => setShowAddTagModal(false)}
                className="px-3 py-1 bg-navy hover:bg-navy-lighter rounded text-sm mr-2"
              >
                Cancel
              </button>
              <button 
                onClick={async () => {
                  // In a real implementation, this would actually upload the files
                  setShowAddTagModal(false);
                  setIsUploading(true);
                  
                  // Simulate upload delay
                  setTimeout(() => {
                    setIsUploading(false);
                    // Would refresh the file list here after upload
                  }, 1500);
                }}
                className="px-3 py-1 bg-gold text-navy font-medium rounded hover:bg-gold/90"
                disabled={isUploading}
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