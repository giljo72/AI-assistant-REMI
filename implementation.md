# AI Assistant: Next-Gen Architecture & Implementation Plan (Updated)

## Project Vision

The AI Assistant project is migrating from a Gradio-based UI to a more scalable and responsive FastAPI + React architecture while maintaining its core philosophy:

* 100% local processing for complete privacy and data ownership
* Project-centered containment for intuitive knowledge management
* Tiered memory system with prioritized document retrieval
* Comprehensive document processing with hierarchical indexing using NeMo
* Modern, responsive interface with adaptive context controls
* Hardware-optimized performance (RTX 4090, Ryzen 7800X3D, 64GB RAM)

This architecture shift preserves all existing functionality while delivering:

* Enhanced performance through TensorRT optimization
* Superior user experience with reactive UI components
* Prioritized document retrieval for improved context relevance
* Multiple reasoning modes optimized for local hardware
* Better maintainability through clear code separation
* Improved development workflow and debugging

## Project-Centered Containment Architecture

The core architectural principle of this implementation is "containment by default, expansion by choice":

### 1. Containment Principle
* Projects are self-contained knowledge environments
* Each project maintains its own set of chats and documents
* Knowledge is contained within project boundaries by default
* Documents are attached to specific projects for context
* Project files are directly accessible through the Project File Manager

### 2. Selective Expansion
* Users can explicitly expand beyond project boundaries when needed
* Clear navigation paths allow browsing global files through the "Browse Global Files" button
* Search functionality in the Main File Manager provides access to the entire document repository
* File attachments from the global repository to projects are clearly indicated

### 3. Implementation Considerations
* Database schema designed to reflect containment relationships
* UI components respect project boundaries with clear visual indicators
* Navigation between project context and global context is explicit and user-controlled
* State management preserves project context across views
* File status indicators show whether files are linked to projects

### 4. Navigation Flow
* From Project Manager to Project File Manager: Shows only files attached to the current project
* From Project File Manager to Main File Manager: Shows all files in the system with "Browse Global Files" button
* From Main File Manager, search functionality leads to Search Results
* Search Results allows selecting and attaching files back to the project

This approach delivers several key benefits:
* Better performance through limited context scope
* More intuitive organization matching real-world workflows
* Greater control over relevance and priority of information
* Clearer mental model for users to understand system behavior
* Explicit navigation between containment and expansion modes

## Frontend Build System Update

The React frontend will be built using Vite rather than Create React App (react-scripts). This decision brings several advantages:

* **Faster Development**: Vite provides near-instantaneous hot module replacement
* **Modern Architecture**: Uses native ES modules for better performance
* **Cleaner Dependencies**: Fewer deprecation warnings and legacy dependencies
* **Better TypeScript Integration**: Improved type checking and editor integration
* **Smaller Bundle Size**: More efficient code splitting and asset optimization

This change enhances developer experience without affecting the planned component architecture or design specifications.

## System Architecture

```
┌───────────────────┐     ┌─────────────────────┐     ┌───────────────────┐
│                   │     │                     │     │                   │
│   REACT FRONTEND  │◄────┤   FASTAPI BACKEND   │◄────┤  DATABASE LAYER   │
│   (Vite SPA)      │     │   (API Services)    │     │  (PostgreSQL +    │
│                   │─────►                     │─────►   pgvector)       │
│                   │     │                     │     │                   │
└───────────────────┘     └─────────────────────┘     └───────────────────┘
         │                          │                          │
         │                          │                          │
         ▼                          ▼                          ▼
┌───────────────────┐     ┌─────────────────────┐     ┌───────────────────┐
│  UI COMPONENTS    │     │ BUSINESS LOGIC      │     │ DATA STORAGE      │
│ - Project Sidebar │     │ - Service Layer     │     │ - Documents       │
│ - Chat Interface  │     │ - API Endpoints     │     │ - Embeddings      │
│ - Document Mgmt   │     │ - RAG Processing    │     │ - Projects/Chats  │
│ - Context Controls│     │ - LLM Integration   │     │ - User Settings   │
└───────────────────┘     └─────────────────────┘     └───────────────────┘
```

## Key Architecture Enhancements

### Project-Centered Containment
* Projects serve as primary organizational containers
* Each project maintains its own chats and attached documents
* Project-specific settings including custom prompts
* UI clearly shows current project context
* Database schema reflects containment relationships
* Vector retrieval respects project boundaries

### Tiered Memory System
* Default: Project-only knowledge (documents and chats)
* Optional: Prioritized project knowledge + global knowledge
* Optional: All knowledge equally weighted
* Visual indicators for active memory scope
* Performance indicators for different memory settings
* Context depth slider for fine-tuning

### NVIDIA Integration
* NeMo Document AI for superior document understanding
* TensorRT optimization for LLM inference acceleration
* Hardware-aware optimization for maximum RTX 4090 utilization
* Hierarchical document processing with structure preservation
* Native or Docker-based deployment on Windows

### Document Prioritization System
* Hierarchical document indexing for improved context
* Project-attached documents receive special treatment
* Prioritized ranking in vector search results
* Enhanced context utilization for deeper understanding
* Visual indicators showing document relevance and priority

### Adaptive Context Controls
* Unified context control panel with preset modes
* Document source selection with prioritization options
* Memory scope controls for chat history utilization
* Reasoning depth adjustment for balancing speed vs thoroughness

### Hardware-Optimized Performance
* CUDA-accelerated vector operations for RTX 4090
* Model optimization for 30-35B parameter models
* Memory management for 64GB RAM utilization
* Pipeline parallelism for CPU/GPU task distribution

### Future Extensibility Framework
* Abstraction layer for reasoning providers
* Pluggable architecture for external API integration
* Privacy-preserving data gateway for external services
* Web search integration capability
* Clear visual indicators for local vs. external processing

## UI-First Implementation Strategy

The project follows a UI-first approach with progressive enhancement to ensure the interface vision is fully realized before adding complex backend functionality:

1. UI Shell & Navigation: Implement complete UI mockups with static data
2. Basic Interaction Layer: Add interactivity using mock data
3. Core Backend Services: Implement essential backend functionality
4. Integration & Enhancement: Connect advanced features and optimizations
5. Optimization & Refinement: Polish the user experience based on feedback

This approach ensures a consistent and polished user experience throughout development.

## Directory Structure

```
F:/Assistant/                        # Project root
├── backend/                         # FastAPI backend
│   ├── app/
│   │   ├── api/                     # API endpoints
│   │   ├── core/                    # Core application modules
│   │   │   ├── mock_nemo/           # Mock NeMo implementation
│   │   │   └── ...
│   │   ├── db/                      # Database models/repositories
│   │   └── main.py                  # Main FastAPI entry point
│   ├── data/                        # Data storage
│   └── .env                         # Environment variables
│
├── frontend/                        # React frontend (Vite-based)
│   ├── public/                      # Static assets
│   ├── src/
│   │   ├── components/              # Reusable UI components
│   │   │   ├── chat/                # Chat-related components
│   │   │   │   ├── ChatView.tsx
│   │   │   │   ├── ContextStatusIndicators.tsx
│   │   │   │   ├── UserPromptIndicator.tsx
│   │   │   │   ├── UserPromptManager.tsx
│   │   │   │   └── UserPromptsPanel.tsx
│   │   │   ├── document/            # Document-related components
│   │   │   │   └── DocumentView.tsx
│   │   │   ├── file/                # File management components
│   │   │   │   ├── MainFileManager.tsx
│   │   │   │   ├── ProjectFileManager.tsx
│   │   │   │   └── SearchFilesResults.tsx
│   │   │   ├── layout/              # Layout components
│   │   │   │   └── MainLayout.tsx
│   │   │   ├── modals/              # Modal components
│   │   │   │   ├── AddChatModal.tsx
│   │   │   │   ├── AddProjectModal.tsx
│   │   │   │   ├── ContextControlsPanel.tsx
│   │   │   │   ├── TagAndAddFileModal.tsx
│   │   │   │   └── UserPromptModal.tsx
│   │   │   ├── project/             # Project-related components
│   │   │   │   └── ProjectManagerView.tsx
│   │   │   └── sidebar/             # Sidebar components
│   │   │       └── ProjectSidebar.tsx
│   │   ├── store/                   # Redux state management
│   │   │   ├── projectSettingsSlice.ts
│   │   │   ├── userPromptsSlice.ts
│   │   │   └── index.ts
│   │   ├── App.tsx                  # Main React component
│   │   └── main.tsx                 # Vite entry point
│   ├── package.json                 # Frontend dependencies
│   ├── tailwind.config.js           # Tailwind CSS configuration
│   └── tsconfig.json                # TypeScript configuration
│
├── scripts/                         # Utility scripts
│   ├── check_system.py              # System verification script
│   └── setup_environment.py         # Environment setup script
│
├── venv_nemo/                       # Python virtual environment for NeMo
├── start_services.bat               # Script to start all services
├── stop_services.bat                # Script to stop all services
├── Devlog.md                        # Development log
├── implementation.md                # Implementation plan (this file)
├── Readme.MD                        # Project overview
└── Scope.md                         # Project scope
```

## Component Interaction Diagram With Containment
```
┌──────────────────────────────────────────────────────────────┐
│                         User Interface                       │
└─────────────────────────────┬────────────────────────────────┘
                              │
┌─────────────────────────────▼────────────────────────────────┐
│                        Project Context                       │
└─────────────────────────────┬────────────────────────────────┘
                              │
           ┌──────────────────┴────────────────┐
           │                                   │
┌──────────▼───────────┐             ┌─────────▼─────────┐
│  Project-Specific    │             │  Global Knowledge │
│  Knowledge Container │             │  (Optional)       │
└──────────┬───────────┘             └─────────┬─────────┘
           │                                   │
  ┌────────┴───────┐                  ┌────────┴───────┐
  │                │                  │                │
┌─▼─────┐    ┌──────▼──┐            ┌─▼───────┐  ┌─────▼───┐
│Project│    │Project  │            │All Other│  │All Other│
│Chats  │    │Documents│            │Chats    │  │Documents│
└───────┘    └─────────┘            └─────────┘  └─────────┘
```

## Core Features Implementation Plan (Updated)

### Phase 1: UI Shell & Navigation (Completed)
- [x] Setup React application with TypeScript, Vite, and Redux
- [x] Create layout components (sidebar, header, main content)
- [x] Implement project management UI (list, create, edit, delete)
- [x] Develop chat interface with static mock data
- [x] Build document management UI with mock data
- [x] Create settings panels and performance monitors
- [x] Implement context controls UI components
- [x] Implement navigation flow between all screens
- [x] Design and implement UI theme with navy/gold color scheme
- [x] Create responsive layouts for different screen sizes

### Phase 2: Project-Centered Components (Implemented)
- [x] Implement project containment UI architecture
- [x] Create project modal dialogs (add, modify, delete)
- [x] Build project-specific chat views and management
- [x] Implement document attachment to projects
- [x] Create project-specific settings and configuration
- [x] Implement visual indicators for project context
- [x] Build project file manager with containment
- [x] Create project-specific chat list
- [x] Implement project-specific sidebar behavior

### Phase 3: User Management & Prompts (Implemented)
- [x] Create UserPromptModal for adding/editing user prompts
- [x] Build UserPromptManager for managing prompt collections
- [x] Implement UserPromptIndicator for active prompt display
- [x] Create UserPromptsPanel for sidebar integration
- [x] Set up Redux store with userPromptsSlice
- [x] Implement prompt activation/deactivation functionality
- [x] Create proper UI flow for prompt management
- [x] Integrate user prompts with chat interface

### Phase 4: Context Controls & Memory System (In Progress)
- [x] Implement ContextControlsPanel component
- [x] Create ContextStatusIndicators for quick toggle access
- [x] Build context controls with preset modes
- [x] Implement document source selection (project vs all)
- [x] Arrange controls in sidebar and chat interface
- [x] Create visual indicators for context state
- [ ] Implement context control state management with backend
- [ ] Connect memory system to RAG implementation (pending backend)

### Phase 5: File Management System (Implemented)
- [x] Create ProjectFileManager component
- [x] Build MainFileManager for global file access
- [x] Implement SearchFilesResults for file discovery
- [x] Create TagAndAddFileModal for file uploads
- [x] Build file status indicators (linked, processed)
- [x] Implement file attachment/detachment functionality
- [x] Create navigation flow between file components
- [x] Add drag-and-drop file upload capabilities

### Phase 6: Basic Backend Services (To Be Implemented)
- [ ] Setup FastAPI application structure
- [ ] Implement database models with containment relationships
- [ ] Create repositories for project-centered data access
- [ ] Build API endpoints for project-centered CRUD operations
- [ ] Setup authentication and security (if needed)
- [ ] Configure logging and error handling
- [ ] Implement service layer with service factory
- [ ] Create document storage system with project associations

### Phase 7: Backend-Frontend Integration (To Be Implemented)
- [ ] Connect React frontend to FastAPI backend
- [ ] Implement API service clients
- [ ] Replace mock services with real API calls
- [ ] Create error handling for API responses
- [ ] Implement real-time updates where needed
- [ ] Develop proper state management with API data
- [ ] Create loading states and indicators
- [ ] Test basic CRUD operations end-to-end

### Phase 8: NVIDIA Integration (To Be Implemented)
- [ ] Implement TensorRT optimization for models
- [ ] Integrate NeMo Document AI components
- [ ] Configure Docker containers for NeMo (if needed)
- [ ] Setup CUDA optimizations for vector operations
- [ ] Create abstraction layers for hardware components
- [ ] Implement hardware monitoring and profiling
- [ ] Test performance on target hardware

### Phase 9: Document Processing & RAG (To Be Implemented)
- [ ] Implement hierarchical document processors with NeMo
- [ ] Create multi-level chunking strategies
- [ ] Implement metadata extraction and storage
- [ ] Setup structure preservation for document context
- [ ] Implement project prioritization for retrieval
- [ ] Create document context visualization
- [ ] Test RAG functionality with prioritization
- [ ] Connect RAG system to chat interface

### Phase 10: Reasoning Capabilities (To Be Implemented)
- [ ] Implement reasoning mode API endpoints
- [ ] Create prompt templates for different reasoning modes
- [ ] Implement chain-of-thought prompting for expert mode
- [ ] Connect reasoning mode UI controls to backend
- [ ] Implement GPU monitoring for reasoning operations
- [ ] Test reasoning capabilities with different modes
- [ ] Optimize for 30-35B models with TensorRT

### Phase 11: Voice Integration (To Be Implemented)
- [ ] Implement Whisper API endpoint
- [ ] Connect voice recording component to backend
- [ ] Implement transcript editing
- [ ] Create voice-to-text workflow
- [ ] Optimize voice processing for hardware
- [ ] Test voice functionality

### Phase 12: Testing and Refinement (To Be Implemented)
- [ ] Comprehensive testing of all features
- [ ] Performance optimization for target hardware
- [ ] UI/UX refinement based on testing
- [ ] Bug fixing and issue resolution
- [ ] Documentation updates and enhancements
- [ ] User workflow testing
- [ ] Performance benchmarking

## UI Design Elements

### Context Controls
```
┌─ CONTEXT CONTROLS ─────────────────────────────────────┐
│                                                        │
│  Mode: [Standard ▼]                                    │
│        • Project Focus                                 │
│        • Deep Research                                 │
│        • Quick Response                                │
│        • Custom                                        │
│                                                        │
│  When in Custom mode:                                  │
│  ├────────────────────────────────────────────────────┤
│                                                        │
│  Context Depth: ├──────●──┤                            │
│               Concise   Comprehensive                  │
│                                                        │
│  Sources: ☑ Project Docs (Priority)                    │
│           ☑ Project Chats                              │
│           ☐ All Documents                              │
│           ☐ All Conversations                          │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### User Prompts
```
┌─ USER PROMPTS ─────────────────────────────────────────┐
│                                                        │
│  ● Active Prompt: [Research Assistant]                 │
│                                                        │
│  Saved Prompts:                                        │
│  ├────────────────────────────────────────────────────┤
│                                                        │
│  ○ Research Assistant                                  │
│  ○ Code Helper                                         │
│  ○ Writing Assistant                                   │
│                                                        │
│  [+ Add Prompt]                                        │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### Color Scheme
* Dark background (#080d13)
* Gold accents (#FFC000)
* Neutral grays for content areas
* High contrast for readability
* Visual indicators for project context
* Visual indicators for reasoning modes

### Layout
* Project sidebar with collapsible sections
* Main content area for chat/documents
* Modal dialogs for forms and confirmations
* Responsive design for different screen sizes
* Context controls panel with collapsible state
* Project containment visualization
* User prompts panel in sidebar

## Technology Stack

### Frontend
* React (UI library)
* TypeScript (type-safe JavaScript)
* Vite (build tool)
* Redux Toolkit (state management)
* Axios (HTTP client)
* React Router (routing)
* Tailwind CSS (styling)
* Material UI (component library)

### Backend
* FastAPI (Python web framework)
* SQLAlchemy (ORM)
* PostgreSQL with pgvector (vector database)
* Pydantic (data validation)
* NeMo (AI model integration)
* TensorRT (NVIDIA optimization)
* NeMo Document AI (document processing)
* CUDA libraries for optimization

## Development Workflow

### Setup Environment
* Clone repository
* Create virtual environment
* Install dependencies
* Set up database
* Configure hardware-specific settings
* Setup NeMo and TensorRT components

### Run Development Servers
* Start FastAPI backend: `cd backend && python -m uvicorn app.main:app --reload`
* Start React frontend: `cd frontend && npm run dev`
* Start Docker containers if needed for NeMo
* Connect to Ollama locally with appropriate model
* Monitor hardware utilization

## Progress Tracking

### Completed Components
- [x] MainLayout.tsx - Main application layout
- [x] ProjectSidebar.tsx - Project sidebar with mock data
- [x] ChatView.tsx - Chat interface
- [x] DocumentView.tsx - Document management view
- [x] AddProjectModal.tsx - Modal for adding new projects
- [x] ProjectManagerView.tsx - Detailed project management view
- [x] AddChatModal.tsx - Modal for adding chats to projects
- [x] App.tsx - Main application component
- [x] MainFileManager.tsx - Global file management
- [x] ProjectFileManager.tsx - Project-specific file management
- [x] SearchFilesResults.tsx - Search results for files
- [x] TagAndAddFileModal.tsx - Modal for adding file descriptions
- [x] ContextStatusIndicators.tsx - UI for toggling context settings
- [x] ContextControlsPanel.tsx - Comprehensive context settings panel
- [x] UserPromptModal.tsx - Modal for adding/editing user prompts
- [x] UserPromptManager.tsx - Management of user prompts
- [x] UserPromptIndicator.tsx - Indicator for active prompts
- [x] UserPromptsPanel.tsx - Container for user prompts in sidebar

### Next Components to Implement
- [ ] DeleteProjectModal.tsx - Modal for deleting projects
- [ ] ModifyProjectModal.tsx - Modal for modifying project settings
- [ ] DeleteChatModal.tsx - Modal for deleting chats
- [ ] ModifyChatModal.tsx - Modal for modifying chat settings
- [ ] Backend integration components and API clients
- [ ] NeMo and TensorRT integration components

## Responsive Design Improvements

To enhance the responsive design and address font scaling issues:

1. Use Tailwind's responsive utility classes (sm:, md:, lg:, xl:)
2. Implement proper font size scaling for different screen sizes
3. Adjust button sizes in the sidebar for better usability
4. Implement proper spacing in the layout for various device sizes
5. Use rem-based sizing for better scalability
6. Consider creating custom utility classes for consistent typography

## Conclusion

This implementation plan outlines a comprehensive approach to building the AI Assistant with project-centered containment. By following this step-by-step process, we'll create a polished, performant application that respects user privacy while providing powerful AI capabilities tailored to the specified hardware configuration.

The project-centered containment approach provides significant benefits for organization, performance, and user experience. By preserving this core architectural principle throughout the implementation, we'll deliver an intuitive, powerful system that aligns with natural human workflows while providing the flexibility to expand context when needed.