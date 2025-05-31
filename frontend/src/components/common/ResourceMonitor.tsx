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
    // Future: Multi-GPU support
    gpus?: Array<{
      id: number;
      name: string;
      total_vram_gb: number;
      used_vram_gb: number;
      utilization: number;
      brand: 'NVIDIA' | 'AMD' | 'Intel';
    }>;
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
    <div className="flex items-center space-x-4">
      {/* Primary NVIDIA GPU Section */}
      <div className="flex flex-col">
        <div className="flex items-center space-x-2 mb-1">
          <span className="text-[10px] font-medium" style={{ color: '#76B900' }}>NVIDIA</span>
          <span className="text-[9px] text-gray-400">{gpuName}</span>
        </div>
        
        {/* VRAM */}
        <div className="flex items-start space-x-2">
          <span className="text-[9px] text-gray-400" style={{ width: '85px' }}>VRAM used: {modelStatus.system.used_vram_gb.toFixed(1)}GB</span>
          <div className="relative" style={{ width: '80px', height: '6px', marginTop: '5px' }}>
            <div className="absolute inset-0 bg-gray-800 rounded-full overflow-hidden">
              <div 
                className="h-full transition-all duration-300 ease-out rounded-full"
                style={{ 
                  width: `${Math.min((modelStatus.system.used_vram_gb / modelStatus.system.total_vram_gb) * 100, 100)}%`,
                  backgroundColor: '#76B900',
                  boxShadow: '0 0 10px #76B90040'
                }}
              />
            </div>
          </div>
        </div>
        
        {/* GPU Utilization */}
        <div className="flex items-start space-x-2">
          <span className="text-[9px] text-gray-400" style={{ width: '85px' }}>Utilization: {(modelStatus.system.gpu_utilization || 0).toFixed(0)}%</span>
          <div className="relative" style={{ width: '80px', height: '6px', marginTop: '4px' }}>
            <div className="absolute inset-0 bg-gray-800 rounded-full overflow-hidden">
              <div 
                className="h-full transition-all duration-300 ease-out rounded-full"
                style={{ 
                  width: `${modelStatus.system.gpu_utilization || 0}%`,
                  backgroundColor: '#76B900',
                  boxShadow: '0 0 10px #76B90040'
                }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Secondary GPU Section - displays when multiple GPUs detected */}
      {modelStatus.system.gpus && modelStatus.system.gpus.length > 1 && (
        modelStatus.system.gpus.slice(1).map((gpu, index) => (
          <div key={gpu.id} className="flex flex-col">
            <div className="flex items-center space-x-2 mb-1">
              <span 
                className="text-[10px] font-medium" 
                style={{ color: gpu.brand === 'NVIDIA' ? '#76B900' : gpu.brand === 'AMD' ? '#FF8C00' : '#0078D4' }}
              >
                {gpu.brand}
              </span>
              <span className="text-[9px] text-gray-400">{gpu.name}</span>
            </div>
            
            {/* VRAM */}
            <div className="flex items-start space-x-2">
              <span className="text-[9px] text-gray-400" style={{ width: '85px' }}>VRAM used: {gpu.used_vram_gb.toFixed(1)}GB</span>
              <div className="relative" style={{ width: '80px', height: '6px', marginTop: '5px' }}>
                <div className="absolute inset-0 bg-gray-800 rounded-full overflow-hidden">
                  <div 
                    className="h-full transition-all duration-300 ease-out rounded-full"
                    style={{ 
                      width: `${Math.min((gpu.used_vram_gb / gpu.total_vram_gb) * 100, 100)}%`,
                      backgroundColor: gpu.brand === 'NVIDIA' ? '#76B900' : gpu.brand === 'AMD' ? '#FF8C00' : '#0078D4',
                      boxShadow: `0 0 10px ${gpu.brand === 'NVIDIA' ? '#76B90040' : gpu.brand === 'AMD' ? '#FF8C0040' : '#0078D440'}`
                    }}
                  />
                </div>
              </div>
            </div>
            
            {/* GPU Utilization */}
            <div className="flex items-start space-x-2">
              <span className="text-[9px] text-gray-400" style={{ width: '85px' }}>Utilization: {gpu.utilization.toFixed(0)}%</span>
              <div className="relative" style={{ width: '80px', height: '6px', marginTop: '4px' }}>
                <div className="absolute inset-0 bg-gray-800 rounded-full overflow-hidden">
                  <div 
                    className="h-full transition-all duration-300 ease-out rounded-full"
                    style={{ 
                      width: `${gpu.utilization}%`,
                      backgroundColor: gpu.brand === 'NVIDIA' ? '#76B900' : gpu.brand === 'AMD' ? '#FF8C00' : '#0078D4',
                      boxShadow: `0 0 10px ${gpu.brand === 'NVIDIA' ? '#76B90040' : gpu.brand === 'AMD' ? '#FF8C0040' : '#0078D440'}`
                    }}
                  />
                </div>
              </div>
            </div>
          </div>
        ))
      )}

      {/* Divider */}
      <div className="h-8 w-px bg-gray-700"></div>

      {/* CPU Section */}
      {systemResources && (
        <div className="flex flex-col">
          <div className="flex items-center space-x-1 mb-1">
            <span 
              className="text-[10px] font-medium" 
              style={{ color: getCpuColor() }}
            >
              {systemResources.cpu.brand}
            </span>
            <span className="text-[9px] text-gray-400">
              {truncateCpuModel(systemResources.cpu.model)}
            </span>
          </div>
          <div style={{ display: 'flex', alignItems: 'flex-start' }}>
            <span className="text-[9px] text-gray-400" style={{ width: '50px' }}>Usage: {systemResources.cpu.usage.toFixed(0)}%</span>
            <div className="relative" style={{ width: '71px', height: '6px', marginTop: '4px', marginLeft: '1px' }}>
              <div className="absolute inset-0 bg-gray-800 rounded-full overflow-hidden">
                <div 
                  className="h-full transition-all duration-300 ease-out rounded-full"
                  style={{ 
                    width: `${systemResources.cpu.usage}%`,
                    backgroundColor: getCpuColor(),
                    boxShadow: `0 0 10px ${getCpuColor()}40`
                  }}
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* RAM Section */}
      {systemResources && (
        <div className="flex flex-col">
          <div className="flex items-center space-x-1 mb-1">
            <span className="text-[10px] font-medium text-purple-500">RAM</span>
            <span className="text-[9px] text-gray-400">{Math.ceil(systemResources.ram.total_gb)}GB</span>
            {systemResources.ram.speed && (
              <span className="text-[9px] text-gray-400">{systemResources.ram.speed}</span>
            )}
          </div>
          <div style={{ display: 'flex', alignItems: 'flex-start' }}>
            <span className="text-[9px] text-gray-400" style={{ width: '50px' }}>Used: {Math.ceil(systemResources.ram.used_gb)}GB</span>
            <div className="relative" style={{ width: '45px', height: '6px', marginTop: '4px', marginLeft: '1px' }}>
              <div className="absolute inset-0 bg-gray-800 rounded-full overflow-hidden">
                <div 
                  className="h-full transition-all duration-300 ease-out rounded-full"
                  style={{ 
                    width: `${Math.min((systemResources.ram.used_gb / systemResources.ram.total_gb) * 100, 100)}%`,
                    backgroundColor: '#9B59B6',
                    boxShadow: '0 0 10px #9B59B640'
                  }}
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Storage Section */}
      {systemResources && (
        <div className="flex flex-col">
          <div className="flex items-center space-x-1 mb-1">
            <span className="text-[10px] font-medium text-white">Storage</span>
            {systemResources.disk.type && (
              <span className="text-[9px] text-gray-400">{systemResources.disk.type} {Math.floor(systemResources.disk.total_gb)}GB</span>
            )}
          </div>
          <div style={{ display: 'flex', alignItems: 'flex-start' }}>
            <span className="text-[9px] text-gray-400" style={{ width: '50px' }}>Used: {Math.floor(systemResources.disk.used_gb)}GB</span>
            <div className="relative" style={{ width: '35px', height: '6px', marginTop: '4px', marginLeft: '1px' }}>
              <div className="absolute inset-0 bg-gray-800 rounded-full overflow-hidden">
                <div 
                  className="h-full transition-all duration-300 ease-out rounded-full"
                  style={{ 
                    width: `${Math.min((systemResources.disk.used_gb / systemResources.disk.total_gb) * 100, 100)}%`,
                    backgroundColor: '#FFFFFF',
                    boxShadow: '0 0 10px #FFFFFF40'
                  }}
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Token Speed only - removed active requests */}
      {activeModel && activeModel.tokens_per_second > 0 && (
        <div className="flex items-center space-x-1 ml-2">
          <span className="text-[9px] text-gray-400">Speed:</span>
          <span className="text-[9px] text-green-400">
            {activeModel.tokens_per_second.toFixed(1)} tok/s
          </span>
        </div>
      )}
    </div>
  );
};