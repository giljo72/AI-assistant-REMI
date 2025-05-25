"""
Repository for System Prompt CRUD operations
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.models.system_prompt import SystemPrompt
from app.db.repositories.base_repository import BaseRepository
from app.schemas.system_prompt import SystemPromptCreate, SystemPromptUpdate


class SystemPromptRepository(BaseRepository[SystemPrompt, SystemPromptCreate, SystemPromptUpdate]):
    """Repository for managing system prompts"""
    
    def __init__(self):
        super().__init__(SystemPrompt)
    
    def get_all(self, db: Session) -> List[SystemPrompt]:
        """Get all system prompts ordered by name"""
        stmt = select(SystemPrompt).order_by(SystemPrompt.name)
        return db.execute(stmt).scalars().all()
    
    def get_by_category(self, db: Session, category: str) -> List[SystemPrompt]:
        """Get all system prompts in a specific category"""
        stmt = select(SystemPrompt).where(
            SystemPrompt.category == category
        ).order_by(SystemPrompt.name)
        return db.execute(stmt).scalars().all()
    
    def get_active(self, db: Session) -> Optional[SystemPrompt]:
        """Get the currently active system prompt"""
        stmt = select(SystemPrompt).where(SystemPrompt.is_active == True)
        return db.execute(stmt).scalar_one_or_none()
    
    def set_active(self, db: Session, prompt_id: UUID) -> SystemPrompt:
        """Set a system prompt as active (deactivates all others)"""
        # The database trigger will handle deactivating others
        prompt = self.get(db, prompt_id)
        if not prompt:
            raise ValueError(f"System prompt with id {prompt_id} not found")
        
        prompt.is_active = True
        db.commit()
        db.refresh(prompt)
        return prompt
    
    def deactivate_all(self, db: Session) -> None:
        """Deactivate all system prompts"""
        stmt = select(SystemPrompt).where(SystemPrompt.is_active == True)
        active_prompts = db.execute(stmt).scalars().all()
        
        for prompt in active_prompts:
            prompt.is_active = False
        
        db.commit()
    
    def create_default_prompts(self, db: Session) -> List[SystemPrompt]:
        """Create the default system prompts if they don't exist"""
        created_prompts = []
        
        default_prompts = [
            {
                "name": "Default Assistant",
                "content": """You are a helpful AI assistant designed to provide accurate, thoughtful, and practical assistance.

Core behaviors:
- Answer questions directly and comprehensively
- Admit uncertainty rather than guessing
- Ask clarifying questions when requests are ambiguous
- Provide step-by-step reasoning for complex topics
- Cite sources or indicate when information may be dated
- Maintain a professional yet conversational tone

When responding:
1. Start with the most relevant information
2. Structure longer responses with clear sections
3. Offer additional context when it adds value
4. Suggest related topics only when relevant

You cannot browse the internet, run code, or access external systems unless explicitly provided with tool access.""",
                "description": "General-purpose assistant for everyday tasks and questions",
                "category": "general",
                "is_default": True,
                "is_active": True  # Default is active by default
            },
            {
                "name": "Coding Assistant",
                "content": """You are an expert programming assistant focused on writing clean, efficient, and well-documented code.

Core principles:
- Provide working code examples with clear explanations
- Follow language-specific best practices and conventions
- Include error handling and edge cases
- Comment complex logic, but avoid over-commenting obvious code
- Suggest optimizations when relevant
- Explain trade-offs between different approaches

When writing code:
1. Ask about specific requirements if not clear (language version, frameworks, constraints)
2. Provide complete, runnable examples when possible
3. Include example usage/test cases
4. Mention potential security considerations
5. Explain time/space complexity for algorithms

Format code with proper syntax highlighting. Default to modern, idiomatic approaches unless legacy support is specified.""",
                "description": "Specialized assistant for programming and software development",
                "category": "coding",
                "is_default": True,
                "is_active": False
            }
        ]
        
        for prompt_data in default_prompts:
            # Check if prompt already exists
            existing = db.query(SystemPrompt).filter(
                SystemPrompt.name == prompt_data["name"]
            ).first()
            
            if not existing:
                prompt = SystemPrompt(**prompt_data)
                db.add(prompt)
                created_prompts.append(prompt)
        
        if created_prompts:
            db.commit()
        
        return created_prompts