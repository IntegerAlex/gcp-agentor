"""
Agent Registry Module

Manages registered agents and their metadata for dynamic discovery and routing.
"""

from typing import Any, Dict, List, Optional, Callable
import logging
from dataclasses import dataclass, asdict


@dataclass
class AgentMetadata:
    """Metadata for a registered agent."""
    name: str
    description: str = ""
    capabilities: Optional[List[str]] = None
    intents: Optional[List[str]] = None
    version: str = "1.0.0"
    is_active: bool = True
    config: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.capabilities is None:
            self.capabilities = []
        if self.intents is None:
            self.intents = []
        if self.config is None:
            self.config = {}


class AgentRegistry:
    """
    Registry for managing agents and their metadata.
    
    Provides methods to register, retrieve, and manage agents dynamically.
    """
    
    def __init__(self):
        """Initialize the agent registry."""
        self._agents: Dict[str, Any] = {}
        self._metadata: Dict[str, AgentMetadata] = {}
        self._logger = logging.getLogger(__name__)
    
    def register(
        self, 
        name: str, 
        agent: Any, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Register an agent with the registry.
        
        Args:
            name: Unique name for the agent
            agent: The agent instance or callable
            metadata: Optional metadata dictionary
        """
        if name in self._agents:
            self._logger.warning(f"Agent '{name}' already registered. Overwriting.")
        
        self._agents[name] = agent
        
        # Create metadata
        agent_metadata = AgentMetadata(
            name=name,
            **(metadata or {})
        )
        self._metadata[name] = agent_metadata
        
        self._logger.info(f"Registered agent '{name}' with capabilities: {agent_metadata.capabilities}")
    
    def get(self, name: str) -> Optional[Any]:
        """
        Get an agent by name.
        
        Args:
            name: Agent name
            
        Returns:
            The agent instance or None if not found
        """
        return self._agents.get(name)
    
    def get_metadata(self, name: str) -> Optional[AgentMetadata]:
        """
        Get agent metadata by name.
        
        Args:
            name: Agent name
            
        Returns:
            AgentMetadata or None if not found
        """
        return self._metadata.get(name)
    
    def list_all(self) -> List[str]:
        """
        Get list of all registered agent names.
        
        Returns:
            List of agent names
        """
        return list(self._agents.keys())
    
    def list_active(self) -> List[str]:
        """
        Get list of active agent names.
        
        Returns:
            List of active agent names
        """
        return [
            name for name, metadata in self._metadata.items()
            if metadata.is_active
        ]
    
    def list_by_capability(self, capability: str) -> List[str]:
        """
        Get agents that have a specific capability.
        
        Args:
            capability: The capability to search for
            
        Returns:
            List of agent names with the capability
        """
        return [
            name for name, metadata in self._metadata.items()
            if metadata.capabilities and capability in metadata.capabilities and metadata.is_active
        ]
    
    def list_by_intent(self, intent: str) -> List[str]:
        """
        Get agents that can handle a specific intent.
        
        Args:
            intent: The intent to search for
            
        Returns:
            List of agent names that can handle the intent
        """
        return [
            name for name, metadata in self._metadata.items()
            if metadata.intents and intent in metadata.intents and metadata.is_active
        ]
    
    def unregister(self, name: str) -> bool:
        """
        Unregister an agent.
        
        Args:
            name: Agent name to unregister
            
        Returns:
            True if agent was unregistered, False if not found
        """
        if name in self._agents:
            del self._agents[name]
            del self._metadata[name]
            self._logger.info(f"Unregistered agent '{name}'")
            return True
        return False
    
    def update_metadata(self, name: str, metadata: Dict[str, Any]) -> bool:
        """
        Update agent metadata.
        
        Args:
            name: Agent name
            metadata: New metadata dictionary
            
        Returns:
            True if updated, False if agent not found
        """
        if name not in self._metadata:
            return False
        
        current_metadata = self._metadata[name]
        for key, value in metadata.items():
            if hasattr(current_metadata, key):
                setattr(current_metadata, key, value)
        
        self._logger.info(f"Updated metadata for agent '{name}'")
        return True
    
    def is_registered(self, name: str) -> bool:
        """
        Check if an agent is registered.
        
        Args:
            name: Agent name
            
        Returns:
            True if registered, False otherwise
        """
        return name in self._agents
    
    def get_agent_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get complete agent information including metadata.
        
        Args:
            name: Agent name
            
        Returns:
            Dictionary with agent and metadata info, or None if not found
        """
        if name not in self._agents:
            return None
        
        return {
            "name": name,
            "agent": self._agents[name],
            "metadata": asdict(self._metadata[name])
        }
    
    def clear(self) -> None:
        """Clear all registered agents."""
        self._agents.clear()
        self._metadata.clear()
        self._logger.info("Cleared all registered agents")
    
    def __len__(self) -> int:
        """Return the number of registered agents."""
        return len(self._agents)
    
    def __contains__(self, name: str) -> bool:
        """Check if an agent is registered."""
        return name in self._agents 