// eslint-disable-next-line @typescript-eslint/no-unused-vars
import React, { useState, useEffect } from 'react';
import { Provider, useSelector } from 'react-redux';
import { store, RootState } from './store';
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
import { ProjectProvider } from './context/ProjectContext';
import { ContextControlsProvider } from './context/ContextControlsContext';
import { useNavigation } from './hooks/useNavigation';

// Adapted chat message type to match UI needs
interface UIMessage {
  id: string;
  content: string;
  sender: 'user' | 'assistant';
  timestamp: string;
  modelInfo?: {
    name: string;
    type: string;
  };
}

// Initial empty state for chat messages
const initialMessages: UIMessage[] = [];

// The main application without Redux provider (for hooks usage)
function AppContent() {
  // Use the navigation hook for state management
  const navigation = useNavigation();
  
  // Get context mode from Redux store
  const { contextMode } = useSelector((state: RootState) => state.projectSettings);
  
  // Local component state
  const [isProcessing, setIsProcessing] = useState(false);
  const [chatMessages, setChatMessages] = useState(initialMessages);
  const [projectNames, setProjectNames] = useState<{[key: string]: string}>({});
  const [chatNames, setChatNames] = useState<{[key: string]: string}>({});
  const [chats, setChats] = useState<ChatType[]>([]);
  
  // State for file search and upload
  const [isTagAndAddModalOpen, setIsTagAndAddModalOpen] = useState(false);
  const [searchResults, setSearchResults] = useState<any[]>([]);
  
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
          
          // Only auto-select first project if we're not in mainFiles view and no project is selected
          if (!navigation.activeProjectId && loadedProjects.length > 0 && navigation.activeView !== 'mainFiles') {
            navigation.navigateToProject(loadedProjects[0].id);
          }
          
          // If active project was deleted, switch to first available
          if (navigation.activeProjectId && 
              !loadedProjects.find(p => p.id === navigation.activeProjectId) && 
              loadedProjects.length > 0) {
            navigation.navigateToProject(loadedProjects[0].id);
          }
        } else {
          // No projects exist
          setProjectNames({});
        }
      } catch (error) {
        console.error('Failed to load projects:', error);
      }
    };
    
    loadProjects();
  }, [navigation.activeProjectId, navigation.activeView]);
  
  // Effect to load chats when the active project changes
  useEffect(() => {
    const loadChats = async () => {
      if (!navigation.activeProjectId) return;
      
      try {
        const loadedChats = await chatService.getChats(navigation.activeProjectId);
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
  }, [navigation.activeProjectId]);
  
  // Effect to load chat messages when the active chat changes
  useEffect(() => {
    const loadChatMessages = async () => {
      if (!navigation.activeChatId) {
        setChatMessages([]);
        return;
      }
      
      try {
        const chat = await chatService.getChat(navigation.activeChatId);
        
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
  }, [navigation.activeChatId]);

  // Helper functions to get project and chat names by ID
  const getProjectName = (projectId: string): string => {
    return projectNames[projectId] || 'Unknown Project';
  };

  const getChatName = (chatId: string | null): string => {
    if (!chatId) return 'New Chat';
    return chatNames[chatId] || 'Unknown Chat';
  };

  // Handle message sending with streaming
  const handleSendMessage = async (content: string, modelName?: string) => {
    if (!navigation.activeChatId) return;
    
    // Immediately add user message to UI
    const tempUserMessage: UIMessage = {
      id: `temp-${Date.now()}`,
      content,
      sender: 'user',
      timestamp: new Date().toLocaleString()
    };
    
    setChatMessages(prev => [...prev, tempUserMessage]);
    setIsProcessing(true);
    
    // Create assistant message placeholder for streaming
    const assistantMessageId = `assistant-${Date.now()}`;
    const assistantMessage: UIMessage = {
      id: assistantMessageId,
      content: '',
      sender: 'assistant',
      timestamp: new Date().toLocaleString(),
      modelInfo: undefined // Will be set when streaming starts
    };
    
    setChatMessages(prev => [...prev, assistantMessage]);
    
    try {
      // Use streaming API
      await chatService.sendMessageStream(navigation.activeChatId, content, {
        context_mode: contextMode,
        model_name: modelName,
        onStart: (modelInfo: { model: string }) => {
          // Update the assistant message with model info
          setChatMessages(prev => 
            prev.map(msg => 
              msg.id === assistantMessageId 
                ? { ...msg, modelInfo: { name: modelInfo.model, type: 'streaming' } }
                : msg
            )
          );
        },
        onChunk: (chunk: string) => {
          // Update the assistant message content as chunks arrive
          setChatMessages(prev => 
            prev.map(msg => 
              msg.id === assistantMessageId 
                ? { ...msg, content: msg.content + chunk }
                : msg
            )
          );
        },
        onComplete: async (messageIds) => {
          // Update message IDs with the real ones from the server
          setChatMessages(prev => 
            prev.map(msg => {
              if (msg.id === tempUserMessage.id) {
                return { ...msg, id: messageIds.user_message_id };
              }
              if (msg.id === assistantMessageId) {
                return { ...msg, id: messageIds.assistant_message_id };
              }
              return msg;
            })
          );
          setIsProcessing(false);
        },
        onError: (error: string) => {
          console.error('Streaming error:', error);
          // Update the assistant message with error
          setChatMessages(prev => 
            prev.map(msg => 
              msg.id === assistantMessageId 
                ? { ...msg, content: `Error: ${error}` }
                : msg
            )
          );
          setIsProcessing(false);
        }
      });
    } catch (error) {
      console.error('Failed to send message:', error);
      
      // Update assistant message with error
      setChatMessages(prev => 
        prev.map(msg => 
          msg.id === assistantMessageId 
            ? { ...msg, content: `Error communicating with server: ${error}` }
            : msg
        )
      );
      setIsProcessing(false);
    }
  };

  // Handle creating a new chat
  const handleCreateChat = async (name: string) => {
    if (!navigation.activeProjectId) return;
    
    try {
      const newChat = await chatService.createChat({
        name,
        project_id: navigation.activeProjectId
      });
      
      // Update chats list
      const updatedChats = await chatService.getChats(navigation.activeProjectId);
      setChats(updatedChats);
      
      // Update chat names map
      setChatNames(prev => ({
        ...prev,
        [newChat.id]: newChat.name
      }));
      
      // Set this as the active chat
      navigation.navigateToChat(newChat.id);
      
      return newChat;
    } catch (error) {
      console.error('Failed to create chat:', error);
      return null;
    }
  };

  // Handle attaching files from search results
  const handleAttachFiles = (fileIds: string[]) => {
    console.log(`Attaching files: ${fileIds.join(', ')} to project ${navigation.activeProjectId}`);
    // In a real app, this would make an API call
    
    // Return to project files view after attaching
    navigation.navigateToView('projectFiles');
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
          project_id: fileData.projectId || navigation.activeProjectId || undefined
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
    navigation.navigateToView('mainFiles');
  };

  // Render the appropriate view based on activeView state
  const renderView = () => {
    switch (navigation.activeView) {
      case 'project':
        return (
          <ProjectManagerView 
            projectId={navigation.activeProjectId || ''} 
            onOpenChat={(chatId) => navigation.navigateToChat(chatId)}
            onOpenFiles={() => navigation.navigateToView('projectFiles')}
            onProjectDeleted={() => {
              // Reset to project view
              navigation.navigateToProject('');
            }}
          />
        );
      case 'chat':
        return (
          <ChatView 
            projectId={navigation.activeProjectId || ''} 
            chatId={navigation.activeChatId}
            projectName={getProjectName(navigation.activeProjectId || '')}
            chatName={getChatName(navigation.activeChatId)}
            messages={chatMessages}
            isProcessing={isProcessing}
            onSendMessage={handleSendMessage}
            onEnableMic={() => console.log('Mic enabled')}
            onStopGeneration={() => {
              console.log('Stopping generation...');
              setIsProcessing(false);
              // TODO: Implement actual API call to stop generation
            }}
          />
        );
      case 'document':
        return (
          <DocumentView 
            projectId={navigation.activeProjectId || ''} 
          />
        );
      case 'projectFiles':
        return (
          <ProjectFileManager 
            projectId={navigation.activeProjectId || ''} 
            onReturn={() => navigation.navigateToView('project')} 
            onOpenMainFileManager={() => navigation.openMainFileManager()} 
          />
        );
      case 'mainFiles':
        return (
          <MainFileManager 
            onReturn={() => navigation.activeProjectId 
              ? navigation.navigateToView('projectFiles') 
              : navigation.navigateToView('project')}
            onSelectProject={(projectId) => navigation.navigateToProject(projectId)}
            projectId={navigation.activeProjectId || ''}
          />
        );
      case 'searchResults':
        return (
          <SearchFilesResults 
            searchResults={searchResults}
            projectId={navigation.activeProjectId || ''}
            onClose={() => navigation.navigateToView('projectFiles')}
            onAttachFiles={handleAttachFiles}
          />
        );
      default:
        return <div>Unknown view</div>;
    }
  };

  return (
    <div className="App">
      <ProjectProvider>
        <MainLayout>
          {renderView()}
        </MainLayout>
        
        {/* Modals */}
        <TagAndAddFileModal 
          isOpen={isTagAndAddModalOpen}
          onClose={() => setIsTagAndAddModalOpen(false)}
          onProcessFiles={handleProcessFiles}
          currentProjectId={navigation.activeProjectId || ''}
        />
      </ProjectProvider>
    </div>
  );
}

// Wrapper component with Redux Provider
function App() {
  return (
    <Provider store={store}>
      <ContextControlsProvider>
        <AppContent />
      </ContextControlsProvider>
    </Provider>
  );
}

export default App;