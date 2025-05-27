import { useState, useEffect, useRef } from 'react';
import { Provider, useSelector, useDispatch } from 'react-redux';
import { store, RootState, AppDispatch } from './store';
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
import { PromptPanelsProvider } from './context/PromptPanelsContext';
import { useNavigation } from './hooks/useNavigation';
import { fetchSystemPrompts, seedDefaultSystemPrompts } from './store/systemPromptsSlice';
import { setCurrentChat } from './store/chatSettingsSlice';

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
  const dispatch = useDispatch<AppDispatch>();
  
  // Get context mode from Redux store
  const { contextMode } = useSelector((state: RootState) => state.projectSettings);
  
  // Get chat settings for the current chat using the proper selector
  const chatSettings = useSelector((state: RootState) => 
    navigation.activeChatId 
      ? state.chatSettings?.settingsByChat?.[navigation.activeChatId] || null
      : null
  );
  
  // Local component state
  const [isProcessing, setIsProcessing] = useState(false);
  const [chatMessages, setChatMessages] = useState(initialMessages);
  const [projectNames, setProjectNames] = useState<{[key: string]: string}>({});
  const [chatNames, setChatNames] = useState<{[key: string]: string}>({});
  const [chats, setChats] = useState<ChatType[]>([]);
  
  // State for file search and upload
  const [isTagAndAddModalOpen, setIsTagAndAddModalOpen] = useState(false);
  const [searchResults] = useState<any[]>([]);
  
  // Ref to track previous chat ID
  const previousChatIdRef = useRef<string | null>(null);
  
  // Effect to initialize system prompts on app startup
  useEffect(() => {
    const initializeSystemPrompts = async () => {
      try {
        // First fetch existing system prompts
        await dispatch(fetchSystemPrompts()).unwrap();
        
        // Get the state to check if we have prompts
        const state = store.getState();
        if (state.systemPrompts.prompts.length === 0) {
          // No prompts exist, seed the defaults
          await dispatch(seedDefaultSystemPrompts()).unwrap();
        }
      } catch (error) {
        console.error('Failed to initialize system prompts:', error);
      }
    };
    
    initializeSystemPrompts();
  }, [dispatch]);
  
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
    // Only clear messages if we're actually changing chats
    if (previousChatIdRef.current !== navigation.activeChatId && navigation.activeChatId) {
      setChatMessages([]);
    }
    previousChatIdRef.current = navigation.activeChatId;
    
    const loadChatMessages = async () => {
      if (!navigation.activeChatId) {
        return;
      }
      
      // Initialize chat settings in Redux when navigating to a chat
      dispatch(setCurrentChat(navigation.activeChatId));
      
      try {
        const chat = await chatService.getChat(navigation.activeChatId);
        
        // Update chat name if not already in chatNames
        if (chat.name && navigation.activeChatId && !chatNames[navigation.activeChatId]) {
          setChatNames(prev => ({
            ...prev,
            [navigation.activeChatId]: chat.name
          }));
        }
        
        // Convert API messages to UI format, ensuring messages is an array
        const messages = Array.isArray(chat.messages) ? chat.messages : [];
        const uiMessages: UIMessage[] = messages.map((msg: ChatMessage) => ({
          id: msg.id || String(Date.now() + Math.random()),
          content: msg.content || '',
          sender: msg.role === 'user' ? 'user' : 'assistant',
          timestamp: new Date().toLocaleString() // Safer date handling
        }));
        
        setChatMessages(uiMessages);
      } catch (error) {
        console.error('Failed to load chat messages:', error);
        // Don't clear messages on error - preserve what we have
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
    // If we have the chat name, use it
    if (chatNames[chatId]) return chatNames[chatId];
    // Otherwise check if we can find it in the chats array
    const chat = chats.find(c => c.id === chatId);
    return chat ? chat.name : 'Loading...';
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
        // Add document context settings from chat settings
        is_project_documents_enabled: chatSettings?.isProjectDocumentsEnabled ?? true,
        is_global_data_enabled: chatSettings?.isGlobalDataEnabled ?? false,
        is_user_prompt_enabled: chatSettings?.isUserPromptEnabled ?? false,
        active_user_prompt_id: chatSettings?.activeUserPromptId || undefined,
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
      
      // Important: Don't let errors clear the chat or navigation state
      // This prevents the UI from going blank on errors
    }
  };

  // Handle creating a new chat
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const handleCreateChat = async (name: string) => {
    if (!navigation.activeProjectId) return;
    
    try {
      const newChat = await chatService.createChat({
        name,
        project_id: navigation.activeProjectId
      });
      
      // Update chats list
      setChats(prev => [...prev, newChat]);
      
      // Update chat names immediately
      setChatNames(prev => ({
        ...prev,
        [newChat.id]: newChat.name
      }));
      
      // Navigate to the new chat
      navigation.navigateToChat(newChat.id);
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
        return <ProjectFileManager />;
      case 'mainFiles':
        return <MainFileManager />;
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
        <PromptPanelsProvider>
          <AppContent />
        </PromptPanelsProvider>
      </ContextControlsProvider>
    </Provider>
  );
}

export default App;