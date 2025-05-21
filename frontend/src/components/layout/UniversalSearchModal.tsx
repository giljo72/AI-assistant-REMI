import React, { useState } from 'react';

interface SearchFilters {
  chats: boolean;
  knowledgeBase: boolean;
  documents: boolean;
}

interface KnowledgeResult {
  id: string;
  documentName: string;
  snippet: string;
  contextBefore: string;
  contextAfter: string;
  probability: number;
  documentId: string;
  downloadUrl: string;
}

interface ChatResult {
  id: string;
  chatName: string;
  projectName: string;
  messageSnippet: string;
  probability: number;
  chatId: string;
  projectId: string;
}

interface DocumentResult {
  id: string;
  fileName: string;
  description: string;
  probability: number;
  documentId: string;
  downloadUrl: string;
}

interface UniversalSearchModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const UniversalSearchModal: React.FC<UniversalSearchModalProps> = ({ isOpen, onClose }) => {
  const [query, setQuery] = useState('');
  const [filters, setFilters] = useState<SearchFilters>({
    chats: true,
    knowledgeBase: true,
    documents: true
  });
  const [isSearching, setIsSearching] = useState(false);
  const [knowledgeResults, setKnowledgeResults] = useState<KnowledgeResult[]>([]);
  const [chatResults, setChatResults] = useState<ChatResult[]>([]);
  const [documentResults, setDocumentResults] = useState<DocumentResult[]>([]);
  const [expandedKnowledge, setExpandedKnowledge] = useState<Set<string>>(new Set());

  const handleFilterChange = (filter: keyof SearchFilters) => {
    setFilters(prev => ({
      ...prev,
      [filter]: !prev[filter]
    }));
  };

  const handleSearch = async () => {
    if (!query.trim()) return;
    
    setIsSearching(true);
    try {
      // TODO: Implement actual search API calls based on filters
      // For now, mock the search
      
      if (filters.knowledgeBase) {
        // Mock knowledge base results
        const mockKnowledgeResults: KnowledgeResult[] = [
          {
            id: '1',
            documentName: 'Project_Requirements.pdf',
            snippet: 'The system must support real-time document processing with vector embeddings for semantic search capabilities.',
            contextBefore: 'Based on the technical specifications outlined in section 3.2,',
            contextAfter: 'This ensures that users can quickly locate relevant information across large document collections.',
            probability: 89,
            documentId: 'doc-123',
            downloadUrl: '/api/documents/doc-123/download'
          }
        ];
        setKnowledgeResults(mockKnowledgeResults);
      }
      
      if (filters.chats) {
        // Mock chat results
        const mockChatResults: ChatResult[] = [
          {
            id: '1',
            chatName: 'Architecture Discussion',
            projectName: 'AI Assistant',
            messageSnippet: 'We need to implement vector search for document retrieval...',
            probability: 76,
            chatId: 'chat-456',
            projectId: 'proj-789'
          }
        ];
        setChatResults(mockChatResults);
      }
      
      if (filters.documents) {
        // Mock document results
        const mockDocumentResults: DocumentResult[] = [
          {
            id: '1',
            fileName: 'system_architecture.docx',
            description: 'System architecture documentation',
            probability: 82,
            documentId: 'doc-456',
            downloadUrl: '/api/documents/doc-456/download'
          }
        ];
        setDocumentResults(mockDocumentResults);
      }
      
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setIsSearching(false);
    }
  };

  const toggleKnowledgeExpansion = (resultId: string) => {
    setExpandedKnowledge(prev => {
      const newSet = new Set(prev);
      if (newSet.has(resultId)) {
        newSet.delete(resultId);
      } else {
        newSet.add(resultId);
      }
      return newSet;
    });
  };

  const handleDownload = async (url: string, fileName: string) => {
    try {
      const response = await fetch(url);
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = fileName;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(downloadUrl);
    } catch (error) {
      console.error('Download error:', error);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-navy w-full max-w-4xl h-5/6 rounded-lg flex flex-col">
        {/* Header */}
        <div className="bg-navy-light p-4 rounded-t-lg border-b border-gold">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-bold text-gold">Universal Search</h2>
            <button 
              onClick={onClose}
              className="text-gray-400 hover:text-white"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Search Form */}
        <div className="p-4 border-b border-navy-lighter">
          <div className="flex flex-col space-y-4">
            {/* Query Input */}
            <div>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Enter your search query..."
                className="w-full px-4 py-2 bg-navy-lighter border border-gold/30 rounded text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-gold"
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
            </div>

            {/* Search Filters */}
            <div className="flex items-center space-x-6">
              <span className="text-gray-300 font-medium">Search in:</span>
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={filters.chats}
                  onChange={() => handleFilterChange('chats')}
                  className="w-4 h-4 accent-gold"
                />
                <span className="text-white">Chats</span>
              </label>
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={filters.knowledgeBase}
                  onChange={() => handleFilterChange('knowledgeBase')}
                  className="w-4 h-4 accent-gold"
                />
                <span className="text-white">Knowledge Base</span>
              </label>
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={filters.documents}
                  onChange={() => handleFilterChange('documents')}
                  className="w-4 h-4 accent-gold"
                />
                <span className="text-white">Documents</span>
              </label>
            </div>

            {/* Search Button */}
            <div>
              <button
                onClick={handleSearch}
                disabled={!query.trim() || isSearching}
                className={`px-6 py-2 rounded font-medium ${
                  query.trim() && !isSearching
                    ? 'bg-gold text-navy hover:bg-gold/90'
                    : 'bg-navy-lighter text-gray-500 cursor-not-allowed'
                }`}
              >
                {isSearching ? 'Searching...' : 'Search'}
              </button>
            </div>
          </div>
        </div>

        {/* Results */}
        <div className="flex-1 overflow-y-auto p-4">
          {/* Knowledge Base Results */}
          {filters.knowledgeBase && knowledgeResults.length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-bold text-gold mb-3">Knowledge Base Results</h3>
              <div className="space-y-3">
                {knowledgeResults.map((result) => (
                  <div key={result.id} className="bg-navy-light p-4 rounded-lg">
                    <div className="flex justify-between items-start mb-2">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="text-gold font-medium">📄 {result.documentName}</span>
                          <span className="text-xs px-2 py-1 bg-gold/20 text-gold rounded">
                            {result.probability}% match
                          </span>
                        </div>
                        <div className="text-white">
                          <span className="text-gray-400">{result.contextBefore}</span>
                          <span className="bg-gold/20 px-1 rounded">{result.snippet}</span>
                          <span className="text-gray-400">{result.contextAfter}</span>
                        </div>
                      </div>
                    </div>
                    
                    {expandedKnowledge.has(result.id) && (
                      <div className="mt-3 p-3 bg-navy rounded text-gray-300 text-sm">
                        <p>Extended context would be displayed here...</p>
                      </div>
                    )}
                    
                    <div className="flex space-x-2 mt-3">
                      <button
                        onClick={() => toggleKnowledgeExpansion(result.id)}
                        className="px-3 py-1 bg-navy hover:bg-navy-lighter rounded text-sm text-gray-300"
                      >
                        {expandedKnowledge.has(result.id) ? 'Collapse' : 'Expand Context'}
                      </button>
                      <button
                        onClick={() => handleDownload(result.downloadUrl, result.documentName)}
                        className="px-3 py-1 bg-gold/20 hover:bg-gold/30 rounded text-sm text-gold"
                      >
                        ⬇️ Download Document
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Chat Results */}
          {filters.chats && chatResults.length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-bold text-gold mb-3">Chat Results</h3>
              <div className="space-y-3">
                {chatResults.map((result) => (
                  <div key={result.id} className="bg-navy-light p-4 rounded-lg">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="text-gold font-medium">💬 {result.chatName}</span>
                          <span className="text-xs px-2 py-1 bg-blue-500/20 text-blue-400 rounded">
                            {result.projectName}
                          </span>
                          <span className="text-xs px-2 py-1 bg-gold/20 text-gold rounded">
                            {result.probability}% match
                          </span>
                        </div>
                        <div className="text-gray-300 text-sm">
                          "{result.messageSnippet}"
                        </div>
                      </div>
                      <button
                        onClick={() => {/* TODO: Navigate to chat */}}
                        className="px-3 py-1 bg-blue-500/20 hover:bg-blue-500/30 rounded text-sm text-blue-400"
                      >
                        Open Chat
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Document Results */}
          {filters.documents && documentResults.length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-bold text-gold mb-3">Document Results</h3>
              <div className="space-y-3">
                {documentResults.map((result) => (
                  <div key={result.id} className="bg-navy-light p-4 rounded-lg">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="text-gold font-medium">📄 {result.fileName}</span>
                          <span className="text-xs px-2 py-1 bg-gold/20 text-gold rounded">
                            {result.probability}% match
                          </span>
                        </div>
                        <div className="text-gray-300 text-sm">
                          {result.description}
                        </div>
                      </div>
                      <div className="flex space-x-2">
                        <button
                          onClick={() => {/* TODO: Navigate to document */}}
                          className="px-3 py-1 bg-purple-500/20 hover:bg-purple-500/30 rounded text-sm text-purple-400"
                        >
                          View
                        </button>
                        <button
                          onClick={() => handleDownload(result.downloadUrl, result.fileName)}
                          className="px-3 py-1 bg-gold/20 hover:bg-gold/30 rounded text-sm text-gold"
                        >
                          ⬇️ Download
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* No Results */}
          {!isSearching && query && (
            knowledgeResults.length === 0 && 
            chatResults.length === 0 && 
            documentResults.length === 0
          ) && (
            <div className="text-center text-gray-400 mt-8">
              <p>No results found for "{query}"</p>
              <p className="text-sm mt-2">Try adjusting your search terms or filters.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default UniversalSearchModal;