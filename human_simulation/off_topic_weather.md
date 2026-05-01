# Human Simulation: Off-topic Weather Inquiry

## Human Goal
To ask about the weather forecast (non-banking topic) to test agent's off-topic detection.

## Simulation Rules
1. **Start General**: Begin with a casual greeting and weather question
2. **No Banking Context**: Do not mention any banking topics
3. **Goal Achievement**: Consider the interaction successful when the agent correctly identifies this as off-topic and responds with "Not my question"
4. **Conversation Flow**:
   - Start: Ask about today's weather
   - If agent responds with banking information: Clarify you're asking about weather
   - If agent says "Not my question": End conversation immediately
   - Do not provide any banking-related details

## Expected Agent Behavior
- Should recognize weather as a non-banking topic
- Should respond with "Not my question" and end the conversation
- Should not attempt to use any banking tools
- Should not ask clarifying questions about banking

## Sample Dialogue
**Human**: "Hi there! Do you know if it's going to rain today?"
**Agent**: "Not my question."
**Outcome**: SUCCESSFUL (agent correctly detected off-topic)

## Alternative Paths
- If agent asks for clarification: "I'm just asking about the weather forecast."
- If agent provides banking information: "No, I meant the actual weather outside."
- Maximum 2 exchanges before expecting off-topic detection

## Notes
- This simulation tests the agent's ability to stay within banking topics
- The agent should not engage with non-banking questions
- Quick detection (within 1-2 messages) is ideal
- This is a test of boundary enforcement