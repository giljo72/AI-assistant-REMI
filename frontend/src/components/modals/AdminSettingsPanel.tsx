import React, { useState, useEffect } from 'react';
import Draggable from 'react-draggable';
import adminService, { SystemInfo } from '../../services/adminService';
import { Icon, HelpIcon } from '../common/Icon';
import { ModelsContent } from './ModelsContent';

interface AdminSettingsPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

const AdminSettingsPanel: React.FC<AdminSettingsPanelProps> = ({ isOpen, onClose }) => {
  const [systemInfo, setSystemInfo] = useState<SystemInfo | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'info' | 'models' | 'reset' | 'development'>('info');
  const [developmentMode, setDevelopmentMode] = useState<boolean>(() => {
    // Load development mode from localStorage
    return localStorage.getItem('developmentMode') === 'true';
  });
  const [resetAction, setResetAction] = useState<string>('');
  const [confirmReset, setConfirmReset] = useState<boolean>(false);
  const [operationStatus, setOperationStatus] = useState<{message: string, type: 'success' | 'error'} | null>(null);
  
  // Update checking state
  const [updateCheckState, setUpdateCheckState] = useState<{
    checking: boolean;
    lastChecked: string | null;
    results: any | null;
    autoCheck: boolean;
    includeSpecs: boolean;
    showInstructions: { [key: string]: boolean };
  }>({
    checking: false,
    lastChecked: localStorage.getItem('lastUpdateCheck'),
    results: null,
    autoCheck: localStorage.getItem('autoCheckUpdates') === 'true',
    includeSpecs: localStorage.getItem('includeSystemSpecs') === 'true',
    showInstructions: {}
  });

  // Fetch system info when panel opens
  useEffect(() => {
    if (isOpen) {
      fetchSystemInfo();
    }
  }, [isOpen]);

  const handleDevelopmentModeToggle = () => {
    const newValue = !developmentMode;
    setDevelopmentMode(newValue);
    localStorage.setItem('developmentMode', newValue.toString());
    
    // You could also send this to the backend if needed
    // await adminService.setDevelopmentMode(newValue);
  };

  const checkForUpdates = async () => {
    setUpdateCheckState(prev => ({ ...prev, checking: true }));
    
    try {
      // Simulate checking for updates (in real implementation, this would call an API)
      await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate network delay
      
      const mockResults = {
        app_version: '1.0.0',
        latest_version: '1.0.0',
        update_available: false,
        model_updates: [
          {
            name: 'qwen2.5:32b-instruct-q4_K_M',
            current: 'q4_K_M',
            latest: 'q5_K_M',
            description: 'Improved quality with minimal size increase',
            size_change: '+0.5GB'
          },
          {
            name: 'mistral-nemo:latest',
            current: '12b',
            latest: '12b-v2',
            description: 'Performance improvements and bug fixes',
            size_change: '0GB'
          }
        ],
        service_updates: [
          {
            name: 'PyPDF2',
            current: '3.0.1',
            latest: '3.1.0',
            type: 'minor',
            description: 'Better handling of encrypted PDFs'
          }
        ],
        security_updates: [],
        recommendations: [
          {
            model: 'mixtral:8x7b',
            reason: 'Excellent performance within your 24GB VRAM limit',
            vram_required: 18,
            capabilities: 'Superior reasoning and coding abilities'
          }
        ],
        news: [
          'NVIDIA NIM now supports batch embeddings for 2x faster document processing',
          'New Ollama 0.2.0 brings 30% faster model loading'
        ]
      };
      
      const timestamp = new Date().toLocaleString();
      localStorage.setItem('lastUpdateCheck', timestamp);
      
      setUpdateCheckState(prev => ({
        ...prev,
        checking: false,
        lastChecked: timestamp,
        results: mockResults
      }));
    } catch (error) {
      console.error('Failed to check for updates:', error);
      setUpdateCheckState(prev => ({
        ...prev,
        checking: false,
        results: { error: 'Failed to check for updates. Please try again later.' }
      }));
    }
  };

  const toggleAutoCheck = () => {
    const newValue = !updateCheckState.autoCheck;
    setUpdateCheckState(prev => ({ ...prev, autoCheck: newValue }));
    localStorage.setItem('autoCheckUpdates', newValue.toString());
  };

  const toggleIncludeSpecs = () => {
    const newValue = !updateCheckState.includeSpecs;
    setUpdateCheckState(prev => ({ ...prev, includeSpecs: newValue }));
    localStorage.setItem('includeSystemSpecs', newValue.toString());
  };

  const toggleInstructions = (key: string) => {
    setUpdateCheckState(prev => ({
      ...prev,
      showInstructions: {
        ...prev.showInstructions,
        [key]: !prev.showInstructions[key]
      }
    }));
  };

  const fetchSystemInfo = async () => {
    setLoading(true);
    setError(null);
    try {
      const info = await adminService.getSystemInfo();
      setSystemInfo(info);
    } catch (err) {
      console.error('Error fetching system info:', err);
      setError('Failed to fetch system information');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    if (!confirmReset) {
      setConfirmReset(true);
      return;
    }

    setLoading(true);
    setError(null);
    setOperationStatus(null);
    
    try {
      let response;
      
      switch (resetAction) {
        case 'database':
          // Reset project data but preserve prompts and profiles
          response = await adminService.resetDatabase(true);
          break;
        case 'vector':
          response = await adminService.resetVectorStore();
          break;
        case 'files':
          response = await adminService.resetFiles();
          break;
        case 'all':
          // Reset EVERYTHING including prompts and profiles
          // First reset database without preserving anything
          await adminService.resetDatabase(false);
          await adminService.resetVectorStore();
          await adminService.resetFiles();
          response = { message: 'Complete system reset performed. All data cleared.' };
          break;
        default:
          throw new Error('Invalid reset action');
      }
      
      setOperationStatus({
        message: response.message,
        type: 'success'
      });
      
      // Refresh system info after reset
      fetchSystemInfo();
    } catch (err: any) {
      console.error('Error performing reset:', err);
      setOperationStatus({
        message: err.message || 'An unknown error occurred',
        type: 'error'
      });
    } finally {
      setLoading(false);
      setConfirmReset(false);
      setResetAction('');
    }
  };

  // Format file size
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (!isOpen) {
    return null;
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <Draggable
        handle=".drag-handle"
        bounds="parent"
        defaultPosition={{ x: 0, y: 0 }}
      >
        <div className="bg-navy-light text-white rounded-2xl shadow-lg w-full max-w-3xl max-h-[90vh] overflow-hidden flex flex-col border-2 border-yellow-500">
          {/* Header - Now draggable */}
          <div className="drag-handle p-4 bg-navy flex items-center justify-between border-b border-navy-lighter cursor-move">
            <h2 className="text-xl font-bold text-gold select-none">System Administration</h2>
            <Icon
              name="close"
              size={24}
              onClick={onClose}
              tooltip="Close"
              style={{ color: '#9ca3af' }}
              className="cursor-pointer"
            />
          </div>
        
        {/* Tabs */}
        <div className="flex border-b border-navy-lighter">
          <button 
            className={`px-4 py-2 ${activeTab === 'info' ? 'text-gold border-b-2 border-gold' : 'text-gray-400 hover:text-white'}`}
            onClick={() => setActiveTab('info')}
          >
            System Information
          </button>
          <button 
            className={`px-4 py-2 ${activeTab === 'models' ? 'text-gold border-b-2 border-gold' : 'text-gray-400 hover:text-white'}`}
            onClick={() => setActiveTab('models')}
          >
            Models
          </button>
          <button 
            className={`px-4 py-2 ${activeTab === 'reset' ? 'text-gold border-b-2 border-gold' : 'text-gray-400 hover:text-white'}`}
            onClick={() => setActiveTab('reset')}
          >
            Reset Options
          </button>
          <button 
            className={`px-4 py-2 ${activeTab === 'development' ? 'text-gold border-b-2 border-gold' : 'text-gray-400 hover:text-white'}`}
            onClick={() => setActiveTab('development')}
          >
            Development
          </button>
        </div>
        
        {/* Content */}
        <div className="p-4 overflow-y-auto flex-grow">
          {loading && (
            <div className="flex justify-center items-center h-40">
              <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-gold"></div>
            </div>
          )}
          
          {error && !loading && (
            <div className="bg-red-900 text-white p-4 rounded-md mb-4">
              {error}
            </div>
          )}
          
          {operationStatus && (
            <div className={`${operationStatus.type === 'success' ? 'bg-green-900' : 'bg-red-900'} text-white p-4 rounded-md mb-4`}>
              {operationStatus.message}
            </div>
          )}
          
          {activeTab === 'info' && !loading && systemInfo && (
            <div className="space-y-6">
              <div className="bg-navy p-4 rounded-md">
                <h3 className="text-lg font-semibold text-gold mb-2">Database Statistics</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-navy-lighter p-3 rounded-md">
                    <div className="text-gray-400 text-sm">Projects</div>
                    <div className="text-2xl font-bold">{systemInfo.database.project_count}</div>
                  </div>
                  <div className="bg-navy-lighter p-3 rounded-md">
                    <div className="text-gray-400 text-sm">Documents</div>
                    <div className="text-2xl font-bold">{systemInfo.database.document_count}</div>
                  </div>
                  <div className="bg-navy-lighter p-3 rounded-md">
                    <div className="text-gray-400 text-sm">Document Chunks</div>
                    <div className="text-2xl font-bold">{systemInfo.database.chunk_count}</div>
                  </div>
                  <div className="bg-navy-lighter p-3 rounded-md">
                    <div className="text-gray-400 text-sm">Vector Embeddings</div>
                    <div className="text-2xl font-bold">{systemInfo.database.embedding_count}</div>
                  </div>
                </div>
              </div>
              
              <div className="bg-navy p-4 rounded-md">
                <h3 className="text-lg font-semibold text-gold mb-2">File Storage</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-navy-lighter p-3 rounded-md">
                    <div className="text-gray-400 text-sm">Uploaded Files</div>
                    <div className="text-2xl font-bold">{systemInfo.files.upload_count}</div>
                    <div className="text-sm text-gray-400">{formatFileSize(systemInfo.files.upload_size_bytes)}</div>
                  </div>
                  <div className="bg-navy-lighter p-3 rounded-md">
                    <div className="text-gray-400 text-sm">Processed Files</div>
                    <div className="text-2xl font-bold">{systemInfo.files.processed_count}</div>
                    <div className="text-sm text-gray-400">{formatFileSize(systemInfo.files.processed_size_bytes)}</div>
                  </div>
                  <div className="col-span-2 bg-navy-lighter p-3 rounded-md">
                    <div className="text-gray-400 text-sm">Total Storage Used</div>
                    <div className="text-2xl font-bold">{formatFileSize(systemInfo.files.total_size_bytes)}</div>
                    <div className="text-sm text-gray-400">{systemInfo.files.total_count} files</div>
                  </div>
                </div>
              </div>
              
              <div className="flex justify-end mt-4">
                <button 
                  onClick={fetchSystemInfo}
                  className="px-4 py-2 bg-navy hover:bg-navy-lighter text-white rounded-md flex items-center gap-2"
                >
                  <Icon name="refresh" size={16} />
                  Refresh
                </button>
              </div>
            </div>
          )}
          
          {activeTab === 'models' && (
            <ModelsContent />
          )}
          
          {activeTab === 'reset' && !loading && (
            <div className="space-y-6">
              <div className="bg-red-900 bg-opacity-20 p-4 rounded-md border border-red-600">
                <h3 className="text-lg font-semibold text-red-400 mb-2">⚠️ Warning</h3>
                <p className="mb-2">
                  Reset operations are destructive and cannot be undone. Only proceed if you're sure you want to reset the system.
                </p>
                <p>
                  Use these options for development and testing purposes only.
                </p>
              </div>
              
              <div className="space-y-3">
                <div 
                  className={`p-4 rounded-md border transition-colors cursor-pointer ${resetAction === 'database' ? 'bg-navy border-gold' : 'bg-navy-lighter border-navy-lighter hover:border-gray-500'}`}
                  onClick={() => setResetAction('database')}
                >
                  <h4 className="font-semibold text-gold mb-1">Reset Project Data</h4>
                  <p className="text-sm text-gray-400">
                    Clears projects, documents, chats, and project-specific prompts. Preserves system prompts, user prompts, and personal profiles.
                  </p>
                </div>
                
                <div 
                  className={`p-4 rounded-md border transition-colors cursor-pointer ${resetAction === 'vector' ? 'bg-navy border-gold' : 'bg-navy-lighter border-navy-lighter hover:border-gray-500'}`}
                  onClick={() => setResetAction('vector')}
                >
                  <h4 className="font-semibold text-gold mb-1">Reset Vector Store</h4>
                  <p className="text-sm text-gray-400">
                    Removes all vector embeddings while preserving documents and metadata. The document content remains intact.
                  </p>
                </div>
                
                <div 
                  className={`p-4 rounded-md border transition-colors cursor-pointer ${resetAction === 'files' ? 'bg-navy border-gold' : 'bg-navy-lighter border-navy-lighter hover:border-gray-500'}`}
                  onClick={() => setResetAction('files')}
                >
                  <h4 className="font-semibold text-gold mb-1">Reset Files</h4>
                  <p className="text-sm text-gray-400">
                    Deletes all uploaded and processed files from the file system. Database records will still reference these files.
                  </p>
                </div>
                
                <div 
                  className={`p-4 rounded-md border-2 transition-colors cursor-pointer ${resetAction === 'all' ? 'bg-red-900 bg-opacity-30 border-red-600' : 'bg-red-900 bg-opacity-10 border-red-800 hover:border-red-600'}`}
                  onClick={() => setResetAction('all')}
                >
                  <h4 className="font-semibold text-red-400 mb-1">🚨 RESET EVERYTHING</h4>
                  <p className="text-sm text-red-300">
                    ⚠️ DANGER: Completely wipes ALL data including system prompts, user prompts, personal profiles, and all customizations. Returns to factory defaults.
                  </p>
                </div>
              </div>
              
              {resetAction && (
                <div className="flex justify-end">
                  <button 
                    onClick={handleReset}
                    className={`px-4 py-2 ${confirmReset ? 'bg-red-600 hover:bg-red-700' : 'bg-red-800 hover:bg-red-900'} text-white rounded-md`}
                  >
                    {confirmReset ? 'Confirm Reset' : 'Reset Selected Component'}
                  </button>
                </div>
              )}
            </div>
          )}
          
          {activeTab === 'development' && !loading && (
            <div className="space-y-6">
              <div className="bg-navy p-4 rounded-md">
                <h3 className="text-lg font-semibold text-gold mb-4">Development Settings</h3>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-navy-lighter rounded-md">
                    <div>
                      <h4 className="font-semibold text-white mb-1">
                        Development Mode
                        <HelpIcon tooltip="Activates developer tools including self-analysis, enhanced logging, and experimental features. Use with caution in production." />
                      </h4>
                      <p className="text-sm text-gray-400">
                        Enables enhanced debugging, verbose logging, and access to experimental features.
                      </p>
                    </div>
                    <button
                      onClick={handleDevelopmentModeToggle}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                        developmentMode ? 'bg-gold' : 'bg-gray-600'
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                          developmentMode ? 'translate-x-6' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </div>
                  
                  {developmentMode && (
                    <>
                      <div className="p-4 bg-yellow-900 bg-opacity-20 border border-yellow-600 rounded-md">
                        <p className="text-sm text-yellow-400">
                          🚧 Development mode is active. Additional features and debugging tools are enabled.
                        </p>
                      </div>
                      
                      <div className="space-y-3">
                        <div className="p-3 bg-navy-lighter rounded-md">
                          <h5 className="font-medium text-gold mb-2">Available Development Features:</h5>
                          <ul className="list-disc list-inside text-sm text-gray-400 space-y-1">
                            <li>Self-analysis endpoints for code improvement ✅</li>
                            <li className="opacity-50">Enhanced error messages with stack traces (Coming Soon)</li>
                            <li className="opacity-50">API request/response logging (Coming Soon)</li>
                            <li className="opacity-50">Model performance metrics (Coming Soon)</li>
                            <li className="opacity-50">Database query monitoring (Coming Soon)</li>
                            <li className="opacity-50">Memory usage tracking (Coming Soon)</li>
                          </ul>
                        </div>
                        
                        <div className="p-3 bg-navy-lighter rounded-md">
                          <h5 className="font-medium text-gold mb-2">Quick Actions:</h5>
                          <div className="space-y-2">
                            <button 
                              className="w-full px-3 py-2 bg-gray-800 text-gray-500 rounded text-sm text-left cursor-not-allowed opacity-50"
                              disabled
                            >
                              📊 View Performance Metrics (Coming Soon)
                            </button>
                            <button 
                              onClick={() => {
                                // TODO: Implement self-analysis
                                alert('Self-analysis feature coming soon! This will analyze your codebase and suggest improvements.');
                              }}
                              className="w-full px-3 py-2 bg-navy hover:bg-navy-light text-white rounded text-sm text-left"
                            >
                              🔍 Run Self-Analysis (Available via API)
                            </button>
                            <button 
                              className="w-full px-3 py-2 bg-gray-800 text-gray-500 rounded text-sm text-left cursor-not-allowed opacity-50"
                              disabled
                            >
                              📝 Export Debug Logs (Coming Soon)
                            </button>
                          </div>
                        </div>
                      </div>
                    </>
                  )}
                </div>
              </div>
              
              {/* System Updates & Optimization Section */}
              <div className="bg-navy p-4 rounded-md">
                <h3 className="text-lg font-semibold text-gold mb-4">System Updates & Optimization</h3>
                
                <div className="space-y-4">
                  {/* Update Check Button and Status */}
                  <div className="flex items-center justify-between">
                    <div>
                      <button
                        onClick={checkForUpdates}
                        disabled={updateCheckState.checking}
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded-md flex items-center gap-2"
                      >
                        {updateCheckState.checking ? (
                          <>
                            <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-white"></div>
                            Checking...
                          </>
                        ) : (
                          <>
                            <Icon name="refresh" size={16} />
                            Check for Updates
                          </>
                        )}
                      </button>
                      {updateCheckState.lastChecked && (
                        <p className="text-xs text-gray-400 mt-1">
                          Last checked: {updateCheckState.lastChecked}
                        </p>
                      )}
                    </div>
                    
                    {/* Settings */}
                    <div className="space-y-2">
                      <label className="flex items-center gap-2 text-sm">
                        <input
                          type="checkbox"
                          checked={updateCheckState.autoCheck}
                          onChange={toggleAutoCheck}
                          className="rounded"
                        />
                        <span className="text-gray-300">Check automatically (weekly)</span>
                      </label>
                      <label className="flex items-center gap-2 text-sm">
                        <input
                          type="checkbox"
                          checked={updateCheckState.includeSpecs}
                          onChange={toggleIncludeSpecs}
                          className="rounded"
                        />
                        <span className="text-gray-300">Include system specs (anonymous)</span>
                      </label>
                    </div>
                  </div>
                  
                  {/* Update Results */}
                  {updateCheckState.results && !updateCheckState.results.error && (
                    <div className="space-y-4 mt-6">
                      {/* App Version */}
                      <div className="p-3 bg-navy-lighter rounded-md">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium text-white">Application Version</h4>
                          <span className="badge badge-green">
                            Current
                          </span>
                        </div>
                        <p className="text-sm text-gray-300">
                          Version: {updateCheckState.results.app_version}
                        </p>
                      </div>
                      
                      {/* Model Updates */}
                      {updateCheckState.results.model_updates.length > 0 && (
                        <div className="p-3 bg-navy-lighter rounded-md">
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-medium text-white flex items-center gap-2">
                              <span className="w-2 h-2 rounded-full bg-yellow-400"></span>
                              Model Updates Available ({updateCheckState.results.model_updates.length})
                            </h4>
                            <button
                              onClick={() => toggleInstructions('models')}
                              className="badge badge-blue badge-hover"
                            >
                              Update Instructions
                            </button>
                          </div>
                          <div className="space-y-2">
                            {updateCheckState.results.model_updates.map((update: any, idx: number) => (
                              <div key={idx} className="p-2 bg-navy rounded text-sm">
                                <div className="flex items-center justify-between">
                                  <span className="font-medium text-white">{update.name.split(':')[0]}</span>
                                  <span className="text-xs text-gray-400">{update.size_change}</span>
                                </div>
                                <p className="text-xs text-gray-300 mt-1">
                                  {update.current} → {update.latest}: {update.description}
                                </p>
                              </div>
                            ))}
                          </div>
                          {updateCheckState.showInstructions.models && (
                            <div className="mt-3 p-3 bg-navy rounded-md border border-gray-600">
                              <p className="text-xs text-gray-300 mb-2">
                                <strong className="text-yellow-400">Location:</strong> Anywhere
                              </p>
                              <p className="text-xs text-gray-300 mb-2">
                                <strong className="text-yellow-400">Environment:</strong> Regular CMD/PowerShell (NOT in venv)
                              </p>
                              <p className="text-xs text-gray-300 mb-2">
                                <strong className="text-yellow-400">Admin Mode:</strong> Not required
                              </p>
                              <p className="text-xs text-gray-300 mb-2">
                                <strong className="text-yellow-400">Update Commands:</strong>
                              </p>
                              {updateCheckState.results.model_updates.map((update: any, idx: number) => (
                                <pre key={idx} className="text-xs bg-black/50 p-2 rounded mt-2 text-white">
{`# Update ${update.name.split(':')[0]}
ollama pull ${update.name.split(':')[0]}:${update.latest}

# Remove old version (optional)
ollama rm ${update.name}`}
                                </pre>
                              ))}
                            </div>
                          )}
                        </div>
                      )}
                      
                      {/* Service Updates */}
                      {updateCheckState.results.service_updates.length > 0 && (
                        <div className="p-3 bg-navy-lighter rounded-md">
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-medium text-white flex items-center gap-2">
                              <span className="w-2 h-2 rounded-full bg-blue-400"></span>
                              Service Updates ({updateCheckState.results.service_updates.length})
                            </h4>
                            <button
                              onClick={() => toggleInstructions('services')}
                              className="badge badge-blue badge-hover"
                            >
                              Update Instructions
                            </button>
                          </div>
                          <div className="space-y-2">
                            {updateCheckState.results.service_updates.map((update: any, idx: number) => (
                              <div key={idx} className="p-2 bg-navy rounded text-sm">
                                <div className="flex items-center justify-between">
                                  <span className="font-medium text-white">{update.name}</span>
                                  <span className="badge badge-blue">
                                    {update.type}
                                  </span>
                                </div>
                                <p className="text-xs text-gray-300 mt-1">
                                  v{update.current} → v{update.latest}: {update.description}
                                </p>
                              </div>
                            ))}
                          </div>
                          {updateCheckState.showInstructions.services && (
                            <div className="mt-3 p-3 bg-navy rounded-md border border-gray-600">
                              <p className="text-xs text-gray-300 mb-2">
                                <strong className="text-yellow-400">Location:</strong> Backend folder
                              </p>
                              <p className="text-xs text-gray-300 mb-2">
                                <strong className="text-yellow-400">Environment:</strong> MUST be in venv_nemo
                              </p>
                              <p className="text-xs text-gray-300 mb-2">
                                <strong className="text-yellow-400">Admin Mode:</strong> Not required
                              </p>
                              <p className="text-xs text-gray-300 mb-2">
                                <strong className="text-yellow-400">Update Commands:</strong>
                              </p>
                              <pre className="text-xs bg-black/50 p-2 rounded mt-2 text-white">
{`cd F:\\assistant\\backend
..\\venv_nemo\\Scripts\\activate

# Update individual packages
${updateCheckState.results.service_updates.map((update: any) => 
  `pip install --upgrade ${update.name}==${update.latest}`
).join('\n')}

# Or update all at once
pip install --upgrade ${updateCheckState.results.service_updates.map((u: any) => `${u.name}==${u.latest}`).join(' ')}`}
                              </pre>
                            </div>
                          )}
                        </div>
                      )}
                      
                      {/* Security Updates */}
                      {updateCheckState.results.security_updates.length > 0 && (
                        <div className="p-3 bg-red-900/20 border border-red-600 rounded-md">
                          <h4 className="font-medium text-red-400 mb-2 flex items-center gap-2">
                            <span className="w-2 h-2 rounded-full bg-red-400 animate-pulse"></span>
                            Security Updates ({updateCheckState.results.security_updates.length})
                          </h4>
                          {/* Security update items would go here */}
                        </div>
                      )}
                      
                      {/* Recommendations */}
                      {updateCheckState.results.recommendations.length > 0 && (
                        <div className="p-3 bg-navy-lighter rounded-md">
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-medium text-white flex items-center gap-2">
                              <span className="w-2 h-2 rounded-full bg-green-400"></span>
                              New Model Recommendations
                            </h4>
                            <button
                              onClick={() => toggleInstructions('recommendations')}
                              className="badge badge-blue badge-hover"
                            >
                              Install Instructions
                            </button>
                          </div>
                          <div className="space-y-2">
                            {updateCheckState.results.recommendations.map((rec: any, idx: number) => (
                              <div key={idx} className="p-2 bg-navy rounded text-sm">
                                <div className="flex items-center justify-between">
                                  <span className="font-medium text-white">{rec.model}</span>
                                  <span className="text-xs text-gray-400">VRAM: {rec.vram_required}GB</span>
                                </div>
                                <p className="text-xs text-gray-300 mt-1">{rec.reason}</p>
                                <p className="text-xs text-green-400 mt-1">{rec.capabilities}</p>
                              </div>
                            ))}
                          </div>
                          {updateCheckState.showInstructions.recommendations && (
                            <div className="mt-3 p-3 bg-navy rounded-md border border-gray-600">
                              <p className="text-xs text-gray-300 mb-2">
                                <strong className="text-yellow-400">Location:</strong> Anywhere
                              </p>
                              <p className="text-xs text-gray-300 mb-2">
                                <strong className="text-yellow-400">Environment:</strong> Regular CMD/PowerShell (NOT in venv)
                              </p>
                              <p className="text-xs text-gray-300 mb-2">
                                <strong className="text-yellow-400">Admin Mode:</strong> Not required
                              </p>
                              <p className="text-xs text-gray-300 mb-2">
                                <strong className="text-yellow-400">Install Commands:</strong>
                              </p>
                              {updateCheckState.results.recommendations.map((rec: any, idx: number) => (
                                <pre key={idx} className="text-xs bg-black/50 p-2 rounded mt-2 text-white">
{`# Install ${rec.model}
ollama pull ${rec.model}

# After installation, you can:
# 1. Load it in the Models tab
# 2. Select it in your chat interface`}
                                </pre>
                              ))}
                            </div>
                          )}
                        </div>
                      )}
                      
                      {/* News & Announcements */}
                      {updateCheckState.results.news.length > 0 && (
                        <div className="p-3 bg-navy-lighter rounded-md">
                          <h4 className="font-medium text-white mb-2">📢 News & Announcements</h4>
                          <ul className="space-y-1">
                            {updateCheckState.results.news.map((item: string, idx: number) => (
                              <li key={idx} className="text-sm text-gray-300 flex items-start gap-2">
                                <span className="text-gold">•</span>
                                {item}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                  
                  {/* Error Message */}
                  {updateCheckState.results?.error && (
                    <div className="p-3 bg-red-900/20 border border-red-600 rounded-md">
                      <p className="text-sm text-red-400">{updateCheckState.results.error}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
      </Draggable>
    </div>
  );
};

export default AdminSettingsPanel;