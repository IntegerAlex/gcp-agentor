# 🚀 gcp-agentor

**GCP-Based Multi-Agent Orchestration Library**

A Python library that provides intelligent multi-agent orchestration for Google Cloud Platform. Routes user messages to appropriate agents, manages shared memory via Firestore, and supports agent-to-agent communication using a defined ACP (Agent Communication Protocol).

## ✨ Features

- 🤖 **Multi-Agent Routing**: Intelligent message routing based on intent and context
- 🧠 **Shared Memory**: Persistent memory management using Firestore
- 📡 **ACP Protocol**: Standardized Agent Communication Protocol
- 🔄 **Agent Registry**: Dynamic agent registration and discovery
- 📊 **Reasoning Logs**: Comprehensive logging of agent decisions and reasoning
- ☁️ **GCP Integration**: Native support for Vertex AI Agent Builder and ADK
- 🔧 **Extensible**: Easy to add new agents and capabilities

## 🚀 Quick Start

### Installation

```bash
pip install gcp-agentor
```

### Basic Usage

```python
from gcp_agentor import AgentOrchestrator
from gcp_agentor.acp import ACPMessage

# Initialize the orchestrator
orchestrator = AgentOrchestrator()

# Create an ACP message
message = ACPMessage({
    "from": "user:farmer123",
    "to": "agent:router",
    "intent": "get_crop_advice",
    "message": "What crop should I grow in July?",
    "language": "en-US",
    "context": {
        "location": "Jalgaon",
        "soil_pH": 6.5
    }
})

# Handle the message
response = orchestrator.handle_message(message.to_dict())
print(response)
```

## 📦 Core Components

### 1. Agent Registry (`agent_registry.py`)
Manages registered agents and their metadata.

```python
from gcp_agentor import AgentRegistry

registry = AgentRegistry()
registry.register("crop_advisor", CropAdvisorAgent(), {"capabilities": ["crop_advice"]})
```

### 2. Router (`router.py`)
Routes ACP messages to appropriate agents based on intent.

```python
from gcp_agentor import AgentRouter

router = AgentRouter(registry, memory_manager)
response = router.route(acp_message)
```

### 3. Memory Manager (`memory.py`)
Shared memory layer using Firestore.

```python
from gcp_agentor import MemoryManager

memory = MemoryManager()
memory.set_context("user123", "last_crop", "wheat")
context = memory.get_context("user123", "last_crop")
```

### 4. ACP Protocol (`acp.py`)
Standardized message schema for agent communication.

```python
from gcp_agentor.acp import ACPMessage

message = ACPMessage({
    "from": "user:farmer123",
    "to": "agent:router",
    "intent": "get_crop_advice",
    "message": "What crop to grow?",
    "context": {"location": "Jalgaon"}
})
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Input    │───▶│   Agent Router  │───▶│  Agent Registry │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   ACP Message   │    │  Memory Manager │    │ Agent Invoker   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Reasoning Logger│    │   Firestore     │    │ Vertex AI/ADK   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔧 Configuration

### Environment Variables

```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
export GCP_PROJECT_ID="your-project-id"
export FIRESTORE_COLLECTION="agentor_memory"
```

### GCP Setup

1. **Enable APIs**:
   - Cloud Firestore API
   - Vertex AI API
   - Cloud Pub/Sub API (optional)

2. **Service Account**:
   - Create a service account with appropriate permissions
   - Download the JSON key file
   - Set `GOOGLE_APPLICATION_CREDENTIALS`

## 📚 Examples

### AgriAgent Example

```python
from gcp_agentor.examples.agri_agent import (
    CropAdvisorAgent, 
    WeatherAgent, 
    PestAssistantAgent
)

# Register agents
registry = AgentRegistry()
registry.register("crop_advisor", CropAdvisorAgent())
registry.register("weather", WeatherAgent())
registry.register("pest_assistant", PestAssistantAgent())

# Use the orchestrator
orchestrator = AgentOrchestrator()
response = orchestrator.handle_message({
    "from": "user:farmer123",
    "intent": "get_crop_advice",
    "message": "What should I plant this season?",
    "context": {"location": "Jalgaon", "season": "monsoon"}
})
```

## 🧪 Testing

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run with coverage
pytest --cov=gcp_agentor tests/
```

## 📖 API Reference

### AgentOrchestrator

Main orchestrator class that coordinates all components.

```python
class AgentOrchestrator:
    def __init__(self, project_id: str = None, collection_name: str = "agentor_memory")
    def handle_message(self, acp_message: dict) -> dict
    def register_agent(self, name: str, agent: Any, metadata: dict = {}) -> None
```

### ACPMessage

Standardized message format for agent communication.

```python
class ACPMessage:
    def __init__(self, data: dict)
    def to_dict(self) -> dict
    def is_valid(self) -> bool
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- 📧 Email: support@gcp-agentor.com
- 🐛 Issues: [GitHub Issues](https://github.com/your-org/gcp-agentor/issues)
- 📖 Docs: [Documentation](https://gcp-agentor.readthedocs.io)

---

**Built with ❤️ for the GCP community** 