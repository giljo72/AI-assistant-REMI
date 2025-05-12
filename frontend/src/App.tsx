// eslint-disable-next-line @typescript-eslint/no-unused-vars
import React, { useState } from 'react';
import MainLayout from './components/layout/MainLayout';
import ProjectManagerView from './components/project/ProjectManagerView';
import ChatView from './components/chat/ChatView';
import DocumentView from './components/document/DocumentView';
import ProjectFileManager from './components/file/ProjectFileManager';
import MainFileManager from './components/file/MainFileManager';
import SearchFilesResults from './components/file/SearchFilesResults';
import TagAndAddFileModal from './components/modals/TagAndAddFileModal';


// Define the possible view types
type View = 'project' | 'chat' | 'document' | 'projectFiles' | 'mainFiles' | 'searchResults';

function App() {
  // State for active project and view
  const [activeProjectId, setActiveProjectId] = useState<string>('1');
  const [activeChatId, setActiveChatId] = useState<string | null>(null);
  const [activeView, setActiveView] = useState<View>('project');
  
  // State for file search and upload
  const [isTagAndAddModalOpen, setIsTagAndAddModalOpen] = useState(false);
  const [searchResults, setSearchResults] = useState<any[]>([]);
  
  // Mock data for testing
  const mockSearchResults = [
    { id: '6', name: 'Reference Paper.pdf', type: 'PDF', size: '1.7 MB', active: true, projectId: null, addedAt: '2025-05-05', processed: true, chunks: 32, relevance: 95 },
    { id: '7', name: 'General Notes.txt', type: 'TXT', size: '45 KB', active: true, projectId: null, addedAt: '2025-05-04', processed: true, chunks: 5, relevance: 82 },
    { id: '8', name: 'Template.docx', type: 'DOCX', size: '230 KB', active: true, projectId: null, addedAt: '2025-05-03', processed: true, chunks: 7, relevance: 75 },
  ];

  // Handle project selection from sidebar
  const handleProjectSelect = (projectId: string) => {
    setActiveProjectId(projectId);
    setActiveChatId(null);
    setActiveView('project');
  };

  // Handle opening a chat
  const handleOpenChat = (chatId: string) => {
    setActiveChatId(chatId);
    setActiveView('chat');
  };

  // Handle navigating to document view
  const handleOpenDocuments = () => {
    setActiveView('document');
  };

  // Handle navigating to project file manager
  const handleOpenProjectFiles = () => {
    setActiveView('projectFiles');
  };

  // Handle navigating to main file manager
  const handleOpenMainFiles = () => {
    setActiveView('mainFiles');
  };

  // Handle navigating to search results
  const handleShowSearchResults = () => {
    // In a real app, we would perform the search here
    // For now, just use mock data
    setSearchResults(mockSearchResults);
    setActiveView('searchResults');
  };

  // Handle attaching files from search results
  const handleAttachFiles = (fileIds: string[]) => {
    console.log(`Attaching files: ${fileIds.join(', ')} to project ${activeProjectId}`);
    // In a real app, this would make an API call
    
    // Return to project files view after attaching
    setActiveView('projectFiles');
  };

  // Handle file upload and processing
  const handleProcessFiles = (files: any[]) => {
    console.log(`Processing ${files.length} files`);
    // In a real app, this would make an API call
    
    // Return to main files view after processing
    setActiveView('mainFiles');
  };

  // Render the appropriate view based on activeView state
  const renderView = () => {
    switch (activeView) {
      case 'project':
        return (
          <ProjectManagerView 
            projectId={activeProjectId} 
            onOpenChat={handleOpenChat}
            onOpenFiles={handleOpenProjectFiles}
          />
        );
      case 'chat':
        return (
          <ChatView 
            projectId={activeProjectId} 
            chatId={activeChatId} 
          />
        );
      case 'document':
        return (
          <DocumentView 
            projectId={activeProjectId} 
          />
        );
      case 'projectFiles':
        return (
          <ProjectFileManager 
            projectId={activeProjectId} 
            onReturn={() => setActiveView('project')} 
            onOpenMainFileManager={handleOpenMainFiles} 
          />
        );
      case 'mainFiles':
        return (
          <MainFileManager 
            onReturn={() => activeProjectId ? setActiveView('projectFiles') : setActiveView('project')}
            onSelectProject={handleProjectSelect}
            projectId={activeProjectId}
          />
        );
      case 'searchResults':
        return (
          <SearchFilesResults 
            searchResults={searchResults}
            projectId={activeProjectId}
            onClose={() => setActiveView('projectFiles')}
            onAttachFiles={handleAttachFiles}
          />
        );
      default:
        return <div>Unknown view</div>;
    }
  };

  return (
    <div className="App">
      <MainLayout onProjectSelect={handleProjectSelect}>
        {renderView()}
      </MainLayout>
      
      {/* Modals */}
      <TagAndAddFileModal 
        isOpen={isTagAndAddModalOpen}
        onClose={() => setIsTagAndAddModalOpen(false)}
        onProcessFiles={handleProcessFiles}
      />
    </div>
  );
}

export default App;