# Backend Integration Testing Instructions

This document provides instructions for testing the backend integration of the file management system.

## Prerequisites

1. Make sure you have both the backend and frontend running:
   ```bash
   # Terminal 1 - Start backend
   cd backend
   ../venv_nemo/Scripts/activate
   python -m uvicorn app.main:app --reload --port 8000

   # Terminal 2 - Start frontend
   cd frontend
   npm run dev
   ```

2. Ensure your database is properly configured with the pgvector extension.

## Migration Process

To migrate from the mock implementation to the real backend implementation:

1. Run the migration script:
   ```bash
   python scripts/migrate_to_real_backend.py
   ```

2. Restart the frontend development server:
   ```bash
   cd frontend
   npm run dev
   ```

## Testing File Management Workflow

### 1. Test File Upload

1. Navigate to the Main File Manager by clicking the file icon in the sidebar.
2. Click the "Upload Files" button.
3. Select a file from your computer (PDF, DOCX, or TXT recommended).
4. Add a description if desired.
5. Select a project from the dropdown or leave as "None (Keep in Global Knowledge)".
6. Click "Upload".
7. Verify the file appears in the file list.
8. Observe the Processing Status panel to see the processing progress.
9. Verify the GPU Utilization display shows activity during processing.

### 2. Test File-Project Linking

1. In the Main File Manager, find a file without a project association.
2. Click the link button (🔗) for that file.
3. Select a project from the dropdown.
4. Click "Link".
5. Verify the file now shows the project name.
6. Navigate to the selected project and click on its File Manager.
7. Verify the file appears in the project's file list.
8. Return to the Main File Manager and verify the file still shows its project association.

### 3. Test File-Project Unlinking

1. In the Main File Manager, find a file with a project association.
2. Click the link button (🔗) for that file.
3. Select "None (Keep in Global Knowledge)" from the dropdown.
4. Click "Link".
5. Verify the file no longer shows a project name.
6. Navigate to the project's File Manager.
7. Verify the file no longer appears in the project's file list.

### 4. Test File Deletion

1. In the Main File Manager, find a file to delete.
2. Click the delete button (🗑️) for that file.
3. Confirm the deletion.
4. Verify the file disappears from the file list.
5. If the file was attached to a project, navigate to that project's File Manager and verify the file is gone.

### 5. Test Admin Tools

1. Click the gear icon (⚙️) in the sidebar to open the Admin Settings Panel.
2. Navigate to the "System Information" tab.
3. Verify it shows database statistics and file storage information.
4. Navigate to the "Reset Options" tab.
5. Test each reset option carefully (be cautious as these are destructive operations):
   - Reset Database: Clears all database tables
   - Reset Vector Store: Removes vector embeddings
   - Reset Files: Deletes physical files
   - Reset Everything: Performs all resets

6. Verify the system information updates after each reset operation.

### 6. Test Error Handling

1. Test error handling by intentionally causing errors:
   - Try to upload a very large file (>50MB)
   - Try to upload an unsupported file type
   - Try to link a file to a non-existent project
   - Try to delete a file that doesn't exist

2. Verify error messages are clear and helpful.

## Complete End-to-End Test

1. Create a new project.
2. Upload multiple files without project association.
3. Link some files to the project.
4. Navigate to the project's File Manager.
5. Verify files appear correctly.
6. Return to Main File Manager.
7. Verify file-project associations are maintained.
8. Delete some files.
9. Verify they're removed from both Main and Project File Managers.
10. Refresh the page completely.
11. Verify all file-project associations persist after refresh.

## Report Issues

If you encounter any issues during testing, please create detailed bug reports that include:
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Screenshots if applicable
- Browser console logs