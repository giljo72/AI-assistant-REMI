import subprocess 
import sys 
import time 
import os 
 
proc = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'app.main:app', '--reload', '--host', '10.1.0.224', '--port', '8000']) 
while proc.poll() is None and os.path.exists('../.services_running'): 
    time.sleep(1) 
if proc.poll() is None: 
    proc.terminate() 
