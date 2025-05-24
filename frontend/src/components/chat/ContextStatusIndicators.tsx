// File: frontend/src/components/chat/ContextStatusIndicators.tsx
import React from 'react';

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
  contextMode?: string;
};

const ContextStatusIndicators: React.FC<ContextStatusIndicatorsProps> = ({
  isProjectPromptEnabled,
  isGlobalDataEnabled,
  isProjectDocumentsEnabled,
  isSystemPromptEnabled = true,
  isUserPromptEnabled = false,
  activeUserPromptName = '',
  selectedModel = '',
  onToggleProjectPrompt,
  onToggleGlobalData,
  onToggleProjectDocuments,
  onToggleSystemPrompt = () => {},
  onToggleUserPrompt = () => {},
  onOpenContextControls,
  contextMode = 'standard'
}) => {
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
        className="inline-flex items-center px-3 py-1 rounded text-sm mr-2 bg-yellow-500/20 text-yellow-400 border border-yellow-500/30 hover:bg-yellow-500/30 transition-colors cursor-pointer"
        title="Click to change context mode"
      >
        <span className="w-2 h-2 rounded-full mr-2 bg-yellow-400"></span>
        Context: <span className="font-semibold ml-1">{getContextModeDisplay(contextMode)}</span>
      </button>

      {/* System Prompt Indicator - Orange */}
      <button
        onClick={onToggleSystemPrompt}
        className={`inline-flex items-center px-3 py-1 rounded text-sm mr-2 ${
          isSystemPromptEnabled
            ? 'bg-orange-900/30 text-orange-400'
            : 'bg-gray-800 text-gray-400'
        }`}
        title={selectedModel.includes('deepseek') ? 'DeepSeek Coder System Prompt' : 'Default Assistant System Prompt'}
      >
        <span className={`w-2 h-2 rounded-full mr-2 ${isSystemPromptEnabled ? 'bg-orange-400' : 'bg-gray-500'}`}></span>
        System Prompt {isSystemPromptEnabled ? 'Enabled' : 'Disabled'}
      </button>

      {/* Active User Prompt Indicator - Gray */}
      {activeUserPromptName && (
        <button
          onClick={onToggleUserPrompt}
          className={`inline-flex items-center px-3 py-1 rounded text-sm mr-2 ${
            isUserPromptEnabled
              ? 'bg-gray-700/50 text-gray-300'
              : 'bg-gray-800 text-gray-500'
          }`}
          title={`User Prompt: ${activeUserPromptName}`}
        >
          <span className={`w-2 h-2 rounded-full mr-2 ${isUserPromptEnabled ? 'bg-gray-400' : 'bg-gray-600'}`}></span>
          {activeUserPromptName} {isUserPromptEnabled ? 'Active' : 'Inactive'}
        </button>
      )}

      {/* Project Prompt Indicator */}
      <button
        onClick={onToggleProjectPrompt}
        className={`inline-flex items-center px-3 py-1 rounded text-sm mr-2 ${
          isProjectPromptEnabled
            ? 'bg-green-900/30 text-green-400'
            : 'bg-gray-800 text-gray-400'
        }`}
      >
        <span className={`w-2 h-2 rounded-full mr-2 ${isProjectPromptEnabled ? 'bg-green-400' : 'bg-gray-500'}`}></span>
        Project Prompt {isProjectPromptEnabled ? 'Enabled' : 'Disabled'}
      </button>

      {/* Global Data Indicator */}
      <button
        onClick={onToggleGlobalData}
        className={`inline-flex items-center px-3 py-1 rounded text-sm mr-2 ${
          isGlobalDataEnabled
            ? 'bg-blue-900/30 text-blue-400'
            : 'bg-gray-800 text-gray-400'
        }`}
      >
        <span className={`w-2 h-2 rounded-full mr-2 ${isGlobalDataEnabled ? 'bg-blue-400' : 'bg-gray-500'}`}></span>
        Global Data {isGlobalDataEnabled ? 'Enabled' : 'Disabled'}
      </button>

      {/* Project Documents Indicator */}
      <button
        onClick={onToggleProjectDocuments}
        className={`inline-flex items-center px-3 py-1 rounded text-sm mr-2 ${
          isProjectDocumentsEnabled
            ? 'bg-purple-900/30 text-purple-400'
            : 'bg-gray-800 text-gray-400'
        }`}
      >
        <span className={`w-2 h-2 rounded-full mr-2 ${isProjectDocumentsEnabled ? 'bg-purple-400' : 'bg-gray-500'}`}></span>
        Project Documents {isProjectDocumentsEnabled ? 'Enabled' : 'Disabled'}
      </button>
    </div>
  );
};

export default ContextStatusIndicators;