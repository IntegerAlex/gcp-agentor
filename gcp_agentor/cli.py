"""
CLI module for gcp-agentor.

Provides command-line interface for managing agents and testing the system.
"""

import argparse
import json
import sys
from typing import Dict, Any
from .core import AgentOrchestrator
from .examples.agri_agent import (
    CropAdvisorAgent, 
    WeatherAgent, 
    PestAssistantAgent,
    SoilAnalyzerAgent,
    MarketAgent,
    GeneralAssistantAgent
)


def setup_agents(orchestrator: AgentOrchestrator) -> None:
    """Set up sample agents for testing."""
    # Register sample agents
    orchestrator.register_agent("crop_advisor", CropAdvisorAgent(), {
        "description": "Provides crop recommendations",
        "capabilities": ["crop_advice"],
        "intents": ["get_crop_advice"]
    })
    
    orchestrator.register_agent("weather", WeatherAgent(), {
        "description": "Provides weather information",
        "capabilities": ["weather_forecast"],
        "intents": ["get_weather"]
    })
    
    orchestrator.register_agent("pest_assistant", PestAssistantAgent(), {
        "description": "Provides pest control advice",
        "capabilities": ["pest_control"],
        "intents": ["pest_control"]
    })
    
    orchestrator.register_agent("soil_analyzer", SoilAnalyzerAgent(), {
        "description": "Provides soil analysis",
        "capabilities": ["soil_analysis"],
        "intents": ["soil_analysis"]
    })
    
    orchestrator.register_agent("market_agent", MarketAgent(), {
        "description": "Provides market information",
        "capabilities": ["market_prices"],
        "intents": ["market_prices"]
    })
    
    orchestrator.register_agent("general_assistant", GeneralAssistantAgent(), {
        "description": "Provides general agricultural advice",
        "capabilities": ["general_advice"],
        "intents": ["general_help"]
    })


def list_agents(orchestrator: AgentOrchestrator) -> None:
    """List all registered agents."""
    agents = orchestrator.list_agents()
    
    if not agents:
        print("No agents registered.")
        return
    
    print("Registered Agents:")
    print("=" * 50)
    
    for name, info in agents.items():
        metadata = info["metadata"]
        print(f"Name: {name}")
        print(f"Description: {metadata.get('description', 'No description')}")
        print(f"Capabilities: {', '.join(metadata.get('capabilities', []))}")
        print(f"Intents: {', '.join(metadata.get('intents', []))}")
        print(f"Active: {metadata.get('is_active', True)}")
        print("-" * 30)


def test_agent(orchestrator: AgentOrchestrator, agent_name: str, message: str) -> None:
    """Test a specific agent."""
    print(f"Testing agent: {agent_name}")
    print(f"Message: {message}")
    print("-" * 40)
    
    try:
        response = orchestrator.invoke_agent_directly(agent_name, message)
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")


def test_routing(orchestrator: AgentOrchestrator, user_id: str, message: str) -> None:
    """Test message routing."""
    print(f"Testing message routing")
    print(f"User: {user_id}")
    print(f"Message: {message}")
    print("-" * 40)
    
    try:
        response = orchestrator.handle_simple_message(user_id, message)
        print(f"Success: {response.get('success', False)}")
        print(f"Agent: {response.get('agent', 'Unknown')}")
        print(f"Response: {response.get('response', 'No response')}")
        if response.get('execution_time'):
            print(f"Execution time: {response['execution_time']:.3f}s")
    except Exception as e:
        print(f"Error: {e}")


def show_status(orchestrator: AgentOrchestrator) -> None:
    """Show system status."""
    status = orchestrator.get_system_status()
    
    print("System Status:")
    print("=" * 30)
    print(f"Project ID: {status.get('project_id', 'Not set')}")
    print(f"Registered Agents: {status['registered_agents']}")
    print(f"Active Agents: {status['active_agents']}")
    print(f"Memory Available: {status['memory_available']}")
    print(f"Logging Available: {status['logging_available']}")
    
    routing_info = status.get('routing_config', {})
    print(f"\nRouting Configuration:")
    print(f"Intent Mappings: {len(routing_info.get('intent_mapping', {}))}")
    print(f"Tool Chains: {len(routing_info.get('tool_chains', {}))}")


def interactive_mode(orchestrator: AgentOrchestrator) -> None:
    """Run interactive mode for testing."""
    print("Interactive Mode - Type 'quit' to exit")
    print("=" * 40)
    
    user_id = "test_user"
    
    while True:
        try:
            message = input(f"[{user_id}]> ").strip()
            
            if message.lower() in ['quit', 'exit', 'q']:
                break
            
            if not message:
                continue
            
            print("-" * 40)
            response = orchestrator.handle_simple_message(user_id, message)
            
            if response.get('success'):
                print(f"✅ {response.get('response', 'No response')}")
            else:
                print(f"❌ Error: {response.get('error', 'Unknown error')}")
            
            print("-" * 40)
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="GCP Agentor - Multi-Agent Orchestration System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  gcp-agentor list                    # List all agents
  gcp-agentor status                  # Show system status
  gcp-agentor test crop_advisor "What crop to grow?"  # Test specific agent
  gcp-agentor route "farmer123" "What crop to grow in monsoon?"  # Test routing
  gcp-agentor interactive             # Run interactive mode
        """
    )
    
    parser.add_argument(
        'command',
        choices=['list', 'status', 'test', 'route', 'interactive'],
        help='Command to execute'
    )
    
    parser.add_argument(
        '--agent', '-a',
        help='Agent name (for test command)'
    )
    
    parser.add_argument(
        '--user', '-u',
        default='test_user',
        help='User ID (for route command)'
    )
    
    parser.add_argument(
        '--message', '-m',
        help='Message to send'
    )
    
    parser.add_argument(
        '--project-id',
        help='GCP Project ID'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize orchestrator
        orchestrator = AgentOrchestrator(project_id=args.project_id)
        
        # Set up sample agents
        setup_agents(orchestrator)
        
        # Execute command
        if args.command == 'list':
            list_agents(orchestrator)
        
        elif args.command == 'status':
            show_status(orchestrator)
        
        elif args.command == 'test':
            if not args.agent:
                print("Error: --agent is required for test command")
                sys.exit(1)
            if not args.message:
                print("Error: --message is required for test command")
                sys.exit(1)
            test_agent(orchestrator, args.agent, args.message)
        
        elif args.command == 'route':
            if not args.message:
                print("Error: --message is required for route command")
                sys.exit(1)
            test_routing(orchestrator, args.user, args.message)
        
        elif args.command == 'interactive':
            interactive_mode(orchestrator)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 