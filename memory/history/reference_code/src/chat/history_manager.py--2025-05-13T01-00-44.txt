# src/chat/history_manager.py
from typing import List, Dict, Any, Optional
import logging
import json
from datetime import datetime
import os
from pathlib import Path

from ..db.repositories.chat_repo import ChatRepository
from ..db.repositories.project_repo import ProjectRepository

logger = logging.getLogger(__name__)

class HistoryManager:
    """Manages chat history export and import"""
    
    def __init__(self, 
                chat_repo: ChatRepository,
                project_repo: ProjectRepository,
                export_path: str = "data/exports"):
        """
        Initialize the history manager
        
        Args:
            chat_repo: Repository for chat operations
            project_repo: Repository for project operations
            export_path: Path to export directory
        """
        self.chat_repo = chat_repo
        self.project_repo = project_repo
        
        self.export_path = Path(export_path)
        self.export_path.mkdir(parents=True, exist_ok=True)
    
    def export_chat_history(self, chat_id: int) -> Optional[str]:
        """
        Export chat history to a JSON file
        
        Args:
            chat_id: ID of chat to export
            
        Returns:
            Path to exported file if successful, None otherwise
        """
        try:
            # Get chat details
            chat = self.chat_repo.get_chat(chat_id)
            if not chat:
                logger.error(f"Chat {chat_id} not found")
                return None
            
            # Get project details
            project = self.project_repo.get_project(chat['project_id'])
            if not project:
                logger.error(f"Project {chat['project_id']} not found")
                return None
            
            # Get messages
            messages = self.chat_repo.get_chat_messages(chat_id)
            
            # Create export data
            export_data = {
                "chat_id": chat_id,
                "chat_name": chat['name'],
                "project_id": project['id'],
                "project_name": project['name'],
                "export_time": datetime.now().isoformat(),
                "messages": messages
            }
            
            # Create export filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_filename = f"chat_{chat_id}_{timestamp}.json"
            export_file_path = self.export_path / export_filename
            
            # Write to file
            with open(export_file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported chat {chat_id} to {export_file_path}")
            return str(export_file_path)
        except Exception as e:
            logger.error(f"Error exporting chat history: {e}")
            return None
    
    def get_export_list(self) -> List[Dict[str, Any]]:
        """
        Get list of all chat exports
        
        Returns:
            List of export file details
        """
        exports = []
        
        try:
            # List all JSON files in export directory
            for file_path in self.export_path.glob("*.json"):
                try:
                    # Read file to get metadata
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Extract key info
                    exports.append({
                        "file_name": file_path.name,
                        "file_path": str(file_path),
                        "chat_id": data.get("chat_id"),
                        "chat_name": data.get("chat_name"),
                        "project_name": data.get("project_name"),
                        "export_time": data.get("export_time"),
                        "message_count": len(data.get("messages", []))
                    })
                except Exception as e:
                    logger.error(f"Error reading export file {file_path}: {e}")
            
            # Sort by export time (newest first)
            exports.sort(key=lambda x: x.get("export_time", ""), reverse=True)
            
            return exports
        except Exception as e:
            logger.error(f"Error listing exports: {e}")
            return []
    
    def load_export(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Load a chat export file
        
        Args:
            file_path: Path to export file
            
        Returns:
            Export data if successful, None otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return data
        except Exception as e:
            logger.error(f"Error loading export file {file_path}: {e}")
            return None