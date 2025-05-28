# TODO List

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