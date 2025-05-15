import numpy as np
import random
import time

class MockNemoModel:
    """Mock implementation of NeMo model for development purposes."""
    
    def __init__(self, model_name="nvidia/nemo-1"):
        """Initialize the mock NeMo model.
        
        Args:
            model_name: Name of the model to simulate
        """
        self.model_name = model_name
        self.embedding_dim = 1536  # Standard dimension for embeddings
        print(f"Initialized mock NeMo model: {model_name}")
    
    def generate(self, prompt, max_length=100):
        """Generate mock text response based on prompt.
        
        Args:
            prompt: The input text prompt
            max_length: Maximum length of generated text
            
        Returns:
            A mock response string
        """
        # Simulate processing time based on prompt length and max_length
        processing_time = (len(prompt) + max_length) / 1000
        time.sleep(processing_time)
        
        # Create deterministic but varied responses based on prompt
        responses = [
            f"This is a mock response to: {prompt[:30]}...",
            f"The AI Assistant is processing your request about {prompt.split()[0:3]}...",
            f"Mock NeMo model generated this placeholder text for: {prompt[:25]}...",
            f"Development mode: Simulating response to query about {' '.join(prompt.split()[0:4])}..."
        ]
        
        # Use a hash of the prompt to deterministically select a response template
        response_index = hash(prompt) % len(responses)
        base_response = responses[response_index]
        
        # Add some length variability
        filler_words = ["additionally", "furthermore", "however", "consequently", 
                        "nevertheless", "meanwhile", "specifically", "generally"]
        
        response = base_response
        target_length = min(max_length, 30 + (hash(prompt) % 50))
        
        while len(response) < target_length:
            filler = random.choice(filler_words)
            response += f" {filler},"
        
        return response
    
    def embeddings(self, text):
        """Generate mock embeddings for input text.
        
        Args:
            text: Input text to generate embeddings for
            
        Returns:
            Numpy array of mock embeddings
        """
        # Create deterministic but random-looking embeddings based on input text
        # Using hash of text to seed the random generator for consistency
        seed = hash(text) % (2**32)
        np.random.seed(seed)
        
        # Generate mock embeddings
        embeddings = np.random.normal(0, 0.1, self.embedding_dim)
        
        # Normalize embeddings to unit length as most embedding models do
        embeddings = embeddings / np.linalg.norm(embeddings)
        
        return embeddings


def load_model(model_name="nvidia/nemo-1"):
    """Load a mock NeMo model.
    
    Args:
        model_name: Name of the model to load
        
    Returns:
        MockNemoModel instance
    """
    print(f"Loading mock NeMo model: {model_name}")
    return MockNemoModel(model_name)


def get_embeddings(text, model=None):
    """Get embeddings for text using the specified model.
    
    Args:
        text: Input text to generate embeddings for
        model: Model to use for generating embeddings, or None to create a new one
        
    Returns:
        Numpy array of embeddings
    """
    if model is None:
        model = load_model()
    
    if isinstance(text, list):
        return [model.embeddings(t) for t in text]
    else:
        return model.embeddings(text)