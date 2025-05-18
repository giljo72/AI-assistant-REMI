// File: frontend/src/components/chat/ChatView.tsx

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
import { RootState } from '../../store';
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
  const endOfMessagesRef = useRef<HTMLDivElement>(null);
  const dispatch = useDispatch();
  
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
      {/* Header - Improved responsive typography */}
      <Paper 
        elevation={2}
        sx={{
          backgroundColor: '#152238', // Darker navy
          color: '#ffffff',
          padding: {
            xs: '8px 16px',  // Smaller padding on mobile
            sm: '12px 20px'  // Normal padding on larger screens
          },
          borderRadius: '8px 8px 0 0',
          marginBottom: '16px'
        }}
      >
        <Typography 
          variant="h6" 
          sx={{ 
            fontSize: { 
              xs: '1rem',     // Smaller on mobile
              sm: '1.125rem',  // Default size on tablets
              md: '1.25rem'    // Larger on desktop
            },
            fontWeight: 'bold'
          }}
        >
          {projectName} / {chatName}
        </Typography>
      </Paper>
      
      {/* Messages Area - Improved contrast and spacing */}
      <Box 
        sx={{ 
          flexGrow: 1, 
          overflowY: 'auto',
          padding: {
            xs: '0 12px', // Smaller padding on mobile
            sm: '0 16px'  // Normal padding on larger screens
          },
          backgroundColor: '#080d13', // Much darker background as per PDF
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
                fontSize: {
                  xs: '0.65rem', // Smaller on mobile
                  sm: '0.7rem'   // Normal on larger screens
                }
              }}
            >
              {message.sender === 'user' ? 'You' : 'Assistant'} • {message.timestamp}
            </Typography>
            
            <Paper
              elevation={1}
              sx={{
                padding: {
                  xs: '10px 14px', // Smaller padding on mobile
                  sm: '12px 16px'  // Normal padding on larger screens
                },
                maxWidth: {
                  xs: '90%', // Wider on mobile
                  sm: '80%'  // Normal width on larger screens
                },
                backgroundColor: message.sender === 'user' ? '#d4af37' : '#1a2b47',
                color: message.sender === 'user' ? '#000000' : '#ffffff',
                borderRadius: message.sender === 'user' ? '16px 16px 0 16px' : '16px 16px 16px 0',
              }}
            >
              <Typography 
                variant="body1" 
                sx={{ 
                  whiteSpace: 'pre-wrap',
                  fontSize: {
                    xs: '0.875rem', // Smaller on mobile
                    sm: '1rem'      // Normal on larger screens
                  }
                }}
              >
                {message.content}
              </Typography>
            </Paper>
          </Box>
        ))}
        
        {/* Processing indicator - Improved visibility */}
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
            <Typography 
              variant="body2" 
              sx={{ 
                color: '#888', // Slightly brighter for better visibility
                fontSize: {
                  xs: '0.75rem', // Smaller on mobile
                  sm: '0.875rem' // Normal on larger screens
                }
              }}
            >
              Processing...
            </Typography>
          </Box>
        )}
        
        <div ref={endOfMessagesRef} />
      </Box>
      
      {/* Input Area - Improved responsive design */}
      <Paper
        elevation={3}
        sx={{
          backgroundColor: '#152238', // Darker navy
          borderRadius: '8px',
          padding: {
            xs: '12px', // Smaller padding on mobile
            sm: '16px'  // Normal padding on larger screens
          },
          marginBottom: '16px',
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
              backgroundColor: '#1a2b47',
              borderRadius: '8px',
              '& .MuiOutlinedInput-root': {
                padding: {
                  xs: '8px', // Smaller padding on mobile
                  sm: '12px' // Normal padding on larger screens
                },
                '& fieldset': {
                  border: 'none',
                },
                '& textarea': {
                  color: '#ffffff', // White text
                  fontSize: {
                    xs: '0.875rem', // Smaller on mobile
                    sm: '1rem'      // Normal on larger screens
                  }
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
                color: '#000000',
                width: {
                  xs: '36px', // Smaller on mobile
                  sm: '40px'  // Normal on larger screens
                },
                height: {
                  xs: '36px', // Smaller on mobile
                  sm: '40px'  // Normal on larger screens
                }
              }}
              onClick={onEnableMic}
            >
              <MicIcon fontSize={window.innerWidth < 600 ? "small" : "medium"} />
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
              color: '#000000',
              width: {
                xs: '36px', // Smaller on mobile
                sm: '40px'  // Normal on larger screens
              },
              height: {
                xs: '36px', // Smaller on mobile
                sm: '40px'  // Normal on larger screens
              }
            }}
            onClick={handleSendMessage}
            disabled={isProcessing || !input.trim()}
          >
            <SendIcon fontSize={window.innerWidth < 600 ? "small" : "medium"} />
          </IconButton>
        </Box>
      </Paper>
      
      {/* Context Controls - Now below the chat input */}
      <ContextStatusIndicators 
        isProjectPromptEnabled={projectPromptEnabled}
        isGlobalDataEnabled={globalDataEnabled}
        isProjectDocumentsEnabled={projectDocumentsEnabled}
        onToggleProjectPrompt={() => dispatch(toggleProjectPrompt())}
        onToggleGlobalData={() => dispatch(toggleGlobalData())}
        onToggleProjectDocuments={() => dispatch(toggleProjectDocuments())}
        onOpenContextControls={() => {}} // We'll handle this from the sidebar now
      />
    </Box>
  );
};

export default ChatView;