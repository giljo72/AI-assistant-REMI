import os
import sys

print("Testing NeMo mock implementation...")

# Add the project root to the path to allow imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # Try to import the mock
    from backend.app.core.mock_nemo import load_model
    
    # Try to initialize the model
    model = load_model("test-model")
    
    # Test generation
    response = model.generate("This is a test prompt")
    
    print("Mock NeMo implementation test successful!")
    print(f"Generated response: {response}")
    
except Exception as e:
    print(f"Error testing mock NeMo: {e}")