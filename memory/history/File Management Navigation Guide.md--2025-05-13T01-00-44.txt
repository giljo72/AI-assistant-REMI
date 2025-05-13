# File Management Navigation Guide

This document explains how the file management system is implemented in our AI Assistant project, following the workflow diagrams in the assistant-projectv2.pdf document.

## Component Structure

We've implemented several key components to handle file management:

1. **ProjectFileManager**: Manages files attached to a specific project.
2. **MainFileManager**: Global file manager for all files in the system.
3. **SearchFilesResults**: Shows search results when looking for files to attach to a project.
4. **TagAndAddFileModal**: Modal for adding descriptions to files during upload.

## Navigation Flow

The file management system follows this navigation flow:

### From Project View

1. **Project Manager → Project Files**:
   - Click "View All" in the "Project Files" section
   - This opens the ProjectFileManager component for the selected project

### Within Project File Manager

2. **Project File Manager → Main File Manager**:
   - Click "Browse Global Files" button
   - This opens the MainFileManager component

3. **Project File Manager → Search Results**:
   - Search for files using the search field in the Main File Manager
   - Click the search button (or press Enter)
   - This opens the SearchFilesResults component

### Within Main File Manager

4. **Main File Manager → Tag and Add File Modal**:
   - Click "Browse Files" button or drop files in the drop area
   - This opens the TagAndAddFileModal component

### Navigation Back

- **Project File Manager → Project Manager**:
   - Click "Return to Project" button

- **Main File Manager → Project File Manager**:
   - Click "Return" button when coming from a project

- **Search Results → Project File Manager**:
   - Click "Cancel" or "Attach Selected" button

## Key Features

### ProjectFileManager Features

- View files attached to the current project
- Toggle file activation status
- Detach files from project
- View, download files
- Browse global files to find and attach new files
- Drag and drop file upload
- Sort files by various criteria

### MainFileManager Features

- View all files in the system
- Sort files by name, date, size, status
- Search across all files
- See file processing status
- Monitor GPU usage during processing
- Select files to attach to projects
- Delete files from the system
- Drag and drop file upload

### SearchFilesResults Features

- View search results with relevance scores
- Sort results by relevance, name, or date
- Select multiple files to attach
- Preview files before attaching
- Attach selected files to the current project

### TagAndAddFileModal Features

- Add descriptions to files during upload
- Select multiple files to process
- Required field validation
- Add more files after initial selection

## Implementation Details

The file management system uses a state-based approach for navigation:

1. `activeView` state in App.tsx determines which component to display
2. Handler functions like `handleOpenProjectFiles()` change the active view
3. Navigation buttons in components call appropriate handlers via props

This approach allows for a seamless workflow that matches the design in the PDF document while maintaining the project-centered containment architecture.

## Status Indicators

The implementation includes several status indicators:

- **Linked Status**: Shows if a file is attached to any project
- **Processing Status**: Shows if a file has been processed for the vector database
- **Active Status**: Toggle switch for enabling/disabling a file in a project
- **GPU Usage**: Indicator that shows processing load during file operations
- **Search Relevance**: Percentage indicator showing search result relevance

All these indicators match the workflow diagrams in the assistant-projectv2.pdf document.