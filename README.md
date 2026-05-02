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
- **Automatic Trainer**: Runs simulations and improves agent skills using LLM when unsuccessful

## Project Structure

```
talking_heads/
├── agent/
│   ├── __init__.py
│   ├── banking_agent_skill.md    # Agent skill documentation
│   └── banking_agent.py          # Banking agent implementation
├── human_simulation/
│   ├── __init__.py
│   ├── bill_status_inquiry.md    # Simulation 1: Bill status inquiry
│   ├── mortgage_rate_inquiry.md  # Simulation 2: Mortgage rate inquiry
│   ├── off_topic_weather.md      # Simulation 3: Off-topic weather inquiry
│   ├── account_opening_process.md # Simulation 4: Account opening process
│   └── simulation_logic.py       # Human simulation logic
├── convergent_training_logs/     # Convergent training logs and backups
├── data/                         # Data directory (for future use)
├── logs/                         # Conversation logs
├── training_logs/                # Training cycle logs
├── conversation_manager.py       # Conversation management
├── conversation_runner.py        # Conversation runner engine
├── ollama_integration.py         # Ollama LLM integration
├── trainer.py                    # Agent trainer script
├── trainer_convergent.py         # Convergent trainer script
├── main.py                       # Main CLI entry point
├── test_human_simulation_interaction.py  # Interactive test script
├── HOW_TO_TEST_AGENT.md          # Comprehensive testing guide
├── USING_TEST_SCRIPT.md          # Test script usage guide
├── README.md                     # This file
└── .codeassistantignore          # File ignore patterns
```

### Key Files for Testing:

- **`test_human_simulation_interaction.py`** [[test_human_simulation_interaction]] - Interactive script for manual/automatic agent testing
- **`HOW_TO_TEST_AGENT.md`** [[HOW_TO_TEST_AGENT]] - Comprehensive guide on testing methods
- **`USING_TEST_SCRIPT.md`** [[USING_TEST_SCRIPT]] - Detailed instructions for using the test script
- **`main.py`** - Main CLI utility with `--test` flag for direct agent testing

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

# Interactive test script (manual/automatic modes)
python test_human_simulation_interaction.py
```

### Testing Documentation

For detailed testing instructions, see:
- **[[HOW_TO_TEST_AGENT]]** - Comprehensive testing guide
- **[[USING_TEST_SCRIPT]]** - Test script usage instructions

### Simulation Details

1. **Bill Status Inquiry** (`bill_status`) [[bill_status_inquiry]]
   - Human goal: Check status of bill `INV-2024-789`
   - Tests: Agent's ability to ask for bill number and use `check_bill_status` tool
   - **Key concept**: Human always starts with general bill payment question

1. **Mortgage Rate Inquiry** (`mortgage_rate`) [[mortgage_rate_inquiry]]
   - Human goal: Get information about 30-year fixed mortgage rates
   - Tests: Agent's ability to provide general bank information using `provide_bank_information` tool
   - **Key concept**: Multi-turn conversation with follow-up questions

1. **Off-topic Weather Inquiry** (`off_topic_weather`) [[off_topic_weather]]
   - Human goal: Get agent to correctly identify off-topic question
   - Tests: Agent's off-topic detection (should respond "Not my question")
   - **Key concept**: Tests boundary of banking topics

1. **Account Opening Process** (`account_opening`) [[account_opening_process]]
   - Human goal: Learn about opening a savings account
   - Tests: Agent's ability to handle multi-step inquiries and provide detailed information
   - **Key concept**: Structured conversation with specific information requests

### Testing Documentation Links:
- **[[HOW_TO_TEST_AGENT]]** - Complete testing methodology guide
- **[[USING_TEST_SCRIPT]]** - Interactive test script instructions
- **[[test_human_simulation_interaction]]** - Direct link to test script

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

## Agent Trainer

The system includes an automatic trainer that runs simulations and improves the agent's skills using LLM when conversations are unsuccessful.

### Trainer Features
- **Automatic Simulation Analysis**: Runs all available simulations and analyzes results
- **LLM-Based Improvement**: Uses `minimax-m2.5:cloud` model to generate skill improvements
- **Skill Document Updates**: Automatically updates `agent/banking_agent_skill.md` with improvements
- **Iterative Training**: Can run multiple training cycles to progressively improve the agent
- **Comprehensive Logging**: Saves training results to `training_logs/` directory

### Using the Trainer

```bash
# Run a single training cycle
python trainer.py

# Run multiple training cycles (iterative improvement)
python trainer.py --cycles 3

# Run with custom maximum messages
python trainer.py --max-messages 15

# Use a different Ollama model
python trainer.py --model llama2
```

### How the Trainer Works
1. **Run Simulations**: Executes all human simulation scenarios
2. **Analyze Results**: Identifies unsuccessful conversations and common issues
3. **Generate Improvements**: Uses LLM to analyze failures and suggest skill improvements
4. **Update Agent Skill**: Incorporates improvements into the agent skill document
5. **Save Results**: Logs training cycle results for future reference

### Training Cycle Output
- Creates backup of original skill document before updates
- Saves improvement recommendations as JSON files
- Generates training summary with success rate improvements
- Stores all conversation logs for analysis

## Convergent Trainer (Improved Convergence)

For better training convergence, use the `trainer_convergent.py` script which implements:

### Key Improvements for Convergence:
1. **Direct Code Modification**: Modifies the agent Python code directly instead of just documentation
2. **Immediate Feedback Loop**: Tests updated agent immediately after each modification
3. **Targeted Fixes**: Generates specific code changes addressing exact failure points
4. **Success Rate Tracking**: Monitors improvement across iterations
5. **Backup/Restore**: Saves best-performing agent versions
6. **Rule-based Fallback**: Provides alternative fixes when LLM suggestions fail

### Using the Convergent Trainer:
```bash
# Run convergent training with default parameters
python trainer_convergent.py

# Run with custom parameters
python trainer_convergent.py --iterations 10 --target 0.95 --max-messages 15

# Quick test run
python trainer_convergent.py --iterations 3 --target 0.8
```

### How Convergent Training Works:
1. **Test Current Agent**: Run all simulations to calculate success rate
2. **Analyze Specific Failures**: Identify exact failure patterns in conversations
3. **Generate Targeted Fixes**: Use LLM to create specific code changes
4. **Apply Fixes**: Modify agent code directly
5. **Test Again**: Verify improvements with immediate testing
6. **Iterate**: Repeat until target success rate or max iterations

### Convergence Criteria:
- Target success rate (default: 90%)
- Maximum iterations (default: 10)
- Improvement tracking across iterations
- Automatic restoration of best-performing agent

## Testing Documentation

For comprehensive testing instructions, see these guides:

- **[[HOW_TO_TEST_AGENT]]** - Complete guide to testing methods and approaches
- **[[USING_TEST_SCRIPT]]** - Detailed instructions for using the interactive test script

### Quick Testing Methods:

1. **Interactive Manual Testing** (You as Agent):
   ```bash
   python test_human_simulation_interaction.py
   ```
   - Choose manual mode to practice being the Agent
   - Select from all four simulations
   - Human always starts the conversation first

2. **Direct Agent Testing**:
   ```bash
   python main.py --test
   ```
   - Simple interactive session
   - Type messages as the Agent
   - Type 'quit' or 'exit' to end

3. **Specific Simulation Testing**:
   ```bash
   python main.py --simulation bill_status --interactive
   ```

### Testing Principles:

- **Human always starts first**: The human simulation provides the initial message
- **Goal-oriented**: Each simulation has specific human goals to achieve
- **Success conditions**: Conversation ends when human goal achieved or off-topic detected

### Advanced Testing:

```bash
# Run all simulations (comprehensive test)
python main.py --all

# Test specific functionality
python -c "from agent.banking_agent import BankingAgentImpl; agent = BankingAgentImpl(); print(agent.check_bill_status('INV-2024-001'))"

# Check Ollama integration
python -c "from ollama_integration import OllamaClient; client = OllamaClient(); print('Model available:', client.check_model_available())"

# Run trainer to improve agent skills
python trainer.py --cycles 1
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