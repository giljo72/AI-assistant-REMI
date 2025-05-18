import React, { useState } from 'react';
import AddProjectModal from '../modals/AddProjectModal';
import { useProjects } from '../../context/ProjectContext';

// Props type for the sidebar
type ProjectSidebarProps = {
  onProjectSelect: (projectId: string) => void;
  onOpenMainFiles?: () => void; // Add prop for opening main file manager
  currentView?: string; // Current active view for highlighting
  forceMainFileView?: boolean; // Flag to force main file view
  setForceMainFileView?: (force: boolean) => void; // Function to set force flag
};

const ProjectSidebar: React.FC<ProjectSidebarProps> = ({ 
  onProjectSelect, 
  onOpenMainFiles, 
  currentView,
  forceMainFileView,
  setForceMainFileView 
}) => {
  const [isProjectsExpanded, setIsProjectsExpanded] = useState(true);
  const [activeProjectId, setActiveProjectId] = useState<string>('');
  const [isAddProjectModalOpen, setIsAddProjectModalOpen] = useState(false);
  
  // Use the shared project context
  const { projects, loading, error, addProject } = useProjects();
  
  // Effect to set active project when projects change
  React.useEffect(() => {
    // Check if current view is mainFiles
    if (currentView === 'mainFiles') {
      console.log("[SIDEBAR] In MainFileManager view - not auto-selecting a project");
      // Don't auto-select a project when in MainFileManager view
      return;
    }
    
    // Set active project ID to first project if we have projects and no active project
    if (projects.length > 0 && !activeProjectId) {
      console.log("[SIDEBAR] Auto-selecting first project");
      setActiveProjectId(projects[0].id);
      onProjectSelect(projects[0].id);
    } else if (projects.length === 0) {
      // If no projects, clear active project
      setActiveProjectId('');
    }
  }, [projects, activeProjectId, onProjectSelect, currentView]);

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
    // Only handle project selection if not in force MainFileManager mode
    if (forceMainFileView && setForceMainFileView) {
      console.log("[SIDEBAR] User selected a project while in forced MainFileManager view");
      console.log("[SIDEBAR] Clearing force flag and allowing project selection");
      
      // Do state updates in specific order to prevent race conditions
      
      // 1. First clear the force flag
      setForceMainFileView(false);
      
      // 2. Set project after a tiny delay
      setTimeout(() => {
        console.log("[SIDEBAR] Now setting project ID and view");
        setActiveProjectId(projectId);
        onProjectSelect(projectId);
      }, 10);
    } else {
      // Normal project selection behavior
      console.log("[SIDEBAR] Normal project selection:", projectId);
      setActiveProjectId(projectId);
      onProjectSelect(projectId); // Notify parent component
    }
  };

  return (
    <div className="h-full flex flex-col bg-navy-light text-white">
      <div className="p-3">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-xl font-bold text-gold">AI Assistant</h2>
        </div>
        
        <div className="mb-4 flex items-center space-x-1">
          <button 
            className={`p-2 ${currentView === 'mainFiles' ? 'bg-navy text-gold' : 'hover:bg-navy-lighter'} rounded-full`}
            onClick={(e) => {
              // Prevent event bubbling
              e.stopPropagation();
              e.preventDefault();
              
              // Open main files but also clear the active project to ensure global file upload works correctly
              if (onOpenMainFiles) {
                console.log("[SIDEBAR] File icon clicked - clearing active project and navigating to MainFileManager");
                
                // We need to clear the active project in ProjectSidebar
                setActiveProjectId('');
                
                // Then call the onOpenMainFiles function
                onOpenMainFiles();
              }
            }}
            onMouseDown={(e) => {
              // Also prevent mouse down events which might trigger other behavior
              e.stopPropagation();
              e.preventDefault();
            }}
            title="File Manager"
          >
            <span className={`${currentView === 'mainFiles' ? 'text-gold font-bold' : 'text-gold'}`}>📄</span>
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
                    className={`p-3 rounded cursor-pointer ${activeProjectId === project.id && currentView !== 'mainFiles' ? 'bg-navy text-gold font-bold' : 'hover:bg-navy-lighter'}`}
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