# Using test_human_simulation_interaction.py

This guide explains how to use the custom test script I created for manual agent testing with human simulations.

## Overview

`test_human_simulation_interaction.py` is an interactive Python script that provides two testing modes:
1. **Manual Mode**: You pretend to be the Agent and type responses
2. **Automatic Mode**: The actual BankingAgent interacts with the human simulation

## Quick Start

```bash
python test_human_simulation_interaction.py
```

## Features

- **Interactive menu system** with clear options
- **All four simulations** available for testing
- **Clear conversation display** with role labels
- **Goal tracking** shows when human achieves their goal
- **User-friendly interface** with prompts and instructions

## Modes Explained

### 1. Manual Testing Mode (You as Agent)

In this mode, **you act as the Agent** and type responses to the human simulation.

**How it works:**
1. Select a simulation from the list
2. The human simulation provides the initial message (always starts first)
3. You type your response as the Agent
4. The human simulation responds based on your message
5. Conversation continues until human goal is achieved or you quit

**Example session:**
```
Select simulation number (1-4) or 'q' to quit: 1

Starting simulation: Bill Status Inquiry
Human Goal: Get bill status for INV-2024-789

CONVERSATION START
======================================================================

HUMAN: Hello, I'd like to check on a bill payment.

AGENT (you): I can help with that. Do you have the bill number?

HUMAN: Yes, it's INV-2024-789.

AGENT (you): The bill INV-2024-789 is currently PENDING.

HUMAN: Thank you for checking. That's all I needed.

>>> Human achieved their goal. Conversation ended.

CONVERSATION END
======================================================================
```

### 2. Automatic Testing Mode (Real Agent)

In this mode, the **actual BankingAgent** interacts with the human simulation.

**How it works:**
1. Script automatically selects the "bill_status" simulation
2. Shows how the real BankingAgent would respond
3. Demonstrates tool usage and agent logic
4. Runs for up to 3 conversation turns

**Example output:**
```
AUTOMATIC AGENT TESTING - Using BankingAgentImpl
======================================================================

Simulation: Bill Status Inquiry
Human Goal: Get bill status for INV-2024-789

CONVERSATION START
======================================================================

HUMAN: Hi, can you help me with a bill status inquiry?

AGENT: I can help with that. Do you have the bill number?
       [Tool used: check_bill_status]

HUMAN: Yes, it's INV-2024-789.

AGENT: The bill INV-2024-789 is currently PENDING.
       [Tool used: check_bill_status]

CONVERSATION END
======================================================================
```

## Available Simulations

When you select Manual Mode, you can choose from:

1. **bill_status** - Human wants to check status of bill INV-2024-789
   - Goal: Get bill status information
   - Best for: Testing basic agent responses

2. **mortgage_rate** - Human wants information about 30-year fixed mortgage rates
   - Goal: Get mortgage rate information
   - Best for: Testing multi-turn conversations

3. **off_topic_weather** - Human asks about weather to test off-topic detection
   - Goal: Get agent to identify this as off-topic
   - Best for: Testing "Not my question" response

4. **account_opening** - Human wants to learn about opening a savings account
   - Goal: Get complete account opening information
   - Best for: Testing complex multi-step conversations

## Command Line Options

The script runs interactively, but you can also use it programmatically:

```python
# Import and use specific functions
from test_human_simulation_interaction import test_as_agent_manual, test_with_real_agent

# Run manual test with specific simulation
test_as_agent_manual()  # Will prompt for simulation choice

# Run automatic test
test_with_real_agent()  # Uses bill_status simulation
```

## Tips for Effective Testing

### For Manual Mode:
1. **Read the human's goal** - Understand what they want to achieve
2. **Use appropriate keywords** - Simulations respond to specific phrases
3. **Be concise** - Clear, direct responses work best
4. **Check for goal achievement** - The script will tell you when human is satisfied

### For Automatic Mode:
1. **Observe tool usage** - See which tools the agent uses
2. **Note response patterns** - Understand how the agent structures responses
3. **Compare with manual responses** - See how your responses differ from the agent's

## Common Use Cases

### Use Case 1: Learning Agent Behavior
```bash
# Run automatic mode to see how the real agent works
python test_human_simulation_interaction.py
# Choose option 2 (Automatic testing)
```

### Use Case 2: Practicing as Agent
```bash
# Run manual mode to practice being an agent
python test_human_simulation_interaction.py
# Choose option 1 (Manual testing)
# Select simulation 1 (bill_status) for simplest practice
```

### Use Case 3: Testing Specific Scenarios
```bash
# Run the script multiple times with different simulations
python test_human_simulation_interaction.py
# Choose option 1, then:
# - Select 1 for bill status testing
# - Select 3 for off-topic detection testing
# - Select 4 for complex multi-step testing
```

## Keyboard Shortcuts

During conversation:
- **Type your response** and press Enter to send
- **Type 'quit', 'exit', or 'q'** to end conversation early
- **Press Ctrl+C** to interrupt and return to main menu

## Integration with Main Testing Framework

This script complements the main testing framework (`main.py`):

| Feature | `main.py --test` | `test_human_simulation_interaction.py` |
|---------|------------------|----------------------------------------|
| Simulation choice | Fixed (generic) | Interactive selection |
| Testing modes | Manual only | Manual + Automatic |
| Conversation display | Basic | Enhanced with labels |
| Goal tracking | Limited | Explicit goal achievement messages |
| Learning focus | Testing agent | Learning agent behavior |

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'human_simulation'"
**Solution:** Run from the project root directory:
```bash
cd c:/Users/alexa/Documents/projects/talking_heads
python test_human_simulation_interaction.py
```

### Issue: Script exits immediately
**Solution:** Make sure you have Python 3.7+ installed:
```bash
python --version
```

### Issue: Input not working in VS Code terminal
**Solution:** Use the system terminal or ensure VS Code terminal is in interactive mode.

## Example Test Scenarios

### Scenario 1: Testing Bill Status Response
1. Run script: `python test_human_simulation_interaction.py`
2. Choose option 1 (Manual testing)
3. Select simulation 1 (bill_status)
4. When human asks about bill payment, respond: "I can help with that. Do you have the bill number?"
5. When human provides bill number, respond: "The bill INV-2024-789 is currently PENDING."

### Scenario 2: Testing Off-topic Detection
1. Run script, choose manual mode
2. Select simulation 3 (off_topic_weather)
3. When human asks about weather, respond: "Not my question"
4. Observe that conversation ends with off-topic detection

### Scenario 3: Comparing Your Response with Agent
1. Run automatic mode (option 2) to see agent's response
2. Run manual mode (option 1) with same simulation
3. Compare your responses with the agent's responses
4. Note differences in approach and tool usage

## Conclusion

The `test_human_simulation_interaction.py` script provides a user-friendly way to:
- Practice being an agent in manual mode
- Observe real agent behavior in automatic mode
- Test all four human simulations
- Learn agent response patterns and tool usage

It's particularly useful for understanding how to interact with human simulations when you're pretending to be the agent.