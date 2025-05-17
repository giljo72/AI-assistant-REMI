import React, { useState } from 'react';
import AddProjectModal from '../modals/AddProjectModal';
import { useProjects } from '../../context/ProjectContext';

// Props type for the sidebar
type ProjectSidebarProps = {
  onProjectSelect: (projectId: string) => void;
  onOpenMainFiles?: () => void; // Add prop for opening main file manager
};

const ProjectSidebar: React.FC<ProjectSidebarProps> = ({ onProjectSelect, onOpenMainFiles }) => {
  const [isProjectsExpanded, setIsProjectsExpanded] = useState(true);
  const [activeProjectId, setActiveProjectId] = useState<string>('');
  const [isAddProjectModalOpen, setIsAddProjectModalOpen] = useState(false);
  
  // Use the shared project context
  const { projects, loading, error, addProject } = useProjects();
  
  // Effect to set active project when projects change
  React.useEffect(() => {
    // Set active project ID to first project if we have projects and no active project
    if (projects.length > 0 && !activeProjectId) {
      setActiveProjectId(projects[0].id);
      onProjectSelect(projects[0].id);
    } else if (projects.length === 0) {
      // If no projects, clear active project
      setActiveProjectId('');
    }
  }, [projects, activeProjectId, onProjectSelect]);

  const handleAddProject = async (name: string, prompt: string) => {
    try {
      // Use the addProject method from context
      const newProject = await addProject(name, prompt || undefined);
      
      // Set this as the active project
      setActiveProjectId(newProject.id);
      onProjectSelect(newProject.id);
    } catch (err) {
      console.error("Error creating project:", err);
    }
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
          <button 
            className="p-2 hover:bg-navy-lighter rounded-full" 
            onClick={onOpenMainFiles}
            title="File Manager"
          >
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
              {loading ? (
                <div className="p-3 text-center text-gray-400">
                  <p>Loading projects...</p>
                </div>
              ) : error ? (
                <div className="p-3 text-center text-red-400">
                  <p>{error}</p>
                </div>
              ) : projects.length === 0 ? (
                <div className="p-3 text-center text-gray-400">
                  <p>No projects found</p>
                  <button
                    onClick={() => setIsAddProjectModalOpen(true)}
                    className="mt-2 px-3 py-1 bg-navy hover:bg-navy-lighter text-white rounded text-sm"
                  >
                    Create your first project
                  </button>
                </div>
              ) : (
                projects.map((project) => (
                  <div 
                    key={project.id} 
                    onClick={() => handleProjectSelect(project.id)}
                    className={`p-3 rounded cursor-pointer ${activeProjectId === project.id ? 'bg-navy text-gold font-bold' : 'hover:bg-navy-lighter'}`}
                  >
                    {project.name}
                  </div>
                ))
              )}
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