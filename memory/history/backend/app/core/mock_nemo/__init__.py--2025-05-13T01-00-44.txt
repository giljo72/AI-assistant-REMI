# backend\app\core\mock_nemo\__init__.py

class MockNemoModel:
    """Mock NeMo model for development purposes."""
    
    def __init__(self, model_name="nvidia/nemo-1"):
        self.model_name = model_name
        print(f"Initialized mock NeMo model: {model_name}")
    
    def generate(self, prompt, max_length=100):
        """Mock text generation."""
        return f"This is a mock response from NeMo model {self.model_name} for: {prompt[:30]}..."

    def embeddings(self, text):
        """Mock embeddings generation."""
        import numpy as np
        # Generate random embedding vector of standard size
        return np.random.rand(768)

# Create export functions
def load_model(model_name):
    """Load a mock NeMo model."""
    return MockNemoModel(model_name)

def get_embeddings(text, model=None):
    """Get mock embeddings."""
    model = model or MockNemoModel()
    return model.embeddings(text)