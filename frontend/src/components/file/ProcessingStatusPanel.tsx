import React, { useState, useEffect } from 'react';
import fileService, { ProcessingStats } from '../../services/fileService';
import GPUUtilizationDisplay from '../common/GPUUtilizationDisplay';

interface ProcessingStatusPanelProps {
  refreshInterval?: number; // in milliseconds
}

const ProcessingStatusPanel: React.FC<ProcessingStatusPanelProps> = ({ 
  refreshInterval = 2000,
}) => {
  const [stats, setStats] = useState<ProcessingStats | null>(null);
  const [expanded, setExpanded] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Initial fetch
    fetchProcessingStats();
    
    // Set up interval for periodic updates
    const intervalId = setInterval(fetchProcessingStats, refreshInterval);
    
    // Clean up interval on unmount
    return () => clearInterval(intervalId);
  }, [refreshInterval]);

  const fetchProcessingStats = async () => {
    try {
      const data = await fileService.getProcessingStatus();
      setStats(data);
      setLoading(false);
      setError(null);
      
      // Auto expand when there's active processing
      if (data.processing_files > 0) {
        setExpanded(true);
      }
    } catch (err) {
      console.error('Error fetching processing stats:', err);
      setError('Failed to fetch processing statistics');
      setLoading(false);
    }
  };

  // Return null if there's nothing to show
  if (!loading && !error && stats && stats.total_files === 0 && stats.gpu_usage === 0) {
    return null;
  }

  return (
    <div className="bg-navy-light border border-navy-lighter rounded-md overflow-hidden mb-4">
      <div 
        className="p-3 flex justify-between items-center cursor-pointer hover:bg-navy-lighter"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center">
          <span className="text-gold mr-2">{expanded ? '▼' : '▶'}</span>
          <h3 className="font-semibold text-white">Processing Status</h3>
          
          {!loading && !error && stats && stats.processing_files > 0 && (
            <span className="text-sm text-green-400 ml-2 animate-pulse">
              Active
            </span>
          )}
        </div>
        
        {!loading && !error && stats && (
          <div className="text-sm text-gray-400">
            {stats.processing_files} / {stats.total_files} files processing
          </div>
        )}
      </div>
      
      {expanded && (
        <div className="p-3 border-t border-navy-lighter">
          {loading ? (
            <div className="flex justify-center items-center h-20">
              <div className="animate-pulse text-gray-400">Loading processing stats...</div>
            </div>
          ) : error ? (
            <div className="text-red-400 p-3">{error}</div>
          ) : stats ? (
            <div className="space-y-4">
              <div className="grid grid-cols-3 gap-3">
                <div className="bg-navy p-3 rounded-md">
                  <div className="text-sm text-gray-400">Processing</div>
                  <div className="text-xl font-bold text-white">{stats.processing_files}</div>
                </div>
                <div className="bg-navy p-3 rounded-md">
                  <div className="text-sm text-gray-400">Processed</div>
                  <div className="text-xl font-bold text-green-400">{stats.processed_files}</div>
                </div>
                <div className="bg-navy p-3 rounded-md">
                  <div className="text-sm text-gray-400">Failed</div>
                  <div className="text-xl font-bold text-red-400">{stats.failed_files}</div>
                </div>
              </div>
              
              <div>
                <h4 className="text-sm text-gray-400 mb-1">GPU Utilization</h4>
                <GPUUtilizationDisplay showDetails={true} refreshInterval={refreshInterval} />
              </div>
              
              {stats.processing_files > 0 && stats.eta !== undefined && stats.eta > 0 && (
                <div>
                  <div className="text-sm text-gray-400 mb-1">Estimated Time Remaining</div>
                  <div className="text-xl font-bold text-white">{Math.ceil(stats.eta)} seconds</div>
                </div>
              )}
              
              {stats.total_chunks > 0 && (
                <div>
                  <div className="text-sm text-gray-400 mb-1">Document Chunks</div>
                  <div className="text-xl font-bold text-white">{stats.total_chunks}</div>
                </div>
              )}
            </div>
          ) : null}
        </div>
      )}
    </div>
  );
};

export default ProcessingStatusPanel;