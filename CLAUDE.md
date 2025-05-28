# AI Assistant Development Guide

## CRITICAL ENVIRONMENT INFORMATION
**IMPORTANT**: Development is done in WSL (Ubuntu), but the application runs on Windows 11. Docker Desktop runs in WSL2 mode for our NVIDIA NIM container. When providing commands or paths, be mindful of this hybrid environment.

## DEVELOPMENT BEHAVIOR EXPECTATIONS

### Core Principles
- **ALWAYS** read project documentation (Scope.md, implementation.md, README.md, Devlog.md) before making changes
- **ASK** questions if something is unclear rather than making assumptions
- **AVOID** creating cascading changes without updating related scripts and code
- **AVOID** creating new diagnostic files - use existing test files and extend them
- **UPDATE** Scope.md, implementation.md, and README.md when adding architectural changes
- **RECOMMEND** complete file rewrites when it improves efficiency over repeated patches
- **THINK** modular over monolithic file structures
- **REMEMBER** application runs on Windows 11, consider this for tests and scripts
- **APPEND** to Devlog.md for every MAJOR step with today's date

### Developer Support
- User is a novice developer relying on AI logic and reasoning
- Provide one-step-at-a-time instructions when giving directions
- Summarize verbose requests before executing code changes

### Learning from Past Issues (from Devlog.md)
- **Deprecated Patterns**: 
  - Avoid `find` and `grep` commands - use built-in search tools
  - Use `rg` (ripgrep) instead of grep when necessary
  - NEVER update git config
- **Fixed Issues**:
  - Markdown files in chat should use 'plaintext' language identifier
  - pgvector embeddings must use Vector column type, not Text
  - NIM requires very low similarity thresholds (0.01 vs 0.3)
  - Self-aware mode password is "dev-mode-2024" (not in .env)

## PROJECT TECHNICAL DETAILS

### Environment Setup
- **Virtual Environment**: `venv_nemo` (NOT `venv`)
- **Python**: 3.10+
- **PostgreSQL**: 17 with pgvector (1024 dimensions)
- **GPU**: NVIDIA RTX 4090 (24GB VRAM limit)
- **Ports**:
  - Frontend: 3000
  - Backend: 8000
  - NVIDIA NIM: 8081
  - Ollama: 11434
  - PostgreSQL: 5432

### Quick Start Commands
```bash
# Start all services
./startai.bat

# Stop all services
./stopai.bat

# Backend only
cd backend
../venv_nemo/Scripts/activate  # Note: venv_nemo is in parent directory
uvicorn app.main:app --reload --port 8000

# Frontend only
cd frontend
npm run dev
```

### Key Technical Constraints
- **100% Local**: No cloud dependencies
- **NIM Required**: No fallback embeddings (1024 dimensions)
- **VRAM Management**: Stay within 24GB limit
- **File Paths**: Always use absolute paths
- **Chunk Size**: 2000 chars (NIM token limit)

### Active Models
- **Qwen 2.5 32B**: Default model
- **Mistral-Nemo 12B**: Fast responses
- **DeepSeek Coder V2 16B**: Code specialist
- **NV-EmbedQA**: Always-on embeddings

### Self-Aware Mode
- **Read Access**: Works in all modes for F:\assistant
- **Write Access**: Password-protected ("dev-mode-2024")
- **Security**: Individual approval for EVERY action
- **Visual**: Bright red "🔴 SELF-AWARE" badge
- **Restrictions**: Write operations limited to F:\ drive

## DEVELOPMENT WORKFLOW

### Before Making Changes
1. Review relevant documentation files
2. Check Devlog.md for past issues and learnings
3. Understand the hybrid WSL/Windows environment
4. Ask clarifying questions if needed

### When Making Changes
1. Follow existing code conventions and patterns
2. Check if libraries are already in use before adding new ones
3. Update documentation for architectural changes
4. Test considering the Windows runtime environment
5. Append major steps to Devlog.md

### Code Style Guidelines
- DO NOT add comments unless explicitly requested
- Prefer modular over monolithic structures
- Follow existing patterns in the codebase
- Ensure security best practices

### File Management
- ALWAYS prefer editing existing files over creating new ones
- Delete temporary files after use
- Only create documentation files when explicitly requested
- Use the TodoWrite tool for task tracking

## COMMON OPERATIONS

### Database Migrations
```bash
cd backend
python run_migration.py
```

### Seeding System Prompts
```bash
cd backend
python -m app.db.seed_system_prompts
```

### Testing Document Upload
```bash
# Use the frontend UI or API endpoints
# Documents are processed with NIM embeddings (2000 char chunks)
```

### Checking Model Status
```bash
# Use the Admin Settings panel in the UI
# Or check http://localhost:8000/api/models/status
```

## IMPORTANT REMINDERS
- Virtual environment is `venv_nemo`, not `venv`
- Application runs on Windows, development in WSL
- Docker Desktop uses WSL2 mode
- No Llama 70B support (requires 4x H100 GPUs)
- NIM embeddings are required (no fallback)
- Self-aware write mode requires password authentication