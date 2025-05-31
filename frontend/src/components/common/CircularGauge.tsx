// File: frontend/src/components/common/CircularGauge.tsx
import React from 'react';

interface CircularGaugeProps {
  value: number; // 0-100
  maxValue: number;
  label: string;
  color: string; // Primary color for the gauge
  backgroundColor?: string;
  size?: number;
  strokeWidth?: number;
}

export const CircularGauge: React.FC<CircularGaugeProps> = ({
  value,
  maxValue,
  label,
  color,
  backgroundColor = '#2a2a2a',
  size = 60,
  strokeWidth = 6,
}) => {
  const percentage = Math.min((value / maxValue) * 100, 100);
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (percentage / 100) * circumference;

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg 
        width={size} 
        height={size} 
        className="transform -rotate-90"
      >
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={backgroundColor}
          strokeWidth={strokeWidth}
        />
        {/* Progress circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className="transition-all duration-500 ease-out"
        />
      </svg>
      {/* Center text */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-xs font-bold text-white">
          {value.toFixed(0)}
        </span>
        <span className="text-[8px] text-gray-400">
          {label}
        </span>
      </div>
    </div>
  );
};