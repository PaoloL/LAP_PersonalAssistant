# LAP Personal Assistant

A multi-agent personal assistant system built with LangGraph that manages calendar events and YouTrack issues through conversational AI.

## Installation and Setup

### Prerequisites
- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager

### Install with uv

```bash
# Clone the repository
git clone <repository-url>
cd LAP_PersonalAssistant

# Install dependencies
uv sync

# Set up environment variables
chmod +x set_env.sh
./set_env.sh
```

### Configuration
1. Add your API credentials to the `secrets/` directory:
   - `anthropic_token.txt` - Anthropic API key
   - `yt_token.txt` - YouTrack token
   - `credentials.json` - Google Calendar credentials
   - `token.json` - Google Calendar token

### Run the Application

```bash
# Activate virtual environment and run
uv run python main_business.py
```

## LangGraph Utilization

This project leverages **LangGraph** to create a hierarchical multi-agent system:

### Architecture
- **Main Supervisor**: Routes user requests to appropriate specialized agents
- **Agent Nodes**: Individual agents (Calendar Manager, YouTrack Manager) handle specific tasks
- **State Management**: Shared `AgentState` tracks conversation flow and agent outputs

### Key LangGraph Features Used
- `StateGraph`: Manages agent workflow and state transitions
- `create_react_agent`: Creates ReAct-pattern agents with tool access
- `InMemorySaver`: Provides conversation checkpointing
- Conditional edges for dynamic agent routing

### Workflow
1. User input → Main Supervisor
2. LLM-based agent selection
3. Specialized agent execution
4. Tool invocation (Calendar/YouTrack APIs)
5. Response aggregation

## Adding a New Agent

### 1. Create Agent File
Create `agents/new_agent_manager.py`:

```python
from langgraph.prebuilt import create_react_agent
from langchain_aws import ChatBedrock
from agent_state import AgentState
from tools.base_tools import BASE_TOOLS

def conversational_new_agent(state: AgentState):
    print("NEW AGENT: Hello, I'm the New Agent")
    
    # Load prompt
    with open("prompts/new_agent_prompt.txt", 'r') as f:
        prompt = f.read().strip()
    
    # Configure LLM
    llm = ChatBedrock(
        model_id="eu.anthropic.claude-3-7-sonnet-20250219-v1:0",
        model_kwargs={"temperature": 0}
    )
    
    # Add agent-specific tools
    tools = [your_custom_tools] + BASE_TOOLS
    
    # Create agent
    agent = create_react_agent(llm, tools, prompt)
    
    # Conversation loop
    while True:
        request = input("YOU: ").strip()
        if request.lower() in ['exit', 'quit', 'bye']:
            break
        response = agent.invoke({"messages": [{"role": "user", "content": request}]})
        print("NEW AGENT:", response["messages"][-1].content)
```

### 2. Create Agent Prompt
Add `prompts/new_agent_prompt.txt` with agent-specific instructions.

### 3. Update Main Supervisor
In `main_business.py`:

```python
# Import new agent
from agents.new_agent_manager import conversational_new_agent

# Add to supervisor prompt
"- NewAgentManager: for new agent tasks"

# Add to valid teams
valid_teams = ["YoutrackManager", "CalendarManager", "NewAgentManager"]

# Add node to graph
main_workflow.add_node("new_agent_node", conversational_new_agent)

# Add routing
"NewAgentManager": "new_agent_node"

# Add edge
main_workflow.add_edge("new_agent_node", END)
```

### 4. Create Custom Tools (Optional)
Add tools in `tools/new_agent_tools.py` following the existing pattern.

## Project Structure

```
LAP_PersonalAssistant/
├── agents/           # Agent implementations
├── tools/            # Tool definitions
├── prompts/          # Agent prompts
├── utils/            # Utility functions
├── secrets/          # API credentials
├── main_business.py  # Main application
└── agent_state.py    # Shared state definition
```