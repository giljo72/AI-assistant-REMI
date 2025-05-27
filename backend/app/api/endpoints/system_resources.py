"""
System Resources Monitoring API Endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import psutil
import platform
import GPUtil
import shutil
import subprocess
import os

router = APIRouter(prefix="/api/system", tags=["system"])

def get_cpu_info_windows():
    """Get CPU info on Windows using wmic"""
    try:
        # Get CPU name
        result = subprocess.run(
            ['wmic', 'cpu', 'get', 'name', '/value'],
            capture_output=True, text=True, shell=True
        )
        cpu_model = ""
        for line in result.stdout.strip().split('\n'):
            if line.startswith('Name='):
                cpu_model = line.split('=', 1)[1].strip()
                break
        
        # Determine brand from model name
        brand = "Unknown"
        if "AMD" in cpu_model:
            brand = "AMD"
        elif "Intel" in cpu_model:
            brand = "Intel"
            
        return brand, cpu_model
    except:
        return "Unknown", "Unknown CPU"

def get_ram_speed_windows():
    """Get RAM speed on Windows using wmic"""
    try:
        result = subprocess.run(
            ['wmic', 'memorychip', 'get', 'speed', '/value'],
            capture_output=True, text=True, shell=True
        )
        speeds = []
        for line in result.stdout.strip().split('\n'):
            if line.startswith('Speed='):
                speed = line.split('=', 1)[1].strip()
                if speed and speed.isdigit():
                    speeds.append(int(speed))
        
        if speeds:
            # Return the most common speed (in case of mixed RAM)
            return f"{max(set(speeds), key=speeds.count)} MHz"
        return "Unknown"
    except:
        return "Unknown"

def get_disk_info_windows():
    """Get disk type on Windows"""
    try:
        # First try to get disk model
        result = subprocess.run(
            ['wmic', 'diskdrive', 'get', 'model,size', '/value'],
            capture_output=True, text=True, shell=True
        )
        
        disk_model = ""
        for line in result.stdout.strip().split('\n'):
            if line.startswith('Model='):
                disk_model = line.split('=', 1)[1].strip()
                break
        
        # Determine disk type from model
        disk_type = "HDD"
        if any(ssd_indicator in disk_model.upper() for ssd_indicator in ['SSD', 'NVME', 'M.2', 'SOLID STATE']):
            disk_type = "SSD"
            if 'NVME' in disk_model.upper():
                disk_type = "NVMe SSD"
        
        return disk_type, disk_model
    except:
        return "Storage", ""

@router.get("/resources")
async def get_system_resources() -> Dict[str, Any]:
    """Get real-time system resource usage"""
    try:
        # CPU Information
        cpu_usage = psutil.cpu_percent(interval=1)
        
        # Get CPU info based on platform
        if os.name == 'nt':  # Windows
            brand, model = get_cpu_info_windows()
        else:
            # Fallback for Linux/Mac
            cpu_info_str = platform.processor()
            brand = "AMD" if "AMD" in cpu_info_str else "Intel" if "Intel" in cpu_info_str else "Unknown"
            model = cpu_info_str
        
        cpu_info = {
            "usage": cpu_usage,
            "brand": brand,
            "model": model
        }
        
        # RAM Information
        ram = psutil.virtual_memory()
        ram_speed = get_ram_speed_windows() if os.name == 'nt' else "Unknown"
        
        ram_info = {
            "used_gb": ram.used / (1024**3),
            "total_gb": ram.total / (1024**3),
            "speed": ram_speed
        }
        
        # Disk Information
        disk = shutil.disk_usage('/')
        disk_type, disk_model = get_disk_info_windows() if os.name == 'nt' else ("Storage", "")
        
        disk_info = {
            "used_gb": disk.used / (1024**3),
            "total_gb": disk.total / (1024**3),
            "type": disk_type,
            "model": disk_model
        }
        
        # GPU Information (already handled by model status)
        gpu_info = {
            "utilization": 0,
            "name": "Unknown GPU"
        }
        
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]  # First GPU
                gpu_info["utilization"] = gpu.load * 100  # Convert to percentage
                gpu_info["name"] = gpu.name
        except:
            pass
        
        return {
            "cpu": cpu_info,
            "ram": ram_info,
            "disk": disk_info,
            "gpu": gpu_info
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system resources: {str(e)}")

@router.get("/gpu-stats")
async def get_gpu_stats() -> Dict[str, Any]:
    """Get detailed GPU statistics"""
    try:
        gpus = GPUtil.getGPUs()
        if not gpus:
            return {"error": "No GPU found"}
        
        gpu = gpus[0]  # First GPU
        return {
            "name": gpu.name,
            "load": gpu.load * 100,  # GPU utilization percentage
            "memory_used": gpu.memoryUsed / 1024,  # Convert to GB
            "memory_total": gpu.memoryTotal / 1024,  # Convert to GB
            "memory_free": gpu.memoryFree / 1024,  # Convert to GB
            "temperature": gpu.temperature
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get GPU stats: {str(e)}")