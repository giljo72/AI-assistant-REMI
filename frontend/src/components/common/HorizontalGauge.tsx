// File: frontend/src/components/common/HorizontalGauge.tsx
import React from 'react';

interface HorizontalGaugeProps {
  label: string;
  value: number;
  maxValue: number;
  unit: string;
  color: string;
  showValueInBar?: boolean;
  width?: number;
}

export const HorizontalGauge: React.FC<HorizontalGaugeProps> = ({
  label,
  value,
  maxValue,
  unit,
  color,
  showValueInBar = true,
  width = 200,
}) => {
  const percentage = Math.min((value / maxValue) * 100, 100);
  // For VRAM (GPU), show decimals. For others, round.
  const displayValue = unit === '%' ? value.toFixed(0) : 
                      (label === '' && color === '#76B900') ? value.toFixed(1) : 
                      Math.round(value).toString();
  
  return (
    <div className="flex flex-col space-y-1">
      {label && <div className="text-[10px] text-gray-400">{label}</div>}
      <div className="relative" style={{ width: `${width}px` }}>
        {/* Background bar */}
        <div className="absolute inset-0 h-5 bg-gray-800 rounded-full overflow-hidden">
          {/* Progress fill */}
          <div 
            className="h-full transition-all duration-300 ease-out rounded-full"
            style={{ 
              width: `${percentage}%`,
              backgroundColor: color,
              boxShadow: `0 0 10px ${color}40`
            }}
          />
        </div>
        
        {/* Value text overlay */}
        <div className="relative h-5 flex items-center justify-between px-2">
          {showValueInBar && (
            <span className="text-[11px] font-bold text-white z-10 drop-shadow-md">
              {displayValue}{unit}
            </span>
          )}
          <span className="text-[11px] text-gray-300 ml-auto">
            {unit === 'GB' || unit === 'TB' ? `${Math.round(maxValue)}${unit}` : ''}
          </span>
        </div>
      </div>
    </div>
  );
};