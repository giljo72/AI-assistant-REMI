import React, { useState, useEffect, useRef } from 'react';
import { Typography } from '@mui/material';

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
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
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
      <Typography 
        variant="body1" 
        sx={{ 
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-word',
          fontSize: fontSize,
          position: 'relative',
          '&::after': isTyping ? {
            content: '"▋"',
            animation: 'blink 1s infinite',
            color: 'inherit',
            opacity: 0.7,
            marginLeft: '2px'
          } : {}
        }}
      >
        {displayedContent}
      </Typography>
    </div>
  );
};

export default TypewriterMessage;