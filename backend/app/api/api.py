from fastapi import APIRouter

from .endpoints import projects, user_prompts, files, semantic_search, chats, admin, test_endpoints, health
from .endpoints.health2 import router as health2_router  # Import directly using an alias
from .endpoints.fix_files import router as fix_files_router  # Import directly using an alias

api_router = APIRouter()

# Include all API endpoint routers
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(user_prompts.router, prefix="/user-prompts", tags=["user_prompts"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(semantic_search.router, prefix="/semantic-search", tags=["semantic_search"])
api_router.include_router(chats.router, prefix="/chats", tags=["chats"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])

# Add test endpoints for debugging
api_router.include_router(test_endpoints.router, prefix="/test", tags=["test"])

# Add health endpoints (these should always work)
api_router.include_router(health.router, prefix="/health", tags=["health"])

# Add new health2 router for testing
api_router.include_router(health2_router, prefix="/health2", tags=["health2"])

# Add fix_files router for testing
api_router.include_router(fix_files_router, prefix="/fix-files", tags=["fix_files"])