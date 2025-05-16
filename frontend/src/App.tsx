// eslint-disable-next-line @typescript-eslint/no-unused-vars
import React, { useState, useEffect } from 'react';
import { Provider } from 'react-redux'; // Add this import
import { store } from './store'; // Add this import
import MainLayout from './components/layout/MainLayout';
import ProjectManagerView from './components/project/ProjectManagerView';
import ChatView from './components/chat/ChatView';
import DocumentView from './components/document/DocumentView';
import ProjectFileManager from './components/file/ProjectFileManager';
import MainFileManager from './components/file/MainFileManager';
import SearchFilesResults from './components/file/SearchFilesResults';
import TagAndAddFileModal from './components/modals/TagAndAddFileModal';
import { projectService } from './services';
import { ProjectProvider } from './context/ProjectContext';

// Define the possible view types
type View = 'project' | 'chat' | 'document' | 'projectFiles' | 'mainFiles' | 'searchResults';

// Initial empty state for chat messages
const initialMessages: {
  id: string;
  content: string;
  sender: 'user' | 'assistant';
  timestamp: string;
}[] = [];

function App() {
  // State for active project and view
  const [activeProjectId, setActiveProjectId] = useState<string>('');
  const [activeChatId, setActiveChatId] = useState<string | null>(null);
  const [activeView, setActiveView] = useState<View>('project');
  const [isProcessing, setIsProcessing] = useState(false);
  const [chatMessages, setChatMessages] = useState(initialMessages);
  const [projectNames, setProjectNames] = useState<{[key: string]: string}>({});
  const [chatNames, setChatNames] = useState<{[key: string]: string}>({});
  
  // State for file search and upload
  const [isTagAndAddModalOpen, setIsTagAndAddModalOpen] = useState(false);
  const [searchResults, setSearchResults] = useState<any[]>([]);
  
  // Initial empty search results
  const initialSearchResults: any[] = [];

  // Use project context to maintain reactive UI
  const { projects } = useProjects();
  
  // Effect to update project names and set active project when projects change
  useEffect(() => {
    if (projects.length > 0) {
      const projectsMap: {[key: string]: string} = {};
      projects.forEach(project => {
        projectsMap[project.id] = project.name;
      });
      setProjectNames(projectsMap);
      
      // If we have no active project but projects exist, set the first one
      if (!activeProjectId && projects.length > 0) {
        setActiveProjectId(projects[0].id);
      }
      
      // If active project was deleted, switch to first available
      if (activeProjectId && !projects.find(p => p.id === activeProjectId) && projects.length > 0) {
        setActiveProjectId(projects[0].id);
      }
    } else {
      // No projects exist
      setProjectNames({});
      setActiveProjectId('');
    }
  }, [projects, activeProjectId]);

  // Helper functions to get project and chat names by ID
  const getProjectName = (projectId: string): string => {
    return projectNames[projectId] || 'Unknown Project';
  };

  const getChatName = (chatId: string | null): string => {
    if (!chatId) return 'New Chat';
    return chatNames[chatId] || 'Unknown Chat';
  };

  // Handle message sending
  const handleSendMessage = (content: string) => {
    setIsProcessing(true);
    
    // Add user message
    const userMessage = {
      id: Date.now().toString(),
      content,
      sender: 'user' as const,
      timestamp: new Date().toLocaleString()
    };
    
    setChatMessages(prev => [...prev, userMessage]);
    
    // Simulate assistant response after delay
    setTimeout(() => {
      const assistantMessage = {
        id: (Date.now() + 1).toString(),
        content: `I received your message: "${content}". This is a mock response.`,
        sender: 'assistant' as const,
        timestamp: new Date().toLocaleString()
      };
      
      setChatMessages(prev => [...prev, assistantMessage]);
      setIsProcessing(false);
    }, 1000);
  };

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
    // TODO: Implement real search functionality
    // For now, just use empty results
    setSearchResults(initialSearchResults);
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
            onProjectDeleted={() => {
              // Reset to project view
              setActiveProjectId('');
              setActiveView('project');
            }}
          />
        );
      case 'chat':
        return (
          <ChatView 
            projectId={activeProjectId} 
            chatId={activeChatId}
            projectName={getProjectName(activeProjectId)}
            chatName={getChatName(activeChatId)}
            messages={chatMessages}
            isProcessing={isProcessing}
            onSendMessage={handleSendMessage}
            onEnableMic={() => console.log('Mic enabled')}
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
    <Provider store={store}>
      <ProjectProvider>
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
      </ProjectProvider>
    </Provider>
  );
}

export default App;