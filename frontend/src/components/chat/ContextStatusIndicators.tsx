import React from 'react';

type ContextStatusIndicatorsProps = {
  isProjectPromptEnabled: boolean;
  isGlobalDataEnabled: boolean;
  isProjectDocumentsEnabled: boolean;
  onToggleProjectPrompt: () => void;
  onToggleGlobalData: () => void;
  onToggleProjectDocuments: () => void;
  onOpenContextControls: () => void;
};

const ContextStatusIndicators: React.FC<ContextStatusIndicatorsProps> = ({
  isProjectPromptEnabled,
  isGlobalDataEnabled,
  isProjectDocumentsEnabled,
  onToggleProjectPrompt,
  onToggleGlobalData,
  onToggleProjectDocuments,
  onOpenContextControls,
}) => {
  return (
    <div className="flex flex-wrap gap-2 my-3">
      {/* Project Prompt Indicator */}
      <div className="flex items-center">
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
      </div>

      {/* Global Data Indicator */}
      <div className="flex items-center">
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
      </div>

      {/* Project Documents Indicator */}
      <div className="flex items-center">
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

      {/* Context Controls Button */}
      <button
        onClick={onOpenContextControls}
        className="inline-flex items-center px-3 py-1 bg-gold/20 hover:bg-gold/30 text-gold rounded text-sm"
      >
        <span className="mr-1">⚙</span>
        Context Settings
      </button>
    </div>
  );
};

export default ContextStatusIndicators;