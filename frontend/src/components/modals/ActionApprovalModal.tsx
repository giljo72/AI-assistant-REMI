import React, { useState, useEffect } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface ActionRequest {
  id: string;
  type: 'command' | 'file_write';
  details: {
    // For commands
    command?: string;
    command_list?: string[];
    working_directory?: string;
    // For file writes
    filepath?: string;
    content_preview?: string;
    content_length?: number;
    // Common
    reason: string;
  };
  status: string;
  created_at: string;
}

interface ActionApprovalModalProps {
  isOpen: boolean;
  action: ActionRequest | null;
  onApprove: (actionId: string) => void;
  onDeny: (actionId: string) => void;
}

const ActionApprovalModal: React.FC<ActionApprovalModalProps> = ({
  isOpen,
  action,
  onApprove,
  onDeny
}) => {
  const [showFullContent, setShowFullContent] = useState(false);

  if (!isOpen || !action) return null;

  const isCommand = action.type === 'command';
  const isFileWrite = action.type === 'file_write';

  const getRiskLevel = () => {
    if (isCommand) {
      const cmd = action.details.command || '';
      if (cmd.includes('rm') || cmd.includes('del') || cmd.includes('format')) return 'high';
      if (cmd.includes('install') || cmd.includes('update')) return 'medium';
      return 'low';
    }
    return 'medium'; // file writes are always medium risk
  };

  const riskLevel = getRiskLevel();
  const riskColors = {
    low: 'text-green-400 border-green-500',
    medium: 'text-yellow-400 border-yellow-500',
    high: 'text-red-400 border-red-500'
  };

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-60 p-4">
      <div className="bg-gray-800 rounded-lg max-w-3xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-red-900/20 border-b border-red-800 p-4">
          <h2 className="text-xl font-bold text-red-400 flex items-center">
            <span className="text-2xl mr-2">🔴</span>
            APPROVAL REQUIRED - SELF-AWARE MODE
          </h2>
          <p className="text-sm text-gray-400 mt-1">
            Each action requires individual approval. There is no "approve all" option.
          </p>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {isCommand && (
            <>
              <h3 className="text-lg font-semibold text-white mb-4">Command Execution Request</h3>
              
              <div className="bg-gray-900 rounded-lg p-4 mb-4">
                <div className="mb-3">
                  <span className="text-gray-400 text-sm">Command:</span>
                  <div className="bg-black rounded p-3 mt-1 font-mono text-green-400">
                    {action.details.command}
                  </div>
                </div>
                
                <div className="mb-3">
                  <span className="text-gray-400 text-sm">Working Directory:</span>
                  <div className="text-white mt-1">{action.details.working_directory}</div>
                </div>
                
                <div className="mb-3">
                  <span className="text-gray-400 text-sm">Risk Level:</span>
                  <span className={`ml-2 font-semibold ${riskColors[riskLevel]}`}>
                    {riskLevel.toUpperCase()}
                  </span>
                </div>
                
                <div>
                  <span className="text-gray-400 text-sm">Reason:</span>
                  <div className="text-white mt-1">{action.details.reason}</div>
                </div>
              </div>
            </>
          )}

          {isFileWrite && (
            <>
              <h3 className="text-lg font-semibold text-white mb-4">File Modification Request</h3>
              
              <div className="bg-gray-900 rounded-lg p-4 mb-4">
                <div className="mb-3">
                  <span className="text-gray-400 text-sm">File Path:</span>
                  <div className="text-white mt-1 font-mono">{action.details.filepath}</div>
                </div>
                
                <div className="mb-3">
                  <span className="text-gray-400 text-sm">Content Size:</span>
                  <div className="text-white mt-1">{action.details.content_length} characters</div>
                </div>
                
                <div className="mb-3">
                  <span className="text-gray-400 text-sm">Reason:</span>
                  <div className="text-white mt-1">{action.details.reason}</div>
                </div>
                
                <div>
                  <span className="text-gray-400 text-sm">Content Preview:</span>
                  <div className="mt-2">
                    <SyntaxHighlighter
                      language={getLanguageFromFilename(action.details.filepath || '')}
                      style={vscDarkPlus}
                      customStyle={{
                        backgroundColor: '#0d1929',
                        border: '1px solid #1a2b47',
                        borderRadius: '0.375rem',
                        fontSize: '0.875rem',
                        maxHeight: showFullContent ? 'none' : '200px',
                        overflow: 'auto'
                      }}
                    >
                      {action.details.content_preview || ''}
                    </SyntaxHighlighter>
                    
                    {action.details.content_preview && action.details.content_preview.endsWith('...') && (
                      <button
                        onClick={() => setShowFullContent(!showFullContent)}
                        className="text-blue-400 hover:text-blue-300 text-sm mt-2"
                      >
                        {showFullContent ? 'Show less' : 'Show more'}
                      </button>
                    )}
                  </div>
                </div>
              </div>
            </>
          )}

          {/* Security Notice */}
          <div className="bg-yellow-900/20 border border-yellow-800 rounded-lg p-4">
            <h4 className="text-yellow-400 font-semibold mb-2">⚠️ Security Notice</h4>
            <ul className="text-sm text-gray-300 space-y-1">
              <li>• This action will be executed immediately upon approval</li>
              <li>• All actions are logged for audit purposes</li>
              <li>• Files are automatically backed up before modification</li>
              {isCommand && <li>• Commands have a 5-minute timeout</li>}
            </ul>
          </div>
        </div>

        {/* Footer */}
        <div className="bg-gray-900 border-t border-gray-700 p-4 flex justify-between items-center">
          <span className="text-sm text-gray-400">
            Action ID: {action.id.substring(0, 8)}...
          </span>
          
          <div className="flex gap-3">
            <button
              onClick={() => onDeny(action.id)}
              className="px-6 py-2 bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg transition-colors"
            >
              DENY
            </button>
            <button
              onClick={() => onApprove(action.id)}
              className="px-6 py-2 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition-colors"
            >
              APPROVE THIS ACTION
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Helper function to determine language for syntax highlighting
function getLanguageFromFilename(filename: string): string {
  const ext = filename.split('.').pop()?.toLowerCase();
  const languageMap: { [key: string]: string } = {
    'js': 'javascript',
    'jsx': 'javascript',
    'ts': 'typescript',
    'tsx': 'typescript',
    'py': 'python',
    'json': 'json',
    'html': 'html',
    'css': 'css',
    'scss': 'scss',
    'sql': 'sql',
    'md': 'markdown',
    'yml': 'yaml',
    'yaml': 'yaml',
    'sh': 'bash',
    'bat': 'batch',
  };
  return languageMap[ext || ''] || 'text';
}

export default ActionApprovalModal;