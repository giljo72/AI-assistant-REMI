import React, { useState, useEffect } from 'react';
import AddProjectModal from '../modals/AddProjectModal';
import AdminSettingsPanel from '../modals/AdminSettingsPanel';
import UniversalSearchModal from '../layout/UniversalSearchModal';
import PersonalProfilesModal from '../modals/PersonalProfilesModal';
import { useProjects } from '../../context/ProjectContext';
import { useNavigation } from '../../hooks/useNavigation';
import { Icon } from '../common/Icon';

const ProjectSidebar: React.FC = () => {
  const [isProjectsExpanded, setIsProjectsExpanded] = useState(true);
  const [isAddProjectModalOpen, setIsAddProjectModalOpen] = useState(false);
  const [isSettingsPanelOpen, setIsSettingsPanelOpen] = useState(false);
  const [isSearchModalOpen, setIsSearchModalOpen] = useState(false);
  const [isContactsOpen, setIsContactsOpen] = useState(false);
  
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
        
        <div className="mb-4 flex justify-center">
          <div className="flex items-center space-x-2">
            <button 
              className={`p-3 ${navigation.activeView === 'mainFiles' ? 'bg-navy text-gold' : 'hover:bg-navy-lighter'} rounded-full flex items-center justify-center`}
              onClick={() => navigation.openMainFileManager()}
              title="File Manager"
            >
              <Icon name="file" size={30} style={{ color: '#d4af37' }} />
            </button>
            <button 
              className={`p-3 ${isSearchModalOpen ? 'bg-navy text-gold' : 'hover:bg-navy-lighter'} rounded-full flex items-center justify-center`}
              onClick={() => setIsSearchModalOpen(true)}
              title="Universal Search"
            >
              <Icon name="search" size={30} style={{ color: '#d4af37' }} />
            </button>
            <button 
              className={`p-3 ${isContactsOpen ? 'bg-navy text-gold' : 'hover:bg-navy-lighter'} rounded-full flex items-center justify-center`}
              onClick={() => setIsContactsOpen(true)}
              title="Contacts"
            >
              <Icon name="users" size={30} style={{ color: '#d4af37' }} />
            </button>
            <button 
              className="p-3 hover:bg-navy-lighter rounded-full flex items-center justify-center" 
              title="System Administration"
              onClick={() => setIsSettingsPanelOpen(true)}
            >
              <Icon name="settings" size={30} style={{ color: '#d4af37' }} />
            </button>
          </div>
        </div>
        
        <button 
          onClick={() => setIsAddProjectModalOpen(true)} 
          className="w-full py-2 mb-4 flex items-center justify-center bg-gold/20 hover:bg-gold/30 text-gold font-medium rounded transition-colors"
        >
          <Icon name="add" size={16} className="mr-1" />
          Add Project
        </button>
      </div>
      
      <div className="px-3 flex-1 overflow-y-auto">
        <div className="mb-2">
          <button 
            onClick={() => setIsProjectsExpanded(!isProjectsExpanded)}
            className="w-full py-2 px-3 flex justify-between items-center rounded hover:bg-navy-lighter"
          >
            <span className={`font-bold text-gold`}>PROJECTS</span>
            <Icon 
              name={isProjectsExpanded ? 'dropdownOpen' : 'dropdownClose'} 
              size={16} 
              style={{ color: '#ffffff' }} 
            />
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
      
      
      {/* Universal Search Modal */}
      <UniversalSearchModal
        isOpen={isSearchModalOpen}
        onClose={() => setIsSearchModalOpen(false)}
      />
      
      {/* Contacts Modal */}
      <PersonalProfilesModal
        open={isContactsOpen}
        onClose={() => setIsContactsOpen(false)}
      />
      
    </div>
  );
};

export default ProjectSidebar;