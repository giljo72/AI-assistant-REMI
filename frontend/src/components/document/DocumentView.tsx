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

// Import project service to fetch project data
import { projectService } from '../../services';

// Empty initial state for files - will be replaced with API call later
const initialFiles: File[] = [];

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
      // Fetch project data from API
      const fetchProjectName = async () => {
        try {
          const project = await projectService.getProject(projectId);
          setProjectName(project.name || '');
        } catch (err) {
          console.error('Error fetching project name:', err);
          setProjectName('Unknown Project');
        }
      };
      
      fetchProjectName();
      
      // TODO: Replace with API call to get files for this project
      // For now, use empty arrays
      setProjectFiles([]);
      
      // TODO: Replace with API call to get unattached files
      // For now, use empty arrays
      setUnattachedFiles([]);
    } else {
      // If no project is specified, show all files
      setProjectName('');
      setProjectFiles([]);
      setUnattachedFiles([]);
    }
    
    // TODO: Implement file fetching service
    console.log('Fetching files for project:', projectId);
  }, [projectId]);

  const handleFileFilter = (filter: string) => {
    setActiveFilter(filter);
  };

  const handleAttachFile = (fileId: string) => {
    // TODO: Implement API call to attach the file to the project
    console.log(`Attaching file ${fileId} to project ${projectId}`);
    
    // This is a placeholder for future implementation
    if (projectId) {
      console.log(`Will attach file ${fileId} to project ${projectId}`);
      // TODO: Update UI after API call succeeds
      // For now, do nothing to avoid errors
    }
  };

  const handleDetachFile = (fileId: string) => {
    // TODO: Implement API call to detach the file from the project
    console.log(`Detaching file ${fileId} from project ${projectId}`);
    
    // This is a placeholder for future implementation
    if (projectId) {
      console.log(`Will detach file ${fileId} from project ${projectId}`);
      // TODO: Update UI after API call succeeds
      // For now, do nothing to avoid errors
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
            {getFilteredFiles(projectId ? unattachedFiles : []).map(file => (
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
            
            {getFilteredFiles(projectId ? unattachedFiles : []).length === 0 && (
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