from fastapi import APIRouter

from .endpoints import projects, user_prompts

api_router = APIRouter()

# Include all API endpoint routers
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(user_prompts.router, prefix="/user-prompts", tags=["user_prompts"])