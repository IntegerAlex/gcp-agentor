"""
GCP-Based Multi-Agent Orchestration Library

A Python library that provides intelligent multi-agent orchestration for Google Cloud Platform.
Routes user messages to appropriate agents, manages shared memory via Firestore, and supports
agent-to-agent communication using a defined ACP (Agent Communication Protocol).
"""

from .core import AgentOrchestrator
from .agent_registry import AgentRegistry
from .router import AgentRouter
from .memory import MemoryManager
from .acp import ACPMessage
from .invoker import AgentInvoker
from .logger import ReasoningLogger

__version__ = "0.1.0"
__author__ = "GCP Agentor Team"

__all__ = [
    "AgentOrchestrator",
    "AgentRegistry", 
    "AgentRouter",
    "MemoryManager",
    "ACPMessage",
    "AgentInvoker",
    "ReasoningLogger",
] 