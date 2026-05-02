#!/usr/bin/env python3
"""
Ollama integration for AI-Agent testing utility.
Uses minimax-m2.5:cloud model for LLM calls.
"""

import json
import subprocess
import time
import re
import random
from typing import Dict, List, Optional, Any, Tuple


class LLMUnavailableError(Exception):
    """Exception raised when LLM is not available."""
    pass


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
                timeout=60
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
    
    def __init__(self, model: str = "minimax-m2.5:cloud"):
        """
        Initialize LLM-enhanced banking agent.
        
        Args:
            model: Ollama model to use
        """
        self.use_llm = True  # Always use LLM, no fallback
        self.llm_client = OllamaClient(model=model)
        
        # Check if model is available, attempt to pull if not
        if not self.llm_client.check_model_available():
            print(f"Model {model} not available. Attempting to pull...")
            if not self.llm_client.pull_model():
                raise LLMUnavailableError(f"Model {model} is not available and could not be pulled.")
        
        # Initialize rule-based data structures for tool execution
        self.bill_database = self._initialize_bill_database()
        self.bank_knowledge_base = self._initialize_knowledge_base()
        
        # Banking keywords for off-topic detection
        self.BANKING_KEYWORDS = [
            'bank', 'account', 'loan', 'mortgage', 'credit', 'debit', 'bill', 'payment',
            'transfer', 'deposit', 'withdrawal', 'balance', 'statement', 'fee', 'interest',
            'rate', 'savings', 'checking', 'investment', 'card', 'atm', 'branch', 'online',
            'banking', 'finance', 'financial', 'money', 'cash', 'check', 'wire', 'ach',
            'overdraft', 'insurance', 'retirement', 'ira', '401k', 'cd', 'certificate',
            'application', 'approval', 'document', 'id', 'verification', 'authentication'
        ]
        
        # Bill number patterns
        self.BILL_PATTERNS = [
            r'INV-\d{4}-\d{3}',  # INV-2024-001
            r'BILL-\d{6}',        # BILL-123456
            r'\d{10}',            # 1234567890
            r'[A-Z]{3}-\d{5}',    # ABC-12345
            r'INV\d{8}',          # INV20240001
            r'BL-\d{4}-\d{4}',   # BL-2024-0001
        ]
        
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
    
    def _initialize_bill_database(self):
        """Initialize a simulated bill database."""
        return {
            "INV-2024-001": "PAID",
            "INV-2024-002": "PENDING",
            "INV-2024-003": "OVERDUE",
            "INV-2024-789": "PENDING",  # From human simulation
            "BILL-123456": "PAID",
            "BILL-654321": "OVERDUE",
            "9876543210": "PENDING",
            "ABC-12345": "PAID",
        }
    
    def _initialize_knowledge_base(self):
        """Initialize a simulated bank knowledge base (RAG system)."""
        return {
            "mortgage rates": [
                "30-year fixed mortgage: 3.5% - 4.2% APR",
                "15-year fixed mortgage: 3.0% - 3.8% APR",
                "Adjustable-rate mortgage (ARM): 2.8% - 3.5% initial rate",
                "Rates depend on credit score, down payment, and loan amount."
            ],
            "savings account": [
                "High-yield savings account: 2.5% APY",
                "Regular savings account: 0.5% APY",
                "Minimum opening deposit: $25",
                "No monthly fees with minimum balance of $300"
            ],
            "checking account": [
                "Free checking with direct deposit",
                "Overdraft protection available",
                "Unlimited ATM fee reimbursements",
                "Mobile check deposit included"
            ],
            "credit cards": [
                "Cashback card: 1.5% on all purchases",
                "Travel card: 2x points on travel and dining",
                "Student card: No annual fee, credit building tools",
                "All cards have $0 fraud liability"
            ],
            "loan application": [
                "Personal loans: 5.99% - 14.99% APR",
                "Auto loans: 3.99% - 7.99% APR",
                "Application requires: ID, proof of income, credit check",
                "Approval typically within 1-3 business days"
            ],
            "account opening": [
                "Required documents: Government-issued ID, proof of address, SSN",
                "Can be done online, in branch, or by phone",
                "Initial deposit required for most accounts",
                "Account activation within 24 hours"
            ],
            "bill payment": [
                "Online bill pay: Free for all customers",
                "Automatic payments available",
                "Payment processing: 1-2 business days",
                "Can pay bills from checking, savings, or credit card"
            ],
            "general information": [
                "Founded in 1950, serving customers for over 70 years",
                "FDIC insured up to $250,000 per depositor",
                "Over 500 branches nationwide",
                "24/7 customer support: 1-800-BANK-123"
            ]
        }
    
    def extract_bill_number(self, message: str):
        """
        Extract a bill number from a message.
        
        Args:
            message: The message to search
        
        Returns:
            Bill number if found, None otherwise
        """
        for pattern in self.BILL_PATTERNS:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(0)
        return None
    
    def check_bill_status(self, bill_number: str):
        """
        Check the status of a bill.
        
        Args:
            bill_number: The bill number to check
        
        Returns:
            Status string: "PAID", "PENDING", "OVERDUE", or "NOT_FOUND"
        """
        return self.bill_database.get(bill_number.upper(), "NOT_FOUND")
    
    def provide_bank_information(self, query: str):
        """
        Provide general bank information (simulated RAG system).
        
        Args:
            query: The query about banking
        
        Returns:
            Information from the knowledge base
        """
        query_lower = query.lower()
        
        # Find the most relevant topic
        best_match = None
        best_score = 0
        
        for topic, info_list in self.bank_knowledge_base.items():
            if topic in query_lower:
                # Exact topic match
                best_match = topic
                break
            
            # Partial match scoring
            topic_words = topic.split()
            score = sum(1 for word in topic_words if word in query_lower)
            if score > best_score:
                best_score = score
                best_match = topic
        
        if best_match:
            info = self.bank_knowledge_base[best_match]
            response = f"Regarding {best_match}:\n"
            for item in info:
                response += f"• {item}\n"
            return response.strip()
        else:
            # Fallback to general information
            info = self.bank_knowledge_base["general information"]
            response = "Here's some general information about our bank:\n"
            for item in info:
                response += f"• {item}\n"
            return response.strip()
    
    def is_off_topic(self, message: str):
        """
        Check if a message is off-topic (non-banking).
        
        Args:
            message: The message to check
        
        Returns:
            True if the message is off-topic
        """
        message_lower = message.lower()
        
        # Check for explicit off-topic indicators
        off_topic_indicators = [
            'weather', 'forecast', 'rain', 'sunny', 'cloud', 'temperature', 'sports', 'movie', 'music', 'tv', 'entertainment',
            'recipe', 'cooking', 'travel', 'vacation', 'holiday', 'party',
            'medical', 'health', 'doctor', 'hospital', 'medicine',
            'legal', 'lawyer', 'court', 'lawsuit',
            'political', 'election', 'government', 'president',
            'technical', 'computer', 'software', 'hardware', 'internet',
            'relationship', 'family', 'friend', 'dating',
            'joke', 'funny', 'humor', 'comedy'
        ]
        
        # If message contains off-topic indicators and no banking keywords, it's off-topic
        has_off_topic = any(indicator in message_lower for indicator in off_topic_indicators)
        has_banking = any(keyword in message_lower for keyword in self.BANKING_KEYWORDS)
        
        # Also check for greetings that don't contain banking context
        if has_off_topic and not has_banking:
            return True
        
        # Special case: pure greetings without context
        simple_greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
        if any(greeting in message_lower for greeting in simple_greetings):
            # If it's just a greeting without banking context, wait for next message
            return False  # Not off-topic yet, but might be if next message is off-topic
            
        return False
    
    def process_message(self, human_message: str) -> Tuple[str, Optional[str]]:
        """
        Process a human message using LLM (no fallback to rule-based agent).
        
        Args:
            human_message: The message from the human
        
        Returns:
            Tuple of (response_message, tool_used)
        
        Raises:
            LLMUnavailableError: If LLM is not available or fails.
        """
        # First, check if the message is off-topic using our own detection
        if self.is_off_topic(human_message):
            return "Not my question", None
        
        # Check for bill number in the message
        bill_number = self.extract_bill_number(human_message)
        
        # Check if the human is asking about bill status
        bill_keywords = ['bill', 'invoice', 'payment', 'status', 'check']
        has_bill_keyword = any(keyword in human_message.lower() for keyword in bill_keywords)
        
        if bill_number and has_bill_keyword:
            # Human provided a bill number and is asking about status
            status = self.check_bill_status(bill_number)
            if status == "NOT_FOUND":
                response = f"I couldn't find bill {bill_number} in our system. Please verify the bill number."
            else:
                response = f"The bill {bill_number} is currently {status}."
            return response, "check_bill_status"
        
        elif has_bill_keyword and not bill_number:
            # Human is asking about bill status but didn't provide bill number
            return "I can check your bill status. Could you please provide the bill number?", None
        
        # Check for general banking information requests
        banking_query_keywords = ['what', 'how', 'tell me', 'information', 'explain', 'details']
        has_query_keyword = any(keyword in human_message.lower() for keyword in banking_query_keywords)
        
        if has_query_keyword:
            # This is a general banking information request
            response = self.provide_bank_information(human_message)
            return response, "provide_bank_information"
        
        # At this point, no tool was used, so we use LLM for response
        if not self.llm_client:
            raise LLMUnavailableError("LLM client is not initialized.")
        
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
        
        # Check if LLM response contains an error indicator (from OllamaClient)
        if llm_response.startswith("Error:"):
            raise LLMUnavailableError(f"LLM returned an error: {llm_response}")
        
        # Use LLM response
        return llm_response, None


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