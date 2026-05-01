#!/usr/bin/env python3
"""
Banking Agent implementation with tools for bill status and bank information.
"""

import re
import random
from typing import Dict, List, Optional, Tuple, Any
from conversation_manager import BankingAgent


class BankingAgentImpl(BankingAgent):
    """Concrete implementation of a banking agent with two tools."""
    
    # Banking keywords to identify on-topic conversations
    BANKING_KEYWORDS = [
        'bank', 'account', 'loan', 'mortgage', 'credit', 'debit', 'bill', 'payment',
        'transfer', 'deposit', 'withdrawal', 'balance', 'statement', 'fee', 'interest',
        'rate', 'savings', 'checking', 'investment', 'card', 'atm', 'branch', 'online',
        'banking', 'finance', 'financial', 'money', 'cash', 'check', 'wire', 'ach',
        'overdraft', 'insurance', 'retirement', 'ira', '401k', 'cd', 'certificate',
        'application', 'approval', 'document', 'id', 'verification', 'authentication'
    ]
    
    # Bill number patterns
    BILL_PATTERNS = [
        r'INV-\d{4}-\d{3}',  # INV-2024-001
        r'BILL-\d{6}',        # BILL-123456
        r'\d{10}',            # 1234567890
        r'[A-Z]{3}-\d{5}',    # ABC-12345
    ]
    
    def __init__(self, name: str = "Banking Assistant"):
        """
        Initialize the banking agent.
        
        Args:
            name: Name of the agent
        """
        super().__init__(name)
        self.bill_database = self._initialize_bill_database()
        self.bank_knowledge_base = self._initialize_knowledge_base()
        
    def _initialize_bill_database(self) -> Dict[str, str]:
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
    
    def _initialize_knowledge_base(self) -> Dict[str, List[str]]:
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
    
    def is_off_topic(self, message: str) -> bool:
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
            'weather', 'sports', 'movie', 'music', 'tv', 'entertainment',
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
    
    def extract_bill_number(self, message: str) -> Optional[str]:
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
    
    def check_bill_status(self, bill_number: str) -> str:
        """
        Check the status of a bill.
        
        Args:
            bill_number: The bill number to check
            
        Returns:
            Status string: "PAID", "PENDING", "OVERDUE", or "NOT_FOUND"
        """
        return self.bill_database.get(bill_number.upper(), "NOT_FOUND")
    
    def provide_bank_information(self, query: str) -> str:
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
    
    def process_message(self, human_message: str) -> Tuple[str, Optional[str]]:
        """
        Process a human message and generate a response.
        
        Args:
            human_message: The message from the human
            
        Returns:
            Tuple of (response_message, tool_used)
        """
        # First check if the message is off-topic
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
        
        # Default response for other banking-related messages
        default_responses = [
            "I'm here to help with your banking needs. How can I assist you today?",
            "I specialize in banking topics. What would you like to know about?",
            "I can help with bill payments, account information, loans, and other banking services. What do you need assistance with?",
        ]
        
        return random.choice(default_responses), None
    
    def ask_clarification(self, missing_info: str) -> str:
        """
        Ask a clarification question.
        
        Args:
            missing_info: What information is missing
            
        Returns:
            Clarification question
        """
        clarification_questions = {
            "bill_number": "Could you please provide the bill number?",
            "account_type": "What type of account are you referring to?",
            "loan_type": "What type of loan are you interested in?",
            "amount": "Could you specify the amount?",
            "timeframe": "What timeframe are you looking at?",
            "general": "Could you please provide more details so I can better assist you?",
        }
        
        return clarification_questions.get(missing_info, clarification_questions["general"])


# Example usage
if __name__ == "__main__":
    agent = BankingAgentImpl()
    
    # Test cases
    test_messages = [
        "Can you check the status of bill INV-2024-001?",
        "What are your mortgage rates?",
        "How do I open a savings account?",
        "What's the weather like today?",
        "I need help with a bill payment.",
    ]
    
    for msg in test_messages:
        print(f"\nHuman: {msg}")
        response, tool = agent.process_message(msg)
        print(f"Agent: {response}")
        if tool:
            print(f"Tool used: {tool}")
        print(f"Off-topic: {agent.is_off_topic(msg)}")