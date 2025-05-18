# AI Assistant Development Guide

## Project Overview

This AI Assistant is a FastAPI + React application providing a local AI assistant with project-centered containment, prioritized document retrieval, and adaptive reasoning capabilities.

## Development Workflow
**IMPORTANT** The development environment is in UBUNTU WSL running in a windows version of Visual Studo code. While the APPLICATION runs in a windows python Venv environment (venv_nemo)
** IMPORTANT ** read the scope.md / Implementation.md / readme.md / devlog.md for project instructions **

### Setup & Installation

#### Prerequisites
- PostgreSQL 17 with pgvector extension
- Python 3.10+
- Node.js 18+
- NVIDIA GPU (RTX 4090 recommended)
- CUDA Toolkit 12.0+ (for GPU acceleration)

#### Quick Start
```bash
# Start all services
./start_services.bat

# Stop all services
./stop_services.bat
```

#### Manual Backend Setup
```bash
cd backend
# The project uses venv_nemo as its virtual environment
python -m venv venv_nemo
venv_nemo\Scripts\activate
pip install -r requirements.txt
python -m app.db.init_db
uvicorn app.main:app --reload --port 8000
```

#### Manual Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Development Commands

#### Frontend
```bash
# Start development server
cd frontend
npm run dev

# Build for production
npm run build

# Lint code
npm run lint
```

#### Backend
```bash
# Start development server with virtual environment
cd backend
..\venv_nemo\Scripts\activate
uvicorn app.main:app --reload --port 8000

# Initialize database
python -m app.db.init_db
```

## Architecture Overview

### Tech Stack
- **Frontend**: React + TypeScript with Vite build system
- **State Management**: Redux Toolkit
- **CSS Framework**: Tailwind CSS
- **Backend**: FastAPI + SQLAlchemy + PostgreSQL with pgvector
- **LLM Integration**: Ollama with TensorRT optimization
- **Document Processing**: NeMo Document AI, LlamaIndex, PyPDF, docx2txt

### Core Data Models

#### Project
The central organizational unit. Projects act as self-contained knowledge environments.
- `id`: UUID string
- `name`: Project name
- `description`: Project description
- Relationships: Chats, Documents, UserPrompts

#### Document
Files uploaded to the system for processing and retrieval.
- `id`: UUID string
- `filename`: Original filename
- `filepath`: Path to stored file
- `filetype`: File type/extension
- `is_processed`: Whether the document has been processed
- `is_active`: Whether the document is active in the context
- Relationships: Projects, Chunks

#### Chat
Project-specific conversation container.
- `id`: UUID string
- `name`: Chat name
- `project_id`: Linked project
- Relationships: Messages, Project

#### UserPrompt
Custom instructions for the assistant's behavior.
- `id`: UUID string
- `name`: Prompt name
- `content`: Prompt content
- `is_active`: Whether prompt is currently active
- `project_id`: Optional linked project

### API Endpoints

#### Projects API
- `GET /api/projects`: List all projects
- `POST /api/projects`: Create a new project
- `GET /api/projects/{id}`: Get project details
- `PUT /api/projects/{id}`: Update a project
- `DELETE /api/projects/{id}`: Delete a project

#### Files API
- `POST /api/files/upload`: Upload a new file
- `GET /api/files`: List all files
- `GET /api/files/project/{id}`: Get files for a project
- `POST /api/files/search`: Search files by content

#### Chats API
- `GET /api/chats/project/{id}`: Get chats for a project
- `POST /api/chats`: Create a new chat
- `GET /api/chats/{id}`: Get chat details
- `POST /api/chats/{id}/messages`: Send a message

#### User Prompts API
- `GET /api/user-prompts`: List all user prompts
- `POST /api/user-prompts`: Create a new user prompt
- `PUT /api/user-prompts/{id}`: Update a user prompt
- `PUT /api/user-prompts/{id}/activate`: Activate a user prompt

### Frontend Structure

#### Key Components
- `App.tsx`: Main application component
- `MainLayout`: Layout wrapper with sidebar
- `ProjectManagerView`: Project overview
- `ChatView`: Chat interface
- `DocumentView`: Document viewer
- `MainFileManager`: Global file manager
- `ProjectFileManager`: Project-specific file manager

#### Services
- `projectService`: Project CRUD operations
- `fileService`: File upload and management
- `chatService`: Chat and message management
- `userPromptService`: Custom prompts management

### Core Features

1. **Project-Centered Containment**
   - Projects as self-contained knowledge environments
   - Documents attached to specific projects
   - Project-specific chats and settings

2. **Document Processing**
   - Hierarchical document indexing with NeMo
   - PDF, DOCX, and text file support
   - Semantic vector search with pgvector

3. **Prioritized Document Retrieval**
   - Project-attached documents given higher priority
   - Context-aware document retrieval
   - Hierarchical document structure preservation

4. **User Prompt System**
   - Create and manage custom prompts
   - Project-specific prompt activation
   - Visual indicators for active prompts

## Implementation Status

The project is partially implemented with the following status:
- Project management: Completed
- Chat interface: Partial implementation
- Document management: Partial implementation
- Document processing: Implemented with mock NeMo
- Vector search: Implemented with pgvector
- User prompts: Completed