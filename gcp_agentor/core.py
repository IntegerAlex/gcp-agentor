"""
Core Orchestrator Module

Main orchestrator interface for external applications (Flask, FastAPI, etc.).
"""

import os
import logging
from typing import Any, Dict, Optional
from .agent_registry import AgentRegistry
from .router import AgentRouter
from .memory import MemoryManager
from .invoker import AgentInvoker
from .logger import ReasoningLogger
from .acp import ACPMessage


class AgentOrchestrator:
    """
    Main orchestrator interface for multi-agent systems.
    
    Provides a unified interface for external applications to interact with
    the agent orchestration system.
    """
    
    def __init__(
        self, 
        project_id: Optional[str] = None,
        collection_name: str = "agentor_memory",
        log_collection: str = "agentor_logs"
    ):
        """
        Initialize the agent orchestrator.
        
        Args:
            project_id: GCP project ID
            collection_name: Firestore collection name for memory
            log_collection: Firestore collection name for logs
        """
        self.project_id = project_id or os.getenv("GCP_PROJECT_ID")
        self._logger = logging.getLogger(__name__)
        
        # Initialize core components
        self.registry = AgentRegistry()
        self.memory = MemoryManager(self.project_id, collection_name)
        self.invoker = AgentInvoker(self.project_id)
        self.logger = ReasoningLogger(self.project_id, log_collection)
        self.router = AgentRouter(
            registry=self.registry,
            memory=self.memory,
            invoker=self.invoker,
            logger=self.logger
        )
        
        self._logger.info("AgentOrchestrator initialized successfully")
    
    def handle_message(self, acp_message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle an ACP message and return the response.
        
        Args:
            acp_message: ACP message dictionary
            
        Returns:
            Response dictionary with agent response and metadata
        """
        try:
            # Validate the message
            message = ACPMessage.from_dict(acp_message)
            if not message.is_valid():
                return {
                    "success": False,
                    "error": "Invalid ACP message format",
                    "response": "Please provide a valid message format."
                }
            
            # Route the message
            response = self.router.route(acp_message)
            
            # Store conversation in memory
            user_id = self._extract_user_id(message.from_id)
            self.memory.add_conversation_message(user_id, {
                "message": message.to_dict(),
                "response": response
            })
            
            return response
            
        except Exception as e:
            self._logger.error(f"Error handling message: {e}")
            return {
                "success": False,
                "error": f"Orchestrator error: {str(e)}",
                "response": "Sorry, I encountered an error processing your request."
            }
    
    def register_agent(
        self, 
        name: str, 
        agent: Any, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Register an agent with the orchestrator.
        
        Args:
            name: Agent name
            agent: Agent instance
            metadata: Optional metadata
        """
        self.registry.register(name, agent, metadata)
        self._logger.info(f"Registered agent: {name}")
    
    def unregister_agent(self, name: str) -> bool:
        """
        Unregister an agent.
        
        Args:
            name: Agent name
            
        Returns:
            True if unregistered, False if not found
        """
        success = self.registry.unregister(name)
        if success:
            self._logger.info(f"Unregistered agent: {name}")
        return success
    
    def get_agent_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a registered agent.
        
        Args:
            name: Agent name
            
        Returns:
            Agent information dictionary or None if not found
        """
        return self.registry.get_agent_info(name)
    
    def list_agents(self) -> Dict[str, Any]:
        """
        Get list of all registered agents.
        
        Returns:
            Dictionary with agent information
        """
        agents = {}
        for name in self.registry.list_all():
            info = self.registry.get_agent_info(name)
            if info:
                agents[name] = info
        return agents
    
    def get_user_context(self, user_id: str) -> Dict[str, Any]:
        """
        Get context for a specific user.
        
        Args:
            user_id: User identifier
            
        Returns:
            User context dictionary
        """
        session = self.memory.get_session(user_id)
        return session.get("context", {})
    
    def set_user_context(self, user_id: str, key: str, value: Any) -> None:
        """
        Set a context value for a user.
        
        Args:
            user_id: User identifier
            key: Context key
            value: Context value
        """
        self.memory.set_context(user_id, key, value)
    
    def get_conversation_history(self, user_id: str, limit: int = 10) -> list:
        """
        Get conversation history for a user.
        
        Args:
            user_id: User identifier
            limit: Maximum number of messages to return
            
        Returns:
            List of conversation messages
        """
        return self.memory.get_conversation_history(user_id, limit)
    
    def clear_user_context(self, user_id: str) -> None:
        """
        Clear all context for a user.
        
        Args:
            user_id: User identifier
        """
        self.memory.clear_context(user_id)
    
    def clear_conversation_history(self, user_id: str) -> None:
        """
        Clear conversation history for a user.
        
        Args:
            user_id: User identifier
        """
        self.memory.clear_conversation_history(user_id)
    
    def get_user_logs(self, user_id: str, limit: int = 100) -> list:
        """
        Get logs for a user.
        
        Args:
            user_id: User identifier
            limit: Maximum number of logs to return
            
        Returns:
            List of log entries
        """
        return self.logger.get_logs(user_id, limit)
    
    def get_routing_info(self) -> Dict[str, Any]:
        """
        Get routing configuration information.
        
        Returns:
            Dictionary with routing configuration
        """
        return self.router.get_routing_info()
    
    def add_intent_mapping(self, intent: str, agents: list) -> None:
        """
        Add or update intent to agent mapping.
        
        Args:
            intent: Intent name
            agents: List of agent names for this intent
        """
        self.router.add_intent_mapping(intent, agents)
    
    def add_tool_chain(self, name: str, steps: list) -> None:
        """
        Add a new tool chain definition.
        
        Args:
            name: Tool chain name
            steps: List of steps with agent and purpose
        """
        self.router.add_tool_chain(name, steps)
    
    def invoke_agent_directly(
        self, 
        agent_name: str, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Invoke an agent directly without routing.
        
        Args:
            agent_name: Agent name
            message: Input message
            context: Optional context
            
        Returns:
            Agent response
        """
        try:
            return self.invoker.invoke(agent_name, message, context or {})
        except Exception as e:
            self._logger.error(f"Error invoking agent {agent_name}: {e}")
            return f"Error: {str(e)}"
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get overall system status.
        
        Returns:
            Dictionary with system status information
        """
        return {
            "project_id": self.project_id,
            "registered_agents": len(self.registry),
            "active_agents": len(self.registry.list_active()),
            "memory_available": True,  # Would check Firestore connectivity
            "logging_available": True,  # Would check Firestore connectivity
            "routing_config": self.get_routing_info()
        }
    
    def _extract_user_id(self, from_id: str) -> str:
        """Extract user ID from from_id field."""
        if from_id.startswith("user:"):
            return from_id[5:]  # Remove "user:" prefix
        return from_id
    
    def create_user_message(
        self, 
        user_id: str, 
        intent: str, 
        message: str, 
        language: str = "en-US",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a user message for the orchestrator.
        
        Args:
            user_id: User identifier
            intent: The intent/action
            message: The message content
            language: Language code
            context: Additional context
            
        Returns:
            ACP message dictionary
        """
        from .acp import create_user_message
        acp_message = create_user_message(user_id, intent, message, language, context)
        return acp_message.to_dict()
    
    def handle_simple_message(
        self, 
        user_id: str, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle a simple text message (auto-detect intent).
        
        Args:
            user_id: User identifier
            message: Text message
            context: Optional context
            
        Returns:
            Response dictionary
        """
        # Create ACP message with auto-intent detection
        acp_message = {
            "from_id": f"user:{user_id}",
            "to_id": "agent:router",
            "intent": "",  # Will be auto-detected
            "message": message,
            "language": "en-US",
            "context": context or {}
        }
        
        return self.handle_message(acp_message) 