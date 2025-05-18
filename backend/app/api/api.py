from fastapi import APIRouter

from .endpoints import projects, user_prompts, files, semantic_search, chats, admin

api_router = APIRouter()

# Include all API endpoint routers
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(user_prompts.router, prefix="/user-prompts", tags=["user_prompts"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(semantic_search.router, prefix="/semantic-search", tags=["semantic_search"])
api_router.include_router(chats.router, prefix="/chats", tags=["chats"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])