# AI Assistant: FastAPI + React Implementation!!

A private, local AI assistant with project-centered containment, prioritized document retrieval, and adaptive reasoning capabilities optimized for high-performance hardware.

## Project Overview

This AI Assistant provides:

- **Project-Centered Containment**: Each project is a self-contained knowledge environment with its own chats and attached documents
- **Universal Search Interface**: Comprehensive 3-checkbox search across Chats, Knowledge Base, and Documents with probability scoring
- **System & Model Management**: Real-time monitoring and switching between Ollama/NeMo models with service controls
- **Selective Knowledge Expansion**: Opt-in controls to expand beyond project boundaries when needed
- **Prioritized Document Retrieval**: Project-attached documents receive higher priority in retrieval
- **Hierarchical Document Processing**: Improved document understanding using NeMo
- **Tiered Memory System**: Adaptive context controls for flexible knowledge access
- **Multiple Reasoning Modes**: Different reasoning depths optimized for hardware capabilities
- **Complete Document Lifecycle**: Upload, process, retrieve, view, and delete documents
- **RAG (Retrieval Augmented Generation)**: Enhanced with PostgreSQL+pgvector
- **Voice Interaction**: Using Whisper for transcription (planned)
- **Modern, Responsive UI**: Built with React and Tailwind CSS
- **Hardware Optimization**: Specifically for RTX 4090, Ryzen 7800X3D, and 64GB RAM

## Core Philosophy: Containment by Default, Expansion by Choice

The system is built around a foundational principle of **"containment by default, expansion by choice"**:

1. **Default Containment**: 
   - Projects act as self-contained knowledge environments
   - Each project has its own set of chats and attached documents
   - Knowledge is contained within project boundaries by default

2. **Selective Expansion**:
   - Users can explicitly opt to expand beyond project boundaries
   - Context controls allow including knowledge from other projects
   - Tiered memory options determine how broadly to search

3. **Performance Benefits**:
   - Containment limits context scope for better performance
   - Selective expansion allows access to broader knowledge when needed
   - Visual indicators show when expanded context is being used

This approach enables better performance, more intuitive organization, and greater control over the relevance and priority of information.

## Technology Stack

- **Frontend**: React + TypeScript (using Vite build system)
- **State Management**: Redux Toolkit
- **CSS Framework**: Tailwind CSS with custom theme
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL with pgvector
- **LLM**: Ollama with TensorRT optimization (30-35B models)
- **Document Processing**: NeMo Document AI, LlamaIndex, PyPDF, docx2txt, etc.
- **Voice Processing**: Whisper
- **Hardware Optimization**: TensorRT, CUDA acceleration, pipeline parallelism
- **NVIDIA Integration**: NeMo Document AI, TensorRT

## Hardware Specifications

The application is optimized for the following hardware configuration:
- **GPU**: NVIDIA RTX 4090 (24GB VRAM)
- **CPU**: AMD Ryzen 7800X3D
- **RAM**: 64GB
- **OS**: Windows 11

## Current Implementation Status

| Feature | Backend Status | Frontend Status | Integration Status | Notes |
|---------|---------------|-----------------|-------------------|-------|
| **UI Shell & Navigation** | ✅ N/A | ✅ Completed | ✅ Completed | Layout structure with sidebar and content areas |
| **Project Management** | ✅ Completed | ✅ Completed | 🟡 Partial | Project creation works, deletion has issues |
| **Chat Interface** | 🟡 Partial | ✅ Completed | 🟡 Partial | Messages display but don't persist to backend |
| **Document Management** | ✅ Completed | ✅ Completed | ✅ Completed | Document viewing and processing fully implemented |
| **Project Containment** | ✅ Completed | ✅ Completed | ✅ Completed | Architecture implemented with proper flows |
| **File Management** | ✅ Completed | ✅ Completed | ✅ Completed | Upload, linking, and attachment fully functional |
| **Universal Search** | 🟡 Pending | ✅ Completed | 🟡 Mock Only | 3-checkbox search interface with probability scoring |
| **System & Models Panel** | 🟡 Pending | 🟡 Planned | 🟡 Pending | Service monitoring and model switching interface |
| **User Prompts** | ✅ Completed | ✅ Completed | ✅ Completed | Create, activate, and manage prompts by project |
| **Context Controls** | 🟡 Pending | ✅ Completed | 🟡 Pending | UI implemented, backend integration pending |
| **Document Processing** | ✅ Completed | ✅ Completed | ✅ Completed | Processing pipeline with status tracking |
| **Vector Database** | ✅ Completed | N/A | ✅ Completed | pgvector integrated for semantic search |
| **Admin Tools** | ✅ Completed | ✅ Completed | ✅ Completed | Database management and system diagnostics |
| **GPU Monitoring** | ✅ Completed | ✅ Completed | ✅ Completed | Real-time utilization visualization |
| **NeMo Integration** | 🟡 Mock Only | N/A | 🟡 Pending | Mock implementation for development |
| **RAG Implementation** | 🟡 Partial | 🟡 Pending | 🟡 Pending | Vector search implemented, retrieval integration pending |
| **Reasoning Modes** | 🟡 Pending | ✅ UI Done | 🟡 Pending | UI completed, backend implementation pending |

**Legend**:
- ✅ Completed: Feature is fully implemented and working
- 🟡 Partial/Pending: Feature is partially implemented or planned
- ❌ Not Started: Feature implementation not yet begun
- N/A: Not applicable

## Key Features

### Universal Search Interface
- Multi-domain search across Chats, Knowledge Base (processed documents), and Documents
- 3-checkbox selection system for targeted search scope
- Probability scoring (0-100%) for all search results
- Knowledge base results with contextual snippets and expandable detail
- Direct document download functionality without in-app viewers
- Project-aware search results with appropriate context

### System & Model Management (Planned)
- Real-time monitoring of system services (FastAPI, PostgreSQL, pgvector)
- Service control interface with start/stop/restart capabilities
- AI model management for Ollama and NeMo models
- Dynamic model loading, unloading, and switching
- Environment monitoring (Python, Node.js, CUDA versions)
- Hardware performance tracking and optimization settings

### Project-Centered Containment
- Projects serve as self-contained knowledge environments
- Each project maintains its own set of chats
- Documents can be attached to specific projects
- Project-specific settings including custom prompts
- Clear visual hierarchy showing project context

### Enhanced Document Processing with NeMo
- Superior document understanding with NVIDIA NeMo Document AI
- Hierarchical indexing preserves document structure
- Layout analysis for better table and diagram comprehension
- Structure-aware processing for improved context retention

### Prioritized Document Retrieval
- Project-attached documents receive special treatment in retrieval
- Hierarchical indexing preserves document structure
- Prioritized ranking in vector search results
- Enhanced context utilization for deeper understanding
- Visual indicators showing document relevance and priority

### Adaptive Context Controls
- Preset modes for different interaction styles (Project Focus, Deep Research, Quick Response)
- Custom configuration for document sources and memory scope
- Context depth slider balancing conciseness vs. comprehensiveness
- Performance-aware settings optimized for target hardware

### User Prompt System
- Create and manage custom prompts for specialized assistant behavior
- One-click activation of saved prompts
- Visual indicators for active prompts
- Custom instructions for different project contexts

### File Management System
- Project-specific file management with containment
- Global file repository with search capabilities
- File attachment to projects with priority settings
- File upload with custom descriptions and tags
- Status indicators for processing and project attachment

### Admin Tools & System Management
- Database reset and maintenance tools via settings panel
- System diagnostics and status reporting
- Log viewing and export capabilities
- User preferences and configuration settings
- Documentation and help resources

## Setup Instructions

### Prerequisites
1. PostgreSQL 17 with pgvector extension
2. Python 3.10 or higher
3. Node.js 18+ and npm
4. Visual Studio 2022 with C++ workload (for building pgvector)
5. CUDA Toolkit 12.0+ for GPU acceleration (optional)

### Quick Start
The easiest way to start the application is using the provided batch file:

1. Make sure PostgreSQL service is running
2. Run `start_services.bat` - this will:
   - Check and initialize the PostgreSQL database
   - Attempt to set up the pgvector extension if needed
   - Create required data directories
   - Start the FastAPI backend server
   - Start the React frontend development server

Once started, you can access:
- Frontend UI: http://localhost:5173
- Backend API docs: http://localhost:8000/docs

### Manual Setup

#### Backend Setup
1. Navigate to backend directory: `cd backend`
2. Create Python virtual environment:
```
python -m venv venv
venv\Scripts\activate
```
3. Install dependencies:
```
pip install -r requirements.txt
```
4. Set up environment variables (copy .env.example to .env and edit)
5. Initialize database:
```
python -m app.db.init_db
```
6. Start the backend server:
```
uvicorn app.main:app --reload
```

#### Frontend Setup
1. Navigate to frontend directory: `cd frontend`
2. Install dependencies:
```
npm install
```
3. Start the development server:
```
npm run dev
```

### pgvector Setup
The pgvector extension is required for vector search capabilities. If `start_services.bat` cannot automatically install it:

1. Download pgvector from https://github.com/pgvector/pgvector
2. Build and install following the repository instructions
3. Enable the extension in your database:
```sql
CREATE EXTENSION vector;
```

## Usage

1. Access the application at http://localhost:5173
2. Create projects to organize your knowledge
3. Upload and process documents (processed with NeMo for enhanced understanding)
4. Attach key documents to projects for prioritized retrieval
5. Create chats within projects for focused conversations
6. Chat with the AI assistant within project contexts
7. Adjust context controls to balance depth vs. speed or expand beyond project boundaries
8. Select reasoning modes appropriate for your questions
9. Monitor hardware utilization during operation

## Development

### Running Tests
#### Frontend tests
```
cd frontend
npm test
```
#### Backend tests
```
cd backend
pytest
```

### Building for Production
#### Frontend build
```
cd frontend
npm run build
```
Backend will serve the static files from the build directory

## Implementation Challenges & Solutions

### 1. Project-Centered Containment
**Challenge**: Creating intuitive project containment while allowing selective expansion  
**Solution**:
- Implement clear project boundaries in UI and database
- Design context controls for explicit opt-in to broader knowledge
- Create visual indicators for containment and expansion
- Build project-specific chat and document management
- Implement priority boost for project-attached documents

### 2. Creating a Clean, Elegant UI
**Challenge**: Building a powerful interface without overwhelming users  
**Solution**:
- UI-first development approach ensures polished experience
- Collapsible context controls keep the interface clean
- Preset modes simplify complex operations
- Progressive disclosure of advanced features
- Clear visual hierarchy and consistent design language

### 3. Windows Compatibility with NVIDIA Components
**Challenge**: Running NeMo Document AI efficiently on Windows  
**Solution**:
- Hybrid deployment strategy using Docker for NeMo components
- Native TensorRT integration for inference optimization
- Hardware-aware configuration for maximum performance
- Minimal containerization to preserve native performance

### 4. Document Context Preservation
**Challenge**: Standard chunking loses document structure and deep context  
**Solution**:
- Implement hierarchical document indexing with NeMo Document AI
- Preserve section relationships and structure
- Store multiple granularity levels for each document
- Prioritize project-attached documents in retrieval

### 5. File-Project Linking Persistence
**Challenge**: Files linked to projects lost their associations when navigating between views  
**Solution**:
- Created robust type system with normalizing functions for project IDs
- Implemented consistent serialization/deserialization for localStorage persistence
- Added extensive validation and error handling for edge cases
- Fixed synchronization between MainFileManager and ProjectFileManager
- Enhanced event handling for proper component updates

### 6. Hardware-Optimized Reasoning
**Challenge**: Balancing reasoning capabilities with hardware constraints  
**Solution**:
- Optimize for 30-35B models with TensorRT for reasonable performance
- Implement multiple reasoning modes with appropriate context sizing
- Use CUDA optimization for vector operations
- Implement progressive response generation for perceived responsiveness

## License

[MIT License](LICENSE)

## Conclusion

This transition from Gradio to a FastAPI+React architecture represents a significant improvement in the AI Assistant's capabilities, performance, and user experience. By implementing project-centered containment, prioritized document retrieval, and hardware-optimized reasoning capabilities, we deliver a powerful knowledge management system that respects user privacy while providing sophisticated AI capabilities.

The project-centered containment approach creates an intuitive organizational structure that matches real-world workflows, while the selective expansion capabilities provide flexibility when needed. The NeMo and TensorRT integrations maximize hardware utilization, allowing for more complex reasoning and document understanding than typical local deployments.