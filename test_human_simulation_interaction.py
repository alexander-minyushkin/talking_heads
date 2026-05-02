#!/usr/bin/env python3
"""
Test script to demonstrate how to talk to Human simulation as an Agent.
This shows the manual testing process where you pretend to be the Agent.
"""

import sys
from human_simulation.simulation_logic import SimulationFactory
from agent.banking_agent import BankingAgentImpl

def test_as_agent_manual():
    """
    Manual testing where you (the user) pretend to be the Agent.
    The Human simulation always starts talking first.
    """
    print("=" * 70)
    print("MANUAL AGENT TESTING - You are the Agent")
    print("=" * 70)
    print("\nAvailable simulations:")
    
    factory = SimulationFactory()
    simulations = factory.get_available_simulations()
    
    for i, sim_name in enumerate(simulations, 1):
        desc = factory.get_simulation_description(sim_name)
        print(f"  {i}. {sim_name:20} - {desc}")
    
    print("\n" + "-" * 70)
    
    # Let user choose a simulation
    while True:
        try:
            choice = input("\nSelect simulation number (1-4) or 'q' to quit: ").strip()
            if choice.lower() == 'q':
                return
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(simulations):
                simulation_name = simulations[choice_num - 1]
                break
            else:
                print(f"Please enter a number between 1 and {len(simulations)}")
        except ValueError:
            print("Please enter a valid number")
    
    # Create the simulation
    simulation = factory.create_simulation(simulation_name)
    if not simulation:
        print(f"Error: Could not create simulation '{simulation_name}'")
        return
    
    print(f"\nStarting simulation: {simulation.name}")
    print(f"Human Goal: {simulation.goal}")
    print("\n" + "=" * 70)
    print("CONVERSATION START")
    print("=" * 70)
    
    # Human always starts first
    human_message = simulation.get_initial_message()
    print(f"\nHUMAN: {human_message}")
    
    # Conversation loop
    while True:
        # Get agent response from user (you)
        agent_response = input("\nAGENT (you): ").strip()
        
        if agent_response.lower() in ['quit', 'exit', 'q']:
            print("\nConversation ended by user.")
            break
        
        # Human simulation responds
        human_response, goal_achieved = simulation.respond(agent_response)
        
        if not human_response and goal_achieved:
            print("\n>>> Human achieved their goal. Conversation ended.")
            break
        
        if human_response:
            print(f"\nHUMAN: {human_response}")
        
        if goal_achieved:
            print("\n>>> Human achieved their goal. Conversation ended.")
            break
        
        # Check if simulation thinks goal is achieved
        if simulation.is_goal_achieved():
            print("\n>>> Human simulation reports goal achieved. Conversation ended.")
            break
    
    print("\n" + "=" * 70)
    print("CONVERSATION END")
    print("=" * 70)

def test_with_real_agent():
    """
    Test with the actual BankingAgent (automatic mode).
    This shows how the agent would interact with the human simulation.
    """
    print("\n" + "=" * 70)
    print("AUTOMATIC AGENT TESTING - Using BankingAgentImpl")
    print("=" * 70)
    
    # Create agent and simulation
    agent = BankingAgentImpl()
    factory = SimulationFactory()
    simulation = factory.create_simulation("bill_status")
    
    if not simulation:
        print("Error: Could not create simulation")
        return
    
    print(f"\nSimulation: {simulation.name}")
    print(f"Human Goal: {simulation.goal}")
    print("\n" + "=" * 70)
    print("CONVERSATION START")
    print("=" * 70)
    
    # Human starts first
    human_message = simulation.get_initial_message()
    print(f"\nHUMAN: {human_message}")
    
    # Agent responds
    agent_response, tool_used = agent.process_message(human_message)
    print(f"\nAGENT: {agent_response}")
    if tool_used:
        print(f"       [Tool used: {tool_used}]")
    
    # Continue conversation for a few turns
    for turn in range(3):
        human_response, goal_achieved = simulation.respond(agent_response)
        
        if not human_response and goal_achieved:
            print("\n>>> Human achieved goal.")
            break
        
        if human_response:
            print(f"\nHUMAN: {human_response}")
        
        if goal_achieved:
            print("\n>>> Human achieved goal.")
            break
        
        # Agent responds again
        agent_response, tool_used = agent.process_message(human_response)
        print(f"\nAGENT: {agent_response}")
        if tool_used:
            print(f"       [Tool used: {tool_used}]")
    
    print("\n" + "=" * 70)
    print("CONVERSATION END")
    print("=" * 70)

def main():
    """Main function to run the test."""
    print("Human Simulation Testing Framework")
    print("Two testing modes available:")
    print("  1. Manual mode - You pretend to be the Agent")
    print("  2. Automatic mode - Use the actual BankingAgent")
    
    while True:
        print("\n" + "-" * 70)
        print("Select mode:")
        print("  1. Manual testing (you as Agent)")
        print("  2. Automatic testing (real Agent)")
        print("  3. Exit")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == '1':
            test_as_agent_manual()
        elif choice == '2':
            test_with_real_agent()
        elif choice == '3':
            print("\nGoodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()