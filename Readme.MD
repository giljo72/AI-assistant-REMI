# AI Assistant: FastAPI + React Implementation

A private, local AI assistant with project-centered containment, prioritized document retrieval, and adaptive reasoning capabilities optimized for high-performance hardware.

## Project Overview

This AI Assistant provides:

- **Project-Centered Containment**: Each project is a self-contained knowledge environment with its own chats and attached documents
- **Selective Knowledge Expansion**: Opt-in controls to expand beyond project boundaries when needed
- **Prioritized Document Retrieval**: Project-attached documents receive higher priority in retrieval
- **Hierarchical Document Processing**: Improved document understanding using NeMo
- **Tiered Memory System**: Adaptive context controls for flexible knowledge access
- **Multiple Reasoning Modes**: Different reasoning depths optimized for hardware capabilities
- **Complete Document Lifecycle**: Upload, process, retrieve, view, and delete documents
- **RAG (Retrieval Augmented Generation)**: Enhanced with PostgreSQL+pgvector
- **Voice Interaction**: Using Whisper for transcription
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

## Key Features

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

### Enhanced Reasoning Capabilities
- Multiple reasoning modes optimized for 30-35B parameter models with TensorRT
- Standard: Balanced analysis with normal context depth
- Comprehensive: Multi-step reasoning with expanded context
- Expert: Detailed chains of thought with maximum context utilization
- Hardware monitoring to optimize performance

### Future Expansion: External Services
The system is architected for future (optional) integration with external services:
- External API verification (Claude, ChatGPT) for complex queries
- Web search capabilities for time-sensitive information
- Privacy-preserving controls for external service usage
- Clear visual indicators when using external resources

## UI-First Development Approach

The project follows a UI-first approach with progressive enhancement:

1. **UI Shell & Navigation**: Build the complete visual interface with static data
2. **Project-Centered Components**: Implement containment architecture in UI
3. **Context Controls & Memory System**: Create tiered memory UI and controls
4. **Basic Backend Services**: Implement essential backend functionality
5. **Backend-Frontend Integration**: Connect UI to real services
6. **NVIDIA Integration & Enhancement**: Connect advanced features and optimizations
7. **Testing and Refinement**: Polish the user experience based on feedback

This approach ensures a consistent and polished user experience throughout development.

## Setup Instructions

### Prerequisites
1. PostgreSQL 17 with pgvector extension
2. Ollama with Llama-3 models (recommend 34B for optimal reasoning/performance balance)
3. Python 3.10 or higher
4. Node.js 18+ and npm
5. Visual Studio 2022 with C++ workload (for building pgvector)
6. CUDA Toolkit 12.0+ for GPU acceleration
7. Docker Desktop (optional, for NeMo Document AI on Windows)

### Backend Setup
1. Clone this repository
2. Navigate to backend directory: `cd backend`
3. Create Python virtual environment:
```
python -m venv venv
venv\Scripts\activate
```
4. Install dependencies:
```
pip install -r requirements.txt
```
5. Run NVIDIA setup script:
```
python -m scripts.setup_tensorrt
python -m scripts.setup_nemo
```
6. Set up environment variables (copy .env.example to .env and edit)
7. Initialize database:
```
python -m scripts.setup_database
```
8. Start the backend server:
```
uvicorn app.main:app --reload
```

### Frontend Setup
1. Navigate to frontend directory: `cd frontend`
2. Install dependencies:
```
npm install
```
3. Start the development server:
```
npm start
```

## Usage

1. Access the application at http://localhost:3000
2. Create projects to organize your knowledge
3. Upload and process documents (processed with NeMo for enhanced understanding)
4. Attach key documents to projects for prioritized retrieval
5. Create chats within projects for focused conversations
6. Chat with the AI assistant within project contexts
7. Adjust context controls to balance depth vs. speed or expand beyond project boundaries
8. Select reasoning modes appropriate for your questions
9. Monitor hardware utilization during operation

## Project Status

Current implementation status:

| Feature | Status | Notes |
|---------|--------|-------|
| **UI Shell & Navigation** | 🟢 Completed | Layout structure with sidebar and content areas |
| **Project Management UI** | 🟡 In Progress | Basic sidebar and project manager implemented |
| **Chat Interface UI** | 🟡 In Progress | Placeholder chat view created |
| **Document Management UI** | 🟡 In Progress | Placeholder document view created |
| **Project-Centered Containment** | 🟡 In Progress | Project structure created, functionality pending |
| **Context Controls UI** | 🟡 Pending | Architecture defined |
| **Backend Foundation** | 🟡 Pending | Waiting for UI phase completion |
| **NeMo Integration** | 🟡 Pending | Architecture defined |
| **TensorRT Optimization** | 🟡 Pending | Architecture defined |
| **RAG Implementation** | 🟡 Pending | Architecture defined |
| **Reasoning Modes** | 🟡 Pending | UI designs created |

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

### 5. Hardware-Optimized Reasoning
**Challenge**: Balancing reasoning capabilities with hardware constraints  
**Solution**:
- Optimize for 30-35B models with TensorRT for reasonable performance
- Implement multiple reasoning modes with appropriate context sizing
- Use CUDA optimization for vector operations
- Implement progressive response generation for perceived responsiveness

### 6. Architecture for Future Expansion
**Challenge**: Building for offline use while enabling future external integration  
**Solution**:
- Abstract provider interfaces for reasoning and retrieval
- Clear separation between local and external components
- Privacy-preserving design patterns for future implementation
- Visual indicators for knowledge source transparency

## Workflow Overview

The application follows a structured workflow:

1. **Welcome Screen**: Project list, system status, and global navigation
2. **Project Management**: Create, modify, and delete projects; manage project-specific chats and documents
3. **Chat Interface**: Interact with AI within project context using different reasoning modes
4. **Document Management**: Upload, process, and attach documents to projects with prioritization
5. **Context Controls**: Select interaction mode, adjust context depth, choose knowledge sources
6. **System Settings**: Configure models, monitor hardware performance, manage preferences

## NVIDIA Integration

The project leverages key NVIDIA technologies:

- **NeMo Document AI**: Enhanced document understanding with structure preservation
- **TensorRT**: Hardware-optimized inference for 30-35B models
- **CUDA Optimization**: Performance tuning for RTX 4090
- **Hybrid Deployment**: Native + Docker approach for maximum performance on Windows

## Development Notes

For development purposes, a mock NeMo implementation is provided to enable
progress without requiring the full NeMo installation. This allows for
frontend and backend development while the full NeMo integration can be
addressed at a later stage.

## License

[MIT License](LICENSE)

## Conclusion

This transition from Gradio to a FastAPI+React architecture represents a significant improvement in the AI Assistant's capabilities, performance, and user experience. By implementing project-centered containment, prioritized document retrieval, and hardware-optimized reasoning capabilities, we deliver a powerful knowledge management system that respects user privacy while providing sophisticated AI capabilities.

The project-centered containment approach creates an intuitive organizational structure that matches real-world workflows, while the selective expansion capabilities provide flexibility when needed. The NeMo and TensorRT integrations maximize hardware utilization, allowing for more complex reasoning and document understanding than typical local deployments.