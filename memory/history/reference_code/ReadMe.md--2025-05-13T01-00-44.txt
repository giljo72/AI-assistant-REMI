# AI Assistant Project
# File version May 7th 2025

A private, local AI assistant with project-centered organization, document memory, and tiered knowledge retrieval.

## Project Overview

This AI Assistant provides:
- Project-centered organization with multiple chats per project
- Tiered memory system with project-specific, global vector, and cross-project memory
- Document processing for various file types (TXT, PDF, DOCX, XLS, etc.)
- File tagging (Private/Business/Either) with custom descriptions
- Complete document lifecycle management (upload, process, retrieve, view, delete)
- RAG (Retrieval Augmented Generation) with PostgreSQL+pgvector
- Voice interaction using Whisper
- Visual indicators for document/prompt usage and memory scope

## Technology Stack

- **Database**: PostgreSQL 17 with pgvector
- **Web Framework**: Gradio 5.29.0
- **LLM Interface**: Ollama
- **RAG Framework**: LangChain
- **Voice Processing**: Whisper
- **Python Environment**: venv (Python 3.10+)

## Setup Instructions

### Prerequisites:
1. PostgreSQL 17 with pgvector extension
2. Ollama with llama3:8b model
3. Python 3.10 or higher
4. Visual Studio 2022 with C++ workload (for building pgvector)

### Installation:
1. Clone this repository
2. Create Python virtual environment:
```
python -m venv venv
venv\Scripts\activate
```
3. Install dependencies:
```
pip install -r requirements.txt
```
4. Install and configure PostgreSQL:
   - Install PostgreSQL 17
   - Compile and install pgvector extension
   - Create ai_assistant database
   - Enable vector extension
5. Install Ollama and download models:
```
ollama pull llama3:8b
```
6. Run database setup script:
```
python -m scripts.setup_database
```

## Starting the Assistant

There are two ways to launch the AI Assistant:

### 1. Automated Launcher (Recommended)
This method automatically starts all required services and launches the AI Assistant:

1. Run `Start_AI.bat` from your desktop or the project directory
   - The launcher will request administrator privileges to start the PostgreSQL service
   - It will check and start all required services (PostgreSQL and Ollama)
   - Once all services are running, it will automatically launch the Gradio interface

### 2. Manual Startup
If you prefer to start services individually:

1. Ensure PostgreSQL is running
2. Start Ollama: `ollama serve`
3. Start the AI Assistant:
```
venv\Scripts\activate
python -m src.gradio.app
```

## Stopping the Assistant

There are two ways to shut down the AI Assistant:

### 1. Automated Shutdown (Recommended)
This method properly terminates all services and processes:

1. Run `Stop-AI.bat` from your desktop or the project directory
   - The script will terminate all assistant-related processes
   - It will properly stop the PostgreSQL service
   - A summary will be displayed showing what was shut down

### 2. Manual Shutdown
If you prefer to stop services individually:

1. Close the Gradio interface (browser window)
2. Stop Ollama (if started manually)
3. Stop PostgreSQL service

## Key Features

### Project-Centered Organization
- Create projects to organize related documents and chats
- Add custom prompts to guide the AI assistant
- Create multiple chat sessions within each project
- Attach documents specifically to projects for targeted knowledge
- Each project and chat has dedicated management controls

### Tiered Memory System
- Level 1: Project-specific memory (only search within project chats and attached documents)
- Level 2: Extended vector database memory (all indexed documents)
- Level 3: Complete memory (all chats across all projects)
- Toggle between memory levels with visual indicators

### Document Management
- Upload, process, and delete documents
- Support for batch uploads with individual metadata per file
- Full-text search with PostgreSQL integration
- Tag documents as Private, Business, or Both
- Add custom descriptions
- View document content with document download functionality
- Secure local storage

### Chat Interface
- Chat with AI within project context
- Visual indicators for document sources and memory scope
- Voice input support via Whisper
- Document source visualization showing which documents influenced AI responses
- Clean, modern dark interface with gold accents

### RAG Context Visualization
- See exactly which documents influenced AI responses
- View document relevance scores
- Explore and preview document sources
- View full documents with highlighted relevant sections

## Architecture Overview

The AI Assistant follows a layered architecture:

1. **UI Layer (Gradio)**: Handles user interactions and display
2. **Service Layer**: Coordinates between UI and backend components
   - Manages application state and session data
   - Provides structured access to backend functionality
   - Adapts backend responses for UI consumption
3. **Backend Layer**: Implements core functionality
   - Document processing
   - Vector storage
   - LLM integration
   - RAG implementation

This layered approach facilitates the migration from Streamlit to Gradio while maintaining the same backend functionality.

## Current Status (May 7, 2025)

### Implementation Progress

| Feature | Status | Notes |
|---------|--------|-------|
| **UI Framework Migration** | 🟢 | Migrated from Streamlit to Gradio 5.29.0 |
| **Project-Centric UI** | 🟢 | Implemented sidebar with projects and chats |
| **Service Layer Implementation** | 🟡 | Service factory implemented with initial services |
| **Project Management Controls** | 🟡 | UI elements created, functionality in progress |
| **Tiered Memory System** | 🟡 | UI controls implemented, backend pending |
| **Document Management** | 🟡 | Basic UI implemented, service integration in progress |
| **Chat Interface** | 🟢 | UI implemented with proper styling |
| **Voice Integration** | 🔴 | Design completed, implementation pending |
| **Database Integration** | 🟢 | Core schema implemented and verified |
| **Document Processing** | 🟢 | Implementation completed |
| **LLM Integration** | 🟡 | Basic setup completed, service integration pending |
| **RAG Implementation** | 🟡 | Core functionality implemented, memory tiers pending |
| **Document Source Visualization** | 🔴 | Planned for final phase |

**Legend**:
- 🟢 Complete
- 🟡 Partially Implemented
- 🔴 Not Started

### Current Focus

The current development focus is on implementing the service layer and connecting it with the UI components. We have successfully:

- Migrated to Gradio 5.29.0 UI framework
- Implemented core service factory pattern
- Created database schema with vector