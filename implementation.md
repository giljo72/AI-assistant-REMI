# AI Assistant: Implementation Plan & Technical Architecture

## Implementation Status Overview

| Component | Status | Progress |
|-----------|--------|----------|
| Frontend (React) | ✅ Complete | 100% |
| Backend (FastAPI) | ✅ Complete | 100% |
| Database (PostgreSQL) | ✅ Complete | 100% |
| AI Models | ✅ Complete | 100% |
| Document Processing | ✅ Working | 85% |
| Vector Search | ✅ Complete | 100% |
| System Monitoring | ✅ Complete | 100% |
| Context Controls | ⚠️ Frontend Only | 60% |
| Self-Aware Context | ⚠️ Backend Only | 70% |

## Current Implementation

### Architecture Overview
```
┌─────────────────────────────────────────────────────────┐
│                   Frontend (React)                       │
│  - TypeScript + Vite    - Redux State Management        │
│  - Tailwind CSS         - Real-time Updates            │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP/WebSocket
┌────────────────────────┴────────────────────────────────┐
│                   Backend (FastAPI)                      │
│  - Async Python         - Unified LLM Service           │
│  - SQLAlchemy ORM       - Document Processing           │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────┐
│                    Data Layer                            │
├─────────────────┬──────────────┬────────────────────────┤
│ PostgreSQL      │ File Storage │ Docker Services        │
│ + pgvector      │ (Local FS)   │ - NIM Containers      │
│ (1024 dims)     │              │ - Ollama Service      │
└─────────────────┴──────────────┴────────────────────────┘
```

### Technology Choices & Rationale

#### Frontend Stack
**Choice**: React + TypeScript + Vite
- **Why**: Modern, fast development with hot reload
- **Alternatives Considered**: 
  - Vue.js (less ecosystem)
  - Angular (too heavy)
  - Vanilla JS (too much boilerplate)
- **Trade-offs**: Requires Node.js toolchain

#### Backend Framework  
**Choice**: FastAPI
- **Why**: Native async, automatic API docs, Python ecosystem
- **Alternatives Considered**:
  - Django (too monolithic)
  - Flask (less modern)
  - Node.js (less AI library support)
- **Trade-offs**: Python GIL limitations

#### Database
**Choice**: PostgreSQL + pgvector
- **Why**: Production-grade, native vector support
- **Alternatives Considered**:
  - Chroma (less mature)
  - Weaviate (requires separate service)
  - Pinecone (cloud-only)
- **Trade-offs**: Requires extension installation

#### AI Model Hosting
**Choice**: Hybrid (Ollama + NVIDIA NIM)
- **Why**: Best of both worlds - flexibility + performance
- **Alternatives Considered**:
  - Pure Ollama (no TensorRT optimization)
  - Pure NIM (less model variety)
  - Transformers (higher complexity)
- **Trade-offs**: Multiple services to manage

## Document Processing Implementation

### Current Approach (Simple & Working)
```python
# Text extraction using proven libraries
- PyPDF2: PDF text extraction
- python-docx: Word document processing  
- pandas: Spreadsheet handling
- Direct file reading: Plain text

# Chunking strategy
- Default: 3000 chars (3x original plan)
- Business docs: Multi-level (3000 + 8000)
- Overlap: 500 chars for context continuity
```

### Why This Approach
1. **Simplicity**: Well-documented, mature libraries
2. **Reliability**: Proven in production environments
3. **Performance**: No additional GPU overhead
4. **Maintainability**: Easy to debug and extend

### Alternatives Considered

#### 1. NVIDIA NV-Ingest (Advanced Multimodal)
**Pros**:
- Extract tables, charts, images
- Preserve document structure
- State-of-the-art accuracy

**Cons**:
- Complex Docker orchestration
- 10-15GB additional VRAM
- Poor documentation
- Significant complexity increase

**Decision**: Deferred to future enhancement

#### 2. LlamaIndex Document Processing
**Pros**:
- Sophisticated chunking
- Built-in document understanding
- Good community support

**Cons**:
- Heavy dependency
- Opinionated architecture
- Performance overhead

**Decision**: Too restrictive for our needs

#### 3. Unstructured.io
**Pros**:
- Handles many formats
- Good accuracy
- Active development

**Cons**:
- Large dependency footprint
- Slower processing
- Memory intensive

**Decision**: Overkill for current needs

### Upgrade Path for Document Processing

#### Phase 1: Enhanced Text Extraction (Next)
- [ ] Add OCR for scanned PDFs (pytesseract)
- [ ] Extract table structure (tabula-py)
- [ ] Preserve heading hierarchy
- [ ] Extract metadata (author, date, etc.)

#### Phase 2: Structured Understanding
- [ ] Implement semantic chunking
- [ ] Add document type detection
- [ ] Create specialized processors per type
- [ ] Enhance chunk metadata

#### Phase 3: Multimodal Integration (Future)
- [ ] Integrate NV-Ingest for visual elements
- [ ] Add chart data extraction
- [ ] Implement layout understanding
- [ ] Enable image text extraction

## Embedding & Vector Search

### Current Implementation
```python
# NVIDIA NIM Embeddings (Required)
Model: nvidia/nv-embedqa-e5-v5
Dimensions: 1024
Endpoint: http://localhost:8081
Input Types: "query" | "passage"

# pgvector Configuration
CREATE EXTENSION vector;
ALTER TABLE document_chunks 
ADD COLUMN embedding vector(1024);

# Similarity Search
SELECT content, 
       1 - (embedding <=> query_embedding) as similarity
FROM document_chunks
WHERE 1 - (embedding <=> query_embedding) > 0.01
ORDER BY similarity DESC
LIMIT 5;
```

### Why NIM Embeddings
1. **Quality**: State-of-the-art retrieval performance
2. **Speed**: TensorRT optimized inference
3. **Integration**: Native NVIDIA ecosystem
4. **Dimensions**: 1024 provides optimal quality/size

### Alternatives Considered

#### 1. Sentence-Transformers (Original Plan)
**Pros**: Easy to use, good quality, CPU support
**Cons**: Slower, smaller dimensions (384-768)
**Decision**: Upgraded to NIM for better quality

#### 2. OpenAI Embeddings
**Pros**: Excellent quality, well-documented
**Cons**: Cloud dependency, privacy concerns, cost
**Decision**: Violates local-only principle

#### 3. Custom Trained Embeddings
**Pros**: Domain-specific optimization
**Cons**: Requires training data, expertise, time
**Decision**: Unnecessary complexity

## AI Model Architecture

### Current Multi-Model Setup

#### 1. Primary Models (Ollama)
```yaml
Qwen 2.5 32B:
  Role: Default assistant
  VRAM: 19GB
  Features: Full RAG support

Mistral-Nemo 12B:
  Role: Quick responses
  VRAM: 7GB
  Features: Fast inference

DeepSeek Coder V2 16B:
  Role: Code generation
  VRAM: 9GB
  Features: Code understanding
```

#### 2. Advanced Models (NVIDIA NIM)
```yaml
Llama 3.1 70B (Removed):
  Status: Could not load on RTX 4090
  VRAM: Required 40GB+
  Decision: Removed from deployment

NV-EmbedQA-E5-V5:
  Role: Embeddings
  VRAM: 1.2GB
  Features: Always running
```

### Model Orchestration Strategy
1. **Intelligent Routing**: Based on query type
2. **Dynamic Loading**: Load/unload as needed
3. **VRAM Management**: Stay within 24GB limit
4. **Fallback Logic**: Graceful degradation

### Future Model Considerations
- **Llama 3.2 Vision**: For image understanding
- **Mixtral 8x7B**: For balanced performance
- **Custom Fine-tunes**: For specialized domains

## Context Management

### Current Implementation (Frontend Only)
```typescript
// Context modes in UI
- Self-Aware: Can read codebase
- Standard: Basic chat
- Business: Enhanced reasoning
- Custom: User-defined

// Visual indicators
- Yellow context badge
- Mode selection modal
- Per-chat persistence
```

### Missing Backend Implementation
The context controls exist in UI but don't affect backend behavior. Need to:

1. [ ] Pass context settings in API calls
2. [ ] Implement context-aware retrieval
3. [ ] Add prompt modification based on mode
4. [ ] Create context filtering logic

### Planned Implementation
```python
class ContextManager:
    def build_context(self, mode: str, settings: dict):
        context = []
        
        if settings.get("system_prompt"):
            context.append(self.get_system_prompt())
            
        if settings.get("project_docs"):
            context.extend(self.get_relevant_docs())
            
        if mode == "self_aware":
            context.extend(self.get_codebase_context())
            
        return self.optimize_context(context)
```

## Chat System & Conversation Management

### Architecture Overview
The chat system manages conversations between users and AI models, maintaining context and handling message flow.

```
┌─────────────────────────────────────────────────────────┐
│                  Chat Interface                          │
│  - Message history display                              │
│  - Real-time streaming responses                        │
│  - Model selection                                      │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────┐
│              Chat API Endpoints                          │
│  POST /chats/{id}/generate      - Standard response    │
│  POST /chats/{id}/generate-stream - Streaming response │
│  GET  /chats/{id}/messages      - Message history      │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────┐
│           Context Building & Management                  │
│  - System prompts                                       │
│  - Conversation history (100 messages)                 │
│  - Document context (RAG)                              │
│  - User/Project prompts                                │
└─────────────────────────────────────────────────────────┘
```

### Context Window Management (Updated 5/28/2025)

#### Problem Solved
- **Issue**: Large content (transcripts, documents) would fall out of context after 10 messages
- **Root Cause**: Limited context window of 10 messages
- **Impact**: AI would "forget" important information and ask for it again

#### Solution Implemented
```python
# Previous configuration
context_messages: int = 10  # Too small for long conversations

# New configuration  
context_messages: int = 100  # Maintains context for ~50 exchanges
```

#### Benefits
- Transcripts and large documents stay in context much longer
- No need to re-paste information during long conversations
- Better continuity for complex discussions
- Minimal resource impact (only ~200KB RAM per chat)

### Message Deduplication Fix (5/28/2025)

#### Problem Solved
- **Issue**: User messages appeared twice in AI context
- **Root Cause**: Message saved to DB then included in context fetch
- **Impact**: AI processed the same message twice, causing confusion

#### Solution
```python
# Filter out just-saved message from context
filtered_messages = [
    msg for msg in recent_messages 
    if msg.id != user_msg_obj.id
][:request.context_messages]
```

### Model Context Limits
Each model has different context window capabilities:
- **Qwen 2.5 32B**: ~32K tokens
- **Mistral-Nemo 12B**: ~128K tokens (best for long contexts)
- **DeepSeek Coder 16B**: ~16K tokens

With 100 messages in context, typical usage is 5-10K tokens, well within all model limits.

### Future Enhancements
1. [ ] Dynamic context sizing based on message importance
2. [ ] Message pinning to keep critical info in context
3. [ ] Context compression for very long conversations
4. [ ] Token usage monitoring and warnings
5. [ ] Automatic summarization when approaching limits

## Self-Aware Context Implementation

### Architecture Overview
The self-aware context enables the AI assistant to read and modify its own source code at F:\assistant, facilitating continuous improvement while maintaining security.

```
┌─────────────────────────────────────────────────────────┐
│                  Chat Interface                          │
│  - Self-aware mode toggle                               │
│  - File content display                                 │
│  - Modification approval UI (pending)                   │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────┐
│              Self-Aware API Endpoints                    │
│  /api/self-aware/files    - Browse source files        │
│  /api/self-aware/read     - Read file content          │
│  /api/self-aware/validate - Check code safety          │
│  /api/self-aware/update   - Write changes              │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────┐
│             Security & Validation Layer                  │
│  - Path traversal protection                            │
│  - Dangerous pattern detection                          │
│  - Automatic backups                                   │
│  - Audit logging                                        │
└─────────────────────────────────────────────────────────┘
```

### Security Implementation

#### Dangerous Code Patterns Blocked
```python
DANGEROUS_PATTERNS = [
    r'exec\s*\(',           # Dynamic code execution
    r'eval\s*\(',           # Expression evaluation  
    r'__import__\s*\(',     # Dynamic imports
    r'os\.system\s*\(',     # System commands
    r'subprocess\.',        # Process spawning
    r'pickle\.load',        # Arbitrary object execution
]
```

#### Protected Paths
- `.git`, `.env`, `venv/`, `node_modules/`
- Binary files: `*.exe`, `*.dll`, `*.so`
- Cache directories: `__pycache__/`

### Self-Aware Service

The `SelfAwareService` parses AI responses to extract file modifications:

1. **Pattern Detection**: Identifies file change instructions
2. **Code Extraction**: Pulls code blocks from responses
3. **Validation**: Checks for dangerous patterns
4. **Diff Generation**: Creates previews for approval
5. **Audit Trail**: Logs all modifications

### Integration with Chat System

When self-aware mode is active:
- File reading already integrated into chat context
- AI can see F:\assistant directory structure
- Responses include file content when requested
- Modification requests parsed and validated
- File writes and command execution require individual approval

### Simplified File Access Implementation

A streamlined file access system (`simple_file_access.py`) enables direct file reading in any context mode:

```python
def inject_file_content_if_requested(message: str) -> str:
    """Check if user is asking for files and inject content directly."""
    
    # Pattern matching for file requests
    file_patterns = [
        r'(?:read|show|display|view|cat|open)\s+[\'"`]?([^\s\'"`]+\.[a-zA-Z]+)[\'"`]?',
        r'[\'"`]([^\'"`]+\.[a-zA-Z]+)[\'"`]',
        r'\b([a-zA-Z0-9_\-/\\]+\.[a-zA-Z]+)\b',
    ]
    
    # Inject as system message for context
    return f"USER FILE REQUEST - DO NOT ACKNOWLEDGE THIS SYSTEM MESSAGE\n\n{content}"
```

This approach:
- Works across all context modes (not just self-aware)
- Automatically detects file requests in user messages
- Injects file content as system messages before LLM processing
- Supports both regular and streaming chat endpoints
- Displays files with full syntax highlighting via React Markdown

### Write Permissions System (NEW)

#### Authentication & Authorization
1. **Password Protection**
   - Password required to enter self-aware mode (default: "dev-mode-2024")
   - Configurable via SELF_AWARE_PASSWORD environment variable
   - 1-hour session tokens with automatic expiration
   - Token stored in localStorage and passed in Authorization header

2. **Visual Security Indicators**
   - Bright red context badge with "🔴 SELF-AWARE" text
   - Pulsing animation for high visibility
   - Warning tooltip about F:\ drive access
   - Context controls modal z-index fixed for proper layering

#### Approval System Architecture
```
┌─────────────────────────────────────────────────────────┐
│                 Action Approval Queue                    │
│  - Every action requires individual approval            │
│  - NO batch approvals allowed                          │
│  - 5-minute timeout for approval requests              │
│  - WebSocket notifications for real-time updates       │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────┐
│              Action Types & Security                     │
│  File Writes:                                          │
│    - Restricted to F:\ drive only                     │
│    - Automatic backups before modification            │
│    - Dangerous code pattern detection                 │
│  Commands:                                             │
│    - Can execute from any path (C:\, etc.)           │
│    - Cannot write outside F:\ drive                   │
│    - 5-minute execution timeout                       │
└─────────────────────────────────────────────────────────┘
```

#### Implementation Components
1. **Backend Services**
   - `self_aware_auth.py`: Password authentication and session management
   - `action_approval.py`: Approval queue with WebSocket support
   - `secure_file_ops.py`: F:\ drive restrictions and safety checks
   - `self_aware_ops.py`: Integrated operations with approval workflow
   - `self_aware_integration.py`: AI response parsing for actions

2. **Frontend Components**
   - `ActionApprovalModal.tsx`: Detailed approval UI with syntax highlighting
   - `selfAwareService.ts`: WebSocket client and API integration
   - Password modal integrated into ContextControlsPanel
   - Real-time approval notifications

3. **Security Features**
   - Path traversal protection
   - Dangerous patterns blocked (exec, eval, subprocess, etc.)
   - Protected paths (.git, .env, node_modules)
   - Automatic backups in F:/assistant/backups/self_aware
   - Comprehensive audit logging

### File Modification Workflow

```
User enters self-aware mode → Password authentication
     ↓
AI suggests file change/command → Parse response
     ↓
Create approval request → WebSocket notification
     ↓
Show approval modal → User reviews details
     ↓
User approves/denies → Execute or cancel
     ↓
If approved: Create backup → Apply change → Log action
```

### Audit Trail Structure
```json
{
  "timestamp": "2025-01-27T10:30:00",
  "path": "backend/app/main.py",
  "reason": "Fix async handler issue",
  "backup": "backups/main_20250127_103000.py",
  "warnings": ["Uses socket module"]
}
```

### Future Enhancements
1. [x] Frontend password authentication modal
2. [x] Real-time diff approval interface
3. [x] WebSocket notifications for changes
4. [ ] Frontend file browser UI
5. [ ] Integration with git for version control
6. [ ] Automated testing of proposed changes
7. [ ] Multi-user approval workflows
8. [ ] Rollback functionality for changes

## System Monitoring

### Current Implementation
```python
# Resource monitoring (10-second polling)
GET /api/system/resources
- CPU usage & model
- RAM usage & speed  
- GPU utilization
- Storage metrics

# Model status
GET /api/models/status/quick
- Active models
- VRAM usage
- Performance metrics
```

### Monitoring Architecture
1. **Frontend**: ResourceMonitor component
2. **Backend**: Cross-platform hardware detection
3. **Logging**: Filtered to separate file
4. **Display**: Real-time gauges and metrics

### Enhanced Backend Console Logging
Implemented user-friendly console logging with timestamps and action names in `backend/run_server.py`:

#### Features
1. **Human-Readable Actions**: Converts API endpoints to friendly names
   - `POST /api/files/upload` → "Upload Document"
   - `POST /api/chats/*/generate` → "Chat Message"
   - `GET /api/projects` → "List Projects"

2. **Color-Coded Status**: Visual feedback based on HTTP status
   - 🟢 **GREEN**: Success (200, 201)
   - 🔵 **CYAN**: Redirects (301, 302, 304, 307)
   - 🟡 **YELLOW**: Client errors (400, 401, 403, 404)
   - 🔴 **RED**: Server errors (500, 502, 503)

3. **Structured Format**:
   ```
   [timestamp] icon action | method path | status
   [2025-05-27 11:50:23] ✓ List Projects | GET /api/projects | 200 OK
   ```

4. **Resource Filtering**: System resource endpoints auto-filtered to reduce noise

#### Implementation
```python
class EnhancedAccessFormatter(logging.Formatter):
    # ANSI color codes
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    def format(self, record):
        # Parse uvicorn log format
        # Apply color based on status
        # Return formatted message
```

## Service Management

### Current Setup
```batch
# Start all services
startai.bat
- PostgreSQL check/start
- Docker containers
- Ollama service
- Backend server
- Frontend dev server

# Stop all services  
stopai.bat
- Graceful shutdown
- Preserve data
- Clean process termination
```

### Service Dependencies
```
PostgreSQL (5432)
    ↓
NIM Containers (8081)
    ↓
Ollama Service (11434)
    ↓
Backend API (8000)
    ↓
Frontend (3000)
```

## Testing Strategy

### Current Test Coverage
- Unit tests: ❌ Not implemented
- Integration tests: ⚠️ Manual only
- E2E tests: ❌ Not implemented
- System tests: ✅ Basic scripts

### Planned Testing Implementation
1. [ ] Jest for frontend unit tests
2. [ ] Pytest for backend tests
3. [ ] Playwright for E2E tests
4. [ ] Load testing with Locust

## Deployment Architecture

### Current: Development Mode
- Frontend: Vite dev server
- Backend: Uvicorn with reload
- Services: Manual startup

### Production Deployment Plan
1. [ ] Frontend: Static build with nginx
2. [ ] Backend: Gunicorn with workers
3. [ ] Services: Systemd management
4. [ ] Monitoring: Prometheus + Grafana

## Security Considerations

### Current Security
- Local-only by design
- No authentication (single user)
- File system permissions
- Docker isolation

### Future Security Enhancements
1. [ ] Optional authentication
2. [ ] API key management
3. [ ] Encrypted storage
4. [ ] Audit logging

## Performance Optimization

### Current Optimizations
- Async Python backends
- React memo/callbacks
- Database indexing
- Model quantization

### Planned Optimizations
1. [ ] Redis caching layer
2. [ ] CDN for static assets
3. [ ] Database query optimization
4. [ ] Model batching

## Technical Debt & Cleanup

See `Cleanup_Opportunities.md` for detailed analysis of:
- Test scripts consolidation
- One-time setup scripts
- Duplicate "cleaned" files
- Deprecated code removal

## Upgrade Roadmap

### Immediate (This Quarter)
1. [ ] Complete context backend
2. [ ] Add unit test coverage
3. [ ] Clean up technical debt
4. [ ] Document API fully

### Short Term (6 Months)
1. [ ] NV-Ingest evaluation
2. [ ] Production deployment
3. [ ] Performance optimization
4. [ ] Security enhancements

### Long Term (1 Year)
1. [ ] Multi-user support
2. [ ] Plugin architecture
3. [ ] Mobile interface
4. [ ] Cloud sync option

## Decision Log

Major technical decisions and rationale:

1. **pgvector over dedicated vector DB**: Simplicity and integration
2. **NIM embeddings required**: Quality over flexibility
3. **Simple text extraction**: Reliability over features
4. **Multiple model backends**: Flexibility over simplicity
5. **React over Vue**: Ecosystem and talent pool
6. **FastAPI over Django**: Modern async capabilities
7. **Local-only design**: Privacy over convenience

This implementation plan provides the technical foundation for achieving the vision outlined in Scope.md while maintaining flexibility for future enhancements.