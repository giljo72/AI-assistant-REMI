import React, { ReactNode } from 'react';
import ProjectSidebar from '../sidebar/ProjectSidebar';

type MainLayoutProps = {
  children: ReactNode;
  onProjectSelect: (projectId: string) => void;
};

const MainLayout: React.FC<MainLayoutProps> = ({ children, onProjectSelect }) => {
  return (
    <div className="flex h-screen bg-navy text-white overflow-hidden">
      {/* Sidebar */}
      <div className="w-64 bg-navy-light border-r border-gold overflow-y-auto">
        <ProjectSidebar onProjectSelect={onProjectSelect} />
      </div>
      
      {/* Main content area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="bg-navy-light p-4 border-b border-gold flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gold">AI Assistant</h1>
          
          {/* Context controls - simplified version */}
          <div className="flex items-center space-x-3">
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
            
            <button className="bg-navy hover:bg-navy-lighter px-3 py-1.5 rounded text-sm">
              Settings
            </button>
          </div>
        </header>
        <main className="flex-1 overflow-y-auto p-4">
          {children}
        </main>
      </div>
    </div>
  );
};

export default MainLayout;