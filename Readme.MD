# AI Assistant: Multi-Model Production System

[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)](https://github.com)
[![Architecture](https://img.shields.io/badge/Architecture-Multi--Model-blue)](https://github.com)
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20Local-orange)](https://github.com)
[![Hardware](https://img.shields.io/badge/Hardware-RTX%204090%20Optimized-green)](https://github.com)

A complete, privacy-focused AI assistant with unified multi-model architecture, providing enterprise-grade capabilities while maintaining complete local control and data ownership.

## 🎯 Key Features

### 🚀 **Multi-Model AI Architecture**
- **4 Production AI Models + Always-On Embeddings**: Qwen 2.5 32B, Llama 3.1 70B (NIM), Mistral-Nemo 12B, DeepSeek-Coder 16B + NVIDIA Embeddings
- **Unified Interface**: Single API routing to NVIDIA NIM and Ollama backends
- **Intelligent Routing**: Automatic service selection based on model type and performance requirements
- **Real-time Management**: Load, unload, and switch between models with live status monitoring

### 🔒 **Complete Privacy & Local Control**
- **100% Local Processing**: No cloud dependencies or external API calls
- **Data Ownership**: All documents and conversations remain on your hardware
- **Offline Operation**: Full functionality without internet connectivity
- **Enterprise Security**: Container isolation and encrypted storage

### 📁 **Project-Centered Organization**
- **Self-Contained Projects**: Each project is an isolated knowledge environment
- **Context Optimization**: Project boundaries improve performance and relevance
- **Flexible Expansion**: Option to search across projects when needed
- **Intuitive Workflow**: Matches real-world project organization

### 🔍 **Advanced Search & Retrieval**
- **Universal Search**: Search across chats, knowledge base, and documents simultaneously
- **Semantic Understanding**: pgvector-powered similarity search with enterprise embeddings
- **Relevance Scoring**: 0-100% probability scores for all results
- **Context Expansion**: Expandable result snippets with full document access

## 🏗️ Architecture Overview

### **Service Architecture**
```
Windows 11 Production Environment
├── Docker Desktop (WSL2 Backend)
│   ├── nim-embeddings:8001 → NVIDIA NV-EmbedQA-E5-V5
│   └── nim-llm:8002 → Llama 3.1 70B (Optional, TensorRT)
├── Ollama Service:11434
│   ├── Mistral-Nemo 12B (Primary workhorse)
│   ├── DeepSeek-Coder V2 16B (Code specialist)
│   ├── Qwen 2.5 32B (Advanced reasoning)
│   └── Llama 3.1 70B (Complex queries)
├── PostgreSQL:5432 (Document storage + pgvector search)
├── FastAPI Backend:8000 (Unified LLM routing)
└── React Frontend:3000 (Model management interface)
```

### **AI Model Lineup**
| Model | Type | VRAM | Use Case | Status |
|-------|------|------|----------|--------|
| **Mistral-Nemo 12B** | Ollama | 7.1GB | Primary workhorse | ✅ Active |
| **DeepSeek-Coder V2 16B** | Ollama | 9GB | Code generation | ✅ Ready |
| **Qwen 2.5 32B** | Ollama | 19GB | Advanced reasoning | ✅ Ready |
| **Llama 3.1 70B** | Ollama | 40GB | Complex queries | ⚡ On-demand |
| **NVIDIA Embeddings** | NIM | 1.2GB | Semantic search | 🔄 Always running |
| **NeMo Document AI** | Mock | 0GB | Document processing | ✅ Ready |

## 🚀 Quick Start

### **Prerequisites**
- **Hardware**: NVIDIA RTX 4090 (24GB VRAM), 64GB RAM recommended
- **OS**: Windows 11 with WSL2 enabled
- **Software**: Docker Desktop, PostgreSQL 17, Node.js 18+, Python 3.10+

### **Installation**

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd assistant
   ```

2. **Setup Environment**
   ```bash
   # Create Python virtual environment
   python -m venv venv_nemo
   venv_nemo\Scripts\activate
   
   # Install Python dependencies
   cd backend
   pip install -r requirements.txt
   
   # Install Node.js dependencies
   cd ..\frontend
   npm install
   ```

3. **Setup Database**
   ```bash
   # Initialize PostgreSQL with pgvector
   cd ..\backend
   python -m app.db.init_db
   ```

4. **Configure Services**
   ```bash
   # Install Ollama models
   python install_models.py
   
   # Configure NGC API key (if not already set)
   # Add to .env file: NGC_API_KEY=your_key_here
   
   # Test NIM integration
   python test_nim_integration.py
   
   # Setup will automatically handle Docker containers
   ```

### **Launch Application**

**Easy Start** (Recommended):
```bash
# Start all services automatically
startai.bat
```

**Manual Start**:
```bash
# Backend
cd backend
..\venv_nemo\Scripts\activate
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm run dev

# Access application
# http://localhost:3000
```

**Stop Services**:
```bash
# Stop all services cleanly
stopai.bat
```

## 💻 Usage Guide

### **Model Management**
1. **Access System Panel**: Click the "❓" button in the top navigation
2. **Switch Models**: Select desired model from the AI Models tab
3. **Monitor Status**: View real-time memory usage and performance metrics
4. **Load Models**: Pull new models or start/stop services as needed

### **Project Workflow**
1. **Create Project**: Click "Add Project" to create a new knowledge environment
2. **Upload Documents**: Use the file manager to upload and process documents
3. **Start Chat**: Create a new chat within your project
4. **Select Model**: Choose the appropriate AI model for your task
5. **Enhanced Conversations**: Benefit from project-specific context and document retrieval

### **Document Processing**
- **Supported Formats**: PDF, DOCX, TXT, and more
- **Automatic Processing**: Documents are automatically chunked and indexed
- **Semantic Search**: Advanced vector search across all document content
- **Context Integration**: Documents automatically enhance chat conversations

## 🛠️ Development

### **Development Environment**
- **Code Editing**: WSL2 Ubuntu environment for development
- **Service Testing**: Cross-platform connectivity to Windows services
- **Hot Reload**: Both frontend and backend support live code updates
- **Debugging**: Comprehensive logging and error tracking

### **Project Structure**
```
assistant/
├── frontend/                 # React + TypeScript application
│   ├── src/
│   │   ├── components/      # UI components
│   │   ├── services/        # API integration
│   │   ├── store/          # Redux state management
│   │   └── types/          # TypeScript definitions
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── api/            # REST API endpoints
│   │   ├── core/           # Core services (NIM, Ollama, etc.)
│   │   ├── db/             # Database models and repositories
│   │   ├── services/       # Business logic services
│   │   └── schemas/        # Pydantic models
├── docker-compose.yml      # NVIDIA NIM container configuration
├── startai.bat            # Automated startup script
└── stopai.bat             # Automated shutdown script
```

### **API Endpoints**
```
# Project Management
GET    /api/projects              # List all projects
POST   /api/projects              # Create new project
GET    /api/projects/{id}         # Get project details
PUT    /api/projects/{id}         # Update project
DELETE /api/projects/{id}         # Delete project

# Chat Operations
GET    /api/chats/project/{id}    # Get project chats
POST   /api/chats                 # Create new chat
POST   /api/chats/{id}/generate   # Generate AI response

# File Management
POST   /api/files/upload          # Upload document
GET    /api/files/project/{id}    # Get project files
POST   /api/files/search          # Semantic search

# System Control
GET    /api/system/status         # Get system health
POST   /api/system/models/load    # Load AI model
POST   /api/system/models/switch  # Switch active model
```

## ⚡ Performance Optimization

### **Memory Management (RTX 4090 - 24GB VRAM)**
- **Conservative Mode**: 1 model + embeddings (6-9GB used)
- **Balanced Mode**: 2 models + embeddings (13-16GB used)
- **Maximum Mode**: 70B model + embeddings (19GB used)
- **Automatic Management**: Dynamic loading/unloading based on usage

### **Hardware Utilization**
- **GPU Acceleration**: All models utilize CUDA cores and Tensor cores
- **TensorRT Optimization**: NVIDIA NIM models are TensorRT-optimized
- **Memory Efficiency**: 4-bit quantization for larger models
- **Parallel Processing**: Concurrent embedding and inference operations

## 🔧 Configuration

### **Environment Variables**
```bash
# Ollama Configuration
OLLAMA_HOST=0.0.0.0:11434
OLLAMA_MODELS=C:\Users\{username}\.ollama\models

# NVIDIA NIM Configuration  
NGC_API_KEY=your_ngc_api_key_here

# Database Configuration
DATABASE_URL=postgresql://user:pass@localhost:5432/ai_assistant
```

### **Model Configuration**
Models are automatically configured but can be customized:
- **Ollama Models**: Pull via `ollama pull <model-name>`
- **NIM Containers**: Configure in `docker-compose.yml`
- **Memory Limits**: Adjust container resource limits as needed

## 🆘 Troubleshooting

### **Common Issues**

**Service Connection Issues**:
```bash
# Check service status
docker ps                    # NIM containers
ollama list                  # Ollama models  
pg_ctl status               # PostgreSQL

# Restart services
startai.bat                 # Restart all services
```

**Model Loading Issues**:
- Ensure sufficient VRAM available
- Check NVIDIA drivers are updated
- Verify NGC API key for NIM containers

**Performance Issues**:
- Monitor GPU memory usage in System Panel
- Switch to smaller models if experiencing memory pressure
- Ensure adequate cooling for sustained workloads

### **Getting Help**
- **System Health**: Use the built-in system monitoring panel
- **Logs**: Check console outputs in service windows
- **Documentation**: Refer to implementation.md for technical details

## 📋 System Requirements

### **Minimum Requirements**
- **GPU**: NVIDIA RTX 3080 (10GB VRAM)
- **RAM**: 32GB system memory
- **Storage**: 500GB available space
- **OS**: Windows 10/11 with WSL2

### **Recommended Requirements**
- **GPU**: NVIDIA RTX 4090 (24GB VRAM)
- **RAM**: 64GB system memory
- **Storage**: 1TB NVMe SSD
- **OS**: Windows 11 with WSL2
- **CPU**: AMD Ryzen 7800X3D or Intel i7-13700K

## 🎉 What's New

### **Latest Updates**
- ✅ **Complete Ollama Integration**: Full HTTP API support with model management
- ✅ **Unified LLM Service**: Single interface for all AI model backends
- ✅ **Automated Service Management**: One-click startup/shutdown scripts
- ✅ **Cross-Platform Development**: WSL2 development with Windows production
- ✅ **Real-time Model Monitoring**: Live status and performance tracking
- ✅ **Enhanced Chat Deletion**: Fixed chat management in project interface

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests for any improvements.

---

**Built with ❤️ for privacy-conscious users who demand both performance and control over their AI assistance.**