import React, { useState } from 'react';
import AddProjectModal from '../modals/AddProjectModal';

// Define a type for our project data
type Project = {
  id: string;
  name: string;
  chatCount: number;
};

// Mock data for projects
const mockProjects: Project[] = [
  { id: '1', name: 'Research Paper', chatCount: 3 },
  { id: '2', name: 'Website Redesign', chatCount: 5 },
  { id: '3', name: 'Marketing Campaign', chatCount: 2 },
  { id: '4', name: 'Product Launch', chatCount: 1 },
];

// Props type for the sidebar
type ProjectSidebarProps = {
  onProjectSelect: (projectId: string) => void;
};

const ProjectSidebar: React.FC<ProjectSidebarProps> = ({ onProjectSelect }) => {
  const [isProjectsExpanded, setIsProjectsExpanded] = useState(true);
  const [activeProjectId, setActiveProjectId] = useState<string>('1'); // Default to first project
  const [isAddProjectModalOpen, setIsAddProjectModalOpen] = useState(false);
  const [projects, setProjects] = useState<Project[]>(mockProjects);

  const handleAddProject = (name: string, prompt: string) => {
    // In a real app, this would be an API call to create a project
    const newProject: Project = {
      id: (projects.length + 1).toString(),
      name,
      chatCount: 0,
    };
    setProjects([...projects, newProject]);
    setActiveProjectId(newProject.id);
    onProjectSelect(newProject.id); // Notify parent component
  };

  const handleProjectSelect = (projectId: string) => {
    setActiveProjectId(projectId);
    onProjectSelect(projectId); // Notify parent component
  };

  return (
    <div className="h-full flex flex-col bg-navy-light text-white">
      <div className="p-3">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-xl font-bold text-gold">AI Assistant</h2>
        </div>
        
        <div className="mb-4 flex items-center space-x-1">
          <button className="p-2 hover:bg-navy-lighter rounded-full">
            <span className="text-gold">📄</span>
          </button>
          <button className="p-2 hover:bg-navy-lighter rounded-full">
            <span className="text-gold">🔍</span>
          </button>
          <button className="p-2 hover:bg-navy-lighter rounded-full">
            <span className="text-gold">❓</span>
          </button>
          <button className="p-2 hover:bg-navy-lighter rounded-full">
            <span className="text-gold">⚙️</span>
          </button>
        </div>
        
        <button 
          onClick={() => setIsAddProjectModalOpen(true)} 
          className="w-full py-2 mb-4 flex items-center justify-center bg-gold/20 hover:bg-gold/30 text-gold font-medium rounded transition-colors"
        >
          <span className="mr-1">+</span> Add Project
        </button>
      </div>
      
      <div className="px-3 flex-1 overflow-y-auto">
        <div className="mb-2">
          <button 
            onClick={() => setIsProjectsExpanded(!isProjectsExpanded)}
            className="w-full py-2 px-3 flex justify-between items-center rounded hover:bg-navy-lighter"
          >
            <span className={`font-bold text-gold`}>PROJECTS</span>
            <span>{isProjectsExpanded ? '▼' : '▶'}</span>
          </button>
          
          {isProjectsExpanded && (
            <div className="mt-1 space-y-1">
              {projects.map((project) => (
                <div 
                  key={project.id} 
                  onClick={() => handleProjectSelect(project.id)}
                  className={`p-3 rounded cursor-pointer ${activeProjectId === project.id ? 'bg-navy text-gold font-bold' : 'hover:bg-navy-lighter'}`}
                >
                  {project.name}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Add Project Modal */}
      <AddProjectModal 
        isOpen={isAddProjectModalOpen}
        onClose={() => setIsAddProjectModalOpen(false)}
        onAddProject={handleAddProject}
      />
    </div>
  );
};

export default ProjectSidebar;