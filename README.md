# AI-Agent Testing Utility - Banking Agent Simulator

A command-line utility to test AI-Agent by simulating its interaction with human simulations. The system includes a banking agent with specialized tools and multiple human simulation scenarios.

## Features

- **Banking Agent** with 2 specialized tools:
  - `check_bill_status`: Checks status of bills when bill number is provided
  - `provide_bank_information`: Provides general bank information using simulated RAG system
- **Human Simulations**: 4 different simulation scenarios with specific goals
- **Success/Failure Conditions**:
  - SUCCESSFUL: Human achieves goal OR agent detects off-topic question
  - UNSUCCESSFUL: Conversation reaches 10 total messages without resolution
- **Ollama Integration**: Optional LLM enhancement using `minimax-m2.5:cloud` model
- **Comprehensive Logging**: All conversations saved to JSON files in `logs/` directory

## Project Structure

```
talking_heads/
├── agent/
│   ├── __init__.py
│   ├── banking_agent_skill.md    # Agent skill documentation
│   └── banking_agent.py          # Banking agent implementation
├── human-simulation/
│   ├── __init__.py
│   ├── bill_status_inquiry.md    # Simulation 1: Bill status inquiry
│   ├── mortgage_rate_inquiry.md  # Simulation 2: Mortgage rate inquiry
│   ├── off_topic_weather.md      # Simulation 3: Off-topic weather inquiry
│   ├── account_opening_process.md # Simulation 4: Account opening process
│   └── simulation_logic.py       # Human simulation logic
├── data/                         # Data directory (for future use)
├── logs/                         # Conversation logs
├── conversation_manager.py       # Conversation management
├── conversation_runner.py        # Conversation runner engine
├── ollama_integration.py         # Ollama LLM integration
├── main.py                       # Main CLI entry point
└── README.md                     # This file
```

## Installation

1. **Clone or create the project structure**
   ```bash
   # The project is already set up with the required folders
   ```

2. **Install Python dependencies** (if any - currently none required)
   ```bash
   # No external dependencies beyond Python standard library
   ```

3. **Install Ollama** (optional, for LLM enhancement)
   ```bash
   # Download from https://ollama.com/
   # Pull the required model:
   ollama pull minimax-m2.5:cloud
   ```

## Usage

### Basic Commands

```bash
# Show help and list simulations
python main.py --help

# List all available simulations
python main.py --list

# Run a specific simulation
python main.py --simulation bill_status
python main.py --simulation mortgage_rate
python main.py --simulation off_topic_weather
python main.py --simulation account_opening

# Run all simulations
python main.py --all

# Test agent directly with user input
python main.py --test

# Use LLM-enhanced agent
python main.py --test --llm
```

### Simulation Details

1. **Bill Status Inquiry** (`bill_status`)
   - Human goal: Check status of bill `INV-2024-789`
   - Tests: Agent's ability to ask for bill number and use `check_bill_status` tool

2. **Mortgage Rate Inquiry** (`mortgage_rate`)
   - Human goal: Get information about 30-year fixed mortgage rates
   - Tests: Agent's ability to provide general bank information using `provide_bank_information` tool

3. **Off-topic Weather Inquiry** (`off_topic_weather`)
   - Human goal: Get agent to correctly identify off-topic question
   - Tests: Agent's off-topic detection (should respond "Not my question")

4. **Account Opening Process** (`account_opening`)
   - Human goal: Learn about opening a savings account
   - Tests: Agent's ability to handle multi-step inquiries and provide detailed information

### Advanced Options

```bash
# Run with custom maximum messages (default: 10)
python main.py --simulation bill_status --max-messages 15

# Run in interactive mode (pause between messages)
python main.py --simulation mortgage_rate --interactive

# Run all simulations with LLM enhancement
python main.py --all --llm

# Test LLM-enhanced agent directly
python main.py --test --llm
```

## Agent Capabilities

### Banking Topics (In-scope)
- Account management and opening
- Bill payments and status inquiries
- Loan applications and rates (mortgage, personal, auto)
- Credit cards and interest rates
- Bank policies and procedures
- Branch locations and hours
- Online banking features
- Investment products

### Non-Banking Topics (Out-of-scope)
- Weather, sports, entertainment
- Personal advice (medical, legal, etc.)
- Technical support for non-banking apps
- Political discussions
- Any topic not directly related to banking

### Agent Response Protocol
1. **Banking Questions**: Use appropriate tools to provide accurate information
2. **Incomplete Information**: Ask clarifying questions (e.g., "Could you provide the bill number?")
3. **Off-topic Detection**: If a question is clearly non-banking, respond with "Not my question" and end conversation
4. **Success Criteria**: Conversation ends successfully when:
   - Human achieves their banking goal
   - Agent detects off-topic question

## Success/Failure Conditions

The system evaluates conversations based on these rules:

| Condition | Outcome | Description |
|-----------|---------|-------------|
| Human achieves goal | SUCCESSFUL | Human simulation reports goal achieved |
| Agent detects off-topic | SUCCESSFUL | Agent responds "Not my question" |
| 10 total messages reached | UNSUCCESSFUL | Conversation exceeds maximum without resolution |

## LLM Integration

The system supports optional LLM enhancement using Ollama with the `minimax-m2.5:cloud` model:

```bash
# Check if Ollama is available
python main.py --test --llm

# The system will automatically:
# 1. Check if model is available
# 2. Fall back to rule-based agent if not
# 3. Use LLM for enhanced responses when appropriate
```

### LLM vs Rule-based Agent
- **Rule-based**: Fast, deterministic, follows strict rules
- **LLM-enhanced**: More natural responses, better handling of edge cases
- **Hybrid**: Uses rule-based for tool selection and off-topic detection, LLM for response generation

## Output and Logging

All conversations are saved to the `logs/` directory with timestamps:

```
logs/
├── conversation_bill_status_20260101_120000.json
├── conversation_mortgage_rate_20260101_120100.json
└── batch_results_20260101_120200.json
```

Each log file contains:
- Conversation metadata (outcome, message count, duration)
- Complete message history with roles and tools used
- Human goal and success reason

## Extending the System

### Adding New Simulations

1. Create a new MD file in `human-simulation/` describing the simulation
2. Implement the simulation logic in `simulation_logic.py`:
   ```python
   class NewSimulation(HumanSimulation):
       def __init__(self):
           super().__init__(name="New Simulation", description="...", goal="...")
       
       def get_initial_message(self) -> str:
           return "Initial message"
       
       def respond(self, agent_message: str) -> Tuple[str, bool]:
           # Logic here
           return "Response", goal_achieved
   ```
3. Add to `SimulationFactory` in `simulation_logic.py`

### Adding New Agent Tools

1. Update `agent/banking_agent.py`:
   ```python
   def new_tool(self, parameters):
       # Tool implementation
       return result
   ```
2. Update tool detection logic in `process_message()`
3. Update agent skill documentation in `agent/banking_agent_skill.md`

## Testing

Run the test suite:

```bash
# Run all simulations (comprehensive test)
python main.py --all

# Test specific functionality
python -c "from agent.banking_agent import BankingAgentImpl; agent = BankingAgentImpl(); print(agent.check_bill_status('INV-2024-001'))"

# Check Ollama integration
python -c "from ollama_integration import OllamaClient; client = OllamaClient(); print('Model available:', client.check_model_available())"
```

## Troubleshooting

### Common Issues

1. **"Model not available" error**
   ```bash
   # Pull the required model
   ollama pull minimax-m2.5:cloud
   
   # Or use rule-based agent only
   python main.py --simulation bill_status  # No --llm flag
   ```

2. **Ollama not running**
   ```bash
   # Start Ollama service
   ollama serve
   # In another terminal, run your command
   ```

3. **Import errors**
   ```bash
   # Ensure you're in the correct directory
   cd c:/Users/alexa/Documents/projects/talking_heads
   
   # Check Python path
   python -c "import sys; print(sys.path)"
   ```

4. **Permission errors**
   ```bash
   # Ensure logs directory is writable
   mkdir -p logs
   ```

## License

This project is created for testing and educational purposes.

## Acknowledgments

- Uses Ollama for LLM integration (optional)
- Designed for AI-Agent testing and evaluation
- Implements realistic banking conversation scenarios