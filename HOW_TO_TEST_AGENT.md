# How to Test Agent with Human Simulation

This guide explains how to test the banking agent manually by interacting with human simulations.

## Overview

The AI-Agent Testing Utility provides two main testing approaches:

1. **Manual Testing**: You pretend to be the Agent and interact with the Human simulation
2. **Automatic Testing**: The actual BankingAgent interacts with the Human simulation

## Key Concept: Human Always Starts First

In all simulations, the **Human simulation always initiates the conversation**. This is a fundamental design principle:
- The Human simulation provides the initial message via `get_initial_message()`
- The Agent (you or the BankingAgent) responds to this message
- The conversation continues with alternating turns

## Available Simulations

Four human simulations are available:

1. **bill_status** - Human wants to check status of bill INV-2024-789
2. **mortgage_rate** - Human wants information about 30-year fixed mortgage rates  
3. **off_topic_weather** - Human asks about weather to test off-topic detection
4. **account_opening** - Human wants to learn about opening a savings account

## Method 1: Using the Built-in Test Command

The simplest way to test is using the `--test` flag with `main.py`:

```bash
python main.py --test
```

This starts an interactive session where:
- You type messages as if you were the Agent
- The system simulates a Human conversation partner
- Type 'quit' or 'exit' to end

### Example Session:
```
> python main.py --test

Direct Agent Testing Mode
============================================================
Type your messages to the banking agent.
Type 'quit' or 'exit' to end.
Note: Only LLM-enhanced agent is available (no rule-based fallback).
------------------------------------------------------------

You: Hello, how can I help you today?
Agent: I can help with that. Do you have the bill number?
[Tool used: check_bill_status]

You: Yes, it's INV-2024-789
Agent: The bill INV-2024-789 is currently PENDING.
```

## Method 2: Running Specific Simulations

To test with a specific human simulation:

```bash
# List all available simulations
python main.py --list

# Run a specific simulation
python main.py --simulation bill_status

# Run in interactive mode (pause between messages)
python main.py --simulation bill_status --interactive

# Run all simulations in batch mode
python main.py --all
```

## Method 3: Manual Testing as Agent (Pretending to be Agent)

If you want to manually test how you would respond as an Agent:

### Step-by-Step Process:

1. **Initialize the Human Simulation**:
   ```python
   from human_simulation.simulation_logic import SimulationFactory
   
   factory = SimulationFactory()
   simulation = factory.create_simulation("bill_status")
   ```

2. **Get the Human's Initial Message**:
   ```python
   human_message = simulation.get_initial_message()
   print(f"HUMAN: {human_message}")
   ```

3. **Respond as the Agent**:
   ```python
   # You type your response
   agent_response = "I can help with that. Do you have the bill number?"
   ```

4. **Get Human's Response**:
   ```python
   human_response, goal_achieved = simulation.respond(agent_response)
   print(f"HUMAN: {human_response}")
   ```

5. **Continue the Conversation**:
   - Keep responding as the Agent
   - The Human simulation will respond based on your messages
   - The conversation ends when the Human's goal is achieved

### Example Conversation Flow:

```
HUMAN: Hello, I'd like to check on a bill payment.
AGENT (you): I can help with that. Do you have the bill number?
HUMAN: Yes, it's INV-2024-789.
AGENT (you): The bill INV-2024-789 is currently PENDING.
HUMAN: Thank you for checking. That's all I needed.
>>> Human achieved their goal. Conversation ended.
```

## Method 4: Using the Test Script

I've created a test script that provides an interactive interface:

```bash
python test_human_simulation_interaction.py
```

This script offers:
- Choice of simulation
- Manual mode (you as Agent)
- Automatic mode (real BankingAgent)
- Clear conversation display

## Understanding Human Simulation Logic

Each human simulation has specific goals and response patterns:

### Bill Status Simulation
- **Goal**: Get bill status for INV-2024-789
- **Pattern**: Waits for you to ask for bill number, then provides it
- **Success**: When you provide status (pending, paid, overdue)

### Mortgage Rate Simulation  
- **Goal**: Get mortgage rate information for 30-year fixed mortgage
- **Pattern**: Waits for you to ask about mortgage type
- **Success**: When you provide rate information and answer one follow-up question

### Off-topic Weather Simulation
- **Goal**: Get agent to correctly identify this as off-topic
- **Pattern**: Asks about weather repeatedly
- **Success**: When you say "Not my question" (off-topic detection)

### Account Opening Simulation
- **Goal**: Get complete information about savings account opening process
- **Pattern**: Asks about account type → documents → timeframe
- **Success**: When all three pieces of information are provided

## Tips for Effective Testing

1. **Start with the bill_status simulation** - it's the simplest and most predictable
2. **Use the --interactive flag** to pause between messages and think about responses
3. **Check the simulation's goal** to understand what the Human wants to achieve
4. **Look for keywords** that trigger specific Human responses
5. **Test edge cases** like off-topic questions or incomplete information

## Common Testing Scenarios

### Scenario 1: Testing Bill Status Inquiry
```bash
python main.py --simulation bill_status --interactive
```

### Scenario 2: Testing Off-topic Detection
```bash
python main.py --simulation off_topic_weather
```

### Scenario 3: Testing Complete Conversation Flow
```bash
python main.py --all --max-messages 20
```

## Debugging Tips

If the conversation isn't progressing as expected:

1. **Check the Human's goal**: `print(simulation.goal)`
2. **Check if goal is achieved**: `print(simulation.is_goal_achieved())`
3. **Review conversation history**: The system saves logs in the `logs/` directory
4. **Increase message limit**: Use `--max-messages 20` for longer conversations

## Conclusion

Testing the agent with human simulations involves understanding that:
1. The Human always starts the conversation
2. Each simulation has specific goals and response patterns
3. You can test manually (as the Agent) or automatically (using the BankingAgent)
4. The `--test` flag provides the simplest interactive testing experience

Use the provided tools and scripts to thoroughly test agent behavior across different scenarios.