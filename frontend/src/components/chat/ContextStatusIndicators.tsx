// File: frontend/src/components/chat/ContextStatusIndicators.tsx
import React, { useState, useRef } from 'react';
import UserPromptQuickSwitcher from './UserPromptQuickSwitcher';
import SystemPromptQuickSwitcher from './SystemPromptQuickSwitcher';

type ContextStatusIndicatorsProps = {
  isProjectPromptEnabled: boolean;
  isGlobalDataEnabled: boolean;
  isProjectDocumentsEnabled: boolean;
  isSystemPromptEnabled?: boolean;
  isUserPromptEnabled?: boolean;
  activeUserPromptName?: string;
  selectedModel?: string;
  onToggleProjectPrompt: () => void;
  onToggleGlobalData: () => void;
  onToggleProjectDocuments: () => void;
  onToggleSystemPrompt?: () => void;
  onToggleUserPrompt?: () => void;
  onOpenContextControls?: () => void;
  onOpenSystemPromptPanel?: () => void;
  onOpenUserPromptPanel?: () => void;
  contextMode?: string;
};

const ContextStatusIndicators: React.FC<ContextStatusIndicatorsProps> = ({
  isProjectPromptEnabled,
  isGlobalDataEnabled,
  isProjectDocumentsEnabled,
  isSystemPromptEnabled = true,
  isUserPromptEnabled = false,
  activeUserPromptName = '',
  onToggleProjectPrompt,
  onToggleGlobalData,
  onToggleProjectDocuments,
  onOpenContextControls,
  onOpenSystemPromptPanel,
  onOpenUserPromptPanel,
  contextMode = 'standard'
}) => {
  const [userPromptMenuOpen, setUserPromptMenuOpen] = useState(false);
  const [systemPromptMenuOpen, setSystemPromptMenuOpen] = useState(false);
  const userPromptButtonRef = useRef<HTMLButtonElement>(null);
  const systemPromptButtonRef = useRef<HTMLButtonElement>(null);
  // Format context mode display name
  const getContextModeDisplay = (mode: string) => {
    const modeMap: { [key: string]: string } = {
      'standard': 'Standard',
      'project-focus': 'Project Focus',
      'deep-research': 'Deep Research',
      'quick-response': 'Quick Response',
      'self-aware': 'Self-Aware',
      'create': 'Create New'
    };
    // If it's not a preset mode, it's a custom context name
    return modeMap[mode] || mode;
  };

  return (
    <div className="flex flex-wrap gap-2 justify-center">
      {/* Context Mode Indicator - Yellow Box */}
      <button
        onClick={onOpenContextControls}
        className="inline-flex items-center px-3 py-1 rounded text-sm mr-2 bg-yellow-500/20 text-yellow-400 border border-yellow-500/30 hover:bg-yellow-500/30 hover:shadow-lg hover:shadow-yellow-500/20 transition-all duration-200 cursor-pointer transform hover:scale-105"
        title="Click to change context mode"
      >
        <span className="w-2 h-2 rounded-full mr-2 bg-yellow-400 animate-pulse"></span>
        Context: <span className="font-semibold ml-1">{getContextModeDisplay(contextMode)}</span>
      </button>

      {/* System Prompt Indicator - Orange */}
      <button
        ref={systemPromptButtonRef}
        onClick={() => setSystemPromptMenuOpen(!systemPromptMenuOpen)}
        className={`inline-flex items-center px-3 py-1 rounded text-sm mr-2 transition-all duration-200 transform hover:scale-105 cursor-pointer ${
          isSystemPromptEnabled
            ? 'bg-orange-900/30 text-orange-400 border border-orange-500/30 hover:bg-orange-500/30 hover:shadow-lg hover:shadow-orange-500/20'
            : 'bg-gray-800 text-gray-400 border border-gray-700 hover:bg-gray-700 hover:text-gray-300'
        }`}
        title="Click to select system prompt"
      >
        <span className={`w-2 h-2 rounded-full mr-2 transition-colors ${isSystemPromptEnabled ? 'bg-orange-400' : 'bg-gray-500'}`}></span>
        System Prompt {isSystemPromptEnabled ? 'Enabled' : 'Disabled'}
      </button>
      
      <SystemPromptQuickSwitcher
        isOpen={systemPromptMenuOpen}
        anchorEl={systemPromptButtonRef.current}
        onClose={() => setSystemPromptMenuOpen(false)}
        onManagePrompts={onOpenSystemPromptPanel}
      />

      {/* User Prompt Indicator - Gray (Always visible) */}
      <button
        ref={userPromptButtonRef}
        onClick={() => setUserPromptMenuOpen(!userPromptMenuOpen)}
        className={`inline-flex items-center px-3 py-1 rounded text-sm mr-2 transition-all duration-200 transform hover:scale-105 cursor-pointer ${
          activeUserPromptName
            ? isUserPromptEnabled
              ? 'bg-gray-700/50 text-gray-300 border border-gray-600 hover:bg-gray-600/50 hover:shadow-lg hover:shadow-gray-600/20'
              : 'bg-gray-800 text-gray-500 border border-gray-700 hover:bg-gray-700 hover:text-gray-400'
            : 'bg-gray-800 text-gray-400 border border-gray-700 hover:bg-gray-700 hover:text-gray-300'
        }`}
        title="Click to select user prompt"
      >
        <span className={`w-2 h-2 rounded-full mr-2 transition-colors ${
          activeUserPromptName 
            ? (isUserPromptEnabled ? 'bg-gray-400' : 'bg-gray-500')
            : 'bg-gray-500'
        }`}></span>
        {activeUserPromptName 
          ? `${activeUserPromptName} ${isUserPromptEnabled ? 'Active' : 'Inactive'}`
          : 'User Prompt Disabled'
        }
      </button>
      
      <UserPromptQuickSwitcher
        isOpen={userPromptMenuOpen}
        anchorEl={userPromptButtonRef.current}
        onClose={() => setUserPromptMenuOpen(false)}
        onManagePrompts={onOpenUserPromptPanel}
      />

      {/* Project Prompt Indicator */}
      <button
        onClick={onToggleProjectPrompt}
        className={`inline-flex items-center px-3 py-1 rounded text-sm mr-2 transition-all duration-200 transform hover:scale-105 cursor-pointer ${
          isProjectPromptEnabled
            ? 'bg-green-900/30 text-green-400 border border-green-500/30 hover:bg-green-500/30 hover:shadow-lg hover:shadow-green-500/20'
            : 'bg-gray-800 text-gray-400 border border-gray-700 hover:bg-gray-700 hover:text-gray-300'
        }`}
        title="Toggle project-specific prompt"
      >
        <span className={`w-2 h-2 rounded-full mr-2 transition-colors ${isProjectPromptEnabled ? 'bg-green-400' : 'bg-gray-500'}`}></span>
        Project Prompt {isProjectPromptEnabled ? 'Enabled' : 'Disabled'}
      </button>

      {/* Global Data Indicator */}
      <button
        onClick={onToggleGlobalData}
        className={`inline-flex items-center px-3 py-1 rounded text-sm mr-2 transition-all duration-200 transform hover:scale-105 cursor-pointer ${
          isGlobalDataEnabled
            ? 'bg-blue-900/30 text-blue-400 border border-blue-500/30 hover:bg-blue-500/30 hover:shadow-lg hover:shadow-blue-500/20'
            : 'bg-gray-800 text-gray-400 border border-gray-700 hover:bg-gray-700 hover:text-gray-300'
        }`}
        title="Toggle global knowledge base access"
      >
        <span className={`w-2 h-2 rounded-full mr-2 transition-colors ${isGlobalDataEnabled ? 'bg-blue-400' : 'bg-gray-500'}`}></span>
        Global Data {isGlobalDataEnabled ? 'Enabled' : 'Disabled'}
      </button>

      {/* Project Documents Indicator */}
      <button
        onClick={onToggleProjectDocuments}
        className={`inline-flex items-center px-3 py-1 rounded text-sm mr-2 transition-all duration-200 transform hover:scale-105 cursor-pointer ${
          isProjectDocumentsEnabled
            ? 'bg-purple-900/30 text-purple-400 border border-purple-500/30 hover:bg-purple-500/30 hover:shadow-lg hover:shadow-purple-500/20'
            : 'bg-gray-800 text-gray-400 border border-gray-700 hover:bg-gray-700 hover:text-gray-300'
        }`}
        title="Toggle project document access"
      >
        <span className={`w-2 h-2 rounded-full mr-2 transition-colors ${isProjectDocumentsEnabled ? 'bg-purple-400' : 'bg-gray-500'}`}></span>
        Project Documents {isProjectDocumentsEnabled ? 'Enabled' : 'Disabled'}
      </button>
    </div>
  );
};

export default ContextStatusIndicators;