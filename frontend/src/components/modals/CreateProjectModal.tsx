import React, { useState } from 'react';
import { projectService } from '../../services';

type CreateProjectModalProps = {
  isOpen: boolean;
  onClose: () => void;
  onProjectCreated: (projectId: string) => void;
};

const CreateProjectModal: React.FC<CreateProjectModalProps> = ({
  isOpen,
  onClose,
  onProjectCreated
}) => {
  const [projectName, setProjectName] = useState('');
  const [projectDescription, setProjectDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!projectName.trim()) {
      setError('Project name is required');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const newProject = await projectService.createProject({
        name: projectName.trim(),
        description: projectDescription.trim() || undefined
      });
      
      // Clear form
      setProjectName('');
      setProjectDescription('');
      
      // Notify parent component
      onProjectCreated(newProject.id);
      
      // Close modal
      onClose();
    } catch (err) {
      console.error('Error creating project:', err);
      setError('Failed to create project. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
      <div className="bg-navy-light rounded-lg p-6 w-full max-w-md">
        <h2 className="text-xl font-bold text-gold mb-4">Create New Project</h2>
        
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label htmlFor="projectName" className="block text-sm font-medium mb-1">
              Project Name*
            </label>
            <input
              id="projectName"
              type="text"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              className="w-full bg-navy p-2 rounded focus:outline-none focus:ring-1 focus:ring-gold"
              placeholder="Enter project name"
              required
            />
          </div>
          
          <div className="mb-4">
            <label htmlFor="projectDescription" className="block text-sm font-medium mb-1">
              Description (optional)
            </label>
            <textarea
              id="projectDescription"
              value={projectDescription}
              onChange={(e) => setProjectDescription(e.target.value)}
              className="w-full bg-navy p-2 rounded focus:outline-none focus:ring-1 focus:ring-gold min-h-[100px]"
              placeholder="Enter project description"
            />
            <p className="text-xs text-gray-400 mt-1">
              Describe the purpose and scope of this project.
            </p>
          </div>
          
          {error && (
            <div className="mb-4 text-red-500 text-sm">
              {error}
            </div>
          )}
          
          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 bg-navy hover:bg-navy-lighter rounded"
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className={`px-4 py-2 bg-gold text-navy font-medium rounded hover:bg-gold/90 ${
                isSubmitting ? 'opacity-70 cursor-not-allowed' : ''
              }`}
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Creating...' : 'Create Project'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateProjectModal;