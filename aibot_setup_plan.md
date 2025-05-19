# AIbot Project Setup Plan

## 1. Project Structure

```
F:/AIbot/
│
├── backend/               # Backend FastAPI application
│   ├── app/               # Core application
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Core functionality
│   │   ├── db/            # Database models and repositories
│   │   ├── document_processing/ # Document processing
│   │   ├── rag/           # RAG system
│   │   ├── schemas/       # Pydantic schemas
│   │   └── main.py        # Application entry point
│   │
│   ├── data/              # Data directories
│   │   ├── uploads/       # Uploaded files
│   │   ├── processed/     # Processed files
│   │   ├── hierarchy/     # Document hierarchies
│   │   └── logs/          # Log files
│   │
│   └── scripts/           # Utility scripts
│       ├── setup_database.py  # Database setup
│       └── reset_database.py  # Database reset
│
├── frontend/             # React frontend
│   ├── src/              # Source code
│   │   ├── components/   # React components
│   │   ├── context/      # React context
│   │   ├── hooks/        # Custom hooks
│   │   ├── services/     # API services
│   │   ├── store/        # Redux store
│   │   └── main.tsx      # Entry point
│   │
│   └── public/           # Public assets
│
├── docs/                 # Project documentation
│   ├── scope.md          # Project scope
│   ├── implementation.md # Implementation details
│   ├── devlog.md         # Development log
│   └── file_management.md # File management guide
│
├── scripts/              # Project-level scripts
│   ├── setup_environment.py # Environment setup
│   ├── start_services.bat  # Start all services
│   └── stop_services.bat   # Stop all services
│
└── venv_nemo/            # Virtual environment (excluded from git)
```

## 2. Setup Steps

1. **Create Project Directory Structure**
   - Create all directories according to the structure above
   - Set up .gitignore for appropriate exclusions

2. **Migrate Core Documentation**
   - Copy and update documentation files from original project
   - Place in appropriate locations in new structure

3. **Setup Python Environment**
   - Create virtual environment
   - Install dependencies from requirements.txt

4. **Setup Database**
   - Configure PostgreSQL connection
   - Set up pgvector extension
   - Create initial tables

5. **Migrate Backend Code**
   - Clean up and migrate app directory
   - Update import paths as needed
   - Test basic API functionality

6. **Migrate Frontend Code**
   - Copy frontend directory structure
   - Update API endpoint references if needed

7. **Setup Services**
   - Create service start/stop scripts
   - Configure for Windows environment

## 3. Dependencies

### Backend Dependencies
```
fastapi>=0.100.0
uvicorn>=0.22.0
sqlalchemy>=2.0.0
pydantic>=2.0.0
python-multipart>=0.0.6
psycopg2-binary>=2.9.6
pgvector>=0.2.0
python-dotenv>=1.0.0
httpx>=0.24.1
docx2txt>=0.8
PyPDF2>=3.0.0
llama-index>=0.8.0
pandas>=2.0.0
numpy>=1.24.0
```

### Frontend Dependencies
```
react>=18.0.0
react-dom>=18.0.0
typescript>=5.0.0
vite>=4.0.0
@reduxjs/toolkit>=1.9.0
tailwindcss>=3.0.0
```

## 4. Configuration Files

### Backend Environment (.env)
```
DATABASE_URL=postgresql://username:password@localhost:5432/aibot
UPLOAD_DIR=./data/uploads
PROCESSED_DIR=./data/processed
LOG_LEVEL=INFO
USE_MOCK_NEMO=true
MODEL_NAME=nvidia/nemo-1
```

### Frontend Environment (.env)
```
VITE_API_URL=http://localhost:8000
```

## 5. Database Configuration

### PostgreSQL Setup
- Database name: aibot
- Extensions: pgvector
- Initial tables:
  - projects
  - documents
  - document_chunks
  - chats
  - messages
  - project_documents
  - user_prompts

## 6. Startup Procedure

1. Start PostgreSQL database service
2. Run backend API with `cd backend && uvicorn app.main:app --reload --port 8000`
3. Run frontend with `cd frontend && npm run dev`
4. Access application at http://localhost:5173