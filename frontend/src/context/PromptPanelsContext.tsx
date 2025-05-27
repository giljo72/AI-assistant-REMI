import React, { createContext, useContext, useState, ReactNode } from 'react';

interface PromptPanelsContextType {
  isUserPromptPanelOpen: boolean;
  isSystemPromptPanelOpen: boolean;
  shouldOpenUserPromptAdd: boolean;
  openUserPromptPanel: () => void;
  closeUserPromptPanel: () => void;
  openSystemPromptPanel: () => void;
  closeSystemPromptPanel: () => void;
  toggleUserPromptPanel: () => void;
  toggleSystemPromptPanel: () => void;
  setShouldOpenUserPromptAdd: (value: boolean) => void;
}

const PromptPanelsContext = createContext<PromptPanelsContextType | undefined>(undefined);

export const PromptPanelsProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isUserPromptPanelOpen, setIsUserPromptPanelOpen] = useState(false);
  const [isSystemPromptPanelOpen, setIsSystemPromptPanelOpen] = useState(false);
  const [shouldOpenUserPromptAdd, setShouldOpenUserPromptAdd] = useState(false);

  const openUserPromptPanel = () => setIsUserPromptPanelOpen(true);
  const closeUserPromptPanel = () => setIsUserPromptPanelOpen(false);
  const toggleUserPromptPanel = () => setIsUserPromptPanelOpen(prev => !prev);

  const openSystemPromptPanel = () => setIsSystemPromptPanelOpen(true);
  const closeSystemPromptPanel = () => setIsSystemPromptPanelOpen(false);
  const toggleSystemPromptPanel = () => setIsSystemPromptPanelOpen(prev => !prev);

  return (
    <PromptPanelsContext.Provider 
      value={{ 
        isUserPromptPanelOpen, 
        isSystemPromptPanelOpen,
        shouldOpenUserPromptAdd,
        openUserPromptPanel, 
        closeUserPromptPanel,
        openSystemPromptPanel,
        closeSystemPromptPanel,
        toggleUserPromptPanel,
        toggleSystemPromptPanel,
        setShouldOpenUserPromptAdd
      }}
    >
      {children}
    </PromptPanelsContext.Provider>
  );
};

export const usePromptPanels = () => {
  const context = useContext(PromptPanelsContext);
  if (!context) {
    throw new Error('usePromptPanels must be used within a PromptPanelsProvider');
  }
  return context;
};