#### AI Assistant: Vision and Architecture
### Last updated May 7 2025
## Project Vision

The AI Assistant project aims to create a completely private, local knowledge management and AI assistance system that keeps user data under their full control. In a world where AI assistants increasingly rely on cloud services and collect user data, this project stands apart by:

- Prioritizing privacy through 100% local processing
- Empowering users to organize knowledge in meaningful ways
- Creating context-aware AI assistance through project-based organization
- Providing transparent document management with full user control
- Delivering a modern, intuitive interface for complex knowledge tasks

The core philosophy is that powerful AI assistance should not require surrendering data ownership or privacy.

## User Needs and Benefits
# Privacy-Focused Users

Complete data ownership with no cloud dependencies
Full transparency about what documents are used in AI responses
Control over how information is organized and accessed

# Knowledge Workers

Project-centered organization to match real-world workflows
Document tagging and categorization (Private/Business/Both)
Visual indicators for context awareness
Voice interaction for hands-free use

# Technical Users

Local LLM hosting with low latency
Vector search capabilities for precise information retrieval
Document processing for various file formats
Customizable prompts for specialized tasks

# Key Differentiators

**Project-First Organization**: Projects serve as the primary organizational unit. Each project contains multiple chats organized around related topics or tasks.

**Tiered Memory Scope**: Users can toggle between three memory scopes:
1. Project-only scope (only searches current project's chats and attached documents)
2. Vector database scope (searches all indexed documents)
3. Complete memory scope (searches across all projects and their chats)

**Visual Context Awareness**: Users always know which documents and prompt templates are influencing AI responses through clear visual indicators and badges.

**Complete Privacy**: No data leaves the user's system, with all processing happening locally.

**Comprehensive Document Management**: Centralized file management interface with project attachment capabilities and full document lifecycle (upload, process, retrieve, download, delete).

**Prompt Management System**: Dedicated prompt management for system prompts, user prompts, and project-specific instructions.

**Voice Integration**: Seamless voice interaction using local Whisper implementation.

**Modern Dark-Themed UI**: Clean, responsive interface with a dark color scheme (#080d13 backgrounds, #FFC000 accents) that clearly organizes projects and their chats.

**Project and Chat Management Controls**: Each project and chat has dedicated controls for settings adjustment and deletion, making organization intuitive.

**Automated Launcher**: One-click startup of all required services (PostgreSQL, Ollama, Gradio) with health verification.

**Automated Shutdown**: One-click termination of all assistant-related processes and services.

# Technology Stack
| Component | Technology | Purpose |
|-----------|------------|---------|
| LLM Interface | Ollama | Local LLM hosting |
| Vector Database | PostgreSQL + pgvector | Vector storage and metadata |
| RAG Framework | LangChain | Document processing and retrieval |
| Web Framework | Gradio 5.29.0 | User interface |
| Voice Processing | Whisper | Transcription |
| Python Environment | venv (Python 3.10+) | Runtime environment |
| Service Management | psutil | Process detection and automation |

## Implementation Status (May 7, 2025)

### Completed Components
- **Core UI Framework**: Successfully migrated from Streamlit to Gradio 5.29.0
- **Database Integration**: Working connection to PostgreSQL with pgvector
- **Project-Centric UI**: Implemented sidebar with projects and chats
- **Theme System**: Created dark theme with gold accents
- **Service Factory**: Implemented centralized service management
- **File Upload**: Basic functionality for document processing
- **Navigation**: Working sidebar with project organization

### In-Progress Components
- **Service Layer**: Initial implementation with project and chat services
- **Project Management**: UI elements created, functionality in progress
- **Memory Scope System**: UI controls implemented, backend pending
- **LLM Integration**: Basic setup completed, service integration pending

### Planned Components
- **Voice Integration**: Design completed, implementation pending
- **Document Source Visualization**: Planned for final phase
- **Prompt Management System**: Design in progress
- **Cross-Project Search**: Planned for later phases

## System Architecture
# Architecture Overview
The AI Assistant follows a modular, layered architecture that prioritizes privacy, local processing, and project-centered organization. Below is a high-level overview of the system's architecture and component interactions:
```
+-----------------------------------------------+
|                 AI ASSISTANT                  |
+-----------------------------------------------+

+----------------+      +-------------------+
|                |      |                   |
|  USER INTERFACE|      |  SERVICE LAYER    |
|  (Gradio 5.29.0)|<---->|                   |
|                |      |                   |
+----------------+      +-------------------+
       |                          |
       |                          |
       v                          v
+----------------+      +-------------------+
|                |      |                   |
|   DOCUMENT     |      |    KNOWLEDGE      |
|   MANAGEMENT   |<---->|    RETRIEVAL      |
|                |      |                   |
+----------------+      +-------------------+
       |                          |
       |                          |
       v                          v
+----------------+      +-------------------+
|                |      |                   |
|    STORAGE     |      |   LLM INTERFACE   |
|    LAYER       |<---->|   (Ollama)        |
|                |      |                   |
+----------------+      +-------------------+
```

## Key System Layers
# User Interface Layer (Gradio)

Provides project-based navigation and management
Renders chat interface with memory scope controls
Manages document upload, tagging, and organization
Handles voice input via microphone integration
Displays document source attribution for AI responses
Manages system settings and configuration

# Service Layer (Updated)

Serves as an intermediary between UI and backend components
Provides a structured API for UI to access backend functionality
Manages application state and session consistency
Handles dependency injection and component lifecycle
Adapts backend responses for UI consumption
Facilitates the migration from Streamlit to Gradio

# Core Services Layer

Coordinates project, chat, and document operations
Manages application state and user session data
Handles event propagation between components
Implements business logic for feature interactions
Provides authentication and security services

# Document Management Layer

Processes various document formats (PDF, TXT, DOCX, XLS)
Handles document chunking and metadata extraction
Manages document tagging (Private/Business/Both)
Tracks document relationships to projects
Maintains document lifecycle (upload, process, retrieve, delete)

# Knowledge Retrieval Layer

Generates vector embeddings for document chunks
Implements tiered memory scope (project-only, vector DB, all chats)
Retrieves relevant context based on user queries
Calculates relevance scores for document chunks
Builds prompt context with selected documents

# Storage Layer

PostgreSQL database with pgvector extension
Manages vector embeddings for semantic search
Stores document metadata and relationships
Persists project and chat history data
Handles secure file storage for document content

# LLM Interface Layer

Connects to Ollama for local LLM hosting
Manages prompt templates and instruction sets
Processes LLM responses for display
Handles source attribution and context visualization
Optimizes performance for local execution

# Service Layer Design (Updated)

The AI Assistant implements a dedicated service layer that acts as an intermediary between the UI components and the backend services. This pattern provides several benefits:

## Service Layer Components

### Service Factory (Implemented)
- Central initialization point for all services and repositories
- Manages dependencies between components
- Provides access to properly initialized services
- Handles service lifecycle

### Domain-Specific Services:

- **FileService (Implemented)**: Connects document UI with file processing backend
- **ProjectService (In Progress)**: Manages project-related operations
- **ChatService (In Progress)**: Handles conversation and response generation
- **RAGService (Planned)**: Will coordinate retrieval and generation processes

## Service Layer Benefits

- **Decoupling**: UI components are not directly dependent on backend implementations
- **Testability**: Services can be mocked for UI testing
- **Flexibility**: Services can adapt different UI frameworks to the same backend
- **Consistency**: Standard patterns for error handling and state management
- **Migration Support**: Facilitates transition from Streamlit to Gradio

## Service Layer Flow

1. UI components request operations through service interfaces
2. Services coordinate the necessary backend components
3. Backend components perform the actual work
4. Services transform results for UI consumption
5. UI components display the results to the user

## UI Design Guidelines
# Visual Theme

**Primary Background**: Dark navy/black (#080d13) for main application background
**Secondary Background**: Slightly lighter (#121922) for content areas
**Accent Color**: Gold (#FFC000) for important UI elements and AI responses
**Text Colors**: White for user content, gold for AI responses, white for UI elements
**Button Colors**: Gold (#FFC000) for primary buttons, transparent for icon buttons

# Project Organization

**Hierarchical Display**: Projects as collapsible sections with chats indented beneath
**Visual Hierarchy**: Project headers in gold, chats in white
**Navigation Controls**: Icon-based navigation in sidebar for major functions
**Management Controls**: Context-sensitive controls for project and chat management

# Chat Display

**Message Differentiation**: User messages right-aligned with blue background, AI messages left-aligned with dark background
**Context Indicators**: Visual badges showing active document context and prompt template
**Memory Scope Controls**: Clearly defined toggles for switching between memory tiers
**Input Area**: Clean, focused input with voice and attachment buttons

# Document Integration

**Document Attachment UI**: Icon beside projects for attaching documents
**Context Visualization**: Visual indicators showing which documents influenced responses
**Relevance Indicators**: Clear visual scale showing document relevance to queries
**Source Attribution**: Direct links to source documents in AI responses

## Current Challenges

### 1. Gradio 5.29.0 Compatibility
- Managing component state across different Gradio components
- Addressing API differences between Gradio versions
- Implementing modal-like functionality without a built-in Modal component

### 2. Service Integration
- Connecting UI components to backend services effectively
- Maintaining proper state management between UI and services
- Handling asynchronous operations and updates

### 3. Memory Scope Implementation
- Connecting UI toggles to the actual retrieval system
- Implementing the tiered approach to memory
- Visualizing document context and relevance

## Development Strategy

1. **Complete Service Implementation**: Finish the service layer to provide full functionality
2. **UI-Backend Integration**: Connect UI components to services for CRUD operations
3. **LLM Integration**: Connect Ollama to the chat interface for real responses
4. **Document Context**: Implement document attachment and visualization

## Project Structure
F:/Project_Files/
├── config/                      # Configuration files
│   ├── .env                     # Environment variables
│   └── settings.yaml            # Application configuration
│
├── src/
│   ├── core/                    # Core system components
│   │   ├── config.py            # Configuration management
│   │   ├── db_interface.py      # Database connection management
│   │   ├── llm_interface.py     # Ollama integration
│   │   └── logger.py            # Logging system
│   │
│   ├── db/                      # Database components
│   │   ├── models.py            # SQLAlchemy models
│   │   └── repositories/        # Database access abstractions
│   │       ├── document_repo.py # Document operations
│   │       ├── project_repo.py  # Project operations
│   │       ├── chat_repo.py     # Chat operations
│   │       └── vector_repo.py   # Vector embeddings operations
│   │
│   ├── document_processing/     # Document handling
│   │   ├── base_processor.py    # Abstract base for document processors
│   │   ├── text_processor.py    # Text documents (txt, docx, rtf)
│   │   ├── pdf_processor.py     # PDF processing
│   │   ├── spreadsheet_processor.py # Excel/CSV processing
│   │   ├── image_processor.py   # Basic image handling
│   │   └── file_manager.py      # File management coordination
│   │
│   ├── services/                # Service layer (Updated)
│   │   ├── __init__.py          # Package initialization
│   │   ├── service_factory.py   # Service initialization and dependency management
│   │   ├── file_service.py      # Document processing service
│   │   ├── project_service.py   # Project management service (New)
│   │   ├── chat_service.py      # Chat and conversation service (Enhanced)
│   │   └── rag_service.py       # Retrieval augmented generation service
│   │
│   ├── rag/                     # Retrieval Augmented Generation
│   │   ├── embeddings.py        # Vector embedding generation
│   │   ├── retrieval.py         # Document retrieval
│   │   └── generation.py        # Response generation
│   │
│   ├── chat/                    # Chat and project management
│   │   ├── project_manager.py   # Project organization
│   │   ├── chat_manager.py      # Chat management within projects
│   │   └── history_manager.py   # Chat history tracking
│   │
│   ├── gradio/                  # Gradio UI components
│   │   ├── app.py               # Main application (Updated)
│   │   ├── pages/               # Page components
│   │   │   ├── chat.py          # Chat interface with memory scope toggle (Updated)
│   │   │   ├── files.py         # File management and project attachment
│   │   │   ├── document_viewer.py # Document viewer interface
│   │   │   └── settings.py      # Settings page
│   │   ├── components/          # Reusable UI components
│   │   │   ├── chat_ui.py       # Chat display
│   │   │   ├── document_viewer.py # Document viewing functionality
│   │   │   ├── file_upload.py   # File upload widget
│   │   │   ├── project_sidebar.py # Project navigation (Updated)
│   │   │   ├── project_modal.py # Project creation/editing modal (New)
│   │   │   ├── chat_modal.py    # Chat creation/editing modal (New)
│   │   │   └── voice_recorder.py # Voice input
│   │   └── utils/               # UI utilities
│   │       ├── theme.py         # Theme configuration
│   │       ├── custom_css.py    # Custom CSS styling
│   │       ├── modal.py         # Custom modal implementation (New)
│   │       └── indicators.py    # Processing indicators
│   │
│   └── utils/                   # Utilities
│       ├── document_formatting.py # Document formatting utilities
│       ├── speech_processor.py  # Whisper integration
│       └── system_utils.py      # System helpers
│
├── scripts/                     # Utility scripts
│   ├── setup_database.py        # Database initialization
│   ├── run_assistant.py         # Application runner
│   └── diagnostics.py           # System diagnostics
│
├── data/                        # Data storage
│   ├── uploads/                 # Temporary upload storage
│   ├── processed/               # Processed document storage
│   └── logs/                    # Application logs
│       └── _process_log.txt     # File processing audit log
│
├── launch_assistant.py          # Service automation script
├── Start_AI.bat                 # One-click launcher
├── stop_assistant.py            # Service termination script
├── Stop-AI.bat                  # One-click shutdown
└── misc/                        # Miscellaneous
    └── n8n_workflows/           # Optional n8n workflow definitions

## Database Schema

A PostgreSQL schema designed to support project-centered organization with comprehensive metadata:

```sql
-- Document embeddings for vector search
CREATE TABLE document_embeddings (
    id SERIAL PRIMARY KEY,
    content_hash TEXT UNIQUE NOT NULL,
    embedding vector(1536) NOT NULL,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,    -- Position in the document
    chunk_text TEXT NOT NULL,        -- Actual text content of the chunk
    chunk_metadata JSONB             -- Optional metadata about the chunk
);

-- Document metadata
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    content_type TEXT NOT NULL,
    tag TEXT NOT NULL,  -- P, B, or PB
    description TEXT,
    status TEXT NOT NULL,  -- Active, Detached, Failed
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    file_path TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    chunk_count INTEGER DEFAULT 0,
    processing_error TEXT, -- Stores error details if status is Failed
    search_vector tsvector  -- For full-text search
);

-- Projects (central organizational unit)
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    custom_prompt TEXT,
    default_memory_scope TEXT NOT NULL DEFAULT 'project', -- 'project', 'vector', 'all'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Chats within projects
CREATE TABLE chats (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Chat messages
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    chat_id INTEGER NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
    role TEXT NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    memory_scope TEXT NOT NULL DEFAULT 'project', -- 'project', 'vector', 'all'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Document associations with projects
CREATE TABLE document_projects (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT uq_document_project UNIQUE (document_id, project_id)
);
```

### User Experience Requirements
## Visual Design

Dark theme with gold and blue accent colors
Project-centric organization with visual hierarchy
Collapsible projects containing multiple chats
Visual badges for document usage, prompt templates, and memory scope
Navigation and action icons for efficient interaction
Context-sensitive controls for projects and chats

## Project Management

Create, modify, and delete projects as the central organizational unit
Projects serve as containers for multiple chats and attached documents
Project-level custom prompts and instructions
Clear visual organization of project resources
Project-specific default memory scope configuration
Context-sensitive project controls (settings, document attachment, deletion)

## Chat Management

Multiple chat sessions within each project
Visual badges indicating:
- Active document context from project attachments
- Current memory scope (project, vector DB, or all)
- Active prompt template
Chat history with user and AI messages
Context-sensitive chat controls (settings, deletion)

## Memory Scope Control

Three-tiered memory system:
- Project-scoped memory by default (only searches current project's chats and attached documents)
- Vector database memory (searches all indexed documents)
- Complete memory (searches across all projects' chats)
Visual indicator showing current memory scope
Memory scope toggle directly in chat interface
Performance optimization through appropriate scope selection
Ability to save preferred memory scope per project

## Document Management

Centralized file management interface separate from chat interface
File upload and tagging (P=Private, B=Business, PB=Either)
File descriptions (50-word maximum)
Document attachment to specific projects from the file manager
Document download functionality for viewing files in native applications
Process log for tracking file operations
Ability to delete documents with confirmation
Full-text search with relevance ranking
Document filtering by tag, status, and project

## Prompt Management

System prompt management for global AI behavior
User prompt templates for specific types of interactions
Project-specific instruction sets
Visual badges indicating which prompt is active
Ability to save, edit, and delete prompt templates

## Voice Interface

Voice recording via microphone button
Transcription using Whisper
Editable transcription before sending

## System Management

Automated one-click launcher for all services
Process detection and verification
Comprehensive process termination and service shutdown
Self-checking system health monitoring
Comprehensive error handling and logging
Service dependency management

## Future Expansion Possibilities

Web search integration (optional, with privacy controls)
PDF OCR for images and scanned documents
Timeline visualization for project history
Document summarization and key point extraction
Template system for common project types
Local image generation integration
Optional model auto-pull logic for Ollama

## Project Constraints

100% local processing (no cloud dependencies)
Privacy-first data handling
Support for Windows environments
Hardware optimization for consumer-grade machines
Modular architecture for future expansion