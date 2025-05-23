import React, { useState, useEffect } from 'react';
import AddChatModal from '../modals/AddChatModal';
import DeleteProjectModal from '../modals/DeleteProjectModal';
import { projectService, userPromptService, chatService } from '../../services';
import { Project, UserPrompt, Chat as ChatType } from '../../services';
import { useProjects } from '../../context/ProjectContext';

type Tab = 'overview' | 'chats' | 'files' | 'settings';

// Local types for UI
type Chat = {
  id: string;
  name: string;
  projectId: string;
  createdAt: string;
};

type File = {
  id: string;
  name: string;
  type: string;
  size: string;
  active: boolean;
  projectId: string;
  addedAt: string;
  description?: string;
  processed: boolean;
  processingFailed?: boolean;
  chunks?: number;
};

// Empty initial states for chats and files (will be replaced with API calls later)
const initialChats: Chat[] = [];
const initialFiles: File[] = [];

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

type ProjectManagerViewProps = {
  projectId: string;
  onOpenChat?: (chatId: string) => void;
  onOpenFiles?: () => void;
  onProjectDeleted?: () => void; // Callback for project deletion
};

const ProjectManagerView: React.FC<ProjectManagerViewProps> = ({ projectId, onOpenChat, onOpenFiles, onProjectDeleted }) => {
  const [activeTab, setActiveTab] = useState<Tab>('overview');
  const [project, setProject] = useState<Project | null>(null);
  const [projectChats, setProjectChats] = useState<Chat[]>([]);
  const [projectFiles, setProjectFiles] = useState<File[]>([]);
  const [projectPrompts, setProjectPrompts] = useState<UserPrompt[]>([]);
  const [isAddChatModalOpen, setIsAddChatModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [projectName, setProjectName] = useState('');
  const [projectDescription, setProjectDescription] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  // Effect to load project data when projectId changes
  useEffect(() => {
    const fetchProjectData = async () => {
      setLoading(true);
      setError(null);
      try {
        // Fetch project details
        const projectData = await projectService.getProject(projectId);
        setProject(projectData);
        setProjectName(projectData.name);
        setProjectDescription(projectData.description || '');
        
        // Fetch project prompts
        const prompts = await userPromptService.getUserPromptsForProject(projectId);
        setProjectPrompts(prompts);
        
        // Fetch project chats
        try {
          const chats = await chatService.getChats(projectId);
          // Convert API chats to UI format - ensure chats is an array
          const uiChats: Chat[] = Array.isArray(chats) ? chats.map(chat => ({
            id: chat.id,
            name: chat.name,
            projectId: chat.project_id,
            createdAt: new Date().toLocaleDateString() // Use safer date format
          })) : [];
          setProjectChats(uiChats);
        } catch (chatError) {
          console.error("Error fetching chats:", chatError);
          setProjectChats([]);
        }
        
        // Fetch project files
        try {
          const fileService = await import('../../services/fileService').then(module => module.default);
          const files = await fileService.getAllFiles({ project_id: projectId });
          
          // Convert API files to UI format
          const uiFiles: File[] = files.map(file => ({
            id: file.id,
            name: file.name,
            type: file.type,
            size: typeof file.size === 'number' ? 
              formatFileSize(file.size) : 
              (file.size as string),
            active: file.active,
            projectId: file.project_id as string,
            addedAt: new Date(file.created_at).toLocaleDateString(),
            description: file.description,
            processed: file.processed || false,
            processingFailed: file.processing_failed,
            chunks: file.chunk_count
          }));
          
          setProjectFiles(uiFiles);
        } catch (fileError) {
          console.error("Error fetching files:", fileError);
          setProjectFiles([]);
        }
      } catch (err) {
        console.error("Error fetching project data:", err);
        setError("Failed to load project. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    if (projectId) {
      fetchProjectData();
    }
  }, [projectId]);

  const handleAddChat = async (name: string) => {
    if (!project) return;
    
    try {
      // Create chat using the API
      const newChat = await chatService.createChat({
        name,
        project_id: project.id
      });
      
      // Convert API chat to local format
      const localChat: Chat = {
        id: newChat.id,
        name: newChat.name,
        projectId: newChat.project_id,
        createdAt: new Date().toLocaleDateString(), // Use safer date format
      };
      
      // Update local state
      setProjectChats([...projectChats, localChat]);
      
      // Open the chat if a handler was provided
      if (onOpenChat) {
        onOpenChat(newChat.id);
      }
    } catch (error) {
      console.error('Error creating chat:', error);
      setError('Failed to create chat. Please try again.');
    }
  };

  // Handler for opening a chat
  const handleOpenChat = (chatId: string) => {
    if (onOpenChat) {
      onOpenChat(chatId);
    }
  };

  // Handler for deleting a chat
  const handleDeleteChat = async (chatId: string) => {
    if (!project) return;
    
    // Simple confirmation
    if (!window.confirm('Are you sure you want to delete this chat? This action cannot be undone.')) {
      return;
    }
    
    try {
      // Delete chat using the API
      await chatService.deleteChat(chatId);
      
      // Update local state by removing the chat
      setProjectChats(projectChats.filter(chat => chat.id !== chatId));
      
    } catch (error) {
      console.error('Error deleting chat:', error);
      setError('Failed to delete chat. Please try again.');
    }
  };

  // Handler for opening file manager
  const handleOpenFiles = () => {
    if (onOpenFiles) {
      onOpenFiles();
    }
  };

  // Handler for saving project settings
  const handleSaveSettings = async () => {
    if (!project) return;
    
    setIsSaving(true);
    try {
      // Only update if something has changed
      if (projectName !== project.name || projectDescription !== (project.description || '')) {
        await projectService.updateProject(project.id, {
          name: projectName,
          description: projectDescription
        });
        
        // Update the local project state with the new values
        setProject({
          ...project,
          name: projectName,
          description: projectDescription
        });
      }
    } catch (err) {
      console.error("Error updating project:", err);
      setError("Failed to update project. Please try again.");
    } finally {
      setIsSaving(false);
    }
  };
  
  // Use project context
  const { deleteProject: contextDeleteProject } = useProjects();
  
  // Handler for deleting the project
  const handleDeleteProject = async () => {
    if (!project) return;
    
    try {
      // Use the context method to delete and update state everywhere
      await contextDeleteProject(project.id);
      
      // Call the onProjectDeleted callback if provided
      if (onProjectDeleted) {
        onProjectDeleted();
      }
    } catch (err) {
      console.error("Error deleting project:", err);
      setError("Failed to delete project. Please try again.");
      // Close the delete modal
      setIsDeleteModalOpen(false);
    }
  };

  if (loading) {
    return <div className="p-4 text-center">Loading project...</div>;
  }

  if (error) {
    return <div className="p-4 text-center text-red-500">{error}</div>;
  }

  if (!project) {
    return <div className="p-4 text-center">Project not found</div>;
  }

  // Find active prompt for this project
  const activePrompt = projectPrompts.find(prompt => prompt.is_active);

  return (
    <div className="h-full flex flex-col">
      <div className="bg-navy-light p-4 mb-4 rounded-lg">
        <div className="flex justify-between items-center mb-2">
          <h2 className="text-xl font-bold text-gold">{project.name}</h2>
          <div className="flex space-x-2">
            <button 
              className="px-3 py-1 bg-navy hover:bg-navy-lighter rounded text-sm"
              onClick={() => setActiveTab('settings')}
            >
              Modify
            </button>
            <button 
              className="px-3 py-1 bg-red-700/30 hover:bg-red-700/50 text-red-400 rounded text-sm"
              onClick={() => setIsDeleteModalOpen(true)}
            >
              Delete
            </button>
          </div>
        </div>
        
        {activePrompt && (
          <div className="text-gray-300 text-sm bg-navy p-3 rounded mb-3">
            <div className="text-xs text-gray-400 mb-1">Active Prompt: {activePrompt.name}</div>
            <p>{activePrompt.content}</p>
          </div>
        )}
        
        <div className="border-b border-navy mt-4">
          <nav className="flex -mb-px">
            <button
              onClick={() => setActiveTab('overview')}
              className={`mr-4 py-2 px-1 ${
                activeTab === 'overview'
                  ? 'border-b-2 border-gold text-gold'
                  : 'text-gray-400 hover:text-gray-300'
              }`}
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab('chats')}
              className={`mr-4 py-2 px-1 ${
                activeTab === 'chats'
                  ? 'border-b-2 border-gold text-gold'
                  : 'text-gray-400 hover:text-gray-300'
              }`}
            >
              Chats
            </button>
            <button
              onClick={() => {
                // Instead of switching to files tab, directly open the file manager
                handleOpenFiles();
              }}
              className={`mr-4 py-2 px-1 text-gray-400 hover:text-gray-300`}
            >
              Files
            </button>
            <button
              onClick={() => setActiveTab('settings')}
              className={`py-2 px-1 ${
                activeTab === 'settings'
                  ? 'border-b-2 border-gold text-gold'
                  : 'text-gray-400 hover:text-gray-300'
              }`}
            >
              Settings
            </button>
          </nav>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto">
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-navy-light p-4 rounded-lg">
              <div className="flex justify-between items-center mb-2">
                <h3 className="text-lg font-medium text-gold">Recent Chats</h3>
                <button 
                  onClick={() => setActiveTab('chats')}
                  className="text-xs px-2 py-1 bg-navy hover:bg-navy-lighter rounded"
                >
                  View All
                </button>
              </div>
              <div className="space-y-2">
                {projectChats.slice(0, 3).map(chat => (
                  <div 
                    key={chat.id} 
                    className="p-2 bg-navy hover:bg-navy-lighter rounded cursor-pointer flex justify-between"
                    onClick={() => handleOpenChat(chat.id)}
                  >
                    <span>{chat.name}</span>
                    <span className="text-xs text-gray-400">{chat.createdAt}</span>
                  </div>
                ))}
                {projectChats.length === 0 && (
                  <div className="p-3 text-center text-gray-400">
                    No chats in this project yet
                  </div>
                )}
              </div>
            </div>
            
            <div className="bg-navy-light p-4 rounded-lg">
              <div className="flex justify-between items-center mb-2">
                <h3 className="text-lg font-medium text-gold">Project Files</h3>
                <button 
                  onClick={() => handleOpenFiles()}
                  className="text-xs px-2 py-1 bg-navy hover:bg-navy-lighter rounded"
                >
                  View All
                </button>
              </div>
              <div className="space-y-2">
                {projectFiles.slice(0, 3).map(file => (
                  <div key={file.id} className="p-2 bg-navy hover:bg-navy-lighter rounded cursor-pointer">
                    <div className="flex justify-between items-center">
                      <span className="font-medium">{file.name}</span>
                      <div className="flex items-center space-x-2">
                        <span className={`w-2 h-2 rounded-full ${file.active ? 'bg-green-500' : 'bg-gray-500'}`}></span>
                        <span className="text-xs text-gray-400">{file.size}</span>
                      </div>
                    </div>
                    <div className="mt-1 text-xs text-gray-400">
                      {file.description && (
                        <p className="text-gray-300 mb-1 line-clamp-1">{file.description}</p>
                      )}
                      <div className="flex flex-wrap gap-x-2">
                        <span>{file.processed ? 
                          <span className="text-green-400">Processed</span> : 
                          <span className="text-yellow-400">Processing...</span>}
                        </span>
                        {(file as any).chunks && (
                          <span>{(file as any).chunks} chunks</span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
                {projectFiles.length === 0 && (
                  <div className="p-3 text-center text-gray-400">
                    No files attached to this project yet
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'chats' && (
          <div className="bg-navy-light p-4 rounded-lg">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gold">Project Chats</h3>
              <button 
                onClick={() => setIsAddChatModalOpen(true)}
                className="px-3 py-1 bg-gold/20 hover:bg-gold/30 text-gold rounded text-sm flex items-center"
              >
                <span className="mr-1">+</span> Add Chat
              </button>
            </div>
            <div className="space-y-2">
              {projectChats.map(chat => (
                <div key={chat.id} className="p-3 bg-navy hover:bg-navy-lighter rounded flex justify-between items-center">
                  <span>{chat.name}</span>
                  <div className="flex space-x-2">
                    <button 
                      className="text-xs px-2 py-1 bg-navy-light hover:bg-navy rounded"
                      onClick={() => handleOpenChat(chat.id)}
                    >
                      Open
                    </button>
                    <button className="text-xs px-2 py-1 bg-navy-light hover:bg-navy rounded">
                      Edit
                    </button>
                    <button 
                      className="text-xs px-2 py-1 bg-red-700/30 hover:bg-red-700/50 text-red-400 rounded"
                      onClick={() => handleDeleteChat(chat.id)}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
              {projectChats.length === 0 && (
                <div className="p-3 text-center text-gray-400">
                  No chats in this project yet. Create your first chat!
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'files' && (
          <div className="bg-navy-light p-4 rounded-lg">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gold">Project Files</h3>
              <button 
                onClick={() => handleOpenFiles()}
                className="px-3 py-1 bg-gold/20 hover:bg-gold/30 text-gold rounded text-sm flex items-center"
              >
                <span className="mr-1">+</span> Attach File
              </button>
            </div>
            <div className="space-y-2">
              {projectFiles.map(file => (
                <div key={file.id} className="p-3 bg-navy hover:bg-navy-lighter rounded flex justify-between items-center">
                  <div className="flex items-center">
                    <div className="w-8 h-8 bg-blue-500/20 rounded flex items-center justify-center mr-3">
                      <span className="text-blue-400 text-xs">{file.type}</span>
                    </div>
                    <div>
                      <h4 className="font-medium">{file.name}</h4>
                      <p className="text-xs text-gray-400">Added {file.addedAt} • {file.size}</p>
                    </div>
                  </div>
                  <div className="flex space-x-2 items-center">
                    <div className="flex items-center mr-2">
                      <label className="inline-flex items-center cursor-pointer">
                        <input 
                          type="checkbox" 
                          checked={file.active}
                          className="sr-only peer"
                        />
                        <div className={`w-9 h-5 rounded-full peer ${file.active ? 'bg-gold/40' : 'bg-navy-lighter'} peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all relative`}></div>
                      </label>
                    </div>
                    <button className="text-xs px-2 py-1 bg-navy-light hover:bg-navy rounded">
                      View
                    </button>
                    <button className="text-xs px-2 py-1 bg-navy-light hover:bg-navy rounded">
                      Download
                    </button>
                    <button className="text-xs px-2 py-1 bg-red-700/30 hover:bg-red-700/50 text-red-400 rounded">
                      Detach
                    </button>
                  </div>
                </div>
              ))}
              {projectFiles.length === 0 && (
                <div className="p-3 text-center text-gray-400">
                  No files attached to this project yet
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="bg-navy-light p-4 rounded-lg">
            <h3 className="text-lg font-medium text-gold mb-4">Project Settings</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">
                  Project Name
                </label>
                <input
                  type="text"
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                  className="w-full bg-navy p-2 rounded focus:outline-none focus:ring-1 focus:ring-gold"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">
                  Project Description
                </label>
                <textarea
                  value={projectDescription}
                  onChange={(e) => setProjectDescription(e.target.value)}
                  className="w-full bg-navy p-2 rounded focus:outline-none focus:ring-1 focus:ring-gold min-h-[100px]"
                />
                <p className="text-xs text-gray-400 mt-1">
                  Describe the purpose and scope of this project.
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">
                  Project Prompts
                </label>
                <div className="bg-navy p-3 rounded">
                  {projectPrompts.length > 0 ? (
                    <div className="space-y-2">
                      {projectPrompts.map(prompt => (
                        <div key={prompt.id} className="flex items-center">
                          <input
                            type="radio"
                            id={`prompt-${prompt.id}`}
                            name="activePrompt"
                            checked={prompt.is_active}
                            onChange={async () => {
                              try {
                                await userPromptService.activateUserPrompt(prompt.id);
                                // Update local state
                                setProjectPrompts(prevPrompts => 
                                  prevPrompts.map(p => ({
                                    ...p,
                                    is_active: p.id === prompt.id
                                  }))
                                );
                              } catch (err) {
                                console.error("Error activating prompt:", err);
                              }
                            }}
                            className="mr-2"
                          />
                          <label htmlFor={`prompt-${prompt.id}`} className="cursor-pointer">
                            {prompt.name}
                          </label>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-gray-400 text-sm">
                      No custom prompts created for this project yet.
                    </div>
                  )}
                  <button className="mt-3 text-xs px-2 py-1 bg-navy-light hover:bg-navy-lighter rounded">
                    Manage Prompts
                  </button>
                </div>
              </div>
              <div className="pt-4 flex justify-end space-x-3">
                <button className="px-4 py-2 bg-navy hover:bg-navy-lighter rounded">
                  Cancel
                </button>
                <button 
                  className={`px-4 py-2 bg-gold text-navy font-medium rounded hover:bg-gold/90 ${isSaving ? 'opacity-70 cursor-not-allowed' : ''}`}
                  onClick={handleSaveSettings}
                  disabled={isSaving}
                >
                  {isSaving ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Add Chat Modal */}
      <AddChatModal 
        isOpen={isAddChatModalOpen}
        onClose={() => setIsAddChatModalOpen(false)}
        onAddChat={handleAddChat}
        projectName={project.name}
      />

      {/* Delete Project Modal */}
      <DeleteProjectModal
        isOpen={isDeleteModalOpen}
        onClose={() => setIsDeleteModalOpen(false)}
        onDelete={handleDeleteProject}
        projectName={project.name}
      />
    </div>
  );
};

export default ProjectManagerView;