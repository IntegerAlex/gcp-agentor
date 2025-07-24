"""
Agent Invoker Module

Handles agent invocation for both local ADK agents and remote Vertex AI agents.
"""

import os
import logging
from typing import Any, Dict, Optional, Union, Callable
from abc import ABC, abstractmethod

try:
    from google.cloud import aiplatform
    from google.cloud.aiplatform_v1.types import PredictRequest, PredictResponse
    VERTEX_AI_AVAILABLE = True
except ImportError:
    VERTEX_AI_AVAILABLE = False
    aiplatform = None


class BaseAgent(ABC):
    """Abstract base class for all agents."""
    
    @abstractmethod
    def invoke(self, message: str, context: Dict[str, Any] = None) -> str:
        """
        Invoke the agent with a message and context.
        
        Args:
            message: Input message
            context: Additional context data
            
        Returns:
            Agent response
        """
        pass


class AgentInvoker:
    """
    Handles agent invocation for different types of agents.
    
    Supports both local ADK agents and remote Vertex AI agents.
    """
    
    def __init__(self, project_id: Optional[str] = None, location: str = "us-central1"):
        """
        Initialize the agent invoker.
        
        Args:
            project_id: GCP project ID
            location: GCP location for Vertex AI resources
        """
        self.project_id = project_id or os.getenv("GCP_PROJECT_ID")
        self.location = location
        self._logger = logging.getLogger(__name__)
        
        if VERTEX_AI_AVAILABLE and self.project_id:
            try:
                aiplatform.init(project=self.project_id, location=self.location)
                self._logger.info(f"Initialized Vertex AI client for project: {self.project_id}")
            except Exception as e:
                self._logger.warning(f"Failed to initialize Vertex AI: {e}")
    
    def invoke(
        self, 
        agent_name: str, 
        message: str, 
        context: Dict[str, Any] = None,
        agent_type: str = "local"
    ) -> str:
        """
        Invoke an agent with a message.
        
        Args:
            agent_name: Name or identifier of the agent
            message: Input message
            context: Additional context data
            agent_type: Type of agent ("local" or "vertex")
            
        Returns:
            Agent response
        """
        context = context or {}
        
        try:
            if agent_type == "vertex":
                return self._invoke_vertex_agent(agent_name, message, context)
            else:
                return self._invoke_local_agent(agent_name, message, context)
        except Exception as e:
            self._logger.error(f"Error invoking agent {agent_name}: {e}")
            return f"Error: Failed to invoke agent {agent_name}. {str(e)}"
    
    def _invoke_local_agent(self, agent_name: str, message: str, context: Dict[str, Any]) -> str:
        """
        Invoke a local ADK agent.
        
        Args:
            agent_name: Agent name
            message: Input message
            context: Context data
            
        Returns:
            Agent response
        """
        # This would typically involve calling the ADK agent runtime
        # For now, we'll return a placeholder response
        self._logger.info(f"Invoking local agent: {agent_name}")
        
        # Mock response for demonstration
        return f"Local agent '{agent_name}' response: {message}"
    
    def _invoke_vertex_agent(self, agent_name: str, message: str, context: Dict[str, Any]) -> str:
        """
        Invoke a Vertex AI agent.
        
        Args:
            agent_name: Vertex AI agent resource name or ID
            message: Input message
            context: Context data
            
        Returns:
            Agent response
        """
        if not VERTEX_AI_AVAILABLE:
            raise RuntimeError("Vertex AI SDK not available")
        
        try:
            # Construct the full resource name if only ID is provided
            if not agent_name.startswith("projects/"):
                agent_name = f"projects/{self.project_id}/locations/{self.location}/agents/{agent_name}"
            
            self._logger.info(f"Invoking Vertex AI agent: {agent_name}")
            
            # Create the endpoint client
            endpoint_client = aiplatform.Endpoint(
                endpoint_name=agent_name
            )
            
            # Prepare the request payload
            payload = {
                "message": message,
                "context": context
            }
            
            # Make the prediction request
            response = endpoint_client.predict([payload])
            
            # Extract the response
            if response and hasattr(response, 'predictions'):
                return str(response.predictions[0])
            else:
                return "No response from Vertex AI agent"
                
        except Exception as e:
            self._logger.error(f"Error invoking Vertex AI agent {agent_name}: {e}")
            raise
    
    def invoke_with_fallback(
        self, 
        agent_name: str, 
        message: str, 
        context: Dict[str, Any] = None,
        fallback_agent: Optional[str] = None
    ) -> str:
        """
        Invoke an agent with fallback support.
        
        Args:
            agent_name: Primary agent name
            message: Input message
            context: Context data
            fallback_agent: Fallback agent name
            
        Returns:
            Agent response or fallback response
        """
        try:
            return self.invoke(agent_name, message, context)
        except Exception as e:
            self._logger.warning(f"Primary agent {agent_name} failed: {e}")
            
            if fallback_agent:
                try:
                    self._logger.info(f"Trying fallback agent: {fallback_agent}")
                    return self.invoke(fallback_agent, message, context)
                except Exception as fallback_error:
                    self._logger.error(f"Fallback agent {fallback_agent} also failed: {fallback_error}")
            
            return f"Error: All agents failed. Original error: {str(e)}"
    
    def batch_invoke(
        self, 
        agents: list, 
        message: str, 
        context: Dict[str, Any] = None
    ) -> Dict[str, str]:
        """
        Invoke multiple agents with the same message.
        
        Args:
            agents: List of agent configurations (dict with 'name' and 'type')
            message: Input message
            context: Context data
            
        Returns:
            Dictionary mapping agent names to responses
        """
        results = {}
        context = context or {}
        
        for agent_config in agents:
            agent_name = agent_config.get('name')
            agent_type = agent_config.get('type', 'local')
            
            if not agent_name:
                continue
            
            try:
                response = self.invoke(agent_name, message, context, agent_type)
                results[agent_name] = response
            except Exception as e:
                results[agent_name] = f"Error: {str(e)}"
        
        return results
    
    def get_agent_status(self, agent_name: str, agent_type: str = "local") -> Dict[str, Any]:
        """
        Get the status of an agent.
        
        Args:
            agent_name: Agent name
            agent_type: Type of agent
            
        Returns:
            Dictionary with agent status information
        """
        status = {
            "name": agent_name,
            "type": agent_type,
            "available": False,
            "error": None
        }
        
        try:
            if agent_type == "vertex":
                if not VERTEX_AI_AVAILABLE:
                    status["error"] = "Vertex AI SDK not available"
                    return status
                
                # Check if Vertex AI agent exists
                if not agent_name.startswith("projects/"):
                    agent_name = f"projects/{self.project_id}/locations/{self.location}/agents/{agent_name}"
                
                # This would typically check the agent's deployment status
                status["available"] = True
                status["endpoint"] = agent_name
                
            else:
                # For local agents, we assume they're available if we can reach this point
                status["available"] = True
                
        except Exception as e:
            status["error"] = str(e)
        
        return status
    
    def list_available_agents(self) -> Dict[str, Dict[str, Any]]:
        """
        List all available agents.
        
        Returns:
            Dictionary mapping agent names to their status
        """
        # This would typically query the registry or Vertex AI
        # For now, return an empty dict
        return {}


class MockAgent(BaseAgent):
    """Mock agent for testing purposes."""
    
    def __init__(self, name: str, response_template: str = "Mock response from {name}: {message}"):
        """
        Initialize the mock agent.
        
        Args:
            name: Agent name
            response_template: Response template string
        """
        self.name = name
        self.response_template = response_template
    
    def invoke(self, message: str, context: Dict[str, Any] = None) -> str:
        """
        Return a mock response.
        
        Args:
            message: Input message
            context: Context data (ignored for mock)
            
        Returns:
            Mock response
        """
        return self.response_template.format(name=self.name, message=message) 