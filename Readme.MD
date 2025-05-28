# AI Assistant

A fully private, local AI assistant with multi-model support, document understanding, and project-based knowledge management. All processing happens on your hardware - your data never leaves your system.

## What It Does

The AI Assistant provides ChatGPT-like capabilities on your local machine with:
- **Multiple AI Models**: Switch between fast responses, deep reasoning, or code generation
- **Document Understanding**: Upload PDFs, Word docs, and spreadsheets for AI-powered search
- **Project Organization**: Keep different projects' knowledge separate and organized
- **Real-time Monitoring**: See exactly what resources the AI is using
- **Complete Privacy**: Everything runs locally - no cloud, no data collection

## Quick Start

### Prerequisites
- Windows 11 with WSL2
- NVIDIA RTX GPU (16GB+ VRAM recommended)
- 32GB+ RAM
- PostgreSQL 17
- Docker Desktop
- Python 3.10+
- Node.js 18+

### Installation

1. **Clone and Setup**
   ```bash
   git clone <repository>
   cd assistant
   python -m venv venv_nemo
   venv_nemo\Scripts\activate
   ```

2. **Install Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   cd ../frontend
   npm install
   ```

3. **Initialize Database**
   ```bash
   cd backend
   python -m app.db.init_db
   ```

4. **Start Services**
   ```bash
   # From project root
   startai.bat
   ```
   This launches all services and opens the browser automatically.

5. **Stop Services**
   ```bash
   stopai.bat
   ```

## Basic Usage

### Creating a Project
1. Click "+" in the sidebar
2. Name your project
3. Add documents via drag-and-drop
4. Start chatting with project context

### Switching AI Models
1. Click the "?" button in header
2. Select desired model:
   - **Qwen 2.5**: Default, best for general use
   - **Mistral-Nemo**: Fast responses
   - **DeepSeek Coder**: Code generation
   - **Llama 70B**: Deep reasoning (solo mode)

### Document Search
1. Click search icon
2. Select search scope (Chats/Knowledge/Documents)
3. Enter query
4. View results with relevance scores

## Key Features

- **100% Local**: No internet required after setup
- **Multi-Model**: 4 different AI models for different tasks
- **Smart Search**: Semantic understanding of documents
- **Project Isolation**: Keep client data separate
- **Resource Monitoring**: Real-time GPU/CPU/RAM usage
- **Visual Context**: See what influences AI responses

## Architecture Overview

```
Frontend (React + TypeScript)
    ↓
Backend (FastAPI + Python)  
    ↓
PostgreSQL + pgvector (Semantic Search)
    ↓
AI Services (Ollama + NVIDIA NIM)
```

## Documentation

- **Vision & Goals**: See [Scope.md](Scope.md)
- **Technical Details**: See [Implementation.md](implementation.md)
- **Development Log**: See [Devlog.md](Devlog.md)
- **File Structure**: See [Project_Structure.md](Project_Structure.md)

## Common Issues

### GPU Not Detected
- Ensure NVIDIA drivers are updated
- Check Docker Desktop GPU support
- Verify CUDA installation

### Services Won't Start
- Check PostgreSQL is running
- Verify Docker Desktop is running
- Ensure ports 3000, 8000, 8081, 11434 are free

### Model Loading Fails
- Check available VRAM (24GB recommended)
- Try unloading other models first
- Use smaller models if needed

## Contributing

This is a private project, but if you have access:
1. Create feature branch
2. Make changes
3. Test thoroughly
4. Submit PR with clear description

## License

Private project - all rights reserved.

---

For detailed technical information, consult the documentation files in the repository.