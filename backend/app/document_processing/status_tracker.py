from typing import Dict, List, Optional, Any
import time
from datetime import datetime, timedelta
import threading
import json
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProcessingStatusTracker:
    """
    Tracks the status of document processing tasks with performance metrics.
    """
    
    def __init__(self, status_file_path: Optional[str] = None):
        """
        Initialize the status tracker.
        
        Args:
            status_file_path: Path to a file for persisting status information
        """
        self.status_file_path = status_file_path
        self.lock = threading.RLock()
        
        # Status storage
        self.processing_files: Dict[str, Dict[str, Any]] = {}
        self.queue_files: List[str] = []
        self.processing_history: List[Dict[str, Any]] = []
        
        # Performance metrics
        self.total_processed = 0
        self.total_failed = 0
        self.avg_processing_time = 0
        self.gpu_usage = 0
        
        # Load status from file if it exists
        if status_file_path and os.path.exists(status_file_path):
            self._load_from_file()
    
    def add_to_queue(self, document_id: str, filename: str, size: int) -> None:
        """
        Add a document to the processing queue.
        
        Args:
            document_id: The document ID
            filename: The filename
            size: The file size in bytes
        """
        with self.lock:
            if document_id not in self.processing_files and document_id not in self.queue_files:
                self.queue_files.append(document_id)
                logger.info(f"Added document {document_id} to processing queue")
                self._save_to_file()
    
    def start_processing(self, document_id: str) -> None:
        """
        Mark a document as being processed.
        
        Args:
            document_id: The document ID
        """
        with self.lock:
            # Remove from queue if present
            if document_id in self.queue_files:
                self.queue_files.remove(document_id)
            
            # Add to processing list
            self.processing_files[document_id] = {
                "start_time": time.time(),
                "progress": 0,
                "eta_seconds": None
            }
            logger.info(f"Started processing document {document_id}")
            self._save_to_file()
    
    def update_progress(self, document_id: str, progress: float) -> None:
        """
        Update the processing progress for a document.
        
        Args:
            document_id: The document ID
            progress: Progress percentage (0-100)
        """
        with self.lock:
            if document_id in self.processing_files:
                self.processing_files[document_id]["progress"] = progress
                
                # Calculate ETA based on progress and time elapsed
                start_time = self.processing_files[document_id]["start_time"]
                elapsed = time.time() - start_time
                if progress > 0:
                    total_time_estimate = elapsed / (progress / 100)
                    remaining = total_time_estimate - elapsed
                    self.processing_files[document_id]["eta_seconds"] = remaining
                
                logger.debug(f"Updated progress for document {document_id} to {progress}%")
                self._save_to_file()
    
    def finish_processing(
        self, document_id: str, success: bool, chunk_count: Optional[int] = None
    ) -> None:
        """
        Mark a document as finished processing.
        
        Args:
            document_id: The document ID
            success: Whether processing was successful
            chunk_count: Number of chunks created
        """
        with self.lock:
            if document_id in self.processing_files:
                start_time = self.processing_files[document_id]["start_time"]
                processing_time = time.time() - start_time
                
                # Add to history
                history_entry = {
                    "document_id": document_id,
                    "success": success,
                    "processing_time": processing_time,
                    "timestamp": datetime.now().isoformat(),
                    "chunk_count": chunk_count
                }
                self.processing_history.append(history_entry)
                
                # Limit history size
                if len(self.processing_history) > 100:
                    self.processing_history = self.processing_history[-100:]
                
                # Update metrics
                if success:
                    self.total_processed += 1
                    # Update average processing time
                    if self.avg_processing_time == 0:
                        self.avg_processing_time = processing_time
                    else:
                        self.avg_processing_time = (
                            (self.avg_processing_time * (self.total_processed - 1) + processing_time) / 
                            self.total_processed
                        )
                else:
                    self.total_failed += 1
                
                # Remove from processing list
                del self.processing_files[document_id]
                
                logger.info(
                    f"Finished processing document {document_id} in {processing_time:.2f}s "
                    f"({'success' if success else 'failed'})"
                )
                self._save_to_file()
    
    def set_gpu_usage(self, usage_percent: float) -> None:
        """
        Set the current GPU usage percentage.
        
        Args:
            usage_percent: GPU usage as a percentage (0-100)
        """
        with self.lock:
            self.gpu_usage = usage_percent
            self._save_to_file()
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current processing status.
        
        Returns:
            Dict containing processing status information
        """
        with self.lock:
            # Calculate overall metrics
            queued_count = len(self.queue_files)
            processing_count = len(self.processing_files)
            
            # Calculate overall ETA
            eta = 0
            if self.avg_processing_time > 0:
                eta = self.avg_processing_time * (queued_count + processing_count * 0.5)
                
                # Add individual ETAs for currently processing files
                for doc_id, info in self.processing_files.items():
                    if info.get("eta_seconds") is not None:
                        eta = max(eta, info["eta_seconds"])
            
            return {
                "total_files": self.total_processed + self.total_failed + processing_count + queued_count,
                "processed_files": self.total_processed,
                "failed_files": self.total_failed,
                "processing_files": processing_count,
                "queued_files": queued_count,
                "total_chunks": sum(
                    entry.get("chunk_count") or 0 for entry in self.processing_history 
                    if entry.get("success", False)
                ),
                "gpu_usage": self.gpu_usage,
                "eta": eta,
                "avg_processing_time": self.avg_processing_time,
                "processing_files_info": self.processing_files
            }
    
    def reset_metrics(self) -> None:
        """
        Reset all metrics and status information.
        """
        with self.lock:
            self.total_processed = 0
            self.total_failed = 0
            self.avg_processing_time = 0
            self.processing_history = []
            self._save_to_file()
    
    def _save_to_file(self) -> None:
        """Save current status to file if path is configured."""
        if not self.status_file_path:
            return
        
        try:
            status_data = {
                "processing_files": self.processing_files,
                "queue_files": self.queue_files,
                "processing_history": self.processing_history,
                "total_processed": self.total_processed,
                "total_failed": self.total_failed,
                "avg_processing_time": self.avg_processing_time,
                "gpu_usage": self.gpu_usage,
                "last_updated": datetime.now().isoformat()
            }
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.status_file_path), exist_ok=True)
            
            # Write to temporary file first, then rename for atomicity
            temp_path = f"{self.status_file_path}.tmp"
            with open(temp_path, "w") as f:
                json.dump(status_data, f)
            
            os.replace(temp_path, self.status_file_path)
        except Exception as e:
            logger.error(f"Error saving status to file: {str(e)}")
    
    def _load_from_file(self) -> None:
        """Load status from file if it exists."""
        try:
            with open(self.status_file_path, "r") as f:
                status_data = json.load(f)
            
            self.processing_files = status_data.get("processing_files", {})
            self.queue_files = status_data.get("queue_files", [])
            self.processing_history = status_data.get("processing_history", [])
            self.total_processed = status_data.get("total_processed", 0)
            self.total_failed = status_data.get("total_failed", 0)
            self.avg_processing_time = status_data.get("avg_processing_time", 0)
            self.gpu_usage = status_data.get("gpu_usage", 0)
            
            logger.info(f"Loaded status from file: {self.status_file_path}")
        except Exception as e:
            logger.error(f"Error loading status from file: {str(e)}")


# Create a singleton instance
status_tracker = ProcessingStatusTracker(
    status_file_path=os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
        "data", "processing_status.json"
    )
)