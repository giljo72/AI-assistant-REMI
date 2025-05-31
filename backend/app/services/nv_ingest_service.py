"""
NVIDIA NV-Ingest Service Integration
Handles multimodal document extraction with smart model loading
"""
import os
import httpx
import logging
import asyncio
from typing import Dict, Any, Optional, List
from pathlib import Path
import json

logger = logging.getLogger(__name__)

class NVIngestService:
    """Service for interacting with NV-Ingest container"""
    
    def __init__(self, base_url: str = "http://localhost:8083"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=300.0)  # 5 min timeout for processing
        self._model_status = {
            "yolox": False,
            "paddleocr": False,
            "deplot": False,
            "cached": False
        }
        
    async def health_check(self) -> bool:
        """Check if NV-Ingest service is available"""
        # NV-Ingest requires complex multi-service setup
        # For now, always return False to use fallback
        logger.info("NV-Ingest not configured - using simple extraction")
        return False
        
        # Original implementation for when NV-Ingest is set up:
        # try:
        #     response = await self.client.get(f"{self.base_url}/health")
        #     return response.status_code == 200
        # except Exception as e:
        #     logger.error(f"NV-Ingest health check failed: {e}")
        #     return False
    
    async def get_model_status(self) -> Dict[str, Any]:
        """Get status of loaded models"""
        try:
            response = await self.client.get(f"{self.base_url}/v1/models")
            if response.status_code == 200:
                data = response.json()
                return {
                    "models_loaded": data.get("models", []),
                    "total_vram_used": data.get("vram_usage_gb", 0),
                    "status": "ready"
                }
        except Exception:
            pass
        
        return {
            "models_loaded": [],
            "total_vram_used": 0,
            "status": "unavailable"
        }
    
    def get_required_models(self, file_type: str) -> List[str]:
        """Determine which models are needed for a file type"""
        file_type = file_type.lower()
        
        # Text files need no models
        if file_type in ["txt", "md", "py", "js", "json", "csv"]:
            return []
        
        # DOCX might have charts/tables
        elif file_type in ["docx", "doc"]:
            return ["yolox", "deplot"]
        
        # PDFs need full suite
        elif file_type == "pdf":
            return ["yolox", "paddleocr", "deplot", "cached"]
        
        # Excel might have charts
        elif file_type in ["xlsx", "xls"]:
            return ["deplot"]
        
        # Default to basic detection
        return ["yolox"]
    
    async def extract_document(
        self,
        file_path: str,
        file_type: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extract content from document using NV-Ingest
        
        Returns:
            {
                "success": bool,
                "content": str,  # Extracted text
                "metadata": dict,  # Tables, charts, etc.
                "models_used": list,
                "processing_time": float
            }
        """
        # Check if service is available
        if not await self.health_check():
            logger.warning("NV-Ingest not available, falling back to simple extraction")
            return {
                "success": False,
                "fallback": True,
                "error": "NV-Ingest service not available"
            }
        
        # Determine required models
        required_models = self.get_required_models(file_type)
        
        # Prepare request
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f, 'application/octet-stream')}
                
                data = {
                    'file_type': file_type,
                    'extract_tables': True,
                    'extract_charts': True,
                    'extract_images': file_type == "pdf",  # Only for PDFs
                    'models': json.dumps(required_models)
                }
                
                # Send to NV-Ingest
                response = await self.client.post(
                    f"{self.base_url}/v1/extract",
                    files=files,
                    data=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Combine all extracted content
                    content_parts = []
                    
                    # Main text
                    if result.get("text"):
                        content_parts.append(result["text"])
                    
                    # Tables as markdown
                    for table in result.get("tables", []):
                        content_parts.append(f"\n## Table: {table.get('title', 'Untitled')}\n")
                        content_parts.append(table.get("markdown", ""))
                    
                    # Chart descriptions
                    for chart in result.get("charts", []):
                        content_parts.append(f"\n## Chart: {chart.get('title', 'Untitled')}\n")
                        content_parts.append(chart.get("description", ""))
                        if chart.get("data"):
                            content_parts.append(f"Data: {json.dumps(chart['data'])}")
                    
                    return {
                        "success": True,
                        "content": "\n\n".join(content_parts),
                        "metadata": {
                            "tables_count": len(result.get("tables", [])),
                            "charts_count": len(result.get("charts", [])),
                            "pages": result.get("pages", 1),
                            "has_images": bool(result.get("images", []))
                        },
                        "models_used": result.get("models_used", required_models),
                        "processing_time": result.get("processing_time", 0)
                    }
                else:
                    logger.error(f"NV-Ingest extraction failed: {response.status_code}")
                    return {
                        "success": False,
                        "error": f"Extraction failed: {response.status_code}",
                        "fallback": True
                    }
                    
        except Exception as e:
            logger.error(f"Error during NV-Ingest extraction: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "fallback": True
            }
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

# Singleton instance
_nv_ingest_service = None

def get_nv_ingest_service() -> NVIngestService:
    """Get or create the NV-Ingest service instance"""
    global _nv_ingest_service
    if _nv_ingest_service is None:
        _nv_ingest_service = NVIngestService()
    return _nv_ingest_service