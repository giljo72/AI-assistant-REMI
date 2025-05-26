// File: frontend/src/components/layout/MainLayout.tsx
import React, { ReactNode, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import ProjectSidebar from '../sidebar/ProjectSidebar';
import UserPromptsPanel from '../chat/UserPromptsPanel';
import SystemPromptsPanel from '../chat/SystemPromptsPanel';
import ContextControlsPanel from '../modals/ContextControlsPanel';
import { RootState } from '../../store';
import { useNavigation } from '../../hooks/useNavigation';
import { useContextControls } from '../../context/ContextControlsContext';
import { Icon } from '../common/Icon';

type MainLayoutProps = {
  children: ReactNode;
};

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const dispatch = useDispatch();
  const { projectPromptEnabled, globalDataEnabled, projectDocumentsEnabled, contextMode } = useSelector(
    (state: RootState) => state.projectSettings
  );
  const { isOpen: isContextControlsOpen, openContextControls, closeContextControls } = useContextControls();
  
  // Get navigation state using our custom hook
  const { activeView } = useNavigation();

  return (
    <div className="flex h-screen bg-navy text-white overflow-hidden">
      {/* Sidebar */}
      <div className="w-80 bg-navy-light border-r border-gold overflow-y-auto flex flex-col" onClick={(e) => e.stopPropagation()}>
        {/* Project sidebar takes the top portion */}
        <div className="flex-1 overflow-y-auto">
          <ProjectSidebar />
        </div>
        
        {/* User Prompts and Context Controls in the bottom portion */}
        <div className="p-3 border-t border-navy">
          {/* Context Settings Button */}
          <button 
            onClick={openContextControls}
            className="w-full py-2 mb-4 flex items-center justify-center bg-gold/20 hover:bg-gold/30 text-gold font-medium rounded transition-colors"
          >
            <Icon name="settings" size={16} className="mr-1" />
            Context Settings
          </button>
          
          {/* System Prompts Panel */}
          <SystemPromptsPanel expanded={false} />
          
          {/* User Prompts Panel */}
          <UserPromptsPanel expanded={false} />
        </div>
      </div>
      
      {/* Main content area */}
      <div className="flex-1 flex flex-col min-h-0">
        <header className="bg-navy-light p-4 border-b border-gold flex justify-between items-center flex-shrink-0">
          <h1 className="text-2xl font-bold text-gold">AI Assistant</h1>
          
          {/* View indicator showing current view */}
          <div className="flex items-center">
            <span className="text-sm text-gold">
              View: <span className="font-bold">{activeView.charAt(0).toUpperCase() + activeView.slice(1)}</span>
            </span>
          </div>
        </header>
        <main className="flex-1 overflow-y-auto p-4 min-h-0">
          {children}
        </main>
      </div>
      
      {/* Context Controls Modal */}
      <ContextControlsPanel
        isOpen={isContextControlsOpen}
        onClose={closeContextControls}
        onApplySettings={(settings) => {
          // Update the context mode in Redux
          dispatch(setContextMode(settings.mode));
          closeContextControls();
        }}
        initialSettings={{
          mode: contextMode,
          contextDepth: 50,
          useProjectDocs: projectPromptEnabled,
          useProjectChats: true,
          useAllDocs: globalDataEnabled,
          useAllChats: false,
        }}
      />
    </div>
  );
};

export default MainLayout;