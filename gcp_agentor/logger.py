"""
Reasoning Logger Module

Comprehensive logging of agent decisions and reasoning traces.
"""

import os
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

try:
    from google.cloud import firestore
    FIRESTORE_AVAILABLE = True
except ImportError:
    FIRESTORE_AVAILABLE = False
    firestore = None


@dataclass
class ReasoningStep:
    """Represents a single reasoning step in the decision process."""
    step_id: str
    timestamp: str
    step_type: str  # "intent_analysis", "agent_selection", "invocation", "response"
    description: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.metadata is None:
            self.metadata = {}


class ReasoningLogger:
    """
    Logs reasoning trace and decisions for multi-agent systems.
    
    Stores detailed logs in Firestore for analysis and debugging.
    """
    
    def __init__(self, project_id: Optional[str] = None, collection_name: str = "agentor_logs"):
        """
        Initialize the reasoning logger.
        
        Args:
            project_id: GCP project ID
            collection_name: Firestore collection name for logs
        """
        self.project_id = project_id or os.getenv("GCP_PROJECT_ID")
        self.collection_name = collection_name
        self._logger = logging.getLogger(__name__)
        
        if not FIRESTORE_AVAILABLE:
            self._logger.warning("Firestore not available. Using in-memory logging.")
            self._use_firestore = False
            self._logs: Dict[str, List[Dict[str, Any]]] = {}
        else:
            self._use_firestore = True
            try:
                self._db = firestore.Client(project=self.project_id)
                self._collection = self._db.collection(collection_name)
                self._logger.info(f"Initialized Firestore logger with collection: {collection_name}")
            except Exception as e:
                self._logger.error(f"Failed to initialize Firestore logger: {e}. Falling back to in-memory logging.")
                self._use_firestore = False
                self._logs = {}
    
    def log(
        self, 
        user_id: str, 
        step: str, 
        details: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> None:
        """
        Log a reasoning step.
        
        Args:
            user_id: User identifier
            step: Step description
            details: Step details and data
            session_id: Optional session identifier
        """
        timestamp = datetime.utcnow().isoformat()
        session_id = session_id or f"session_{int(datetime.utcnow().timestamp())}"
        
        log_entry = {
            "user_id": user_id,
            "session_id": session_id,
            "timestamp": timestamp,
            "step": step,
            "details": details
        }
        
        if self._use_firestore:
            try:
                doc_ref = self._collection.document(f"user_{user_id}").collection("logs").document()
                doc_ref.set(log_entry)
                self._logger.debug(f"Logged step for user {user_id}: {step}")
            except Exception as e:
                self._logger.error(f"Error logging step for user {user_id}: {e}")
        else:
            if user_id not in self._logs:
                self._logs[user_id] = []
            self._logs[user_id].append(log_entry)
    
    def log_reasoning_step(
        self, 
        user_id: str, 
        reasoning_step: ReasoningStep,
        session_id: Optional[str] = None
    ) -> None:
        """
        Log a structured reasoning step.
        
        Args:
            user_id: User identifier
            reasoning_step: ReasoningStep object
            session_id: Optional session identifier
        """
        details = {
            "step_id": reasoning_step.step_id,
            "step_type": reasoning_step.step_type,
            "description": reasoning_step.description,
            "input_data": reasoning_step.input_data,
            "output_data": reasoning_step.output_data,
            "metadata": reasoning_step.metadata
        }
        
        self.log(user_id, f"reasoning_step_{reasoning_step.step_type}", details, session_id)
    
    def log_intent_analysis(
        self, 
        user_id: str, 
        message: str, 
        detected_intent: str, 
        confidence: float,
        alternatives: List[str] = None,
        session_id: Optional[str] = None
    ) -> None:
        """
        Log intent analysis results.
        
        Args:
            user_id: User identifier
            message: Original message
            detected_intent: Detected intent
            confidence: Confidence score
            alternatives: Alternative intents
            session_id: Optional session identifier
        """
        details = {
            "message": message,
            "detected_intent": detected_intent,
            "confidence": confidence,
            "alternatives": alternatives or []
        }
        
        self.log(user_id, "intent_analysis", details, session_id)
    
    def log_agent_selection(
        self, 
        user_id: str, 
        intent: str, 
        selected_agent: str,
        available_agents: List[str],
        selection_reason: str,
        session_id: Optional[str] = None
    ) -> None:
        """
        Log agent selection process.
        
        Args:
            user_id: User identifier
            intent: The intent to handle
            selected_agent: Selected agent name
            available_agents: List of available agents
            selection_reason: Reason for selection
            session_id: Optional session identifier
        """
        details = {
            "intent": intent,
            "selected_agent": selected_agent,
            "available_agents": available_agents,
            "selection_reason": selection_reason
        }
        
        self.log(user_id, "agent_selection", details, session_id)
    
    def log_agent_invocation(
        self, 
        user_id: str, 
        agent_name: str, 
        input_message: str,
        context: Dict[str, Any],
        response: str,
        execution_time: float,
        session_id: Optional[str] = None
    ) -> None:
        """
        Log agent invocation details.
        
        Args:
            user_id: User identifier
            agent_name: Agent name
            input_message: Input message
            context: Context data
            response: Agent response
            execution_time: Execution time in seconds
            session_id: Optional session identifier
        """
        details = {
            "agent_name": agent_name,
            "input_message": input_message,
            "context": context,
            "response": response,
            "execution_time": execution_time
        }
        
        self.log(user_id, "agent_invocation", details, session_id)
    
    def log_error(
        self, 
        user_id: str, 
        error_type: str, 
        error_message: str,
        stack_trace: Optional[str] = None,
        context: Dict[str, Any] = None,
        session_id: Optional[str] = None
    ) -> None:
        """
        Log error information.
        
        Args:
            user_id: User identifier
            error_type: Type of error
            error_message: Error message
            stack_trace: Optional stack trace
            context: Error context
            session_id: Optional session identifier
        """
        details = {
            "error_type": error_type,
            "error_message": error_message,
            "stack_trace": stack_trace,
            "context": context or {}
        }
        
        self.log(user_id, "error", details, session_id)
    
    def get_logs(
        self, 
        user_id: str, 
        limit: int = 100,
        session_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get logs for a user.
        
        Args:
            user_id: User identifier
            limit: Maximum number of logs to return
            session_id: Optional session filter
            
        Returns:
            List of log entries
        """
        if self._use_firestore:
            try:
                query = self._collection.document(f"user_{user_id}").collection("logs")
                
                if session_id:
                    query = query.where("session_id", "==", session_id)
                
                query = query.order_by("timestamp", direction=firestore.Query.DESCENDING).limit(limit)
                docs = query.stream()
                
                logs = []
                for doc in docs:
                    log_data = doc.to_dict()
                    log_data["log_id"] = doc.id
                    logs.append(log_data)
                
                return logs
            except Exception as e:
                self._logger.error(f"Error getting logs for user {user_id}: {e}")
                return []
        else:
            user_logs = self._logs.get(user_id, [])
            if session_id:
                user_logs = [log for log in user_logs if log.get("session_id") == session_id]
            
            # Sort by timestamp descending and limit
            user_logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            return user_logs[:limit]
    
    def get_session_logs(self, user_id: str, session_id: str) -> List[Dict[str, Any]]:
        """
        Get all logs for a specific session.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            
        Returns:
            List of log entries for the session
        """
        return self.get_logs(user_id, limit=1000, session_id=session_id)
    
    def get_reasoning_trace(
        self, 
        user_id: str, 
        session_id: str
    ) -> List[ReasoningStep]:
        """
        Get structured reasoning trace for a session.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            
        Returns:
            List of ReasoningStep objects
        """
        logs = self.get_session_logs(user_id, session_id)
        reasoning_steps = []
        
        for log in logs:
            if log.get("step", "").startswith("reasoning_step_"):
                details = log.get("details", {})
                step = ReasoningStep(
                    step_id=details.get("step_id", ""),
                    timestamp=log.get("timestamp", ""),
                    step_type=details.get("step_type", ""),
                    description=details.get("description", ""),
                    input_data=details.get("input_data", {}),
                    output_data=details.get("output_data", {}),
                    metadata=details.get("metadata", {})
                )
                reasoning_steps.append(step)
        
        return reasoning_steps
    
    def export_logs(self, user_id: str, session_id: Optional[str] = None) -> str:
        """
        Export logs as JSON string.
        
        Args:
            user_id: User identifier
            session_id: Optional session filter
            
        Returns:
            JSON string representation of logs
        """
        logs = self.get_logs(user_id, limit=1000, session_id=session_id)
        return json.dumps(logs, indent=2, default=str)
    
    def cleanup_old_logs(self, days_old: int = 30) -> int:
        """
        Clean up logs older than specified days.
        
        Args:
            days_old: Number of days after which logs are considered old
            
        Returns:
            Number of logs deleted
        """
        if not self._use_firestore:
            # For in-memory storage, we don't have timestamps, so skip cleanup
            return 0
        
        cutoff_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - days_old)
        
        deleted_count = 0
        
        try:
            # This would require a more complex query structure in Firestore
            # For now, we'll just log the cleanup attempt
            self._logger.info(f"Cleanup requested for logs older than {days_old} days")
        except Exception as e:
            self._logger.error(f"Error during log cleanup: {e}")
        
        return deleted_count
    
    def get_log_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get log statistics for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with log statistics
        """
        logs = self.get_logs(user_id, limit=1000)
        
        if not logs:
            return {
                "user_id": user_id,
                "total_logs": 0,
                "sessions": 0,
                "step_types": {},
                "errors": 0
            }
        
        sessions = set(log.get("session_id") for log in logs)
        step_types = {}
        errors = 0
        
        for log in logs:
            step = log.get("step", "")
            step_types[step] = step_types.get(step, 0) + 1
            
            if step == "error":
                errors += 1
        
        return {
            "user_id": user_id,
            "total_logs": len(logs),
            "sessions": len(sessions),
            "step_types": step_types,
            "errors": errors,
            "date_range": {
                "earliest": min(log.get("timestamp", "") for log in logs),
                "latest": max(log.get("timestamp", "") for log in logs)
            }
        } 