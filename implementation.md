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
│   │   │   ├── endpoints/           # Specific API route modules
│   │   │   │   ├── projects.py      # (To be implemented)
│   │   │   │   ├── chats.py         # (To be implemented)
│   │   │   │   ├── documents.py     # (To be implemented)
│   │   │   │   ├── embeddings.py    # (To be implemented)
│   │   │   │   ├── reasoning.py     # (To be implemented)
│   │   │   │   ├── external.py      # (To be implemented)
│   │   │   │   └── settings.py      # (To be implemented)
│   │   │   └── router.py            # (To be implemented)
│   │   ├── core/                    # Core application modules
│   │   │   ├── config.py            # (To be implemented)
│   │   │   ├── db_interface.py      # (To be implemented)
│   │   │   ├── llm_interface.py     # (To be implemented)
│   │   │   ├── nvidia_interface.py  # (To be implemented)
│   │   │   ├── logger.py            # (To be implemented)
│   │   │   ├── security.py          # (To be implemented)
│   │   │   └── hardware.py          # (To be implemented)
│   │   ├── db/                      # Database models/repositories
│   │   │   ├── models/              # (To be implemented)
│   │   │   └── repositories/        # (To be implemented)
│   │   ├── schemas/                 # (To be implemented)
│   │   ├── services/                # Business logic (To be implemented)
│   │   ├── document_processing/     # Document processing logic (To be implemented)
│   │   ├── rag/                     # RAG implementation (To be implemented)
│   │   ├── reasoning/               # Reasoning capabilities (To be implemented)
│   │   ├── external/                # External integration (To be implemented)
│   │   └── main.py                  # Main FastAPI application entry point
│   ├── static/                      # Static files for backend
│   ├── data/                        # Data storage
│   │   ├── uploads/                 # Document upload storage
│   │   ├── processed/               # Processed documents
│   │   ├── hierarchy/               # Hierarchical document indices
│   │   └── logs/                    # Application logs
│   ├── migrations/                  # Database migrations
│   ├── tests/                       # Backend tests
│   │   ├── test_api/
│   │   ├── test_services/
│   │   ├── test_rag/
│   │   ├── test_reasoning/
│   │   ├── test_nemo/
│   │   └── test_tensorrt/
│   ├── requirements.txt             # Backend dependencies (consolidated)
│   ├── .env                         # Environment variables with NeMo config
│   └── README.md                    # Backend documentation
│
├── frontend/                        # React frontend (Vite-based)
│   ├── public/                      # Static assets
│   ├── src/
│   │   ├── components/              # Reusable UI components
│   │   │   ├── chat/                # Chat-related components
│   │   │   │   ├── ChatView.tsx     # Chat interface (Implemented/Updated)
│   │   │   │   └── ContextStatusIndicators.tsx # Status indicators for context settings (Implemented)
│   │   │   ├── document/            # Document-related components
│   │   │   │   └── DocumentView.tsx # Document management (Implemented)
│   │   │   ├── file/
│   │   │   │    ├── ProjectFileManager.tsx # Project-specific file management (Updated)
│   │   │   │    ├── MainFileManager.tsx   # Global file management (Implemented)
│   │   │   │    └── SearchFilesResults.tsx # Search results for files (Implemented)
│   │   │   ├── layout/              # Layout components
│   │   │   │   └── MainLayout.tsx   # Main application layout (Implemented)
│   │   │   ├── modals/              # Modal components
│   │   │   │   ├── AddProjectModal.tsx      # Add project modal (Implemented)
│   │   │   │   ├── AddChatModal.tsx         # Add chat modal (Implemented)
│   │   │   │   ├── ContextControlsPanel.tsx # Context control settings modal (Implemented)
│   │   │   │   └── TagAndAddFileModal.tsx   # File tagging modal (Updated)
│   │   │   ├── project/             # Project-related components
│   │   │   │   └── ProjectManagerView.tsx  # Project manager view (Implemented)
│   │   │   └── sidebar/             # Sidebar components
│   │   │       └── ProjectSidebar.tsx # Project sidebar (Implemented)
│   │   ├── pages/                   # Application pages
│   │   ├── services/                # API client services
│   │   ├── hooks/                   # Custom React hooks
│   │   ├── store/                   # Redux state management
│   │   ├── utils/                   # Utility functions
│   │   ├── types/                   # TypeScript type definitions
│   │   ├── styles/                  # CSS/styling
│   │   ├── App.tsx                  # Main React component (Modified)
│   │   └── main.tsx                 # Vite entry point
│   ├── index.html                   # HTML entry point
│   ├── package.json                 # Frontend dependencies
│   ├── vite.config.ts               # Vite configuration
│   ├── tsconfig.json                # TypeScript configuration
│   ├── postcss.config.js            # PostCSS configuration for Tailwind
│   ├── tailwind.config.js           # Tailwind CSS configuration (Modified)
│   └── README.md                    # Frontend documentation
│
├── scripts/                         # Utility scripts
│   ├── setup_database.py            # Database initialization
│   ├── check_system.py              # System verification script
│   ├── launch_assistant.py          # Application launcher (to be implemented)
│   ├── stop_assistant.py            # Application termination (to be implemented)
│   ├── optimize_cuda.py             # CUDA optimization script (to be implemented)
│   ├── setup_nemo.py                # NeMo setup and configuration (to be implemented)
│   ├── setup_tensorrt.py            # TensorRT optimization setup (to be implemented)
│   └── setup_environment.py         # Environment setup script
│
├── docker/                          # Docker configuration (to be implemented)
│   ├── docker-compose.yml
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── Dockerfile.nemo              # NeMo Document AI container
│
├── docs/                            # Project documentation
│   ├── architecture.md
│   ├── api_docs.md
│   ├── development_guide.md
│   ├── nvidia_integration.md        # NeMo and TensorRT integration guide
│   ├── hardware_optimization.md     # Hardware tuning guide
│   ├── future_extensions.md         # Guide for external API integration
│   └── user_guide.md
│
├── venv_nemo/                       # Python 3.11 virtual environment for NeMo
├── requirements.txt                 # Project-level dependencies (consolidated)
├── setup_environment.py             # Setup script (consolidated)
├── start_services.bat               # Script to start all services
├── stop_services.bat                # Script to stop all services
├── Devlog.md                        # Development log (Updated)
├── implementation.md                # Implementation plan
├── Readme.MD                        # Project overview
├── Scope.md                         # Project scope
└── LICENSE                          # Project license
```

## Component Interaction Diagram With Containment
```
┌──────────────────────────────────────────────────────────────┐
│                         User Interface                        │
└─────────────────────────────┬────────────────────────────────┘
                              │
┌─────────────────────────────▼────────────────────────────────┐
│                        Project Context                        │
└─────────────────────────────┬────────────────────────────────┘
                              │
           ┌─────────────────┴─────────────────┐
           │                                   │
┌──────────▼───────────┐             ┌─────────▼────────┐
│  Project-Specific    │             │  Global Knowledge │
│  Knowledge Container │             │  (Optional)       │
└──────────┬───────────┘             └─────────┬─────────┘
           │                                   │
  ┌────────┴───────┐                  ┌────────┴───────┐
  │                │                  │                │
┌─▼────┐    ┌──────▼─┐             ┌─▼───────┐  ┌─────▼───┐
│Project│    │Project │             │All Other│  │All Other│
│Chats  │    │Documents│            │Chats    │  │Documents│
└───────┘    └────────┘             └─────────┘  └─────────┘
```

## Core Features Implementation Plan (Updated)

### Phase 1: UI Shell & Navigation (3 weeks)
- [x] Setup React application with TypeScript, Vite, and Redux
- [x] Create layout components (sidebar, header, main content)
- [x] Implement project management UI (list, create, edit, delete)
- [x] Develop chat interface with static mock data
- [x] Build document management UI with mock data
- [ ] Create settings panels and performance monitors
- [ ] Implement context controls UI components
- [ ] Design reasoning mode selector UI
- [x] Implement navigation flow between all screens
- [x] Design and implement UI theme with navy/gold color scheme
- [x] Create responsive layouts for different screen sizes
- [ ] Implement animations and transitions

### Phase 2: Project-Centered Components (2 weeks)
- [x] Implement project containment UI architecture
- [x] Create project modal dialogs (add, modify, delete)
- [x] Build project-specific chat views and management
- [ ] Implement document attachment to projects
- [ ] Create project-specific settings and configuration
- [ ] Implement visual indicators for project context
- [ ] Build project file manager with containment
- [ ] Create project-specific chat list
- [ ] Implement project-specific sidebar behavior

### Phase 3: Context Controls & Memory System (2 weeks)
- [ ] Implement tiered memory system UI
- [ ] Create context controls with preset modes
- [ ] Build custom mode configuration interface
- [ ] Implement document source selection (project vs all)
- [ ] Create memory scope controls (chat vs project vs all)
- [ ] Implement reasoning depth slider
- [ ] Build visual indicators for context state
- [ ] Create performance monitoring components
- [ ] Implement context control state management

### Phase 4: Basic Backend Services (3 weeks)
- [ ] Setup FastAPI application structure
- [ ] Implement database models with containment relationships
- [ ] Create repositories for project-centered data access
- [ ] Build API endpoints for project-centered CRUD operations
- [ ] Setup authentication and security (if needed)
- [ ] Configure logging and error handling
- [ ] Implement service layer with service factory
- [ ] Create document storage system with project associations
- [ ] Implement chat storage with project relationships
- [ ] Design API interfaces for contextual retrieval

### Phase 5: Backend-Frontend Integration (2 weeks)
- [ ] Connect React frontend to FastAPI backend
- [ ] Implement API service clients
- [ ] Replace mock services with real API calls
- [ ] Create error handling for API responses
- [ ] Implement real-time updates where needed
- [ ] Develop proper state management with API data
- [ ] Implement authentication flow (if needed)
- [ ] Create loading states and indicators
- [ ] Test basic CRUD operations end-to-end
- [ ] Implement file upload with real processing

### Phase 6: NVIDIA Integration (2 weeks)
- [ ] Implement TensorRT optimization for models
- [ ] Integrate NeMo Document AI components
- [ ] Configure Docker containers for NeMo (if needed)
- [ ] Setup CUDA optimizations for vector operations
- [ ] Create abstraction layers for hardware components
- [ ] Implement hardware monitoring and profiling
- [ ] Test performance on target hardware
- [ ] Create optimization scripts for deployment

### Phase 7: Document Processing With Hierarchical Indexing (2 weeks)
- [ ] Implement hierarchical document processors with NeMo
- [ ] Create multi-level chunking strategies
- [ ] Implement metadata extraction and storage
- [ ] Setup structure preservation for document context
- [ ] Implement document preview generation
- [ ] Create document hierarchy visualization data
- [ ] Test document processing with various formats
- [ ] Optimize processing for performance
- [ ] Connect document processing to UI components

### Phase 8: RAG Implementation With Project Prioritization (2 weeks)
- [ ] Implement project-centered retrieval with prioritization
- [ ] Create tiered memory system with document priority
- [ ] Implement document context visualization
- [ ] Create relevance indicators for documents
- [ ] Implement document source attribution
- [ ] Create reranking logic for project priority
- [ ] Optimize vector operations with CUDA
- [ ] Test RAG functionality with prioritization
- [ ] Implement context window management
- [ ] Connect RAG system to chat interface

### Phase 9: Reasoning Capabilities (1 week)
- [ ] Implement reasoning mode API endpoints
- [ ] Create prompt templates for different reasoning modes
- [ ] Implement chain-of-thought prompting for expert mode
- [ ] Connect reasoning mode UI controls to backend
- [ ] Implement GPU monitoring for reasoning operations
- [ ] Test reasoning capabilities with different modes
- [ ] Optimize for 30-35B models with TensorRT
- [ ] Create performance metrics for reasoning modes

### Phase 10: Voice Integration (1 week)
- [ ] Implement Whisper API endpoint
- [ ] Connect voice recording component to backend
- [ ] Implement transcript editing
- [ ] Create voice-to-text workflow
- [ ] Optimize voice processing for hardware
- [ ] Test voice functionality
- [ ] Implement GPU offloading for voice processing

### Phase 11: External API Framework (1 week)
- [ ] Create abstraction layers for external providers
- [ ] Implement privacy preservation controls
- [ ] Design data flow for external API integration
- [ ] Create UI components for external service indicators
- [ ] Implement API key management system
- [ ] Create database structures for external sources
- [ ] Design comparison logic for local vs. external results
- [ ] Document extension points for future implementation

### Phase 12: Testing and Refinement (2 weeks)
- [ ] Comprehensive testing of all features
- [ ] Performance optimization for target hardware
- [ ] UI/UX refinement
- [ ] Bug fixing and issue resolution
- [ ] Documentation updates
- [ ] User workflow testing
- [ ] Performance benchmarking
- [ ] Security review

### Phase 13: Deployment and Finalization (1 week)
- [ ] Prepare production build
- [ ] Create deployment scripts
- [ ] Update launcher and service management
- [ ] Final documentation
- [ ] Create hardware optimization guide
- [ ] Performance profiling
- [ ] Release preparation
- [ ] User guide creation

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

### Future External Integration UI
```
┌─ EXTERNAL RESOURCES ─────────────────────────────────────┐
│                                                          │
│  Enable External Services: [ ] (Disabled by default)     │
│                                                          │
│  When enabled:                                           │
│  ├──────────────────────────────────────────────────────┤
│                                                          │
│  Verification: [ ] Use Claude API to verify results      │
│                [ ] Use ChatGPT API to verify results     │
│                                                          │
│  Web Search:   [ ] Enable web search for recent info     │
│                                                          │
│  Privacy:      [•] Ask before sending data externally    │
│                [ ] Always redact sensitive information   │
│                [ ] Show preview of outgoing data         │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

## Project-Centered Workflow Implementation Details

### Welcome Screen / Dashboard
* Project list with collapsible sections
* System status indicators
* File management access
* Search functionality
* Add project function
* Clear visual hierarchy showing project containment

### Project Management
* Project creation with name and custom prompt
* Project modification and deletion
* Project-specific chat management
* Project-specific document attachment
* Project settings configuration
* Project containment visualization

### Chat Interface
* Project-specific chats only by default
* Message history with user/assistant distinction
* Input area with voice dictation option
* Project-aware context control panel
* Document context visualization with project indicators
* Reasoning mode selection
* GPU utilization indicators
* User prompt management

### Document Management
* Global file manager for all documents
* Project-specific file attachment
* Document upload with description
* Document processing status tracking
* Hierarchical document viewer with NeMo
* Document attachment to projects with priority
* Search and filtering capabilities
* Project context indicators for documents

## UI Design Guidelines

### Color Scheme
* Dark background (#080d13)
* Gold accents (#FFC000)
* Neutral grays for content areas
* High contrast for readability
* Visual indicators for project context
* Visual indicators for reasoning modes
* Future: Visual indicators for external services

### Layout
* Project sidebar with collapsible sections
* Main content area for chat/documents
* Modal dialogs for forms and confirmations
* Responsive design for different screen sizes
* Context controls panel with collapsible state
* Project containment visualization
* Future: External resource indicator area

### Component Design
* Clean, minimal interfaces
* Consistent styling with Tailwind CSS
* Responsive feedback for user actions
* Clear visual hierarchy for project containment
* Hardware status indicators
* Context expansion indicators
* Future: Privacy indicators for external services

## Technology Stack

### Frontend
* React (UI library)
* TypeScript (type-safe JavaScript)
* Vite (build tool)
* Redux Toolkit (state management)
* Axios (HTTP client)
* React Router (routing)
* Tailwind CSS (styling)
* React Query (optional, for data fetching with caching)

### Backend
* FastAPI (Python web framework)
* SQLAlchemy (ORM)
* PostgreSQL with pgvector (vector database)
* Pydantic (data validation)
* NeMo (AI model integration)
* TensorRT (NVIDIA optimization)
* NeMo Document AI (document processing)
* CUDA libraries for optimization
* Docker (optional for NeMo on Windows)

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

### Development Process
* Implement features according to phase plan
* Test functionality throughout development
* Document changes and features
* Track progress against implementation plan
* Benchmark performance against target hardware
* Build for future extensibility

### Important Development Notes
* NEVER use console commands like `echo` to create code files
* Always use a proper text editor (VS Code recommended)
* Follow proper case sensitivity in filenames (PascalCase for components)
* Use consistent coding conventions throughout the project
* Test frequently during development to catch issues early
* Maintain detailed documentation in the Devlog for all changes

### Testing
* Unit tests for backend services
* API tests for endpoints
* Component tests for React components
* Integration tests for complete flows
* Performance tests for hardware utilization
* Accessibility testing for UI components

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

### Next Components to Implement
- [ ] DeleteProjectModal.tsx - Modal for deleting projects
- [ ] ModifyProjectModal.tsx - Modal for modifying project settings
- [ ] AttachFileModal.tsx - Modal for attaching files to projects
- [ ] ContextControlsPanel.tsx - Panel for controlling context settings
- [ ] ProjectFileManager.tsx - Project-specific file manager
- [ ] DeleteChatModal.tsx - Modal for deleting chats
- [ ] ModifyChatModal.tsx - Modal for modifying chat settings

## Conclusion

This implementation plan outlines a comprehensive approach to building the AI Assistant with project-centered containment. By following this step-by-step process, we'll create a polished, performant application that respects user privacy while providing powerful AI capabilities tailored to the specified hardware configuration.

The project-centered containment approach provides significant benefits for organization, performance, and user experience. By preserving this core architectural principle throughout the implementation, we'll deliver an intuitive, powerful system that aligns with natural human workflows while providing the flexibility to expand context when needed.