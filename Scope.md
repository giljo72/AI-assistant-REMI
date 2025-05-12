# AI Assistant: Local Vector-Backed Knowledge System
## Project Vision & Scope Document (Updated)

## Project Vision
The AI Assistant project aims to create a fully private, locally-hosted knowledge management and AI assistance system that gives users complete control over their data and workflow. By implementing a modern FastAPI + React architecture, we'll deliver:

* Uncompromising privacy through 100% local processing
* Intuitive knowledge organization with a project-centered containment approach
* Context-aware AI assistance with tiered memory retrieval and enhanced reasoning capabilities
* Transparent document management with prioritized project-specific documents
* Modern, responsive interface with adaptive context controls
* Hardware-optimized performance (RTX 4090, Ryzen 7800X3D, 64GB RAM)

The core philosophy remains that powerful AI assistance should not require surrendering data ownership or privacy, now enhanced with modern web architecture for improved performance and user experience.

## User Needs and Benefits

### Privacy-Focused Users
* Complete data ownership with no cloud dependencies
* Transparent information usage through visual context indicators
* Granular control over how knowledge is organized and accessed
* Local LLM processing that never sends queries to external services

### Knowledge Workers
* Project-centered organization that matches real-world workflows
* Adaptive context controls balancing depth vs. speed
* Visual indicators for document context and relevance
* Fast, responsive interface for complex knowledge tasks
* Enhanced reasoning capabilities for deeper analysis

### Technical Users
* Local LLM integration with NVIDIA optimization (30-35B models)
* Optimized vector search with PostgreSQL + pgvector
* Comprehensive document processing pipeline with hierarchical storage using NeMo
* Customizable system with well-documented API endpoints
* TensorRT optimization for maximizing hardware performance

## Key Differentiators

### Project-First Containment Architecture
Projects serve as the primary organizational unit, acting as self-contained knowledge environments. Each project contains:

* Multiple chats specific to that project's context
* Attached documents relevant to the project's focus
* Project-specific settings (including custom prompts)

This containment approach mirrors real-world workflows, creates intuitive knowledge boundaries, and enables performance optimization by limiting context scope.

### Tiered Memory System with Prioritization
Users can control both the scope and prioritization of knowledge:

* **Document Sources**:
  * Project Documents Only (focused, fastest)
  * Prioritize Project Documents (balanced, project documents given higher weight)
  * All Documents Equally (comprehensive)

* **Memory Scope**:
  * Current Chat Only (focused, fastest)
  * Project Chats (balanced)
  * All Conversations (comprehensive)

This tiered system allows selective expansion of context beyond project boundaries when needed, while maintaining project containment as the default.

### Adaptive Reasoning Modes
The system provides different reasoning modes optimized for the hardware:

* **Standard**: Balanced analysis with normal context depth
* **Comprehensive**: Multi-step reasoning with expanded context
* **Expert**: Detailed reasoning chains with maximum context utilization

### Visual Context Awareness
The interface provides clear visual indicators showing:

* Which documents influence AI responses and their priority level
* Document relevance scores for transparency
* Active memory scope and reasoning mode
* Project context and settings
* Expected performance characteristics

### Modern React Architecture
The React frontend provides:

* Responsive, single-page application experience
* Fluid transitions between components
* Consistent state management with Redux
* Component-based architecture for maintainability
* Context-aware UI elements that adapt to user workflow

### FastAPI Backend
The FastAPI backend delivers:

* High-performance API endpoints
* Clear separation of concerns
* Asynchronous processing for long-running tasks
* Well-documented API with Swagger UI
* Optimized document processing pipeline

## Technology Stack

## Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Frontend | React + TypeScript + Vite | User interface with fast build system |
| State Management | Redux Toolkit | Centralized application state |
| Backend API | FastAPI | High-performance API endpoints |
| Vector Database | PostgreSQL + pgvector | Vector storage and retrieval |
| LLM Options | NeMo (primary) / Ollama + TensorRT (alternative) | Language model capabilities |
| Document Processing | NeMo Document AI + Python libraries | Hierarchical document processing |
| Voice Processing | Whisper | Transcription for voice input |
| NVIDIA Integration | TensorRT, NeMo | Hardware optimization and document understanding |

## Core System Architecture
The AI Assistant follows a modern, layered architecture that separates concerns while maintaining high performance:

```
┌────────────────────────────────────────────────────────────┐
│                     REACT FRONTEND                         │
├────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────┐ │
│ │Project      │ │Chat         │ │Document     │ │Settings│ │
│ │Management   │ │Interface    │ │Management   │ │Panel   │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └────────┘ │
└───────────────────────────┬────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────┐
│                     FASTAPI BACKEND                        │
├────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────┐ │
│ │API          │ │Service      │ │Repository   │ │Document│ │
│ │Endpoints    │ │Layer        │ │Layer        │ │Process │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └────────┘ │
└───────────────────────────┬────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────┐
│                 DATABASE & STORAGE LAYER                   │
├────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────┐ │
│ │PostgreSQL   │ │Vector       │ │Document     │ │Settings│ │
│ │Database     │ │Storage      │ │Storage      │ │Storage │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └────────┘ │
└───────────────────────────┬────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────┐
│                  OPTIMIZED LLM LAYER                       │
│                 (TensorRT + Ollama)                        │
└────────────────────────────────────────────────────────────┘
```

## Containment vs. Expansion Architecture

The system is designed around a philosophy of "containment by default, expansion by choice":

1. **Default Containment**: Projects act as self-contained knowledge environments with:
   - Project-specific chats
   - Project-attached documents
   - Project-level settings and custom prompts

2. **Selective Expansion**: Users can opt to expand beyond containment boundaries via:
   - Context controls to include knowledge from other projects
   - Memory scope controls to incorporate conversation history from other contexts
   - Reasoning depth controls to adjust processing intensity

3. **Performance Benefits**:
   - Containment limits context scope for better performance
   - Selective expansion allows access to broader knowledge when needed
   - Clear visual indicators show when expanded context is being used

4. **Future Extension**:
   - The same containment/expansion model applies to future external integrations
   - Optional connections to external APIs and web search will follow the same pattern
   - Users maintain control over what leaves the local environment

## Key System Layers

### 1. React Frontend Layer
* Implements container/presentation pattern for component organization
* Uses React Router for navigation between application sections
* Manages application state with Redux Toolkit
* Communicates with backend through API services
* Provides responsive UI with modern design principles
* Implements context controls with adaptive reasoning modes

### 2. FastAPI Backend Layer
* Exposes RESTful API endpoints for all functionality
* Implements business logic in service layer
* Manages data access through repository pattern
* Handles document processing and vector operations
* Integrates with Ollama and TensorRT for LLM generation
* Implements performance optimizations for hardware

### 3. Database & Storage Layer
* PostgreSQL database with pgvector extension
* Manages document storage and metadata
* Stores vector embeddings with hierarchical information
* Handles project and chat organization
* Maintains user settings and preferences
* Optimized for performance on target hardware

### 4. Optimized LLM Layer
* Manages local language model execution (30-35B models)
* Processes prompts with relevant context
* Generates responses based on retrieved information
* Handles instruction following and context window
* Implements reasoning modes with appropriate prompting
* Uses TensorRT for hardware-optimized inference

## UI Design Guidelines

### Context Controls Panel
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
│  Sources: ☑ Project Docs (Priority)                   │
│           ☑ Project Chats                             │
│           ☐ All Documents                              │
│           ☐ All Conversations                          │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### Visual Theme
#### Primary Colors:
* Dark navy (#080d13) for main backgrounds
* Gold (#FFC000) for accent elements
* Lighter navy (#121922) for content areas
* White text on dark backgrounds for readability

#### Design Principles:
* Clean, minimal interfaces
* Clear visual hierarchy
* Appropriate spacing for readability
* Responsive design for different screen sizes
* Visual feedback for reasoning modes

### Component Patterns
* Implement container/presentation pattern
* Use context API for cross-cutting concerns
* Create compound components for flexibility
* Use React Hooks for component logic
* Implement adaptive UI based on context state

## Future Expansion: External API & Web Integration

While the core project maintains complete privacy and offline operation, future versions will include optional capabilities for external connectivity:

### External API Integration
* Optional Claude AI and ChatGPT API integration for result verification
* Transparent system showing exactly what data leaves the system
* Secure API key management and usage tracking
* Result comparison between local and external models
* Privacy-preserving prompting with sensitive information redaction

### Web Search Capabilities
* Optional web search for time-sensitive information
* Integration of search results into local knowledge base
* Source attribution and citation management
* Web content processing with minimal external dependencies
* Opt-in approach preserving offline-first philosophy

### Hybrid Knowledge Architecture
* Clear separation between local and external knowledge
* Visual indicators when using external resources
* Ability to save external knowledge to local database
* Configurable trust levels for different knowledge sources
* Preservation of privacy as the default mode

This expansion will be implemented through a modular architecture that:
1. Maintains the existing offline-first experience
2. Provides clear opt-in controls for external services
3. Ensures transparent information flow
4. Preserves the project-centered organization paradigm
5. Integrates external knowledge seamlessly within existing workflows

## UI-First Implementation Strategy

To ensure the interface vision is fully realized, the project follows a UI-first approach with progressive enhancement:

### Phase 1: UI Shell & Navigation (3 weeks)
* Implement complete UI mockups with React
* Build all screens with static data
* Create the full navigation flow
* Implement responsive layouts and animations
* Focus on getting the "feel" right before adding functionality

### Phase 2: Basic Interaction Layer (2 weeks)
* Add simple chat functionality with mock responses
* Implement project/chat/document management UI interactions
* Create context controls with visual feedback (but no actual backend effect)
* Build file upload UI with processing indicators

### Phase 3: Core Backend Services (3 weeks)
* Implement FastAPI backend with database connections
* Build basic document processing pipeline
* Add simple RAG functionality with pgvector
* Connect basic Ollama integration (without optimization yet)

### Phase 4: NVIDIA Integration & Enhancement (3 weeks)
* Connect UI to real backend services
* Implement document prioritization and hierarchical indexing
* Add reasoning capabilities with multiple modes
* Integrate NeMo and TensorRT components for performance

### Phase 5: Optimization & Refinement (2 weeks)
* Optimize performance based on user feedback
* Refine UI based on actual usage patterns
* Implement hardware-specific optimizations
* Add final polish to the interface

This approach allows us to:
1. Rapidly iterate on the UI experience
2. Get early feedback on the interface design
3. Ensure the UI vision is fully realized before adding complex backend functionality
4. Maintain a consistent user experience throughout development

## Data Model
The PostgreSQL schema supports project-centered organization with hierarchical document storage:

```sql
-- Document metadata
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    content_type TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL,  -- Active, Detached, Failed
    file_path TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    chunk_count INTEGER DEFAULT 0,
    has_hierarchy BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Vector embeddings for document chunks with hierarchy
CREATE TABLE document_embeddings (
    id SERIAL PRIMARY KEY,
    content_hash TEXT UNIQUE NOT NULL,
    embedding vector(1536) NOT NULL, -- Using embedding size
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    parent_chunk_id INTEGER NULL REFERENCES document_embeddings(id),
    section_level INTEGER DEFAULT 0, -- 0=chunk, 1=section, 2=chapter, etc.
    section_title TEXT,
    chunk_metadata JSONB
);

-- Projects (central organizational unit)
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    custom_prompt TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Chats within projects
CREATE TABLE chats (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Chat messages
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    chat_id INTEGER REFERENCES chats(id) ON DELETE CASCADE,
    role TEXT NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    memory_scope TEXT DEFAULT 'project', -- 'current', 'project', 'all'
    document_scope TEXT DEFAULT 'prioritize', -- 'project_only', 'prioritize', 'all_equal'
    reasoning_mode TEXT DEFAULT 'standard', -- 'standard', 'comprehensive', 'expert'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Document associations with projects
CREATE TABLE document_projects (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    priority_boost FLOAT DEFAULT 1.0, -- For prioritization in retrieval
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT uq_document_project UNIQUE (document_id, project_id)
);

-- User prompts
CREATE TABLE user_prompts (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    prompt_text TEXT NOT NULL,
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## User Experience Requirements

### Project-Centered Organization
* Projects serve as containers for related chats
* Clear visual hierarchy showing project/chat relationship
* Intuitive controls for project management
* Document attachment at project level with prioritization

### Chat Experience
* Modern chat interface with message history
* Clear visual distinction between user and AI messages
* Context controls for memory scope, document priority, and reasoning depth
* Document context visualization showing relevance and priority

### Document Management
* Comprehensive file browser with filtering
* Document upload with metadata
* Preview capabilities for various document types
* Clear indication of document usage, priority, and context
* Hierarchical document processing for improved context

### Reasoning Capabilities
* Multiple reasoning modes optimized for 30-35B models
* Chain-of-thought prompting for complex questions
* Visual indicators of reasoning depth and processing status
* Performance monitoring with GPU utilization display

### Settings and Configuration
* LLM model selection and configuration
* System settings for performance tuning
* User preferences for UI and behavior
* Theme customization including dark mode
* Performance optimization controls

## Performance Considerations

### Hardware Optimization
* Optimize for RTX 4090, Ryzen 7800X3D, 64GB RAM
* Implement TensorRT optimization for 30-35B models
* Use NVIDIA CUDA optimizations for vector operations
* Implement NeMo Document AI in native or Docker configuration
* Balance memory usage between GPU and system RAM

### Backend Optimization
* Asynchronous API endpoints for long-running operations
* Efficient vector operations with pgvector
* Background processing for document handling
* Caching for frequently accessed data
* Optimized chunking and embedding generation

### Frontend Optimization
* Component memoization for re-render prevention
* Lazy loading for code splitting
* Virtual scrolling for large datasets
* State normalization for efficient updates
* Progressive rendering for improved perceived performance

### Database Optimization
* Proper indexing for efficient queries
* Connection pooling for performance
* Transaction management for data integrity
* PostgreSQL configuration tuning for target hardware
* Optimized vector search algorithms

## Security Considerations

### Data Protection
* Local processing guarantees data privacy
* No external API calls for core functionality
* Secure file storage with proper permissions
* Optional encryption for sensitive documents

### API Security
* Authentication for API endpoints (if needed)
* Rate limiting for abuse prevention
* Input validation for all endpoints
* Proper error handling with minimal information disclosure

### Frontend Security
* Safe data handling practices
* Prevention of common web vulnerabilities
* Secure communication with backend API
* Protection against common frontend attacks

## Deployment and Distribution

### Development Environment
* Local development setup with Docker
* Hot reloading for efficient development
* Comprehensive testing environment
* Debugging tools for both frontend and backend

### Production Deployment
* Standalone executable for easy distribution
* Local installation with minimal dependencies
* Automated backup and restore
* System health monitoring and performance tracking

## Conclusion
This AI Assistant project represents a significant advancement in local, private AI systems by combining modern web technologies with powerful retrieval-augmented generation capabilities. By implementing a FastAPI backend with a React frontend, we'll deliver a responsive, intuitive interface for knowledge management while maintaining complete data privacy through local processing.

The project-centered containment approach aligns with natural human workflows, creating an organizational structure that feels intuitive and powerful. The tiered memory system with document prioritization offers flexibility in knowledge retrieval, allowing users to precisely control the scope and depth of AI assistance.

With hardware-optimized performance using NVIDIA technologies and enhanced reasoning capabilities, the AI Assistant will provide a truly modern knowledge management experience that respects user privacy while delivering powerful AI capabilities tailored to the specified hardware configuration. The architecture is designed to support future expansion to optional external services while maintaining the core privacy-first philosophy.