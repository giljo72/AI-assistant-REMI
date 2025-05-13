import React, { useState, useEffect } from 'react';

// Define types for our data
type File = {
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
};

// Define types for projects
type Project = {
  id: string;
  name: string;
};

// Mock project data
const mockProjects: Project[] = [
  { id: '1', name: 'Research Paper' },
  { id: '2', name: 'Website Redesign' },
  { id: '3', name: 'Marketing Campaign' },
  { id: '4', name: 'Product Launch' },
];

// Mock data for documents
const mockFiles: File[] = [
  { id: '1', name: 'Research Paper.pdf', type: 'PDF', size: '1.2 MB', active: true, projectId: '1', addedAt: '2025-05-10', processed: true, chunks: 24 },
  { id: '2', name: 'Literature Notes.docx', type: 'DOCX', size: '538 KB', active: true, projectId: '1', addedAt: '2025-05-09', processed: true, chunks: 12 },
  { id: '3', name: 'Data Analysis.xlsx', type: 'XLSX', size: '724 KB', active: false, projectId: '1', addedAt: '2025-05-08', processed: true, chunks: 8 },
  { id: '4', name: 'Website Mockup.png', type: 'PNG', size: '2.4 MB', active: true, projectId: '2', addedAt: '2025-05-07', processed: true, chunks: 1 },
  { id: '5', name: 'Campaign Brief.pdf', type: 'PDF', size: '890 KB', active: true, projectId: '3', addedAt: '2025-05-06', processed: true, chunks: 16 },
  { id: '6', name: 'Reference Paper.pdf', type: 'PDF', size: '1.7 MB', active: true, projectId: null, addedAt: '2025-05-05', processed: true, chunks: 32 },
  { id: '7', name: 'General Notes.txt', type: 'TXT', size: '45 KB', active: true, projectId: null, addedAt: '2025-05-04', processed: true, chunks: 5 },
  { id: '8', name: 'Template.docx', type: 'DOCX', size: '230 KB', active: true, projectId: null, addedAt: '2025-05-03', processed: true, chunks: 7 },
  { id: '9', name: 'Failed Document.pdf', type: 'PDF', size: '3.8 MB', active: false, projectId: null, addedAt: '2025-05-01', processed: false, processingFailed: true },
];

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

// This function returns the projects a file is linked to
const getLinkedProjects = (fileId: string): Project[] => {
  const projectIds = mockFiles
    .filter(file => file.id === fileId && file.projectId !== null)
    .map(file => file.projectId as string);
  
  return mockProjects.filter(project => projectIds.includes(project.id));
};

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
  const [files, setFiles] = useState<File[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortField, setSortField] = useState<'name' | 'date' | 'size' | 'status' | 'processed'>('date');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');
  const [showAddTagModal, setShowAddTagModal] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);
  const [searchResults, setSearchResults] = useState<Array<File & { relevance?: number }>>([]); 
  const [isSearching, setIsSearching] = useState(false);
  const [gpuUsage, setGpuUsage] = useState(0); // Mock GPU usage for processing indicator

  // Effect to load all files
  useEffect(() => {
    setFiles(mockFiles);
    
    // Simulate GPU usage fluctuation for visual effect
    const interval = setInterval(() => {
      setGpuUsage(Math.floor(Math.random() * 80) + 10); // Random number between 10-90%
    }, 2000);
    
    return () => clearInterval(interval);
  }, []);

  // Handle search
  const handleSearch = () => {
    if (!searchTerm.trim()) {
      setIsSearching(false);
      setSearchResults([]);
      return;
    }
    
    setIsSearching(true);
    
    // Simulate search with relevance scores
    const results = files
      .filter(file => 
        file.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
        (file.description && file.description.toLowerCase().includes(searchTerm.toLowerCase()))
      )
      .map(file => ({
        ...file,
        relevance: Math.floor(Math.random() * 50) + 50 // Random relevance score between 50-100%
      }))
      .sort((a, b) => (b.relevance || 0) - (a.relevance || 0));
    
    setSearchResults(results);
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
  const handleAttachToProject = () => {
    if (!projectId || selectedFiles.length === 0) return;
    
    // In a real app, this would make an API call
    console.log(`Attaching files ${selectedFiles.join(', ')} to project ${projectId}`);
    
    // Update the local state to simulate the change
    setFiles(prev => 
      prev.map(file => 
        selectedFiles.includes(file.id) 
          ? { ...file, projectId } 
          : file
      )
    );
    
    // Clear selection
    setSelectedFiles([]);
  };

  // Handle retry processing for failed files
  const handleRetryProcessing = (fileId: string) => {
    // In a real app, this would trigger backend processing
    console.log(`Retrying processing for file ${fileId}`);
    
    // Update local state to simulate starting the process
    setFiles(prev => 
      prev.map(file => 
        file.id === fileId 
          ? { ...file, processed: false, processingFailed: false } 
          : file
      )
    );
    
    // Simulate successful processing after delay
    setTimeout(() => {
      setFiles(prev => 
        prev.map(file => 
          file.id === fileId 
            ? { ...file, processed: true, processingFailed: false, chunks: Math.floor(Math.random() * 30) + 1 } 
            : file
        )
      );
    }, 2000);
  };

  // Handle file deletion
  const handleDeleteFile = (fileId: string) => {
    // In a real app, this would make an API call
    console.log(`Deleting file ${fileId}`);
    
    // Update local state
    setFiles(prev => prev.filter(file => file.id !== fileId));
    setSelectedFiles(prev => prev.filter(id => id !== fileId));
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
          >
            Browse Files
          </button>
        </div>
      </div>
      
      {/* GPU Usage Indicator */}
      {gpuUsage > 0 && (
        <div className="bg-navy-light p-4 mb-4 rounded-lg">
          <div className="flex items-center">
            <div className="mr-3 text-gray-400">GPU Usage:</div>
            <div className="flex-1 bg-navy rounded-full h-2.5">
              <div 
                className="bg-gold h-2.5 rounded-full" 
                style={{ width: `${gpuUsage}%` }}
              ></div>
            </div>
            <div className="ml-3 text-gold">{gpuUsage}%</div>
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
        
        {getSortedFiles().length > 0 ? (
          <div className="space-y-2">
            {getSortedFiles().map(file => {
              const isLinked = file.projectId !== null;
              const linkedProjects = isLinked ? getLinkedProjects(file.id) : [];
              const searchRelevance = 'relevance' in file ? file.relevance : undefined;
              
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
                        {searchRelevance !== undefined && (
                          <span className="ml-2 text-xs px-1.5 py-0.5 bg-gold/20 text-gold rounded">
                            {searchRelevance}%
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
                        
                        {/* Linked projects */}
                        {isLinked && linkedProjects.length > 0 && (
                          <>
                            <span>•</span>
                            <div className="relative inline-block">
                              <button className="text-blue-400 hover:text-blue-300">
                                <span className="bg-blue-400 text-navy rounded-full w-5 h-5 inline-flex items-center justify-center">!</span>
                              </button>
                              <div className="hidden group-hover:block absolute z-10 w-48 bg-navy-lighter p-2 rounded shadow-lg text-xs">
                                <p className="font-bold mb-1">Linked Projects:</p>
                                <ul>
                                  {linkedProjects.map(project => (
                                    <li key={project.id} className="mb-1">
                                      <button 
                                        className="text-blue-400 hover:underline"
                                        onClick={() => onSelectProject && onSelectProject(project.id)}
                                      >
                                        {project.name}
                                      </button>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            </div>
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
                    
                    <button className="text-xs px-2 py-1 bg-navy-light hover:bg-navy rounded">
                      View
                    </button>
                    <button className="text-xs px-2 py-1 bg-navy-light hover:bg-navy rounded">
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
      
      {/* Mock Tag and Add File Modal - We would implement this fully in a real app */}
      {showAddTagModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-navy-light rounded-lg p-6 max-w-md w-full">
            <h3 className="text-lg font-medium text-gold mb-4">Tag and Add Files</h3>
            <p className="text-gray-400 mb-4">
              This is a placeholder for the Tag and Add File modal. In a real implementation, 
              this would allow adding file descriptions and initiating processing.
            </p>
            <div className="flex justify-end">
              <button 
                onClick={() => setShowAddTagModal(false)}
                className="px-3 py-1 bg-navy hover:bg-navy-lighter rounded text-sm mr-2"
              >
                Cancel
              </button>
              <button 
                onClick={() => setShowAddTagModal(false)}
                className="px-3 py-1 bg-gold text-navy font-medium rounded hover:bg-gold/90"
              >
                Process Files
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MainFileManager;