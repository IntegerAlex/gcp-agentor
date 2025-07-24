"""
Tests for AgentRegistry module.
"""

import pytest
from gcp_agentor.agent_registry import AgentRegistry, AgentMetadata
from gcp_agentor.examples.agri_agent import CropAdvisorAgent, WeatherAgent


class TestAgentRegistry:
    """Test cases for AgentRegistry."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.registry = AgentRegistry()
        self.crop_agent = CropAdvisorAgent()
        self.weather_agent = WeatherAgent()
    
    def test_register_agent(self):
        """Test agent registration."""
        self.registry.register("crop_advisor", self.crop_agent)
        assert "crop_advisor" in self.registry
        assert self.registry.get("crop_advisor") == self.crop_agent
    
    def test_register_agent_with_metadata(self):
        """Test agent registration with metadata."""
        metadata = {
            "description": "Crop advisory agent",
            "capabilities": ["crop_advice"],
            "intents": ["get_crop_advice"]
        }
        self.registry.register("crop_advisor", self.crop_agent, metadata)
        
        agent_info = self.registry.get_agent_info("crop_advisor")
        assert agent_info is not None
        assert agent_info["metadata"]["description"] == "Crop advisory agent"
        assert "crop_advice" in agent_info["metadata"]["capabilities"]
    
    def test_get_nonexistent_agent(self):
        """Test getting a non-existent agent."""
        assert self.registry.get("nonexistent") is None
    
    def test_list_all_agents(self):
        """Test listing all agents."""
        self.registry.register("crop_advisor", self.crop_agent)
        self.registry.register("weather", self.weather_agent)
        
        agents = self.registry.list_all()
        assert "crop_advisor" in agents
        assert "weather" in agents
        assert len(agents) == 2
    
    def test_list_active_agents(self):
        """Test listing active agents."""
        self.registry.register("crop_advisor", self.crop_agent)
        self.registry.register("weather", self.weather_agent)
        
        # Deactivate one agent
        self.registry.update_metadata("weather", {"is_active": False})
        
        active_agents = self.registry.list_active()
        assert "crop_advisor" in active_agents
        assert "weather" not in active_agents
        assert len(active_agents) == 1
    
    def test_list_by_capability(self):
        """Test listing agents by capability."""
        self.registry.register("crop_advisor", self.crop_agent, {
            "capabilities": ["crop_advice", "soil_analysis"]
        })
        self.registry.register("weather", self.weather_agent, {
            "capabilities": ["weather_forecast"]
        })
        
        crop_agents = self.registry.list_by_capability("crop_advice")
        assert "crop_advisor" in crop_agents
        assert "weather" not in crop_agents
    
    def test_list_by_intent(self):
        """Test listing agents by intent."""
        self.registry.register("crop_advisor", self.crop_agent, {
            "intents": ["get_crop_advice", "analyze_soil"]
        })
        self.registry.register("weather", self.weather_agent, {
            "intents": ["get_weather"]
        })
        
        crop_intent_agents = self.registry.list_by_intent("get_crop_advice")
        assert "crop_advisor" in crop_intent_agents
        assert "weather" not in crop_intent_agents
    
    def test_unregister_agent(self):
        """Test agent unregistration."""
        self.registry.register("crop_advisor", self.crop_agent)
        assert "crop_advisor" in self.registry
        
        success = self.registry.unregister("crop_advisor")
        assert success is True
        assert "crop_advisor" not in self.registry
    
    def test_unregister_nonexistent_agent(self):
        """Test unregistering a non-existent agent."""
        success = self.registry.unregister("nonexistent")
        assert success is False
    
    def test_update_metadata(self):
        """Test updating agent metadata."""
        self.registry.register("crop_advisor", self.crop_agent, {
            "description": "Old description"
        })
        
        success = self.registry.update_metadata("crop_advisor", {
            "description": "New description"
        })
        assert success is True
        
        agent_info = self.registry.get_agent_info("crop_advisor")
        assert agent_info["metadata"]["description"] == "New description"
    
    def test_update_nonexistent_agent_metadata(self):
        """Test updating metadata for non-existent agent."""
        success = self.registry.update_metadata("nonexistent", {
            "description": "New description"
        })
        assert success is False
    
    def test_clear_registry(self):
        """Test clearing all agents."""
        self.registry.register("crop_advisor", self.crop_agent)
        self.registry.register("weather", self.weather_agent)
        
        assert len(self.registry) == 2
        self.registry.clear()
        assert len(self.registry) == 0
    
    def test_registry_length(self):
        """Test registry length."""
        assert len(self.registry) == 0
        self.registry.register("crop_advisor", self.crop_agent)
        assert len(self.registry) == 1
    
    def test_contains_operator(self):
        """Test 'in' operator."""
        assert "crop_advisor" not in self.registry
        self.registry.register("crop_advisor", self.crop_agent)
        assert "crop_advisor" in self.registry


class TestAgentMetadata:
    """Test cases for AgentMetadata."""
    
    def test_agent_metadata_creation(self):
        """Test AgentMetadata creation."""
        metadata = AgentMetadata(
            name="test_agent",
            description="Test agent",
            capabilities=["test_capability"],
            intents=["test_intent"]
        )
        
        assert metadata.name == "test_agent"
        assert metadata.description == "Test agent"
        assert "test_capability" in metadata.capabilities
        assert "test_intent" in metadata.intents
        assert metadata.is_active is True
    
    def test_agent_metadata_defaults(self):
        """Test AgentMetadata default values."""
        metadata = AgentMetadata(name="test_agent")
        
        assert metadata.description == ""
        assert metadata.capabilities == []
        assert metadata.intents == []
        assert metadata.version == "1.0.0"
        assert metadata.is_active is True
        assert metadata.config == {} 