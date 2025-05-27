import React, { useState, useEffect } from 'react';
import { fileService, projectService } from '../../services';
import { File, FileFilterOptions, FileSortOptions, ProcessingStats, FileSearchResult } from '../../services/fileService';
import { useNavigation } from '../../hooks/useNavigation';
import { ProjectId, normalizeProjectId, isFileLinkedToProject } from '../../types/common';
import TagAndAddFileModal from '../modals/TagAndAddFileModal';
import { Icon, HelpIcon } from '../common/Icon';

// Local interface for mapped files from API response
interface LocalFile {
  id: string;
  name: string;
  type: string;
  size: string;
  active: boolean;
  projectId: ProjectId; // Using our ProjectId type for consistency
  projectName?: string; // Name of the project this file is linked to
  addedAt: string;
  processed: boolean; // Indicates if the file has been processed into vector DB
  processingFailed?: boolean; // If processing failed
  chunks?: number; // Number of chunks if processed
  description?: string;
  relevance?: number; // For search results
}

// Define types for projects
interface Project {
  id: string;
  name: string;
}

// File type metadata for improved visualization
interface FileTypeMetadata {
  color: string;
  icon: string;
  description: string;
}

// Get file type metadata for display
const getFileTypeMetadata = (type: string): FileTypeMetadata => {
  const fileType = type.toLowerCase();
  
  switch (fileType) {
    case 'pdf':
      return {
        color: 'red',
        icon: 'document',
        description: 'Adobe PDF Document'
      };
    case 'docx':
    case 'doc':
      return {
        color: 'blue',
        icon: 'document',
        description: 'Microsoft Word Document'
      };
    case 'xlsx':
    case 'xls':
      return {
        color: 'green',
        icon: 'table',
        description: 'Microsoft Excel Spreadsheet'
      };
    case 'pptx':
    case 'ppt':
      return {
        color: 'orange',
        icon: 'chart',
        description: 'Microsoft PowerPoint Presentation'
      };
    case 'png':
    case 'jpg':
    case 'jpeg':
    case 'gif':
    case 'bmp':
    case 'svg':
    case 'webp':
      return {
        color: 'purple',
        icon: 'image',
        description: 'Image File'
      };
    case 'txt':
      return {
        color: 'gray',
        icon: 'document',
        description: 'Text Document'
      };
    case 'md':
    case 'markdown':
      return {
        color: 'gray',
        icon: 'document',
        description: 'Markdown Document'
      };
    case 'json':
    case 'xml':
    case 'yaml':
    case 'yml':
      return {
        color: 'yellow',
        icon: 'code',
        description: 'Data/Configuration File'
      };
    case 'csv':
      return {
        color: 'green',
        icon: 'table',
        description: 'Comma-Separated Values'
      };
    case 'zip':
    case 'rar':
    case '7z':
    case 'tar':
    case 'gz':
      return {
        color: 'amber',
        icon: 'download',
        description: 'Compressed Archive'
      };
    case 'html':
    case 'htm':
    case 'css':
    case 'js':
    case 'jsx':
    case 'ts':
    case 'tsx':
    case 'py':
    case 'java':
    case 'cpp':
    case 'c':
    case 'cs':
    case 'php':
    case 'rb':
    case 'go':
    case 'rs':
    case 'swift':
    case 'kt':
      return {
        color: 'orange',
        icon: 'code',
        description: 'Source Code'
      };
    default:
      return {
        color: 'gray',
        icon: 'document',
        description: 'Document'
      };
  }
};

// Helper function to get badge styles based on file type
const getFileBadgeStyles = (type: string): { bgClass: string, textClass: string, iconFilter: string } => {
  const color = getFileTypeMetadata(type).color;
  
  switch (color) {
    case 'blue':
      return { 
        bgClass: 'bg-blue-500/20', 
        textClass: 'text-blue-400',
        // CSS filter to make the icon blue-400
        iconFilter: 'brightness(0) saturate(100%) invert(63%) sepia(35%) saturate(1726%) hue-rotate(178deg) brightness(101%) contrast(96%)'
      };
    case 'green':
      return { 
        bgClass: 'bg-green-500/20', 
        textClass: 'text-green-400',
        // CSS filter to make the icon green-400
        iconFilter: 'brightness(0) saturate(100%) invert(78%) sepia(51%) saturate(1823%) hue-rotate(84deg) brightness(97%) contrast(86%)'
      };
    case 'red':
      return { 
        bgClass: 'bg-red-500/20', 
        textClass: 'text-red-400',
        // CSS filter to make the icon red-400
        iconFilter: 'brightness(0) saturate(100%) invert(67%) sepia(44%) saturate(4893%) hue-rotate(329deg) brightness(98%) contrast(95%)'
      };
    case 'orange':
      return { 
        bgClass: 'bg-orange-500/20', 
        textClass: 'text-orange-400',
        // CSS filter to make the icon orange-400
        iconFilter: 'brightness(0) saturate(100%) invert(67%) sepia(60%) saturate(1076%) hue-rotate(1deg) brightness(101%) contrast(98%)'
      };
    case 'purple':
      return { 
        bgClass: 'bg-purple-500/20', 
        textClass: 'text-purple-400',
        // CSS filter to make the icon purple-400
        iconFilter: 'brightness(0) saturate(100%) invert(64%) sepia(52%) saturate(615%) hue-rotate(223deg) brightness(100%) contrast(97%)'
      };
    case 'gray':
      return { 
        bgClass: 'bg-gray-500/20', 
        textClass: 'text-white',
        // CSS filter to make the icon white
        iconFilter: 'brightness(0) saturate(100%) invert(100%) sepia(0%) saturate(0%) hue-rotate(0deg) brightness(100%) contrast(100%)'
      };
    case 'yellow':
      return { 
        bgClass: 'bg-yellow-500/20', 
        textClass: 'text-yellow-400',
        // CSS filter to make the icon yellow-400
        iconFilter: 'brightness(0) saturate(100%) invert(86%) sepia(66%) saturate(507%) hue-rotate(358deg) brightness(101%) contrast(98%)'
      };
    case 'amber':
      return { 
        bgClass: 'bg-amber-500/20', 
        textClass: 'text-amber-400',
        // CSS filter to make the icon amber-400
        iconFilter: 'brightness(0) saturate(100%) invert(75%) sepia(76%) saturate(480%) hue-rotate(358deg) brightness(101%) contrast(98%)'
      };
    case 'pink':
      return { 
        bgClass: 'bg-pink-500/20', 
        textClass: 'text-pink-400',
        // CSS filter to make the icon pink-400
        iconFilter: 'brightness(0) saturate(100%) invert(70%) sepia(52%) saturate(1620%) hue-rotate(295deg) brightness(101%) contrast(92%)'
      };
    case 'teal':
      return { 
        bgClass: 'bg-teal-500/20', 
        textClass: 'text-teal-400',
        // CSS filter to make the icon teal-400
        iconFilter: 'brightness(0) saturate(100%) invert(75%) sepia(36%) saturate(1837%) hue-rotate(128deg) brightness(92%) contrast(93%)'
      };
    case 'cyan':
      return { 
        bgClass: 'bg-cyan-500/20', 
        textClass: 'text-cyan-400',
        // CSS filter to make the icon cyan-400
        iconFilter: 'brightness(0) saturate(100%) invert(80%) sepia(57%) saturate(2122%) hue-rotate(157deg) brightness(97%) contrast(91%)'
      };
    default:
      return { 
        bgClass: 'bg-gray-500/20', 
        textClass: 'text-gray-400',
        // CSS filter to make the icon gray-400
        iconFilter: 'brightness(0) saturate(100%) invert(65%) sepia(8%) saturate(192%) hue-rotate(172deg) brightness(95%) contrast(87%)'
      };
  }
};

// Helper to format bytes to human-readable size
const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return bytes + ' B';
  const units = ['KB', 'MB', 'GB', 'TB'];
  let size = bytes / 1024;
  let unitIndex = 0;
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }
  
  return size.toFixed(1) + ' ' + units[unitIndex];
};

// Map API File to LocalFile format
const mapApiFileToLocal = (apiFile: File): LocalFile => {
  // Log the raw project_id value for debugging
  console.log(`[MAPPER] Mapping file ${apiFile.id} (${apiFile.name}), project_id: ${apiFile.project_id}, project_name: ${(apiFile as any).project_name}, type: ${typeof apiFile.project_id}`);
  
  // Use our normalization function for consistent types
  const normalizedProjectId = normalizeProjectId(apiFile.project_id);
  
  console.log(`[MAPPER] Normalized project_id for ${apiFile.id}: ${normalizedProjectId} (${typeof normalizedProjectId})`);
  
  return {
    id: apiFile.id,
    name: apiFile.name,
    type: apiFile.type.toUpperCase(),
    size: formatFileSize(apiFile.size),
    active: apiFile.active,
    projectId: normalizedProjectId, // Using our normalized project ID
    projectName: (apiFile as any).project_name, // Include project name from backend
    addedAt: apiFile.created_at.split('T')[0], // Format date
    processed: apiFile.processed,
    processingFailed: apiFile.processing_failed,
    chunks: apiFile.chunk_count,
    description: apiFile.description,
    // Add relevance if this is a search result
    relevance: (apiFile as any).relevance
  };
};

type MainFileManagerProps = {
  // No props needed since we use the navigation system
};

const MainFileManager: React.FC<MainFileManagerProps> = () => {
  // Use our navigation hook
  const navigation = useNavigation();
  
  // Helper function to handle return to previous view
  const handleReturn = () => {
    if (navigation.activeProjectId) {
      navigation.navigateToView('projectFiles');
    } else {
      navigation.navigateToView('project');
    }
  };
  
  // Helper function to navigate to a project
  const handleSelectProject = (projectId: string) => {
    navigation.navigateToProject(projectId);
  };
  
  // Determine the current project ID
  const projectId = navigation.activeProjectId;
  // Files state
  const [files, setFiles] = useState<LocalFile[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Project state
  const [projects, setProjects] = useState<Project[]>([]);
  
  // UI state
  const [searchTerm, setSearchTerm] = useState('');
  const [sortField, setSortField] = useState<'name' | 'date' | 'size' | 'status' | 'processed'>('date');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');
  const [showAddTagModal, setShowAddTagModal] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);
  const [searchResults, setSearchResults] = useState<LocalFile[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [droppedFiles, setDroppedFiles] = useState<File[]>([]);
  const [selectAllChecked, setSelectAllChecked] = useState(false);
  
  // Processing state
  const [processingStats, setProcessingStats] = useState<ProcessingStats | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  
  // Details panel state
  const [selectedFileDetails, setSelectedFileDetails] = useState<LocalFile | null>(null);
  const [showDetailsPanel, setShowDetailsPanel] = useState(false);

  // Function to fetch files based on current filters
  const fetchFiles = async () => {
    setIsLoading(true);
    setError(null);
    
    // Set up API filters
    const filterOptions: FileFilterOptions = {};
    // Only filter by project if we're in a specific project view
    // In the main file manager, we want to see ALL files (linked and unlinked)
    // So we explicitly do NOT set project_id filter for the main view
    if (projectId !== undefined && projectId !== null) {
      filterOptions.project_id = projectId;
    }
    
    // Set up API sort
    const sortOptions: FileSortOptions = {
      field: sortField === 'date' ? 'created_at' : 
             sortField === 'status' ? 'project_id' : sortField,
      direction: sortDirection
    };
    
    try {
      console.log("[MAINFILEMANAGER] Fetching files with options:", { filterOptions, sortOptions });
      
      // Force reload window.mockFiles from localStorage to ensure we have the latest data
      try {
        const storedFiles = localStorage.getItem('mockFiles');
        if (storedFiles) {
          window.mockFiles = JSON.parse(storedFiles);
          console.log("[MAINFILEMANAGER] Refreshed mockFiles from localStorage:", window.mockFiles.length);
          
          // Debug file-project associations
          console.log("[MAINFILEMANAGER] Current file-project associations in localStorage:");
          JSON.parse(storedFiles).forEach((file: any) => {
            console.log(`- ${file.id} (${file.name}): project_id = ${file.project_id || 'none'}`);
          });
        }
      } catch (e) {
        console.error('[MAINFILEMANAGER] Error refreshing mockFiles from localStorage', e);
      }
      
      // Fetch files
      const apiFiles = await fileService.getAllFiles(filterOptions, sortOptions);
      console.log("[MAINFILEMANAGER] Received", apiFiles.length, "files from API/mock");
      
      const localFiles = apiFiles.map(mapApiFileToLocal);
      console.log("[MAINFILEMANAGER] Mapped files:", localFiles.length);
      
      setFiles(localFiles);
      
      // Debug output for global mock files
      console.log("[MAINFILEMANAGER] Current global mock files:", window.mockFiles?.length || 0, "files");
      
      return true;
    } catch (err) {
      console.error('[MAINFILEMANAGER] Error fetching files:', err);
      setError('Failed to load files. Please try again.');
      return false;
    } finally {
      setIsLoading(false);
    }
  };
  
  // Function to refresh additional data (projects, processing stats)
  const fetchAdditionalData = async () => {
    try {
      // Fetch projects for linking info
      const projectsData = await projectService.getAllProjects();
      setProjects(projectsData);
      console.log("[MAINFILEMANAGER] Loaded projects:", projectsData);
      
      // Log projects for debugging
      if (projectsData.length > 0) {
        console.log("[MAINFILEMANAGER] Available projects for linking:");
        projectsData.forEach(project => {
          console.log(`- Project: ${project.id} - ${project.name}`);
        });
      } else {
        console.warn("[MAINFILEMANAGER] No projects available for linking files");
      }
      
      // Try to fetch processing stats once (may not be available)
      try {
        const stats = await fileService.getProcessingStatus();
        setProcessingStats(stats);
      } catch (err) {
        console.log('[MAINFILEMANAGER] Processing status endpoint not available - skipping');
      }
    } catch (err) {
      console.error('[MAINFILEMANAGER] Error fetching additional data:', err);
    }
  };
  
  // Function to handle after a file is uploaded
  const handleUploadSuccess = async () => {
    console.log("[MAINFILEMANAGER] Manually refreshing files after upload");
    await fetchFiles();
  };
  
  // Effect to load all files and projects on component mount and when filters change
  useEffect(() => {
    // Load initial data
    const loadInitialData = async () => {
      console.log("[MAINFILEMANAGER] Initial data load triggered with projectId:", projectId);
      await fetchFiles();
      await fetchAdditionalData();
    };
    
    loadInitialData();
    
    // Define event handlers for our custom events
    const handleFileAdded = async (event: Event) => {
      console.log("[MAINFILEMANAGER] File added event detected, refreshing file list");
      
      // Get details from the event if available
      const customEvent = event as CustomEvent;
      if (customEvent.detail) {
        console.log("[MAINFILEMANAGER] Event details:", customEvent.detail);
      }
      
      // Force reload from localStorage to ensure we have the latest data
      try {
        const storedFiles = localStorage.getItem('mockFiles');
        if (storedFiles) {
          window.mockFiles = JSON.parse(storedFiles);
          console.log("[MAINFILEMANAGER] Successfully reloaded mockFiles from localStorage:", window.mockFiles.length);
        }
      } catch (e) {
        console.error('[MAINFILEMANAGER] Error refreshing mockFiles from localStorage', e);
      }
      
      // Refresh files list
      await fetchFiles();
    };
    
    const handleFileDeleted = async (event: Event) => {
      console.log("[MAINFILEMANAGER] File deleted event detected, refreshing file list");
      
      // Get details from the event if available
      const customEvent = event as CustomEvent;
      if (customEvent.detail) {
        console.log("[MAINFILEMANAGER] Delete event details:", customEvent.detail);
      }
      
      await fetchFiles();
    };
    
    // Handler to close project dropdowns when clicking outside
    const handleClickOutside = (event: MouseEvent) => {
      // Close individual file project dropdowns
      const fileDropdowns = document.querySelectorAll('[id^="project-dropdown-"]');
      fileDropdowns.forEach(dropdown => {
        if (!dropdown.contains(event.target as Node) && 
            !(event.target as Element).classList.contains('project-dropdown-toggle')) {
          (dropdown as HTMLElement).classList.add('hidden');
        }
      });
      
      // Close batch project dropdown
      const batchDropdown = document.getElementById('batch-project-dropdown');
      if (batchDropdown && 
          !batchDropdown.contains(event.target as Node) && 
          !(event.target as Element).classList.contains('project-dropdown-toggle')) {
        batchDropdown.classList.add('hidden');
      }
    };
    
    // Add event listeners for our custom events
    window.addEventListener('mockFileAdded', handleFileAdded);
    window.addEventListener('mockFileDeleted', handleFileDeleted);
    document.body.addEventListener('click', handleClickOutside);
    
    // Force reload files when the component is mounted or projectId changes
    const forceReload = () => {
      console.log("[MAINFILEMANAGER] Force reloading files and projects on mount or projectId change");
      // Clear any cached data
      setFiles([]);
      setProjects([]);
      // Reload everything from scratch
      fetchFiles();
      fetchAdditionalData();
    };
    
    // Call the force reload function
    forceReload();
    
    // Clean up event listeners when component unmounts
    return () => {
      window.removeEventListener('mockFileAdded', handleFileAdded);
      window.removeEventListener('mockFileDeleted', handleFileDeleted);
      document.body.removeEventListener('click', handleClickOutside);
    };
  }, [projectId, sortField, sortDirection]); // Dependencies trigger re-fetch when they change

  // Handle search
  const handleSearch = async () => {
    if (!searchTerm.trim()) {
      setIsSearching(false);
      setSearchResults([]);
      return;
    }
    
    console.log("[MAINFILEMANAGER] Starting search for:", searchTerm);
    setIsSearching(true);
    setIsLoading(true);
    
    try {
      // Build search request
      const searchRequest = {
        query: searchTerm,
        project_id: projectId,
        include_content: true
      };
      
      // Call API for search
      console.log("[MAINFILEMANAGER] Sending search request:", searchRequest);
      const results = await fileService.searchFileContents(searchRequest);
      console.log("[MAINFILEMANAGER] Received search results:", results);
      
      // Always ensure we have results - if no results came back, show all files
      if (!results || results.length === 0) {
        console.log("[MAINFILEMANAGER] No search results found, showing all files");
        // As a fallback, show all current files sorted by relevance
        const fallbackResults = files.map(file => ({
          ...file,
          // Calculate a relevance score based on similarity
          relevance: 50 - (levenshteinDistance(file.name.toLowerCase(), searchTerm.toLowerCase()) / 
                         Math.max(file.name.length, searchTerm.length)) * 50,
          content_snippets: [`No exact matches found - showing all files`]
        }));
        
        setSearchResults(fallbackResults);
      } else {
        // Map API results to local format
        const mappedResults = results.map(mapApiFileToLocal);
        console.log("[MAINFILEMANAGER] Mapped search results:", mappedResults);
        setSearchResults(mappedResults);
      }
    } catch (err) {
      console.error('[MAINFILEMANAGER] Error searching files:', err);
      setError('Search failed. Showing all files as fallback.');
      
      // Show all files as fallback
      const fallbackResults = files.map(file => ({
        ...file,
        relevance: 30 // Low relevance for fallback results
      }));
      
      setSearchResults(fallbackResults);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Helper function to calculate string similarity
  const levenshteinDistance = (str1: string, str2: string): number => {
    const track = Array(str2.length + 1).fill(null).map(() => 
      Array(str1.length + 1).fill(null));
    
    for (let i = 0; i <= str1.length; i += 1) {
      track[0][i] = i;
    }
    
    for (let j = 0; j <= str2.length; j += 1) {
      track[j][0] = j;
    }
    
    for (let j = 1; j <= str2.length; j += 1) {
      for (let i = 1; i <= str1.length; i += 1) {
        const indicator = str1[i - 1] === str2[j - 1] ? 0 : 1;
        track[j][i] = Math.min(
          track[j][i - 1] + 1, // deletion
          track[j - 1][i] + 1, // insertion
          track[j - 1][i - 1] + indicator, // substitution
        );
      }
    }
    
    return track[str2.length][str1.length];
  };

  // Handle file selection for bulk operations
  const toggleFileSelection = (fileId: string) => {
    setSelectedFiles(prev => {
      const newSelection = prev.includes(fileId) 
        ? prev.filter(id => id !== fileId) 
        : [...prev, fileId];
      
      // Update select all checkbox state based on selection
      setSelectAllChecked(newSelection.length === getSortedFiles().length);
      
      return newSelection;
    });
  };
  
  // Toggle all files selection
  const toggleSelectAll = () => {
    if (selectAllChecked) {
      // Deselect all files
      setSelectedFiles([]);
      setSelectAllChecked(false);
    } else {
      // Select all files
      const allFileIds = getSortedFiles().map(file => file.id);
      setSelectedFiles(allFileIds);
      setSelectAllChecked(true);
    }
  };
  
  // Clear selection
  const clearSelection = () => {
    setSelectedFiles([]);
    setSelectAllChecked(false);
  };

  // Handle attaching selected files to current project
  const handleAttachToProject = async () => {
    if (!projectId || selectedFiles.length === 0) return;
    
    try {
      // Call API to link files
      await fileService.linkFilesToProject({
        file_ids: selectedFiles,
        project_id: projectId
      });
      
      // Update local state
      setFiles(prev => 
        prev.map(file => 
          selectedFiles.includes(file.id) 
            ? { ...file, projectId } 
            : file
        )
      );
      
      // Clear selection
      setSelectedFiles([]);
    } catch (err) {
      console.error('Error attaching files to project:', err);
      setError('Failed to attach files to project. Please try again.');
    }
  };

  // Handle retry processing for failed files
  const handleRetryProcessing = async (fileId: string) => {
    try {
      // Update local state to show processing starting
      setFiles(prev => 
        prev.map(file => 
          file.id === fileId 
            ? { ...file, processed: false, processingFailed: false } 
            : file
        )
      );
      
      // Call API to retry processing
      const updatedFile = await fileService.retryProcessing(fileId);
      
      // Update file in local state
      setFiles(prev => 
        prev.map(file => 
          file.id === fileId 
            ? mapApiFileToLocal(updatedFile)
            : file
        )
      );
      
      // Set up a delayed status check since processing happens in the background
      const checkStatus = async () => {
        try {
          const file = await fileService.getFile(fileId);
          setFiles(prev => 
            prev.map(f => 
              f.id === fileId 
                ? mapApiFileToLocal(file)
                : f
            )
          );
          
          // If still processing, check again after a delay
          if (!file.processed && !file.processing_failed) {
            setTimeout(checkStatus, 3000); // Check again in 3 seconds
          }
        } catch (err) {
          console.error('Error checking file status:', err);
        }
      };
      
      // Start checking after 2 seconds
      setTimeout(checkStatus, 2000);
    } catch (err) {
      console.error('Error retrying file processing:', err);
      setError('Failed to retry processing. Please try again.');
      
      // Reset file to failed state
      setFiles(prev => 
        prev.map(file => 
          file.id === fileId 
            ? { ...file, processed: false, processingFailed: true } 
            : file
        )
      );
    }
  };

  // Handle file deletion
  const handleDeleteFile = async (fileId: string) => {
    try {
      // Call API to delete file
      await fileService.deleteFile(fileId);
      
      // Update local state
      setFiles(prev => prev.filter(file => file.id !== fileId));
      setSelectedFiles(prev => prev.filter(id => id !== fileId));
    } catch (err) {
      console.error('Error deleting file:', err);
      setError('Failed to delete file. Please try again.');
    }
  };

  // Sort files based on current sort field and direction
  const getSortedFiles = () => {
    let filesToSort = isSearching ? searchResults : files;
    
    return [...filesToSort].sort((a, b) => {
      if (sortField === 'name') {
        return sortDirection === 'asc' 
          ? a.name.localeCompare(b.name) 
          : b.name.localeCompare(a.name);
      } else if (sortField === 'date') {
        return sortDirection === 'asc' 
          ? a.addedAt.localeCompare(b.addedAt) 
          : b.addedAt.localeCompare(a.addedAt);
      } else if (sortField === 'size') {
        // Parse sizes correctly for numerical comparison
        const parseSizeToBytes = (sizeStr: string): number => {
          const match = sizeStr.match(/^([\d.]+)\s*([KMGT]?B)$/i);
          if (!match) return 0;
          
          const value = parseFloat(match[1]);
          const unit = match[2].toUpperCase();
          
          switch (unit) {
            case 'B': return value;
            case 'KB': return value * 1024;
            case 'MB': return value * 1024 * 1024;
            case 'GB': return value * 1024 * 1024 * 1024;
            case 'TB': return value * 1024 * 1024 * 1024 * 1024;
            default: return value;
          }
        };
        
        const aBytes = parseSizeToBytes(a.size);
        const bBytes = parseSizeToBytes(b.size);
        
        return sortDirection === 'asc' 
          ? aBytes - bBytes 
          : bBytes - aBytes;
      } else if (sortField === 'status') {
        // Sort by projectId (linked status)
        if (sortDirection === 'asc') {
          return (a.projectId === null) === (b.projectId === null) 
            ? 0 
            : a.projectId === null ? 1 : -1;
        } else {
          return (a.projectId === null) === (b.projectId === null) 
            ? 0 
            : a.projectId === null ? -1 : 1;
        }
      } else if (sortField === 'processed') {
        // Sort by processed status
        if (sortDirection === 'asc') {
          return a.processed === b.processed ? 0 : a.processed ? 1 : -1;
        } else {
          return a.processed === b.processed ? 0 : a.processed ? -1 : 1;
        }
      }
      return 0;
    });
  };

  // Show file details panel
  const showFileDetails = (file: LocalFile) => {
    setSelectedFileDetails(file);
    setShowDetailsPanel(true);
  };
  
  // Close file details panel
  const closeDetailsPanel = () => {
    setShowDetailsPanel(false);
    // Clear the selected file after a brief delay for smooth animation
    setTimeout(() => setSelectedFileDetails(null), 300);
  };
  
  // Handle sort field change
  const handleSortChange = (field: 'name' | 'date' | 'size' | 'status' | 'processed') => {
    // Update sort state
    let newDirection: 'asc' | 'desc';
    
    if (field === sortField) {
      newDirection = sortDirection === 'asc' ? 'desc' : 'asc';
      setSortDirection(newDirection);
    } else {
      setSortField(field);
      newDirection = 'asc';
      setSortDirection(newDirection);
    }
    
    // Log the change
    console.log(`[MAINFILEMANAGER] Sort changed to ${field} ${newDirection}`);
    
    // Refresh data with new sort
    if (!isSearching) {
      // Only trigger an API refetch if we're not in search mode
      // For searches, we'll just resort the client-side data
      fetchFiles();
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="bg-navy-light p-4 mb-4 rounded-lg flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-gold">Main File Manager</h2>
          <p className="text-gray-400 text-sm">Manage all system files</p>
          <div className="mt-2 flex items-center space-x-3">
            <span className="px-2 py-0.5 bg-navy rounded text-sm">
              <span className="text-gold font-medium">{files.length}</span>
              <span className="text-gray-400 ml-1">files total</span>
            </span>
            <span className="px-2 py-0.5 bg-navy rounded text-sm">
              <span className="text-green-400 font-medium">{files.filter(f => f.processed).length}</span>
              <span className="text-gray-400 ml-1">processed</span>
            </span>
            <span className="px-2 py-0.5 bg-navy rounded text-sm">
              <span className="text-blue-400 font-medium">{files.filter(f => isFileLinkedToProject(f.projectId)).length}</span>
              <span className="text-gray-400 ml-1">linked to projects</span>
            </span>
          </div>
        </div>
        <div className="flex space-x-2">
          <button 
            onClick={handleReturn}
            className="px-3 py-1 bg-navy hover:bg-navy-lighter rounded text-sm"
          >
            Return
          </button>
        </div>
      </div>
      
      {/* File Upload Area */}
      <div className="bg-navy-light p-4 mb-4 rounded-lg">
        <div 
          className="border-2 border-dashed border-navy-lighter rounded-lg p-6 text-center"
          onDragOver={(e) => {
            e.preventDefault();
            e.stopPropagation();
            e.currentTarget.classList.add('border-gold');
          }}
          onDragLeave={(e) => {
            e.preventDefault();
            e.stopPropagation();
            e.currentTarget.classList.remove('border-gold');
          }}
          onDrop={(e) => {
            e.preventDefault();
            e.stopPropagation();
            e.currentTarget.classList.remove('border-gold');
            
            // Get dropped files
            if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
              // Handle file upload with the files
              const filesToUpload = Array.from(e.dataTransfer.files);
              console.log('Files dropped:', filesToUpload);
              
              // Store files in state
              setDroppedFiles(filesToUpload);
              
              // Open tagging modal with the dropped files
              setShowAddTagModal(true);
            }
          }}
        >
          <div className="mb-4 flex justify-center">
            <Icon name="add" size={32} className="text-gold" />
          </div>
          <p className="text-gray-400 mb-2">Drag and drop files here</p>
          <p className="text-gray-500 text-sm mb-4">or</p>
          <button 
            className="px-4 py-2 bg-gold text-navy font-medium rounded hover:bg-gold/90"
            onClick={() => setShowAddTagModal(true)}
            disabled={isUploading}
          >
            {isUploading ? 'Uploading...' : 'Browse Files'}
          </button>
        </div>
      </div>
      
      {/* Processing Stats Indicator - Only show if endpoint is working */}
      {processingStats && Object.keys(processingStats).length > 0 && (
        <div className="bg-navy-light p-4 mb-4 rounded-lg">
          <div className="flex flex-col space-y-3">
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Processing Status:</span>
              <span className="text-gold">
                {processingStats.processing_files ?? 0} processing, 
                {processingStats.processed_files ?? 0} complete, 
                {processingStats.failed_files ?? 0} failed
              </span>
            </div>
            
            {processingStats.gpu_usage !== undefined && (
              <div className="flex items-center">
                <div className="mr-3 text-gray-400">GPU Usage:</div>
                <div className="flex-1 bg-navy rounded-full h-2.5">
                  <div 
                    className="bg-gold h-2.5 rounded-full" 
                    style={{ width: `${processingStats.gpu_usage}%` }}
                  ></div>
                </div>
                <div className="ml-3 text-gold">{processingStats.gpu_usage}%</div>
              </div>
            )}
            
            {processingStats.eta !== undefined && processingStats.eta > 0 && (
              <div className="text-sm text-gray-400">
                Estimated time remaining: {Math.ceil(processingStats.eta / 60)} minutes
              </div>
            )}
          </div>
        </div>
      )}
      
      {/* Search and Controls */}
      <div className="bg-navy-light p-4 mb-4 rounded-lg flex flex-wrap gap-2 justify-between items-center">
        <div className="flex space-x-2 items-center">
          <div className="relative flex items-center">
            <input
              type="text"
              placeholder="Search file names & contents..."
              className="bg-navy p-2 pl-9 rounded-l focus:outline-none focus:ring-1 focus:ring-gold min-w-[300px]"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
            <span className="absolute left-3 text-gold">
              {isLoading && isSearching ? 
                <span className="animate-spin inline-block h-4 w-4 border-2 border-gold border-r-transparent rounded-full"/> : 
                <Icon name="search" size={16} style={{ color: '#d4af37' }} />
              }
            </span>
            <button 
              className={`px-3 py-2 ${!searchTerm.trim() ? 'bg-gold/10 text-gray-400' : 'bg-gold/20 hover:bg-gold/30 text-gold'} font-medium rounded-r border-l border-navy-lighter`}
              onClick={handleSearch}
              disabled={!searchTerm.trim() || (isLoading && isSearching)}
            >
              {isLoading && isSearching ? 'Searching...' : 'Search'}
            </button>
            {searchTerm && (
              <Icon 
                name="close"
                size={14}
                className="absolute right-[85px]"
                tooltip="Clear search"
                onClick={() => {
                  setSearchTerm('');
                  if (isSearching) {
                    setIsSearching(false);
                    setSearchResults([]);
                  }
                }}
                style={{ cursor: 'pointer', opacity: 0.6 }}
              />
            )}
          </div>
        </div>
        
        <div className="flex space-x-3">
          {/* Sort Controls */}
          <div className="flex items-center space-x-1 mr-2">
            <span className="text-xs text-gray-400">Sort by:</span>
          </div>
          <button 
            className={`px-3 py-1 rounded text-sm font-medium border ${sortField === 'name' 
              ? 'bg-gold/20 text-gold border-gold' 
              : 'bg-navy hover:bg-navy-lighter border-transparent'}`}
            onClick={() => handleSortChange('name')}
          >
            Name {sortField === 'name' && (sortDirection === 'asc' ? '↑' : '↓')}
          </button>
          <button 
            className={`px-3 py-1 rounded text-sm font-medium border ${sortField === 'size' 
              ? 'bg-gold/20 text-gold border-gold' 
              : 'bg-navy hover:bg-navy-lighter border-transparent'}`}
            onClick={() => handleSortChange('size')}
          >
            Size {sortField === 'size' && (sortDirection === 'asc' ? '↑' : '↓')}
          </button>
          <button 
            className={`px-3 py-1 rounded text-sm font-medium border ${sortField === 'date' 
              ? 'bg-gold/20 text-gold border-gold' 
              : 'bg-navy hover:bg-navy-lighter border-transparent'}`}
            onClick={() => handleSortChange('date')}
          >
            Date {sortField === 'date' && (sortDirection === 'asc' ? '↑' : '↓')}
          </button>
          <button 
            className={`px-3 py-1 rounded text-sm font-medium border ${sortField === 'status' 
              ? 'bg-gold/20 text-gold border-gold' 
              : 'bg-navy hover:bg-navy-lighter border-transparent'}`}
            onClick={() => handleSortChange('status')}
          >
            Linked {sortField === 'status' && (sortDirection === 'asc' ? '↑' : '↓')}
          </button>
          <button 
            className={`px-3 py-1 rounded text-sm font-medium border ${sortField === 'processed' 
              ? 'bg-gold/20 text-gold border-gold' 
              : 'bg-navy hover:bg-navy-lighter border-transparent'}`}
            onClick={() => handleSortChange('processed')}
          >
            Processed {sortField === 'processed' && (sortDirection === 'asc' ? '↑' : '↓')}
          </button>
        </div>
        
        {selectedFiles.length > 0 && projectId && (
          <button 
            onClick={handleAttachToProject}
            className="px-3 py-1 bg-gold/20 hover:bg-gold/30 text-gold rounded text-sm"
          >
            Attach Selected ({selectedFiles.length})
          </button>
        )}
      </div>
      
      {/* Files List with bulk selection header */}
      <div className="flex-1 bg-navy-light p-4 rounded-lg overflow-y-auto">
        <h3 className="text-lg font-medium text-gold mb-3 pb-2 border-b border-navy flex justify-between items-center">
          <div className="flex items-center">
            {isSearching ? (
              <div className="flex flex-col">
                <div className="flex items-center">
                  <span className="text-lg">Search Results</span>
                  <span className="ml-2 px-2 py-0.5 bg-gold/20 text-gold rounded text-sm">
                    {searchResults.length} {searchResults.length === 1 ? 'match' : 'matches'}
                  </span>
                </div>
                <div className="text-sm mt-1">
                  <span className="text-gray-400">Query: </span>
                  <span className="text-gold font-bold italic">"{searchTerm}"</span>
                </div>
              </div>
            ) : (
              <div className="flex items-center">
                <span className="text-lg mr-2">All Files</span>
                <div className="text-sm bg-navy/60 rounded px-2 py-0.5 flex items-center">
                  <span className="text-gray-400">Showing:</span>
                  <span className="ml-1 text-gold">{getSortedFiles().length}</span>
                  {sortField && (
                    <span className="ml-1 text-gray-400">
                      • Sorted by <span className="text-gold">{sortField}</span> 
                      {sortDirection === 'asc' ? '↑' : '↓'}
                    </span>
                  )}
                </div>
              </div>
            )}
          </div>
          <div className="flex items-center space-x-2">
            {/* Select All Checkbox and Bulk Action Controls */}
            <div className="flex items-center mr-3">
              <label className="flex items-center cursor-pointer mr-3">
                <input
                  type="checkbox"
                  checked={selectAllChecked}
                  onChange={toggleSelectAll}
                  className="w-4 h-4 accent-gold bg-navy border-gold/30 rounded focus:ring-gold"
                />
                <span className="ml-2 text-xs text-gray-400">Select All</span>
              </label>
              
              {selectedFiles.length > 0 && (
                <button
                  onClick={clearSelection}
                  className="text-xs text-gray-400 hover:text-gray-300 underline ml-2"
                >
                  Clear
                </button>
              )}
            </div>
            
            {/* Batch action buttons - only show when files are selected */}
            {selectedFiles.length > 0 && (
              <>
                <span className="text-xs text-gray-400 mr-1">
                  {selectedFiles.length} selected
                </span>
                <button 
                  onClick={async () => {
                    // Implement batch download
                    for (const fileId of selectedFiles) {
                      try {
                        const file = files.find(f => f.id === fileId);
                        if (file) {
                          const blob = await fileService.downloadFile(fileId);
                          const url = window.URL.createObjectURL(blob);
                          const a = document.createElement('a');
                          a.href = url;
                          a.download = file.name;
                          document.body.appendChild(a);
                          a.click();
                          window.URL.revokeObjectURL(url);
                          a.remove();
                        }
                      } catch (err) {
                        console.error(`Error downloading file ${fileId}:`, err);
                      }
                    }
                  }}
                  className="text-xs px-2 py-1 bg-gold/20 hover:bg-gold/30 text-gold rounded"
                >
                  Download Selected ({selectedFiles.length})
                </button>
                
                <button 
                  onClick={() => {
                    // Show project assignment dropdown for batch assignment
                    const dropdown = document.getElementById('batch-project-dropdown');
                    if (dropdown) {
                      dropdown.classList.toggle('hidden');
                    }
                  }}
                  className="text-xs px-2 py-1 bg-gold/20 hover:bg-gold/30 text-gold rounded project-dropdown-toggle"
                >
                  Assign Selected ({selectedFiles.length})
                </button>
                
                <button 
                  onClick={async () => {
                    // Implement batch delete with confirmation
                    if (window.confirm(`Are you sure you want to delete ${selectedFiles.length} files? This action cannot be undone.`)) {
                      try {
                        // Delete each file
                        for (const fileId of selectedFiles) {
                          await fileService.deleteFile(fileId);
                        }
                        
                        // Update local state by removing deleted files
                        setFiles(prev => prev.filter(file => !selectedFiles.includes(file.id)));
                        
                        // Clear selection
                        setSelectedFiles([]);
                      } catch (err) {
                        console.error('Error deleting files:', err);
                        setError('Failed to delete some files. Please try again.');
                      }
                    }
                  }}
                  className="text-xs px-2 py-1 bg-red-700/30 hover:bg-red-700/50 text-red-400 rounded"
                >
                  Delete Selected ({selectedFiles.length})
                </button>
                
                {/* Relative positioned container for dropdown */}
                <div className="relative">
                  {/* Project selection dropdown for batch assignment */}
                  <div 
                    id="batch-project-dropdown"
                    className="absolute right-0 mt-8 bg-navy-light rounded shadow-lg z-10 hidden"
                    style={{ minWidth: '200px' }}
                    onClick={(e) => e.stopPropagation()}
                  >
                    <div className="p-2 border-b border-navy">
                      <div className="text-xs text-gold font-medium mb-1">Assign to Project:</div>
                      {projects.length > 0 ? (
                        <div className="max-h-40 overflow-y-auto">
                          {projects.map(project => (
                            <div 
                              key={project.id} 
                              className="p-1.5 hover:bg-navy rounded text-sm cursor-pointer"
                              onClick={async () => {
                                try {
                                  // Call API to link files to project
                                  await fileService.linkFilesToProject({
                                    file_ids: selectedFiles,
                                    project_id: project.id
                                  });
                                  
                                  // Update local state
                                  setFiles(prev => 
                                    prev.map(file => 
                                      selectedFiles.includes(file.id) 
                                        ? { ...file, projectId: project.id } 
                                        : file
                                    )
                                  );
                                  
                                  // Hide dropdown
                                  const dropdown = document.getElementById('batch-project-dropdown');
                                  if (dropdown) {
                                    dropdown.classList.add('hidden');
                                  }
                                  
                                  // Clear selection after successful operation
                                  setSelectedFiles([]);
                                  
                                  // Force refresh the file list to ensure it's up to date
                                  await fetchFiles();
                                } catch (err) {
                                  console.error('Error assigning files to project:', err);
                                  setError('Failed to assign files to project. Please try again.');
                                }
                              }}
                            >
                              {project.name}
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="text-xs text-gray-400 p-1.5">No projects available</div>
                      )}
                    </div>
                    <div 
                      className="p-2 text-xs hover:bg-red-700/30 text-red-400 rounded cursor-pointer"
                      onClick={async () => {
                        // For each selected file that has a project ID, remove it from that project
                        const filesToProcess = files.filter(
                          file => selectedFiles.includes(file.id) && file.projectId !== null
                        );
                        
                        if (filesToProcess.length > 0 && 
                            window.confirm(`Are you sure you want to remove ${filesToProcess.length} file(s) from their projects?`)) {
                          try {
                            // Group files by project for more efficient unlinking
                            const filesByProject: {[key: string]: string[]} = {};
                            
                            filesToProcess.forEach(file => {
                              if (file.projectId) {
                                if (!filesByProject[file.projectId]) {
                                  filesByProject[file.projectId] = [];
                                }
                                filesByProject[file.projectId].push(file.id);
                              }
                            });
                            
                            // Process each project group
                            for (const [projectId, fileIds] of Object.entries(filesByProject)) {
                              await fileService.unlinkFilesFromProject(fileIds, projectId);
                            }
                            
                            // Update local state
                            setFiles(prev => 
                              prev.map(file => 
                                selectedFiles.includes(file.id) && file.projectId !== null
                                  ? { ...file, projectId: null }
                                  : file
                              )
                            );
                            
                            // Clear selection after successful operation
                            setSelectedFiles([]);
                            
                            // Force refresh the file list to ensure it's up to date
                            await fetchFiles();
                          } catch (err) {
                            console.error('Error removing files from projects:', err);
                            setError('Failed to remove files from projects. Please try again.');
                          }
                        }
                        
                        // Hide dropdown
                        const dropdown = document.getElementById('batch-project-dropdown');
                        if (dropdown) {
                          dropdown.classList.add('hidden');
                        }
                      }}
                    >
                      <span className="text-red-400">Remove from Projects</span>
                    </div>
                  </div>
                </div>
              </>
            )}
            {isSearching && (
              <button 
                onClick={() => {
                  setIsSearching(false);
                  setSearchTerm('');
                  setSearchResults([]);
                  fetchFiles(); // Reload original file list
                }}
                className="w-8 h-8 flex items-center justify-center bg-red-700/30 hover:bg-red-700/50 text-red-400 rounded"
                title="Clear search"
              >
                <Icon name="close" size={16} />
              </button>
            )}
          </div>
        </h3>
        
        {isLoading ? (
          <div className="p-6 text-center">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-gold border-r-transparent align-[-0.125em]" role="status">
              <span className="!absolute !-m-px !h-px !w-px !overflow-hidden !whitespace-nowrap !border-0 !p-0 ![clip:rect(0,0,0,0)]">Loading...</span>
            </div>
            <div className="mt-2 text-gray-400">Loading files...</div>
          </div>
        ) : error ? (
          <div className="p-6 text-center text-red-400">
            <Icon name="question" size={24} className="mb-2 mx-auto" style={{ color: '#f87171' }} />
            <div>{error}</div>
            <button 
              onClick={() => window.location.reload()}
              className="mt-4 px-4 py-2 bg-navy hover:bg-navy-lighter rounded text-sm"
            >
              Retry
            </button>
          </div>
        ) : getSortedFiles().length > 0 ? (
          <div className="space-y-2">
            {getSortedFiles().map(file => {
              // Log each file to debug projectId values
              console.log(`[MAINFILEMANAGER] Processing file in UI: ${file.id} (${file.name}), projectId: ${file.projectId}, type: ${typeof file.projectId}`);
              
              // Use our helper function to check if file is linked to a project
              const isLinked = isFileLinkedToProject(file.projectId);
              
              // If project ID is valid, find the matching project
              let linkedProject = null;
              if (isLinked && file.projectId) {
                linkedProject = projects.find(p => p.id === file.projectId);
                console.log(`[MAINFILEMANAGER] File ${file.id} is linked to project: ${file.projectId}`);
                console.log(`[MAINFILEMANAGER] Found linked project: ${linkedProject ? linkedProject.name : 'not found'}`);
                
                if (!linkedProject) {
                  console.warn(`[MAINFILEMANAGER] Project not found for ID: ${file.projectId}. This may indicate a stale reference.`);
                }
              }
              
              return (
                <div key={file.id} className="p-3 bg-navy hover:bg-navy-lighter rounded-lg flex items-center justify-between">
                  <div className="flex items-center">
                    {/* Checkbox for selection */}
                    <div className="mr-3">
                      <input
                        type="checkbox"
                        checked={selectedFiles.includes(file.id)}
                        onChange={() => toggleFileSelection(file.id)}
                        className="w-4 h-4 accent-gold bg-navy border-gold/30 rounded focus:ring-gold"
                      />
                    </div>
                    
                    {/* Enhanced file type icon */}
                    <div className={`w-12 h-12 ${getFileBadgeStyles(file.type).bgClass} rounded-lg flex flex-col items-center justify-center mr-3`} 
                      title={getFileTypeMetadata(file.type).description}>
                      <Icon 
                        name={getFileTypeMetadata(file.type).icon as any} 
                        size={16} 
                        style={{ 
                          filter: getFileBadgeStyles(file.type).iconFilter,
                          cursor: 'default'
                        }}
                      />
                      <span className={`${getFileBadgeStyles(file.type).textClass} text-xs mt-0.5 font-medium`}>{file.type.toUpperCase()}</span>
                    </div>
                    
                    {/* File info */}
                    <div className="flex-1 min-w-0">
                      <h4 className="font-medium flex items-center">
                        {file.name}
                        {/* Search relevance if available */}
                        {isSearching && file.relevance !== undefined && (
                          <span className="ml-2 text-xs px-1.5 py-0.5 bg-gold/20 text-gold rounded">
                            {Math.round(file.relevance)}%
                          </span>
                        )}
                      </h4>
                      <div className="flex text-xs text-gray-400 space-x-2 flex-wrap">
                        <span>Added {file.addedAt}</span>
                        <span>•</span>
                        <span>{file.size}</span>
                        
                        {/* Display search snippets for search results */}
                        {isSearching && (file as any).content_snippets && (file as any).content_snippets.length > 0 && (
                          <div className="w-full mt-1.5 bg-navy/50 rounded p-1.5">
                            {(file as any).content_snippets.map((snippet: string, index: number) => (
                              <div key={index} className="text-blue-300 italic mb-1 last:mb-0 text-xs">
                                "{snippet}"
                              </div>
                            ))}
                          </div>
                        )}
                        
                        {/* Processing status */}
                        {file.processed ? (
                          <>
                            <span>•</span>
                            <span className="text-green-400">Processed</span>
                            {file.chunks && (
                              <>
                                <span>•</span>
                                <span>{file.chunks} chunks</span>
                              </>
                            )}
                          </>
                        ) : file.processingFailed ? (
                          <>
                            <span>•</span>
                            <span className="text-red-400">Processing Failed</span>
                          </>
                        ) : (
                          <>
                            <span>•</span>
                            <span className="text-yellow-400">Processing...</span>
                          </>
                        )}
                        
                        {/* Linked status */}
                        <span>•</span>
                        <span className={isLinked ? "text-blue-400" : "text-gray-500"}>
                          {isLinked ? "Linked" : "Unlinked"}
                        </span>
                        
                        {/* Linked project */}
                        {isLinked && (
                          <>
                            <span>•</span>
                            {file.projectName ? (
                              <button 
                                className="text-blue-400 hover:underline"
                                onClick={() => handleSelectProject(file.projectId as string)}
                              >
                                Project: {file.projectName}
                              </button>
                            ) : linkedProject ? (
                              <button 
                                className="text-blue-400 hover:underline"
                                onClick={() => handleSelectProject(linkedProject.id)}
                              >
                                Project: {linkedProject.name}
                              </button>
                            ) : (
                              <span className="text-yellow-400">
                                Project ID: {file.projectId}
                              </span>
                            )}
                          </>
                        )}
                      </div>
                      
                      {/* File Description Box - Hidden by default */}
                      <div id={`file-description-box-${file.id}`} className="w-full mt-2 hidden">
                        <div className="bg-navy-lighter p-3 rounded">
                          <h5 className="text-sm font-medium text-gold mb-1">Description:</h5>
                          <div className="text-xs text-gray-300">
                            {file.description ? 
                              file.description : 
                              <span className="italic text-gray-500">No description provided</span>
                            }
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  {/* Action buttons */}
                  <div className="flex space-x-2 items-center relative">
                    {/* Show retry processing button for failed files */}
                    {file.processingFailed && (
                      <button 
                        onClick={() => handleRetryProcessing(file.id)}
                        className="w-8 h-8 flex items-center justify-center bg-gold/20 hover:bg-gold/30 text-gold rounded"
                        title="Retry processing"
                      >
                        <Icon name="refresh" size={16} />
                      </button>
                    )}
                    
                    {/* View Details Button */}
                    <button 
                      onClick={() => showFileDetails(file)}
                      className="w-8 h-8 flex items-center justify-center bg-gold/20 hover:bg-gold/30 text-gold rounded"
                      title="View file details"
                    >
                      <Icon name="view" size={16} />
                    </button>
                    
                    {/* Assign/Link Button */}
                    <button 
                      onClick={(e) => {
                        e.stopPropagation(); // Prevent clicking from bubbling up to the document
                        // Show project selection dropdown for assignment
                        const dropdown = document.getElementById(`project-dropdown-${file.id}`);
                        if (dropdown) {
                          dropdown.classList.toggle('hidden');
                        }
                      }}
                      className="w-8 h-8 flex items-center justify-center bg-gold/20 hover:bg-gold/30 text-gold rounded project-dropdown-toggle"
                      title="Assign to project"
                    >
                      <Icon name="link" size={16} />
                    </button>
                    
                    {/* Modify Button */}
                    <button 
                      onClick={() => {
                        // Show modify modal for this file
                        // Create a modal if it doesn't exist
                        let modal = document.getElementById(`modify-modal-${file.id}`);
                        if (!modal) {
                          modal = document.createElement('div');
                          modal.id = `modify-modal-${file.id}`;
                          modal.className = 'fixed inset-0 bg-black/50 flex items-center justify-center z-50';
                          modal.innerHTML = `
                            <div class="bg-navy-light rounded-lg p-6 max-w-md w-full">
                              <h3 class="text-lg font-medium text-gold mb-4">Modify File Details</h3>
                              <div class="mb-4">
                                <label class="block text-sm text-gray-400 mb-1">File Name</label>
                                <input type="text" value="${file.name}" 
                                  class="w-full bg-navy p-2 rounded text-gray-300" id="file-name-${file.id}">
                              </div>
                              <div class="mb-4">
                                <label class="block text-sm text-gray-400 mb-1">Description</label>
                                <textarea class="w-full bg-navy p-2 rounded text-gray-300 h-20" 
                                  id="file-description-${file.id}">${file.description || ''}</textarea>
                              </div>
                              <div class="flex justify-end">
                                <button class="px-3 py-1 bg-red-700/30 hover:bg-red-700/50 text-red-400 rounded text-sm mr-2 cancel-btn">
                                  Cancel
                                </button>
                                <button class="px-3 py-1 bg-gold text-navy font-medium rounded hover:bg-gold/90 save-btn">
                                  Save Changes
                                </button>
                              </div>
                            </div>
                          `;
                          
                          document.body.appendChild(modal);
                          
                          // Add event listeners
                          const saveBtn = modal.querySelector('.save-btn');
                          const cancelBtn = modal.querySelector('.cancel-btn');
                          const clickOutside = (e: MouseEvent) => {
                            if (e.target === modal) {
                              if (window.confirm("Are you sure you want to close? Any unsaved changes will be lost.")) {
                                modal?.remove();
                              }
                            }
                          };
                          
                          saveBtn?.addEventListener('click', async () => {
                            try {
                              const nameInput = document.getElementById(`file-name-${file.id}`) as HTMLInputElement;
                              const descInput = document.getElementById(`file-description-${file.id}`) as HTMLTextAreaElement;
                              
                              if (nameInput && descInput) {
                                // Call API to update file
                                await fileService.updateFile(file.id, {
                                  name: nameInput.value,
                                  description: descInput.value
                                });
                                
                                // Update local state
                                setFiles(prev => 
                                  prev.map(f => 
                                    f.id === file.id 
                                      ? { ...f, name: nameInput.value, description: descInput.value } 
                                      : f
                                  )
                                );
                              }
                              
                              // Remove modal
                              modal?.remove();
                            } catch (err) {
                              console.error('Error updating file:', err);
                              setError('Failed to update file. Please try again.');
                            }
                          });
                          
                          cancelBtn?.addEventListener('click', () => {
                            if (window.confirm("Are you sure you want to cancel? Any unsaved changes will be lost.")) {
                              modal?.remove();
                            }
                          });
                          
                          modal.addEventListener('click', clickOutside);
                        } else {
                          // If modal exists, just show it
                          modal.classList.remove('hidden');
                        }
                      }}
                      className="w-8 h-8 flex items-center justify-center bg-gold/20 hover:bg-gold/30 text-gold rounded"
                      title="Modify file details"
                    >
                      <Icon name="settings" size={16} />
                    </button>
                    
                    {/* Project assignment dropdown */}
                    <div 
                      id={`project-dropdown-${file.id}`}
                      className="absolute mt-8 bg-navy-light rounded shadow-lg z-10 hidden"
                      style={{ minWidth: '180px' }}
                      onClick={(e) => e.stopPropagation()} // Prevent dropdown clicks from closing itself
                    >
                      <div className="p-2 border-b border-navy">
                        <div className="text-xs text-gold font-medium mb-1">Assign to Project:</div>
                        {projects.length > 0 ? (
                          <div className="max-h-40 overflow-y-auto">
                            {projects.map(project => (
                              <div 
                                key={project.id} 
                                className="p-1.5 hover:bg-navy rounded text-sm cursor-pointer"
                                onClick={async () => {
                                  try {
                                    // Call API to link file to project
                                    await fileService.linkFilesToProject({
                                      file_ids: [file.id],
                                      project_id: project.id
                                    });
                                    
                                    // Update local state
                                    setFiles(prev => 
                                      prev.map(f => 
                                        f.id === file.id 
                                          ? { ...f, projectId: project.id } 
                                          : f
                                      )
                                    );
                                    
                                    // Hide dropdown
                                    const dropdown = document.getElementById(`project-dropdown-${file.id}`);
                                    if (dropdown) {
                                      dropdown.classList.add('hidden');
                                    }
                                    
                                    // Force refresh the file list to ensure it's up to date
                                    await fetchFiles();
                                  } catch (err) {
                                    console.error('Error assigning file to project:', err);
                                    setError('Failed to assign file to project. Please try again.');
                                  }
                                }}
                              >
                                {project.name}
                              </div>
                            ))}
                          </div>
                        ) : (
                          <div className="text-xs text-gray-400 p-1.5">No projects available</div>
                        )}
                      </div>
                      <div 
                        className="p-2 text-xs hover:bg-red-700/30 text-red-400 rounded cursor-pointer"
                        onClick={async () => {
                          // Only attempt to unlink if currently attached to a project
                          if (file.projectId && window.confirm(`Are you sure you want to remove "${file.name}" from its project?`)) {
                            try {
                              // Call API to unlink file
                              await fileService.unlinkFilesFromProject([file.id], file.projectId);
                              
                              // Update local state
                              setFiles(prev => 
                                prev.map(f => 
                                  f.id === file.id 
                                    ? { ...f, projectId: null } 
                                    : f
                                )
                              );
                              
                              // Force refresh the file list to ensure it's up to date
                              await fetchFiles();
                            } catch (err) {
                              console.error('Error removing file from project:', err);
                              setError('Failed to remove file from project. Please try again.');
                            }
                          }
                          
                          // Hide dropdown
                          const dropdown = document.getElementById(`project-dropdown-${file.id}`);
                          if (dropdown) {
                            dropdown.classList.add('hidden');
                          }
                        }}
                      >
                        <span className={file.projectId ? "text-red-400" : "text-gray-500"}>
                          {file.projectId ? "Remove from Project" : "Not Assigned"}
                        </span>
                      </div>
                    </div>
                    
                    {/* Download Button */}
                    <button 
                      onClick={async () => {
                        try {
                          console.log(`Attempting to download file: ${file.id} - ${file.name}`);
                          
                          // Try two different download methods for maximum compatibility
                          
                          // Method 1: Direct URL approach
                          const baseUrl = window.location.origin;
                          const downloadUrl = `${baseUrl}/api/files/${file.id}/download`;
                          console.log(`Download URL: ${downloadUrl}`);
                          
                          // Try direct download method first
                          const a = document.createElement('a');
                          a.href = downloadUrl;
                          a.download = file.name; // Suggest a filename
                          a.target = '_blank';
                          a.rel = 'noopener noreferrer';
                          document.body.appendChild(a);
                          a.click();
                          document.body.removeChild(a);
                          
                          // Method 2: Backup approach - use fileService
                          // This will be attempted if the user sees Method 1 not working
                          console.log("If the file doesn't download automatically, try the API method...");
                          
                          // Allow user to try a backup method if needed
                          setTimeout(() => {
                            try {
                              // Create a trigger for backup method if needed
                              const backupTrigger = document.createElement('div');
                              backupTrigger.textContent = 'Click here if download didn\'t start';
                              backupTrigger.style.position = 'fixed';
                              backupTrigger.style.bottom = '20px';
                              backupTrigger.style.right = '20px';
                              backupTrigger.style.backgroundColor = '#1F2937';
                              backupTrigger.style.color = '#D1D5DB';
                              backupTrigger.style.padding = '10px';
                              backupTrigger.style.borderRadius = '4px';
                              backupTrigger.style.cursor = 'pointer';
                              backupTrigger.style.zIndex = '9999';
                              backupTrigger.onclick = async () => {
                                try {
                                  // Use the Blob method as backup
                                  const blob = await fileService.downloadFile(file.id);
                                  const url = window.URL.createObjectURL(blob);
                                  const a = document.createElement('a');
                                  a.href = url;
                                  a.download = file.name;
                                  document.body.appendChild(a);
                                  a.click();
                                  window.URL.revokeObjectURL(url);
                                  a.remove();
                                  document.body.removeChild(backupTrigger);
                                } catch (backupError) {
                                  console.error('Backup download method failed:', backupError);
                                  alert('Both download methods failed. Please try again later.');
                                }
                              };
                              document.body.appendChild(backupTrigger);
                              
                              // Auto-remove after 10 seconds
                              setTimeout(() => {
                                if (document.body.contains(backupTrigger)) {
                                  document.body.removeChild(backupTrigger);
                                }
                              }, 10000);
                            } catch (notifyError) {
                              console.error('Error showing backup notification:', notifyError);
                            }
                          }, 1000);
                          
                        } catch (err) {
                          console.error('Error initiating download:', err);
                          setError('Failed to download file. Please try again.');
                        }
                      }}
                      className="w-8 h-8 flex items-center justify-center bg-gold/20 hover:bg-gold/30 text-gold rounded"
                      title="Download file"
                    >
                      <Icon name="download" size={16} />
                    </button>
                    {/* Delete Button */}
                    <button 
                      className="px-3 py-1 bg-red-700/30 hover:bg-red-700/50 text-red-400 rounded text-sm"
                      onClick={() => {
                        if (window.confirm(`Are you sure you want to delete "${file.name}"? This action cannot be undone.`)) {
                          handleDeleteFile(file.id);
                        }
                      }}
                      title="Delete file"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="p-6 text-center">
            {isSearching ? (
              <div>
                <div className="text-4xl mb-2">🔍</div>
                <div className="text-gray-400 mb-2">No files match your search criteria.</div>
                <div className="text-xs text-gray-500">Try using different keywords or uploading relevant documents.</div>
              </div>
            ) : (
              <div>
                <Icon name="view" size={48} className="mb-2 mx-auto" style={{ opacity: 0.5 }} />
                <div className="text-gray-400 mb-2">No files have been added yet.</div>
                <div className="text-xs text-gray-500">Upload files using the panel above to get started.</div>
              </div>
            )}
          </div>
        )}
      </div>
      
      {/* File Details Panel */}
      {showDetailsPanel && selectedFileDetails && (
        <div className="fixed inset-y-0 right-0 w-80 bg-navy-light border-l border-navy-lighter shadow-lg z-40 transform transition-transform duration-300 ease-in-out">
          <div className="h-full flex flex-col p-4">
            {/* Header */}
            <div className="flex justify-between items-center mb-4 pb-3 border-b border-navy">
              <h3 className="text-lg font-medium text-gold">File Details</h3>
              <Icon 
                name="close"
                size={20}
                onClick={closeDetailsPanel}
                tooltip="Close details"
                style={{ cursor: 'pointer' }}
              />
            </div>
            
            {/* File preview */}
            <div className="mb-4 bg-navy rounded-lg p-4 flex flex-col items-center">
              <div className={`w-16 h-16 ${getFileBadgeStyles(selectedFileDetails.type).bgClass} rounded-lg flex flex-col items-center justify-center mb-2`}>
                <Icon 
                  name={getFileTypeMetadata(selectedFileDetails.type).icon as any} 
                  size={24}
                  style={{ 
                    filter: getFileBadgeStyles(selectedFileDetails.type).iconFilter,
                    cursor: 'default'
                  }}
                />
                <span className={`${getFileBadgeStyles(selectedFileDetails.type).textClass} text-xs mt-1`}>{selectedFileDetails.type}</span>
              </div>
              <h4 className="text-center font-medium text-gold mt-2 break-words w-full">{selectedFileDetails.name}</h4>
            </div>
            
            {/* File metadata */}
            <div className="flex-1 overflow-y-auto">
              <div className="space-y-4">
                {/* Basic info */}
                <div>
                  <h5 className="text-sm text-gray-400 mb-1">Basic Information</h5>
                  <div className="bg-navy rounded p-3 space-y-2">
                    <div className="flex justify-between">
                      <span className="text-xs text-gray-400">Size:</span>
                      <span className="text-xs text-gold">{selectedFileDetails.size}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-xs text-gray-400">Added:</span>
                      <span className="text-xs text-gold">{selectedFileDetails.addedAt}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-xs text-gray-400">Status:</span>
                      <span className="text-xs">
                        {selectedFileDetails.processed ? (
                          <span className="text-green-400">Processed</span>
                        ) : selectedFileDetails.processingFailed ? (
                          <span className="text-red-400">Processing Failed</span>
                        ) : (
                          <span className="text-yellow-400">Processing...</span>
                        )}
                      </span>
                    </div>
                    {selectedFileDetails.processed && selectedFileDetails.chunks && (
                      <div className="flex justify-between">
                        <span className="text-xs text-gray-400">Chunks:</span>
                        <span className="text-xs text-gold">{selectedFileDetails.chunks}</span>
                      </div>
                    )}
                  </div>
                </div>
                
                {/* Project info */}
                <div>
                  <h5 className="text-sm text-gray-400 mb-1">Project Assignment</h5>
                  <div className="bg-navy rounded p-3">
                    {isFileLinkedToProject(selectedFileDetails.projectId) ? (
                      <div>
                        <div className="flex justify-between mb-2">
                          <span className="text-xs text-gray-400">Project:</span>
                          <span className="text-xs text-blue-400">
                            {selectedFileDetails.projectName || selectedFileDetails.projectId}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-xs text-gray-400">Active in project:</span>
                          <span className={`text-xs ${selectedFileDetails.active ? 'text-green-400' : 'text-orange-400'}`}>
                            {selectedFileDetails.active ? 'Yes' : 'No'}
                          </span>
                        </div>
                      </div>
                    ) : (
                      <div className="text-xs text-gray-400 text-center py-1">
                        Not assigned to any project
                      </div>
                    )}
                  </div>
                </div>
                
                {/* Description */}
                <div>
                  <h5 className="text-sm text-gray-400 mb-1">Description</h5>
                  <div className="bg-navy rounded p-3">
                    {selectedFileDetails.description ? (
                      <p className="text-xs text-gray-300 whitespace-pre-wrap">{selectedFileDetails.description}</p>
                    ) : (
                      <p className="text-xs text-gray-500 italic">No description provided</p>
                    )}
                  </div>
                </div>
              </div>
            </div>
            
            {/* Action buttons */}
            <div className="mt-4 pt-3 border-t border-navy flex justify-between">
              <button 
                onClick={async () => {
                  try {
                    const blob = await fileService.downloadFile(selectedFileDetails.id);
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = selectedFileDetails.name;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    a.remove();
                  } catch (err) {
                    console.error(`Error downloading file:`, err);
                  }
                }}
                className="px-3 py-1.5 bg-gold/20 hover:bg-gold/30 text-gold rounded text-sm flex-1 mr-2"
              >
                <Icon name="download" size={16} className="inline mr-1" />
                Download
              </button>
              
              {isFileLinkedToProject(selectedFileDetails.projectId) && (
                <button 
                  onClick={async () => {
                    if (window.confirm(`Are you sure you want to detach this file from its project?`)) {
                      try {
                        await fileService.unlinkFilesFromProject([selectedFileDetails.id], selectedFileDetails.projectId as string);
                        // Update the local file list
                        setFiles(prev => prev.map(f => f.id === selectedFileDetails.id ? {...f, projectId: null} : f));
                        // Update the details panel
                        setSelectedFileDetails({...selectedFileDetails, projectId: null});
                      } catch (err) {
                        console.error('Error detaching file:', err);
                      }
                    }
                  }}
                  className="px-3 py-1.5 bg-red-700/30 hover:bg-red-700/50 text-red-400 rounded text-sm flex-1"
                >
                  Detach
                </button>
              )}
            </div>
          </div>
        </div>
      )}
      
      {/* File Upload Modal using TagAndAddFileModal */}
      <TagAndAddFileModal
        isOpen={showAddTagModal}
        onClose={() => {
          setShowAddTagModal(false);
          setDroppedFiles([]);
        }}
        preDroppedFiles={droppedFiles}
        onProcessFiles={async (selectedFiles) => {
          console.log("Processing files from TagAndAddFileModal:", selectedFiles);
          setIsUploading(true);
          
          try {
            // Process each file with its individual description
            for (const selectedFile of selectedFiles) {
              console.log("Processing file:", {
                name: selectedFile.file.name,
                description: selectedFile.description,
                projectId: selectedFile.projectId
              });
              
              const uploadRequest = {
                file: selectedFile.file,
                name: selectedFile.file.name,
                description: selectedFile.description,
                project_id: selectedFile.projectId || undefined
              };
              
              try {
                // Upload the file using fileService
                const uploadedFile = await fileService.uploadFile(uploadRequest);
                console.log(`Successfully uploaded file: ${selectedFile.file.name} with project_id: ${selectedFile.projectId || 'null'}`);
                
                // Set up status checking for the uploaded file
                if (uploadedFile && uploadedFile.id) {
                  const checkUploadedFileStatus = async () => {
                    try {
                      const file = await fileService.getFile(uploadedFile.id);
                      setFiles(prev => {
                        const exists = prev.some(f => f.id === uploadedFile.id);
                        if (exists) {
                          return prev.map(f => 
                            f.id === uploadedFile.id 
                              ? mapApiFileToLocal(file)
                              : f
                          );
                        } else {
                          // Add the file if it doesn't exist yet
                          return [...prev, mapApiFileToLocal(file)];
                        }
                      });
                      
                      // If still processing, check again after a delay
                      if (!file.processed && !file.processing_failed) {
                        setTimeout(checkUploadedFileStatus, 3000); // Check again in 3 seconds
                      }
                    } catch (err) {
                      console.error('Error checking uploaded file status:', err);
                    }
                  };
                  
                  // Start checking after 2 seconds
                  setTimeout(checkUploadedFileStatus, 2000);
                }
              } catch (uploadError) {
                console.error(`Error uploading file ${selectedFile.file.name}:`, uploadError);
                // If the API endpoint doesn't exist yet, show a mock success message
                alert(`Mock upload: File ${selectedFile.file.name} uploaded successfully (API endpoint not available)`);
              }
            }
            
            // Clear dropped files
            setDroppedFiles([]);
            
            console.log("[MAINFILEMANAGER] Upload complete");
            
            // Manually trigger a refresh of the file list after upload
            await handleUploadSuccess();
            
            console.log(`Successfully processed ${selectedFiles.length} files`);
          } catch (error) {
            console.error('Error uploading files:', error);
            setError('Failed to upload one or more files. Please try again.');
          } finally {
            setIsUploading(false);
          }
        }}
        currentProjectId={projectId}
      />
    </div>
  );
};

export default MainFileManager;