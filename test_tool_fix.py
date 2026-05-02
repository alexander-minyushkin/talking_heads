#!/usr/bin/env python3
"""
Test the tool execution fix.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ollama_integration import LLMEnhancedBankingAgent

def test_bill_status_with_tool():
    """Test that bill status queries execute the tool and return results, not XML."""
    print("Testing bill status tool execution...")
    
    # Create agent with LLM enabled
    agent = LLMEnhancedBankingAgent()
    
    # Test 1: Human asks about bill status with bill number
    print("\nTest 1: Direct bill status query with bill number")
    response, tool = agent.process_message("What's the status of bill INV-2024-001?")
    print(f"Human: What's the status of bill INV-2024-001?")
    print(f"Agent: {response}")
    print(f"Tool used: {tool}")
    
    # Should not contain XML
    assert "<invoke" not in response, f"Response should not contain XML: {response}"
    assert "INV-2024-001" in response, f"Response should mention bill number: {response}"
    assert tool == "check_bill_status", f"Should use check_bill_status tool, got: {tool}"
    
    # Test 2: Human provides bill number after being asked
    print("\nTest 2: Human provides bill number (contextual)")
    # First, agent asks for bill number
    response1, tool1 = agent.process_message("I want to check my bill status")
    print(f"Human: I want to check my bill status")
    print(f"Agent: {response1}")
    
    # Then human provides bill number
    response2, tool2 = agent.process_message("It's INV-2024-002")
    print(f"Human: It's INV-2024-002")
    print(f"Agent: {response2}")
    print(f"Tool used: {tool2}")
    
    # The response should not contain XML
    if "<invoke" in response2:
        print(f"WARNING: Response contains XML: {response2}")
    else:
        print("✓ Response does not contain XML")
    
    # Test 3: Off-topic query
    print("\nTest 3: Off-topic query")
    response, tool = agent.process_message("What's the weather like?")
    print(f"Human: What's the weather like?")
    print(f"Agent: {response}")
    print(f"Tool used: {tool}")
    
    assert response == "Not my question", f"Should detect off-topic, got: {response}"
    assert tool is None, f"Should not use tool for off-topic, got: {tool}"
    
    print("\n✓ All tests completed")
    return True

def main():
    """Run the test."""
    print("=" * 60)
    print("Testing Tool Execution Fix")
    print("=" * 60)
    
    try:
        test_bill_status_with_tool()
        print("\n" + "=" * 60)
        print("Tool execution fix test completed successfully!")
        print("=" * 60)
        return 0
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())