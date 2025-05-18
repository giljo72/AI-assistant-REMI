# Backend API Routing Issue Investigation

## Problem Description

We are encountering issues with the FastAPI application in our backend. The main problems are:

1. **File Upload Endpoint**: The `/api/files/upload` endpoint returns a 500 error with `{"detail":"Failed to create document record: 'name' is an invalid keyword argument for Document"}`
2. **Processing Status Endpoint**: The `/api/files/processing-status` endpoint returns a 404 error with `{"detail":"File not found"}`
3. **Test Endpoints**: Added test endpoints like `/api/test/ping` are not accessible and return a 404 error with `{"detail":"Not Found"}`

Curiously, the root endpoint at `http://localhost:8000/` does work and returns `{"message":"AI Assistant API is running","model":"nvidia/nemo-1","using_nemo":false,"using_mock":false}`. This suggests that the FastAPI application itself is running correctly, but there are issues with the router registration or endpoint handlers.

## What We've Tried

### 1. Diagnostic Analysis

We created several diagnostic scripts to analyze the application structure and routing configuration:

#### a. `check_import_paths.py` Results:

This script checks the module structure and verifies that routes are correctly defined in the routers:

```
Checking module: app.api.endpoints.files
============================================
Module found at: F:\Assistant\backend\app\api\endpoints\files.py
Module loaded successfully
Is package: False
Module file: F:\Assistant\backend\app\api\endpoints\files.py
Has router: Yes
Routes defined: 20
  - / [GET]
  - /{file_id} [GET]
  - /simple-upload [POST]
  - /upload [POST]
  - /{file_id}/download [GET]
  - /process [POST]
  - /{file_id}/retry-processing [POST]
  - /{file_id} [PATCH]
  - /{file_id} [DELETE]
  - /bulk-delete [POST]
  - /link [POST]
  - /unlink [POST]
  - /search [POST]
  - /{file_id}/preview [GET]
  - /test-status [GET]
  - /status [GET]
  - /processing-stats [GET]
  - /processing_status [GET]
  - /processing-status [GET]
  - /tags [GET]
```

The script confirmed that all the routers and routes are correctly defined in their respective modules.

#### b. `list_routes.py` Results:

This script examines the application routes and confirms they're registered correctly:

```
Registered routes in the application:
====================================
/openapi.json {'GET', 'HEAD'}
/docs {'GET', 'HEAD'}
/docs/oauth2-redirect {'GET', 'HEAD'}
/redoc {'GET', 'HEAD'}
/api/projects/ {'GET'}
...
/api/files/simple-upload {'POST'}
/api/files/upload {'POST'}
...
/api/files/processing-status {'GET'}
/api/test/ping {'GET'}
/api/test/test-upload {'POST'}
/api/test/db-test {'GET'}
/ {'GET'}
/health {'GET'}
```

The script shows that all the routes we've defined, including the test routes and processing-status endpoints, are correctly registered in the application.

#### c. `check_routes_registered.py` Results:

This comprehensive diagnostic script checks module loading, router inclusion, and route registration:

```
Module Loading Check
==================================================
Importing app.api.api...
✓ Successfully imported app.api.api
✗ Module doesn't have a router attribute
Importing app.api.endpoints.files...
✓ Successfully imported app.api.endpoints.files
✓ Module has router with 22 routes
Importing app.api.endpoints.test_endpoints...
✓ Successfully imported app.api.endpoints.test_endpoints
✓ Module has router with 4 routes
Importing app.api.endpoints.health...
✓ Successfully imported app.api.endpoints.health
✓ Module has router with 2 routes

API Router Includes Check
==================================================
Import statements in api.py:
  from fastapi import APIRouter
  from .endpoints import projects, user_prompts, files, semantic_search, chats, admin, test_endpoints, health

Router includes in api.py:
  api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
  ...
  api_router.include_router(test_endpoints.router, prefix="/test", tags=["test"])
  api_router.include_router(health.router, prefix="/health", tags=["health"])

files Routes Check
==================================================
Found 22 routes in files:
  / {'GET'}
    Function: get_files
    Module: app.api.endpoints.files
  ...
  /processing-status {'GET'}
    Function: get_processing_status
    Module: app.api.endpoints.files
  ...

API Server Health Check
==================================================
Testing connection to root endpoint...
✓ Server responded: {'message': 'AI Assistant API is running', 'model': 'nvidia/nemo-1', 'using_nemo': False, 'using_mock': False}
Testing /api/health/ping...
✗ Failed to access /api/health/ping: HTTP Error 404: Not Found
...
```

This confirms that all routes are correctly registered but still not accessible when directly accessed.

### 2. Direct database access testing

We created a direct database access script to check the Document model:

#### a. `fix_db_schema.py` Results:

```
Document Model Diagnostics
==================================================
Checking Document model schema...
Found 16 columns in 'documents' table:
  - id: VARCHAR
  - filename: VARCHAR
  - filepath: VARCHAR
  - filetype: VARCHAR
  - filesize: BIGINT
  - title: VARCHAR
  - description: TEXT
  - created_at: TIMESTAMP
  ...

Testing Document object creation...
✅ Created Document with standard fields
✅ Creating Document with 'name' field correctly raised: 'name' is an invalid keyword argument for Document
✅ Session rolled back successfully

Document class has 16 attributes:
  - id: VARCHAR
  - filename: VARCHAR
  - filepath: VARCHAR
  ...

Document class __init__ signature:
(self, **kwargs)

Found name-related attributes: ['__tablename__', 'filename']

Summary
==================================================
✅ Document model schema looks correct
✅ Document object creation works as expected
🔍 The issue is likely in the API layer that maps between 'name' and 'filename'
```

This confirmed that the Document model is correctly defined in the database and doesn't accept a 'name' field, only 'filename'.

#### b. Test direct upload script:

We created `upload_file_direct.py` to bypass the API and add files directly to the database:

```
✅ File copied to: F:\Assistant\data\uploads\4351280c-3d39-4ec7-8e4f-635ed454ad92_test_upload.txt
✅ Document record created with ID: 4351280c-3d39-4ec7-8e4f-635ed454ad92

Document details:
  - ID: 4351280c-3d39-4ec7-8e4f-635ed454ad92
  - Filename: Test File
  - File path: F:\Assistant\data\uploads\4351280c-3d39-4ec7-8e4f-635ed454ad92_test_upload.txt
  - File type: txt
  - File size: 192 bytes
  - Description: A test file
  - Created at: 2025-05-18 16:04:05.986760-04:00

✅ File uploaded successfully with ID: 4351280c-3d39-4ec7-8e4f-635ed454ad92
```

This confirmed that direct interaction with the database works as expected, so the issue is specifically with the API endpoints.

### 3. Standalone Test Applications

We created standalone FastAPI applications to verify that FastAPI routing works correctly in the environment:

#### a. `diag_app.py`:

A simple diagnostic app with basic endpoints:
```python
@main_router.get("/ping")
async def ping():
    return {"message": "pong from main router"}

@test_router.get("/hello")
async def hello():
    return {"message": "hello from test router"}
```

This app worked perfectly, with all endpoints accessible:
```
{"message":"pong from main router"}
{"message":"hello from test router"}
```

#### b. `test_minimal_app.py`:

Another minimal test application with direct endpoint definitions, which should bypass any potential router registration issues.

### 4. Code Modifications

We tried various code modifications to fix the issues:

1. **Schema changes**: Updated the document schema to use 'filename' instead of 'name'
2. **Direct document creation**: Modified the upload endpoint to create Document objects directly
3. **Multiple endpoint definitions**: Added multiple endpoint decorators for the processing status handler
4. **Error handling improvements**: Added better error handling in the processing status endpoint
5. **New test endpoints**: Added simple test endpoints that don't rely on complex logic
6. **New health module**: Created a standalone health.py module with simple endpoints

None of these modifications resolved the issue with accessing the endpoints.

## Modified Files

During our investigation, we modified or created the following files:

1. **Modified files**:
   - `/backend/app/api/api.py`: Added imports for new endpoint modules
   - `/backend/app/api/endpoints/files.py`: Updated endpoint handlers and added test endpoints
   - `/backend/app/schemas/document.py`: Changed 'name' to 'filename' in schema definitions

2. **Created files**:
   - `/backend/test_file_upload.py`: Test script for API endpoints
   - `/backend/test_file_upload_verbose.py`: Verbose test script with more diagnostic info
   - `/backend/fix_db_schema.py`: Diagnostic script for the Document model
   - `/backend/upload_file_direct.py`: Direct database upload script bypassing the API
   - `/backend/batch_upload_files.py`: Batch file upload script
   - `/backend/test_db_connection.py`: Database connection test script
   - `/backend/test_direct_upload.py`: Direct database upload test
   - `/backend/test_api_scan.py`: API scanning script
   - `/backend/diag_app.py`: Standalone diagnostic FastAPI app
   - `/backend/check_import_paths.py`: Module path check script
   - `/backend/clear_cache_and_run.py`: Script to clear module cache
   - `/backend/list_routes.py`: Route listing script
   - `/backend/check_routes_registered.py`: Comprehensive route diagnostic
   - `/backend/test_minimal_app.py`: Minimal FastAPI app for testing
   - `/backend/app/api/endpoints/health.py`: New health check endpoint module

## Project Structure

The relevant parts of the project structure are:

```
backend/
  ├── app/
  │   ├── api/
  │   │   ├── __init__.py
  │   │   ├── api.py                 # Router registration
  │   │   └── endpoints/
  │   │       ├── __init__.py
  │   │       ├── admin.py
  │   │       ├── chats.py
  │   │       ├── files.py           # File endpoints (problematic)
  │   │       ├── health.py          # Health check endpoints (added)
  │   │       ├── projects.py
  │   │       ├── semantic_search.py
  │   │       ├── test_endpoints.py  # Test endpoints (added)
  │   │       └── user_prompts.py
  │   ├── core/
  │   │   └── mock_nemo/
  │   │       └── __init__.py
  │   ├── db/
  │   │   ├── __init__.py
  │   │   ├── database.py            # Database connection
  │   │   ├── init_db.py
  │   │   ├── models/
  │   │   │   ├── __init__.py
  │   │   │   ├── document.py        # Document model definition
  │   │   │   ├── project.py
  │   │   │   └── ...
  │   │   └── repositories/
  │   │       ├── __init__.py
  │   │       ├── base_repository.py
  │   │       ├── document_repository.py
  │   │       └── ...
  │   ├── document_processing/
  │   │   ├── processor.py
  │   │   └── status_tracker.py
  │   ├── main.py                   # Main application entry point
  │   ├── rag/
  │   │   └── vector_store.py
  │   └── schemas/
  │       ├── __init__.py
  │       ├── document.py           # Document schemas (modified)
  │       └── ...
  ├── data/
  │   ├── hierarchy/
  │   ├── logs/
  │   ├── processed/
  │   └── uploads/                  # File uploads go here
  ├── requirements.txt
  └── test_*.py                     # Various test scripts created
```

## Current Theories and Next Steps

After extensive debugging, we have a few theories about what might be causing the issues:

1. **Middleware Interference**: There could be middleware in the application that's intercepting requests and blocking certain endpoints.

2. **Route Overriding**: Some routes might be registered multiple times or overridden by other routes.

3. **Import/Module Issues**: There might be an issue with how Python imports and caches modules.

4. **Path Resolution**: The URL paths might not be resolved correctly due to prefix issues.

5. **API Router Corruption**: The `api_router` might be modified or not include the routes correctly.

6. **Application Context**: The application context might not be properly maintained during request handling.

7. **Environment-Specific Issues**: There could be Windows-specific issues with path handling or file operations.

### Next Steps

To resolve these issues, we might need to consider more drastic interventions:

1. **Complete API Module Rewrite**: Create an entirely new API module with simplified, direct endpoint definitions.

2. **Application Structure Reorganization**: Restructure the application to use a flatter router hierarchy.

3. **Custom Route Registration**: Implement a custom mechanism for route registration that bypasses potential issues.

4. **Per-Component Test Applications**: Create small test applications for each component to isolate the issues.

5. **Middleware Debugging**: Add diagnostic middleware to track request/response flow.

6. **Direct FastAPI Registration**: Register endpoints directly with the main FastAPI application instead of through routers.

It's important to approach these changes carefully to avoid causing cascading issues with other components of the project.