import React, { useState, useEffect } from 'react';
import fileService, { ProcessingStats } from '../../services/fileService';

interface GPUUtilizationDisplayProps {
  refreshInterval?: number; // in milliseconds
  showDetails?: boolean;
}

const GPUUtilizationDisplay: React.FC<GPUUtilizationDisplayProps> = ({ 
  refreshInterval = 2000,
  showDetails = false 
}) => {
  const [stats, setStats] = useState<ProcessingStats | null>(null);
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
    } catch (err) {
      console.error('Error fetching GPU stats:', err);
      setError('Failed to fetch GPU statistics');
      setLoading(false);
    }
  };

  // Helper function to determine color based on GPU usage
  const getGPUBarColor = (usage: number) => {
    if (usage < 30) return 'bg-green-500';
    if (usage < 70) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  // Return null if we want to hide everything when idle
  if (!loading && !error && stats && stats.gpu_usage === 0 && stats.processing_files === 0 && !showDetails) {
    return null;
  }

  return (
    <div className="bg-navy-light p-3 rounded-md text-white">
      {loading ? (
        <div className="flex justify-center items-center h-10">
          <div className="animate-pulse text-sm text-gray-400">Loading system stats...</div>
        </div>
      ) : error ? (
        <div className="text-red-400 text-sm">{error}</div>
      ) : stats ? (
        <div className="space-y-2">
          <div className="flex flex-col">
            <div className="flex justify-between mb-1">
              <span className="text-sm text-gray-400">GPU Utilization</span>
              <span className="text-sm font-bold">{Math.round(stats.gpu_usage || 0)}%</span>
            </div>
            <div className="w-full bg-navy h-3 rounded-full overflow-hidden">
              <div 
                className={`h-full ${getGPUBarColor(stats.gpu_usage || 0)} transition-all duration-500 ease-out`}
                style={{ width: `${stats.gpu_usage || 0}%` }}
              ></div>
            </div>
          </div>
          
          {showDetails && (
            <div className="grid grid-cols-2 gap-2 text-sm mt-2">
              <div>
                <span className="text-gray-400">Processing:</span>
                <span className="ml-2 font-bold">{stats.processing_files}</span>
              </div>
              <div>
                <span className="text-gray-400">Processed:</span>
                <span className="ml-2 font-bold">{stats.processed_files}</span>
              </div>
              <div>
                <span className="text-gray-400">Failed:</span>
                <span className="ml-2 font-bold">{stats.failed_files}</span>
              </div>
              <div>
                <span className="text-gray-400">Chunks:</span>
                <span className="ml-2 font-bold">{stats.total_chunks}</span>
              </div>
              
              {stats.eta !== undefined && stats.eta > 0 && (
                <div className="col-span-2">
                  <span className="text-gray-400">ETA:</span>
                  <span className="ml-2 font-bold">{Math.ceil(stats.eta)}s</span>
                </div>
              )}
            </div>
          )}
          
          {!showDetails && stats.processing_files > 0 && (
            <div className="text-xs text-gray-400">
              Processing {stats.processing_files} file{stats.processing_files !== 1 ? 's' : ''}
              {stats.eta !== undefined && stats.eta > 0 ? ` (ETA: ${Math.ceil(stats.eta)}s)` : ''}
            </div>
          )}
        </div>
      ) : null}
    </div>
  );
};

export default GPUUtilizationDisplay;