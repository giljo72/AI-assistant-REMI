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
import { projectService, chatService, fileService } from './services';
import type { Chat as ChatType, ChatMessage } from './services';
import { ProjectProvider, useProjects } from './context/ProjectContext';

// Define the possible view types
type View = 'project' | 'chat' | 'document' | 'projectFiles' | 'mainFiles' | 'searchResults';

// Adapted chat message type to match UI needs
interface UIMessage {
  id: string;
  content: string;
  sender: 'user' | 'assistant';
  timestamp: string;
}

// Initial empty state for chat messages
const initialMessages: UIMessage[] = [];

function App() {
  // State for active project and view
  const [activeProjectId, setActiveProjectId] = useState<string>('');
  const [activeChatId, setActiveChatId] = useState<string | null>(null);
  const [activeView, setActiveView] = useState<View>('project');
  const [forceMainFileView, setForceMainFileView] = useState(false); // New state for forcing main file view
  const [isProcessing, setIsProcessing] = useState(false);
  const [chatMessages, setChatMessages] = useState(initialMessages);
  const [projectNames, setProjectNames] = useState<{[key: string]: string}>({});
  const [chatNames, setChatNames] = useState<{[key: string]: string}>({});
  const [chats, setChats] = useState<ChatType[]>([]);
  
  // State for file search and upload
  const [isTagAndAddModalOpen, setIsTagAndAddModalOpen] = useState(false);
  const [searchResults, setSearchResults] = useState<any[]>([]);
  
  // Initial empty search results
  const initialSearchResults: any[] = [];
  
  // Effect to load projects and update project names
  useEffect(() => {
    const loadProjects = async () => {
      try {
        const loadedProjects = await projectService.getAllProjects();
        
        if (loadedProjects.length > 0) {
          const projectsMap: {[key: string]: string} = {};
          loadedProjects.forEach(project => {
            projectsMap[project.id] = project.name;
          });
          setProjectNames(projectsMap);
          
          // If we have no active project but projects exist, set the first one
          if (!activeProjectId && loadedProjects.length > 0) {
            setActiveProjectId(loadedProjects[0].id);
          }
          
          // If active project was deleted, switch to first available
          if (activeProjectId && !loadedProjects.find(p => p.id === activeProjectId) && loadedProjects.length > 0) {
            setActiveProjectId(loadedProjects[0].id);
          }
        } else {
          // No projects exist
          setProjectNames({});
          setActiveProjectId('');
        }
      } catch (error) {
        console.error('Failed to load projects:', error);
      }
    };
    
    loadProjects();
  }, [activeProjectId]);
  
  // Single effect to handle forced main file view
  useEffect(() => {
    // If force flag is set and view is not mainFiles, force it back
    if (forceMainFileView) {
      if (activeView !== 'mainFiles') {
        console.log("[APP] Force flag active - keeping view on mainFiles");
        // Set a short timeout to ensure other state updates complete first
        setTimeout(() => {
          setActiveView('mainFiles');
        }, 50);
      }
    }
  }, [activeView, forceMainFileView]);
  
  // Effect to load chats when the active project changes
  useEffect(() => {
    const loadChats = async () => {
      if (!activeProjectId) return;
      
      try {
        const loadedChats = await chatService.getChats(activeProjectId);
        setChats(loadedChats || []);
        
        // Create a map of chat names
        const chatsMap: {[key: string]: string} = {};
        if (Array.isArray(loadedChats)) {
          loadedChats.forEach(chat => {
            if (chat && chat.id && chat.name) {
              chatsMap[chat.id] = chat.name;
            }
          });
        }
        setChatNames(chatsMap);
      } catch (error) {
        console.error('Failed to load chats:', error);
        setChats([]);
        setChatNames({});
      }
    };
    
    loadChats();
  }, [activeProjectId]);
  
  // Effect to load chat messages when the active chat changes
  useEffect(() => {
    const loadChatMessages = async () => {
      if (!activeChatId) {
        setChatMessages([]);
        return;
      }
      
      try {
        const chat = await chatService.getChat(activeChatId);
        
        // Convert API messages to UI format, ensuring messages is an array
        const messages = Array.isArray(chat.messages) ? chat.messages : [];
        const uiMessages: UIMessage[] = messages.map((msg: ChatMessage) => ({
          id: msg.id || String(Date.now() + Math.random()),
          content: msg.content || '',
          sender: msg.is_user ? 'user' : 'assistant',
          timestamp: new Date().toLocaleString() // Safer date handling
        }));
        
        setChatMessages(uiMessages);
      } catch (error) {
        console.error('Failed to load chat messages:', error);
        setChatMessages([]);
      }
    };
    
    loadChatMessages();
  }, [activeChatId]);

  // Helper functions to get project and chat names by ID
  const getProjectName = (projectId: string): string => {
    return projectNames[projectId] || 'Unknown Project';
  };

  const getChatName = (chatId: string | null): string => {
    if (!chatId) return 'New Chat';
    return chatNames[chatId] || 'Unknown Chat';
  };

  // Handle message sending
  const handleSendMessage = async (content: string) => {
    if (!activeChatId) return;
    
    setIsProcessing(true);
    
    try {
      // Send message to API
      await chatService.sendMessage(activeChatId, content);
      
      // Reload messages
      const chat = await chatService.getChat(activeChatId);
      
      // Convert API messages to UI format
      const uiMessages: UIMessage[] = chat.messages.map((msg: ChatMessage) => ({
        id: msg.id,
        content: msg.content,
        sender: msg.is_user ? 'user' : 'assistant',
        timestamp: new Date(msg.created_at).toLocaleString()
      }));
      
      setChatMessages(uiMessages);
    } catch (error) {
      console.error('Failed to send message:', error);
      
      // Fallback to local message display if API fails
      const userMessage: UIMessage = {
        id: Date.now().toString(),
        content,
        sender: 'user',
        timestamp: new Date().toLocaleString()
      };
      
      setChatMessages(prev => [...prev, userMessage]);
      
      // Simulate assistant response
      setTimeout(() => {
        const assistantMessage: UIMessage = {
          id: (Date.now() + 1).toString(),
          content: `Error communicating with server. This is a fallback response.`,
          sender: 'assistant',
          timestamp: new Date().toLocaleString()
        };
        
        setChatMessages(prev => [...prev, assistantMessage]);
      }, 1000);
    } finally {
      setIsProcessing(false);
    }
  };

  // Handle project selection from sidebar
  const handleProjectSelect = (projectId: string) => {
    // Clear force flag if user intentionally navigates to a project
    if (forceMainFileView) {
      console.log("[APP] User selected a project, clearing force main file view flag");
      setForceMainFileView(false);
    }
    
    setActiveProjectId(projectId);
    setActiveChatId(null);
    setActiveView('project');
  };

  // Handle opening a chat
  const handleOpenChat = async (chatId: string) => {
    setActiveChatId(chatId);
    setActiveView('chat');
  };
  
  // Handle creating a new chat
  const handleCreateChat = async (name: string) => {
    if (!activeProjectId) return;
    
    try {
      const newChat = await chatService.createChat({
        name,
        project_id: activeProjectId
      });
      
      // Update chats list
      const updatedChats = await chatService.getChats(activeProjectId);
      setChats(updatedChats);
      
      // Update chat names map
      setChatNames(prev => ({
        ...prev,
        [newChat.id]: newChat.name
      }));
      
      // Set this as the active chat
      setActiveChatId(newChat.id);
      setActiveView('chat');
      
      return newChat;
    } catch (error) {
      console.error('Failed to create chat:', error);
      return null;
    }
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
  const handleOpenMainFiles = (clearActiveProject: boolean = false) => {
    console.log("[APP] Navigating to MainFileManager, clearActiveProject:", clearActiveProject);
    
    // When navigating to main file manager from paper icon, always clear the project ID
    // This prevents files from being attached to the last active project
    setActiveProjectId('');
    
    // Set the view to mainFiles and force it to stay there
    setActiveView('mainFiles');
    setForceMainFileView(true);
    
    console.log("[APP] Active project ID cleared, view set to mainFiles, force flag set");
    
    // Add a timeout to ensure React has time to update the UI
    setTimeout(() => {
      console.log("[APP] Verifying mainFiles view is active");
      setActiveView('mainFiles');
    }, 100);
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
  const handleProcessFiles = async (files: any[]) => {
    console.log(`Processing ${files.length} files`);
    
    try {
      // Process each file individually
      for (const fileData of files) {
        // Create a file upload request
        const uploadRequest = {
          file: fileData.file,
          name: fileData.file.name,
          description: fileData.description,
          project_id: fileData.projectId || activeProjectId || undefined
        };
        
        // Upload the file
        await fileService.uploadFile(uploadRequest);
      }
      
      // Success message
      console.log(`Successfully uploaded ${files.length} files`);
    } catch (error) {
      console.error('Error uploading files:', error);
    }
    
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
      <div className="App">
        <ProjectProvider>
          <MainLayout 
            onProjectSelect={handleProjectSelect}
            onOpenMainFiles={() => handleOpenMainFiles(true)} // Pass true to clear active project
          >
            {renderView()}
          </MainLayout>
          
          {/* Modals */}
          <TagAndAddFileModal 
            isOpen={isTagAndAddModalOpen}
            onClose={() => setIsTagAndAddModalOpen(false)}
            onProcessFiles={handleProcessFiles}
            currentProjectId={activeProjectId}
          />
        </ProjectProvider>
      </div>
    </Provider>
  );
}

export default App;