import logging
from sqlalchemy.orm import Session

from .database import Base, engine, SessionLocal
from .repositories.project_repository import project_repository
from .repositories.user_prompt_repository import user_prompt_repository
from ..schemas.project import ProjectCreate
from ..schemas.user_prompt import UserPromptCreate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initial data for projects
INITIAL_PROJECTS = [
    {
        "name": "AI Research Project",
        "description": "Research project focused on artificial intelligence concepts and applications."
    },
    {
        "name": "React Frontend Development",
        "description": "Project for developing React-based frontend applications with TypeScript."
    },
    {
        "name": "FastAPI Backend",
        "description": "Backend development project using FastAPI, SQLAlchemy, and PostgreSQL."
    }
]

# Initial data for user prompts
INITIAL_USER_PROMPTS = [
    {
        "name": "Research Assistant",
        "content": "You are a research assistant helping with academic and technical research. Provide detailed, well-structured information with citations when available.",
        "project_id": None  # Will be linked to first project
    },
    {
        "name": "Code Helper",
        "content": "You are a coding assistant helping with programming tasks. Provide clean, well-documented code examples and explanations.",
        "project_id": None  # Will be linked to second project
    },
    {
        "name": "Writing Assistant",
        "content": "You are a writing assistant helping to improve text quality, clarity, and style. Suggest improvements while maintaining the original message.",
        "project_id": None  # Will be linked to third project
    }
]


def init_db(db: Session) -> None:
    """Initialize database with sample data."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create projects
    project_ids = []
    for project_data in INITIAL_PROJECTS:
        logger.info(f"Creating project: {project_data['name']}")
        project = project_repository.create(db, obj_in=ProjectCreate(**project_data))
        project_ids.append(project.id)
    
    # Create user prompts
    for i, prompt_data in enumerate(INITIAL_USER_PROMPTS):
        if i < len(project_ids):
            prompt_data["project_id"] = project_ids[i]
        
        logger.info(f"Creating user prompt: {prompt_data['name']}")
        user_prompt_repository.create(db, obj_in=UserPromptCreate(**prompt_data))
    
    logger.info("Database initialized with sample data")


def main() -> None:
    """Main function to initialize database."""
    logger.info("Creating initial data")
    db = SessionLocal()
    init_db(db)
    db.close()


if __name__ == "__main__":
    main()