import React, { useState, useEffect } from 'react';
import { fileService, projectService } from '../../services';
import { File, FileFilterOptions, ProcessingStats } from '../../services/fileService';
import { Project } from '../../services/projectService';

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
  description: apiFile.description
});

type ProjectFileManagerProps = {
  projectId: string;
  onReturn: () => void; // Function to return to project view
  onOpenMainFileManager: () => void; // Function to open the main file manager
};

const ProjectFileManager: React.FC<ProjectFileManagerProps> = ({ 
  projectId, 
  onReturn, 
  onOpenMainFileManager 
}) => {
  // Files state
  const [projectFiles, setProjectFiles] = useState<LocalFile[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Project state
  const [project, setProject] = useState<Project | null>(null);
  
  // Upload state
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  
  // Effect to get project and files
  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        // Get project details
        const projectData = await projectService.getProject(projectId);
        setProject(projectData);
        
        // Get project files
        const filterOptions: FileFilterOptions = {
          project_id: projectId,
          active_only: false // Get all files, active and inactive
        };
        
        const apiFiles = await fileService.getAllFiles(filterOptions);
        const localFiles = apiFiles.map(mapApiFileToLocal);
        setProjectFiles(localFiles);
      } catch (err) {
        console.error('Error fetching project files:', err);
        setError('Failed to load project files. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchData();
  }, [projectId]);

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
    try {
      // Call API to unlink file
      await fileService.unlinkFilesFromProject([fileId], projectId);
      
      // Update local state
      setProjectFiles(prevFiles => prevFiles.filter(file => file.id !== fileId));
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
        </div>
        <div className="flex space-x-2">
          <button 
            onClick={onReturn}
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
          onClick={onOpenMainFileManager}
          className="px-4 py-2 bg-gold/20 hover:bg-gold/30 text-gold rounded"
        >
          Browse Global Files
        </button>
      </div>
      
      {/* Attached Files List */}
      <div className="flex-1 bg-navy-light p-4 rounded-lg overflow-y-auto">
        <h3 className="text-lg font-medium text-gold mb-3 pb-2 border-b border-navy">Project Files</h3>
        
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
                  <div className={`w-10 h-10 bg-${getFileTypeColor(file.type)}-500/20 rounded flex items-center justify-center mr-3`}>
                    <span className={`text-${getFileTypeColor(file.type)}-400 text-xs`}>{file.type}</span>
                  </div>
                  <div>
                    <h4 className="font-medium">{file.name}</h4>
                    <div className="flex text-xs text-gray-400 space-x-2">
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
      
      {/* File Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-navy-light rounded-lg p-6 max-w-md w-full">
            <h3 className="text-lg font-medium text-gold mb-4">Upload Files to Project</h3>
            
            <div className="mb-4">
              <label className="block text-sm text-gray-400 mb-1">Files</label>
              <input 
                type="file" 
                multiple
                className="w-full bg-navy p-2 rounded text-gray-300"
              />
            </div>
            
            <div className="mb-4">
              <label className="block text-sm text-gray-400 mb-1">Description</label>
              <textarea 
                className="w-full bg-navy p-2 rounded text-gray-300 h-20"
                placeholder="Add a description for these files..."
              />
            </div>
            
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
                onClick={() => setShowUploadModal(false)}
                className="px-3 py-1 bg-navy hover:bg-navy-lighter rounded text-sm mr-2"
              >
                Cancel
              </button>
              <button 
                onClick={async () => {
                  // In a real implementation, this would actually upload the files
                  setShowUploadModal(false);
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

export default ProjectFileManager;