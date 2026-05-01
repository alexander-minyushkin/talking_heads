#!/usr/bin/env python3
"""
Ollama integration for AI-Agent testing utility.
Uses minimax-m2.5:cloud model for LLM calls.
"""

import json
import subprocess
import time
from typing import Dict, List, Optional, Any, Tuple


class OllamaClient:
    """Client for interacting with Ollama API."""
    
    def __init__(self, model: str = "minimax-m2.5:cloud", base_url: str = "http://localhost:11434"):
        """
        Initialize Ollama client.
        
        Args:
            model: The model to use (default: minimax-m2.5:cloud)
            base_url: Ollama API base URL
        """
        self.model = model
        self.base_url = base_url
        
    def check_model_available(self) -> bool:
        """
        Check if the specified model is available.
        
        Returns:
            True if model is available, False otherwise
        """
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return self.model in result.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
            return False
    
    def pull_model(self) -> bool:
        """
        Pull the model if not available.
        
        Returns:
            True if successful, False otherwise
        """
        print(f"Pulling model {self.model}...")
        try:
            result = subprocess.run(
                ["ollama", "pull", self.model],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout for pulling
            )
            if result.returncode == 0:
                print(f"Model {self.model} pulled successfully.")
                return True
            else:
                print(f"Failed to pull model: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print("Timeout while pulling model.")
            return False
        except Exception as e:
            print(f"Error pulling model: {e}")
            return False
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None, 
                 temperature: float = 0.7, max_tokens: int = 500) -> str:
        """
        Generate text using Ollama.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            temperature: Temperature for generation (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text
        """
        # Prepare the request data
        request_data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        if system_prompt:
            request_data["system"] = system_prompt
        
        try:
            # Use curl to call Ollama API
            curl_cmd = [
                "curl", "-s", "-X", "POST",
                f"{self.base_url}/api/generate",
                "-H", "Content-Type: application/json",
                "-d", json.dumps(request_data)
            ]
            
            result = subprocess.run(
                curl_cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                response = json.loads(result.stdout)
                return response.get("response", "").strip()
            else:
                print(f"Ollama API error: {result.stderr}")
                return f"Error: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return "Error: Request timeout"
        except json.JSONDecodeError:
            return "Error: Invalid JSON response"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """
        Chat completion using Ollama.
        
        Args:
            messages: List of message dicts with "role" and "content"
            temperature: Temperature for generation
            
        Returns:
            Assistant's response
        """
        # Prepare the request data
        request_data = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        
        try:
            # Use curl to call Ollama chat API
            curl_cmd = [
                "curl", "-s", "-X", "POST",
                f"{self.base_url}/api/chat",
                "-H", "Content-Type: application/json",
                "-d", json.dumps(request_data)
            ]
            
            result = subprocess.run(
                curl_cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                response = json.loads(result.stdout)
                return response.get("message", {}).get("content", "").strip()
            else:
                print(f"Ollama chat API error: {result.stderr}")
                return f"Error: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return "Error: Request timeout"
        except json.JSONDecodeError:
            return "Error: Invalid JSON response"
        except Exception as e:
            return f"Error: {str(e)}"


class LLMEnhancedBankingAgent:
    """Banking agent enhanced with LLM capabilities."""
    
    def __init__(self, use_llm: bool = True, model: str = "minimax-m2.5:cloud"):
        """
        Initialize LLM-enhanced banking agent.
        
        Args:
            use_llm: Whether to use LLM for responses
            model: Ollama model to use
        """
        self.use_llm = use_llm
        self.llm_client = None
        
        if use_llm:
            self.llm_client = OllamaClient(model=model)
            if not self.llm_client.check_model_available():
                print(f"Model {model} not available. Attempting to pull...")
                if not self.llm_client.pull_model():
                    print("Falling back to rule-based agent.")
                    self.use_llm = False
        
        # Import the rule-based agent for fallback
        from agent.banking_agent import BankingAgentImpl
        self.rule_agent = BankingAgentImpl()
        
        # System prompt for banking agent
        self.system_prompt = """You are a helpful banking assistant specializing in banking topics.
        You have access to two tools:
        1. check_bill_status(bill_number) - Checks status of a bill (returns PAID, PENDING, OVERDUE, or NOT_FOUND)
        2. provide_bank_information(query) - Provides general bank information from knowledge base
        
        Your responsibilities:
        - Only answer banking-related questions (accounts, loans, bills, payments, etc.)
        - If asked about non-banking topics (weather, sports, entertainment, etc.), respond with "Not my question" and end the conversation
        - Ask clarifying questions if information is incomplete
        - Use the appropriate tool when needed
        - Keep responses concise and helpful
        
        Banking topics include: accounts, loans, mortgages, credit cards, bill payments, transfers, investments, bank policies, etc.
        Non-banking topics include: weather, sports, movies, music, personal advice, technical support, politics, etc."""
    
    def process_message(self, human_message: str) -> Tuple[str, Optional[str]]:
        """
        Process a human message using LLM or rule-based agent.
        
        Args:
            human_message: The message from the human
            
        Returns:
            Tuple of (response_message, tool_used)
        """
        # First, use rule-based agent for off-topic detection and tool usage
        rule_response, tool_used = self.rule_agent.process_message(human_message)
        
        # If agent detected off-topic, return immediately
        if rule_response == "Not my question":
            return rule_response, tool_used
        
        # If a tool was used, we have our response
        if tool_used:
            return rule_response, tool_used
        
        # If using LLM and no tool was needed, enhance the response
        if self.use_llm and self.llm_client:
            try:
                # Prepare messages for LLM
                messages = [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": human_message}
                ]
                
                # Get LLM response
                llm_response = self.llm_client.chat(messages, temperature=0.3)
                
                # Check if LLM response indicates off-topic
                if "not my question" in llm_response.lower() or "not a banking topic" in llm_response.lower():
                    return "Not my question", None
                
                # Use LLM response
                return llm_response, None
                
            except Exception as e:
                print(f"LLM error: {e}. Falling back to rule-based response.")
                return rule_response, None
        
        # Fallback to rule-based response
        return rule_response, None
    
    def is_off_topic(self, message: str) -> bool:
        """Check if a message is off-topic using rule-based agent."""
        return self.rule_agent.is_off_topic(message)


# Example usage
if __name__ == "__main__":
    # Test Ollama client
    client = OllamaClient()
    
    print("Checking model availability...")
    if client.check_model_available():
        print(f"Model {client.model} is available.")
        
        # Test generation
        test_prompt = "What are the benefits of a savings account?"
        print(f"\nTesting generation with prompt: {test_prompt}")
        
        response = client.generate(
            prompt=test_prompt,
            system_prompt="You are a helpful banking assistant.",
            temperature=0.3
        )
        
        print(f"Response: {response}")
        
        # Test chat
        print("\nTesting chat...")
        messages = [
            {"role": "system", "content": "You are a helpful banking assistant."},
            {"role": "user", "content": "How do I open a checking account?"}
        ]
        
        chat_response = client.chat(messages, temperature=0.3)
        print(f"Chat response: {chat_response}")
        
    else:
        print(f"Model {client.model} is not available.")
        print("You can pull it with: ollama pull minimax-m2.5:cloud")
    
    # Test LLM-enhanced agent
    print("\n" + "="*60)
    print("Testing LLM-enhanced banking agent...")
    
    agent = LLMEnhancedBankingAgent(use_llm=True)
    
    test_messages = [
        "Can you check the status of bill INV-2024-001?",
        "What are your mortgage rates?",
        "What's the weather like today?",
        "How do I transfer money to another account?"
    ]
    
    for msg in test_messages:
        print(f"\nHuman: {msg}")
        response, tool = agent.process_message(msg)
        print(f"Agent: {response}")
        if tool:
            print(f"Tool used: {tool}")