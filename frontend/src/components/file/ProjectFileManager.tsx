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
  chunks?: number; // Number of chunks if processed
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
  const [projectFiles, setProjectFiles] = useState<File[]>([]);
  const [projectName, setProjectName] = useState('');

  // Effect to get project name and files
  useEffect(() => {
    // Find the project name
    const project = mockProjects.find(p => p.id === projectId);
    setProjectName(project?.name || '');
    
    // Filter files for this project
    const filesForProject = mockFiles.filter(file => file.projectId === projectId);
    setProjectFiles(filesForProject);
  }, [projectId]);

  // Handle file activation toggle
  const handleToggleActive = (fileId: string) => {
    setProjectFiles(prevFiles => 
      prevFiles.map(file => 
        file.id === fileId ? { ...file, active: !file.active } : file
      )
    );
  };

  // Handle file detachment
  const handleDetachFile = (fileId: string) => {
    setProjectFiles(prevFiles => prevFiles.filter(file => file.id !== fileId));
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="bg-navy-light p-4 mb-4 rounded-lg flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-gold">Project File Manager</h2>
          <p className="text-gray-400 text-sm">Project: {projectName}</p>
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
          <button className="px-4 py-2 bg-gold text-navy font-medium rounded hover:bg-gold/90">
            Browse Files
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
        
        {projectFiles.length > 0 ? (
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
                      {file.processed && (
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
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex space-x-2 items-center">
                  <div className="flex items-center mr-2">
                    <label className="inline-flex items-center cursor-pointer">
                      <input 
                        type="checkbox" 
                        checked={file.active}
                        onChange={() => handleToggleActive(file.id)}
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
          <div className="p-3 text-center text-gray-400">
            No files attached to this project yet. Use the controls above to add files.
          </div>
        )}
      </div>
    </div>
  );
};

export default ProjectFileManager;