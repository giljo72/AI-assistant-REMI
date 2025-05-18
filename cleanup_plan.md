# Project Cleanup and Migration Plan

## 1. Backend Files to Clean Up

### Files to Remove (Diagnostic/Test Scripts):
- `/backend/test_file_upload.py`
- `/backend/test_file_upload_verbose.py`
- `/backend/fix_db_schema.py`
- `/backend/upload_file_direct.py`
- `/backend/batch_upload_files.py`
- `/backend/test_db_connection.py`
- `/backend/test_direct_upload.py`
- `/backend/test_api_scan.py`
- `/backend/diag_app.py`
- `/backend/check_import_paths.py`
- `/backend/clear_cache_and_run.py`
- `/backend/list_routes.py`
- `/backend/check_routes_registered.py`
- `/backend/test_minimal_app.py`
- `/backend/test_correct_urls.py`
- `/backend/direct_endpoint_tests.py` 
- `/backend/quick_test.py`
- `/backend/check_paths.py`
- `/backend/run_direct.py`
- `/backend/test_direct_api.py`
- `/backend/reset_and_run.py`
- `/backend/run_server.py`
- `/backend/app/direct_main.py`
- `/backend/backendproblem.md`

### Core Backend Files to Keep and Clean:
- `/backend/app/main.py` - Remove diagnostic endpoints, keep only core functionality
- `/backend/app/api/api.py` - Remove test router includes, keep only production routers
- `/backend/app/api/endpoints/files.py` - Clean up file upload endpoint, remove test endpoints
- `/backend/app/api/endpoints/health.py` - Keep only essential health check endpoints
- `/backend/app/schemas/document.py` - Fix schema naming for production

### Files to Remove from Endpoints:
- `/backend/app/api/endpoints/test_endpoints.py`
- `/backend/app/api/endpoints/health2.py`
- `/backend/app/api/endpoints/fix_files.py`

## 2. Frontend Files to Clean
- Keep current frontend structure, no cleanup needed

## 3. Important Documentation to Migrate
- `F:/Assistant/Scope.md`
- `F:/Assistant/Readme.MD`
- `F:/Assistant/CLAUDE.md`
- `F:/Assistant/Devlog.md`
- `F:/Assistant/implementation.md`
- `F:/Assistant/File Management Navigation Guide.md`

## 4. Database Configuration to Migrate
- PostgreSQL connection settings
- pgvector extension configuration

## 5. Environment Setup for New Project
- Python 3.10+ environment
- Node.js 18+ environment 
- PostgreSQL 17 with pgvector

## 6. Core Dependencies for New Project
- FastAPI
- SQLAlchemy
- Pydantic
- React + TypeScript
- Redux Toolkit
- Tailwind CSS