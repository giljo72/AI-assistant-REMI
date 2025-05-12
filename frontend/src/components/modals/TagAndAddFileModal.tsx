import React, { useState } from 'react';

// Define types for our selected files
type SelectedFile = {
  id: string; // Temporary ID for UI purposes
  file: File; // Actual File object
  description: string; // User-provided description
};

type TagAndAddFileModalProps = {
  isOpen: boolean;
  onClose: () => void;
  onProcessFiles: (files: SelectedFile[]) => void;
};

const TagAndAddFileModal: React.FC<TagAndAddFileModalProps> = ({ 
  isOpen, 
  onClose, 
  onProcessFiles 
}) => {
  const [selectedFiles, setSelectedFiles] = useState<SelectedFile[]>([]);

  // Handle file selection from the file input
  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (!event.target.files?.length) return;
    
    // Convert FileList to array and add description field
    const newFiles: SelectedFile[] = Array.from(event.target.files).map(file => ({
      id: `temp-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      file,
      description: ''
    }));
    
    setSelectedFiles(prev => [...prev, ...newFiles]);
  };

  // Handle removal of a selected file
  const handleRemoveFile = (id: string) => {
    setSelectedFiles(prev => prev.filter(file => file.id !== id));
  };

  // Handle description change for a file
  const handleDescriptionChange = (id: string, description: string) => {
    setSelectedFiles(prev => 
      prev.map(file => 
        file.id === id ? { ...file, description } : file
      )
    );
  };

  // Handle form submission
  const handleSubmit = () => {
    onProcessFiles(selectedFiles);
    setSelectedFiles([]);
    onClose();
  };

  // Handle cancel
  const handleCancel = () => {
    if (selectedFiles.length > 0) {
      if (window.confirm('Are you sure you want to cancel? Any changes will be lost.')) {
        setSelectedFiles([]);
        onClose();
      }
    } else {
      onClose();
    }
  };

  // If modal is not open, don't render anything
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="bg-navy-light rounded-lg p-6 max-w-2xl w-full max-h-[80vh] flex flex-col">
        <h3 className="text-xl font-bold text-gold mb-4">Tag and Add Files</h3>
        
        {/* File input area - only show if no files are selected yet */}
        {selectedFiles.length === 0 && (
          <div className="border-2 border-dashed border-navy-lighter rounded-lg p-6 text-center mb-4">
            <div className="mb-4">
              <div className="mx-auto w-12 h-12 bg-navy-lighter rounded-full flex items-center justify-center">
                <span className="text-gold text-2xl">+</span>
              </div>
            </div>
            <p className="text-gray-400 mb-2">Select files to tag and add</p>
            <input
              type="file"
              multiple
              className="hidden"
              id="file-upload"
              onChange={handleFileSelect}
            />
            <label 
              htmlFor="file-upload"
              className="px-4 py-2 bg-gold text-navy font-medium rounded hover:bg-gold/90 cursor-pointer inline-block"
            >
              Browse Files
            </label>
          </div>
        )}
        
        {/* Selected files list */}
        {selectedFiles.length > 0 && (
          <div className="flex-1 overflow-y-auto mb-4">
            <div className="mb-3 flex justify-between items-center">
              <h4 className="font-medium text-white">Selected Files</h4>
              <label 
                htmlFor="file-upload-add"
                className="text-xs px-2 py-1 bg-navy hover:bg-navy-lighter rounded cursor-pointer text-gold"
              >
                + Add More
              </label>
              <input
                type="file"
                multiple
                className="hidden"
                id="file-upload-add"
                onChange={handleFileSelect}
              />
            </div>
            
            <div className="space-y-4">
              {selectedFiles.map(selectedFile => (
                <div key={selectedFile.id} className="p-3 bg-navy rounded-lg">
                  <div className="flex justify-between mb-2">
                    <span className="font-medium text-white">{selectedFile.file.name}</span>
                    <button 
                      onClick={() => handleRemoveFile(selectedFile.id)}
                      className="text-red-400 hover:text-red-300"
                      aria-label="Remove file"
                    >
                      ✕
                    </button>
                  </div>
                  <div className="text-xs text-gray-400 mb-2">
                    {(selectedFile.file.size / 1024).toFixed(1)} KB • {selectedFile.file.type || 'Unknown type'}
                  </div>
                  <div>
                    <label className="text-sm text-gray-300 block mb-1">Description (required):</label>
                    <textarea
                      className="w-full bg-navy-lighter p-2 rounded focus:outline-none focus:ring-1 focus:ring-gold text-sm text-white"
                      rows={2}
                      placeholder="Enter a description for this file..."
                      value={selectedFile.description}
                      onChange={(e) => handleDescriptionChange(selectedFile.id, e.target.value)}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {/* Action buttons */}
        <div className="flex justify-end space-x-3 mt-auto">
          <button 
            onClick={handleCancel}
            className="px-3 py-1 bg-navy hover:bg-navy-lighter rounded text-white"
          >
            Cancel
          </button>
          
          <button 
            onClick={handleSubmit}
            disabled={selectedFiles.length === 0 || selectedFiles.some(f => !f.description.trim())}
            className={`px-4 py-2 rounded font-medium ${
              selectedFiles.length > 0 && !selectedFiles.some(f => !f.description.trim())
                ? 'bg-gold text-navy hover:bg-gold/90' 
                : 'bg-navy-lighter text-gray-500 cursor-not-allowed'
            }`}
          >
            Process Files
          </button>
        </div>
      </div>
    </div>
  );
};

export default TagAndAddFileModal;