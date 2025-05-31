// File: frontend/src/components/layout/MainLayout.tsx
import React, { ReactNode, useState, useEffect, useRef } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import ProjectSidebar from '../sidebar/ProjectSidebar';
import UserPromptsPanel from '../chat/UserPromptsPanel';
import SystemPromptsPanel from '../chat/SystemPromptsPanel';
import ContextControlsPanel from '../modals/ContextControlsPanel';
import { RootState } from '../../store';
import { useNavigation } from '../../hooks/useNavigation';
import { useContextControls } from '../../context/ContextControlsContext';
import { usePromptPanels } from '../../context/PromptPanelsContext';
import { useAuth } from '../../context/AuthContext';
import { Icon } from '../common/Icon';
import { setContextMode } from '../../store/projectSettingsSlice';
import { updateContextMode } from '../../store/chatSettingsSlice';
import { ResourceMonitor } from '../common/ResourceMonitor';
import { FormControl, Select, MenuItem } from '@mui/material';
import systemService from '../../services/systemService';

type MainLayoutProps = {
  children: ReactNode;
};

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const dispatch = useDispatch();
  const { projectPromptEnabled, globalDataEnabled, projectDocumentsEnabled, contextMode } = useSelector(
    (state: RootState) => state.projectSettings
  );
  const { isOpen: isContextControlsOpen, openContextControls, closeContextControls } = useContextControls();
  const { 
    isUserPromptPanelOpen, 
    isSystemPromptPanelOpen,
    toggleUserPromptPanel,
    toggleSystemPromptPanel
  } = usePromptPanels();
  
  // Get navigation state using our custom hook
  const { activeView } = useNavigation();
  
  // Get auth context
  const { user, logout } = useAuth();
  
  // Dropdown state
  const [isUserDropdownOpen, setIsUserDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  
  // Model selector state
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [availableModels, setAvailableModels] = useState<any[]>([]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsUserDropdownOpen(false);
      }
    };

    if (isUserDropdownOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isUserDropdownOpen]);

  // Fetch available models on mount
  useEffect(() => {
    const fetchModels = async () => {
      try {
        // First, get active model quickly
        const activeModel = await systemService.getActiveModelQuick();
        
        // Then fetch full model list in background
        const models = await systemService.getAvailableModels();
        
        // Filter out embeddings models and keep only chat models
        const chatModels = models.filter((m: any) => 
          !m.name.includes('embedqa') && 
          m.last_used !== 'Embeddings' &&
          (m.type !== 'nvidia-nim' || 
           m.name === 'llama3.1:70b-instruct-q4_K_M' || 
           m.name === 'meta/llama-3.1-70b-instruct')
        );
        setAvailableModels(chatModels);
        
        // Validate that the active model exists in the available models list
        const modelExists = chatModels.some((m: any) => m.name === activeModel);
        
        if (modelExists) {
          setSelectedModel(activeModel);
        } else if (chatModels.length > 0) {
          // Prefer Qwen if available, otherwise use first available model
          const defaultModel = chatModels.find((m: any) => m.name.includes('qwen2.5:32b')) || 
                              chatModels.find((m: any) => m.name.includes('qwen')) || 
                              chatModels[0];
          setSelectedModel(defaultModel.name);
        } else {
          setSelectedModel('');
        }
      } catch (error) {
        console.error('Failed to fetch models:', error);
        setSelectedModel('');
        setAvailableModels([]);
      }
    };
    fetchModels();
  }, []);

  return (
    <div className="flex h-screen bg-navy text-white overflow-hidden">
      {/* Sidebar */}
      <div className="w-80 bg-navy-light border-r border-gold overflow-y-auto flex flex-col" onClick={(e) => e.stopPropagation()}>
        {/* Project sidebar takes the top portion */}
        <div className="flex-1 overflow-y-auto">
          <ProjectSidebar />
        </div>
        
        {/* User Prompts and Context Controls in the bottom portion */}
        <div className="p-3 border-t border-yellow-500">
          {/* Context Settings Button */}
          <button 
            onClick={openContextControls}
            className="w-full py-2 mb-4 flex items-center justify-center bg-gold/20 hover:bg-gold/30 text-gold font-medium rounded transition-colors"
          >
            <Icon name="settings" size={16} className="mr-1" />
            Context Settings
          </button>
          
          {/* System Prompts Panel */}
          <SystemPromptsPanel 
            expanded={isSystemPromptPanelOpen} 
            onToggleExpand={toggleSystemPromptPanel}
          />
          
          {/* User Prompts Panel */}
          <UserPromptsPanel 
            expanded={isUserPromptPanelOpen} 
            onToggleExpand={toggleUserPromptPanel}
          />
        </div>
      </div>
      
      {/* Main content area */}
      <div className="flex-1 flex flex-col min-h-0">
        <header className="bg-navy-light p-2 border-b border-gold flex justify-between items-center flex-shrink-0">
          {/* Left side - Resource Monitor with integrated Model Selector */}
          <div className="flex items-center">
            <ResourceMonitor />
            
            {/* Model Selector - positioned after CPU section */}
            <div className="flex items-center gap-1 ml-3">
              <span className="text-[9px]" style={{ color: '#FCC000' }}>Model:</span>
              <FormControl size="small" sx={{ minWidth: 180 }}>
                <Select
                  value={selectedModel}
                  onChange={async (e) => {
                    const newModel = e.target.value;
                    setSelectedModel(newModel);
                    // Switch the model in the backend
                    try {
                      const modelType = newModel.includes('meta/') ? 'nvidia-nim' : 'ollama';
                      await systemService.setActiveModel(newModel, modelType);
                    } catch (error) {
                      console.error('Failed to switch model:', error);
                    }
                  }}
                  MenuProps={{
                    PaperProps: {
                      sx: {
                        backgroundColor: '#1a2b47',
                        border: '1px solid #FCC000',
                        '& .MuiMenuItem-root': {
                          color: '#fff',
                          fontSize: '0.75rem',
                          '&:hover': {
                            backgroundColor: '#243449',
                          },
                          '&.Mui-selected': {
                            backgroundColor: '#FCC000',
                            color: '#000',
                            '&:hover': {
                              backgroundColor: '#FCC000',
                            }
                          }
                        }
                      }
                    }
                  }}
                  sx={{
                    backgroundColor: '#1a2b47',
                    color: '#fff',
                    fontSize: '0.65rem',
                    height: '20px',
                    '& .MuiOutlinedInput-notchedOutline': {
                      borderColor: '#152238',
                    },
                    '&:hover .MuiOutlinedInput-notchedOutline': {
                      borderColor: '#FCC000',
                    },
                    '& .MuiSelect-icon': {
                      color: '#FCC000',
                      fontSize: '14px',
                    },
                    '& .MuiSelect-select': {
                      paddingTop: '2px',
                      paddingBottom: '2px',
                    }
                  }}
                >
                  {availableModels.length > 0 ? (
                    availableModels.map((model) => {
                      // Format model display name - show full names and variants
                      let displayName = model.name;
                      if (model.name.includes('qwen2.5:32b')) {
                        displayName = 'Qwen 2.5 32B Instruct';
                      } else if (model.name.includes('llama3.1:70b') || model.name === 'meta/llama-3.1-70b-instruct') {
                        displayName = 'Llama 3.1 70B Instruct';
                      } else if (model.name.includes('llama-3.1-70b')) {
                        displayName = 'Llama 3.1 70B Instruct';
                      } else if (model.name.includes('mistral-nemo')) {
                        displayName = 'Mistral Nemo 12B Latest';
                      } else if (model.name.includes('deepseek-coder')) {
                        displayName = 'DeepSeek Coder V2 16B Lite';
                      }
                      
                      return (
                        <MenuItem key={model.name} value={model.name}>
                          {displayName}
                        </MenuItem>
                      );
                    })
                  ) : (
                    <MenuItem value="" disabled>
                      No models
                    </MenuItem>
                  )}
                </Select>
              </FormControl>
            </div>
          </div>
          
          {/* Right side controls */}
          <div className="flex items-center gap-4">
            {/* User dropdown */}
            <div className="relative" ref={dropdownRef}>
              <button
                onClick={() => setIsUserDropdownOpen(!isUserDropdownOpen)}
                className="flex flex-col items-center gap-1 hover:bg-navy-lighter px-3 py-1.5 rounded transition-colors"
              >
                <div 
                  className="w-10 h-10 rounded-full bg-gold flex items-center justify-center font-semibold text-lg"
                  style={{ color: '#080d13' }}
                  title={user?.email}
                >
                  {user?.username?.charAt(0).toUpperCase() || 'U'}
                </div>
                <span className="text-xs text-whiteGray">
                  {user?.username}
                </span>
              </button>
              
              {/* Dropdown menu */}
              {isUserDropdownOpen && (
                <div className="absolute right-0 mt-2 w-56 bg-navy-light border border-gold rounded-lg shadow-xl z-50">
                  <div className="p-3 border-b border-navy">
                    <p className="text-sm font-medium text-white">{user?.username}</p>
                    <p className="text-xs text-gray-400">{user?.email}</p>
                    <p className="text-xs text-gold mt-1">{user?.role === 'admin' ? 'Administrator' : 'User'}</p>
                  </div>
                  
                  <div className="py-1">
                    <button
                      onClick={() => {
                        setIsUserDropdownOpen(false);
                        // TODO: Navigate to user profile
                        alert('User Profile - Coming Soon');
                      }}
                      className="w-full text-left px-4 py-2 text-sm text-white hover:bg-navy hover:text-gold transition-colors flex items-center gap-2"
                    >
                      <Icon name="user" size={16} />
                      My Profile
                    </button>
                    
                    {user?.role === 'admin' && (
                      <button
                        onClick={() => {
                          setIsUserDropdownOpen(false);
                          // TODO: Navigate to user management
                          alert('User Management - Coming Soon');
                        }}
                        className="w-full text-left px-4 py-2 text-sm text-white hover:bg-navy hover:text-gold transition-colors flex items-center gap-2"
                      >
                        <Icon name="users" size={16} />
                        Manage Users
                      </button>
                    )}
                    
                    <div className="border-t border-navy my-1"></div>
                    
                    <button
                      onClick={() => {
                        setIsUserDropdownOpen(false);
                        logout();
                      }}
                      className="w-full text-left px-4 py-2 text-sm text-red hover:bg-navy transition-colors flex items-center gap-2"
                    >
                      <Icon name="lock" size={16} />
                      Logout
                    </button>
                  </div>
                </div>
              )}
            </div>
            
          </div>
        </header>
        <main className="flex-1 overflow-y-auto p-4 min-h-0">
          {children}
        </main>
      </div>
      
      {/* Context Controls Modal */}
      <ContextControlsPanel
        isOpen={isContextControlsOpen}
        onClose={closeContextControls}
        onApplySettings={(settings) => {
          // Update the context mode in both Redux slices
          dispatch(setContextMode(settings.mode)); // For project settings
          dispatch(updateContextMode(settings.mode)); // For chat settings
          closeContextControls();
        }}
        initialSettings={{
          mode: contextMode,
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