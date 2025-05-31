import React, { createContext, useState, useEffect, useContext, ReactNode } from 'react';
import { projectService, Project } from '../services';

interface ProjectContextType {
  projects: Project[];
  loading: boolean;
  error: string | null;
  refreshProjects: () => Promise<void>;
  addProject: (name: string, description?: string) => Promise<Project>;
  deleteProject: (id: string) => Promise<void>;
}

const ProjectContext = createContext<ProjectContextType | undefined>(undefined);

export const ProjectProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refreshProjects = async () => {
    setLoading(true);
    setError(null);
    try {
      const projectData = await projectService.getAllProjects();
      setProjects(projectData);
      return projectData;
    } catch (err) {
      console.error("Error fetching projects:", err);
      setError("Failed to load projects");
      return [];
    } finally {
      setLoading(false);
    }
  };

  const addProject = async (name: string, description?: string): Promise<Project> => {
    try {
      const newProject = await projectService.createProject({
        name,
        description
      });
      
      // Update local state with new project
      setProjects(prev => [...prev, newProject]);
      return newProject;
    } catch (err) {
      console.error("Error creating project:", err);
      throw err;
    }
  };

  const deleteProject = async (id: string): Promise<void> => {
    try {
      await projectService.deleteProject(id);
      
      // Update local state by removing the deleted project
      setProjects(prev => prev.filter(p => p.id !== id));
    } catch (err) {
      console.error("Error deleting project:", err);
      throw err;
    }
  };

  useEffect(() => {
    refreshProjects();
  }, []);

  return (
    <ProjectContext.Provider 
      value={{ 
        projects, 
        loading, 
        error, 
        refreshProjects, 
        addProject, 
        deleteProject 
      }}
    >
      {children}
    </ProjectContext.Provider>
  );
};

export const useProjects = () => {
  const context = useContext(ProjectContext);
  if (context === undefined) {
    throw new Error('useProjects must be used within a ProjectProvider');
  }
  return context;
};