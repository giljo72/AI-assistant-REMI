# AI Assistant Dev Log

## January 26, 2025 - UI Cleanup and Sidebar Improvements

### UI Refinements: Prompt Display Cleanup
Cleaned up redundant visual elements in the sidebar to reduce clutter and improve user experience.

1. **Sidebar Visual Updates:**
   - Changed the divider line above [CONTEXT SETTINGS] from dark to yellow (`border-yellow-500`)
   - Maintains visual consistency with the gold theme throughout the application

2. **Removed Redundant Prompt Indicators:**
   - **System Prompts Panel**: Removed the orange active prompt indicator badge
   - **User Prompts Panel**: Removed the gray/white active prompt indicator badge
   - Rationale: These indicators were redundant as the same information is clearly displayed under the chat window
   - Kept all configuration functionality intact - panels still manage prompts through Redux

3. **Code Cleanup:**
   - Removed unused imports from both SystemPromptsPanel and UserPromptsPanel
   - Removed `UserPromptIndicator` component references
   - Removed unused Redux selectors and dispatch calls
   - Simplified component logic by removing active prompt tracking in sidebar

4. **Architecture Verification:**
   - Confirmed proper separation of concerns:
     - Sidebar panels: Configuration and management of prompts
     - Chat window badges: Visual display of active prompts
   - Both systems operate independently through shared Redux state
   - No breaking changes to functionality

### Technical Details:
- Modified files:
  - `/frontend/src/components/layout/MainLayout.tsx` (yellow divider)
  - `/frontend/src/components/chat/SystemPromptsPanel.tsx` (removed indicator)
  - `/frontend/src/components/chat/UserPromptsPanel.tsx` (removed indicator)
- Result: Cleaner, less cluttered UI while maintaining full functionality

## January 26, 2025 - Resource Monitoring Implementation

### Major Feature: Real-time Resource Monitor in Top Bar
Implemented comprehensive resource monitoring display to replace "AI Assistant" text in header.

1. **Initial Implementation:**
   - Real-time VRAM usage display with progress bar
   - Active model name with status indicator
   - Token generation speed display
   - 2-second polling for updates

2. **Circular Gauge Redesign:**
   - Created CircularGauge component matching the design from chat.jpg
   - Four circular gauges with color-coded themes:
     - **GPU (NVIDIA Green #76B900)**: VRAM usage monitoring
     - **CPU (AMD Red #ED1C24 / Intel Blue #0078D4)**: CPU utilization
     - **RAM (Purple #9B59B6)**: Memory usage tracking
     - **HDD (Gray #6C757D)**: Storage space monitoring
   - Each gauge shows numeric value in center with label below
   - Brand names displayed under each gauge (NVIDIA, AMD/Intel, Memory, Storage)

3. **Visual Design:**
   - Circular progress indicators with smooth animations
   - Consistent 50px gauge size with 5px stroke width
   - Model info and stats displayed separately after divider
   - Compact layout fits perfectly in top bar

4. **Integration:**
   - Replaced "AI Assistant" header text with ResourceMonitor
   - Sidebar retains "AI Assistant" title as branding
   - Mock data for CPU/RAM/HDD (backend endpoints pending)
   - Real GPU/VRAM data from existing endpoints

### Technical Implementation:
- Components: 
  - `/frontend/src/components/common/ResourceMonitor.tsx`
  - `/frontend/src/components/common/CircularGauge.tsx`
- Service updates: 
  - Added `getQuickModelStatus()` to modelService
  - Added `getSystemResources()` to systemService (for future use)
- Polling interval: 2 seconds for responsive updates

## May 26, 2025 - NVIDIA NV-Ingest Integration Decision

### Strategic Decision: Advanced Document Processing with NV-Ingest
1. **Why NV-Ingest over Simple Libraries:**
   - **Multimodal Extraction**: Handles text, tables, charts, and images from PDFs/DOCX
   - **15x Performance**: Enterprise-grade speed vs traditional extraction
   - **Future-Proof**: No need to migrate data when scaling up
   - **Smart Loading**: Only loads models needed for specific file types
   - **RTX 4090 Optimized**: Leverages GPU for maximum performance

2. **Smart Model Loading Strategy:**
   - TXT/Code: Direct extraction (0GB VRAM, instant)
   - DOCX: YOLOX + DePlot for charts/tables (4-6GB VRAM, 8-10s)
   - PDF: Full suite including OCR (10-12GB VRAM, 15-20s)
   - XLSX: DePlot for chart extraction (2-3GB VRAM, 5s)

3. **VRAM Management Considerations:**
   - Total models: 6-12GB during processing (fits within 24GB)
   - Models load on-demand, unload when idle
   - No competition with LLMs - documents process separately
   - User gets visual feedback during model loading

4. **Implementation Plan:**
   - Add NV-Ingest container to docker-compose.yml
   - Create processing status WebSocket for real-time updates
   - Enhance ProcessingStatusPanel with model loading progress
   - Implement smart routing based on file extension

## May 26, 2025 - Document Extraction Bug Discovery

### Critical Bug Found:
1. **Document content not being extracted**
   - Documents (DOCX, PDF, etc.) were storing placeholder text instead of actual content
   - Root cause: `processor.py` had placeholder implementations that were never completed
   - This explains why AI couldn't access document content despite successful embeddings
   
2. **Investigation Results:**
   - Both current code AND backup had the same placeholders
   - Text extraction was NEVER implemented, not a regression
   - System was creating embeddings of placeholder text like "[Word document content would be extracted here...]"
   - This is why switching from sentence-transformers to NIM "broke" document retrieval

## May 26, 2025 - Full Migration to NIM Embeddings & Enhanced Document Processing

### Major Changes:
1. **Completely removed sentence-transformers**
   - No more fallback - NIM is now required
   - Removed all sentence-transformers references from code
   - Updated embedding service to require NIM
   - Fixed NIM integration issues (async health check, method names)

2. **Database migration to 1024 dimensions**
   - Changed vector column from 768 to 1024 dimensions
   - Reset all document processing flags
   - Ready for NIM's higher-dimensional embeddings
   - Discovered NIM requires very low similarity thresholds (0.01 vs 0.3)

3. **Enhanced Document Chunking System**
   - Increased default chunk size from 1000 to 3000 characters (3x improvement)
   - Implemented auto-detect document chunking based on filename patterns
   - Business documents get multiple chunk sizes (3000 + 8000 chars)
   - Technical documents get specialized chunking (3000 + 5000 chars)
   - Default documents use standard 3000 char chunks

4. **Simplified User Experience**
   - Auto-chunking is default, no user configuration needed
   - Context modes (Quick/Standard/Deep) will automatically use appropriate chunk sizes
   - Optional manual override available during upload (future feature)

### Technical Discoveries:
- NIM embeddings use different normalization than traditional models
- Similarity scores are much lower (0.05 = excellent match vs 0.7-0.9 traditional)
- NIM optimized for ranking rather than absolute similarity scores
- Both query and passage embeddings require explicit input_type parameter

### Breaking Changes:
- NIM container MUST be running on port 8081
- All existing embeddings were deleted (documents preserved)
- Documents need to be re-processed with NIM
- Minimum similarity threshold changed from 0.3 to 0.01

### Architecture Decisions:
- Chose simplicity over complexity for chunking UI
- Default to "auto-detect" with optional overrides
- Context modes drive chunk selection, not user configuration
- Multi-level chunking only for documents that benefit from it

### Next Steps:
- Test document upload with new auto-chunking
- Implement context mode integration (Deep Research → large chunks)
- Add optional document type override in upload UI
- Turn off "Global Data" context by default (only use project documents)

## May 26, 2025 - NIM Embeddings Integration

### Improvements:
1. **Added NIM embeddings with automatic fallback**
   - Configured system to use NVIDIA NIM embeddings (NV-EmbedQA-E5-V5) as primary
   - Automatic fallback to sentence-transformers when NIM service unavailable
   - Fixed async/await issue in embedding service health check
   
2. **Enhanced embeddings visibility**
   - Added sentence-transformers to models UI as "EMBEDDING FALLBACK"
   - Shows current embedding model status and memory usage
   - Both models use compatible 768-dimensional vectors

### Status:
- NIM embedding service needs to run on port 8001 for NIM usage
- Currently using sentence-transformers as fallback (working correctly)
- Document retrieval confirmed working with semantic search

## January 25, 2025 - Performance Optimizations and Document Context Fixes

### Issues Addressed:
1. **Slow chat loading** - Model status check was taking ~10 seconds
2. **Chat title showing "unknown"** - Chat names weren't loaded before display
3. **Documents not being used in chat context** - Document retrieval had issues

### Solutions Implemented:

#### 1. Optimized Model Status Checking
- Added `get_quick_model_status()` method in ModelOrchestrator that returns minimal info
- Added VRAM caching with 5-second refresh interval to avoid repeated GPU queries
- Created new `/api/models/status/quick` endpoint for frontend
- Updated ChatView to use quick status first, then load full model list in background

#### 2. Fixed Chat Title Display
- Modified `getChatName()` in App.tsx to show "Loading..." instead of "Unknown Chat"
- Added logic to update chat names when chat data is loaded
- Ensures chat name is populated when navigating to a specific chat

#### 3. Enhanced Document Context Retrieval
- Added debugging logs to document search in chat endpoint
- Lowered similarity threshold from 0.6 to 0.3 for better document recall
- Added check for processed documents in project before searching
- Improved error logging with full stack traces
- Added similarity scores to document context display
- Created debug endpoint `/api/files/debug/project-documents/{project_id}` to check document processing status

### Technical Details:
- VRAM usage is now cached and updated every 5 seconds
- Document search now retrieves top 5 chunks but only uses top 3
- Context mode controls are respected (quick-response mode skips documents)
- Better error handling and logging throughout the document pipeline

## January 25, 2025 - Icon Fixes and File Processing Updates

### Fixed View Icon Path
- **Problem**: view.svg icon was not displaying properly in file managers
- **Cause**: Icon component referenced `/icons/View.SVG` with incorrect capitalization
- **Solution**: Updated to `/icons/view.svg` to match actual filename in public/icons directory

### Fixed Infinite Polling in ProjectFileManager
- **Problem**: File status polling continued indefinitely, flooding backend with requests
- **Cause**: useEffect dependency was only checking array length, not actual processing status
- **Solution**: 
  - Changed dependency to track specific processing file IDs
  - Only polls when there are actually files in processing state
  - Stops immediately when all files are processed or failed
  - More efficient tracking prevents unnecessary re-renders

### Fixed Chat Creation Error Handling
- **Problem**: Chat creation failures resulted in fake chat IDs that caused 404 errors
- **Cause**: chatService was creating fallback chats with Date.now() IDs when backend errors occurred
- **Solution**: 
  - Removed fallback chat creation in chatService
  - Now properly throws errors when chat creation fails
  - Frontend will need to handle errors and ensure valid project_id is always provided

### Fixed Chat Creation Schema Mismatch
- **Problem**: Chat creation failed with TypeError: 'context_settings' is an invalid keyword argument
- **Cause**: ChatCreate schema included context_settings field but Chat model didn't have this column
- **Solution**: 
  - Modified base repository create method to filter out fields not in the model
  - Now only passes fields that exist in the database model
  - Prevents schema/model mismatches from causing 500 errors

### Performance and UX Improvements
- **Optimized Model Status Check**:
  - Added fast endpoint `/system/active-model-quick` with 5-second caching
  - Reduced model check time from ~10 seconds to <100ms
  - Added `getActiveModelQuick()` method to systemService
  - Fixed model name mismatch (qwen-2.5-coder:32b → qwen2.5:32b-instruct-q4_K_M)
  - Added caching for available models to prevent multiple API calls
- **Fixed Chat Title Display**:
  - Chat names now update immediately when creating new chats
  - Added chat to chatNames map during creation
  - Changed "Unknown Chat" to "Loading..." for better UX
- **Enhanced Document Debug**:
  - Added `/chats/debug/documents/{project_id}` endpoint
  - Shows document processing status and chunk counts
  - Fixed DocumentChunk import issue
  - Documents are confirmed processed with chunks
- **Document Search Investigation**:
  - Confirmed documents are processed and have chunks
  - Semantic search returns no results even with low threshold (0.1)
  - Issue appears to be with embedding storage or retrieval in pgvector
  - Chat endpoint already uses 0.3 similarity threshold

## January 25, 2025 - Drag and Drop & File Processing Fixes
### Fixed Drag and Drop in ProjectFileManager
- **Problem**: Drag and drop area was just visual placeholder, files would open instead of uploading
- **Solution**: Added proper drag event handlers:
  - `onDragOver` - Prevents default behavior and shows visual feedback
  - `onDragEnter` - Activates drag state
  - `onDragLeave` - Deactivates drag state  
  - `onDrop` - Handles file upload to project
- **Features Added**:
  - Visual feedback during drag (gold border and background)
  - New `isDragging` state for UI updates
  - `handleDroppedFiles` function that opens TagAndAddFileModal
  - Files passed to modal via `preDroppedFiles` prop
  - Modal allows adding descriptions before upload

### Fixed File Processing Status Updates
- **Problems Fixed**:
  - Files showed "Processing..." indefinitely
  - Files didn't appear until page refresh
  - No dynamic updates when processing completed
- **Solutions**:
  - Added separate useEffect for polling processing status
  - Polls every 2 seconds when files are processing
  - Automatically stops polling when all files are processed
  - Clear separation of concerns between file list and status updates
  - Fixed closure issue with projectFiles state in polling logic

### Replaced Emoji Icons with SVG Icons
- **MainFileManager**:
  - Replaced 👁️ with view.svg for View Details button
  - Replaced 🔗 with link.svg for Assign to Project button
  - Replaced ⚙️ with settings.svg for Modify button
  - Replaced ⬇️ with download.svg for Download button
  - Replaced 🗑️ with trash.svg for Delete button
  - Replaced 🔄 with refresh.svg for Retry Processing button
- **ProjectFileManager**:
  - Replaced 👁️ with view.svg for View Details button
  - Replaced ⬇️ with download.svg for Download button
  - Replaced ✕ with close.svg for Close Details button
- **Drag and Drop Areas**:
  - Removed blue circle background (bg-navy-lighter rounded-full)
  - Updated all drag zones to use add.svg without background
  - Consistent styling across MainFileManager, ProjectFileManager, and TagAndAddFileModal

## January 25, 2025 - System Prompt Modal Fixes and Styling

### Fixed Missing Import Error:
- Fixed "Typography is not defined" error in SystemPromptModal
- Added missing Typography and IconButton imports from @mui/material
- Modal now opens correctly when editing system prompts

### Updated Modal Styling:
- Changed all field labels to yellow (#FFC000) for consistency
- Updated input borders from gray to white for better visibility
- Made dialog title yellow to match the app's color scheme
- Added white helper text color for better readability
- Hover states now use yellow instead of gray
- All text fields now have consistent white borders and yellow labels

### Improved Disabled Field Visibility:
- Made disabled/locked text lighter (50% opacity) for better readability
- Disabled field borders now use 30% opacity white
- Disabled text uses WebkitTextFillColor for consistent rendering
- Helper text also becomes lighter when field is disabled
- All labels remain yellow even when disabled for consistency

## January 25, 2025 - Prompt Menu UI Cleanup

### Streamlined System and User Prompt Interfaces:

1. **System Prompts Improvements**
   - Removed category badges (general/coding) to reduce clutter
   - Moved edit icon next to radio button for better space usage
   - Removed trash/delete icon from list view
   - Delete functionality remains available in edit modal

2. **User Prompts Consistency**
   - Changed from checkbox to radio buttons (matching system prompts)
   - Moved edit icon next to radio button
   - Removed trash/delete icon from list view
   - Delete functionality available in edit modal

3. **Benefits**
   - More consistent UI between system and user prompts
   - Cleaner interface with less visual clutter
   - Better use of limited sidebar space
   - Simplified interaction patterns

### Technical Details:
- Both managers now use Radio components for selection
- Edit icons positioned inline with radio buttons (14px size)
- Delete functionality consolidated into edit modals
- Removed redundant visual elements (badges, extra icons)

## January 25, 2025 - Earlier UI Improvements and Bug Fixes

### UI Fixes and Enhancements:

1. **Fixed Project Modification Cancel Button**
   - Cancel button in project settings now properly resets values
   - Restores original project name and description on cancel
   - No longer leaves unsaved changes

2. **Restored Chat Window Icons**
   - Microphone icon properly restored using microphone.svg
   - Send button now uses Material-UI SendIcon (arrow icon)
   - Stop button uses Material-UI StopIcon during generation
   - Proper visual feedback for different states

3. **Sidebar Width Increased**
   - Changed from w-64 (256px) to w-80 (320px) 
   - Added 64px more space for better prompt menu display
   - Reduces text cramping in system/user prompt panels

### Technical Details:
- Added missing onClick handler to project settings cancel button
- Updated Icon component mapping to include microphone icon
- Imported Material-UI icons for send/stop functionality
- Changed Tailwind class from w-64 to w-80 in MainLayout

## January 25, 2025 - Icon Replacements and UI Consistency

### Icon Standardization Complete:
Replaced all text/emoji symbols with proper SVG icons throughout the application

1. **Add Icons (add.svg)**
   - Replaced "Add Prompt" buttons with icon-only + tooltip in UserPromptManager
   - Replaced "Add Prompt" buttons with icon-only + tooltip in SystemPromptManager
   - Updated "+ Create Project" button in ProjectListView

2. **Close Icons (close.svg)**
   - Updated UserPromptModal close button
   - Updated SystemModelsPanel close button

3. **Delete/Trash Icons (trash.svg)**
   - Fixed Icon component mapping (changed 'delete' to 'trash')
   - Updated delete buttons in UserPromptManager
   - Updated delete buttons in SystemPromptManager
   - Updated delete button in UserPromptModal

4. **Refresh Icons (refresh.svg)**
   - Updated refresh buttons in SystemModelsPanel
   - Added tooltips for better UX

5. **Edit Icons (userEdit.svg)**
   - Updated edit buttons in UserPromptManager
   - Updated edit buttons in SystemPromptManager

### Benefits:
- ✅ Consistent visual language across the application
- ✅ Reduced text clutter in UI
- ✅ Better space utilization with icon-only buttons
- ✅ Improved accessibility with tooltips
- ✅ Aligned with design system using SVG assets in public/icons

### Technical Details:
- Used existing Icon component with tooltip support
- Maintained consistent icon sizes (16-24px based on context)
- All icons use hover effects and proper color theming

## January 25, 2025 - Embedding Service & Visual Polish

### Major Accomplishments:

1. **Real Embedding Service Implementation ✅**
   - Replaced mock embeddings with sentence-transformers
   - Model: all-mpnet-base-v2 (768-dimensional embeddings)
   - GPU acceleration with CUDA for <100ms generation
   - Integrated with vector store and document processing
   - Fixed broken search_chat_context function

2. **Visual Interface Overhaul ✅**
   - Replaced ALL emoji and Material-UI icons with custom SVGs
   - Created reusable Icon component with tooltip support
   - Implemented consistent yellow scrollbar styling globally
   - Icon mappings: file.svg, settings.svg, add.svg, etc.
   - Added hover effects and visual feedback

3. **Backend Integration Fixes**
   - Fixed chat context search with direct vector store integration
   - Added embedding service singleton pattern
   - Implemented graceful fallback to mock embeddings
   - Async/await patterns for non-blocking operations

### Technical Details:
- **Embedding Model**: sentence-transformers/all-mpnet-base-v2
- **Vector Dimensions**: 768 (normalized embeddings)
- **GPU Support**: CUDA-enabled for RTX 4090 utilization
- **Icon System**: SVG-based with public asset serving
- **Scrollbar CSS**: Global styles with webkit customization

### Next Steps:
- Test document uploads with real embeddings
- Implement Phase 2: Document Processing Enhancement
- Add hierarchical document structure preservation
- Optimize batch embedding generation

## January 24, 2025 - Production Database Implementation & UI Enhancements

### Major Accomplishments:
1. **Personal Profiles Database Integration**
   - Created `personal_profiles` table with privacy settings
   - Migrated from localStorage to PostgreSQL
   - Added user_id based authentication
   - Implemented soft delete and default profile management
   - Added team sharing capabilities

2. **User Preferences System**
   - Created `user_preferences` table for per-project settings
   - Stores active prompts, documents, and UI preferences
   - Tracks preferred models per project
   - Enables persistent context across sessions

3. **Message Context Tracking**
   - Created `message_contexts` table for audit trail
   - Tracks all context used for each AI response
   - Stores model settings, prompts, and documents used
   - Links to personal profiles used in generation

4. **API Endpoints Created**
   - `/api/personal-profiles/` - Full CRUD for profiles
   - `/api/preferences/` - User preferences management
   - Automatic migration from localStorage on first use
   - Privacy controls and team sharing options

5. **Frontend Updates**
   - PersonalProfilesModal now uses database
   - Added loading states and error handling
   - Automatic migration from localStorage
   - Real-time sync across browser tabs

### Technical Implementation:
- **Database Models**: SQLAlchemy with PostgreSQL/pgvector
- **Privacy**: User-scoped queries with team sharing options
- **Migration**: Automatic localStorage → DB migration
- **Performance**: Async API calls with proper error handling

### Benefits:
- ✅ Profiles sync across all devices/browsers
- ✅ Persistent storage with backups
- ✅ Team collaboration features
- ✅ Full audit trail of AI interactions
- ✅ Context preferences per project

### Additional Improvements:
1. **System Prompts Implementation**
   - Added default assistant prompt for all models
   - Added specialized DeepSeek Coder prompt
   - Auto-activation based on selected model
   - Stored as user prompts with "System:" prefix

2. **UI/UX Enhancements**
   - Removed large purple SystemPromptIndicator box
   - Added inline indicators (orange for system, gray for user prompts)
   - PersonalProfilesModal redesigned with yellow color scheme
   - Removed "New Profile" default text
   - Added role field with clear labeling
   - Removed address field, replaced with "+ Add Field" button
   - Changed instruction banner to blue (rgb(59, 130, 246))
   - All text made readable with proper contrast

3. **Model Management Fixes**
   - Fixed model restart functionality with proper unload
   - Added Llama 70B NIM model to chat selector
   - System prompts now properly activate with model changes

### Next Steps:
- Continue improving UI/UX based on user feedback
- Implement remaining context control features
- Add more sophisticated prompt management

## January 18, 2025 - Streaming Architecture & Model Management

### BREAKING: Complete Streaming Implementation 
Successfully implemented Server-Sent Events (SSE) for all model responses with visual feedback.

### What Was Fixed:
1. **Streaming Infrastructure**
   - FastAPI SSE endpoints with proper async generators
   - Frontend EventSource integration for all services
   - Typewriter effect showing tokens as they arrive
   - Proper cleanup and error handling

2. **Model Service Updates**
   - Ollama: Native streaming support preserved
   - NIM: Implemented token buffering for streaming simulation
   - Transformers: Added word-by-word streaming
   - NeMo: Streaming wrapper for compatibility

3. **UI Enhancements**
   - Real-time token display with typewriter animation
   - Loading states during model switching
   - Proper error handling with user feedback
   - Smooth transitions between messages

### Technical Implementation:
- EventSource API for browser compatibility
- Async generators throughout the backend
- Proper memory management for long responses
- Token parsing for natural display

This provides a much better user experience, especially for the 40-70 second Llama 70B responses!

## January 18, 2025 - Admin Panel & Model Integration

### Major Update: Admin Settings Panel
Created comprehensive admin interface for model management and system configuration.

### Key Features:
1. **Model Status Overview**
   - Real-time status for all 5 models (4 LLMs + embeddings)
   - Visual indicators: green (active), gray (inactive), red (error)
   - One-click load/unload functionality
   - Automatic VRAM management

2. **Quick Model Switching**
   - Production models with clear descriptions
   - Solo mode handling for Llama 70B
   - Automatic embedding service management
   - Loading states during transitions

3. **System Information**
   - VRAM usage tracking (X/24 GB)
   - Active model display
   - Service health monitoring
   - Performance metrics

### Model Profiles:
- **Qwen 2.5 32B**: Default with full document support
- **Llama 3.1 70B**: Solo mode for deep reasoning
- **Mistral-Nemo 12B**: Quick responses
- **DeepSeek Coder V2 16B**: Specialized coding
- **NV-EmbedQA**: Always-on embeddings (except solo mode)

### Technical Details:
- Redux integration for state management
- Async API calls with proper error handling
- Automatic model unloading based on VRAM
- Protected embedding service (except solo mode)

## January 12, 2025 - User & System Prompts Implementation

### Complete Prompt System Overhaul
Implemented comprehensive prompt management system with visual indicators and database persistence.

### System Prompts:
1. **Database Implementation**
   - New `system_prompts` table with model associations
   - Auto-activation based on selected model
   - Version tracking and audit fields
   - Seeded with production prompts

2. **Default Prompts Created**
   - General assistant prompt (all models)
   - DeepSeek Coder specialized prompt
   - Model-specific behavior customization
   - Token-optimized instructions

3. **Visual Integration**
   - Orange indicators for active system prompts
   - Inline display next to model selector
   - Hover tooltips showing prompt preview
   - Clear visual hierarchy

### User Prompts:
1. **Enhanced Management**
   - Create, edit, delete functionality
   - Project-specific and global prompts
   - Activation/deactivation toggles
   - Search and filter capabilities

2. **UI Improvements**
   - Dedicated prompt panels in chat view
   - Gray indicators for active user prompts
   - Drag-and-drop reordering (planned)
   - Quick access shortcuts

### Integration:
- Prompts automatically included in chat context
- Proper ordering: System → User → Project → Chat
- Token counting for context management
- Performance optimized queries

## January 5, 2025 - Multi-Model Production Architecture

### Complete Model Reconfiguration
Transitioned from experimental to production-ready model selection.

### Final Model Lineup:
1. **Qwen 2.5 32B** (19GB) - New default model
   - Superior document understanding
   - 32k context window
   - Runs with embeddings active

2. **Llama 3.1 70B** (22GB) - Solo mode only
   - Maximum reasoning capability
   - TensorRT optimized via NIM
   - Requires all other models unloaded

3. **Mistral-Nemo 12B** (7GB) - Quick responses
   - Fast general-purpose model
   - 128k context efficiency
   - Good for simple queries

4. **DeepSeek Coder V2 16B** (9GB) - Coding specialist
   - Optimized for programming
   - Self-aware development mode
   - Integrated with codebase context

5. **NV-EmbedQA-E5-V5** (2GB) - Always-on embeddings
   - Enterprise-grade semantic search
   - Active with all models except Llama 70B
   - Real-time document processing

### Intelligent VRAM Management:
- Model orchestrator with priority scoring
- LRU cache with 1-hour timeout
- Automatic unloading based on memory pressure
- Solo mode enforcement for Llama 70B
- Protected status for embedding service

### Service Architecture:
- Unified LLM service with intelligent routing
- Health checks with 3-retry resilience
- Graceful failover between services
- Comprehensive error handling

This configuration maximizes the RTX 4090's capabilities while providing flexibility for different use cases.

## January 25, 2025 - UI Enhancement and Icon System Updates

### Icon System Overhaul
Replaced Material-UI icons with custom SVG icons throughout the application for consistency and better visual design.

### Icon Updates:
1. **Component-wide Icon Replacement**
   - Replaced all Add icons with add.svg
   - Replaced all Close/X icons with close.svg
   - Replaced Delete icons with trash.svg
   - Replaced Refresh icons with refresh.svg
   - Added copy.svg for chat message copy functionality
   - Added proper Icon component usage across all components

2. **Updated Components**
   - UserPromptManager: Changed to radio buttons with icon support
   - SystemPromptManager: Removed badges, repositioned edit icons
   - SystemPromptModal: Fixed imports and styling issues
   - SystemModelsPanel: Updated refresh and close icons
   - ElegantSystemModelsPanel: Replaced emoji icons with SVG icons
   - ProjectListView: Updated all action icons
   - ChatView: Restored microphone and send icons, added copy.svg

### UI Improvements:
1. **System Prompt Modal Styling**
   - All field labels now use gold color (promptColors.gold)
   - Borders changed to white for better contrast
   - Disabled field text opacity increased to 0.7 for readability
   - Added proper spacing to prevent dialog content cutoff
   - Reduced multiline field from 12 to 10 rows

2. **Project Management**
   - Fixed cancel button to properly exit settings view
   - Save button now returns to overview after saving
   - Improved workflow for project modifications

3. **Layout Changes**
   - Sidebar width increased from w-64 to w-80 (256px to 320px)
   - Better accommodation for prompt management panels

4. **Edit Icons Enhancement**
   - Increased edit icon size by 50% (from 14 to 21 pixels)
   - Better visibility and easier clicking for prompt editing

### Hover Effects Implementation
Added comprehensive hover effects for all icons across the application:

1. **Global Icon Hover System**
   - Base transition effects in Icon component
   - Brightness, scale, and opacity adjustments
   - Context-aware hover behaviors

2. **Specialized Hover Effects**
   - Sidebar icons: Slide and scale effect
   - Modal close buttons: 90-degree rotation
   - Refresh icons: 180-degree rotation animation
   - File icons: Drop shadow effect
   - Gold icons: Glow effect with drop shadow

3. **CSS Architecture**
   - Global styles in index.css for Material-UI integration
   - Context-specific styles in app.css
   - Smooth cubic-bezier transitions
   - Disabled state handling

This update significantly improves the visual feedback and user experience throughout the application.

### Chat-Specific Context Settings Implementation
Implemented comprehensive chat-specific settings that are remembered per chat thread:

1. **Context Control Hover Effects**
   - Added smooth hover animations to all prompt control buttons
   - Scale transform (1.05x) on hover
   - Color-matched shadow effects for each button type
   - Border highlighting on hover
   - Smooth transitions (200ms duration)

2. **Selectable System and User Prompts**
   - System prompt now toggleable per chat
   - User prompt activation/deactivation per chat
   - Visual feedback with proper enabled/disabled states
   - Consistent with context button behavior
   - User prompt button always visible (disabled when no prompt selected)

3. **Chat Settings State Management**
   - New `chatSettingsSlice` Redux store
   - Stores settings per chat ID
   - Settings include:
     - Context mode
     - System prompt enabled/disabled
     - User prompt enabled/disabled
     - Active user prompt ID and name
     - Project prompt, global data, and document settings
   - Automatic initialization with default settings

4. **Sidebar Integration**
   - User prompt activation from sidebar updates chat settings
   - System prompt changes reflect in active chat
   - Bidirectional sync between sidebar and chat controls
   - Radio button selection persists per chat

5. **Backend Schema and API Updates**
   - Added `ChatContextSettings` model
   - Updated chat schemas to include context settings
   - Fixed user prompt activation endpoint to support both global and project-specific prompts
   - Resolved 400 Bad Request error with proper activation logic
   - Settings persist with chat data (ready for API integration)

6. **User Prompt Activation Fix**
   - Updated backend to handle global prompt activation
   - Added `activate_global_prompt` method to repository
   - Proper error handling for missing prompts
   - Radio button state now correctly persists

## January 25, 2025

### Fixed pgvector Document Search Issue
Resolved critical issue where documents attached to projects weren't being used in chat context due to incorrect embedding storage:

1. **Problem Identification**
   - Documents were processed and chunks created, but semantic search returned no results
   - Embeddings were stored as JSON text strings instead of pgvector vector type
   - DocumentChunk model used Text column instead of Vector column type

2. **Database Migration**
   - Created migration script to convert embedding column from Text to Vector(768)
   - Migration handles existing embeddings by parsing JSON and converting to pgvector format
   - Added proper pgvector index for efficient similarity search
   - Script: `backend/app/db/migrations/fix_embedding_column.py`

3. **Model Updates**
   - Updated DocumentChunk model to use `Vector(768)` column type
   - Added pgvector SQLAlchemy import
   - Fixed embedding storage in `process_document_background`

4. **Vector Store Improvements**
   - Updated `update_document_embedding` to work with pgvector directly
   - Fixed similarity search to properly format query vectors
   - Removed unnecessary JSON string conversions

5. **Testing Tools**
   - Created `run_embedding_migration.py` for easy migration execution
   - Created `test_pgvector_search.py` to verify pgvector functionality
   - Added comprehensive error handling and logging

This fix enables proper semantic search functionality, allowing the AI assistant to use project documents in chat responses as intended.

### Implemented Document Context in Chat Responses
Connected the document retrieval system to the chat interface so documents are actually used:

1. **Backend Integration**
   - Added document context fields to ChatGenerateRequest schema
   - Implemented semantic search in generate_chat_response_stream endpoint
   - Retrieves top 5 most relevant document chunks based on user query
   - Supports both project-scoped and global document search
   - Adds relevant chunks to chat context with similarity scores

2. **Frontend Updates**
   - Updated ChatGenerateRequest interface with document context settings
   - Modified App.tsx to pass chat settings to the streaming API
   - Connected Redux chat settings to the API calls
   - Document context toggles now control actual behavior

3. **How It Works**
   - When "Project Documents Enabled" is on, searches project documents
   - When "Global Data Enabled" is on, searches all documents system-wide
   - User's message is converted to embedding vector
   - Semantic search finds most relevant chunks (similarity > 0.3)
   - Relevant chunks are added to the chat context
   - AI uses this context to provide informed responses

The AI assistant can now access and use document content when answering questions, making it truly context-aware.

### Identified Redux/Navigation Timing Issue
Discovered recurring pattern of crashes when accessing chat settings:

1. **Symptoms**
   - "Cannot read properties of undefined" errors when navigating to chats
   - Particularly after deleting chats or rapid navigation
   - Redux state not initialized before component renders

2. **Root Cause**
   - Navigation state (activeChatId) and Redux state (currentChatId) are separate
   - Components render before Redux updates complete
   - Race condition: Navigation → Render → Redux (should be Navigation → Redux → Render)

3. **Current Mitigation**
   - Fixed property name mismatch (settingsByChat vs chats)
   - Added setCurrentChat dispatch when loading chat messages
   - Added defensive null checks with optional chaining
   - This is a "good enough" fix but not architecturally sound

4. **Proper Solution (Future)**
   - Unify navigation state into Redux as single source of truth
   - Add middleware to block navigation until Redux is ready
   - Implement proper loading states in components
   - This would require significant refactoring of navigation system

This issue is documented in implementation.md for future architectural improvements.

### Fixed SQLAlchemy Session Issue in Document Retrieval
The document context feature was failing with "Instance is not bound to a Session" error:

1. **Root Cause**: Accessing `chat.project_id` inside async generator after session closed
2. **Fix**: Capture `project_id_for_context` before entering generator
3. **Result**: Document retrieval now works perfectly!

### Discovered Embedding Model Mismatch
Found that we're using sentence-transformers instead of the superior NVIDIA NIM embeddings:

1. **Current State**: 
   - Using: sentence-transformers/all-mpnet-base-v2 (109M params)
   - Available: NVIDIA NV-EmbedQA-E5-V5 (335M params, already running!)

2. **Impact**: Missing better semantic understanding (e.g., motorcycle→vehicle)

3. **Planned Improvements**:
   - Make embedding models visible in UI
   - Switch to NIM embeddings as default
   - Keep sentence-transformers as fallback option

### Identified File Active/Inactive Toggle Issue
The active/inactive toggle doesn't actually prevent files from being searched:

1. **Conceptual Confusion**: What does "inactive" mean if files are still searchable?
2. **Proposed Solution**: Remove toggle, keep only attach/detach
3. **Benefit**: Clearer mental model - attached files are searchable, detached aren't

## 1/26/2025

### Updated Embedding Dimensions for NIM (768 → 1024)
Updated all embedding dimension references from 768 to 1024 to match NVIDIA NIM embeddings:

1. **Files Updated**:
   - `/backend/app/rag/vector_store.py`: EMBEDDING_DIMENSIONS constant
   - `/backend/app/api/endpoints/system.py`: Fallback embedding dimension and model info display
   - `/backend/app/services/embedding_service.py`: Documentation comments
   - `/backend/app/db/models/document.py`: DocumentChunk embedding column (Vector(1024))

2. **Impact**: 
   - Ensures consistency with NIM's 1024-dimensional embeddings
   - Database schema now correctly reflects the embedding size
   - Note: This requires a database migration to update existing vectors

These settings are now uniquely tied to each chat thread and will be remembered as users navigate between different chats within projects.