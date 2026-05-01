#!/usr/bin/env python3
"""
Human simulation logic implementing the scenarios from MD files.
"""

import re
import random
from typing import Dict, List, Optional, Tuple, Any
from conversation_manager import HumanSimulation


class BillStatusInquirySimulation(HumanSimulation):
    """Simulation for bill status inquiry."""
    
    def __init__(self):
        super().__init__(
            name="Bill Status Inquiry",
            description="Human wants to check status of bill INV-2024-789",
            goal="Get bill status for INV-2024-789"
        )
        self.bill_number = "INV-2024-789"
        self.bill_number_provided = False
        self.status_received = False
        
    def get_initial_message(self) -> str:
        """Get the initial message - general question about bill payments."""
        initial_options = [
            "Hello, I'd like to check on a bill payment.",
            "Hi, can you help me with a bill status inquiry?",
            "I need to check if a bill has been paid.",
            "Could you tell me about a bill payment status?"
        ]
        return random.choice(initial_options)
    
    def respond(self, agent_message: str) -> Tuple[str, bool]:
        """
        Generate a response to an agent message.
        
        Args:
            agent_message: The agent's message
            
        Returns:
            Tuple of (response_message, goal_achieved)
        """
        agent_lower = agent_message.lower()
        
        # Check if agent asked for bill number
        if any(keyword in agent_lower for keyword in ['bill number', 'invoice number', 'number', 'which bill']):
            if not self.bill_number_provided:
                self.bill_number_provided = True
                return f"Yes, it's {self.bill_number}.", False
        
        # Check if agent provided bill status
        if self.bill_number in agent_message or "status" in agent_lower:
            if "pending" in agent_lower or "paid" in agent_lower or "overdue" in agent_lower:
                self.status_received = True
                thank_options = [
                    "Thank you for checking. That's all I needed.",
                    "Thanks, that answers my question.",
                    "Appreciate the help. That's what I wanted to know."
                ]
                return random.choice(thank_options), True
        
        # If agent asks for clarification but we've already provided bill number
        if self.bill_number_provided and any(keyword in agent_lower for keyword in ['clarify', 'more details', 'specify']):
            return f"I already gave you the bill number: {self.bill_number}. Can you check the status?", False
        
        # Default response if agent doesn't ask for bill number
        if not self.bill_number_provided:
            prompt_options = [
                "Can you check the status?",
                "Do you need the bill number?",
                "What information do you need from me?"
            ]
            return random.choice(prompt_options), False
        
        # If we've provided bill number but no status yet
        return "Can you check the status now?", False
    
    def is_goal_achieved(self) -> bool:
        """Check if the human's goal has been achieved."""
        return self.status_received


class MortgageRateInquirySimulation(HumanSimulation):
    """Simulation for mortgage rate inquiry."""
    
    def __init__(self):
        super().__init__(
            name="Mortgage Rate Inquiry",
            description="Human wants information about 30-year fixed mortgage rates",
            goal="Get mortgage rate information for 30-year fixed mortgage"
        )
        self.mortgage_type_specified = False
        self.rate_info_received = False
        self.followup_asked = False
        
    def get_initial_message(self) -> str:
        """Get the initial message - general question about mortgage options."""
        initial_options = [
            "I'm thinking about buying a house and wanted to know about mortgage rates.",
            "Hi, I'd like information about mortgage options.",
            "Can you tell me about current mortgage rates?",
            "I'm considering a mortgage and need some information."
        ]
        return random.choice(initial_options)
    
    def respond(self, agent_message: str) -> Tuple[str, bool]:
        """
        Generate a response to an agent message.
        
        Args:
            agent_message: The agent's message
            
        Returns:
            Tuple of (response_message, goal_achieved)
        """
        agent_lower = agent_message.lower()
        
        # Check if agent asked for mortgage type
        if any(keyword in agent_lower for keyword in ['type', 'kind', 'which', 'fixed or adjustable']):
            if not self.mortgage_type_specified:
                self.mortgage_type_specified = True
                return "I'm interested in a 30-year fixed mortgage.", False
        
        # Check if agent provided rate information
        if any(keyword in agent_lower for keyword in ['rate', 'apr', 'percentage', 'interest']):
            if '30' in agent_message or 'fixed' in agent_lower:
                self.rate_info_received = True
                
                # Ask one follow-up question
                if not self.followup_asked:
                    self.followup_asked = True
                    followup_options = [
                        "What's the typical application process like?",
                        "How long does approval usually take?",
                        "What credit score is needed for the best rates?"
                    ]
                    return random.choice(followup_options), False
                else:
                    # Already asked follow-up, now we're done
                    thank_options = [
                        "Thank you, that's very helpful.",
                        "Thanks for the detailed information.",
                        "Appreciate your help. That answers all my questions."
                    ]
                    return random.choice(thank_options), True
        
        # Default response
        if not self.mortgage_type_specified:
            return "What information do you need from me?", False
        else:
            return "Can you provide more details about the rates?", False
    
    def is_goal_achieved(self) -> bool:
        """Check if the human's goal has been achieved."""
        return self.rate_info_received and self.followup_asked


class OffTopicWeatherSimulation(HumanSimulation):
    """Simulation for off-topic weather inquiry."""
    
    def __init__(self):
        super().__init__(
            name="Off-topic Weather Inquiry",
            description="Human asks about weather to test off-topic detection",
            goal="Get agent to correctly identify this as off-topic"
        )
        self.off_topic_detected = False
        self.attempts = 0
        
    def get_initial_message(self) -> str:
        """Get the initial message - casual weather question."""
        initial_options = [
            "Hi there! Do you know if it's going to rain today?",
            "Hello, what's the weather forecast for tomorrow?",
            "Hey, is it sunny outside right now?",
            "Do you think I'll need an umbrella today?"
        ]
        return random.choice(initial_options)
    
    def respond(self, agent_message: str) -> Tuple[str, bool]:
        """
        Generate a response to an agent message.
        
        Args:
            agent_message: The agent's message
            
        Returns:
            Tuple of (response_message, goal_achieved)
        """
        self.attempts += 1
        
        # Check if agent said "Not my question"
        if "not my question" in agent_message.lower():
            self.off_topic_detected = True
            return "", True  # Empty response, conversation ends
        
        # If agent responds with banking information
        if any(keyword in agent_message.lower() for keyword in ['bank', 'account', 'loan', 'mortgage']):
            if self.attempts == 1:
                return "No, I meant the actual weather outside.", False
            else:
                return "I'm just asking about the weather forecast.", False
        
        # If agent asks for clarification
        if any(keyword in agent_message.lower() for keyword in ['clarify', 'explain', 'what do you mean']):
            return "I'm asking about today's weather, like temperature and rain.", False
        
        # Default: prompt again
        return "So, about the weather...", False
    
    def is_goal_achieved(self) -> bool:
        """Check if the human's goal has been achieved."""
        return self.off_topic_detected


class AccountOpeningProcessSimulation(HumanSimulation):
    """Simulation for account opening process inquiry."""
    
    def __init__(self):
        super().__init__(
            name="Account Opening Process Inquiry",
            description="Human wants to learn about opening a savings account",
            goal="Get complete information about savings account opening process"
        )
        self.account_type_specified = False
        self.documents_info_received = False
        self.timeframe_info_received = False
        self.step = 0  # 0: initial, 1: type specified, 2: docs asked, 3: timeframe asked
        
    def get_initial_message(self) -> str:
        """Get the initial message - general question about opening accounts."""
        initial_options = [
            "I'm interested in opening a new account. Can you tell me about the process?",
            "Hi, I want to open an account. What do I need to do?",
            "How do I go about opening a new bank account?",
            "Can you explain the account opening procedure?"
        ]
        return random.choice(initial_options)
    
    def respond(self, agent_message: str) -> Tuple[str, bool]:
        """
        Generate a response to an agent message.
        
        Args:
            agent_message: The agent's message
            
        Returns:
            Tuple of (response_message, goal_achieved)
        """
        agent_lower = agent_message.lower()
        
        # Step 0: Agent asks for account type
        if self.step == 0 and any(keyword in agent_lower for keyword in ['type', 'kind', 'which account']):
            self.step = 1
            self.account_type_specified = True
            return "A savings account.", False
        
        # Step 1: Agent provides initial info, human asks about documents
        if self.step == 1 and 'savings' in agent_lower:
            self.step = 2
            return "What documents are typically required?", False
        
        # Step 2: Agent provides document info, human asks about timeframe
        if self.step == 2 and any(keyword in agent_lower for keyword in ['document', 'id', 'proof', 'required']):
            self.step = 3
            self.documents_info_received = True
            return "How long does it take to open the account?", False
        
        # Step 3: Agent provides timeframe info, human thanks and ends
        if self.step == 3 and any(keyword in agent_lower for keyword in ['time', 'long', 'process', 'hours', 'days']):
            self.step = 4
            self.timeframe_info_received = True
            thank_options = [
                "Thank you, that answers all my questions.",
                "Thanks for the detailed information.",
                "Appreciate your help. I have all the information I need."
            ]
            return random.choice(thank_options), True
        
        # Default response if agent doesn't follow expected flow
        if self.step == 0:
            return "What do you need to know from me?", False
        elif self.step == 1:
            return "I said a savings account. Can you tell me about opening one?", False
        elif self.step == 2:
            return "I asked about required documents.", False
        elif self.step == 3:
            return "I'm asking about how long it takes.", False
        
        return "Thank you.", True
    
    def is_goal_achieved(self) -> bool:
        """Check if the human's goal has been achieved."""
        return self.account_type_specified and self.documents_info_received and self.timeframe_info_received


class SimulationFactory:
    """Factory to create simulation instances."""
    
    @staticmethod
    def create_simulation(simulation_name: str) -> Optional[HumanSimulation]:
        """
        Create a simulation instance by name.
        
        Args:
            simulation_name: Name of the simulation to create
            
        Returns:
            Simulation instance or None if not found
        """
        simulations = {
            "bill_status": BillStatusInquirySimulation,
            "mortgage_rate": MortgageRateInquirySimulation,
            "off_topic_weather": OffTopicWeatherSimulation,
            "account_opening": AccountOpeningProcessSimulation,
        }
        
        simulation_class = simulations.get(simulation_name.lower())
        if simulation_class:
            return simulation_class()
        return None
    
    @staticmethod
    def get_available_simulations() -> List[str]:
        """Get list of available simulation names."""
        return ["bill_status", "mortgage_rate", "off_topic_weather", "account_opening"]
    
    @staticmethod
    def get_simulation_description(name: str) -> str:
        """Get description of a simulation."""
        descriptions = {
            "bill_status": "Human wants to check status of bill INV-2024-789",
            "mortgage_rate": "Human wants information about 30-year fixed mortgage rates",
            "off_topic_weather": "Human asks about weather to test off-topic detection",
            "account_opening": "Human wants to learn about opening a savings account",
        }
        return descriptions.get(name, "Unknown simulation")


# Example usage
if __name__ == "__main__":
    factory = SimulationFactory()
    
    print("Available simulations:")
    for sim_name in factory.get_available_simulations():
        print(f"  - {sim_name}: {factory.get_simulation_description(sim_name)}")
    
    # Test a simulation
    sim = factory.create_simulation("bill_status")
    if sim:
        print(f"\nTesting {sim.name}:")
        print(f"Goal: {sim.goal}")
        print(f"Initial message: {sim.get_initial_message()}")
        
        # Simulate a conversation
        agent_messages = [
            "I can help with that. Do you have the bill number?",
            "The bill INV-2024-789 is currently PENDING."
        ]
        
        for agent_msg in agent_messages:
            print(f"\nAgent: {agent_msg}")
            response, goal_achieved = sim.respond(agent_msg)
            if response:
                print(f"Human: {response}")
            if goal_achieved:
                print("Goal achieved!")
                break