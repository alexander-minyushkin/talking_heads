# Human Simulation: Account Opening Process Inquiry

## Human Goal
To learn about the process for opening a new savings account, including required documents and timeframes.

## Simulation Rules
1. **Start General**: Begin with a general question about opening accounts
2. **Reveal Details Gradually**: Only specify "savings account" if asked; start with general account opening
3. **Goal Achievement**: Consider the interaction successful when the agent provides comprehensive information about the savings account opening process
4. **Conversation Flow**:
   - Start: Ask about opening a new account
   - If agent asks what type: Specify savings account
   - Ask about required documents
   - Ask about processing time
   - Thank and end when satisfied

## Expected Agent Behavior
- Should recognize this as a banking topic
- Should use the `provide_bank_information` tool for account opening procedures
- Should ask clarifying questions about account type
- Should provide step-by-step information

## Sample Dialogue
**Human**: "I'm interested in opening a new account. Can you tell me about the process?"
**Agent**: "Certainly. What type of account are you interested in opening?"
**Human**: "A savings account."
**Agent**: [Uses tool] "To open a savings account, you'll need to provide identification, proof of address, and an initial deposit. The process can be completed online or in-branch."
**Human**: "What documents are typically required?"
**Agent**: [Provides document list]
**Human**: "How long does it take to open the account?"
**Agent**: [Provides timeframe]
**Human**: "Thank you, that answers all my questions."
**Outcome**: SUCCESSFUL (human obtained complete information)

## Notes
- This simulation tests the agent's ability to handle multi-step inquiries
- The agent should provide detailed, accurate information
- May require 3-4 message exchanges to achieve goal
- Tests the agent's patience and thoroughness