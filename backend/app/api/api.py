from fastapi import APIRouter

from .endpoints import projects, user_prompts, files, semantic_search, chats, admin, health, system, models, self_analysis, personal_profiles, preferences, system_prompts, system_fast, system_resources, self_aware, action_approval, auth
from .endpoints.fix_files import router as fix_files_router

api_router = APIRouter()

# Authentication endpoints (no prefix to keep /api/auth/login)
api_router.include_router(auth.router, tags=["authentication"])

# Include all API endpoint routers
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(user_prompts.router, prefix="/user-prompts", tags=["user_prompts"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(semantic_search.router, prefix="/semantic-search", tags=["semantic_search"])
api_router.include_router(chats.router, prefix="/chats", tags=["chats"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(system.router, prefix="/system", tags=["system"])

# Test endpoints removed - were not used in production

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

# Add self-aware endpoints for code introspection
api_router.include_router(self_aware.router, tags=["self_aware"])

# DEPRECATED: Self-aware authentication endpoints - replaced by admin-only authentication
# api_router.include_router(self_aware_auth.router, prefix="/self-aware", tags=["self_aware_auth"])

# Add action approval endpoints
api_router.include_router(action_approval.router, prefix="/approvals", tags=["approvals"])

# DEPRECATED: Self-aware operations endpoints - uses old password authentication
# api_router.include_router(self_aware_ops.router, prefix="/self-aware-ops", tags=["self_aware_ops"])

# Test file chat endpoint removed - was not used in production