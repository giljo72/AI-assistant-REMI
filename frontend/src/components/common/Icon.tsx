import React from 'react';
import Tooltip from '@mui/material/Tooltip';

// Icon mapping to public SVG files
const icons = {
  add: '/icons/add.svg',
  chart: '/icons/chart.svg',
  close: '/icons/close.svg',
  code: '/icons/code.svg',
  copy: '/icons/copy.svg',
  delete: '/icons/delete.svg',  // Map delete to delete.svg
  document: '/icons/document.svg',
  trash: '/icons/trash.svg',
  download: '/icons/download.svg',
  dropdownClose: '/icons/dropdown_close.svg',
  dropdownOpen: '/icons/dropdown_open.svg',
  file: '/icons/file.svg',
  image: '/icons/image.svg',
  link: '/icons/link.svg',
  microphone: '/icons/microphone.svg',
  question: '/icons/question.svg',
  refresh: '/icons/refresh.svg',
  save: '/icons/save.svg',
  search: '/icons/search.svg',
  settings: '/icons/settings.svg',
  table: '/icons/table.svg',
  unlink: '/icons/unlink.svg',
  user: '/icons/user.svg',
  userAdd: '/icons/useradd.svg',
  userDelete: '/icons/userdelete.svg',
  userEdit: '/icons/useredit.svg',
  view: '/icons/view.svg',
};

export type IconName = keyof typeof icons;

interface IconProps {
  name: IconName;
  size?: number;
  className?: string;
  tooltip?: string;
  onClick?: () => void;
  style?: React.CSSProperties;
}

export const Icon: React.FC<IconProps> = ({ 
  name, 
  size = 20, 
  className = '', 
  tooltip,
  onClick,
  style = {}
}) => {
  const iconPath = icons[name];
  
  if (!iconPath) {
    console.warn(`Icon "${name}" not found`);
    return null;
  }

  const iconElement = (
    <img 
      src={iconPath} 
      alt={name}
      width={size}
      height={size}
      className={`icon icon-hover ${className}`}
      onClick={onClick}
      style={{
        cursor: onClick ? 'pointer' : 'default',
        transition: 'all 0.2s ease',
        filter: 'brightness(1)',
        ...style
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.opacity = '0.8';
        e.currentTarget.style.transform = 'scale(1.1)';
        e.currentTarget.style.filter = 'brightness(1.2)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.opacity = '1';
        e.currentTarget.style.transform = 'scale(1)';
        e.currentTarget.style.filter = 'brightness(1)';
      }}
    />
  );

  if (tooltip) {
    return (
      <Tooltip title={tooltip} arrow placement="top">
        {iconElement}
      </Tooltip>
    );
  }

  return iconElement;
};

// Help Icon with built-in tooltip
interface HelpIconProps {
  tooltip: string;
  size?: number;
  className?: string;
}

export const HelpIcon: React.FC<HelpIconProps> = ({ tooltip, size = 16, className = '' }) => {
  return (
    <Icon 
      name="question" 
      size={size} 
      tooltip={tooltip}
      className={`help-icon ${className}`}
      style={{ 
        marginLeft: '8px',
        verticalAlign: 'middle',
        opacity: 0.6,
        cursor: 'help'
      }}
    />
  );
};