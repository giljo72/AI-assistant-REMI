import React, { useState, useEffect } from 'react';
import ContextStatusIndicators from './ContextStatusIndicators';
import ContextControlsPanel from '../modals/ContextControlsPanel';

// Define types for our data
type Message = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
};

type Chat = {
  id: string;
  name: string;
  projectId: string;
  messages: Message[];
};

// Mock project data
const mockProjects = [
  { id: '1', name: 'Research Paper' },
  { id: '2', name: 'Website Redesign' },
  { id: '3', name: 'Marketing Campaign' },
  { id: '4', name: 'Product Launch' },
];

// Mock data for chats
const mockChats: Chat[] = [
  {
    id: '1',
    name: 'Research Question #1',
    projectId: '1',
    messages: [
      {
        id: '1',
        role: 'user',
        content: 'Can you help me analyze the results of my experiment?',
        timestamp: '2025-05-10T10:15:00'
      },
      {
        id: '2',
        role: 'assistant',
        content: 'I\'d be happy to help analyze your experiment results. Could you provide more details about what type of experiment you conducted and what kind of data you collected?',
        timestamp: '2025-05-10T10:15:15'
      },
      {
        id: '3',
        role: 'user',
        content: 'It was a survey about user preferences for the new interface design. I have collected responses from 50 participants rating various aspects of the UI on a scale of 1-5.',
        timestamp: '2025-05-10T10:16:20'
      },
      {
        id: '4',
        role: 'assistant',
        content: 'Thanks for providing those details. To properly analyze your survey results, I would recommend:\n1. Calculate the average rating for each UI aspect\n2. Identify the highest and lowest rated features\n3. Look for correlations between different aspects\n4. Segment responses by user demographics if available\n\nWould you like me to help you with any specific part of this analysis?',
        timestamp: '2025-05-10T10:16:45'
      }
    ]
  },
  {
    id: '2',
    name: 'Literature Review',
    projectId: '1',
    messages: [
      {
        id: '1',
        role: 'user',
        content: 'Can you help me find relevant papers for my literature review on AI ethics?',
        timestamp: '2025-05-09T14:22:00'
      },
      {
        id: '2',
        role: 'assistant',
        content: 'I\'d be happy to help with your literature review on AI ethics. Could you specify any particular aspects of AI ethics you\'re focusing on?',
        timestamp: '2025-05-09T14:22:30'
      }
    ]
  },
  {
    id: '3',
    name: 'Methodology Discussion',
    projectId: '1',
    messages: [
      {
        id: '1',
        role: 'user',
        content: 'I need help structuring the methodology section of my paper.',
        timestamp: '2025-05-08T11:05:00'
      },
      {
        id: '2',
        role: 'assistant',
        content: 'I can definitely help with structuring your methodology section. A well-organized methodology typically includes these components:\n\n1. Research design overview\n2. Participant selection/sampling method\n3. Data collection procedures\n4. Measurement instruments or tools\n5. Data analysis approach\n6. Ethical considerations\n\nWhich part would you like to focus on first?',
        timestamp: '2025-05-08T11:06:00'
      }
    ]
  },
  {
    id: '4',
    name: 'Navigation Design',
    projectId: '2',
    messages: [
      {
        id: '1',
        role: 'user',
        content: 'What are some best practices for website navigation design?',
        timestamp: '2025-05-07T09:10:00'
      },
      {
        id: '2',
        role: 'assistant',
        content: 'Here are some best practices for website navigation design:\n1. Keep it simple and intuitive\n2. Use clear, descriptive labels\n3. Maintain consistency across pages\n4. Ensure mobile responsiveness\n5. Include a search function for larger sites\n6. Use visual hierarchy to guide users\n\nWould you like me to elaborate on any of these points?',
        timestamp: '2025-05-07T09:10:30'
      }
    ]
  }
];

type ChatViewProps = {
  projectId?: string;
  chatId?: string | null;
};

const ChatView: React.FC<ChatViewProps> = ({ projectId = '1', chatId = null }) => {
  const [activeChat, setActiveChat] = useState<Chat | null>(null);
  const [newMessage, setNewMessage] = useState('');
  const [projectName, setProjectName] = useState('');
  
  // Context controls state
  const [isProjectPromptEnabled, setIsProjectPromptEnabled] = useState(true);
  const [isGlobalDataEnabled, setIsGlobalDataEnabled] = useState(false);
  const [isProjectDocumentsEnabled, setIsProjectDocumentsEnabled] = useState(true);
  const [isContextControlsOpen, setIsContextControlsOpen] = useState(false);
  const [contextSettings, setContextSettings] = useState({
    mode: 'standard',
    contextDepth: 50,
    useProjectDocs: true,
    useProjectChats: true,
    useAllDocs: false,
    useAllChats: false,
  });

  // Effect to set active chat and project name based on projectId and chatId
  useEffect(() => {
    // If a specific chatId is provided, find that chat
    if (chatId) {
      const chat = mockChats.find(c => c.id === chatId);
      if (chat) {
        setActiveChat(chat);
        // Make sure the chat belongs to the active project
        if (chat.projectId !== projectId) {
          console.warn('Chat does not belong to the active project');
        }
      }
    } else {
      // Otherwise, find the first chat for this project
      const projectChat = mockChats.find(chat => chat.projectId === projectId);
      setActiveChat(projectChat || null);
    }
    
    // Find the project name
    const project = mockProjects.find(p => p.id === projectId);
    setProjectName(project?.name || '');
  }, [projectId, chatId]);

  // Handle sending a new message
  const handleSendMessage = () => {
    if (!newMessage.trim() || !activeChat) return;
    
    // In a real app, this would call an API
    console.log('Sending message:', newMessage);
    
    // For now, let's simulate adding the message to the UI
    const newUserMessage: Message = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: newMessage,
      timestamp: new Date().toISOString()
    };
    
    // Clone the active chat and add the new message
    const updatedChat = { 
      ...activeChat, 
      messages: [...activeChat.messages, newUserMessage] 
    };
    
    setActiveChat(updatedChat);
    setNewMessage('');
  };

  // Context controls handlers
  const handleToggleProjectPrompt = () => {
    setIsProjectPromptEnabled(prev => !prev);
  };

  const handleToggleGlobalData = () => {
    setIsGlobalDataEnabled(prev => !prev);
  };

  const handleToggleProjectDocuments = () => {
    setIsProjectDocumentsEnabled(prev => !prev);
  };

  const handleApplyContextSettings = (settings) => {
    setContextSettings(settings);
    
    // Apply settings to the indicators
    setIsProjectPromptEnabled(true); // Project prompt is always enabled in settings
    setIsGlobalDataEnabled(settings.useAllDocs || settings.useAllChats);
    setIsProjectDocumentsEnabled(settings.useProjectDocs);
  };

  // If no chat is active, show a message
  if (!activeChat) {
    return (
      <div className="h-full flex flex-col items-center justify-center bg-navy-light rounded-lg p-6">
        <p className="text-gray-400 text-center">
          No chats found for this project. Create a new chat to get started.
        </p>
        <button className="mt-4 px-4 py-2 bg-gold/20 hover:bg-gold/30 text-gold rounded text-sm flex items-center">
          <span className="mr-1">+</span> Create New Chat
        </button>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      <div className="bg-navy-light p-4 mb-4 rounded-lg flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-gold">{activeChat.name}</h2>
          <p className="text-gray-400 text-sm">Project: {projectName}</p>
        </div>
        <div className="flex gap-2">
          <button className="px-3 py-1 bg-navy hover:bg-navy-lighter rounded text-sm">
            Settings
          </button>
          <button className="px-3 py-1 bg-gold/20 hover:bg-gold/30 text-gold rounded text-sm">
            Context
          </button>
        </div>
      </div>
      
      {/* Context Status Indicators */}
      <ContextStatusIndicators
        isProjectPromptEnabled={isProjectPromptEnabled}
        isGlobalDataEnabled={isGlobalDataEnabled}
        isProjectDocumentsEnabled={isProjectDocumentsEnabled}
        onToggleProjectPrompt={handleToggleProjectPrompt}
        onToggleGlobalData={handleToggleGlobalData}
        onToggleProjectDocuments={handleToggleProjectDocuments}
        onOpenContextControls={() => setIsContextControlsOpen(true)}
      />
      
      <div className="flex-1 overflow-y-auto bg-navy-light rounded-lg p-4 mb-4">
        {/* Message history */}
        <div className="space-y-4">
          {activeChat.messages.map(message => (
            <div 
              key={message.id} 
              className={`p-3 rounded-lg ${message.role === 'user' ? 'bg-navy' : 'bg-navy-lighter'}`}
            >
              <p className="text-xs text-gray-400 mb-1">{message.role === 'user' ? 'You' : 'AI Assistant'}</p>
              <p className="whitespace-pre-line">{message.content}</p>
            </div>
          ))}
        </div>
      </div>
      
      {/* Message input */}
      <div className="bg-navy-light rounded-lg p-3">
        <div className="flex">
          <input 
            type="text" 
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            className="flex-1 bg-navy p-2 rounded-l-md focus:outline-none focus:ring-1 focus:ring-gold"
            placeholder="Type your message..."
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
          />
          <button 
            onClick={handleSendMessage}
            className="bg-gold text-navy font-medium px-4 rounded-r-md hover:bg-gold/90"
          >
            Send
          </button>
        </div>
      </div>

      {/* Context Controls Modal */}
      <ContextControlsPanel
        isOpen={isContextControlsOpen}
        onClose={() => setIsContextControlsOpen(false)}
        onApplySettings={handleApplyContextSettings}
        initialSettings={contextSettings}
      />
    </div>
  );
};

export default ChatView;