#!/usr/bin/env python3
"""
Conversation Manager for AI-Agent Testing Utility

Manages interactions between the banking agent and human simulations,
tracking message counts and determining success/failure conditions.
"""

import json
import time
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any


class ConversationOutcome(Enum):
    """Possible outcomes of a conversation."""
    SUCCESS = "SUCCESSFUL"
    FAILURE = "UNSUCCESSFUL"
    IN_PROGRESS = "IN_PROGRESS"


class ConversationManager:
    """Manages the conversation between agent and human simulation."""
    
    def __init__(self, max_messages: int = 10):
        """
        Initialize a new conversation manager.
        
        Args:
            max_messages: Maximum number of messages before failure (default: 10)
        """
        self.max_messages = max_messages
        self.messages: List[Dict[str, Any]] = []
        self.message_count = 0
        self.start_time = datetime.now()
        self.outcome = ConversationOutcome.IN_PROGRESS
        
    def add_message(self, role: str, content: str, tool_used: Optional[str] = None) -> int:
        """
        Add a message to the conversation.
        
        Args:
            role: 'agent' or 'human'
            content: The message content
            tool_used: Optional tool name if agent used a tool
            
        Returns:
            The current message count
        """
        self.message_count += 1
        message = {
            "id": self.message_count,
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "tool_used": tool_used
        }
        self.messages.append(message)
        
        # Check if we've reached the maximum messages
        if self.message_count >= self.max_messages:
            self.outcome = ConversationOutcome.FAILURE
            
        return self.message_count
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the current conversation state."""
        return {
            "total_messages": self.message_count,
            "max_messages": self.max_messages,
            "outcome": self.outcome.value,
            "duration_seconds": (datetime.now() - self.start_time).total_seconds(),
            "agent_messages": len([m for m in self.messages if m["role"] == "agent"]),
            "human_messages": len([m for m in self.messages if m["role"] == "human"]),
        }
    
    def get_conversation_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get the conversation history.
        
        Args:
            limit: Optional limit on number of messages to return
            
        Returns:
            List of message dictionaries
        """
        if limit:
            return self.messages[-limit:]
        return self.messages
    
    def mark_success(self) -> None:
        """Mark the conversation as successful."""
        self.outcome = ConversationOutcome.SUCCESS
    
    def mark_failure(self) -> None:
        """Mark the conversation as failed."""
        self.outcome = ConversationOutcome.FAILURE
    
    def is_complete(self) -> bool:
        """Check if the conversation is complete (success or failure)."""
        return self.outcome != ConversationOutcome.IN_PROGRESS
    
    def save_to_file(self, filename: str) -> None:
        """
        Save the conversation to a JSON file.
        
        Args:
            filename: Path to save the conversation
        """
        data = {
            "metadata": self.get_conversation_summary(),
            "messages": self.messages,
            "start_time": self.start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def print_conversation(self) -> None:
        """Print the conversation to console."""
        print("\n" + "="*60)
        print("CONVERSATION HISTORY")
        print("="*60)
        
        for msg in self.messages:
            role_display = "AGENT" if msg["role"] == "agent" else "HUMAN"
            tool_info = f" [Tool: {msg['tool_used']}]" if msg["tool_used"] else ""
            print(f"{role_display}{tool_info}: {msg['content']}")
            print("-"*40)
        
        print(f"\nTotal messages: {self.message_count}/{self.max_messages}")
        print(f"Outcome: {self.outcome.value}")
        print("="*60)


class HumanSimulation:
    """Base class for human simulations."""
    
    def __init__(self, name: str, description: str, goal: str):
        """
        Initialize a human simulation.
        
        Args:
            name: Name of the simulation
            description: Brief description
            goal: The human's goal for the interaction
        """
        self.name = name
        self.description = description
        self.goal = goal
        self.state = "initial"  # Tracks simulation state
        self.details_revealed = False
        
    def get_initial_message(self) -> str:
        """Get the initial message from the human."""
        raise NotImplementedError("Subclasses must implement get_initial_message")
    
    def respond(self, agent_message: str) -> Tuple[str, bool]:
        """
        Generate a response to an agent message.
        
        Args:
            agent_message: The agent's message
            
        Returns:
            Tuple of (response_message, goal_achieved)
        """
        raise NotImplementedError("Subclasses must implement respond")
    
    def is_goal_achieved(self) -> bool:
        """Check if the human's goal has been achieved."""
        raise NotImplementedError("Subclasses must implement is_goal_achieved")


class BankingAgent:
    """Base class for banking agents."""
    
    def __init__(self, name: str):
        """
        Initialize a banking agent.
        
        Args:
            name: Name of the agent
        """
        self.name = name
        
    def process_message(self, human_message: str) -> Tuple[str, Optional[str]]:
        """
        Process a human message and generate a response.
        
        Args:
            human_message: The message from the human
            
        Returns:
            Tuple of (response_message, tool_used)
        """
        raise NotImplementedError("Subclasses must implement process_message")
    
    def is_off_topic(self, message: str) -> bool:
        """
        Check if a message is off-topic (non-banking).
        
        Args:
            message: The message to check
            
        Returns:
            True if the message is off-topic
        """
        raise NotImplementedError("Subclasses must implement is_off_topic")