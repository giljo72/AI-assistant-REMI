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
  Tooltip,
  Select,
  MenuItem,
  FormControl,
} from '@mui/material';
import {
  Send as SendIcon,
  Mic as MicIcon,
  ContentCopy as CopyIcon,
  Stop as StopIcon
} from '@mui/icons-material';
import ContextStatusIndicators from './ContextStatusIndicators';
import { RootState } from '../../store';
import { 
  toggleProjectPrompt, 
  toggleGlobalData, 
  toggleProjectDocuments 
} from '../../store/projectSettingsSlice';
import { useContextControls } from '../../context/ContextControlsContext';

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
    modelInfo?: {
      name: string;
      type: string;
    };
  }>;
  isProcessing: boolean;
  onSendMessage: (content: string, modelName?: string) => void;
  onEnableMic?: () => void;
  onStopGeneration?: () => void;
}

const ChatView: React.FC<ChatViewProps> = ({
  projectName,
  chatName,
  projectId,
  chatId,
  messages,
  isProcessing,
  onSendMessage,
  onEnableMic,
  onStopGeneration
}) => {
  const [input, setInput] = useState('');
  const [selectedModel, setSelectedModel] = useState<string>('qwen2.5:32b-instruct-q4_K_M');
  const endOfMessagesRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null);
  
  const dispatch = useDispatch();
  const { projectPromptEnabled, globalDataEnabled, projectDocumentsEnabled, contextMode } = useSelector(
    (state: RootState) => state.projectSettings
  );
  const { openContextControls } = useContextControls();

  // Scroll to bottom when messages change
  useEffect(() => {
    if (endOfMessagesRef.current) {
      endOfMessagesRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const handleSendMessage = () => {
    if (input.trim() && !isProcessing) {
      const model = selectedModel;
      onSendMessage(input.trim(), model);
      setInput('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleCopyMessage = async (content: string, messageId: string) => {
    try {
      await navigator.clipboard.writeText(content);
      setCopiedMessageId(messageId);
      setTimeout(() => setCopiedMessageId(null), 2000);
    } catch (err) {
      console.error('Failed to copy message:', err);
    }
  };

  return (
    <Box sx={{ 
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden'
    }}>
      {/* Header - Fixed at top */}
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
          flexShrink: 0
        }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
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
          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
            <Typography variant="caption" sx={{ color: '#999' }}>Mode:</Typography>
            <Select
              size="small"
              value="balanced"
              sx={{
                backgroundColor: '#1a2b47',
                color: '#d4af37',
                fontSize: '0.75rem',
                height: '24px',
                '& .MuiOutlinedInput-notchedOutline': {
                  border: 'none',
                },
                '& .MuiSelect-select': {
                  padding: '2px 8px',
                }
              }}
            >
              <MenuItem value="balanced">Balanced</MenuItem>
              <MenuItem value="business_deep">Business Deep</MenuItem>
              <MenuItem value="business_fast">Business Fast</MenuItem>
              <MenuItem value="development">Development</MenuItem>
              <MenuItem value="quick">Quick Response</MenuItem>
            </Select>
          </Box>
        </Box>
      </Paper>
      
      {/* Scrollable Chat History Area */}
      <Box sx={{ 
        flexGrow: 1,
        overflowY: 'auto',
        overflowX: 'hidden',
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: '#080d13',
        '&::-webkit-scrollbar': {
          width: '8px',
        },
        '&::-webkit-scrollbar-track': {
          backgroundColor: '#121922',
        },
        '&::-webkit-scrollbar-thumb': {
          backgroundColor: '#FFC000', // Yellow scrollbar
          borderRadius: '4px',
          '&:hover': {
            backgroundColor: '#e6ac00',
          }
        }
      }}>
        {/* Messages Area */}
        <Box 
          ref={messagesContainerRef}
          sx={{ 
            flexGrow: 0,
            flexShrink: 0,
            padding: {
              xs: '12px', // Smaller padding on mobile
              sm: '16px'  // Normal padding on larger screens
            },
            minHeight: '200px',
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
                {message.sender === 'user' ? 'You' : 'Assistant'}
                {message.sender === 'assistant' && message.modelInfo && (
                  <span style={{ color: '#d4af37', fontWeight: 'bold' }}> ({message.modelInfo.name})</span>
                )}
                {' • '}{message.timestamp}
              </Typography>
              
              <Box sx={{ 
                display: 'flex', 
                alignItems: 'flex-start',
                gap: '8px'
              }}>
                <Paper
                  elevation={1}
                  sx={{
                    padding: {
                      xs: '10px 14px', // Smaller padding on mobile
                      sm: '12px 16px'  // Normal padding on larger screens
                    },
                    width: 'fit-content',
                    minWidth: '200px',
                    maxWidth: '100%', // Allow full width expansion
                    backgroundColor: message.sender === 'user' ? '#d4af37' : '#1a2b47',
                    color: message.sender === 'user' ? '#000000' : '#ffffff',
                    borderRadius: message.sender === 'user' ? '16px 16px 0 16px' : '16px 16px 16px 0',
                    wordBreak: 'break-word',
                    overflowWrap: 'break-word',
                    overflow: 'visible'
                  }}
                >
                  <Typography 
                    variant="body1" 
                    sx={{ 
                      whiteSpace: 'pre-wrap',
                      wordBreak: 'break-word',
                      fontSize: {
                        xs: '0.875rem', // Smaller on mobile
                        sm: '1rem'      // Normal on larger screens
                      }
                    }}
                  >
                    {message.content}
                  </Typography>
                </Paper>
                
                {/* Copy button for assistant messages */}
                {message.sender === 'assistant' && (
                  <Tooltip title={copiedMessageId === message.id ? "Copied!" : "Copy message"}>
                    <IconButton
                      size="small"
                      onClick={() => handleCopyMessage(message.content, message.id)}
                      sx={{
                        opacity: 0.6,
                        '&:hover': {
                          opacity: 1,
                          backgroundColor: 'rgba(255, 255, 255, 0.1)'
                        },
                        color: '#FFC000',
                        padding: '4px'
                      }}
                    >
                      <CopyIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                )}
              </Box>
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
              <Typography 
                variant="body2" 
                sx={{ 
                  color: '#888',
                  fontSize: {
                    xs: '0.75rem',
                    sm: '0.875rem'
                  }
                }}
              >
                Processing...
              </Typography>
            </Box>
          )}
          
          <div ref={endOfMessagesRef} />
          {/* Buffer space to ensure last message isn't hidden behind input */}
          <Box sx={{ height: '80px' }} />
        </Box>
      </Box>
      
      {/* Fixed Input Area at Bottom */}
      <Box sx={{ 
        flexShrink: 0,
        backgroundColor: '#080d13',
        borderTop: '1px solid #152238',
        padding: {
          xs: '12px',
          sm: '16px'
        }
      }}>
        {/* Model Selector */}
        <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="caption" sx={{ color: '#999' }}>Model:</Typography>
          <FormControl size="small" sx={{ minWidth: 200 }}>
            <Select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              sx={{
                backgroundColor: '#1a2b47',
                color: '#fff',
                fontSize: '0.875rem',
                height: '32px',
                '& .MuiOutlinedInput-notchedOutline': {
                  borderColor: '#152238',
                },
                '&:hover .MuiOutlinedInput-notchedOutline': {
                  borderColor: '#d4af37',
                },
                '& .MuiSelect-icon': {
                  color: '#d4af37',
                }
              }}
            >
              <MenuItem value="qwen2.5:32b-instruct-q4_K_M">Qwen 2.5 32B (Default) - Full document/RAG support</MenuItem>
              <MenuItem value="llama3.1:70b-instruct-q4_K_M">Llama 3.1 70B (Solo Mode) - Deep reasoning only</MenuItem>
              <MenuItem value="mistral-nemo:latest">Mistral Nemo - Quick responses</MenuItem>
              <MenuItem value="deepseek-coder-v2:16b-lite-instruct-q4_K_M">DeepSeek Coder - Self-aware coding mode</MenuItem>
            </Select>
          </FormControl>
          <Typography variant="caption" sx={{ color: '#666', flex: 1 }}>
            {selectedModel === 'qwen2.5:32b-instruct-q4_K_M' && 'Primary model with full document/RAG support'}
            {selectedModel === 'llama3.1:70b-instruct-q4_K_M' && 'Solo mode - All other models unloaded for max power'}
            {selectedModel === 'mistral-nemo:latest' && 'Fast responses when speed is priority'}
            {selectedModel === 'deepseek-coder-v2:16b-lite-instruct-q4_K_M' && 'Code generation in self-aware mode'}
          </Typography>
        </Box>
        
        {/* Input Area */}
        <Paper
          elevation={3}
          sx={{
            backgroundColor: '#152238',
            borderRadius: '8px',
            padding: {
              xs: '12px',
              sm: '16px'
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
                    xs: '8px',
                    sm: '12px'
                  },
                  '& fieldset': {
                    border: 'none',
                  },
                  '& textarea': {
                    color: '#ffffff',
                    fontSize: {
                      xs: '0.875rem',
                      sm: '1rem'
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
                  backgroundColor: 'rgba(212, 175, 55, 0.1)',
                  '&:hover': {
                    backgroundColor: 'rgba(212, 175, 55, 0.2)',
                  },
                  color: '#d4af37',
                  width: {
                    xs: '36px',
                    sm: '40px'
                  },
                  height: {
                    xs: '36px',
                    sm: '40px'
                  }
                }}
                onClick={onEnableMic}
              >
                <MicIcon fontSize={window.innerWidth < 600 ? "small" : "medium"} />
              </IconButton>
            )}
            
            {/* Show stop button when processing, send button otherwise */}
            {isProcessing && onStopGeneration ? (
              <Tooltip title="Stop generating">
                <IconButton 
                  color="error"
                  sx={{ 
                    ml: 1,
                    backgroundColor: 'rgba(244, 67, 54, 0.8)',
                    '&:hover': {
                      backgroundColor: '#f44336',
                    },
                    color: '#ffffff',
                    width: {
                      xs: '36px',
                      sm: '40px'
                    },
                    height: {
                      xs: '36px',
                      sm: '40px'
                    }
                  }}
                  onClick={onStopGeneration}
                >
                  <StopIcon fontSize={window.innerWidth < 600 ? "small" : "medium"} />
                </IconButton>
              </Tooltip>
            ) : (
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
                    xs: '36px',
                    sm: '40px'
                  },
                  height: {
                    xs: '36px',
                    sm: '40px'
                  }
                }}
                onClick={handleSendMessage}
                disabled={isProcessing || !input.trim()}
              >
                <SendIcon fontSize={window.innerWidth < 600 ? "small" : "medium"} />
              </IconButton>
            )}
          </Box>
        </Paper>
        
        {/* Context Controls - Below the chat input */}
        <ContextStatusIndicators 
          isProjectPromptEnabled={projectPromptEnabled}
          isGlobalDataEnabled={globalDataEnabled}
          isProjectDocumentsEnabled={projectDocumentsEnabled}
          onToggleProjectPrompt={() => dispatch(toggleProjectPrompt())}
          onToggleGlobalData={() => dispatch(toggleGlobalData())}
          onToggleProjectDocuments={() => dispatch(toggleProjectDocuments())}
          onOpenContextControls={openContextControls}
          contextMode={contextMode}
        />
      </Box>
    </Box>
  );
};

export default ChatView;