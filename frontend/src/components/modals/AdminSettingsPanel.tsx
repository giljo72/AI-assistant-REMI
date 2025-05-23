import React, { useState, useEffect } from 'react';
import adminService, { SystemInfo } from '../../services/adminService';

interface AdminSettingsPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

const AdminSettingsPanel: React.FC<AdminSettingsPanelProps> = ({ isOpen, onClose }) => {
  const [systemInfo, setSystemInfo] = useState<SystemInfo | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'info' | 'reset' | 'development'>('info');
  const [developmentMode, setDevelopmentMode] = useState<boolean>(false);
  const [resetAction, setResetAction] = useState<string>('');
  const [confirmReset, setConfirmReset] = useState<boolean>(false);
  const [operationStatus, setOperationStatus] = useState<{message: string, type: 'success' | 'error'} | null>(null);

  // Fetch system info when panel opens
  useEffect(() => {
    if (isOpen) {
      fetchSystemInfo();
    }
  }, [isOpen]);

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
          response = await adminService.resetDatabase();
          break;
        case 'vector':
          response = await adminService.resetVectorStore();
          break;
        case 'files':
          response = await adminService.resetFiles();
          break;
        case 'all':
          response = await adminService.resetEverything();
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
      <div className="bg-navy-light text-white rounded-lg shadow-lg w-full max-w-3xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-4 bg-navy flex items-center justify-between border-b border-navy-lighter">
          <h2 className="text-xl font-bold text-gold">System Administration</h2>
          <button 
            onClick={onClose}
            className="text-gray-400 hover:text-white"
          >
            ✕
          </button>
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
              
              <div className="flex justify-end">
                <button 
                  onClick={fetchSystemInfo}
                  className="px-4 py-2 bg-navy hover:bg-navy-lighter text-white rounded-md flex items-center"
                >
                  <span className="mr-2">🔄</span> Refresh
                </button>
              </div>
            </div>
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
                  <h4 className="font-semibold text-gold mb-1">Reset Database</h4>
                  <p className="text-sm text-gray-400">
                    Clears all database tables while preserving the schema. This will remove all projects, documents, and chats.
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
                  className={`p-4 rounded-md border transition-colors cursor-pointer ${resetAction === 'all' ? 'bg-navy border-gold' : 'bg-navy-lighter border-navy-lighter hover:border-gray-500'}`}
                  onClick={() => setResetAction('all')}
                >
                  <h4 className="font-semibold text-gold mb-1">Reset Everything</h4>
                  <p className="text-sm text-gray-400">
                    Completely resets the system by clearing the database, vector store, and all files. This is a clean slate reset.
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
                      <h4 className="font-semibold text-white mb-1">Development Mode</h4>
                      <p className="text-sm text-gray-400">
                        Enables enhanced debugging, verbose logging, and access to experimental features.
                      </p>
                    </div>
                    <button
                      onClick={() => setDevelopmentMode(!developmentMode)}
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
                            <li>Enhanced error messages with stack traces</li>
                            <li>API request/response logging</li>
                            <li>Model performance metrics</li>
                            <li>Database query monitoring</li>
                            <li>Memory usage tracking</li>
                            <li>Self-analysis endpoints for code improvement</li>
                          </ul>
                        </div>
                        
                        <div className="p-3 bg-navy-lighter rounded-md">
                          <h5 className="font-medium text-gold mb-2">Quick Actions:</h5>
                          <div className="space-y-2">
                            <button className="w-full px-3 py-2 bg-navy hover:bg-navy-light text-white rounded text-sm text-left">
                              📊 View Performance Metrics
                            </button>
                            <button className="w-full px-3 py-2 bg-navy hover:bg-navy-light text-white rounded text-sm text-left">
                              🔍 Run Self-Analysis
                            </button>
                            <button className="w-full px-3 py-2 bg-navy hover:bg-navy-light text-white rounded text-sm text-left">
                              📝 Export Debug Logs
                            </button>
                          </div>
                        </div>
                      </div>
                    </>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminSettingsPanel;