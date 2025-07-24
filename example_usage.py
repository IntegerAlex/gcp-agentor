#!/usr/bin/env python3
"""
Example usage of gcp-agentor library.

This script demonstrates how to use the multi-agent orchestration system
with the AgriAgent example for agricultural advisory.
"""

import json
from gcp_agentor import AgentOrchestrator
from gcp_agentor.examples.agri_agent import (
    CropAdvisorAgent,
    WeatherAgent,
    PestAssistantAgent,
    SoilAnalyzerAgent,
    MarketAgent,
    GeneralAssistantAgent
)


def setup_agri_system():
    """Set up the agricultural advisory system with all agents."""
    print("🚀 Setting up GCP Agentor - Agricultural Advisory System")
    print("=" * 60)
    
    # Initialize the orchestrator
    orchestrator = AgentOrchestrator()
    
    # Register all agricultural agents
    print("📝 Registering agents...")
    
    orchestrator.register_agent("crop_advisor", CropAdvisorAgent(), {
        "description": "Provides crop recommendations based on season and location",
        "capabilities": ["crop_advice", "seasonal_planning"],
        "intents": ["get_crop_advice", "crop_recommendations"]
    })
    
    orchestrator.register_agent("weather", WeatherAgent(), {
        "description": "Provides weather forecasts and alerts",
        "capabilities": ["weather_forecast", "weather_alerts"],
        "intents": ["get_weather", "weather_forecast"]
    })
    
    orchestrator.register_agent("pest_assistant", PestAssistantAgent(), {
        "description": "Provides pest control advice and treatment recommendations",
        "capabilities": ["pest_control", "disease_management"],
        "intents": ["pest_control", "disease_treatment"]
    })
    
    orchestrator.register_agent("soil_analyzer", SoilAnalyzerAgent(), {
        "description": "Provides soil analysis and fertilizer recommendations",
        "capabilities": ["soil_analysis", "fertilizer_advice"],
        "intents": ["soil_analysis", "fertilizer_recommendations"]
    })
    
    orchestrator.register_agent("market_agent", MarketAgent(), {
        "description": "Provides market prices and trading information",
        "capabilities": ["market_prices", "trading_advice"],
        "intents": ["market_prices", "price_information"]
    })
    
    orchestrator.register_agent("general_assistant", GeneralAssistantAgent(), {
        "description": "Provides general agricultural advice and tips",
        "capabilities": ["general_advice", "farming_tips"],
        "intents": ["general_help", "farming_basics"]
    })
    
    print(f"✅ Registered {len(orchestrator.list_agents())} agents")
    return orchestrator


def demonstrate_basic_usage(orchestrator):
    """Demonstrate basic usage of the orchestrator."""
    print("\n🎯 Basic Usage Examples")
    print("=" * 40)
    
    # Example 1: Simple message routing
    print("\n1. Simple message routing:")
    user_id = "farmer123"
    message = "What crop should I grow in monsoon season?"
    
    print(f"User: {user_id}")
    print(f"Message: {message}")
    
    response = orchestrator.handle_simple_message(user_id, message)
    print(f"Response: {response.get('response', 'No response')}")
    print(f"Agent: {response.get('agent', 'Unknown')}")
    
    # Example 2: Direct agent invocation
    print("\n2. Direct agent invocation:")
    weather_response = orchestrator.invoke_agent_directly(
        "weather", 
        "What's the weather like in Jalgaon?"
    )
    print(f"Weather Agent: {weather_response}")
    
    # Example 3: Context-aware interaction
    print("\n3. Context-aware interaction:")
    context = {
        "location": "Jalgaon",
        "soil_pH": 6.8,
        "season": "monsoon"
    }
    
    acp_message = orchestrator.create_user_message(
        user_id="farmer456",
        intent="get_crop_advice",
        message="I want to know what crops are best for my area",
        context=context
    )
    
    response = orchestrator.handle_message(acp_message)
    print(f"Context-aware response: {response.get('response', 'No response')}")


def demonstrate_advanced_features(orchestrator):
    """Demonstrate advanced features like tool chains and memory."""
    print("\n🔧 Advanced Features")
    print("=" * 40)
    
    # Example 1: Tool chain execution
    print("\n1. Tool chain execution:")
    
    # Add a tool chain for comprehensive advice
    orchestrator.add_tool_chain("comprehensive_advice", [
        {"agent": "weather", "purpose": "get_weather_data"},
        {"agent": "crop_advisor", "purpose": "get_crop_recommendations"},
        {"agent": "pest_assistant", "purpose": "get_pest_advice"}
    ])
    
    # Use tool chain
    context = {
        "tool_chain": "comprehensive_advice",
        "location": "Mumbai",
        "season": "monsoon"
    }
    
    acp_message = orchestrator.create_user_message(
        user_id="farmer789",
        intent="comprehensive_advice",
        message="Give me comprehensive farming advice for monsoon",
        context=context
    )
    
    response = orchestrator.handle_message(acp_message)
    print(f"Tool chain response: {response.get('response', 'No response')}")
    
    # Example 2: Memory and context persistence
    print("\n2. Memory and context persistence:")
    
    # Set user context
    orchestrator.set_user_context("farmer123", "last_crop", "rice")
    orchestrator.set_user_context("farmer123", "soil_type", "clay")
    orchestrator.set_user_context("farmer123", "irrigation", "drip")
    
    # Retrieve context
    context = orchestrator.get_user_context("farmer123")
    print(f"User context: {context}")
    
    # Example 3: Conversation history
    print("\n3. Conversation history:")
    
    # Send multiple messages
    messages = [
        "What's the weather today?",
        "What crop should I plant?",
        "How do I control pests?"
    ]
    
    for i, msg in enumerate(messages, 1):
        print(f"\nMessage {i}: {msg}")
        response = orchestrator.handle_simple_message("farmer123", msg)
        print(f"Response: {response.get('response', 'No response')[:100]}...")
    
    # Get conversation history
    history = orchestrator.get_conversation_history("farmer123", limit=5)
    print(f"\nConversation history: {len(history)} messages")


def demonstrate_system_management(orchestrator):
    """Demonstrate system management features."""
    print("\n⚙️ System Management")
    print("=" * 40)
    
    # Show system status
    print("\n1. System Status:")
    status = orchestrator.get_system_status()
    print(f"Registered Agents: {status['registered_agents']}")
    print(f"Active Agents: {status['active_agents']}")
    print(f"Project ID: {status.get('project_id', 'Not set')}")
    
    # Show routing configuration
    print("\n2. Routing Configuration:")
    routing_info = orchestrator.get_routing_info()
    print(f"Intent Mappings: {len(routing_info.get('intent_mapping', {}))}")
    print(f"Tool Chains: {len(routing_info.get('tool_chains', {}))}")
    
    # List all agents
    print("\n3. Registered Agents:")
    agents = orchestrator.list_agents()
    for name, info in agents.items():
        metadata = info["metadata"]
        print(f"  - {name}: {metadata.get('description', 'No description')}")
    
    # Show user logs
    print("\n4. User Activity Logs:")
    logs = orchestrator.get_user_logs("farmer123", limit=3)
    print(f"Recent logs: {len(logs)} entries")


def interactive_demo(orchestrator):
    """Run an interactive demo."""
    print("\n🎮 Interactive Demo")
    print("=" * 40)
    print("Type your questions (or 'quit' to exit):")
    print("Examples:")
    print("  - What crop should I grow in monsoon?")
    print("  - What's the weather in Mumbai?")
    print("  - How do I control pests in rice?")
    print("  - What are the market prices for wheat?")
    print("  - Give me soil analysis advice")
    print()
    
    user_id = "demo_user"
    
    while True:
        try:
            message = input(f"[{user_id}]> ").strip()
            
            if message.lower() in ['quit', 'exit', 'q']:
                break
            
            if not message:
                continue
            
            print("-" * 50)
            response = orchestrator.handle_simple_message(user_id, message)
            
            if response.get('success'):
                print(f"✅ {response.get('response', 'No response')}")
                print(f"🤖 Agent: {response.get('agent', 'Unknown')}")
                if response.get('execution_time'):
                    print(f"⏱️  Time: {response['execution_time']:.3f}s")
            else:
                print(f"❌ Error: {response.get('error', 'Unknown error')}")
            
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Main demonstration function."""
    try:
        # Set up the system
        orchestrator = setup_agri_system()
        
        # Demonstrate basic usage
        demonstrate_basic_usage(orchestrator)
        
        # Demonstrate advanced features
        demonstrate_advanced_features(orchestrator)
        
        # Demonstrate system management
        demonstrate_system_management(orchestrator)
        
        # Run interactive demo
        interactive_demo(orchestrator)
        
        print("\n🎉 Demo completed successfully!")
        print("\nTo use the CLI, run:")
        print("  python -m gcp_agentor.cli interactive")
        print("\nTo install the package:")
        print("  pip install -e .")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 