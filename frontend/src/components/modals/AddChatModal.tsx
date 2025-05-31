import React, { useState } from 'react';

type AddChatModalProps = {
  isOpen: boolean;
  onClose: () => void;
  onAddChat: (name: string) => void;
  projectName: string;
};

const AddChatModal: React.FC<AddChatModalProps> = ({ 
  isOpen, 
  onClose, 
  onAddChat,
  projectName
}) => {
  const [chatName, setChatName] = useState('');
  const [nameError, setNameError] = useState('');

  if (!isOpen) return null;

  const handleSubmit = () => {
    if (!chatName.trim()) {
      setNameError('Chat name is required');
      return;
    }
    
    onAddChat(chatName);
    setChatName('');
    setNameError('');
    onClose();
  };

  const handleCancel = () => {
    // Ask user if they are sure
    if (chatName) {
      if (window.confirm('Are you sure you want to cancel? Any changes will be lost.')) {
        setChatName('');
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
        <h2 className="text-xl font-bold text-gold mb-4">Add New Chat to {projectName}</h2>
        
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">
            Chat Name <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={chatName}
            onChange={(e) => {
              setChatName(e.target.value);
              if (e.target.value.trim()) setNameError('');
            }}
            className="w-full bg-navy p-2 rounded focus:outline-none focus:ring-1 focus:ring-gold"
            placeholder="Enter chat name"
          />
          {nameError && <p className="text-red-500 text-xs mt-1">{nameError}</p>}
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
            Add Chat
          </button>
        </div>
      </div>
    </div>
  );
};

export default AddChatModal;