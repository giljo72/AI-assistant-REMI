from fastapi import APIRouter

from .endpoints import projects, user_prompts, files, semantic_search, chats, admin, test_endpoints, health, system, models, self_analysis, personal_profiles, preferences, system_prompts, system_fast, system_resources
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

# Add model management endpoints
api_router.include_router(models.router, prefix="/models", tags=["models"])

# Add self-analysis endpoints (development mode)
api_router.include_router(self_analysis.router, tags=["self_analysis"])

# Add personal profiles endpoints
api_router.include_router(personal_profiles.router, prefix="/personal-profiles", tags=["personal_profiles"])

# Add user preferences endpoints
api_router.include_router(preferences.router, prefix="/preferences", tags=["preferences"])

# Add system prompts endpoints
api_router.include_router(system_prompts.router, prefix="/system-prompts", tags=["system_prompts"])

# Add fast system endpoints for UI responsiveness
api_router.include_router(system_fast.router, prefix="/system", tags=["system"])

# Add system resources monitoring endpoints
api_router.include_router(system_resources.router, prefix="/system", tags=["system_resources"])