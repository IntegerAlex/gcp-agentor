"""
Agent Router Module

Routes ACP messages to appropriate agents based on intent and context.
"""

import time
import logging
from typing import Any, Dict, List, Optional, Tuple
from .agent_registry import AgentRegistry
from .memory import MemoryManager
from .invoker import AgentInvoker
from .logger import ReasoningLogger, ReasoningStep
from .acp import ACPMessage


class AgentRouter:
    """
    Routes ACP messages to appropriate agents based on intent and context.
    
    Provides intelligent routing with fallback support and tool chain capabilities.
    """
    
    def __init__(
        self, 
        registry: AgentRegistry, 
        memory: MemoryManager,
        invoker: Optional[AgentInvoker] = None,
        logger: Optional[ReasoningLogger] = None
    ):
        """
        Initialize the agent router.
        
        Args:
            registry: Agent registry instance
            memory: Memory manager instance
            invoker: Agent invoker instance (optional)
            logger: Reasoning logger instance (optional)
        """
        self.registry = registry
        self.memory = memory
        self.invoker = invoker or AgentInvoker()
        self.logger = logger or ReasoningLogger()
        self._logger = logging.getLogger(__name__)
        
        # Intent to agent mapping
        self._intent_mapping = {
            "get_crop_advice": ["crop_advisor"],
            "get_weather": ["weather"],
            "pest_control": ["pest_assistant"],
            "soil_analysis": ["soil_analyzer"],
            "market_prices": ["market_agent"],
            "general_help": ["general_assistant"]
        }
        
        # Tool chain definitions
        self._tool_chains = {
            "comprehensive_advice": [
                {"agent": "weather", "purpose": "get_weather_data"},
                {"agent": "crop_advisor", "purpose": "get_crop_recommendations"},
                {"agent": "pest_assistant", "purpose": "get_pest_advice"}
            ]
        }
    
    def route(self, acp_message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route an ACP message to the appropriate agent(s).
        
        Args:
            acp_message: ACP message dictionary
            
        Returns:
            Response dictionary with agent response and metadata
        """
        start_time = time.time()
        
        try:
            # Parse the ACP message
            message = ACPMessage.from_dict(acp_message)
            if not message.is_valid():
                return self._create_error_response("Invalid ACP message format")
            
            # Extract user ID from from_id
            user_id = self._extract_user_id(message.from_id)
            session_id = message.session_id
            
            # Log the incoming message
            self.logger.log(
                user_id, 
                "message_received", 
                {"message": message.to_dict()}, 
                session_id
            )
            
            # Analyze intent
            intent = self._analyze_intent(message)
            self.logger.log_intent_analysis(
                user_id, message.message, intent, 0.9, session_id=session_id
            )
            
            # Select appropriate agent(s)
            selected_agents = self._select_agents(intent, message.context or {})
            if not selected_agents:
                return self._create_error_response(f"No agent found for intent: {intent}")
            
            # Log agent selection
            self.logger.log_agent_selection(
                user_id, intent, selected_agents[0], 
                self.registry.list_active(), 
                "Intent-based routing", session_id or "default"
            )
            
            # Execute tool chain if needed
            if len(selected_agents) > 1:
                response = self._execute_tool_chain(selected_agents, message, user_id, session_id or "default")
            else:
                response = self._invoke_single_agent(selected_agents[0], message, user_id, session_id or "default")
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Log the response
            self.logger.log(
                user_id, 
                "response_sent", 
                {"response": response, "execution_time": execution_time}, 
                session_id
            )
            
            # Add response metadata
            response["execution_time"] = execution_time
            response["session_id"] = session_id
            response["user_id"] = user_id
            
            return response
            
        except Exception as e:
            self._logger.error(f"Error in routing: {e}")
            return self._create_error_response(f"Routing error: {str(e)}")
    
    def _extract_user_id(self, from_id: str) -> str:
        """Extract user ID from from_id field."""
        if from_id.startswith("user:"):
            return from_id[5:]  # Remove "user:" prefix
        return from_id
    
    def _analyze_intent(self, message: ACPMessage) -> str:
        """
        Analyze the intent from the message.
        
        Args:
            message: ACP message
            
        Returns:
            Detected intent
        """
        # Use explicit intent if provided
        if message.intent:
            return message.intent
        
        # Simple keyword-based intent detection
        message_lower = message.message.lower()
        
        if any(word in message_lower for word in ["crop", "plant", "grow", "harvest"]):
            return "get_crop_advice"
        elif any(word in message_lower for word in ["weather", "rain", "temperature", "climate"]):
            return "get_weather"
        elif any(word in message_lower for word in ["pest", "disease", "insect", "treatment"]):
            return "pest_control"
        elif any(word in message_lower for word in ["soil", "ph", "nutrient", "fertilizer"]):
            return "soil_analysis"
        elif any(word in message_lower for word in ["price", "market", "cost", "sell"]):
            return "market_prices"
        else:
            return "general_help"
    
    def _select_agents(self, intent: str, context: Dict[str, Any]) -> List[str]:
        """
        Select appropriate agents for the intent.
        
        Args:
            intent: Detected intent
            context: Message context
            
        Returns:
            List of selected agent names
        """
        # Check if this is a tool chain request
        if context.get("tool_chain"):
            chain_name = context.get("tool_chain")
            if chain_name in self._tool_chains:
                return [step["agent"] for step in self._tool_chains[chain_name]]
        
        # Direct intent mapping
        if intent in self._intent_mapping:
            agents = self._intent_mapping[intent]
            # Filter to only active agents
            available_agents = [agent for agent in agents if self.registry.is_registered(agent)]
            return available_agents
        
        # Fallback: find agents by intent capability
        agents_by_intent = self.registry.list_by_intent(intent)
        if agents_by_intent:
            return agents_by_intent
        
        # Final fallback: general assistant
        if self.registry.is_registered("general_assistant"):
            return ["general_assistant"]
        
        return []
    
    def _invoke_single_agent(
        self, 
        agent_name: str, 
        message: ACPMessage, 
        user_id: str, 
        session_id: str
    ) -> Dict[str, Any]:
        """
        Invoke a single agent.
        
        Args:
            agent_name: Agent name
            message: ACP message
            user_id: User identifier
            session_id: Session identifier
            
        Returns:
            Response dictionary
        """
        start_time = time.time()
        
        try:
            # Get agent from registry
            agent = self.registry.get(agent_name)
            if not agent:
                return self._create_error_response(f"Agent {agent_name} not found")
            
            # Prepare context
            context = self._prepare_context(user_id, message.context or {})
            
            # Invoke agent
            if hasattr(agent, 'invoke'):
                response = agent.invoke(message.message, context)
            else:
                # Use invoker for external agents
                response = self.invoker.invoke(agent_name, message.message, context)
            
            execution_time = time.time() - start_time
            
            # Log the invocation
            self.logger.log_agent_invocation(
                user_id, agent_name, message.message, context, 
                response, execution_time, session_id
            )
            
            return {
                "success": True,
                "agent": agent_name,
                "response": response,
                "context": context
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.log_error(
                user_id, "agent_invocation_error", str(e), 
                context={"agent": agent_name}, session_id=session_id
            )
            return self._create_error_response(f"Agent {agent_name} failed: {str(e)}")
    
    def _execute_tool_chain(
        self, 
        agents: List[str], 
        message: ACPMessage, 
        user_id: str, 
        session_id: str
    ) -> Dict[str, Any]:
        """
        Execute a tool chain of multiple agents.
        
        Args:
            agents: List of agent names
            message: ACP message
            user_id: User identifier
            session_id: Session identifier
            
        Returns:
            Combined response dictionary
        """
        chain_results = []
        context = self._prepare_context(user_id, message.context or {})
        
        for i, agent_name in enumerate(agents):
            try:
                # Update context with previous results
                if chain_results:
                    context["previous_results"] = chain_results
                
                # Invoke agent
                if self.registry.is_registered(agent_name):
                    agent = self.registry.get(agent_name)
                    if agent and hasattr(agent, 'invoke'):
                        result = agent.invoke(message.message, context)
                    else:
                        result = self.invoker.invoke(agent_name, message.message, context)
                else:
                    result = self.invoker.invoke(agent_name, message.message, context)
                
                chain_results.append({
                    "agent": agent_name,
                    "step": i + 1,
                    "result": result
                })
                
                # Log each step
                self.logger.log(
                    user_id, 
                    "tool_chain_step", 
                    {"agent": agent_name, "step": i + 1, "result": result}, 
                    session_id
                )
                
            except Exception as e:
                self.logger.log_error(
                    user_id, "tool_chain_error", str(e), 
                    stack_trace=None,
                    context={"agent": agent_name, "step": i + 1}, 
                    session_id=session_id
                )
                chain_results.append({
                    "agent": agent_name,
                    "step": i + 1,
                    "error": str(e)
                })
        
        # Combine results
        combined_response = self._combine_tool_chain_results(chain_results)
        
        return {
            "success": True,
            "tool_chain": True,
            "agents": agents,
            "response": combined_response,
            "step_results": chain_results,
            "context": context
        }
    
    def _combine_tool_chain_results(self, results: List[Dict[str, Any]]) -> str:
        """
        Combine results from a tool chain into a single response.
        
        Args:
            results: List of step results
            
        Returns:
            Combined response string
        """
        if not results:
            return "No results from tool chain"
        
        combined = []
        for result in results:
            agent = result.get("agent", "unknown")
            if "error" in result:
                combined.append(f"❌ {agent}: {result['error']}")
            else:
                combined.append(f"✅ {agent}: {result.get('result', 'No response')}")
        
        return "\n\n".join(combined)
    
    def _prepare_context(self, user_id: str, message_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare context for agent invocation.
        
        Args:
            user_id: User identifier
            message_context: Context from message
            
        Returns:
            Combined context dictionary
        """
        # Get user's stored context
        user_context = {}
        session = self.memory.get_session(user_id)
        if session and "context" in session:
            user_context = session["context"]
        
        # Combine with message context
        combined_context = {**user_context, **message_context}
        
        # Add metadata
        combined_context["user_id"] = user_id
        combined_context["timestamp"] = time.time()
        
        return combined_context
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """
        Create a standardized error response.
        
        Args:
            error_message: Error message
            
        Returns:
            Error response dictionary
        """
        return {
            "success": False,
            "error": error_message,
            "response": f"Sorry, I encountered an error: {error_message}",
            "agent": None
        }
    
    def add_intent_mapping(self, intent: str, agents: List[str]) -> None:
        """
        Add or update intent to agent mapping.
        
        Args:
            intent: Intent name
            agents: List of agent names for this intent
        """
        self._intent_mapping[intent] = agents
        self._logger.info(f"Added intent mapping: {intent} -> {agents}")
    
    def add_tool_chain(self, name: str, steps: List[Dict[str, str]]) -> None:
        """
        Add a new tool chain definition.
        
        Args:
            name: Tool chain name
            steps: List of steps with agent and purpose
        """
        self._tool_chains[name] = steps
        self._logger.info(f"Added tool chain: {name} with {len(steps)} steps")
    
    def get_routing_info(self) -> Dict[str, Any]:
        """
        Get routing configuration information.
        
        Returns:
            Dictionary with routing configuration
        """
        return {
            "intent_mapping": self._intent_mapping,
            "tool_chains": self._tool_chains,
            "registered_agents": self.registry.list_all(),
            "active_agents": self.registry.list_active()
        } 