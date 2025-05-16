import React, { useState } from 'react';

type DeleteProjectModalProps = {
  isOpen: boolean;
  onClose: () => void;
  onDelete: () => void;
  projectName: string;
};

const DeleteProjectModal: React.FC<DeleteProjectModalProps> = ({
  isOpen,
  onClose,
  onDelete,
  projectName,
}) => {
  const [isDeleting, setIsDeleting] = useState(false);

  if (!isOpen) return null;

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await onDelete();
      onClose();
    } catch (error) {
      console.error('Error deleting project:', error);
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="fixed inset-0 flex items-center justify-center z-50 bg-navy-darker bg-opacity-75">
      <div className="bg-navy-light p-6 rounded-lg shadow-lg max-w-md w-full">
        <h2 className="text-xl font-bold text-red-400 mb-4">Delete Project</h2>
        <p className="mb-6 text-gray-300">
          Are you sure you want to delete <span className="font-bold text-gold">{projectName}</span>?
          This action cannot be undone and will delete all associated chats and file attachments.
        </p>
        <div className="flex justify-end space-x-3">
          <button
            className="px-4 py-2 bg-navy hover:bg-navy-lighter rounded"
            onClick={onClose}
            disabled={isDeleting}
          >
            Cancel
          </button>
          <button
            className={`px-4 py-2 bg-red-700/60 hover:bg-red-700/80 text-white font-medium rounded ${
              isDeleting ? 'opacity-70 cursor-not-allowed' : ''
            }`}
            onClick={handleDelete}
            disabled={isDeleting}
          >
            {isDeleting ? 'Deleting...' : 'Delete Project'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default DeleteProjectModal;