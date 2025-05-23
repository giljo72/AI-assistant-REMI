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

## Implementation Status

**🎉 PROJECT COMPLETE** - The AI Assistant is now fully operational with production-ready multi-model architecture:

### ✅ **Core System (100% Complete)**
* ✅ **UI Shell & Navigation**: Complete frontend structure with project sidebar, chat interface, and document management
* ✅ **Project-Centered Architecture**: Implemented project containment with proper navigation flows
* ✅ **User Prompts System**: Created user prompt functionality for custom assistant instructions
* ✅ **Context Controls UI**: Implemented context settings panel with project/global toggle controls
* ✅ **File Management UI**: Developed project file management and global file system with proper flow and robust file-project linking persistence
* ✅ **Universal Search Interface**: Implemented comprehensive search with 3-checkbox system (Chats, Knowledge Base, Documents)
* ✅ **System Management Architecture**: Complete separation between system monitoring (❓) and admin controls (⚙️)
* ✅ **Database Models**: Created database models with proper relationships for project containment
* ✅ **API Endpoints**: Implemented backend API endpoints for core functionality
* ✅ **Document Processing**: Backend pipeline created with chunking and processing capabilities
* ✅ **Vector Database**: Integrated pgvector for semantic search capabilities

### ✅ **Multi-Model AI Integration (100% Complete)**
* ✅ **Unified LLM Service**: Single interface routing to NIM, Ollama, Transformers, and NeMo models
* ✅ **NVIDIA NIM Integration**: Complete TensorRT-optimized inference with Llama 3.1 8B/70B models
* ✅ **Ollama Integration**: Full HTTP API support with Mistral-Nemo 12B and CodeLlama 13B models
* ✅ **Model Switching**: Seamless switching between 6 different AI models via unified interface
* ✅ **Chat Backend**: Complete chat API with multi-model support and context management
* ✅ **RAG Implementation**: Vector database integrated with semantic search and document retrieval

### ✅ **Production Infrastructure (100% Complete)**
* ✅ **Docker Integration**: Complete NIM container deployment with GPU acceleration
* ✅ **Service Management**: Automated startup/shutdown scripts (startai.bat/stopai.bat)
* ✅ **Cross-Platform Support**: WSL2 development environment with Windows production deployment
* ✅ **Hardware Optimization**: Full RTX 4090 utilization across all model types
* ✅ **Network Configuration**: Proper service binding for multi-environment access

### ✅ **System & Models Panel (100% Complete)**
* ✅ **Real-time Model Status**: Live monitoring of all AI models with memory usage and performance metrics
* ✅ **Model Loading/Switching**: Interface for loading, unloading, and switching between models
* ✅ **Service Health Monitoring**: Real-time status tracking for FastAPI, PostgreSQL, Docker, NIM, and Ollama
* ✅ **Hardware Monitoring**: GPU utilization, VRAM usage, and system resource tracking
* ✅ **Environment Information**: Complete system information display with dependency versions

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
* **Multi-Model Architecture**: Unified interface supporting NVIDIA NIM, Ollama, Transformers, and NeMo models
* **Production AI Models**: 6 specialized models optimized for different use cases (chat, code, embeddings, documents)
* **Hardware Optimization**: Complete RTX 4090 utilization with TensorRT acceleration and 4-bit quantization
* **Enterprise Integration**: NVIDIA NIM containers with professional-grade inference optimization
* **Local Model Flexibility**: Ollama integration for rapid model experimentation and development
* **Vector Search Engine**: PostgreSQL + pgvector with enterprise-grade semantic embeddings
* **Cross-Platform Development**: WSL2 development environment with Windows production deployment

## Key Differentiators

### Universal Search Interface
The system provides a comprehensive search capability across all knowledge domains:

* **Multi-Domain Search**: Search across Chats, Knowledge Base (processed documents), and Documents simultaneously
* **Probability Scoring**: All search results include relevance scores (0-100%) for transparency
* **Contextual Knowledge Results**: Knowledge base results show relevant snippets with expandable context
* **Direct Download Access**: Quick access to source documents without in-app viewers
* **Project-Aware Results**: Search results understand project context and relationships

### Multi-Model AI Architecture
Complete AI model management and optimization system:

* **Unified Model Interface**: Single API supporting NVIDIA NIM, Ollama, Transformers, and NeMo backends
* **Production Model Lineup**: 6 specialized models including Mistral-Nemo 12B, CodeLlama 13B, Llama 3.1 8B/70B
* **Intelligent Model Routing**: Automatic service selection based on model type and performance requirements
* **Real-time Model Management**: Load, unload, and switch between models with live status monitoring
* **Hardware Optimization**: Dynamic VRAM management with automatic container orchestration
* **Cross-Platform Deployment**: WSL2 development with Windows production, optimized networking
* **Service Health Monitoring**: Real-time status tracking for all AI services with automatic failover

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

## Asset Resources

### UI Icons
* **SVG Icon Library**: Curated collection of UI icons stored in `/Images/` directory
  * **Primary Usage Icons**: View (👁️→View.SVG), Add (+ buttons→add.svg), Close (X buttons→close.svg), Delete (🗑️→delete.svg), Download (⬇️→download.svg), Link (🔗→link.svg), Question (?→question.svg), Refresh, Search (🔍→search.svg)
  * **Dropdown Controls**: Multiple dropdown state icons for various UI elements
  * **Usage Pattern**: "Add Project (+)" where (+) represents the clickable add.svg icon
  * **Modal Integration**: All modal close buttons should use close.svg instead of text/emoji
  * **Reserved for Future**: unlink.svg (no current unlink function), save.svg (using download.svg instead)
  * Location: `F:\Assistant\Images\` - Scalable vector graphics for crisp display

## Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Frontend | React + TypeScript + Vite | User interface with fast build system |
| State Management | Redux Toolkit | Centralized application state |
| Backend API | FastAPI | High-performance API endpoints |
| Vector Database | PostgreSQL + pgvector | Vector storage and retrieval |
| LLM Generation | NVIDIA NIM MegatronGPT-20B | Production-optimized language model with TensorRT acceleration |
| Embeddings | NVIDIA NIM NV-Embed-v1 | Enterprise-grade document understanding and semantic search |
| Document Processing | NeMo Document AI + Python libraries | Hierarchical document processing with structure preservation |
| Voice Processing | Whisper (planned) | Transcription for voice input |
| System Monitoring | Custom service management + psutil | Real-time system and model status tracking |
| Model Management | Dynamic loading system (planned) | Runtime model switching and configuration |
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
│                    NVIDIA NIM LAYER                        │
│              (MegatronGPT-20B + NV-Embed-v1)               │
│                   TensorRT Optimized                       │
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

### 1. React Frontend Layer (Implemented)
* Implements container/presentation pattern for component organization
* Uses Redux for state management
* Communicates with backend through API services (mocked currently)
* Provides responsive UI with modern design principles
* Implements context controls with adaptive reasoning modes
* Provides project-centered file and chat management

### 2. FastAPI Backend Layer (In Progress)
* Exposes RESTful API endpoints for all functionality
* Implements business logic in service layer
* Manages data access through repository pattern
* Handles document processing and vector operations
* Integrates with Ollama and TensorRT for LLM generation
* Implements performance optimizations for hardware

### 3. Database & Storage Layer (To Be Implemented)
* PostgreSQL database with pgvector extension
* Manages document storage and metadata
* Stores vector embeddings with hierarchical information
* Handles project and chat organization
* Maintains user settings and preferences
* Optimized for performance on target hardware

### 4. NVIDIA NIM Inference Layer (To Be Implemented)
* **Dual NIM Architecture:** Separate containers for embeddings and generation
  * **NV-Embed-v1 (7.9B):** Enterprise-grade document understanding and semantic search
  * **MegatronGPT-20B:** Production-optimized text generation and reasoning
* **Offline Operation:** Complete local processing with no external dependencies
* **TensorRT Acceleration:** Hardware-optimized inference for RTX 4090
* **Smart Document Processing:** Hybrid approach using NeMo Document AI for structure preservation
* **Context-Aware Retrieval:** Advanced embedding model for accurate knowledge retrieval
* **Production-Grade Responses:** 20B parameter model for sophisticated reasoning and synthesis

## UI Design Guidelines

### Color Scheme
* Dark background (#080d13)
* Gold accents (#FFC000)
* Navy backgrounds (#121922, #152238, #1a2b47) for layered interfaces
* White and light gray text for readability
* Visual indicators with distinct colors for context states
* Semantic colors for status indicators (green, red, yellow)

### Layout
* Project sidebar with collapsible sections
* Main content area for chat/documents
* Modal dialogs for forms and confirmations
* Responsive design for different screen sizes
* Context controls panel with collapsible state
* Project containment visualization
* Sidebar sections for project navigation and system controls

### Component Design
* Clean, minimal interfaces
* Consistent styling with Tailwind CSS
* Responsive feedback for user actions
* Clear visual hierarchy for project containment
* Hardware status indicators
* Context expansion indicators
* Standardized modal patterns for user interactions

## Implementation Phases

### Phase 1: UI Shell & Navigation (Completed)
* Implement complete UI mockups with React
* Build all screens with static data
* Create the full navigation flow
* Implement responsive layouts and animations

### Phase 2: Project-Centered Components (Completed)
* Implement project containment UI architecture
* Create project modal dialogs
* Build project-specific chat views
* Implement document attachment to projects

### Phase 3: User Management & Prompts (Completed)
* Create UserPromptModal for adding/editing user prompts
* Build UserPromptManager for managing prompt collections
* Implement UserPromptIndicator for active prompt display
* Create UserPromptsPanel for sidebar integration

### Phase 4: Context Controls & Memory System (In Progress)
* Implement ContextControlsPanel component
* Create ContextStatusIndicators for quick toggle access
* Build context controls with preset modes
* Implement document source selection (project vs all)

### Phase 5: Basic Backend Services (To Be Implemented)
* Setup FastAPI application structure
* Implement database models with containment relationships
* Create repositories for project-centered data access
* Build API endpoints for project-centered CRUD operations

### Phase 6: Document Processing & RAG (To Be Implemented)
* Implement hierarchical document processors with NeMo
* Create multi-level chunking strategies
* Implement metadata extraction and storage
* Setup structure preservation for document context

### Phase 7: NVIDIA NIM Integration & Optimization (To Be Implemented)
* **Deploy NVIDIA NIM Containers:** 
  * NV-Embed-v1 for enterprise-grade embeddings
  * MegatronGPT-20B for production text generation
* **Hybrid Architecture Integration:**
  * Keep existing NeMo Document AI for hierarchical processing
  * Integrate NIM inference endpoints for embeddings and generation
  * Configure dual-container orchestration with Docker Compose
* **Hardware Optimization:**
  * TensorRT acceleration through NIM (built-in)
  * Memory management for dual RTX 4090 workloads
  * API load balancing between containers

### Phase 8: Testing and Refinement (To Be Implemented)
* Comprehensive testing of all features
* Performance optimization for target hardware
* UI/UX refinement based on testing
* Bug fixing and issue resolution

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

## Conclusion
This AI Assistant project represents a significant advancement in local, private AI systems by combining modern web technologies with powerful retrieval-augmented generation capabilities. By implementing a FastAPI backend with a React frontend, we'll deliver a responsive, intuitive interface for knowledge management while maintaining complete data privacy through local processing.

The project-centered containment approach aligns with natural human workflows, creating an organizational structure that feels intuitive and powerful. The tiered memory system with document prioritization offers flexibility in knowledge retrieval, allowing users to precisely control the scope and depth of AI assistance.

With hardware-optimized performance using NVIDIA technologies and enhanced reasoning capabilities, the AI Assistant will provide a truly modern knowledge management experience that respects user privacy while delivering powerful AI capabilities tailored to the specified hardware configuration.