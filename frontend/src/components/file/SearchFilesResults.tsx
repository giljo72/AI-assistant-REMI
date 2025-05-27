import React, { useState } from 'react';
import { fileService } from '../../services';
import { FileSearchResult } from '../../services/fileService';
import { Icon } from '../common/Icon';

// Local interface for displayed files
interface LocalFile {
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
  contentSnippets?: string[]; // Text snippets with matching content
}

// File type metadata for improved visualization
interface FileTypeMetadata {
  color: string;
  icon: string;
  description: string;
}

// Get file type metadata for display
const getFileTypeMetadata = (type: string): FileTypeMetadata => {
  const fileType = type.toLowerCase();
  
  switch (fileType) {
    case 'pdf':
      return {
        color: 'red',
        icon: 'document',
        description: 'Adobe PDF Document'
      };
    case 'docx':
    case 'doc':
      return {
        color: 'blue',
        icon: 'document',
        description: 'Microsoft Word Document'
      };
    case 'xlsx':
    case 'xls':
      return {
        color: 'green',
        icon: 'table',
        description: 'Microsoft Excel Spreadsheet'
      };
    case 'pptx':
    case 'ppt':
      return {
        color: 'orange',
        icon: 'chart',
        description: 'Microsoft PowerPoint Presentation'
      };
    case 'png':
    case 'jpg':
    case 'jpeg':
    case 'gif':
    case 'bmp':
    case 'svg':
    case 'webp':
      return {
        color: 'purple',
        icon: 'image',
        description: 'Image File'
      };
    case 'txt':
      return {
        color: 'gray',
        icon: 'document',
        description: 'Text Document'
      };
    case 'md':
    case 'markdown':
      return {
        color: 'cyan',
        icon: 'document',
        description: 'Markdown Document'
      };
    case 'json':
    case 'xml':
    case 'yaml':
    case 'yml':
      return {
        color: 'yellow',
        icon: 'code',
        description: 'Data/Configuration File'
      };
    case 'csv':
      return {
        color: 'green',
        icon: 'table',
        description: 'Comma-Separated Values'
      };
    case 'zip':
    case 'rar':
    case '7z':
    case 'tar':
    case 'gz':
      return {
        color: 'amber',
        icon: 'download',
        description: 'Compressed Archive'
      };
    case 'html':
    case 'htm':
    case 'css':
    case 'js':
    case 'jsx':
    case 'ts':
    case 'tsx':
    case 'py':
    case 'java':
    case 'cpp':
    case 'c':
    case 'cs':
    case 'php':
    case 'rb':
    case 'go':
    case 'rs':
    case 'swift':
    case 'kt':
      return {
        color: 'indigo',
        icon: 'code',
        description: 'Source Code'
      };
    default:
      return {
        color: 'gray',
        icon: 'document',
        description: 'Document'
      };
  }
};

// Helper function to get just the color
const getFileTypeColor = (type: string): string => {
  return getFileTypeMetadata(type).color;
};

// Helper to format bytes to human-readable size
const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return bytes + ' B';
  const units = ['KB', 'MB', 'GB', 'TB'];
  let size = bytes / 1024;
  let unitIndex = 0;
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }
  
  return size.toFixed(1) + ' ' + units[unitIndex];
};

// Map API search result to local format
const mapSearchResultToLocal = (result: FileSearchResult): LocalFile => ({
  id: result.id,
  name: result.name,
  type: result.type.toUpperCase(),
  size: formatFileSize(result.size),
  active: result.active,
  projectId: result.project_id,
  addedAt: result.created_at.split('T')[0], // Format date
  processed: result.processed,
  processingFailed: result.processing_failed,
  chunks: result.chunk_count,
  relevance: result.relevance,
  contentSnippets: (result as any).content_snippets // Extract snippets if available
});

type SearchFilesResultsProps = {
  searchResults: FileSearchResult[];
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
  const [isAttaching, setIsAttaching] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Convert API search results to local format
  const localSearchResults = searchResults.map(mapSearchResultToLocal);

  // Handle selection/deselection of a file
  const toggleFileSelection = (fileId: string) => {
    setSelectedFileIds(prev => 
      prev.includes(fileId) 
        ? prev.filter(id => id !== fileId) 
        : [...prev, fileId]
    );
  };

  // Handle attaching selected files to the project
  const handleAttachFiles = async () => {
    if (selectedFileIds.length === 0) return;
    
    setIsAttaching(true);
    setError(null);
    
    try {
      // Call API to link files to project
      await fileService.linkFilesToProject({
        file_ids: selectedFileIds,
        project_id: projectId
      });
      
      // Call parent handler
      onAttachFiles(selectedFileIds);
    } catch (err) {
      console.error('Error attaching files to project:', err);
      setError('Failed to attach files to project. Please try again.');
    } finally {
      setIsAttaching(false);
    }
  };

  // Sort files based on current sort field and direction
  const sortedResults = [...localSearchResults].sort((a, b) => {
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
          disabled={selectedFileIds.length === 0 || isAttaching}
          className={`px-4 py-2 rounded font-medium ${
            selectedFileIds.length > 0 && !isAttaching
              ? 'bg-gold text-navy hover:bg-gold/90' 
              : 'bg-navy-lighter text-gray-500 cursor-not-allowed'
          }`}
        >
          {isAttaching 
            ? 'Attaching...' 
            : `Attach Selected (${selectedFileIds.length})`
          }
        </button>
      </div>
      
      {/* Error message if present */}
      {error && (
        <div className="bg-red-900/20 border border-red-700 text-red-400 p-3 mb-4 rounded-lg">
          {error}
        </div>
      )}
      
      {/* Search Results List */}
      <div className="flex-1 bg-navy-light p-4 rounded-lg overflow-y-auto">
        {sortedResults.length > 0 ? (
          <div className="space-y-4">
            {sortedResults.map(file => (
              <div 
                key={file.id} 
                className={`p-3 rounded-lg flex flex-col ${
                  selectedFileIds.includes(file.id) 
                    ? 'bg-navy-lighter border border-gold/30' 
                    : 'bg-navy hover:bg-navy-lighter'
                }`}
              >
                <div className="flex items-center justify-between">
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
                    <div className={`w-12 h-12 bg-${getFileTypeColor(file.type)}-500/20 rounded-lg flex flex-col items-center justify-center mr-3`}
                      title={getFileTypeMetadata(file.type).description}>
                      <Icon 
                        name={getFileTypeMetadata(file.type).icon as any} 
                        size={16} 
                        style={{ 
                          opacity: 0.5, 
                          filter: 'brightness(1.5)',
                          cursor: 'default'
                        }}
                      />
                      <span className={`text-${getFileTypeColor(file.type)}-400 text-xs mt-0.5 font-medium`}>{file.type.toUpperCase()}</span>
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
                      <div className="flex text-xs text-gray-400 space-x-2 flex-wrap">
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
                  <button 
                    onClick={() => window.open(`/api/files/${file.id}/preview`, '_blank')}
                    className="text-xs px-2 py-1 bg-navy-light hover:bg-navy rounded"
                  >
                    Preview
                  </button>
                </div>
                
                {/* Content snippets if available */}
                {file.contentSnippets && file.contentSnippets.length > 0 && (
                  <div className="mt-3 pl-10">
                    <div className="text-xs text-gold mb-1">Matching Content:</div>
                    <div className="bg-navy-darker p-2 rounded text-xs text-gray-300 max-h-28 overflow-y-auto">
                      {file.contentSnippets.map((snippet, idx) => (
                        <div key={idx} className="mb-1 last:mb-0">
                          "{snippet}"
                        </div>
                      ))}
                    </div>
                  </div>
                )}
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
          disabled={selectedFileIds.length === 0 || isAttaching}
          className={`px-4 py-2 rounded font-medium ${
            selectedFileIds.length > 0 && !isAttaching
              ? 'bg-gold text-navy hover:bg-gold/90' 
              : 'bg-navy-lighter text-gray-500 cursor-not-allowed'
          }`}
        >
          {isAttaching 
            ? 'Attaching...' 
            : `Attach Selected (${selectedFileIds.length})`
          }
        </button>
      </div>
    </div>
  );
};

export default SearchFilesResults;