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
  { id: '1', name: 'Research Paper.pdf', type: 'PDF', size: '1.2 MB', active: true, projectId: '1', addedAt: '2025-05-10' },
  { id: '2', name: 'Literature Notes.docx', type: 'DOCX', size: '538 KB', active: true, projectId: '1', addedAt: '2025-05-09' },
  { id: '3', name: 'Data Analysis.xlsx', type: 'XLSX', size: '724 KB', active: false, projectId: '1', addedAt: '2025-05-08' },
  { id: '4', name: 'Website Mockup.png', type: 'PNG', size: '2.4 MB', active: true, projectId: '2', addedAt: '2025-05-07' },
  { id: '5', name: 'Campaign Brief.pdf', type: 'PDF', size: '890 KB', active: true, projectId: '3', addedAt: '2025-05-06' },
  { id: '6', name: 'Reference Paper.pdf', type: 'PDF', size: '1.7 MB', active: true, projectId: null, addedAt: '2025-05-05' },
  { id: '7', name: 'General Notes.txt', type: 'TXT', size: '45 KB', active: true, projectId: null, addedAt: '2025-05-04' },
  { id: '8', name: 'Template.docx', type: 'DOCX', size: '230 KB', active: true, projectId: null, addedAt: '2025-05-03' },
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

type DocumentViewProps = {
  projectId?: string;
};

const DocumentView: React.FC<DocumentViewProps> = ({ projectId }) => {
  const [activeFilter, setActiveFilter] = useState('all');
  const [projectFiles, setProjectFiles] = useState<File[]>([]);
  const [unattachedFiles, setUnattachedFiles] = useState<File[]>([]);
  const [projectName, setProjectName] = useState('');
  const [showAttachModal, setShowAttachModal] = useState(false);

  // Effect to filter files by project when projectId changes
  useEffect(() => {
    if (projectId) {
      // Find the project name
      const project = mockProjects.find(p => p.id === projectId);
      setProjectName(project?.name || '');
      
      // Filter files for this project
      const filesForProject = mockFiles.filter(file => file.projectId === projectId);
      setProjectFiles(filesForProject);
      
      // Get unattached files (that can be attached to this project)
      const unattached = mockFiles.filter(file => file.projectId === null);
      setUnattachedFiles(unattached);
    } else {
      // If no project is specified, show all files
      setProjectName('');
      setProjectFiles([]);
      setUnattachedFiles(mockFiles);
    }
  }, [projectId]);

  const handleFileFilter = (filter: string) => {
    setActiveFilter(filter);
  };

  const handleAttachFile = (fileId: string) => {
    // In a real app, this would make an API call to attach the file to the project
    console.log(`Attaching file ${fileId} to project ${projectId}`);
    
    // For now, simulate updating the UI
    const updatedUnattachedFiles = unattachedFiles.filter(file => file.id !== fileId);
    const fileToAttach = unattachedFiles.find(file => file.id === fileId);
    
    if (fileToAttach && projectId) {
      const attachedFile = { ...fileToAttach, projectId };
      setProjectFiles([...projectFiles, attachedFile]);
      setUnattachedFiles(updatedUnattachedFiles);
    }
  };

  const handleDetachFile = (fileId: string) => {
    // In a real app, this would make an API call to detach the file from the project
    console.log(`Detaching file ${fileId} from project ${projectId}`);
    
    // For now, simulate updating the UI
    const fileToDetach = projectFiles.find(file => file.id === fileId);
    const updatedProjectFiles = projectFiles.filter(file => file.id !== fileId);
    
    if (fileToDetach) {
      const detachedFile = { ...fileToDetach, projectId: null };
      setUnattachedFiles([...unattachedFiles, detachedFile]);
      setProjectFiles(updatedProjectFiles);
    }
  };

  // Filter files based on active filter
  const getFilteredFiles = (files: File[]): File[] => {
    if (activeFilter === 'all') return files;
    return files.filter(file => file.type.toLowerCase() === activeFilter.toLowerCase());
  };

  return (
    <div className="h-full flex flex-col">
      <div className="bg-navy-light p-4 mb-4 rounded-lg flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-gold">Document Management</h2>
          {projectId && <p className="text-gray-400 text-sm">Project: {projectName}</p>}
        </div>
        <div>
          <button className="px-4 py-2 bg-gold text-navy font-medium rounded hover:bg-gold/90 flex items-center">
            <span className="mr-1">+</span> Upload Document
          </button>
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto">
        {/* Recently Uploaded / All Documents */}
        <div className="bg-navy-light rounded-lg p-4 mb-4">
          <div className="flex items-center justify-between mb-3 pb-2 border-b border-navy">
            <h3 className="text-lg font-medium text-gold">{projectId ? 'All Documents' : 'Recently Uploaded'}</h3>
            <select 
              className="bg-navy text-white p-1 rounded text-sm"
              value={activeFilter}
              onChange={(e) => handleFileFilter(e.target.value)}
            >
              <option value="all">All Documents</option>
              <option value="pdf">PDFs</option>
              <option value="docx">Word Documents</option>
              <option value="xlsx">Spreadsheets</option>
              <option value="txt">Text Files</option>
            </select>
          </div>
          
          <div className="space-y-2">
            {getFilteredFiles(projectId ? unattachedFiles : mockFiles).map(file => (
              <div key={file.id} className="p-3 bg-navy hover:bg-navy-lighter rounded-lg flex items-center justify-between group">
                <div className="flex items-center">
                  <div className={`w-8 h-8 bg-${getFileTypeColor(file.type)}-500/20 rounded flex items-center justify-center mr-3`}>
                    <span className={`text-${getFileTypeColor(file.type)}-400 text-xs`}>{file.type}</span>
                  </div>
                  <div>
                    <h4 className="font-medium group-hover:text-gold">{file.name}</h4>
                    <p className="text-xs text-gray-400">Added {file.addedAt} • {file.size}</p>
                  </div>
                </div>
                <div className="flex space-x-2">
                  <button className="text-xs px-2 py-1 bg-navy-light hover:bg-navy rounded">
                    View
                  </button>
                  {projectId && file.projectId === null && (
                    <button 
                      className="text-xs px-2 py-1 bg-navy-light hover:bg-navy rounded"
                      onClick={() => handleAttachFile(file.id)}
                    >
                      Attach
                    </button>
                  )}
                </div>
              </div>
            ))}
            
            {getFilteredFiles(projectId ? unattachedFiles : mockFiles).length === 0 && (
              <div className="p-3 text-center text-gray-400">
                No documents found with the selected filter.
              </div>
            )}
          </div>
        </div>
        
        {/* Project Attachments section - only show when a project is selected */}
        {projectId && (
          <div className="bg-navy-light rounded-lg p-4">
            <h3 className="text-lg font-medium text-gold mb-3 pb-2 border-b border-navy">Project Attachments</h3>
            
            {projectFiles.length > 0 ? (
              <div className="space-y-2">
                {projectFiles.map(file => (
                  <div key={file.id} className="p-3 bg-navy hover:bg-navy-lighter rounded-lg flex items-center justify-between group">
                    <div className="flex items-center">
                      <div className={`w-8 h-8 bg-${getFileTypeColor(file.type)}-500/20 rounded flex items-center justify-center mr-3`}>
                        <span className={`text-${getFileTypeColor(file.type)}-400 text-xs`}>{file.type}</span>
                      </div>
                      <div>
                        <h4 className="font-medium group-hover:text-gold">{file.name}</h4>
                        <p className="text-xs text-gray-400">Added {file.addedAt} • {file.size}</p>
                      </div>
                    </div>
                    <div className="flex space-x-2 items-center">
                      <div className="flex items-center mr-2">
                        <label className="inline-flex items-center cursor-pointer">
                          <input 
                            type="checkbox" 
                            checked={file.active}
                            className="sr-only peer"
                          />
                          <div className={`w-9 h-5 rounded-full peer ${file.active ? 'bg-gold/40' : 'bg-navy-lighter'} peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all relative`}></div>
                        </label>
                      </div>
                      <button className="text-xs px-2 py-1 bg-navy-light hover:bg-navy rounded">
                        View
                      </button>
                      <button className="text-xs px-2 py-1 bg-navy-light hover:bg-navy rounded">
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
              <div className="p-3 bg-navy rounded-lg">
                <p className="text-center text-gray-400">
                  No documents attached to the current project.
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentView;