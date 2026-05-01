# Human Simulation: Bill Status Inquiry

## Human Goal
To check the status of a specific bill (bill number: INV-2024-789) and determine if it has been paid.

## Simulation Rules
1. **Start General**: Begin with a general question about bill payments
2. **Reveal Details Only When Asked**: Only provide the bill number if the agent explicitly asks for it
3. **Goal Achievement**: Consider the interaction successful when the agent provides the bill status
4. **Conversation Flow**:
   - Start: Ask a general question about checking bill status
   - If agent asks for bill number: Provide "INV-2024-789"
   - If agent provides status: Thank them and end conversation
   - If agent asks clarifying questions: Answer truthfully but keep responses minimal

## Expected Agent Behavior
- Should ask for the bill number to check status
- Should use the `check_bill_status` tool with the provided bill number
- Should return the status (simulated as "PENDING" for this bill)

## Sample Dialogue
**Human**: "Hello, I'd like to check on a bill payment."
**Agent**: "Sure, I can help with that. Do you have the bill number?"
**Human**: "Yes, it's INV-2024-789."
**Agent**: [Uses tool] "The bill INV-2024-789 is currently PENDING."
**Human**: "Thank you for checking. That's all I needed."
**Outcome**: SUCCESSFUL (human achieved goal)

## Notes
- This simulation tests the agent's ability to handle bill status inquiries
- The agent should recognize this as a banking topic and use the appropriate tool
- If the agent doesn't ask for the bill number within 3 messages, the simulation may need to prompt