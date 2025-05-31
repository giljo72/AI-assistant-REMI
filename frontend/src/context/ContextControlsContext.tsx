import React, { createContext, useContext, useState, ReactNode } from 'react';

interface ContextControlsContextType {
  isOpen: boolean;
  openContextControls: () => void;
  closeContextControls: () => void;
}

const ContextControlsContext = createContext<ContextControlsContextType | undefined>(undefined);

export const ContextControlsProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isOpen, setIsOpen] = useState(false);

  const openContextControls = () => setIsOpen(true);
  const closeContextControls = () => setIsOpen(false);

  return (
    <ContextControlsContext.Provider value={{ isOpen, openContextControls, closeContextControls }}>
      {children}
    </ContextControlsContext.Provider>
  );
};

export const useContextControls = () => {
  const context = useContext(ContextControlsContext);
  if (!context) {
    throw new Error('useContextControls must be used within a ContextControlsProvider');
  }
  return context;
};