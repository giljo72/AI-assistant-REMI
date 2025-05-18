# Frontend Rebuild Plan: Separating MainFileManager from Project Navigation

## Problem Statement

The current implementation suffers from a critical navigation issue: when clicking the paper icon to access the Main File Manager, the application briefly shows the Main File Manager view but then quickly reverts back to a project view (usually the first/top project). This creates a confusing user experience where:

1. The Main File Manager is not properly isolated from the project context
2. Project selection state interferes with the Main File Manager navigation
3. The UI shows inconsistent state (highlights projects when in file manager view)
4. Multiple states in App.tsx are competing with each other causing race conditions

## Objective

Create a clear separation between project context and the Main File Manager by:

1. Treating the Main File Manager as a completely separate view that exists outside of the project context
2. Ensuring that when navigating to the Main File Manager, all project selection state is properly cleared
3. Making the Main File Manager the default "file hub" for the application
4. Creating clear visual indicators in the sidebar when in the Main File Manager view

## Core Architecture Changes

### 1. Navigation State Management

#### Current Approach (Problematic)
- Uses `activeView` state with multiple dependencies
- Uses `activeProjectId` that can auto-select based on available projects  
- Uses a complex `forceMainFileView` flag with multiple dependencies
- Multiple useEffect hooks with competing conditions
- Complex setTimeout-based state updates to handle race conditions

#### New Approach
- Create a dedicated navigation reducer with clear actions
- Separate the concept of "active project" from "current view"
- Handle view transitions through a single dispatcher
- Use a state machine approach to define valid transitions

### 2. Component Hierarchy

#### Current Approach (Problematic)
- All views are siblings in App.tsx's renderView function
- Project ID state is passed to MainFileManager even when it should be ignored
- ProjectSidebar maintains its own activeProjectId state that can conflict with App.tsx

#### New Approach
- Create a clear separation between project and non-project views
- Isolate the MainFileManager completely from project context
- Restructure the sidebar to have a stateless implementation
- Move all state management to a centralized location with clear ownership

### 3. Event Flow

#### Current Approach (Problematic)
- Multiple props are passed down to manage the same state
- Components make assumptions about parent component states
- State updates occur across different components causing race conditions

#### New Approach
- Use a unidirectional data flow with clear actions
- Implement an action-based navigation system
- Create a clear separation of concerns between UI components and state management

## Specific Implementation Plan

### 1. Create New State Management

Create a dedicated navigation reducer in `/frontend/src/store/navigationSlice.ts`:

```typescript
import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export type ViewType = 'project' | 'chat' | 'document' | 'projectFiles' | 'mainFiles' | 'searchResults';

interface NavigationState {
  currentView: ViewType;
  activeProjectId: string | null;
  activeChatId: string | null;
  previousView: ViewType | null; // For return navigation
}

const initialState: NavigationState = {
  currentView: 'mainFiles', // Default to main files view
  activeProjectId: null,
  activeChatId: null,
  previousView: null,
};

export const navigationSlice = createSlice({
  name: 'navigation',
  initialState,
  reducers: {
    // Navigation actions
    navigateToMainFiles: (state) => {
      state.previousView = state.currentView;
      state.currentView = 'mainFiles';
      state.activeProjectId = null; // Always clear project when going to main files
    },
    navigateToProject: (state, action: PayloadAction<string>) => {
      state.previousView = state.currentView;
      state.currentView = 'project';
      state.activeProjectId = action.payload;
      state.activeChatId = null;
    },
    navigateToProjectFiles: (state, action: PayloadAction<string>) => {
      state.previousView = state.currentView;
      state.currentView = 'projectFiles';
      state.activeProjectId = action.payload;
    },
    navigateToChat: (state, action: PayloadAction<{projectId: string, chatId: string}>) => {
      state.previousView = state.currentView;
      state.currentView = 'chat';
      state.activeProjectId = action.payload.projectId;
      state.activeChatId = action.payload.chatId;
    },
    navigateToPreviousView: (state) => {
      if (state.previousView) {
        state.currentView = state.previousView;
        state.previousView = null;
      }
    },
    // Additional actions as needed
  },
});

export const { 
  navigateToMainFiles, 
  navigateToProject, 
  navigateToProjectFiles,
  navigateToChat,
  navigateToPreviousView
} = navigationSlice.actions;

export default navigationSlice.reducer;
```

### 2. Update App Component

Rewrite `/frontend/src/App.tsx` to use the new navigation state:

```typescript
import React, { useState, useEffect } from 'react';
import { Provider, useSelector, useDispatch } from 'react-redux';
import { store } from './store';
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
import { 
  navigateToMainFiles, 
  navigateToProject, 
  navigateToProjectFiles,
  navigateToChat,
  navigateToPreviousView
} from './store/navigationSlice';
import { RootState } from './store';

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
  // Use Redux for navigation state
  const dispatch = useDispatch();
  const { currentView, activeProjectId, activeChatId } = useSelector(
    (state: RootState) => state.navigation
  );
  
  // Local UI state
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
        } else {
          setProjectNames({});
        }
      } catch (error) {
        console.error('Failed to load projects:', error);
      }
    };
    
    loadProjects();
  }, []);
  
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
    console.log("[APP] Project selected:", projectId);
    dispatch(navigateToProject(projectId));
  };

  // Handle opening a chat
  const handleOpenChat = async (chatId: string) => {
    if (!activeProjectId) return;
    dispatch(navigateToChat({ projectId: activeProjectId, chatId }));
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
      dispatch(navigateToChat({ projectId: activeProjectId, chatId: newChat.id }));
      
      return newChat;
    } catch (error) {
      console.error('Failed to create chat:', error);
      return null;
    }
  };

  // Handle navigating to main file manager
  const handleOpenMainFiles = () => {
    console.log("[APP] Navigating to MainFileManager");
    dispatch(navigateToMainFiles());
  };

  // Handle navigating to project file manager
  const handleOpenProjectFiles = () => {
    if (!activeProjectId) return;
    dispatch(navigateToProjectFiles(activeProjectId));
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
          project_id: fileData.projectId || undefined
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
    dispatch(navigateToMainFiles());
  };

  // Handle navigating to search results
  const handleShowSearchResults = () => {
    // TODO: Implement real search functionality
    setSearchResults([]);
    // Need to update this with a proper navigation action
  };

  // Handle attaching files from search results
  const handleAttachFiles = (fileIds: string[]) => {
    if (!activeProjectId) return;
    
    console.log(`Attaching files: ${fileIds.join(', ')} to project ${activeProjectId}`);
    // In a real app, this would make an API call
    
    // Return to project files view after attaching
    dispatch(navigateToProjectFiles(activeProjectId));
  };

  // Render the appropriate view based on currentView state
  const renderView = () => {
    switch (currentView) {
      case 'project':
        if (!activeProjectId) {
          // If somehow we're in project view without a project ID, go to main files
          dispatch(navigateToMainFiles());
          return null;
        }
        return (
          <ProjectManagerView 
            projectId={activeProjectId} 
            onOpenChat={handleOpenChat}
            onOpenFiles={handleOpenProjectFiles}
            onProjectDeleted={() => {
              // If project is deleted, go to main files
              dispatch(navigateToMainFiles());
            }}
          />
        );
      case 'chat':
        if (!activeProjectId || !activeChatId) {
          // If somehow we're in chat view without IDs, go to main files
          dispatch(navigateToMainFiles());
          return null;
        }
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
        if (!activeProjectId) {
          dispatch(navigateToMainFiles());
          return null;
        }
        return (
          <DocumentView 
            projectId={activeProjectId} 
          />
        );
      case 'projectFiles':
        if (!activeProjectId) {
          dispatch(navigateToMainFiles());
          return null;
        }
        return (
          <ProjectFileManager 
            projectId={activeProjectId} 
            onReturn={() => dispatch(navigateToProject(activeProjectId))} 
            onOpenMainFileManager={handleOpenMainFiles} 
          />
        );
      case 'mainFiles':
        return (
          <MainFileManager 
            onReturn={() => {
              if (activeProjectId) {
                dispatch(navigateToProject(activeProjectId)); 
              }
            }}
            onSelectProject={handleProjectSelect}
          />
        );
      case 'searchResults':
        return (
          <SearchFilesResults 
            searchResults={searchResults}
            projectId={activeProjectId}
            onClose={() => {
              if (activeProjectId) {
                dispatch(navigateToProjectFiles(activeProjectId));
              } else {
                dispatch(navigateToMainFiles());
              }
            }}
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
            currentView={currentView}
            activeProjectId={activeProjectId}
            onProjectSelect={handleProjectSelect}
            onOpenMainFiles={handleOpenMainFiles}
          >
            {renderView()}
          </MainLayout>
          
          {/* Modals */}
          <TagAndAddFileModal 
            isOpen={isTagAndAddModalOpen}
            onClose={() => setIsTagAndAddModalOpen(false)}
            onProcessFiles={handleProcessFiles}
            currentProjectId={activeProjectId || undefined}
          />
        </ProjectProvider>
      </div>
    </Provider>
  );
}

export default App;
```

### 3. Update MainLayout Component

Simplify `/frontend/src/components/layout/MainLayout.tsx`:

```typescript
import React, { ReactNode, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import ProjectSidebar from '../sidebar/ProjectSidebar';
import UserPromptsPanel from '../chat/UserPromptsPanel';
import ContextControlsPanel from '../modals/ContextControlsPanel';
import { RootState } from '../../store';

type MainLayoutProps = {
  children: ReactNode;
  currentView: string;
  activeProjectId: string | null;
  onProjectSelect: (projectId: string) => void;
  onOpenMainFiles: () => void;
};

const MainLayout: React.FC<MainLayoutProps> = ({ 
  children, 
  currentView,
  activeProjectId,
  onProjectSelect, 
  onOpenMainFiles
}) => {
  const [isContextControlsOpen, setIsContextControlsOpen] = useState(false);
  const dispatch = useDispatch();
  const { projectPromptEnabled, globalDataEnabled } = useSelector(
    (state: RootState) => state.projectSettings
  );

  return (
    <div className="flex h-screen bg-navy text-white overflow-hidden">
      {/* Sidebar */}
      <div className="w-64 bg-navy-light border-r border-gold overflow-y-auto flex flex-col" onClick={(e) => e.stopPropagation()}>
        {/* Project sidebar takes the top portion */}
        <div className="flex-1 overflow-y-auto">
          <ProjectSidebar 
            activeProjectId={activeProjectId}
            currentView={currentView}
            onProjectSelect={onProjectSelect} 
            onOpenMainFiles={onOpenMainFiles}
          />
        </div>
        
        {/* User Prompts and Context Controls in the bottom portion */}
        <div className="p-3 border-t border-navy">
          {/* Context Settings Button */}
          <button 
            onClick={() => setIsContextControlsOpen(true)}
            className="w-full py-2 mb-4 flex items-center justify-center bg-gold/20 hover:bg-gold/30 text-gold font-medium rounded transition-colors"
          >
            <span className="mr-1">⚙</span> Context Settings
          </button>
          
          {/* User Prompts Panel */}
          <UserPromptsPanel expanded={false} />
        </div>
      </div>
      
      {/* Main content area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="bg-navy-light p-4 border-b border-gold flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gold">AI Assistant</h1>
          
          {/* Mode dropdown - simplified version */}
          <div className="flex items-center bg-navy px-3 py-1.5 rounded">
            <span className="text-sm text-gray-400 mr-2">Mode:</span>
            <select className="bg-navy text-white text-sm focus:outline-none focus:ring-1 focus:ring-gold rounded">
              <option>Standard</option>
              <option>Project Focus</option>
              <option>Deep Research</option>
              <option>Quick Response</option>
              <option>Custom</option>
            </select>
          </div>
        </header>
        <main className="flex-1 overflow-y-auto p-4">
          {children}
        </main>
      </div>
      
      {/* Context Controls Modal */}
      <ContextControlsPanel
        isOpen={isContextControlsOpen}
        onClose={() => setIsContextControlsOpen(false)}
        onApplySettings={(settings) => {
          // Here you would dispatch actions to update settings
          setIsContextControlsOpen(false);
        }}
        initialSettings={{
          mode: 'standard',
          contextDepth: 50,
          useProjectDocs: projectPromptEnabled,
          useProjectChats: true,
          useAllDocs: globalDataEnabled,
          useAllChats: false,
        }}
      />
    </div>
  );
};

export default MainLayout;
```

### 4. Update ProjectSidebar Component

Rewrite `/frontend/src/components/sidebar/ProjectSidebar.tsx` to be completely stateless:

```typescript
import React, { useState } from 'react';
import AddProjectModal from '../modals/AddProjectModal';
import { useProjects } from '../../context/ProjectContext';

type ProjectSidebarProps = {
  activeProjectId: string | null;
  currentView: string;
  onProjectSelect: (projectId: string) => void;
  onOpenMainFiles: () => void;
};

const ProjectSidebar: React.FC<ProjectSidebarProps> = ({ 
  activeProjectId,
  currentView,
  onProjectSelect, 
  onOpenMainFiles
}) => {
  const [isProjectsExpanded, setIsProjectsExpanded] = useState(true);
  const [isAddProjectModalOpen, setIsAddProjectModalOpen] = useState(false);
  
  // Use the shared project context
  const { projects, loading, error, addProject } = useProjects();
  
  const handleAddProject = async (name: string, prompt: string) => {
    try {
      // Use the addProject method from context
      const newProject = await addProject(name, prompt || undefined);
      
      // Set this as the active project
      onProjectSelect(newProject.id);
    } catch (err) {
      console.error("Error creating project:", err);
    }
  };

  return (
    <div className="h-full flex flex-col bg-navy-light text-white">
      <div className="p-3">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-xl font-bold text-gold">AI Assistant</h2>
        </div>
        
        <div className="mb-4 flex items-center space-x-1">
          {/* File Manager Icon - Always highlighted when in mainFiles view */}
          <button 
            className={`p-2 ${currentView === 'mainFiles' ? 'bg-navy text-gold' : 'hover:bg-navy-lighter'} rounded-full`}
            onClick={(e) => {
              // Prevent event bubbling
              e.stopPropagation();
              e.preventDefault();
              onOpenMainFiles();
            }}
            title="File Manager"
          >
            <span className={`${currentView === 'mainFiles' ? 'text-gold font-bold' : 'text-gold'}`}>📄</span>
          </button>
          <button className="p-2 hover:bg-navy-lighter rounded-full">
            <span className="text-gold">🔍</span>
          </button>
          <button className="p-2 hover:bg-navy-lighter rounded-full">
            <span className="text-gold">❓</span>
          </button>
          <button className="p-2 hover:bg-navy-lighter rounded-full">
            <span className="text-gold">⚙️</span>
          </button>
        </div>
        
        <button 
          onClick={() => setIsAddProjectModalOpen(true)} 
          className="w-full py-2 mb-4 flex items-center justify-center bg-gold/20 hover:bg-gold/30 text-gold font-medium rounded transition-colors"
        >
          <span className="mr-1">+</span> Add Project
        </button>
      </div>
      
      <div className="px-3 flex-1 overflow-y-auto">
        <div className="mb-2">
          <button 
            onClick={() => setIsProjectsExpanded(!isProjectsExpanded)}
            className="w-full py-2 px-3 flex justify-between items-center rounded hover:bg-navy-lighter"
          >
            <span className={`font-bold text-gold`}>PROJECTS</span>
            <span>{isProjectsExpanded ? '▼' : '▶'}</span>
          </button>
          
          {isProjectsExpanded && (
            <div className="mt-1 space-y-1">
              {loading ? (
                <div className="p-3 text-center text-gray-400">
                  <p>Loading projects...</p>
                </div>
              ) : error ? (
                <div className="p-3 text-center text-red-400">
                  <p>{error}</p>
                </div>
              ) : projects.length === 0 ? (
                <div className="p-3 text-center text-gray-400">
                  <p>No projects found</p>
                  <button
                    onClick={() => setIsAddProjectModalOpen(true)}
                    className="mt-2 px-3 py-1 bg-navy hover:bg-navy-lighter text-white rounded text-sm"
                  >
                    Create your first project
                  </button>
                </div>
              ) : (
                projects.map((project) => (
                  <div 
                    key={project.id} 
                    onClick={() => onProjectSelect(project.id)}
                    className={`p-3 rounded cursor-pointer ${
                      // Only highlight if we're in a project-related view AND this is the active project
                      activeProjectId === project.id && currentView !== 'mainFiles' 
                        ? 'bg-navy text-gold font-bold' 
                        : 'hover:bg-navy-lighter'
                    }`}
                  >
                    {project.name}
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>

      {/* Add Project Modal */}
      <AddProjectModal 
        isOpen={isAddProjectModalOpen}
        onClose={() => setIsAddProjectModalOpen(false)}
        onAddProject={handleAddProject}
      />
    </div>
  );
};

export default ProjectSidebar;
```

### 5. Update MainFileManager Component

Simplify `/frontend/src/components/file/MainFileManager.tsx` to remove the projectId dependency:

```typescript
// Update the MainFileManager props type to remove projectId
type MainFileManagerProps = {
  onReturn: () => void; // Function to return to previous view
  onSelectProject?: (projectId: string) => void; // Function to navigate to a project
};

const MainFileManager: React.FC<MainFileManagerProps> = ({ 
  onReturn, 
  onSelectProject
}) => {
  // Rest of the component stays mostly the same
  // Remove all references to projectId prop
  // ...

  // When uploading files, never use a default projectId:
  const uploadRequest = {
    file,
    name: file.name,
    description: descriptionInput?.value || '',
    project_id: selectedProjectId || undefined // Never use a default project ID
  };

  // ...
};
```

### 6. Update Store Configuration

Ensure the store is properly configured with the new navigation reducer in `/frontend/src/store/index.ts`:

```typescript
import { configureStore } from '@reduxjs/toolkit';
import projectSettingsReducer from './projectSettingsSlice';
import userPromptsReducer from './userPromptsSlice';
import navigationReducer from './navigationSlice';

export const store = configureStore({
  reducer: {
    projectSettings: projectSettingsReducer,
    userPrompts: userPromptsReducer,
    navigation: navigationReducer
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
```

## Implementation Sequence

1. Create the navigation slice
2. Update store configuration
3. Update the App component
4. Update the MainLayout component
5. Update the ProjectSidebar component
6. Update the MainFileManager component
7. Test the navigation flow

## Expected Behavior After Implementation

1. When clicking the file icon (paper icon) in the sidebar:
   - The application will immediately navigate to the Main File Manager
   - All project context will be cleared (activeProjectId = null)
   - The paper icon will be visually highlighted
   - No project in the sidebar will be highlighted

2. When selecting a project in the sidebar:
   - The application will navigate to the project view
   - The active project will be highlighted
   - The paper icon will not be highlighted

3. When viewing files in a project and clicking "Browse Global Files":
   - The application will navigate to the Main File Manager
   - Active project context will be cleared
   - The paper icon will be highlighted
   - No project in the sidebar will be highlighted

4. When uploading files in the Main File Manager:
   - Files can be optionally linked to a project
   - If no project is selected, the file will be stored globally

This architecture creates a clear separation between the Main File Manager (global context) and Project views (project-specific context), ensuring that navigation between these views is reliable and the UI state accurately reflects the current context.