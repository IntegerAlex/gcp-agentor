"""
Memory Manager Module

Shared memory layer using Firestore for persistent storage and context management.
"""

import os
import json
import logging
from typing import Any, Dict, Optional, List
from datetime import datetime, timedelta

try:
    from google.cloud import firestore
    from google.cloud.firestore_v1.base_document import DocumentSnapshot
    FIRESTORE_AVAILABLE = True
except ImportError:
    FIRESTORE_AVAILABLE = False
    firestore = None


class MemoryManager:
    """
    Manages shared memory using Firestore for persistent storage.
    
    Provides methods to store and retrieve context data, session information,
    and conversation history for multi-agent systems.
    """
    
    def __init__(self, project_id: Optional[str] = None, collection_name: str = "agentor_memory"):
        """
        Initialize the memory manager.
        
        Args:
            project_id: GCP project ID (uses default if not provided)
            collection_name: Firestore collection name for memory storage
        """
        self.project_id = project_id or os.getenv("GCP_PROJECT_ID")
        self.collection_name = collection_name
        self._logger = logging.getLogger(__name__)
        
        if not FIRESTORE_AVAILABLE:
            self._logger.warning("Firestore not available. Using in-memory storage.")
            self._use_firestore = False
            self._memory: Dict[str, Dict[str, Any]] = {}
        else:
            self._use_firestore = True
            try:
                self._db = firestore.Client(project=self.project_id)
                self._collection = self._db.collection(collection_name)
                self._logger.info(f"Initialized Firestore memory manager with collection: {collection_name}")
            except Exception as e:
                self._logger.error(f"Failed to initialize Firestore: {e}. Falling back to in-memory storage.")
                self._use_firestore = False
                self._memory = {}
    
    def get_session(self, user_id: str) -> Dict[str, Any]:
        """
        Get complete session data for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary containing all session data
        """
        if self._use_firestore:
            try:
                doc_ref = self._collection.document(f"user_{user_id}")
                doc = doc_ref.get()
                if doc.exists:
                    return doc.to_dict() or {}
                return {}
            except Exception as e:
                self._logger.error(f"Error getting session for user {user_id}: {e}")
                return {}
        else:
            return self._memory.get(f"user_{user_id}", {})
    
    def save_session(self, user_id: str, data: Dict[str, Any]) -> None:
        """
        Save complete session data for a user.
        
        Args:
            user_id: User identifier
            data: Session data to save
        """
        if self._use_firestore:
            try:
                doc_ref = self._collection.document(f"user_{user_id}")
                doc_ref.set(data, merge=True)
                self._logger.debug(f"Saved session for user {user_id}")
            except Exception as e:
                self._logger.error(f"Error saving session for user {user_id}: {e}")
        else:
            self._memory[f"user_{user_id}"] = data
    
    def get_context(self, user_id: str, key: str) -> Any:
        """
        Get a specific context value for a user.
        
        Args:
            user_id: User identifier
            key: Context key
            
        Returns:
            The context value or None if not found
        """
        session = self.get_session(user_id)
        return session.get("context", {}).get(key)
    
    def set_context(self, user_id: str, key: str, value: Any) -> None:
        """
        Set a specific context value for a user.
        
        Args:
            user_id: User identifier
            key: Context key
            value: Context value to set
        """
        session = self.get_session(user_id)
        if "context" not in session:
            session["context"] = {}
        session["context"][key] = value
        session["last_updated"] = datetime.utcnow().isoformat()
        self.save_session(user_id, session)
    
    def get_conversation_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get conversation history for a user.
        
        Args:
            user_id: User identifier
            limit: Maximum number of messages to return
            
        Returns:
            List of conversation messages
        """
        session = self.get_session(user_id)
        history = session.get("conversation_history", [])
        return history[-limit:] if limit > 0 else history
    
    def add_conversation_message(self, user_id: str, message: Dict[str, Any]) -> None:
        """
        Add a message to the conversation history.
        
        Args:
            user_id: User identifier
            message: Message to add to history
        """
        session = self.get_session(user_id)
        if "conversation_history" not in session:
            session["conversation_history"] = []
        
        # Add timestamp if not present
        if "timestamp" not in message:
            message["timestamp"] = datetime.utcnow().isoformat()
        
        session["conversation_history"].append(message)
        
        # Keep only last 100 messages to prevent memory bloat
        if len(session["conversation_history"]) > 100:
            session["conversation_history"] = session["conversation_history"][-100:]
        
        session["last_updated"] = datetime.utcnow().isoformat()
        self.save_session(user_id, session)
    
    def clear_context(self, user_id: str) -> None:
        """
        Clear all context data for a user.
        
        Args:
            user_id: User identifier
        """
        session = self.get_session(user_id)
        session["context"] = {}
        session["last_updated"] = datetime.utcnow().isoformat()
        self.save_session(user_id, session)
    
    def clear_conversation_history(self, user_id: str) -> None:
        """
        Clear conversation history for a user.
        
        Args:
            user_id: User identifier
        """
        session = self.get_session(user_id)
        session["conversation_history"] = []
        session["last_updated"] = datetime.utcnow().isoformat()
        self.save_session(user_id, session)
    
    def delete_session(self, user_id: str) -> None:
        """
        Delete all session data for a user.
        
        Args:
            user_id: User identifier
        """
        if self._use_firestore:
            try:
                doc_ref = self._collection.document(f"user_{user_id}")
                doc_ref.delete()
                self._logger.info(f"Deleted session for user {user_id}")
            except Exception as e:
                self._logger.error(f"Error deleting session for user {user_id}: {e}")
        else:
            self._memory.pop(f"user_{user_id}", None)
    
    def get_session_info(self, user_id: str) -> Dict[str, Any]:
        """
        Get session metadata and statistics.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with session information
        """
        session = self.get_session(user_id)
        history = session.get("conversation_history", [])
        
        return {
            "user_id": user_id,
            "context_keys": list(session.get("context", {}).keys()),
            "message_count": len(history),
            "last_updated": session.get("last_updated"),
            "created_at": session.get("created_at"),
            "context_size": len(json.dumps(session.get("context", {})))
        }
    
    def cleanup_old_sessions(self, days_old: int = 30) -> int:
        """
        Clean up sessions older than specified days.
        
        Args:
            days_old: Number of days after which sessions are considered old
            
        Returns:
            Number of sessions deleted
        """
        if not self._use_firestore:
            # For in-memory storage, we don't have timestamps, so skip cleanup
            return 0
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        deleted_count = 0
        
        try:
            docs = self._collection.where("last_updated", "<", cutoff_date.isoformat()).stream()
            for doc in docs:
                doc.reference.delete()
                deleted_count += 1
            
            self._logger.info(f"Cleaned up {deleted_count} old sessions")
        except Exception as e:
            self._logger.error(f"Error during cleanup: {e}")
        
        return deleted_count
    
    def export_session(self, user_id: str) -> str:
        """
        Export session data as JSON string.
        
        Args:
            user_id: User identifier
            
        Returns:
            JSON string representation of session data
        """
        session = self.get_session(user_id)
        return json.dumps(session, indent=2, default=str)
    
    def import_session(self, user_id: str, json_data: str) -> bool:
        """
        Import session data from JSON string.
        
        Args:
            user_id: User identifier
            json_data: JSON string containing session data
            
        Returns:
            True if import was successful, False otherwise
        """
        try:
            data = json.loads(json_data)
            self.save_session(user_id, data)
            return True
        except Exception as e:
            self._logger.error(f"Error importing session for user {user_id}: {e}")
            return False 