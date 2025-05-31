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
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import systemService from '../../services/systemService';
import ContextStatusIndicators from './ContextStatusIndicators';
import { RootState } from '../../store';
import { Icon } from '../common/Icon';
import SendIcon from '@mui/icons-material/Send';
import StopIcon from '@mui/icons-material/Stop';
import { useContextControls } from '../../context/ContextControlsContext';
import { usePromptPanels } from '../../context/PromptPanelsContext';
import { useNavigation } from '../../hooks/useNavigation';
import {
  setCurrentChat,
  toggleSystemPrompt as toggleChatSystemPrompt,
  toggleUserPrompt as toggleChatUserPrompt,
  toggleProjectPrompt as toggleChatProjectPrompt,
  toggleGlobalData as toggleChatGlobalData,
  toggleProjectDocuments as toggleChatProjectDocuments,
  selectCurrentChatSettings,
} from '../../store/chatSettingsSlice';
import ActionApprovalModal from '../modals/ActionApprovalModal';
import { selfAwareService, ActionRequest } from '../../services/selfAwareService';
import { useAuth } from '../../context/AuthContext';

interface ChatViewProps {
  projectName: string;  
  chatName: string;     
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
  chatId,
  messages,
  isProcessing,
  onSendMessage,
  onEnableMic,
  onStopGeneration
}) => {
  const [input, setInput] = useState('');
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [availableModels, setAvailableModels] = useState<any[]>([]);
  const endOfMessagesRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null);
  
  // Self-aware mode approval state
  const [pendingAction, setPendingAction] = useState<ActionRequest | null>(null);
  const [showApprovalModal, setShowApprovalModal] = useState(false);
  
  const dispatch = useDispatch();
  const { openContextControls } = useContextControls();
  const { openUserPromptPanel, openSystemPromptPanel } = usePromptPanels();
  const { user } = useAuth();
  const { navigateToView } = useNavigation();
  
  // Get chat-specific settings
  const chatSettings = useSelector((state: RootState) => selectCurrentChatSettings(state));
  const { prompts: userPrompts, activePromptId } = useSelector((state: RootState) => state.userPrompts);
  
  // Find active user prompt using Redux activePromptId
  const activeUserPrompt = userPrompts.find(p => p.id === activePromptId);

  // Set current chat when component mounts or chat changes
  useEffect(() => {
    if (chatId) {
      dispatch(setCurrentChat(chatId));
    }
    return () => {
      // Clear current chat when unmounting
      dispatch(setCurrentChat(null));
    };
  }, [chatId, dispatch]);

  // Listen for action approval requests in self-aware mode
  useEffect(() => {
    // Check if we're in self-aware mode and user is admin
    if (chatSettings?.contextMode === 'self-aware' && user?.role === 'admin') {
      // Connect WebSocket for action approvals
      selfAwareService.connectWebSocket();
      
      // Subscribe to action requests
      const unsubscribe = selfAwareService.onActionRequest((action) => {
        setPendingAction(action);
        setShowApprovalModal(true);
      });

      return () => {
        unsubscribe();
        // Note: We don't disconnect WebSocket here as it might be used by other components
      };
    }
  }, [chatSettings?.contextMode, user]);

  // Fetch active model from backend on mount
  useEffect(() => {
    const fetchModels = async () => {
      try {
        // First, get active model quickly
        const activeModel = await systemService.getActiveModelQuick();
        
        // Then fetch full model list in background
        const models = await systemService.getAvailableModels();
        console.log('✅ Available models received:', models);
        
        // Filter out embeddings models and keep only chat models
        const chatModels = models.filter((m: any) => 
          !m.name.includes('embedqa') && 
          m.last_used !== 'Embeddings' &&
          // Include Llama 70B even though it's NIM
          (m.type !== 'nvidia-nim' || 
           m.name === 'llama3.1:70b-instruct-q4_K_M' || 
           m.name === 'meta/llama-3.1-70b-instruct')
        );
        setAvailableModels(chatModels);
        
        // Validate that the active model exists in the available models list
        const modelExists = chatModels.some((m: any) => m.name === activeModel);
        
        if (modelExists) {
          // Use the active model if it exists in the list
          setSelectedModel(activeModel);
        } else if (chatModels.length > 0) {
          // If active model doesn't exist, find a suitable default
          console.warn(`Active model "${activeModel}" not found in available models, selecting default`);
          
          // Prefer Qwen if available, otherwise use first available model
          const defaultModel = chatModels.find((m: any) => m.name.includes('qwen2.5:32b')) || 
                              chatModels.find((m: any) => m.name.includes('qwen')) || 
                              chatModels[0];
          setSelectedModel(defaultModel.name);
        } else {
          // No models available - set empty string to avoid MUI error
          console.warn('No chat models available');
          setSelectedModel('');
        }
      } catch (error) {
        console.error('Failed to fetch models:', error);
        // Set empty string to avoid MUI error
        setSelectedModel('');
        setAvailableModels([]);
      }
    };
    fetchModels();
  }, []);

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

  // Handle approval of actions in self-aware mode
  const handleApproveAction = async (actionId: string) => {
    try {
      await selfAwareService.approveAction(actionId, true);
      setShowApprovalModal(false);
      setPendingAction(null);
    } catch (error) {
      console.error('Failed to approve action:', error);
    }
  };

  const handleDenyAction = async (actionId: string) => {
    try {
      await selfAwareService.approveAction(actionId, false);
      setShowApprovalModal(false);
      setPendingAction(null);
    } catch (error) {
      console.error('Failed to deny action:', error);
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
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <IconButton
              onClick={() => navigateToView('project')}
              sx={{
                color: '#FCC000',
                backgroundColor: 'transparent',
                border: '1px solid #FCC000',
                borderRadius: '4px',
                padding: '4px 8px',
                '&:hover': {
                  backgroundColor: '#FCC000',
                  color: '#000000'
                }
              }}
              size="small"
            >
              <Icon name="Home" size={16} />
            </IconButton>
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
        backgroundColor: '#080d13'
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
                {message.sender === 'assistant' && message.modelInfo && message.modelInfo.model_name && (
                  <span style={{ color: '#FCC000', fontWeight: 'bold' }}> ({message.modelInfo.model_name})</span>
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
                    backgroundColor: message.sender === 'user' ? '#FCC000' : '#1a2b47',
                    color: message.sender === 'user' ? '#000000' : '#ffffff',
                    borderRadius: message.sender === 'user' ? '16px 16px 0 16px' : '16px 16px 16px 0',
                    wordBreak: 'break-word',
                    overflowWrap: 'break-word',
                    overflow: 'visible'
                  }}
                >
                  {message.sender === 'assistant' ? (
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      components={{
                        code({ node, inline, className, children, ...props }) {
                          const match = /language-(\w+)/.exec(className || '');
                          return !inline && match ? (
                            <SyntaxHighlighter
                              style={vscDarkPlus}
                              language={match[1]}
                              PreTag="div"
                              customStyle={{
                                margin: '8px 0',
                                borderRadius: '6px',
                                fontSize: '0.9rem',
                                backgroundColor: '#0d1929', // Darker blue background
                                border: '1px solid #1a2b47', // Subtle border matching message bg
                              }}
                              {...props}
                            >
                              {String(children).replace(/\n$/, '')}
                            </SyntaxHighlighter>
                          ) : (
                            <code className={className} {...props} style={{ 
                              backgroundColor: '#0d1929', 
                              padding: '2px 4px', 
                              borderRadius: '3px',
                              fontSize: '0.9em',
                              border: '1px solid #1a2b47'
                            }}>
                              {children}
                            </code>
                          );
                        },
                        p: ({ children }) => (
                          <Typography variant="body1" sx={{ mb: 1, fontSize: { xs: '0.875rem', sm: '1rem' } }}>
                            {children}
                          </Typography>
                        ),
                        h1: ({ children }) => (
                          <Typography variant="h5" sx={{ mb: 2, mt: 2, fontWeight: 'bold' }}>{children}</Typography>
                        ),
                        h2: ({ children }) => (
                          <Typography variant="h6" sx={{ mb: 1.5, mt: 1.5, fontWeight: 'bold' }}>{children}</Typography>
                        ),
                        h3: ({ children }) => (
                          <Typography variant="subtitle1" sx={{ mb: 1, mt: 1, fontWeight: 'bold' }}>{children}</Typography>
                        ),
                        ul: ({ children }) => (
                          <Box component="ul" sx={{ pl: 3, mb: 1 }}>{children}</Box>
                        ),
                        ol: ({ children }) => (
                          <Box component="ol" sx={{ pl: 3, mb: 1 }}>{children}</Box>
                        ),
                      }}
                    >
                      {message.content}
                    </ReactMarkdown>
                  ) : (
                    <Typography 
                      variant="body1" 
                      sx={{ 
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-word',
                        fontSize: {
                          xs: '0.875rem',
                          sm: '1rem'
                        }
                      }}
                    >
                      {message.content}
                    </Typography>
                  )}
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
                      <Icon name="copy" size={16} />
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
              <CircularProgress size={20} sx={{ color: '#FCC000', marginRight: '12px' }} />
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
                  backgroundColor: 'rgba(252, 192, 0, 0.1)',
                  '&:hover': {
                    backgroundColor: 'rgba(252, 192, 0, 0.2)',
                  },
                  color: '#FCC000',
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
                <Icon name="microphone" size={window.innerWidth < 600 ? 20 : 24} />
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
                  <StopIcon sx={{ fontSize: window.innerWidth < 600 ? 20 : 24 }} />
                </IconButton>
              </Tooltip>
            ) : (
              <IconButton 
                color="primary"
                sx={{ 
                  ml: 1,
                  backgroundColor: 'rgba(252, 192, 0, 0.8)',
                  '&:hover': {
                    backgroundColor: '#FCC000',
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
                <SendIcon sx={{ fontSize: window.innerWidth < 600 ? 20 : 24 }} />
              </IconButton>
            )}
          </Box>
        </Paper>
        
        {/* Context Controls - Below the chat input */}
        <ContextStatusIndicators 
          isProjectPromptEnabled={chatSettings.isProjectPromptEnabled}
          isGlobalDataEnabled={chatSettings.isGlobalDataEnabled}
          isProjectDocumentsEnabled={chatSettings.isProjectDocumentsEnabled}
          isSystemPromptEnabled={chatSettings.isSystemPromptEnabled}
          isUserPromptEnabled={chatSettings.isUserPromptEnabled}
          activeUserPromptName={activeUserPrompt?.name || chatSettings.activeUserPromptName || ''}
          selectedModel={selectedModel}
          onToggleProjectPrompt={() => dispatch(toggleChatProjectPrompt())}
          onToggleGlobalData={() => dispatch(toggleChatGlobalData())}
          onToggleProjectDocuments={() => dispatch(toggleChatProjectDocuments())}
          onToggleSystemPrompt={() => dispatch(toggleChatSystemPrompt())}
          onToggleUserPrompt={() => dispatch(toggleChatUserPrompt())}
          onOpenContextControls={openContextControls}
          onOpenSystemPromptPanel={openSystemPromptPanel}
          onOpenUserPromptPanel={openUserPromptPanel}
          contextMode={chatSettings.contextMode}
        />
      </Box>

      {/* Action Approval Modal */}
      <ActionApprovalModal
        isOpen={showApprovalModal}
        action={pendingAction}
        onApprove={handleApproveAction}
        onDeny={handleDenyAction}
      />
    </Box>
  );
};

export default ChatView;