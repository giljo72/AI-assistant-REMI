import React, { useState, useEffect } from 'react';
import { fileService, projectService } from '../../services';
import { File, FileFilterOptions, ProcessingStats } from '../../services/fileService';
import { Project } from '../../services/projectService';
import { useNavigation } from '../../hooks/useNavigation';
import { ProjectId, normalizeProjectId, isFileLinkedToProject } from '../../types/common';
import TagAndAddFileModal from '../modals/TagAndAddFileModal';

// Local interface for mapped files from API response
interface LocalFile {
  id: string;
  name: string;
  type: string;
  size: string;
  active: boolean;
  projectId: ProjectId; // Using our ProjectId type for consistency
  projectName?: string; // Name of the project this file is linked to
  addedAt: string;
  processed: boolean; // Indicates if the file has been processed into vector DB
  processingFailed?: boolean; // If processing failed
  chunks?: number; // Number of chunks if processed
  description?: string;
}

// File type metadata for improved visualization
interface FileTypeMetadata {
  color: string;
  icon: string;
  description: string;
}

// Get file type metadata for display
const getFileTypeMetadata = (type: string): FileTypeMetadata => {
  const fileType = type.toLowerCase();
  
  switch (fileType) {
    case 'pdf':
      return {
        color: 'red',
        icon: '📄',
        description: 'Adobe PDF Document'
      };
    case 'docx':
    case 'doc':
      return {
        color: 'blue',
        icon: '📝',
        description: 'Microsoft Word Document'
      };
    case 'xlsx':
    case 'xls':
      return {
        color: 'green',
        icon: '📊',
        description: 'Microsoft Excel Spreadsheet'
      };
    case 'pptx':
    case 'ppt':
      return {
        color: 'orange',
        icon: '📋',
        description: 'Microsoft PowerPoint Presentation'
      };
    case 'png':
    case 'jpg':
    case 'jpeg':
    case 'gif':
    case 'bmp':
      return {
        color: 'purple',
        icon: '🖼️',
        description: 'Image File'
      };
    case 'txt':
      return {
        color: 'gray',
        icon: '📄',
        description: 'Text Document'
      };
    case 'md':
    case 'markdown':
      return {
        color: 'cyan',
        icon: '📝',
        description: 'Markdown Document'
      };
    case 'json':
    case 'xml':
    case 'yaml':
    case 'yml':
      return {
        color: 'yellow',
        icon: '⚙️',
        description: 'Data/Configuration File'
      };
    case 'csv':
      return {
        color: 'green',
        icon: '📊',
        description: 'Comma-Separated Values'
      };
    case 'zip':
    case 'rar':
    case '7z':
    case 'tar':
    case 'gz':
      return {
        color: 'amber',
        icon: '📦',
        description: 'Compressed Archive'
      };
    case 'html':
    case 'htm':
    case 'css':
    case 'js':
      return {
        color: 'indigo',
        icon: '🌐',
        description: 'Web Document'
      };
    default:
      return {
        color: 'gray',
        icon: '📄',
        description: 'Document'
      };
  }
};

// Helper function to get just the color
const getFileTypeColor = (type: string): string => {
  return getFileTypeMetadata(type).color;
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
const mapApiFileToLocal = (apiFile: File): LocalFile => {
  // Log the raw project_id value for debugging
  console.log(`[PROJECTFILE-MAPPER] Mapping file ${apiFile.id} (${apiFile.name}), project_id: ${apiFile.project_id}, project_name: ${(apiFile as any).project_name}, type: ${typeof apiFile.project_id}`);
  
  // Use our normalization function for consistent types
  const normalizedProjectId = normalizeProjectId(apiFile.project_id);
  
  console.log(`[PROJECTFILE-MAPPER] Normalized project_id for ${apiFile.id}: ${normalizedProjectId} (${typeof normalizedProjectId})`);
  
  return {
    id: apiFile.id,
    name: apiFile.name,
    type: apiFile.type.toUpperCase(),
    size: formatFileSize(apiFile.size),
    active: apiFile.active,
    projectId: normalizedProjectId, // Using our normalized project ID
    projectName: (apiFile as any).project_name, // Include project name from backend
    addedAt: apiFile.created_at.split('T')[0], // Format date
    processed: apiFile.processed,
    processingFailed: apiFile.processing_failed,
    chunks: apiFile.chunk_count,
    description: apiFile.description
  };
};

type ProjectFileManagerProps = {
  // No props needed since we use the navigation system
};

const ProjectFileManager: React.FC<ProjectFileManagerProps> = () => {
  // Use our navigation hook
  const navigation = useNavigation();
  
  // Get the current project ID from navigation state
  const projectId = navigation.activeProjectId || '';
  
  // Helper function to return to project view
  const handleReturn = () => {
    navigation.navigateToView('project');
  };
  
  // Helper function to open the main file manager
  const handleOpenMainFileManager = () => {
    navigation.openMainFileManager();
  };
  // Files state
  const [projectFiles, setProjectFiles] = useState<LocalFile[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Project state
  const [project, setProject] = useState<Project | null>(null);
  
  // Upload state
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  
  // Selection state
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);
  const [selectAllChecked, setSelectAllChecked] = useState(false);
  
  // Details panel state
  const [selectedFileDetails, setSelectedFileDetails] = useState<LocalFile | null>(null);
  const [showDetailsPanel, setShowDetailsPanel] = useState(false);
  
  // Function to fetch project and files
  const fetchProjectData = async () => {
    console.log(`[PROJECTFILEMANAGER] Loading data for project ${projectId}`);
    setIsLoading(true);
    setError(null);
    
    try {
      // Get project details
      const projectData = await projectService.getProject(projectId);
      console.log("[PROJECTFILEMANAGER] Project data loaded:", projectData);
      setProject(projectData);
      
      // Normalize the project ID for consistency
      const normalizedProjectId = normalizeProjectId(projectId);
      console.log(`[PROJECTFILEMANAGER] Normalized project ID: ${normalizedProjectId} (${typeof normalizedProjectId})`);
      
      if (!normalizedProjectId) {
        console.error('[PROJECTFILEMANAGER] Invalid project ID provided:', projectId);
        setError('Invalid project ID. Cannot load files.');
        setIsLoading(false);
        return;
      }
      
      // Force refresh of localStorage first
      try {
        const storedFiles = localStorage.getItem('mockFiles');
        if (storedFiles) {
          // Parse and normalize all project IDs from localStorage
          const parsedFiles = JSON.parse(storedFiles);
          window.mockFiles = parsedFiles.map((file: any) => ({
            ...file,
            project_id: normalizeProjectId(file.project_id)
          }));
          
          console.log("[PROJECTFILEMANAGER] Refreshed mockFiles from localStorage:", window.mockFiles.length);
          
          // Log all project-related files in storage using normalized comparison
          const projectFiles = parsedFiles.filter((f: any) => 
            normalizeProjectId(f.project_id) === normalizedProjectId
          );
          
          console.log(`[PROJECTFILEMANAGER] Found ${projectFiles.length} files for project ${normalizedProjectId} in localStorage:`);
          projectFiles.forEach((file: any) => {
            console.log(`- ${file.id} (${file.name}), project_id: ${file.project_id}, normalized: ${normalizeProjectId(file.project_id)}`);
          });
        }
      } catch (e) {
        console.error('[PROJECTFILEMANAGER] Error refreshing mockFiles from localStorage', e);
      }
      
      // Get project files with normalized project ID
      const filterOptions: FileFilterOptions = {
        project_id: normalizedProjectId, // Use the normalized ID
        active_only: false // Get all files, active and inactive
      };
      
      console.log("[PROJECTFILEMANAGER] Fetching files with options:", filterOptions);
      const apiFiles = await fileService.getAllFiles(filterOptions);
      console.log("[PROJECTFILEMANAGER] Files received from API:", apiFiles.length);
      
      // Map files with consistent project ID handling
      const localFiles = apiFiles.map(mapApiFileToLocal);
      console.log("[PROJECTFILEMANAGER] Mapped files:", localFiles.length);
      
      // Double-check that all files are properly linked to this project
      const linkedFileCount = localFiles.filter(file => 
        normalizeProjectId(file.projectId) === normalizedProjectId
      ).length;
      
      console.log(`[PROJECTFILEMANAGER] Verification: ${linkedFileCount} out of ${localFiles.length} files correctly linked to project ${normalizedProjectId}`);
      
      setProjectFiles(localFiles);
    } catch (err) {
      console.error('[PROJECTFILEMANAGER] Error fetching project files:', err);
      setError('Failed to load project files. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Toggle file selection for bulk operations
  const toggleFileSelection = (fileId: string) => {
    setSelectedFiles(prev => {
      const newSelection = prev.includes(fileId) 
        ? prev.filter(id => id !== fileId) 
        : [...prev, fileId];
      
      // Update select all checkbox state
      setSelectAllChecked(newSelection.length === projectFiles.length);
      
      return newSelection;
    });
  };
  
  // Toggle all files selection
  const toggleSelectAll = () => {
    if (selectAllChecked) {
      // Deselect all files
      setSelectedFiles([]);
      setSelectAllChecked(false);
    } else {
      // Select all files
      const allFileIds = projectFiles.map(file => file.id);
      setSelectedFiles(allFileIds);
      setSelectAllChecked(true);
    }
  };
  
  // Clear selection
  const clearSelection = () => {
    setSelectedFiles([]);
    setSelectAllChecked(false);
  };
  
  // Handle bulk detach action
  const handleBulkDetach = async () => {
    if (selectedFiles.length === 0 || !project?.id) return;
    
    if (window.confirm(`Are you sure you want to detach ${selectedFiles.length} files from this project?`)) {
      try {
        // Normalize project ID for consistency
        const normalizedProjectId = normalizeProjectId(projectId);
        
        // Call API to unlink the files
        await fileService.unlinkFilesFromProject(selectedFiles, normalizedProjectId);
        
        // Update local state by removing the detached files
        setProjectFiles(prev => prev.filter(file => !selectedFiles.includes(file.id)));
        
        // Clear selection
        setSelectedFiles([]);
        setSelectAllChecked(false);
        
        // Force refresh to ensure we have the latest data
        setTimeout(() => {
          fetchProjectData();
        }, 500);
      } catch (err) {
        console.error('Error detaching files from project:', err);
        setError('Failed to detach files from project. Please try again.');
      }
    }
  };
  
  // Handle bulk activation/deactivation
  const handleBulkToggleActive = async (activate: boolean) => {
    if (selectedFiles.length === 0) return;
    
    try {
      // Update each file in the selection
      for (const fileId of selectedFiles) {
        await fileService.updateFile(fileId, { active: activate });
      }
      
      // Update local state
      setProjectFiles(prev => 
        prev.map(file => 
          selectedFiles.includes(file.id) 
            ? { ...file, active: activate } 
            : file
        )
      );
      
      // Keep selection but refresh data
      setTimeout(() => {
        fetchProjectData();
      }, 500);
    } catch (err) {
      console.error(`Error ${activate ? 'activating' : 'deactivating'} files:`, err);
      setError(`Failed to ${activate ? 'activate' : 'deactivate'} files. Please try again.`);
    }
  };

  // Effect to get project and files
  useEffect(() => {
    fetchProjectData();
    
    // Define event handlers for file changes
    const handleFileChange = async (event: Event) => {
      console.log("[PROJECTFILEMANAGER] File change event detected, refreshing file list");
      
      // Get details from the event if available
      const customEvent = event as CustomEvent;
      if (customEvent.detail) {
        console.log("[PROJECTFILEMANAGER] Event details:", customEvent.detail);
        
        // Check if this event is related to our project
        if (customEvent.detail.project === projectId) {
          console.log("[PROJECTFILEMANAGER] This event is related to our project, refreshing immediately");
          await fetchProjectData();
        }
      } else {
        // If no details, refresh anyway
        await fetchProjectData();
      }
    };
    
    // Add event listeners
    window.addEventListener('mockFileAdded', handleFileChange);
    window.addEventListener('mockFileDeleted', handleFileChange);
    
    // Clean up event listeners when component unmounts
    return () => {
      window.removeEventListener('mockFileAdded', handleFileChange);
      window.removeEventListener('mockFileDeleted', handleFileChange);
    };
  }, [projectId]);

  // Show file details panel
  const showFileDetails = (file: LocalFile) => {
    setSelectedFileDetails(file);
    setShowDetailsPanel(true);
  };
  
  // Close file details panel
  const closeDetailsPanel = () => {
    setShowDetailsPanel(false);
    // Clear the selected file after a brief delay for smooth animation
    setTimeout(() => setSelectedFileDetails(null), 300);
  };

  // Handle file activation toggle
  const handleToggleActive = async (fileId: string, currentActive: boolean) => {
    try {
      // Optimistically update UI
      setProjectFiles(prevFiles => 
        prevFiles.map(file => 
          file.id === fileId ? { ...file, active: !currentActive } : file
        )
      );
      
      // Call API to update file
      await fileService.updateFile(fileId, { active: !currentActive });
    } catch (err) {
      console.error('Error toggling file active state:', err);
      setError('Failed to update file status. Please try again.');
      
      // Revert UI on error
      setProjectFiles(prevFiles => 
        prevFiles.map(file => 
          file.id === fileId ? { ...file, active: currentActive } : file
        )
      );
    }
  };

  // Handle file detachment from project
  const handleDetachFile = async (fileId: string) => {
    // Normalize project ID for consistency
    const normalizedProjectId = normalizeProjectId(projectId);
    
    console.log(`Attempting to detach file ${fileId} from project ${normalizedProjectId} (original: ${projectId})`);
    
    if (!normalizedProjectId) {
      console.error('[PROJECTFILEMANAGER] Cannot detach file: Invalid project ID');
      setError('Invalid project ID. Cannot detach file.');
      return;
    }
    
    try {
      // Call API to unlink file with normalized project ID
      await fileService.unlinkFilesFromProject([fileId], normalizedProjectId);
      
      // Update local state
      setProjectFiles(prevFiles => prevFiles.filter(file => file.id !== fileId));
      
      console.log(`Successfully detached file ${fileId} from project ${normalizedProjectId}`);
      
      // Force refresh of project data to ensure consistency
      setTimeout(() => {
        fetchProjectData(); // Reload after a brief delay to allow storage to update
      }, 500);
    } catch (err) {
      console.error('Error detaching file from project:', err);
      setError('Failed to detach file from project. Please try again.');
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="bg-navy-light p-4 mb-4 rounded-lg flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-gold">Project File Manager</h2>
          <p className="text-gray-400 text-sm">
            Project: {project?.name || 'Loading...'}
          </p>
          <div className="mt-2 flex items-center space-x-3">
            <span className="px-2 py-0.5 bg-navy rounded text-sm">
              <span className="text-gold font-medium">{projectFiles.length}</span>
              <span className="text-gray-400 ml-1">project files</span>
            </span>
            <span className="px-2 py-0.5 bg-navy rounded text-sm">
              <span className="text-green-400 font-medium">{projectFiles.filter(f => f.active).length}</span>
              <span className="text-gray-400 ml-1">active</span>
            </span>
            <span className="px-2 py-0.5 bg-navy rounded text-sm">
              <span className="text-orange-400 font-medium">{projectFiles.filter(f => !f.active).length}</span>
              <span className="text-gray-400 ml-1">inactive</span>
            </span>
          </div>
        </div>
        <div className="flex space-x-2">
          <button 
            onClick={handleReturn}
            className="px-3 py-1 bg-navy hover:bg-navy-lighter rounded text-sm"
          >
            Return to Project
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
            onClick={() => setShowUploadModal(true)}
            disabled={isUploading}
          >
            {isUploading ? 'Uploading...' : 'Browse Files'}
          </button>
        </div>
      </div>
      
      {/* Browse Global Files button */}
      <div className="bg-navy-light p-4 mb-4 rounded-lg flex justify-center">
        <button 
          onClick={handleOpenMainFileManager}
          className="px-4 py-2 bg-gold/20 hover:bg-gold/30 text-gold rounded"
        >
          Browse Global Files
        </button>
      </div>
      
      {/* Attached Files List */}
      <div className="flex-1 bg-navy-light p-4 rounded-lg overflow-y-auto">
        <h3 className="text-lg font-medium text-gold mb-3 pb-2 border-b border-navy flex justify-between items-center">
          <div className="flex items-center">
            <span>Project Files</span>
            <div className="ml-3 text-sm bg-navy/60 rounded px-2 py-0.5 flex items-center">
              <span className="text-gray-400">Processing Status:</span>
              <span className="ml-2 text-green-400 font-medium">{projectFiles.filter(f => f.processed).length}</span>
              <span className="text-gray-400 mx-1">/</span>
              <span className="text-gold font-medium">{projectFiles.length}</span>
              {projectFiles.some(f => f.processingFailed) && (
                <span className="ml-2 text-red-400">⚠ {projectFiles.filter(f => f.processingFailed).length} failed</span>
              )}
            </div>
          </div>
          
          {/* Bulk Actions Menu */}
          <div className="flex items-center">
            {/* Select All Checkbox */}
            <div className="flex items-center mr-3">
              <label className="flex items-center cursor-pointer mr-3">
                <input
                  type="checkbox"
                  checked={selectAllChecked}
                  onChange={toggleSelectAll}
                  className="w-4 h-4 accent-gold bg-navy border-gold/30 rounded focus:ring-gold"
                />
                <span className="ml-2 text-xs text-gray-400">Select All</span>
              </label>
              
              {selectedFiles.length > 0 && (
                <button
                  onClick={clearSelection}
                  className="text-xs text-gray-400 hover:text-gray-300 underline ml-2"
                >
                  Clear
                </button>
              )}
            </div>
            
            {/* Bulk action buttons - only show when files are selected */}
            {selectedFiles.length > 0 && (
              <div className="flex space-x-2">
                <button
                  onClick={() => handleBulkToggleActive(true)}
                  className="text-xs px-2 py-1 bg-green-700/30 hover:bg-green-700/50 text-green-400 rounded"
                  title="Activate selected files"
                >
                  Activate ({selectedFiles.length})
                </button>
                
                <button
                  onClick={() => handleBulkToggleActive(false)}
                  className="text-xs px-2 py-1 bg-orange-700/30 hover:bg-orange-700/50 text-orange-400 rounded"
                  title="Deactivate selected files"
                >
                  Deactivate ({selectedFiles.length})
                </button>
                
                <button
                  onClick={handleBulkDetach}
                  className="text-xs px-2 py-1 bg-red-700/30 hover:bg-red-700/50 text-red-400 rounded"
                  title="Detach selected files from project"
                >
                  Detach ({selectedFiles.length})
                </button>
              </div>
            )}
          </div>
        </h3>
        
        {isLoading ? (
          <div className="p-6 text-center">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-gold border-r-transparent align-[-0.125em]" role="status">
              <span className="!absolute !-m-px !h-px !w-px !overflow-hidden !whitespace-nowrap !border-0 !p-0 ![clip:rect(0,0,0,0)]">Loading...</span>
            </div>
            <div className="mt-2 text-gray-400">Loading project files...</div>
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
        ) : projectFiles.length > 0 ? (
          <div className="space-y-2">
            {projectFiles.map(file => (
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
                  <div className={`w-12 h-12 bg-${getFileTypeColor(file.type)}-500/20 rounded-lg flex flex-col items-center justify-center mr-3`} 
                    title={getFileTypeMetadata(file.type).description}>
                    <span className="text-xl">{getFileTypeMetadata(file.type).icon}</span>
                    <span className={`text-${getFileTypeColor(file.type)}-400 text-xs mt-1`}>{file.type}</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="font-medium">{file.name}</h4>
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
                    </div>
                    
                    {/* File Description Box - Hidden by default */}
                    <div id={`project-file-description-box-${file.id}`} className="w-full mt-2 hidden">
                      <div className="bg-navy-lighter p-3 rounded">
                        <h5 className="text-sm font-medium text-gold mb-1">Description:</h5>
                        <div className="text-xs text-gray-300">
                          {file.description ? 
                            file.description : 
                            <span className="italic text-gray-500">No description provided</span>
                          }
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="flex space-x-2 items-center">
                  <div className="flex items-center mr-2">
                    <label className="inline-flex items-center cursor-pointer">
                      <span className={`text-xs mr-2 ${file.active ? 'text-green-400' : 'text-gray-500'}`}>
                        {file.active ? 'Active' : 'Inactive'}
                      </span>
                      <input 
                        type="checkbox" 
                        checked={file.active}
                        onChange={() => handleToggleActive(file.id, file.active)}
                        className="sr-only peer"
                      />
                      <div className={`w-9 h-5 rounded-full peer ${file.active ? 'bg-gold/40' : 'bg-navy-lighter'} peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all relative`}></div>
                    </label>
                  </div>
                  {/* View Details Button */}
                  <button 
                    onClick={() => showFileDetails(file)}
                    className="w-8 h-8 flex items-center justify-center bg-gold/20 hover:bg-gold/30 text-gold rounded"
                    title="View file details"
                  >
                    👁️
                  </button>
                  
                  {/* Download Button - Using ⬇️ as placeholder for download icon */}
                  <button 
                    onClick={async () => {
                      try {
                        console.log(`Attempting to download file: ${file.id} - ${file.name}`);
                        
                        // Try two different download methods for maximum compatibility
                        
                        // Method 1: Direct URL approach
                        const baseUrl = window.location.origin;
                        const downloadUrl = `${baseUrl}/api/files/${file.id}/download`;
                        console.log(`Download URL: ${downloadUrl}`);
                        
                        // Try direct download method first
                        const a = document.createElement('a');
                        a.href = downloadUrl;
                        a.download = file.name; // Suggest a filename
                        a.target = '_blank';
                        a.rel = 'noopener noreferrer';
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                          
                        // Method 2: Backup approach - use fileService
                        // This will be attempted if the user sees Method 1 not working
                        console.log("If the file doesn't download automatically, try the API method...");
                        
                        // Allow user to try a backup method if needed
                        setTimeout(() => {
                          try {
                            // Create a trigger for backup method if needed
                            const backupTrigger = document.createElement('div');
                            backupTrigger.textContent = 'Click here if download didn\'t start';
                            backupTrigger.style.position = 'fixed';
                            backupTrigger.style.bottom = '20px';
                            backupTrigger.style.right = '20px';
                            backupTrigger.style.backgroundColor = '#1F2937';
                            backupTrigger.style.color = '#D1D5DB';
                            backupTrigger.style.padding = '10px';
                            backupTrigger.style.borderRadius = '4px';
                            backupTrigger.style.cursor = 'pointer';
                            backupTrigger.style.zIndex = '9999';
                            backupTrigger.onclick = async () => {
                              try {
                                // Use the Blob method as backup
                                const blob = await fileService.downloadFile(file.id);
                                const url = window.URL.createObjectURL(blob);
                                const a = document.createElement('a');
                                a.href = url;
                                a.download = file.name;
                                document.body.appendChild(a);
                                a.click();
                                window.URL.revokeObjectURL(url);
                                a.remove();
                                document.body.removeChild(backupTrigger);
                              } catch (backupError) {
                                console.error('Backup download method failed:', backupError);
                                alert('Both download methods failed. Please try again later.');
                              }
                            };
                            document.body.appendChild(backupTrigger);
                            
                            // Auto-remove after 10 seconds
                            setTimeout(() => {
                              if (document.body.contains(backupTrigger)) {
                                document.body.removeChild(backupTrigger);
                              }
                            }, 10000);
                          } catch (notifyError) {
                            console.error('Error showing backup notification:', notifyError);
                          }
                        }, 1000);
                      } catch (err) {
                        console.error('Error initiating download:', err);
                        setError('Failed to download file. Please try again.');
                      }
                    }}
                    className="w-8 h-8 flex items-center justify-center bg-gold/20 hover:bg-gold/30 text-gold rounded"
                    title="Download file"
                  >
                    ⬇️
                  </button>
                  
                  {/* Detach Button - Keeping as text for clarity */}
                  <button 
                    className="text-xs px-2 py-1 bg-red-700/30 hover:bg-red-700/50 text-red-400 rounded"
                    onClick={() => handleDetachFile(file.id)}
                  >
                    Detach
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-3 text-center text-gray-400">
            No files attached to this project yet. Use the controls above to add files.
          </div>
        )}
      </div>
      
      {/* File Details Panel */}
      {showDetailsPanel && selectedFileDetails && (
        <div className="fixed inset-y-0 right-0 w-80 bg-navy-light border-l border-navy-lighter shadow-lg z-40 transform transition-transform duration-300 ease-in-out">
          <div className="h-full flex flex-col p-4">
            {/* Header */}
            <div className="flex justify-between items-center mb-4 pb-3 border-b border-navy">
              <h3 className="text-lg font-medium text-gold">File Details</h3>
              <button 
                onClick={closeDetailsPanel}
                className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-navy/50"
                title="Close details"
              >
                ✕
              </button>
            </div>
            
            {/* File preview */}
            <div className="mb-4 bg-navy rounded-lg p-4 flex flex-col items-center">
              <div className={`w-16 h-16 bg-${getFileTypeColor(selectedFileDetails.type)}-500/20 rounded-lg flex flex-col items-center justify-center mb-2`}>
                <span className="text-2xl">{getFileTypeMetadata(selectedFileDetails.type).icon}</span>
                <span className={`text-${getFileTypeColor(selectedFileDetails.type)}-400 text-xs mt-1`}>{selectedFileDetails.type}</span>
              </div>
              <h4 className="text-center font-medium text-gold mt-2 break-words w-full">{selectedFileDetails.name}</h4>
            </div>
            
            {/* File metadata */}
            <div className="flex-1 overflow-y-auto">
              <div className="space-y-4">
                {/* Basic info */}
                <div>
                  <h5 className="text-sm text-gray-400 mb-1">Basic Information</h5>
                  <div className="bg-navy rounded p-3 space-y-2">
                    <div className="flex justify-between">
                      <span className="text-xs text-gray-400">Size:</span>
                      <span className="text-xs text-gold">{selectedFileDetails.size}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-xs text-gray-400">Added:</span>
                      <span className="text-xs text-gold">{selectedFileDetails.addedAt}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-xs text-gray-400">Status:</span>
                      <span className="text-xs">
                        {selectedFileDetails.processed ? (
                          <span className="text-green-400">Processed</span>
                        ) : selectedFileDetails.processingFailed ? (
                          <span className="text-red-400">Processing Failed</span>
                        ) : (
                          <span className="text-yellow-400">Processing...</span>
                        )}
                      </span>
                    </div>
                    {selectedFileDetails.processed && selectedFileDetails.chunks && (
                      <div className="flex justify-between">
                        <span className="text-xs text-gray-400">Chunks:</span>
                        <span className="text-xs text-gold">{selectedFileDetails.chunks}</span>
                      </div>
                    )}
                  </div>
                </div>
                
                {/* Project status */}
                <div>
                  <h5 className="text-sm text-gray-400 mb-1">Project Status</h5>
                  <div className="bg-navy rounded p-3">
                    <div className="flex justify-between mb-2">
                      <span className="text-xs text-gray-400">Project:</span>
                      <span className="text-xs text-blue-400">
                        {project?.name || 'Current Project'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-xs text-gray-400">Active in project:</span>
                      <span className={`text-xs ${selectedFileDetails.active ? 'text-green-400' : 'text-orange-400'}`}>
                        {selectedFileDetails.active ? 'Yes' : 'No'}
                      </span>
                    </div>
                  </div>
                </div>
                
                {/* Description */}
                <div>
                  <h5 className="text-sm text-gray-400 mb-1">Description</h5>
                  <div className="bg-navy rounded p-3">
                    {selectedFileDetails.description ? (
                      <p className="text-xs text-gray-300 whitespace-pre-wrap">{selectedFileDetails.description}</p>
                    ) : (
                      <p className="text-xs text-gray-500 italic">No description provided</p>
                    )}
                  </div>
                </div>
              </div>
            </div>
            
            {/* Action buttons */}
            <div className="mt-4 pt-3 border-t border-navy flex justify-between">
              <button 
                onClick={async () => {
                  try {
                    const blob = await fileService.downloadFile(selectedFileDetails.id);
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = selectedFileDetails.name;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    a.remove();
                  } catch (err) {
                    console.error(`Error downloading file:`, err);
                  }
                }}
                className="px-3 py-1.5 bg-gold/20 hover:bg-gold/30 text-gold rounded text-sm flex-1 mr-2"
              >
                Download
              </button>
              
              <button 
                onClick={() => {
                  // Toggle active state
                  handleToggleActive(selectedFileDetails.id, selectedFileDetails.active);
                  // Update the details panel
                  setSelectedFileDetails({...selectedFileDetails, active: !selectedFileDetails.active});
                }}
                className={`px-3 py-1.5 ${selectedFileDetails.active ? 'bg-orange-700/30 hover:bg-orange-700/50 text-orange-400' : 'bg-green-700/30 hover:bg-green-700/50 text-green-400'} rounded text-sm flex-1`}
              >
                {selectedFileDetails.active ? 'Deactivate' : 'Activate'}
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* File Upload Modal using TagAndAddFileModal */}
      <TagAndAddFileModal
        isOpen={showUploadModal}
        onClose={() => setShowUploadModal(false)}
        onProcessFiles={async (selectedFiles) => {
          console.log("Processing files from TagAndAddFileModal in ProjectFileManager:", selectedFiles);
          setIsUploading(true);
          
          try {
            // Process each file with its individual description
            for (const selectedFile of selectedFiles) {
              console.log("Processing file:", {
                name: selectedFile.file.name,
                description: selectedFile.description,
                projectId: selectedFile.projectId
              });
              
              const uploadRequest = {
                file: selectedFile.file,
                name: selectedFile.file.name,
                description: selectedFile.description,
                project_id: selectedFile.projectId || projectId
              };
              
              try {
                // Upload the file using fileService
                await fileService.uploadFile(uploadRequest);
                console.log(`Successfully uploaded file: ${selectedFile.file.name} with project_id: ${selectedFile.projectId || projectId}`);
              } catch (uploadError) {
                console.error(`Error uploading file ${selectedFile.file.name}:`, uploadError);
                // If the API endpoint doesn't exist yet, show a mock success message
                alert(`Mock upload: File ${selectedFile.file.name} uploaded successfully (API endpoint not available)`);
              }
            }
            
            // Refresh project files list
            try {
              const filterOptions: FileFilterOptions = {
                project_id: projectId,
                active_only: false
              };
              
              console.log("[PROJECTFILEMANAGER] Refreshing files after upload with options:", filterOptions);
              const apiFiles = await fileService.getAllFiles(filterOptions);
              console.log("[PROJECTFILEMANAGER] Received", apiFiles.length, "files after upload");
              
              const localFiles = apiFiles.map(mapApiFileToLocal);
              console.log("[PROJECTFILEMANAGER] Mapped files after upload:", localFiles.length);
              
              setProjectFiles(localFiles);
              
              // Also dispatch a custom event to ensure MainFileManager is updated
              const refreshEvent = new CustomEvent('mockFileAdded');
              window.dispatchEvent(refreshEvent);
            } catch (refreshError) {
              console.error('Error refreshing file list:', refreshError);
            }
            
            console.log(`Successfully processed ${selectedFiles.length} files`);
          } catch (error) {
            console.error('Error uploading files:', error);
            setError('Failed to upload one or more files. Please try again.');
          } finally {
            setIsUploading(false);
          }
        }}
        currentProjectId={projectId}
      />
    </div>
  );
};

export default ProjectFileManager;