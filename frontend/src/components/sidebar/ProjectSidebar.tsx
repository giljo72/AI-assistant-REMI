import React, { useState, useEffect } from 'react';
import AddProjectModal from '../modals/AddProjectModal';
import AdminSettingsPanel from '../modals/AdminSettingsPanel';
import ElegantSystemModelsPanel from '../modals/ElegantSystemModelsPanel';
import PersonalProfilesModal from '../modals/PersonalProfilesModal';
import UniversalSearchModal from '../layout/UniversalSearchModal';
import { useProjects } from '../../context/ProjectContext';
import { useNavigation } from '../../hooks/useNavigation';

const ProjectSidebar: React.FC = () => {
  const [isProjectsExpanded, setIsProjectsExpanded] = useState(true);
  const [isAddProjectModalOpen, setIsAddProjectModalOpen] = useState(false);
  const [isSettingsPanelOpen, setIsSettingsPanelOpen] = useState(false);
  const [isSystemPanelOpen, setIsSystemPanelOpen] = useState(false);
  const [isSearchModalOpen, setIsSearchModalOpen] = useState(false);
  const [isProfilesModalOpen, setIsProfilesModalOpen] = useState(false);
  
  // Use the shared project context
  const { projects, loading, error, addProject } = useProjects();
  
  // Use our navigation hook
  const navigation = useNavigation();
  
  // Effect to set active project when projects change
  useEffect(() => {
    // Only auto-select first project if we're not in mainFiles view and no project is selected
    if (navigation.activeView !== 'mainFiles' && 
        !navigation.activeProjectId && 
        projects.length > 0) {
      console.log("[SIDEBAR] Auto-selecting first project");
      navigation.navigateToProject(projects[0].id);
    }
  }, [projects, navigation.activeProjectId, navigation.activeView]);

  const handleAddProject = async (name: string, prompt: string) => {
    try {
      // Use the addProject method from context
      const newProject = await addProject(name, prompt || undefined);
      
      // Set this as the active project
      navigation.navigateToProject(newProject.id);
    } catch (err) {
      console.error("Error creating project:", err);
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
            className={`p-2 ${navigation.activeView === 'mainFiles' ? 'bg-navy text-gold' : 'hover:bg-navy-lighter'} rounded-full`}
            onClick={() => navigation.openMainFileManager()}
            title="File Manager"
          >
            <span className={`${navigation.activeView === 'mainFiles' ? 'text-gold font-bold' : 'text-gold'}`}>📄</span>
          </button>
          <button 
            className={`p-2 ${isSearchModalOpen ? 'bg-navy text-gold' : 'hover:bg-navy-lighter'} rounded-full`}
            onClick={() => setIsSearchModalOpen(true)}
            title="Universal Search"
          >
            <span className="text-gold">🔍</span>
          </button>
          <button 
            className={`p-2 ${isSystemPanelOpen ? 'bg-navy text-gold' : 'hover:bg-navy-lighter'} rounded-full`}
            onClick={() => setIsSystemPanelOpen(true)}
            title="System & Models"
          >
            <span className="text-gold">❓</span>
          </button>
          <button 
            className="p-2 hover:bg-navy-lighter rounded-full" 
            title="Personal Profiles"
            onClick={() => setIsProfilesModalOpen(true)}
          >
            <span className="text-gold">👤</span>
          </button>
          <button 
            className="p-2 hover:bg-navy-lighter rounded-full" 
            title="Admin Settings"
            onClick={() => setIsSettingsPanelOpen(true)}
          >
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
                    onClick={() => navigation.navigateToProject(project.id)}
                    className={`p-3 rounded cursor-pointer ${
                      navigation.activeProjectId === project.id && navigation.activeView !== 'mainFiles' 
                        ? 'bg-navy text-gold font-bold' 
                        : 'hover:bg-navy-lighter'
                    }`}
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
      
      {/* Admin Settings Panel */}
      <AdminSettingsPanel
        isOpen={isSettingsPanelOpen}
        onClose={() => setIsSettingsPanelOpen(false)}
      />
      
      {/* System & Models Panel */}
      <ElegantSystemModelsPanel 
        isOpen={isSystemPanelOpen} 
        onClose={() => setIsSystemPanelOpen(false)} 
      />
      
      {/* Universal Search Modal */}
      <UniversalSearchModal
        isOpen={isSearchModalOpen}
        onClose={() => setIsSearchModalOpen(false)}
      />
      
      {/* Personal Profiles Modal */}
      <PersonalProfilesModal
        isOpen={isProfilesModalOpen}
        onClose={() => setIsProfilesModalOpen(false)}
      />
    </div>
  );
};

export default ProjectSidebar;