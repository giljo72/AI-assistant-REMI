# Cleanup Opportunities & Test Scripts Analysis

## Test Scripts (Root Directory)

### 1. test_nim_integration.py
- **Purpose**: Tests NVIDIA NIM API integration
- **Status**: KEEP - Useful for verifying NIM connectivity
- **Usage**: Run when troubleshooting NIM issues

### 2. test_system.py  
- **Purpose**: Comprehensive system test including models, DB, embeddings
- **Status**: KEEP - Good for system health checks
- **Usage**: Run after major changes

### 3. test_model_switch.py
- **Purpose**: Tests model switching functionality
- **Status**: KEEP - Validates model orchestration
- **Usage**: Run when adding new models

### 4. test_nim_embedding.py
- **Purpose**: Tests NIM embedding service
- **Status**: POTENTIAL DUPLICATE - May overlap with test_nim_integration.py
- **Action**: Review and potentially merge with test_nim_integration.py

## Setup & Installation Scripts

### 1. setup_nim.py
- **Purpose**: One-time NIM container setup
- **Status**: ARCHIVE - Only needed for initial setup
- **Action**: Move to scripts/archive/

### 2. install_models.py
- **Purpose**: Downloads and installs Ollama models
- **Status**: KEEP - Needed for new installations
- **Location**: Good in root

### 3. install_pdf_libs.py
- **Purpose**: Installs PDF processing libraries
- **Status**: QUESTIONABLE - Just runs pip install
- **Action**: Remove and add to setup documentation

## Scripts Directory Analysis

### Active Scripts
- check_installed_models.bat - KEEP
- check_model_status.py - KEEP
- model_reconfiguration.py - KEEP (2000+ lines!)

### One-Time Scripts
- install_all_models.bat - ARCHIVE
- install_models.bat - ARCHIVE  
- install_required_models.bat - ARCHIVE
- setup_llama_70b_nim.bat - ARCHIVE
- cleanup_models.py - KEEP (useful utility)

## Backend Test/Debug Files

### 1. backend/app/api/endpoints/test_endpoints.py
- **Purpose**: Test endpoints for development
- **Status**: REVIEW - Check if still needed
- **Contains**: /test routes that shouldn't be in production

### 2. backend/app/api/cleaned_api.py
- **Purpose**: Unknown - appears to be a cleaned version
- **Status**: INVESTIGATE - Possible duplicate

### 3. backend/app/cleaned_main.py
- **Purpose**: Unknown - another cleaned version
- **Status**: INVESTIGATE - Possible duplicate

### 4. backend/app/api/endpoints/cleaned_files.py
- **Purpose**: Unknown - yet another cleaned version
- **Status**: INVESTIGATE - Why so many "cleaned" files?

### 5. backend/app/api/endpoints/fix_files.py
- **Purpose**: Appears to be a one-time fix script
- **Status**: ARCHIVE or DELETE

## Frontend Cleanup

### 1. frontend/src/services/fileService.mock.ts
- **Purpose**: Mock service for development
- **Status**: QUESTIONABLE - Using real services now
- **Action**: Move to tests/ directory or remove

### 2. frontend/src/components/file/MainFileManager.tsx.bak
- **Purpose**: Backup file
- **Status**: DELETE - Use git for version control

### 3. frontend/src/components/chat/nul
- **Purpose**: Unknown empty file
- **Status**: DELETE

## Database & Migration Files

### 1. backend/app/db/init_db.py.bak
- **Purpose**: Backup of init_db.py
- **Status**: DELETE - Use git

### 2. backend/run_migration.py
- **Purpose**: One-time migration runner
- **Status**: ARCHIVE - Keep for reference

## Duplicate/Deprecated Services

### 1. Multiple LLM implementations
- backend/app/core/nemo_llm.py
- backend/app/core/transformers_llm.py
- backend/app/core/nemo_docker_client.py
- **Action**: Verify which are active, archive unused

### 2. Mock Services
- backend/app/core/mock_nemo/
- **Status**: KEEP - Useful for development
- **Action**: Add flag to disable in production

## Recommended Actions

### Immediate Cleanup
1. Delete all .bak files
2. Delete frontend/src/components/chat/nul
3. Archive one-time setup scripts
4. Remove install_pdf_libs.py

### Investigation Needed
1. Why are there "cleaned" versions of files?
2. Is test_endpoints.py used in production?
3. Can we consolidate NIM test scripts?
4. Which LLM implementations are actually used?

### Directory Structure
Create these directories:
- `/scripts/archive/` - For one-time setup scripts
- `/scripts/active/` - For utilities still in use
- `/tests/` - Consolidate all test scripts
- `/docs/archive/` - For outdated documentation

### Configuration Cleanup
1. Review .env files for unused variables
2. Check docker-compose.yml for unused services
3. Audit requirements.txt for unused packages

## Next Steps
1. Get approval for cleanup plan
2. Create archive directories
3. Move files systematically
4. Update documentation
5. Test that nothing breaks
6. Commit with clear message about reorganization