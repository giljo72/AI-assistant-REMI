import React, { useState, useEffect, useRef } from 'react';
import { Typography } from '@mui/material';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface TypewriterMessageProps {
  content: string;
  isNew: boolean;
  onTypingComplete?: () => void;
  fontSize?: {
    xs: string;
    sm: string;
  };
}

const TypewriterMessage: React.FC<TypewriterMessageProps> = ({ 
  content, 
  isNew, 
  onTypingComplete,
  fontSize = { xs: '0.875rem', sm: '1rem' }
}) => {
  const [displayedContent, setDisplayedContent] = useState(isNew ? '' : content);
  const [isTyping, setIsTyping] = useState(isNew);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isNew || !content) {
      setDisplayedContent(content);
      return;
    }

    let currentIndex = 0;
    const contentLength = content.length;
    
    // Determine typing speed based on content length
    const baseSpeed = 45; // Base milliseconds per character (comfortable reading speed)
    const fastSpeed = 12; // Speed for large content (still visible but faster)
    const isLargeContent = contentLength > 1000;
    const typingSpeed = isLargeContent ? fastSpeed : baseSpeed;
    
    // Calculate chunk size for smoother animation
    const chunkSize = isLargeContent ? 3 : 1; // Smaller chunks for better visibility

    const typeWriter = () => {
      if (currentIndex < contentLength) {
        const nextChunk = content.slice(currentIndex, currentIndex + chunkSize);
        setDisplayedContent((prev) => prev + nextChunk);
        currentIndex += chunkSize;
        
        // Auto-scroll to bottom as content is typed
        if (containerRef.current) {
          // Find the scrollable chat history container
          let scrollContainer = containerRef.current.parentElement;
          while (scrollContainer && !scrollContainer.classList.contains('MuiBox-root')) {
            scrollContainer = scrollContainer.parentElement;
          }
          
          // Look for the container with overflow-y: auto
          const chatHistoryContainer = document.querySelector('[style*="overflow-y: auto"]');
          if (chatHistoryContainer && chatHistoryContainer instanceof HTMLElement) {
            chatHistoryContainer.scrollTop = chatHistoryContainer.scrollHeight;
          }
        }
      } else {
        // Typing complete
        setIsTyping(false);
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
        }
        if (onTypingComplete) {
          onTypingComplete();
        }
      }
    };

    intervalRef.current = setInterval(typeWriter, typingSpeed);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [content, isNew, onTypingComplete]);

  return (
    <div ref={containerRef}>
      <div style={{ position: 'relative' }}>
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
              <Typography variant="body1" sx={{ mb: 1, fontSize }}>
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
          }}
        >
          {displayedContent}
        </ReactMarkdown>
        {isTyping && (
          <span style={{
            animation: 'blink 1s infinite',
            opacity: 0.7,
            marginLeft: '2px',
            position: 'absolute',
            bottom: '4px'
          }}>
            ▋
          </span>
        )}
      </div>
    </div>
  );
};

export default TypewriterMessage;