"""
System prompts for different models and scenarios
"""

DEFAULT_SYSTEM_PROMPT = """You are a helpful AI assistant designed to provide accurate, thoughtful, and practical assistance.

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

def get_system_prompt(model_name: str, user_profile: dict = None) -> str:
    """
    Get the appropriate system prompt for a model, optionally including user profile data
    
    Args:
        model_name: The name of the model
        user_profile: Optional user profile data to append
        
    Returns:
        The complete system prompt
    """
    # Select base prompt based on model
    if 'deepseek-coder' in model_name.lower():
        base_prompt = DEEPSEEK_CODER_PROMPT
    else:
        base_prompt = DEFAULT_SYSTEM_PROMPT
    
    # Append user profile if provided
    if user_profile:
        profile_text = _format_user_profile(user_profile)
        if profile_text:
            base_prompt += f"\n\n{profile_text}"
    
    return base_prompt

def _format_user_profile(profile: dict) -> str:
    """Format user profile data into a prompt addition"""
    if not profile:
        return ""
    
    parts = ["Personal context about the user you're assisting:"]
    
    if profile.get("name"):
        parts.append(f"- Name: {profile['name']}")
    
    if profile.get("address"):
        parts.append(f"- Location: {profile['address']}")
    
    # Add custom fields
    custom_fields = profile.get("customFields", [])
    for field in custom_fields:
        if field.get("key") and field.get("value"):
            parts.append(f"- {field['key']}: {field['value']}")
    
    if len(parts) > 1:  # Has more than just the header
        return "\n".join(parts)
    
    return ""