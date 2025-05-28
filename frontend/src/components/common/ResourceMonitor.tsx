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

  // Fetch GPU status only (more frequent)
  const fetchGPUStatus = async () => {
    try {
      const modelData = await modelService.getQuickModelStatus();
      setModelStatus(modelData);
      setError(null);
    } catch (err: any) {
      console.error('[ResourceMonitor] Failed to fetch GPU status:', err);
      setError('Connection Error');
    }
  };

  // Fetch all resources (less frequent)
  const fetchAllResources = async () => {
    try {
      const [modelData, systemData] = await Promise.all([
        modelService.getQuickModelStatus(),
        systemService.getSystemResources().catch((err) => {
          console.error('[ResourceMonitor] System resources error:', err);
          return null;
        })
      ]);
      
      setModelStatus(modelData);
      
      // Get real system resources if available
      if (systemData) {
        setSystemResources({
          cpu: systemData.cpu,
          ram: systemData.ram,
          disk: systemData.disk
        });
      }
      
      setError(null);
    } catch (err: any) {
      console.error('[ResourceMonitor] Failed to fetch resources:', err);
      setError('Connection Error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Initial fetch of all resources
    fetchAllResources();

    // Poll GPU every 2 seconds for real-time updates
    const gpuInterval = setInterval(fetchGPUStatus, 2000);
    
    // Poll other resources every 10 seconds
    const resourceInterval = setInterval(fetchAllResources, 10000);

    return () => {
      clearInterval(gpuInterval);
      clearInterval(resourceInterval);
    };
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

  // Truncate CPU model name
  const truncateCpuModel = (model: string) => {
    // Extract just the processor model, remove frequency info
    const parts = model.split('@');
    let cpuName = parts[0].trim();
    
    // Further truncate if still too long
    if (cpuName.length > 25) {
      cpuName = cpuName.substring(0, 22) + '...';
    }
    
    return cpuName;
  };

  // Format storage values to display in TB if over 1000GB
  const formatStorage = (gb: number) => {
    if (gb >= 1000) {
      return { value: gb / 1000, unit: 'TB' };
    }
    return { value: gb, unit: 'GB' };
  };

  const diskFormatted = systemResources ? formatStorage(systemResources.disk.total_gb) : { value: 0, unit: 'GB' };

  return (
    <div className="flex items-start space-x-6">
      {/* NVIDIA GPU Section */}
      <div className="flex flex-col">
        <div className="flex items-center space-x-2 mb-1">
          <span className="text-xs font-medium" style={{ color: '#76B900' }}>NVIDIA</span>
          <span className="text-[10px] text-gray-400">{gpuName}</span>
        </div>
        
        <div className="space-y-2">
          {/* VRAM Gauge */}
          <div>
            <div className="text-[10px] text-gray-400 mb-1">VRAM</div>
            <HorizontalGauge
              label=""
              value={modelStatus.system.used_vram_gb}
              maxValue={modelStatus.system.total_vram_gb}
              unit="GB"
              color="#76B900"
              width={180}
            />
          </div>
          
          {/* GPU Utilization Gauge */}
          <div>
            <div className="text-[10px] text-gray-400 mb-1">Utilization</div>
            <HorizontalGauge
              label=""
              value={modelStatus.system.gpu_utilization || 0}
              maxValue={100}
              unit="%"
              color="#76B900"
              width={180}
            />
          </div>
        </div>
      </div>

      {/* Divider */}
      <div className="h-20 w-px bg-gray-700"></div>

      {/* CPU Section */}
      {systemResources && (
        <div className="flex flex-col">
          <div className="flex items-center space-x-2 mb-1">
            <span 
              className="text-xs font-medium" 
              style={{ color: getCpuColor() }}
            >
              {systemResources.cpu.brand}
            </span>
            <span className="text-[10px] text-gray-400">
              {truncateCpuModel(systemResources.cpu.model)}
            </span>
          </div>
          <div className="text-[10px] text-gray-400 mb-1">Utilization</div>
          <HorizontalGauge
            label=""
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
          <div className="flex items-center space-x-2 mb-1">
            <span className="text-xs font-medium text-purple-500">RAM</span>
            {systemResources.ram.speed && (
              <span className="text-[10px] text-gray-400">{systemResources.ram.speed}</span>
            )}
          </div>
          <div className="text-[10px] text-gray-400 mb-1">Utilization</div>
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
          <div className="flex items-center space-x-2 mb-1">
            <span className="text-xs font-medium text-white">Storage</span>
            {systemResources.disk.type && (
              <span className="text-[10px] text-gray-400">{systemResources.disk.type}</span>
            )}
          </div>
          <div className="text-[10px] text-gray-400 mb-1">Utilization</div>
          <HorizontalGauge
            label=""
            value={systemResources.disk.used_gb}
            maxValue={systemResources.disk.total_gb}
            unit={diskFormatted.unit}
            color="#FFFFFF"
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