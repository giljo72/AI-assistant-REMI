# AI Assistant - Complete Setup Instructions

## Overview
This document provides complete instructions for setting up and running the AI Assistant with the new multi-model architecture.

## Prerequisites

### Required Software
1. **Python 3.10+** - Must be in PATH
2. **Node.js 18+** - For frontend development
3. **PostgreSQL 17** - With pgvector extension
4. **Docker Desktop** - For NVIDIA NIM containers (optional)
5. **NVIDIA GPU** - RTX 4090 or similar with 24GB VRAM
6. **Ollama** - For local model management

### Required Models
- **Mistral-Nemo** (7GB) - Quick chat and drafting
- **DeepSeek-Coder-V2-Lite** (9GB) - Code analysis
- **Qwen 2.5 32B** (17GB) - Business reasoning
- **Llama 3.1 70B** (22GB) - Deep analysis (via NIM)
- **NV-Embedqa-E5-v5** (2GB) - Document embeddings (via NIM)

## Installation Steps

### 1. Install Models
Run the model installation helper:
```bash
python install_models.py
```

This will:
- Check if Ollama is running
- Show which models are installed
- Offer to install missing models
- Check Docker and NGC API key setup

### 2. Configure NVIDIA NIM (Optional)
If you want to use Llama 70B and NV-Embedqa:

1. Ensure NGC API key is in `.env` file:
   ```
   NGC_API_KEY=your_key_here
   ```

2. Start Docker Desktop

3. Pull and start NIM containers:
   ```bash
   # For embeddings (always needed for RAG)
   docker-compose up -d nim-embeddings
   
   # For Llama 70B (optional, high VRAM)
   docker-compose up nim-generation-70b
   ```

### 3. Start the Application

#### Method 1: Simple (Recommended)
Double-click or run:
```bash
startai.bat
```

This will:
- Check all prerequisites
- Start PostgreSQL
- Start Ollama
- Start Backend API
- Start Frontend
- Check installed models
- Open browser automatically
- Show detailed logs

#### Method 2: Manual Start
If you prefer to start services individually:

1. **PostgreSQL**: Should auto-start with Windows
2. **Ollama**: `ollama serve`
3. **Backend**: 
   ```bash
   cd backend
   ..\venv_nemo\Scripts\activate
   uvicorn app.main:app --reload --port 8000
   ```
4. **Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

### 4. Stop the Application
Double-click or run:
```bash
stopai.bat
```

This will gracefully stop all services except PostgreSQL.

## Using the Multi-Model System

### Model Selection
1. **Automatic (Default)**: System selects best model based on your message
2. **Manual Override**: Use dropdown in chat to select specific model

### Model Purposes
- **Mistral-Nemo**: General chat, quick responses (2-20 seconds)
- **DeepSeek-Coder**: Code analysis, debugging (15-30 seconds)
- **Qwen 32B**: Business analysis (20-35 seconds)
- **Llama 70B**: Deep business insights (40-70 seconds)

### Operational Modes
Access via mode selector in chat header:
- **Balanced**: Default mode with Mistral-Nemo
- **Business Deep**: Loads Llama 70B for analysis
- **Business Fast**: Uses Qwen 32B
- **Development**: Loads DeepSeek-Coder
- **Quick**: Mistral-Nemo only for speed

### New Features

#### 1. Streaming Responses
All models now stream responses, so you see output as it's generated instead of waiting.

#### 2. Model Indicators
Each assistant message shows which model responded in the header.

#### 3. VRAM Management
System automatically loads/unloads models to fit in 24GB VRAM limit.

#### 4. Self-Analysis (Development Mode)
Enable in Admin Settings > Development tab to access code analysis features.

## Troubleshooting

### Common Issues

1. **"Ollama not running"**
   - Start Ollama: `ollama serve`
   - Or use startup script which handles this

2. **"Model not found"**
   - Run `python install_models.py`
   - Or manually: `ollama pull model-name`

3. **"Port already in use"**
   - Another instance is running
   - Use `stopai.bat` to clean up

4. **"Docker not found"**
   - Install Docker Desktop
   - Only needed for NIM models

5. **"Out of VRAM"**
   - System should auto-manage
   - Try switching to "Quick" mode
   - Restart to clear VRAM

### Checking Status

1. **View logs**: Check `logs/` directory
2. **Model status**: Click ❓ icon in UI
3. **Service health**: 
   - Backend: http://localhost:8000/docs
   - Ollama: http://localhost:11434

## Advanced Configuration

### Customizing Models
Edit `/backend/app/services/model_orchestrator.py` to:
- Add new models
- Change memory allocations
- Modify routing logic

### Adding New Models
1. Install via Ollama: `ollama pull model-name`
2. Add to orchestrator configuration
3. Update UI dropdowns if needed

### Performance Tuning
- Adjust `max_vram_gb` in orchestrator
- Modify `reserved_vram_gb` for stability
- Change model priorities in routing

## Summary of Commands

### Installation
```bash
# Install Python dependencies
cd backend
..\venv_nemo\Scripts\activate
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install

# Install models
python install_models.py
```

### Running
```bash
# Start everything
startai.bat

# Stop everything
stopai.bat

# Check models
ollama list

# Pull specific model
ollama pull model-name
```

### Docker (Optional)
```bash
# Start NIM containers
docker-compose up -d nim-embeddings
docker-compose up nim-generation-70b

# Stop NIM containers
docker-compose down

# Check container status
docker ps
```

## Support

If you encounter issues:
1. Check the logs in `logs/` directory
2. Ensure all prerequisites are installed
3. Try the manual start method for better error visibility
4. Check model status in the UI (❓ icon)

The system is designed to be resilient and will fall back to available models if preferred ones aren't accessible.