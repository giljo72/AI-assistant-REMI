import React, { useState } from 'react';

type Mode = 'standard' | 'project-focus' | 'deep-research' | 'quick-response' | 'custom';

type ContextControlsPanelProps = {
  isOpen: boolean;
  onClose: () => void;
  onApplySettings: (settings: ContextSettings) => void;
  initialSettings?: ContextSettings;
};

type ContextSettings = {
  mode: Mode;
  contextDepth: number; // 0-100 scale
  useProjectDocs: boolean;
  useProjectChats: boolean;
  useAllDocs: boolean;
  useAllChats: boolean;
};

const defaultSettings: ContextSettings = {
  mode: 'standard',
  contextDepth: 50,
  useProjectDocs: true,
  useProjectChats: true,
  useAllDocs: false,
  useAllChats: false,
};

const ContextControlsPanel: React.FC<ContextControlsPanelProps> = ({
  isOpen,
  onClose,
  onApplySettings,
  initialSettings,
}) => {
  const [settings, setSettings] = useState<ContextSettings>(initialSettings || defaultSettings);
  const [isCustomMode, setIsCustomMode] = useState(settings.mode === 'custom');

  // Handle mode change
  const handleModeChange = (mode: Mode) => {
    if (mode === 'custom') {
      setIsCustomMode(true);
      setSettings({
        ...settings,
        mode: 'custom',
      });
    } else {
      setIsCustomMode(false);
      // Apply preset settings based on mode
      const newSettings = { ...settings, mode };
      
      switch (mode) {
        case 'project-focus':
          newSettings.contextDepth = 40;
          newSettings.useProjectDocs = true;
          newSettings.useProjectChats = true;
          newSettings.useAllDocs = false;
          newSettings.useAllChats = false;
          break;
        case 'deep-research':
          newSettings.contextDepth = 80;
          newSettings.useProjectDocs = true;
          newSettings.useProjectChats = true;
          newSettings.useAllDocs = true;
          newSettings.useAllChats = true;
          break;
        case 'quick-response':
          newSettings.contextDepth = 20;
          newSettings.useProjectDocs = true;
          newSettings.useProjectChats = false;
          newSettings.useAllDocs = false;
          newSettings.useAllChats = false;
          break;
        case 'standard':
        default:
          newSettings.contextDepth = 50;
          newSettings.useProjectDocs = true;
          newSettings.useProjectChats = true;
          newSettings.useAllDocs = false;
          newSettings.useAllChats = false;
          break;
      }
      
      setSettings(newSettings);
    }
  };

  // Handle slider change
  const handleDepthChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const contextDepth = parseInt(e.target.value, 10);
    setSettings({
      ...settings,
      contextDepth,
      mode: 'custom',
    });
    setIsCustomMode(true);
  };

  // Handle checkbox changes
  const handleCheckboxChange = (field: keyof ContextSettings) => {
    setSettings({
      ...settings,
      [field]: !settings[field],
      mode: 'custom',
    });
    setIsCustomMode(true);
  };

  // Apply settings and close
  const handleApply = () => {
    onApplySettings(settings);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="bg-navy-light rounded-lg p-6 max-w-md w-full">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-bold text-gold">Context Controls</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white"
            aria-label="Close"
          >
            ✕
          </button>
        </div>

        {/* Mode Selection */}
        <div className="mb-6">
          <label className="block text-sm font-medium mb-2 text-gray-300">
            Mode:
          </label>
          <select
            value={settings.mode}
            onChange={(e) => handleModeChange(e.target.value as Mode)}
            className="w-full bg-navy p-2 rounded focus:outline-none focus:ring-1 focus:ring-gold text-white"
          >
            <option value="standard">Standard</option>
            <option value="project-focus">Project Focus</option>
            <option value="deep-research">Deep Research</option>
            <option value="quick-response">Quick Response</option>
            <option value="custom">Custom</option>
          </select>
        </div>

        {/* Custom Controls - only shown when in custom mode */}
        {isCustomMode && (
          <div className="border-t border-navy pt-4 mb-6">
            {/* Context Depth Slider */}
            <div className="mb-6">
              <label className="block text-sm font-medium mb-2 text-gray-300">
                Context Depth:
              </label>
              <div className="flex items-center">
                <span className="text-xs text-gray-400 w-16">Concise</span>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={settings.contextDepth}
                  onChange={handleDepthChange}
                  className="w-full h-2 bg-navy rounded-lg appearance-none cursor-pointer mx-2 accent-gold"
                />
                <span className="text-xs text-gray-400 w-32">Comprehensive</span>
              </div>
            </div>

            {/* Source Selection */}
            <div>
              <label className="block text-sm font-medium mb-2 text-gray-300">
                Sources:
              </label>
              <div className="space-y-2">
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="useProjectDocs"
                    checked={settings.useProjectDocs}
                    onChange={() => handleCheckboxChange('useProjectDocs')}
                    className="h-4 w-4 accent-gold bg-navy border-navy-lighter rounded mr-2"
                  />
                  <label htmlFor="useProjectDocs" className="text-white">
                    Project Docs (Priority)
                  </label>
                </div>
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="useProjectChats"
                    checked={settings.useProjectChats}
                    onChange={() => handleCheckboxChange('useProjectChats')}
                    className="h-4 w-4 accent-gold bg-navy border-navy-lighter rounded mr-2"
                  />
                  <label htmlFor="useProjectChats" className="text-white">
                    Project Chats
                  </label>
                </div>
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="useAllDocs"
                    checked={settings.useAllDocs}
                    onChange={() => handleCheckboxChange('useAllDocs')}
                    className="h-4 w-4 accent-gold bg-navy border-navy-lighter rounded mr-2"
                  />
                  <label htmlFor="useAllDocs" className="text-white">
                    All Documents
                  </label>
                </div>
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="useAllChats"
                    checked={settings.useAllChats}
                    onChange={() => handleCheckboxChange('useAllChats')}
                    className="h-4 w-4 accent-gold bg-navy border-navy-lighter rounded mr-2"
                  />
                  <label htmlFor="useAllChats" className="text-white">
                    All Conversations
                  </label>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Mode Description */}
        <div className="bg-navy p-3 rounded-lg mb-6">
          <h4 className="text-sm font-medium text-gold mb-1">Mode Description:</h4>
          <p className="text-sm text-gray-300">
            {settings.mode === 'standard' && 'Balanced approach with project-focused context. Good for general questions and tasks.'}
            {settings.mode === 'project-focus' && 'Strictly uses project-specific documents and chats. Best for staying focused on project scope.'}
            {settings.mode === 'deep-research' && 'Comprehensive analysis using all available knowledge. Best for complex research tasks.'}
            {settings.mode === 'quick-response' && 'Faster responses with minimal context. Best for simple questions and quick tasks.'}
            {settings.mode === 'custom' && 'Custom settings tailored to your specific needs.'}
          </p>
        </div>

        {/* Action buttons */}
        <div className="flex justify-end space-x-3">
          <button
            onClick={onClose}
            className="px-3 py-1 bg-navy hover:bg-navy-lighter rounded text-white"
          >
            Cancel
          </button>
          <button
            onClick={handleApply}
            className="px-4 py-2 bg-gold text-navy font-medium rounded hover:bg-gold/90"
          >
            Apply
          </button>
        </div>
      </div>
    </div>
  );
};

export default ContextControlsPanel;