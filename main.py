#!/usr/bin/env python3
"""
AI-Agent Testing Utility - Main Entry Point

Command-line utility to test AI-Agent by simulating its interaction with human.
"""

import argparse
import sys
import json
from datetime import datetime
from typing import Optional

from conversation_runner import run_simulation, run_all_simulations
from ollama_integration import OllamaClient, LLMEnhancedBankingAgent
from human_simulation.simulation_logic import SimulationFactory


def print_banner():
    """Print application banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║         AI-AGENT TESTING UTILITY - BANKING AGENT         ║
    ║         Human Simulation Testing Framework               ║
    ╚══════════════════════════════════════════════════════════╝
    """
    print(banner)


def check_ollama_status():
    """Check Ollama status and model availability."""
    print("Checking Ollama status...")
    client = OllamaClient()
    
    if client.check_model_available():
        print(f"✓ Ollama is running with model '{client.model}' available.")
        return True
    else:
        print(f"✗ Model '{client.model}' is not available.")
        print("  You can pull it with: ollama pull minimax-m2.5:cloud")
        print("  Or use the rule-based agent without LLM.")
        return False


def list_simulations():
    """List all available simulations."""
    simulations = SimulationFactory.get_available_simulations()
    
    print("\nAvailable Human Simulations:")
    print("="*60)
    
    for i, sim_name in enumerate(simulations, 1):
        desc = SimulationFactory.get_simulation_description(sim_name)
        print(f"{i}. {sim_name:20} - {desc}")
    
    print("\nUsage: python main.py --simulation <name>")
    return simulations


def run_single_simulation(args):
    """Run a single simulation."""
    print(f"\nRunning simulation: {args.simulation}")
    print("-"*60)
    
    results = run_simulation(
        simulation_name=args.simulation,
        max_messages=args.max_messages,
        interactive=args.interactive
    )
    
    if "error" in results:
        print(f"Error: {results['error']}")
        return 1
    
    return 0


def run_batch_simulations(args):
    """Run all simulations in batch mode."""
    print("\nRunning all simulations in batch mode...")
    print("-"*60)
    
    all_results = run_all_simulations(max_messages=args.max_messages)
    
    # Save batch results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    batch_file = f"logs/batch_results_{timestamp}.json"
    
    with open(batch_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\nBatch results saved to: {batch_file}")
    return 0


def test_agent_directly(args):
    """Test the agent directly with user input."""
    from ollama_integration import LLMEnhancedBankingAgent, LLMUnavailableError
    
    print("\nDirect Agent Testing Mode")
    print("="*60)
    print("Type your messages to the banking agent.")
    print("Type 'quit' or 'exit' to end.")
    print("Note: Only LLM-enhanced agent is available (no rule-based fallback).")
    print("-"*60)
    
    # Initialize agent (LLM only, no fallback)
    try:
        llm_agent = LLMEnhancedBankingAgent()
    except LLMUnavailableError as e:
        print(f"LLM unavailable: {e}")
        print("Cannot proceed without LLM. Exiting.")
        return 1
    
    current_agent = llm_agent
    use_llm = True
    
    print("Using LLM-enhanced agent (no rule-based fallback).")
    
    print("-"*60)
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if user_input.lower() == 'switch':
                print("Rule-based agent is no longer available. Only LLM-enhanced agent is used.")
                continue
            
            if not user_input:
                continue
            
            # Process the message
            response, tool_used = current_agent.process_message(user_input)
            
            print(f"\nAgent: {response}")
            if tool_used:
                print(f"[Tool used: {tool_used}]")
            
            # Check if agent ended conversation
            if response == "Not my question":
                print("Agent detected off-topic. Conversation ended.")
                break
                
        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")
    
    return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AI-Agent Testing Utility - Test banking agent with human simulations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --list                    List all available simulations
  %(prog)s --simulation bill_status  Run bill status simulation
  %(prog)s --all                     Run all simulations
  %(prog)s --test                    Test agent directly with user input
  %(prog)s --test --llm              Test LLM-enhanced agent directly
        
Simulation Names:
  bill_status        - Human wants to check status of bill INV-2024-789
  mortgage_rate      - Human wants information about 30-year fixed mortgage rates
  off_topic_weather  - Human asks about weather to test off-topic detection
  account_opening    - Human wants to learn about opening a savings account
        """
    )
    
    # Mode selection
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--list", "-l", action="store_true",
                          help="List all available simulations")
    mode_group.add_argument("--simulation", "-s", type=str,
                          help="Run a specific simulation by name")
    mode_group.add_argument("--all", "-a", action="store_true",
                          help="Run all simulations in batch mode")
    mode_group.add_argument("--test", "-t", action="store_true",
                          help="Test agent directly with user input")
    
    # Options
    parser.add_argument("--interactive", "-i", action="store_true",
                       help="Run in interactive mode (pause between messages)")
    parser.add_argument("--max-messages", "-m", type=int, default=10,
                       help="Maximum messages before failure (default: 10)")
    parser.add_argument("--llm", action="store_true",
                       help="Use LLM-enhanced agent (requires Ollama)")
    parser.add_argument("--no-banner", action="store_true",
                       help="Don't show the banner")
    
    args = parser.parse_args()
    
    # Print banner
    if not args.no_banner:
        print_banner()
    
    # Check Ollama status if LLM is requested
    if args.llm:
        if not check_ollama_status():
            print("\nWarning: LLM features may not work correctly.")
            print("Continuing with rule-based agent as fallback...")
    
    # Handle different modes
    if args.list:
        list_simulations()
        return 0
    
    elif args.simulation:
        # Validate simulation name
        simulations = SimulationFactory.get_available_simulations()
        if args.simulation not in simulations:
            print(f"Error: Unknown simulation '{args.simulation}'")
            print("\nAvailable simulations:")
            for sim in simulations:
                print(f"  - {sim}")
            return 1
        
        return run_single_simulation(args)
    
    elif args.all:
        return run_batch_simulations(args)
    
    elif args.test:
        return test_agent_directly(args)
    
    else:
        # No arguments provided, show help
        parser.print_help()
        
        # Also show available simulations
        print("\n" + "="*60)
        list_simulations()
        
        return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)