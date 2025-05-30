import { useState, useEffect, useRef } from 'react';
import { Provider, useSelector, useDispatch } from 'react-redux';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
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
import type { Chat as ChatType, ChatMessage, Project } from './services';
import { ProjectProvider } from './context/ProjectContext';
import { ContextControlsProvider } from './context/ContextControlsContext';
import { PromptPanelsProvider } from './context/PromptPanelsContext';
import { AuthProvider, useAuth } from './context/AuthContext';
import { LoginPage } from './components/auth/LoginPage';
import { WelcomeScreen } from './components/auth/WelcomeScreen';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { SetupWizard } from './components/auth/SetupWizard';
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
  const { user } = useAuth();
  
  // Get context mode from Redux store
  const { contextMode } = useSelector((state: RootState) => state.projectSettings);
  
  // Get chat settings for the current chat using the proper selector
  const chatSettings = useSelector((state: RootState) => 
    navigation.activeChatId 
      ? state.chatSettings?.settingsByChat?.[navigation.activeChatId] || null
      : null
  );
  
  // State for projects and chats
  const [projects, setProjects] = useState<Project[]>([]);
  const [activeChat, setActiveChat] = useState<ChatType | null>(null);
  
  // Active chat state from navigation hook
  const activeChatId = navigation.activeChatId;
  const hasProjects = projects.length > 0;
  
  const [chatMessages, setChatMessages] = useState<UIMessage[]>(initialMessages);
  const [isLoading, setIsLoading] = useState(false);
  const [showAddFileModal, setShowAddFileModal] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Load projects when user logs in
  useEffect(() => {
    const loadProjects = async () => {
      if (user) {
        try {
          const loadedProjects = await projectService.getAllProjects();
          setProjects(loadedProjects);
        } catch (error) {
          console.error('Failed to load projects:', error);
          setProjects([]);
        }
      }
    };
    
    loadProjects();
  }, [user]);
  
  // Load active chat when chat ID changes
  useEffect(() => {
    const loadActiveChat = async () => {
      if (activeChatId && navigation.activeProjectId) {
        try {
          const chats = await chatService.getProjectChats(navigation.activeProjectId);
          const chat = chats.find(c => c.id === activeChatId);
          setActiveChat(chat || null);
        } catch (error) {
          console.error('Failed to load active chat:', error);
          setActiveChat(null);
        }
      } else {
        setActiveChat(null);
      }
    };
    
    loadActiveChat();
  }, [activeChatId, navigation.activeProjectId]);
  
  // Load messages for active chat
  useEffect(() => {
    const loadChatMessages = async () => {
      if (activeChatId) {
        try {
          const messages = await chatService.getChatMessages(activeChatId);
          
          // Convert chat messages to UI format
          const uiMessages: UIMessage[] = messages.map((msg: ChatMessage) => ({
            id: msg.id,
            content: msg.content,
            sender: msg.is_user ? 'user' : 'assistant',
            timestamp: new Date(msg.created_at).toLocaleTimeString(),
            modelInfo: msg.model_info
          }));
          
          setChatMessages(uiMessages);
          
          // Set current chat in Redux for chat settings
          dispatch(setCurrentChat(activeChatId));
        } catch (error) {
          console.error('Failed to load chat messages:', error);
          setChatMessages([]);
        }
      } else {
        setChatMessages([]);
      }
    };
    
    loadChatMessages();
  }, [activeChatId, dispatch]);
  
  // Load system prompts when user logs in
  useEffect(() => {
    const loadSystemPrompts = async () => {
      if (user) {
        try {
          const result = await dispatch(fetchSystemPrompts()).unwrap();
          
          // If no system prompts exist, seed the default ones
          if (result.length === 0) {
            await dispatch(seedDefaultSystemPrompts()).unwrap();
          }
        } catch (error) {
          console.error('Failed to load system prompts:', error);
        }
      }
    };
    
    loadSystemPrompts();
  }, [dispatch, user]);
  
  // Scroll to bottom when messages update
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  useEffect(() => {
    scrollToBottom();
  }, [chatMessages]);
  
  // Handler for sending messages
  const handleSendMessage = async (content: string) => {
    if (!activeChatId || !navigation.activeProjectId) return;
    
    // Add user message to UI immediately
    const userMessage: UIMessage = {
      id: 'temp-' + Date.now(),
      content,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString()
    };
    setChatMessages(prev => [...prev, userMessage]);
    
    setIsLoading(true);
    try {
      // Use chat settings for message configuration
      const response = await chatService.sendChatMessage(
        activeChatId,
        content,
        contextMode,
        navigation.activeProjectId,
        chatSettings?.systemPromptId,
        chatSettings?.userPromptIds || []
      );
      
      // Update with actual response
      setChatMessages(prev => [
        ...prev.filter(m => m.id !== userMessage.id),
        {
          id: response.user_message_id,
          content,
          sender: 'user',
          timestamp: new Date().toLocaleTimeString()
        },
        {
          id: response.assistant_message_id,
          content: response.content,
          sender: 'assistant',
          timestamp: new Date().toLocaleTimeString(),
          modelInfo: response.model_info
        }
      ]);
    } catch (error) {
      console.error('Failed to send message:', error);
      // Remove the temporary message on error
      setChatMessages(prev => prev.filter(m => m.id !== userMessage.id));
    } finally {
      setIsLoading(false);
    }
  };
  
  // Show welcome screen when no project is selected
  const showWelcomeScreen = !navigation.activeProjectId && navigation.activeView === 'chat';
  
  // Render different views based on current navigation
  const renderContent = () => {
    if (showWelcomeScreen) {
      return (
        <WelcomeScreen 
          hasProjects={hasProjects}
          onStartProject={() => navigation.navigateToView('project')}
        />
      );
    }

    switch (navigation.activeView) {
      case 'project':
        return <ProjectManagerView />;
      case 'chat':
        return activeChat ? (
          <ChatView
            messages={chatMessages}
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
            messagesEndRef={messagesEndRef}
          />
        ) : (
          <div className="flex-1 flex items-center justify-center bg-navy">
            <p className="text-gray-400">Select or create a chat to start</p>
          </div>
        );
      case 'document':
        return <DocumentView />;
      case 'projectFiles':
        return <ProjectFileManager />;
      case 'mainFiles':
        return <MainFileManager />;
      case 'searchResults':
        return <SearchFilesResults searchQuery={navigation.searchQuery || ''} />;
      default:
        return null;
    }
  };
  
  return (
    <ProtectedRoute>
      <MainLayout>
        {renderContent()}
        {showAddFileModal && (
          <TagAndAddFileModal
            onClose={() => setShowAddFileModal(false)}
            onFilesAdded={() => {
              setShowAddFileModal(false);
              // Refresh file list if needed
            }}
          />
        )}
      </MainLayout>
    </ProtectedRoute>
  );
}

// Main App component with all providers
function App() {
  return (
    <Provider store={store}>
      <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/setup" element={<SetupWizard />} />
            <Route
              path="/*"
              element={
                <ProjectProvider>
                  <ContextControlsProvider>
                    <PromptPanelsProvider>
                      <AppContent />
                    </PromptPanelsProvider>
                  </ContextControlsProvider>
                </ProjectProvider>
              }
            />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </Provider>
  );
}

export default App;