import React, { useState, useRef, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import {
  Box,
  Paper,
  Typography,
  TextField,
  IconButton,
  CircularProgress,
} from '@mui/material';
import {
  Send as SendIcon,
  Mic as MicIcon
} from '@mui/icons-material';
import ContextStatusIndicators from './ContextStatusIndicators';
import UserPromptsPanel from './UserPromptsPanel';
import { RootState } from '../../store';
// Import toggle actions from projectSettingsSlice
import { 
  toggleProjectPrompt, 
  toggleGlobalData, 
  toggleProjectDocuments 
} from '../../store/projectSettingsSlice';

interface ChatViewProps {
  projectName: string;  
  chatName: string;     
  projectId?: string;   
  chatId?: string | null;
  messages: Array<{
    id: string;
    content: string;
    sender: 'user' | 'assistant';
    timestamp: string;
  }>;
  isProcessing: boolean;
  onSendMessage: (content: string) => void;
  onEnableMic?: () => void;
}

const ChatView: React.FC<ChatViewProps> = ({
  projectName,
  chatName,
  messages,
  isProcessing,
  onSendMessage,
  onEnableMic
}) => {
  const [input, setInput] = useState('');
  const [userPromptsExpanded, setUserPromptsExpanded] = useState(false);
  const [contextControlsOpen, setContextControlsOpen] = useState(false); // Add state for context controls
  const endOfMessagesRef = useRef<HTMLDivElement>(null);
  const dispatch = useDispatch(); // Initialize dispatch
  
  // Get the active prompt from Redux store
  const { prompts } = useSelector((state: RootState) => state.userPrompts);
  const activePrompt = prompts.find((p: any) => p.active); // Add type annotation to avoid 'any' error
  
  // Project settings from Redux store
  const { projectPromptEnabled, globalDataEnabled, projectDocumentsEnabled } = useSelector(
    (state: RootState) => state.projectSettings
  );

  useEffect(() => {
    // Scroll to bottom when messages change
    if (endOfMessagesRef.current) {
      endOfMessagesRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const handleSendMessage = () => {
    if (input.trim() && !isProcessing) {
      onSendMessage(input.trim());
      setInput('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Paper 
        elevation={2}
        sx={{
          backgroundColor: '#152238', // Darker navy
          color: '#ffffff',
          padding: '12px 20px',
          borderRadius: '8px 8px 0 0',
          marginBottom: '16px'
        }}
      >
        <Typography variant="h6">
          {projectName} / {chatName}
        </Typography>
      </Paper>
      
      {/* Context Controls */}
      <ContextStatusIndicators 
        isProjectPromptEnabled={projectPromptEnabled}
        isGlobalDataEnabled={globalDataEnabled}
        isProjectDocumentsEnabled={projectDocumentsEnabled}
        onToggleProjectPrompt={() => dispatch(toggleProjectPrompt())}
        onToggleGlobalData={() => dispatch(toggleGlobalData())}
        onToggleProjectDocuments={() => dispatch(toggleProjectDocuments())}
        onOpenContextControls={() => setContextControlsOpen(true)}
      />
      
      {/* User Prompts Panel */}
      <UserPromptsPanel 
        expanded={userPromptsExpanded}
        onToggleExpand={() => setUserPromptsExpanded(!userPromptsExpanded)}
      />
      
      {/* Messages Area */}
      <Box 
        sx={{ 
          flexGrow: 1, 
          overflowY: 'auto',
          padding: '0 16px',
          backgroundColor: '#f5f5f5',
          borderRadius: '8px',
          marginBottom: '16px'
        }}
      >
        {messages.map((message) => (
          <Box
            key={message.id}
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: message.sender === 'user' ? 'flex-end' : 'flex-start',
              marginBottom: '16px',
              paddingTop: '16px'
            }}
          >
            <Typography 
              variant="caption" 
              sx={{ 
                marginBottom: '4px',
                color: '#666',
                fontSize: '0.7rem'
              }}
            >
              {message.sender === 'user' ? 'You' : 'Assistant'} • {message.timestamp}
            </Typography>
            
            <Paper
              elevation={1}
              sx={{
                padding: '12px 16px',
                maxWidth: '80%',
                backgroundColor: message.sender === 'user' ? '#d4af37' : '#1a2b47',
                color: message.sender === 'user' ? '#000000' : '#ffffff',
                borderRadius: message.sender === 'user' ? '16px 16px 0 16px' : '16px 16px 16px 0',
              }}
            >
              <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                {message.content}
              </Typography>
            </Paper>
          </Box>
        ))}
        
        {/* Processing indicator */}
        {isProcessing && (
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              padding: '12px',
              marginBottom: '16px'
            }}
          >
            <CircularProgress size={20} sx={{ color: '#d4af37', marginRight: '12px' }} />
            <Typography variant="body2" sx={{ color: '#666' }}>
              Processing...
            </Typography>
          </Box>
        )}
        
        <div ref={endOfMessagesRef} />
      </Box>
      
      {/* Input Area */}
      <Paper
        elevation={3}
        sx={{
          backgroundColor: '#152238', // Darker navy
          borderRadius: '0 0 8px 8px',
          padding: '16px',
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'flex-end' }}>
          <TextField
            fullWidth
            multiline
            maxRows={6}
            placeholder="Type your message here..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isProcessing}
            sx={{
              backgroundColor: '#f5f5f5',
              borderRadius: '8px',
              '& .MuiOutlinedInput-root': {
                padding: '12px',
                '& fieldset': {
                  border: 'none',
                },
              },
            }}
          />
          
          {onEnableMic && (
            <IconButton 
              color="primary" 
              sx={{ 
                ml: 1,
                backgroundColor: 'rgba(212, 175, 55, 0.8)',
                '&:hover': {
                  backgroundColor: '#d4af37',
                },
                color: '#000000'
              }}
              onClick={onEnableMic}
            >
              <MicIcon />
            </IconButton>
          )}
          
          <IconButton 
            color="primary" 
            sx={{ 
              ml: 1,
              backgroundColor: 'rgba(212, 175, 55, 0.8)',
              '&:hover': {
                backgroundColor: '#d4af37',
              },
              color: '#000000'
            }}
            onClick={handleSendMessage}
            disabled={isProcessing || !input.trim()}
          >
            <SendIcon />
          </IconButton>
        </Box>
      </Paper>
    </Box>
  );
};

export default ChatView;