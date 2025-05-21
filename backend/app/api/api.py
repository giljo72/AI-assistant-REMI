from fastapi import APIRouter

from .endpoints import projects, user_prompts, files, semantic_search, chats, admin, test_endpoints, health, system
from .endpoints.fix_files import router as fix_files_router

api_router = APIRouter()

# Include all API endpoint routers
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(user_prompts.router, prefix="/user-prompts", tags=["user_prompts"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(semantic_search.router, prefix="/semantic-search", tags=["semantic_search"])
api_router.include_router(chats.router, prefix="/chats", tags=["chats"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(system.router, prefix="/system", tags=["system"])

# Add test endpoints for debugging
api_router.include_router(test_endpoints.router, prefix="/test", tags=["test"])

# Add health endpoints (these should always work)
api_router.include_router(health.router, prefix="/health", tags=["health"])

# Add fix_files router for testing
api_router.include_router(fix_files_router, prefix="/fix-files", tags=["fix_files"])