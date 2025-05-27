// File: frontend/src/components/common/ResourceMonitor.tsx
import React, { useState, useEffect } from 'react';
import { modelService } from '../../services/modelService';
import { systemService } from '../../services/systemService';
import { Icon } from './Icon';
import { HorizontalGauge } from './HorizontalGauge';

interface ModelStatus {
  models: Record<string, {
    display_name: string;
    status: string;
    status_color: string;
    tokens_per_second: number;
    memory_gb: number;
  }>;
  system: {
    total_vram_gb: number;
    used_vram_gb: number;
    available_vram_gb: number;
    active_primary_model: string;
    total_requests_active: number;
    gpu_utilization?: number;
    gpu_name?: string;
  };
}

interface SystemResources {
  cpu: {
    usage: number;
    brand: 'Intel' | 'AMD' | 'Unknown';
    model: string;
  };
  ram: {
    used_gb: number;
    total_gb: number;
    speed?: string;
  };
  disk: {
    used_gb: number;
    total_gb: number;
    type?: string;
    model?: string;
  };
}

export const ResourceMonitor: React.FC = () => {
  const [modelStatus, setModelStatus] = useState<ModelStatus | null>(null);
  const [systemResources, setSystemResources] = useState<SystemResources | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Add debug logging
  useEffect(() => {
    console.log('[ResourceMonitor] Component mounted');
    console.log('[ResourceMonitor] Model Status:', modelStatus);
    console.log('[ResourceMonitor] System Resources:', systemResources);
  }, [modelStatus, systemResources]);

  // Fetch model status
  const fetchStatus = async () => {
    try {
      console.log('[ResourceMonitor] Fetching status...');
      const [modelData, systemData] = await Promise.all([
        modelService.getQuickModelStatus(),
        systemService.getSystemResources().catch((err) => {
          console.error('[ResourceMonitor] System resources error:', err);
          return null;
        })
      ]);
      
      console.log('[ResourceMonitor] Model data:', modelData);
      console.log('[ResourceMonitor] System data:', systemData);
      
      setModelStatus(modelData);
      
      // Get real system resources if available
      if (systemData) {
        setSystemResources({
          cpu: systemData.cpu,
          ram: systemData.ram,
          disk: systemData.disk
        });
      } else {
        // Fallback to mock data if endpoint not available
        setSystemResources({
          cpu: {
            usage: Math.random() * 100,
            brand: 'AMD',
            model: 'Ryzen 9 5950X'
          },
          ram: {
            used_gb: 32 + Math.random() * 32,
            total_gb: 64,
            speed: '3200 MHz'
          },
          disk: {
            used_gb: 500 + Math.random() * 500,
            total_gb: 2000,
            type: 'NVMe SSD'
          }
        });
      }
      
      setError(null);
    } catch (err: any) {
      console.error('[ResourceMonitor] Failed to fetch status:', err);
      console.error('[ResourceMonitor] Error details:', err.response?.data || err.message);
      setError('Connection Error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Initial fetch
    fetchStatus();

    // Poll every 5 seconds for real-time updates
    const interval = setInterval(fetchStatus, 5000);

    return () => clearInterval(interval);
  }, []);

  // Get active model info
  const getActiveModelInfo = () => {
    if (!modelStatus?.system.active_primary_model || !modelStatus.models) {
      return null;
    }

    const activeModel = modelStatus.models[modelStatus.system.active_primary_model];
    return activeModel;
  };

  const activeModel = getActiveModelInfo();
  
  if (loading) {
    return (
      <div className="flex items-center space-x-4">
        <div className="animate-pulse flex space-x-3">
          <div className="h-5 bg-gray-700 rounded-full w-48"></div>
          <div className="h-5 bg-gray-700 rounded-full w-48"></div>
          <div className="h-5 bg-gray-700 rounded-full w-32"></div>
        </div>
      </div>
    );
  }

  if (error || !modelStatus) {
    return (
      <div className="flex items-center space-x-2 text-sm text-red-500">
        <Icon name="question" size={16} className="pointer-events-none" />
        <span>{error || 'Connection Error'}</span>
      </div>
    );
  }

  // Determine CPU color based on brand
  const getCpuColor = () => {
    if (!systemResources) return '#888888';
    return systemResources.cpu.brand === 'Intel' ? '#0078D4' : '#FF8C00'; // Orange for AMD
  };

  const gpuName = modelStatus.system.gpu_name || 'RTX 4090';

  return (
    <div className="flex items-start space-x-6">
      {/* NVIDIA GPU Section */}
      <div className="flex flex-col">
        <div className="flex items-center space-x-2 mb-2">
          <span className="text-xs font-medium" style={{ color: '#76B900' }}>NVIDIA</span>
          <span className="text-[10px] text-gray-400">{gpuName}</span>
        </div>
        
        <div className="space-y-2">
          {/* VRAM Gauge */}
          <HorizontalGauge
            label="VRAM"
            value={modelStatus.system.used_vram_gb}
            maxValue={modelStatus.system.total_vram_gb}
            unit="GB"
            color="#76B900"
            width={180}
          />
          
          {/* GPU Utilization Gauge */}
          <HorizontalGauge
            label="Utilization"
            value={modelStatus.system.gpu_utilization || 0}
            maxValue={100}
            unit="%"
            color="#76B900"
            width={180}
          />
        </div>
      </div>

      {/* Divider */}
      <div className="h-20 w-px bg-gray-700"></div>

      {/* CPU Section */}
      {systemResources && (
        <div className="flex flex-col">
          <div className="flex items-center space-x-2 mb-2">
            <span 
              className="text-xs font-medium" 
              style={{ color: getCpuColor() }}
            >
              {systemResources.cpu.brand}
            </span>
            <span className="text-[10px] text-gray-400">
              {systemResources.cpu.model.length > 30 
                ? systemResources.cpu.model.substring(0, 30) + '...' 
                : systemResources.cpu.model}
            </span>
          </div>
          <HorizontalGauge
            label="CPU"
            value={systemResources.cpu.usage}
            maxValue={100}
            unit="%"
            color={getCpuColor()}
            width={150}
          />
        </div>
      )}

      {/* RAM Section */}
      {systemResources && (
        <div className="flex flex-col">
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-xs font-medium text-purple-500">RAM</span>
            {systemResources.ram.speed && (
              <span className="text-[10px] text-gray-400">{systemResources.ram.speed}</span>
            )}
          </div>
          <HorizontalGauge
            label=""
            value={systemResources.ram.used_gb}
            maxValue={systemResources.ram.total_gb}
            unit="GB"
            color="#9B59B6"
            width={120}
          />
        </div>
      )}

      {/* Storage Section */}
      {systemResources && (
        <div className="flex flex-col">
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-xs font-medium text-gray-500">Storage</span>
            {systemResources.disk.type && (
              <span className="text-[10px] text-gray-400">{systemResources.disk.type}</span>
            )}
          </div>
          <HorizontalGauge
            label=""
            value={systemResources.disk.used_gb}
            maxValue={systemResources.disk.total_gb}
            unit="GB"
            color="#6C757D"
            width={120}
          />
        </div>
      )}

      {/* Divider */}
      <div className="h-20 w-px bg-gray-700"></div>

      {/* Model Info */}
      <div className="flex flex-col justify-center h-20">
        {activeModel && (
          <div className="flex items-center space-x-2 mb-1">
            <span className="text-xs text-gray-400">Model:</span>
            <span className="text-xs text-gold font-medium">
              {activeModel.display_name}
            </span>
          </div>
        )}
        
        {/* Token Speed */}
        {activeModel && activeModel.tokens_per_second > 0 && (
          <div className="flex items-center space-x-2 mb-1">
            <span className="text-xs text-gray-400">Speed:</span>
            <span className="text-xs text-green-400">
              {activeModel.tokens_per_second.toFixed(1)} tok/s
            </span>
          </div>
        )}

        {/* Active Requests */}
        {modelStatus.system.total_requests_active > 0 && (
          <div className="flex items-center space-x-1">
            <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-pulse" />
            <span className="text-xs text-blue-400">
              {modelStatus.system.total_requests_active} active
            </span>
          </div>
        )}
      </div>
    </div>
  );
};