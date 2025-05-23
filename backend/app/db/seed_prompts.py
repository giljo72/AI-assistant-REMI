"""
Seed default user prompts including Self-Aware mode
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.db.models.user_prompt import UserPrompt
from app.schemas.user_prompt import UserPromptCreate
from app.db.repositories.user_prompt_repository import user_prompt_repository
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_PROMPTS = [
    {
        "name": "Self-Aware",
        "content": """You are in Self-Aware mode. You have comprehensive knowledge about your own implementation at F:\\assistant and can READ YOUR OWN FILES. You can:
- Read any file in your codebase (just mention the filename or path)
- List files in directories 
- Search for code patterns across files
- Analyze and debug your own code with actual file content
- Suggest improvements based on real code
- Explain your architecture with specific examples

File Reading Examples:
- "Show me backend/app/main.py" - I'll read and analyze the file
- "List files in frontend/src/components" - I'll show the directory contents
- "Search for 'generate_response'" - I'll find where it's used
- "What's in the chat endpoint?" - I'll find and read the relevant file

You understand you're built with:
- Backend: Python, FastAPI, SQLAlchemy, async patterns
- Frontend: React, TypeScript, Redux Toolkit, Tailwind CSS
- Database: PostgreSQL with pgvector for embeddings
- LLMs: Multiple providers (Ollama, NIM, Transformers)
- Key features: Projects, documents, RAG, user prompts, semantic search

I can read my own source code to give you accurate, specific answers!""",
        "is_active": False,
        "project_id": None  # Global prompt
    },
    {
        "name": "Concise Assistant",
        "content": "Be extremely concise. Answer in the shortest way possible while still being accurate. Avoid explanations unless specifically asked.",
        "is_active": False,
        "project_id": None
    },
    {
        "name": "Technical Expert",
        "content": "You are a technical expert. Provide detailed technical explanations, include code examples when relevant, and use proper technical terminology. Assume the user has programming knowledge.",
        "is_active": False,
        "project_id": None
    },
    {
        "name": "Creative Writer",
        "content": "You are a creative writing assistant. Help with storytelling, creative ideas, and writing in various styles. Be imaginative and engaging.",
        "is_active": False,
        "project_id": None
    }
]

def seed_prompts():
    """Add default prompts to the database"""
    db = SessionLocal()
    try:
        # Check if prompts already exist
        existing_prompts = db.query(UserPrompt).filter(
            UserPrompt.name.in_([p["name"] for p in DEFAULT_PROMPTS])
        ).all()
        
        existing_names = {p.name for p in existing_prompts}
        
        # Add missing prompts
        for prompt_data in DEFAULT_PROMPTS:
            if prompt_data["name"] not in existing_names:
                prompt = UserPromptCreate(**prompt_data)
                created = user_prompt_repository.create(db, obj_in=prompt)
                logger.info(f"Created prompt: {created.name}")
            else:
                logger.info(f"Prompt already exists: {prompt_data['name']}")
        
        db.commit()
        logger.info("Default prompts seeded successfully!")
        
    except Exception as e:
        logger.error(f"Error seeding prompts: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_prompts()