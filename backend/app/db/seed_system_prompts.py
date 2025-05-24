"""
Seed system prompts for different models
"""
from sqlalchemy import select
from app.db.database import SessionLocal
from app.db.models.user_prompt import UserPrompt

DEFAULT_ASSISTANT_PROMPT = """You are a helpful AI assistant designed to provide accurate, thoughtful, and practical assistance.

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

You cannot browse the internet, run code, or access external systems unless explicitly provided with tool access."""

DEEPSEEK_CODER_PROMPT = """You are an expert programming assistant focused on writing clean, efficient, and well-documented code.

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

Format code with proper syntax highlighting. Default to modern, idiomatic approaches unless legacy support is specified."""

def seed_system_prompts():
    """Create system prompts if they don't exist"""
    session = SessionLocal()
    try:
        # Check if system prompts already exist
        existing_default = session.query(UserPrompt).filter(
            UserPrompt.name == "System: Default Assistant"
        ).first()
        
        existing_coder = session.query(UserPrompt).filter(
            UserPrompt.name == "System: DeepSeek Coder"
        ).first()
        
        if not existing_default:
            # Create default assistant prompt
            default_prompt = UserPrompt(
                name="System: Default Assistant",
                content=DEFAULT_ASSISTANT_PROMPT,
                is_active=True,  # Active by default
                project_id=None  # Global prompt
            )
            session.add(default_prompt)
            print("Created System: Default Assistant prompt")
        else:
            print("System: Default Assistant prompt already exists")
        
        if not existing_coder:
            # Create DeepSeek coder prompt
            coder_prompt = UserPrompt(
                name="System: DeepSeek Coder",
                content=DEEPSEEK_CODER_PROMPT,
                is_active=False,  # Not active by default
                project_id=None  # Global prompt
            )
            session.add(coder_prompt)
            print("Created System: DeepSeek Coder prompt")
        else:
            print("System: DeepSeek Coder prompt already exists")
        
        session.commit()
        print("System prompts seeded successfully")
    except Exception as e:
        print(f"Error seeding prompts: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    seed_system_prompts()