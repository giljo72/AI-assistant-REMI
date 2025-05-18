"""
Quick test script to check only a few critical endpoints.
This focuses on the root path and direct routes to isolate issues.
"""
import requests

BASE_URL = "http://localhost:8000"
ENDPOINTS = [
    "/",                      # Root path
    "/health",                # Direct health endpoint
    "/direct-ping",           # Our direct ping endpoint
    "/api/direct-health",     # Our direct API health endpoint 
    "/api/direct-status",     # Our direct status endpoint
    "/api/health/ping",       # Router health ping
    "/api/health2/ping2",     # Our new health2 router
    "/api/fix-files/ping"     # Our new fix-files router
]

def test_endpoints():
    """Test a list of critical endpoints"""
    print("Testing critical endpoints...")
    
    for endpoint in ENDPOINTS:
        url = f"{BASE_URL}{endpoint}"
        try:
            response = requests.get(url, timeout=5)
            status = response.status_code
            
            # Print result with color based on status
            if status == 200:
                print(f"✅ GET {url}: Status {status}")
            else:
                print(f"❌ GET {url}: Status {status}")
                
            if status == 200:
                try:
                    # Try to print JSON response
                    print(f"   Response: {response.json()}")
                except:
                    # Fallback to text response
                    print(f"   Response: {response.text[:100]}...")
        except requests.RequestException as e:
            print(f"❌ GET {url}: Error - {str(e)}")

if __name__ == "__main__":
    test_endpoints()