# TODO List

## Self-Aware Context (High Priority)
- [x] Implement simplified file reading that works in any context mode
- [x] Add syntax highlighting and markdown rendering for code display
- [x] Integrate file content injection into both regular and streaming endpoints
- [ ] MUST DISCUSS: File write permissions strategy before implementation
  - Security considerations for write access
  - User approval workflow
  - Backup and rollback mechanisms
- [ ] Create frontend file browser UI for self-aware mode
  - File tree navigation component
  - Syntax-highlighted code viewer
  - Search within files functionality
- [ ] Implement diff approval interface
  - Side-by-side diff viewer
  - Approve/reject buttons
  - Modification history viewer
- [ ] Add WebSocket for real-time file change notifications
- [ ] Integrate with git for version control of AI changes

## Document Processing
- [ ] Test batch upload functionality with multiple files (PDFs, DOCX, TXT)
  - Verify all files process successfully with the new 2000 character chunk limit
  - Check that NIM embeddings work for all file types
  - Monitor processing status updates

## Recently Completed
- [x] Fixed NIM token limit error by reducing chunk size from 3000 to 2000 characters
- [x] Fixed processing status endpoint TypeError with null chunk counts
- [x] Removed redundant blue refresh button from MainFileManager
- [x] Successfully reprocessed failed PDF files
- [x] Implemented self-aware context backend API endpoints
- [x] Added security validation for code modifications
- [x] Created automatic backup system for file changes
- [x] Implemented audit logging for all modifications
- [x] Integrated self-aware file reading into chat context
- [x] Created SelfAwareService for parsing AI responses
- [x] Removed Llama 3.1 70B model (could not load on RTX 4090)
- [x] Implemented react-markdown with syntax highlighting
- [x] Customized code block styling with darker blue background
- [x] Fixed file reading to show actual content instead of generic examples