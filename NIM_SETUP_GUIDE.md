# NVIDIA NIM Integration Setup Guide

## Quick Start

1. **Run the test script to verify your setup:**
   ```bash
   python test_nim_integration.py
   ```

2. **If all tests pass, start the assistant:**
   ```bash
   python start_assistant.py
   # or
   startai.bat
   ```

## Manual Setup (if needed)

### 1. NGC API Key Setup

If you don't have an NGC API key:
1. Visit https://ngc.nvidia.com/
2. Sign up or log in
3. Go to Setup → API Key
4. Generate a new API key

Add to `.env` file:
```
NGC_API_KEY=your-key-here
```

### 2. Docker Setup

Ensure Docker Desktop is installed and running:
- Windows: https://docs.docker.com/desktop/install/windows-install/
- Enable WSL2 backend
- Enable GPU support (if available)

### 3. Start NIM Containers Manually

```bash
# Start embeddings container (required for RAG)
docker-compose up -d nim-embeddings

# Optionally start LLM container (if you have enough VRAM)
docker-compose up -d nim-llm
```

### 4. Verify Containers

```bash
# Check running containers
docker ps

# Check embeddings API
curl http://localhost:8001/v1/models

# View logs
docker logs nim-embeddings
```

## Architecture Overview

```
┌─────────────────┐
│   Frontend      │
│  (React App)    │
│ localhost:3000  │
└────────┬────────┘
         │
┌────────┴────────┐
│   Backend API   │
│   (FastAPI)     │
│ localhost:8000  │
└────────┬────────┘
         │
    ┌────┴────┬──────────┬───────────┐
    │         │          │           │
┌───┴───┐ ┌──┴────┐ ┌───┴────┐ ┌────┴────┐
│Ollama │ │  NIM  │ │  NIM   │ │Database │
│Models │ │Embed  │ │  LLM   │ │(pgvector)│
│:11434 │ │:8001  │ │ :8002  │ │  :5432  │
└───────┘ └───────┘ └────────┘ └─────────┘
```

## Model Configuration

The system supports multiple models with intelligent routing:

1. **Ollama Models** (localhost:11434):
   - Mistral Nemo (12B) - Default chat
   - DeepSeek Coder V2 (16B) - Code generation
   - Qwen 2.5 (32B) - Advanced reasoning
   - Llama 3.1 (70B) - Complex queries

2. **NIM Models**:
   - NV-EmbedQA-E5-v5 - Document embeddings (port 8001)
   - Optional: Llama 3.1 70B via NIM (port 8002)

## Troubleshooting

### Docker Issues

```bash
# Reset Docker containers
docker-compose down
docker-compose up -d

# Clean up Docker resources
docker system prune -a
```

### Port Conflicts

Check if ports are in use:
```bash
# Windows
netstat -an | findstr :8000
netstat -an | findstr :8001
netstat -an | findstr :11434

# Linux/WSL
lsof -i :8000
lsof -i :8001
lsof -i :11434
```

### Memory Issues

- nim-embeddings requires ~4GB VRAM
- nim-llm requires ~16GB+ VRAM
- Ollama models have varying requirements (9-40GB)

Monitor GPU usage:
```bash
nvidia-smi -l 1
```

### Logs

View container logs:
```bash
docker logs -f nim-embeddings
docker logs -f backend
docker logs -f frontend
```

## Configuration Files

- `.env` - Environment variables (NGC_API_KEY)
- `docker-compose.yml` - Container definitions
- `backend/app/services/model_orchestrator.py` - Model routing logic
- `frontend/src/services/chatService.ts` - Frontend integration

## Support

- NVIDIA NIM Docs: https://docs.nvidia.com/nim/
- NGC Support: https://ngc.nvidia.com/support
- Project Issues: Create an issue in this repository