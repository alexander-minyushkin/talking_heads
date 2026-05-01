#!/usr/bin/env python3
"""
Conversation Runner - Main engine for running agent-human simulations
with success/failure condition tracking.
"""

import sys
import json
import time
from datetime import datetime
from typing import Optional, Dict, Any

from conversation_manager import ConversationManager, ConversationOutcome
from agent.banking_agent import BankingAgentImpl
from human_simulation.simulation_logic import SimulationFactory


class ConversationRunner:
    """Runs conversations between agent and human simulations."""
    
    def __init__(self, max_messages: int = 10):
        """
        Initialize the conversation runner.
        
        Args:
            max_messages: Maximum messages before failure (default: 10)
        """
        self.max_messages = max_messages
        self.conversation_manager = None
        self.agent = None
        self.human_simulation = None
        self.simulation_name = None
        
    def setup_conversation(self, simulation_name: str) -> bool:
        """
        Set up a new conversation with the specified simulation.
        
        Args:
            simulation_name: Name of the simulation to run
            
        Returns:
            True if setup successful, False otherwise
        """
        # Create agent
        self.agent = BankingAgentImpl()
        
        # Create human simulation
        self.human_simulation = SimulationFactory.create_simulation(simulation_name)
        if not self.human_simulation:
            print(f"Error: Unknown simulation '{simulation_name}'")
            return False
        
        # Create conversation manager
        self.conversation_manager = ConversationManager(max_messages=self.max_messages)
        self.simulation_name = simulation_name
        
        print(f"Setup complete: {self.human_simulation.name}")
        print(f"Human goal: {self.human_simulation.goal}")
        print(f"Max messages: {self.max_messages}")
        print("-" * 60)
        
        return True
    
    def run_conversation(self, interactive: bool = False) -> Dict[str, Any]:
        """
        Run the conversation to completion.
        
        Args:
            interactive: If True, pause between messages for user input
            
        Returns:
            Dictionary with conversation results
        """
        if not self.conversation_manager or not self.agent or not self.human_simulation:
            raise RuntimeError("Conversation not set up. Call setup_conversation first.")
        
        print("Starting conversation...\n")
        
        # Get initial human message
        human_message = self.human_simulation.get_initial_message()
        self.conversation_manager.add_message("human", human_message)
        print(f"HUMAN: {human_message}")
        
        # Main conversation loop
        while not self.conversation_manager.is_complete():
            # Get the last human message
            last_human_message = self.conversation_manager.messages[-1]["content"]
            
            # Agent processes the message
            agent_response, tool_used = self.agent.process_message(last_human_message)
            self.conversation_manager.add_message("agent", agent_response, tool_used)
            print(f"\nAGENT: {agent_response}")
            if tool_used:
                print(f"       [Tool used: {tool_used}]")
            
            # Check for off-topic detection
            if agent_response == "Not my question":
                print("\n>>> Agent detected off-topic question.")
                self.conversation_manager.mark_success()
                break
            
            # Check if we've reached max messages
            if self.conversation_manager.message_count >= self.max_messages:
                print(f"\n>>> Reached maximum of {self.max_messages} messages.")
                self.conversation_manager.mark_failure()
                break
            
            # Human simulation responds
            human_response, goal_achieved = self.human_simulation.respond(agent_response)
            
            if human_response:  # Empty response means conversation should end
                self.conversation_manager.add_message("human", human_response)
                print(f"\nHUMAN: {human_response}")
            
            # Check if human achieved their goal
            if goal_achieved:
                print("\n>>> Human achieved their goal.")
                self.conversation_manager.mark_success()
                break
            
            # Check if human simulation thinks goal is achieved
            if self.human_simulation.is_goal_achieved():
                print("\n>>> Human simulation reports goal achieved.")
                self.conversation_manager.mark_success()
                break
            
            # Interactive mode pause
            if interactive:
                input("\nPress Enter to continue...")
        
        # Generate results
        results = self._generate_results()
        self._print_results(results)
        
        return results
    
    def _generate_results(self) -> Dict[str, Any]:
        """Generate comprehensive results from the conversation."""
        summary = self.conversation_manager.get_conversation_summary()
        
        # Determine success reason
        success_reason = "Unknown"
        if summary["outcome"] == "SUCCESSFUL":
            if self.conversation_manager.messages and self.conversation_manager.messages[-1].get("content") == "Not my question":
                success_reason = "Agent detected off-topic question"
            elif self.human_simulation and self.human_simulation.is_goal_achieved():
                success_reason = f"Human achieved goal: {self.human_simulation.goal}"
            else:
                success_reason = "Conversation ended successfully"
        elif summary["outcome"] == "UNSUCCESSFUL":
            success_reason = f"Reached maximum of {self.max_messages} messages"
        
        # Count tools used
        tools_used = {}
        for msg in self.conversation_manager.messages:
            tool = msg.get("tool_used")
            if tool:
                tools_used[tool] = tools_used.get(tool, 0) + 1
        
        return {
            "simulation": self.simulation_name,
            "human_goal": self.human_simulation.goal if self.human_simulation else "Unknown",
            "outcome": summary["outcome"],
            "success_reason": success_reason,
            "total_messages": summary["total_messages"],
            "max_messages": summary["max_messages"],
            "duration_seconds": summary["duration_seconds"],
            "agent_messages": summary["agent_messages"],
            "human_messages": summary["human_messages"],
            "tools_used": tools_used,
            "conversation_history": [
                {
                    "role": msg["role"],
                    "content": msg["content"],
                    "tool": msg.get("tool_used")
                }
                for msg in self.conversation_manager.messages
            ]
        }
    
    def _print_results(self, results: Dict[str, Any]) -> None:
        """Print conversation results."""
        print("\n" + "="*60)
        print("CONVERSATION RESULTS")
        print("="*60)
        
        print(f"Simulation: {results['simulation']}")
        print(f"Human goal: {results['human_goal']}")
        print(f"Outcome: {results['outcome']}")
        print(f"Reason: {results['success_reason']}")
        print(f"Total messages: {results['total_messages']}/{results['max_messages']}")
        print(f"Duration: {results['duration_seconds']:.2f} seconds")
        print(f"Agent messages: {results['agent_messages']}")
        print(f"Human messages: {results['human_messages']}")
        
        if results['tools_used']:
            print("Tools used:")
            for tool, count in results['tools_used'].items():
                print(f"  - {tool}: {count} time(s)")
        
        print("="*60)
    
    def save_results(self, filename: Optional[str] = None) -> str:
        """
        Save conversation results to a file.
        
        Args:
            filename: Optional filename, will generate one if not provided
            
        Returns:
            The filename used
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"logs/conversation_{self.simulation_name}_{timestamp}.json"
        
        results = self._generate_results()
        
        # Ensure logs directory exists
        import os
        os.makedirs("logs", exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Results saved to: {filename}")
        return filename


def run_simulation(simulation_name: str, max_messages: int = 10, interactive: bool = False) -> Dict[str, Any]:
    """
    Run a single simulation.
    
    Args:
        simulation_name: Name of the simulation to run
        max_messages: Maximum messages before failure
        interactive: Whether to run in interactive mode
        
    Returns:
        Conversation results
    """
    runner = ConversationRunner(max_messages=max_messages)
    
    if not runner.setup_conversation(simulation_name):
        return {"error": f"Failed to setup simulation '{simulation_name}'"}
    
    results = runner.run_conversation(interactive=interactive)
    runner.save_results()
    
    return results


def run_all_simulations(max_messages: int = 10) -> Dict[str, Dict[str, Any]]:
    """
    Run all available simulations.
    
    Args:
        max_messages: Maximum messages before failure
        
    Returns:
        Dictionary mapping simulation names to results
    """
    all_results = {}
    simulations = SimulationFactory.get_available_simulations()
    
    print(f"Running all {len(simulations)} simulations...")
    print("="*60)
    
    for sim_name in simulations:
        print(f"\n>>> Running simulation: {sim_name}")
        print("-"*40)
        
        try:
            results = run_simulation(sim_name, max_messages=max_messages, interactive=False)
            all_results[sim_name] = results
        except Exception as e:
            print(f"Error running simulation {sim_name}: {e}")
            all_results[sim_name] = {"error": str(e)}
        
        time.sleep(1)  # Brief pause between simulations
    
    # Print summary
    print("\n" + "="*60)
    print("ALL SIMULATIONS SUMMARY")
    print("="*60)
    
    successful = 0
    unsuccessful = 0
    errors = 0
    
    for sim_name, results in all_results.items():
        if "error" in results:
            errors += 1
            print(f"{sim_name}: ERROR - {results['error']}")
        else:
            outcome = results.get("outcome", "UNKNOWN")
            if outcome == "SUCCESSFUL":
                successful += 1
                print(f"{sim_name}: SUCCESSFUL - {results.get('success_reason', '')}")
            else:
                unsuccessful += 1
                print(f"{sim_name}: UNSUCCESSFUL - {results.get('success_reason', '')}")
    
    print("\n" + "="*60)
    print(f"Total simulations: {len(simulations)}")
    print(f"Successful: {successful}")
    print(f"Unsuccessful: {unsuccessful}")
    print(f"Errors: {errors}")
    print("="*60)
    
    return all_results


if __name__ == "__main__":
    # Example usage
    import argparse
    
    parser = argparse.ArgumentParser(description="Run AI-Agent human simulation tests")
    parser.add_argument("--simulation", "-s", type=str, 
                       help="Name of simulation to run (bill_status, mortgage_rate, off_topic_weather, account_opening)")
    parser.add_argument("--all", "-a", action="store_true",
                       help="Run all simulations")
    parser.add_argument("--interactive", "-i", action="store_true",
                       help="Run in interactive mode (pause between messages)")
    parser.add_argument("--max-messages", "-m", type=int, default=10,
                       help="Maximum messages before failure (default: 10)")
    
    args = parser.parse_args()
    
    if args.all:
        run_all_simulations(max_messages=args.max_messages)
    elif args.simulation:
        run_simulation(args.simulation, max_messages=args.max_messages, interactive=args.interactive)
    else:
        # Show available simulations
        print("Available simulations:")
        for sim_name in SimulationFactory.get_available_simulations():
            desc = SimulationFactory.get_simulation_description(sim_name)
            print(f"  {sim_name}: {desc}")
        print("\nUse --simulation <name> to run a specific simulation or --all to run all.")