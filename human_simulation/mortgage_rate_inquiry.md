# Human Simulation: Mortgage Rate Inquiry

## Human Goal
To get information about current mortgage rates for a 30-year fixed mortgage.

## Simulation Rules
1. **Start General**: Begin with a general question about mortgage options
2. **Reveal Details Only When Asked**: Only specify "30-year fixed" if the agent asks for clarification
3. **Goal Achievement**: Consider the interaction successful when the agent provides relevant mortgage rate information
4. **Conversation Flow**:
   - Start: Ask about mortgage rates in general
   - If agent asks for specifics: Mention interest in a 30-year fixed mortgage
   - If agent provides information: Ask one follow-up question about the application process
   - Then thank them and end conversation

## Expected Agent Behavior
- Should recognize this as a banking topic
- Should use the `provide_bank_information` tool with mortgage rate query
- Should provide accurate information about current rates
- May ask clarifying questions about mortgage type

## Sample Dialogue
**Human**: "I'm thinking about buying a house and wanted to know about mortgage rates."
**Agent**: "I can help with that. Are you looking for a fixed or adjustable rate mortgage?"
**Human**: "I'm interested in a fixed rate mortgage."
**Agent**: [Uses tool] "Our current 30-year fixed mortgage rates range from 3.5% to 4.2% depending on credit score and down payment."
**Human**: "What's the typical application process like?"
**Agent**: [Provides information]
**Human**: "Thank you, that's very helpful."
**Outcome**: SUCCESSFUL (human obtained needed information)

## Notes
- This simulation tests the agent's ability to provide general bank information
- The agent should use the RAG system tool for mortgage rate information
- The simulation may include 2-3 exchanges before goal achievement