"""
Agent Communication Protocol (ACP) Module

Defines the standard message schema for agent communication.
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional
import json
from datetime import datetime


@dataclass
class ACPMessage:
    """
    Standardized message format for agent communication.
    
    Attributes:
        from_id: Sender identifier (e.g., "user:farmer123", "agent:crop_advisor")
        to_id: Recipient identifier (e.g., "agent:router", "agent:weather")
        intent: The intent/action to be performed
        message: The actual message content
        language: Language code (e.g., "en-US", "hi-IN")
        context: Additional context data
        timestamp: Message timestamp
        session_id: Session identifier for conversation tracking
    """
    from_id: str
    to_id: str
    intent: str
    message: str
    language: str = "en-US"
    context: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None
    session_id: Optional[str] = None
    
    def __post_init__(self):
        """Initialize default values after object creation."""
        if self.context is None:
            self.context = {}
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()
        if self.session_id is None:
            self.session_id = f"session_{int(datetime.utcnow().timestamp())}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the message to a dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert the message to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    def is_valid(self) -> bool:
        """Validate the message structure."""
        required_fields = ["from_id", "to_id", "intent", "message"]
        
        for field in required_fields:
            if not hasattr(self, field) or getattr(self, field) is None:
                return False
        
        # Validate language code format
        if not isinstance(self.language, str) or len(self.language) < 2:
            return False
        
        # Validate context is a dictionary
        if self.context is not None and not isinstance(self.context, dict):
            return False
        
        return True
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ACPMessage":
        """Create an ACPMessage from a dictionary."""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> "ACPMessage":
        """Create an ACPMessage from a JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def __str__(self) -> str:
        """String representation of the message."""
        return f"ACPMessage(from={self.from_id}, to={self.to_id}, intent={self.intent})"


def create_user_message(
    user_id: str,
    intent: str,
    message: str,
    language: str = "en-US",
    context: Optional[Dict[str, Any]] = None
) -> ACPMessage:
    """
    Create a user message for the router.
    
    Args:
        user_id: User identifier
        intent: The intent/action
        message: The message content
        language: Language code
        context: Additional context
    
    Returns:
        ACPMessage configured for user input
    """
    return ACPMessage(
        from_id=f"user:{user_id}",
        to_id="agent:router",
        intent=intent,
        message=message,
        language=language,
        context=context or {}
    )


def create_agent_message(
    from_agent: str,
    to_agent: str,
    intent: str,
    message: str,
    context: Optional[Dict[str, Any]] = None
) -> ACPMessage:
    """
    Create an agent-to-agent message.
    
    Args:
        from_agent: Source agent name
        to_agent: Target agent name
        intent: The intent/action
        message: The message content
        context: Additional context
    
    Returns:
        ACPMessage configured for agent communication
    """
    return ACPMessage(
        from_id=f"agent:{from_agent}",
        to_id=f"agent:{to_agent}",
        intent=intent,
        message=message,
        context=context or {}
    ) 