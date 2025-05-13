import React, { useState } from 'react';

// Define types for our data
type File = {
  id: string;
  name: string;
  type: string;
  size: string;
  active: boolean;
  projectId: string | null; // null for unattached documents
  addedAt: string;
  processed: boolean; // Indicates if the file has been processed into vector DB
  processingFailed?: boolean; // If processing failed
  chunks?: number; // Number of chunks if processed
  relevance?: number; // Search relevance score (0-100)
};

// Get file type badge color
const getFileTypeColor = (type: string): string => {
  switch (type.toLowerCase()) {
    case 'pdf':
      return 'red';
    case 'docx':
    case 'doc':
      return 'blue';
    case 'xlsx':
    case 'xls':
      return 'green';
    case 'png':
    case 'jpg':
    case 'jpeg':
      return 'purple';
    case 'txt':
      return 'gray';
    default:
      return 'gray';
  }
};

type SearchFilesResultsProps = {
  searchResults: File[];
  projectId: string;
  onClose: () => void;
  onAttachFiles: (fileIds: string[]) => void;
};

const SearchFilesResults: React.FC<SearchFilesResultsProps> = ({ 
  searchResults, 
  projectId, 
  onClose, 
  onAttachFiles 
}) => {
  const [selectedFileIds, setSelectedFileIds] = useState<string[]>([]);
  const [sortField, setSortField] = useState<'relevance' | 'name' | 'date'>('relevance');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');

  // Handle selection/deselection of a file
  const toggleFileSelection = (fileId: string) => {
    setSelectedFileIds(prev => 
      prev.includes(fileId) 
        ? prev.filter(id => id !== fileId) 
        : [...prev, fileId]
    );
  };

  // Handle attaching selected files to the project
  const handleAttachFiles = () => {
    if (selectedFileIds.length === 0) return;
    onAttachFiles(selectedFileIds);
  };

  // Sort files based on current sort field and direction
  const sortedResults = [...searchResults].sort((a, b) => {
    if (sortField === 'relevance') {
      const aRelevance = a.relevance || 0;
      const bRelevance = b.relevance || 0;
      return sortDirection === 'asc' ? aRelevance - bRelevance : bRelevance - aRelevance;
    } else if (sortField === 'name') {
      return sortDirection === 'asc' 
        ? a.name.localeCompare(b.name) 
        : b.name.localeCompare(a.name);
    } else { // 'date'
      return sortDirection === 'asc' 
        ? a.addedAt.localeCompare(b.addedAt) 
        : b.addedAt.localeCompare(a.addedAt);
    }
  });

  // Handle sort field change
  const handleSortChange = (field: 'relevance' | 'name' | 'date') => {
    if (field === sortField) {
      setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc'); // Default to descending for new sort field
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="bg-navy-light p-4 mb-4 rounded-lg flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-gold">Search Results</h2>
          <p className="text-gray-400 text-sm">{searchResults.length} files found</p>
        </div>
        <div className="flex space-x-2">
          <button 
            onClick={onClose}
            className="px-3 py-1 bg-navy hover:bg-navy-lighter rounded text-sm"
          >
            Cancel
          </button>
        </div>
      </div>
      
      {/* Sort Controls */}
      <div className="bg-navy-light p-4 mb-4 rounded-lg flex justify-between items-center">
        <div className="flex space-x-3">
          <button 
            className={`px-3 py-1 rounded text-sm ${sortField === 'relevance' ? 'bg-gold/20 text-gold' : 'bg-navy hover:bg-navy-lighter'}`}
            onClick={() => handleSortChange('relevance')}
          >
            Relevance {sortField === 'relevance' && (sortDirection === 'asc' ? '↑' : '↓')}
          </button>
          <button 
            className={`px-3 py-1 rounded text-sm ${sortField === 'name' ? 'bg-gold/20 text-gold' : 'bg-navy hover:bg-navy-lighter'}`}
            onClick={() => handleSortChange('name')}
          >
            Name {sortField === 'name' && (sortDirection === 'asc' ? '↑' : '↓')}
          </button>
          <button 
            className={`px-3 py-1 rounded text-sm ${sortField === 'date' ? 'bg-gold/20 text-gold' : 'bg-navy hover:bg-navy-lighter'}`}
            onClick={() => handleSortChange('date')}
          >
            Date {sortField === 'date' && (sortDirection === 'asc' ? '↑' : '↓')}
          </button>
        </div>
        
        <button 
          onClick={handleAttachFiles}
          disabled={selectedFileIds.length === 0}
          className={`px-4 py-2 rounded font-medium ${
            selectedFileIds.length > 0 
              ? 'bg-gold text-navy hover:bg-gold/90' 
              : 'bg-navy-lighter text-gray-500 cursor-not-allowed'
          }`}
        >
          Attach Selected ({selectedFileIds.length})
        </button>
      </div>
      
      {/* Search Results List */}
      <div className="flex-1 bg-navy-light p-4 rounded-lg overflow-y-auto">
        {sortedResults.length > 0 ? (
          <div className="space-y-2">
            {sortedResults.map(file => (
              <div 
                key={file.id} 
                className={`p-3 rounded-lg flex items-center justify-between ${
                  selectedFileIds.includes(file.id) 
                    ? 'bg-navy-lighter border border-gold/30' 
                    : 'bg-navy hover:bg-navy-lighter'
                }`}
              >
                <div className="flex items-center">
                  {/* Checkbox for selection */}
                  <div className="mr-3">
                    <input
                      type="checkbox"
                      checked={selectedFileIds.includes(file.id)}
                      onChange={() => toggleFileSelection(file.id)}
                      className="w-4 h-4 accent-gold bg-navy border-gold/30 rounded focus:ring-gold"
                    />
                  </div>
                  
                  {/* File type icon */}
                  <div className={`w-10 h-10 bg-${getFileTypeColor(file.type)}-500/20 rounded flex items-center justify-center mr-3`}>
                    <span className={`text-${getFileTypeColor(file.type)}-400 text-xs`}>{file.type}</span>
                  </div>
                  
                  {/* File info */}
                  <div>
                    <h4 className="font-medium flex items-center">
                      {file.name}
                      {/* Relevance score */}
                      {file.relevance !== undefined && (
                        <span className="ml-2 text-xs px-1.5 py-0.5 bg-gold/20 text-gold rounded">
                          {file.relevance}%
                        </span>
                      )}
                    </h4>
                    <div className="flex text-xs text-gray-400 space-x-2">
                      <span>Added {file.addedAt}</span>
                      <span>•</span>
                      <span>{file.size}</span>
                      
                      {/* Processing status */}
                      {file.processed ? (
                        <>
                          <span>•</span>
                          <span className="text-green-400">Processed</span>
                          {file.chunks && (
                            <>
                              <span>•</span>
                              <span>{file.chunks} chunks</span>
                            </>
                          )}
                        </>
                      ) : file.processingFailed ? (
                        <>
                          <span>•</span>
                          <span className="text-red-400">Processing Failed</span>
                        </>
                      ) : (
                        <>
                          <span>•</span>
                          <span className="text-yellow-400">Processing...</span>
                        </>
                      )}
                      
                      {/* Project attachment status */}
                      {file.projectId === projectId ? (
                        <>
                          <span>•</span>
                          <span className="text-blue-400">Already Attached</span>
                        </>
                      ) : file.projectId !== null ? (
                        <>
                          <span>•</span>
                          <span className="text-purple-400">Attached to Another Project</span>
                        </>
                      ) : null}
                    </div>
                  </div>
                </div>
                
                {/* Preview button */}
                <button className="text-xs px-2 py-1 bg-navy-light hover:bg-navy rounded">
                  Preview
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-3 text-center text-gray-400">
            No search results found. Try a different search term.
          </div>
        )}
      </div>
      
      {/* Bottom action bar */}
      <div className="bg-navy-light p-4 mt-4 rounded-lg flex justify-between">
        <button 
          onClick={onClose}
          className="px-3 py-1 bg-navy hover:bg-navy-lighter rounded"
        >
          Cancel
        </button>
        
        <button 
          onClick={handleAttachFiles}
          disabled={selectedFileIds.length === 0}
          className={`px-4 py-2 rounded font-medium ${
            selectedFileIds.length > 0 
              ? 'bg-gold text-navy hover:bg-gold/90' 
              : 'bg-navy-lighter text-gray-500 cursor-not-allowed'
          }`}
        >
          Attach Selected ({selectedFileIds.length})
        </button>
      </div>
    </div>
  );
};

export default SearchFilesResults;