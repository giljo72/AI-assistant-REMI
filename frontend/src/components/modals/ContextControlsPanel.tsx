import React, { useState } from 'react';

type Mode = 'standard' | 'project-focus' | 'deep-research' | 'quick-response' | 'self-aware' | 'create';

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
  customContext?: string; // For custom mode context instructions
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
  const [isCustomMode, setIsCustomMode] = useState(settings.mode === 'create');
  const [showContextHelp, setShowContextHelp] = useState(false);
  const [newContextName, setNewContextName] = useState('');
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [password, setPassword] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [previousMode, setPreviousMode] = useState<Mode>(settings.mode);

  // Handle mode change
  const handleModeChange = (mode: Mode) => {
    if (mode === 'self-aware') {
      // Store current mode before showing password modal
      setPreviousMode(settings.mode);
      // Show password modal for self-aware mode
      setShowPasswordModal(true);
      // Don't update settings yet - wait for authentication
      return;
    }
    
    // Update previous mode for other changes
    setPreviousMode(mode);
    
    if (mode === 'create') {
      setIsCustomMode(true);
      setSettings({
        ...settings,
        mode: 'create',
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
        case 'self-aware':
          newSettings.contextDepth = 90;
          newSettings.useProjectDocs = false; // No project docs in self-aware mode
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
      mode: 'create',
    });
    setIsCustomMode(true);
  };

  // Handle checkbox changes
  const handleCheckboxChange = (field: keyof ContextSettings) => {
    setSettings({
      ...settings,
      [field]: !settings[field],
      mode: 'create',
    });
    setIsCustomMode(true);
  };

  // Handle password submission for self-aware mode
  const handlePasswordSubmit = async () => {
    try {
      const response = await fetch('/api/self-aware/authenticate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ password }),
      });
      
      if (response.ok) {
        const data = await response.json();
        // Store token in localStorage
        localStorage.setItem('selfAwareToken', data.token);
        
        // Apply self-aware settings
        const selfAwareSettings: ContextSettings = {
          mode: 'self-aware',
          contextDepth: 90,
          useProjectDocs: false,
          useProjectChats: false,
          useAllDocs: false,
          useAllChats: false,
        };
        setSettings(selfAwareSettings);
        setShowPasswordModal(false);
        setPassword('');
        setPasswordError('');
      } else {
        setPasswordError('Invalid password');
      }
    } catch (error) {
      setPasswordError('Authentication failed');
    }
  };

  // Apply settings and close
  const handleApply = () => {
    onApplySettings(settings);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Password Modal for Self-Aware Mode */}
      {showPasswordModal && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-[100]">
          <div className="bg-navy-light rounded-lg p-6 max-w-sm w-full relative z-[110]">
            <h3 className="text-xl font-bold text-red-500 mb-4">🔒 Self-Aware Mode Authentication</h3>
            <p className="text-gray-300 mb-4 text-sm">
              Self-aware mode grants read and write access to the AI assistant's source code.
              This requires authentication.
            </p>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handlePasswordSubmit()}
              placeholder="Enter password"
              className="w-full bg-navy p-2 rounded focus:outline-none focus:ring-1 focus:ring-red-500 text-white mb-2"
              autoFocus
            />
            {passwordError && (
              <p className="text-red-400 text-sm mb-3">{passwordError}</p>
            )}
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => {
                  setShowPasswordModal(false);
                  setPassword('');
                  setPasswordError('');
                  // Reset the select to previous value since user cancelled
                  // Don't change settings - keep the current mode
                }}
                className="px-3 py-1 bg-navy hover:bg-navy-lighter rounded text-white"
              >
                Cancel
              </button>
              <button
                onClick={handlePasswordSubmit}
                className="px-4 py-2 bg-red-600 text-white font-medium rounded hover:bg-red-700"
              >
                Authenticate
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* Main Context Controls Modal */}
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
            value={showPasswordModal ? previousMode : settings.mode}
            onChange={(e) => handleModeChange(e.target.value as Mode)}
            className="w-full bg-navy p-2 rounded focus:outline-none focus:ring-1 focus:ring-gold text-white"
          >
            <option value="standard">Standard</option>
            <option value="project-focus">Project Focus</option>
            <option value="deep-research">Deep Research</option>
            <option value="quick-response">Quick Response</option>
            <option value="self-aware">Self-Aware (Code Analysis)</option>
            <option value="create">+ Create New Context</option>
          </select>
        </div>

        {/* Show preset template for non-create modes */}
        {!isCustomMode && settings.mode !== 'standard' && (
          <div className="border-t border-navy pt-4 mb-6">
            <h4 className="text-sm font-medium text-gold mb-3">Context Template Settings</h4>
            
            {/* Context Depth Display (non-editable) */}
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2 text-gray-400">
                Context Depth: <span className="text-gray-300">{settings.contextDepth}%</span>
              </label>
              <div className="w-full h-2 bg-navy rounded-lg relative">
                <div 
                  className="h-full bg-gold/50 rounded-lg"
                  style={{ width: `${settings.contextDepth}%` }}
                />
              </div>
            </div>
            
            {/* Source Selection Display (non-editable) */}
            <div>
              <label className="block text-sm font-medium mb-2 text-gray-400">
                Active Sources:
              </label>
              <div className="space-y-1 text-sm text-gray-300">
                {settings.useProjectDocs && <div>✓ Project Documents</div>}
                {settings.useProjectChats && <div>✓ Project Chats</div>}
                {settings.useAllDocs && <div>✓ All Documents</div>}
                {settings.useAllChats && <div>✓ All Conversations</div>}
              </div>
            </div>
          </div>
        )}

        {/* Custom Controls - only shown when in create mode */}
        {isCustomMode && (
          <div className="border-t border-navy pt-4 mb-6">
            {/* Context Name Input */}
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2 text-gold">
                Context Name <span className="text-red-400">*</span>
              </label>
              <input
                type="text"
                value={newContextName}
                onChange={(e) => setNewContextName(e.target.value)}
                placeholder="e.g., Technical Documentation Focus"
                className="w-full bg-navy p-2 rounded focus:outline-none focus:ring-1 focus:ring-gold text-white"
              />
            </div>
            
            {/* Custom Context Instructions */}
            <div className="mb-4 bg-navy/50 p-3 rounded-lg border border-gold/20">
              <div className="flex items-start justify-between mb-2">
                <h4 className="text-sm font-medium text-gold">Custom Context Instructions</h4>
                <button
                  onClick={() => setShowContextHelp(!showContextHelp)}
                  className="text-gold hover:text-gold/80 text-xs"
                >
                  {showContextHelp ? 'Hide Help' : 'Show Help'}
                </button>
              </div>
              
              {showContextHelp && (
                <div className="text-xs text-gray-300 mb-3 space-y-1">
                  <p><strong>Context</strong> defines the AI's knowledge scope and behavior:</p>
                  <ul className="list-disc list-inside space-y-1 ml-2">
                    <li>Sets what information the AI has access to</li>
                    <li>Determines search depth and breadth</li>
                    <li>Controls which documents and chats to include</li>
                    <li>Different from prompts (which guide personality/style)</li>
                  </ul>
                </div>
              )}
              
              <textarea
                value={settings.customContext || ''}
                onChange={(e) => setSettings({...settings, customContext: e.target.value})}
                placeholder="Define custom context behavior... (e.g., 'Focus only on Python files', 'Include all technical documentation', 'Prioritize recent chats')"
                className="w-full bg-navy p-2 rounded text-white text-sm h-20 resize-none focus:outline-none focus:ring-1 focus:ring-gold"
              />
            </div>
            
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
            {settings.mode === 'self-aware' && 'AI can read and analyze its own source code at F:\\assistant. Perfect for debugging, code improvements, and understanding the system architecture. No project documents are used in this mode.'}
            {settings.mode === 'create' && 'Create a new custom context with your own settings. Define context name, depth, sources, and specific instructions for the AI.'}
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
    </>
  );
};

export default ContextControlsPanel;