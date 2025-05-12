import React, { useState } from 'react';

type AddProjectModalProps = {
  isOpen: boolean;
  onClose: () => void;
  onAddProject: (name: string, prompt: string) => void;
};

const AddProjectModal: React.FC<AddProjectModalProps> = ({ 
  isOpen, 
  onClose, 
  onAddProject 
}) => {
  const [projectName, setProjectName] = useState('');
  const [projectPrompt, setProjectPrompt] = useState('');
  const [nameError, setNameError] = useState('');

  if (!isOpen) return null;

  const handleSubmit = () => {
    if (!projectName.trim()) {
      setNameError('Project name is required');
      return;
    }
    
    onAddProject(projectName, projectPrompt);
    setProjectName('');
    setProjectPrompt('');
    setNameError('');
    onClose();
  };

  const handleCancel = () => {
    // Ask user if they are sure
    if (projectName || projectPrompt) {
      if (window.confirm('Are you sure you want to cancel? Any changes will be lost.')) {
        setProjectName('');
        setProjectPrompt('');
        setNameError('');
        onClose();
      }
    } else {
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="bg-navy-light rounded-lg w-full max-w-md p-6">
        <h2 className="text-xl font-bold text-gold mb-4">Add New Project</h2>
        
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">
            Project Name <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={projectName}
            onChange={(e) => {
              setProjectName(e.target.value);
              if (e.target.value.trim()) setNameError('');
            }}
            className="w-full bg-navy p-2 rounded focus:outline-none focus:ring-1 focus:ring-gold"
            placeholder="Enter project name"
          />
          {nameError && <p className="text-red-500 text-xs mt-1">{nameError}</p>}
        </div>
        
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">
            Project Prompt
          </label>
          <textarea
            value={projectPrompt}
            onChange={(e) => setProjectPrompt(e.target.value)}
            className="w-full bg-navy p-2 rounded focus:outline-none focus:ring-1 focus:ring-gold min-h-[100px]"
            placeholder="Custom prompt for this project (optional)"
          />
          <p className="text-xs text-gray-400 mt-1">
            If no prompt is added, the indicator on main chat will show "Project Prompt Disabled"
          </p>
        </div>
        
        <div className="flex justify-end space-x-3">
          <button
            onClick={handleCancel}
            className="px-4 py-2 bg-navy hover:bg-navy-lighter rounded"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            className="px-4 py-2 bg-gold text-navy font-medium rounded hover:bg-gold/90"
          >
            Add Project
          </button>
        </div>
      </div>
    </div>
  );
};

export default AddProjectModal;