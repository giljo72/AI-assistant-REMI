import React, { useState, useEffect } from 'react';
import { projectService } from '../../services';
import { Project } from '../../services';

type ProjectListViewProps = {
  onSelectProject: (projectId: string) => void;
  onCreateProject: () => void;
};

const ProjectListView: React.FC<ProjectListViewProps> = ({ 
  onSelectProject, 
  onCreateProject 
}) => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProjects = async () => {
      setLoading(true);
      setError(null);
      try {
        const projectData = await projectService.getAllProjects();
        setProjects(projectData);
      } catch (err) {
        console.error("Error fetching projects:", err);
        setError("Failed to load projects. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    fetchProjects();
  }, []);

  return (
    <div className="h-full flex flex-col p-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-gold">All Projects</h2>
        <button 
          onClick={onCreateProject}
          className="px-3 py-1 bg-gold/20 hover:bg-gold/30 text-gold rounded text-sm flex items-center"
        >
          <span className="mr-1">+</span> Create Project
        </button>
      </div>

      {loading ? (
        <div className="flex-1 flex items-center justify-center">
          <p>Loading projects...</p>
        </div>
      ) : error ? (
        <div className="flex-1 flex items-center justify-center text-red-500">
          <p>{error}</p>
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto">
          {projects.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-gray-400">
              <p className="mb-2">No projects found</p>
              <button
                onClick={onCreateProject}
                className="px-3 py-1 bg-navy-light hover:bg-navy text-white rounded"
              >
                Create your first project
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {projects.map((project) => (
                <div
                  key={project.id}
                  className="bg-navy-light rounded-lg p-4 hover:bg-navy-lighter cursor-pointer transition-colors"
                  onClick={() => onSelectProject(project.id)}
                >
                  <h3 className="text-lg font-medium text-gold mb-2">{project.name}</h3>
                  {project.description && (
                    <p className="text-sm text-gray-300 mb-3 line-clamp-2">{project.description}</p>
                  )}
                  <div className="flex justify-between text-xs text-gray-400">
                    <span>{project.chat_count} chats</span>
                    <span>{project.document_count} documents</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ProjectListView;