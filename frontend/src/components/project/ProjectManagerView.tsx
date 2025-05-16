import React, { useState, useEffect } from 'react';
import AddChatModal from '../modals/AddChatModal';
import { projectService, userPromptService } from '../../services';
import { Project, UserPrompt } from '../../services';

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
};

// Mock data for chats and files until we implement their APIs
const mockChats: Chat[] = [
  { id: '1', name: 'Research Question #1', projectId: '1', createdAt: '2025-05-10' },
  { id: '2', name: 'Literature Review', projectId: '1', createdAt: '2025-05-09' },
  { id: '3', name: 'Methodology Discussion', projectId: '1', createdAt: '2025-05-08' },
  { id: '4', name: 'Navigation Design', projectId: '2', createdAt: '2025-05-07' },
  { id: '5', name: 'Color Schemes', projectId: '2', createdAt: '2025-05-06' },
  { id: '6', name: 'Social Media Strategy', projectId: '3', createdAt: '2025-05-05' },
];

const mockFiles: File[] = [
  { id: '1', name: 'Research Paper.pdf', type: 'PDF', size: '1.2 MB', active: true, projectId: '1', addedAt: '2025-05-10' },
  { id: '2', name: 'Literature Notes.docx', type: 'DOCX', size: '538 KB', active: true, projectId: '1', addedAt: '2025-05-09' },
  { id: '3', name: 'Data Analysis.xlsx', type: 'XLSX', size: '724 KB', active: false, projectId: '1', addedAt: '2025-05-08' },
  { id: '4', name: 'Website Mockup.png', type: 'PNG', size: '2.4 MB', active: true, projectId: '2', addedAt: '2025-05-07' },
  { id: '5', name: 'Campaign Brief.pdf', type: 'PDF', size: '890 KB', active: true, projectId: '3', addedAt: '2025-05-06' },
];

type ProjectManagerViewProps = {
  projectId: string;
  onOpenChat?: (chatId: string) => void;
  onOpenFiles?: () => void;
};

const ProjectManagerView: React.FC<ProjectManagerViewProps> = ({ projectId, onOpenChat, onOpenFiles }) => {
  const [activeTab, setActiveTab] = useState<Tab>('overview');
  const [project, setProject] = useState<Project | null>(null);
  const [projectChats, setProjectChats] = useState<Chat[]>([]);
  const [projectFiles, setProjectFiles] = useState<File[]>([]);
  const [projectPrompts, setProjectPrompts] = useState<UserPrompt[]>([]);
  const [isAddChatModalOpen, setIsAddChatModalOpen] = useState(false);
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
        
        // Use mock data for chats and files for now
        const chats = mockChats.filter(chat => chat.projectId === projectId);
        setProjectChats(chats);
        
        const files = mockFiles.filter(file => file.projectId === projectId);
        setProjectFiles(files);
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

  const handleAddChat = (name: string) => {
    if (!project) return;
    
    const newChat: Chat = {
      id: (projectChats.length + 1).toString(),
      name,
      projectId: project.id,
      createdAt: new Date().toISOString().split('T')[0],
    };
    
    // Update local state
    setProjectChats([...projectChats, newChat]);
    
    // TODO: In the future, implement API call to create a chat
  };

  // Handler for opening a chat
  const handleOpenChat = (chatId: string) => {
    if (onOpenChat) {
      onOpenChat(chatId);
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
            <button className="px-3 py-1 bg-navy hover:bg-navy-lighter rounded text-sm">
              Modify
            </button>
            <button className="px-3 py-1 bg-red-700/30 hover:bg-red-700/50 text-red-400 rounded text-sm">
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
              onClick={() => setActiveTab('files')}
              className={`mr-4 py-2 px-1 ${
                activeTab === 'files'
                  ? 'border-b-2 border-gold text-gold'
                  : 'text-gray-400 hover:text-gray-300'
              }`}
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
                  <div key={file.id} className="p-2 bg-navy hover:bg-navy-lighter rounded cursor-pointer flex justify-between">
                    <span>{file.name}</span>
                    <div className="flex items-center space-x-2">
                      <span className={`w-2 h-2 rounded-full ${file.active ? 'bg-green-500' : 'bg-gray-500'}`}></span>
                      <span className="text-xs text-gray-400">{file.size}</span>
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
                    <button className="text-xs px-2 py-1 bg-red-700/30 hover:bg-red-700/50 text-red-400 rounded">
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
    </div>
  );
};

export default ProjectManagerView;