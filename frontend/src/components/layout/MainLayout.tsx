// File: frontend/src/components/layout/MainLayout.tsx
import React, { ReactNode, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import ProjectSidebar from '../sidebar/ProjectSidebar';
import UserPromptsPanel from '../chat/UserPromptsPanel';
import ContextControlsPanel from '../modals/ContextControlsPanel';
import { RootState } from '../../store';

type MainLayoutProps = {
  children: ReactNode;
  onProjectSelect: (projectId: string) => void;
  onOpenMainFiles?: () => void; // Add prop for opening main file manager
};

const MainLayout: React.FC<MainLayoutProps> = ({ children, onProjectSelect, onOpenMainFiles }) => {
  const [isContextControlsOpen, setIsContextControlsOpen] = useState(false);
  const dispatch = useDispatch();
  const { projectPromptEnabled, globalDataEnabled, projectDocumentsEnabled } = useSelector(
    (state: RootState) => state.projectSettings
  );

  return (
    <div className="flex h-screen bg-navy text-white overflow-hidden">
      {/* Sidebar */}
      <div className="w-64 bg-navy-light border-r border-gold overflow-y-auto flex flex-col" onClick={(e) => e.stopPropagation()}>
        {/* Project sidebar takes the top portion */}
        <div className="flex-1 overflow-y-auto">
          <ProjectSidebar 
            onProjectSelect={onProjectSelect} 
            onOpenMainFiles={onOpenMainFiles} 
          />
        </div>
        
        {/* User Prompts and Context Controls in the bottom portion */}
        <div className="p-3 border-t border-navy">
          {/* Context Settings Button */}
          <button 
            onClick={() => setIsContextControlsOpen(true)}
            className="w-full py-2 mb-4 flex items-center justify-center bg-gold/20 hover:bg-gold/30 text-gold font-medium rounded transition-colors"
          >
            <span className="mr-1">⚙</span> Context Settings
          </button>
          
          {/* User Prompts Panel */}
          <UserPromptsPanel expanded={false} />
        </div>
      </div>
      
      {/* Main content area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="bg-navy-light p-4 border-b border-gold flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gold">AI Assistant</h1>
          
          {/* Mode dropdown - simplified version */}
          <div className="flex items-center bg-navy px-3 py-1.5 rounded">
            <span className="text-sm text-gray-400 mr-2">Mode:</span>
            <select className="bg-navy text-white text-sm focus:outline-none focus:ring-1 focus:ring-gold rounded">
              <option>Standard</option>
              <option>Project Focus</option>
              <option>Deep Research</option>
              <option>Quick Response</option>
              <option>Custom</option>
            </select>
          </div>
        </header>
        <main className="flex-1 overflow-y-auto p-4">
          {children}
        </main>
      </div>
      
      {/* Context Controls Modal */}
      <ContextControlsPanel
        isOpen={isContextControlsOpen}
        onClose={() => setIsContextControlsOpen(false)}
        onApplySettings={(settings) => {
          // Here you would dispatch actions to update settings
          setIsContextControlsOpen(false);
        }}
        initialSettings={{
          mode: 'standard',
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