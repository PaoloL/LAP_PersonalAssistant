import os

# Import ChatAnthropic
from langchain_anthropic import ChatAnthropic
from langchain.agents import AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_tool_calling_agent

# Import tools
from tools.langchain_youtrack import list_projects, list_issues_from_project, list_work_items_from_issue, create_work_item
from tools.langchain_timer import get_current_time
from tools.langchain_gcal import get_gcal_events, set_gcal_event

def read_anthropic_token():
    try:
        with open(os.path.expanduser("secrets/anthropic_token.txt"), 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        print("Anthropic token file not found: secrets/anthropic_token.txt")
        exit(1)
        return None

working_tools = [
        list_projects, 
        list_issues_from_project, 
        list_work_items_from_issue, 
        create_work_item, 
        get_current_time,
        get_gcal_events,
        set_gcal_event
    ]

# Set up your LLM to use Claude
anthropic_api_key = read_anthropic_token()
llm = ChatAnthropic(model="claude-3-5-sonnet-20241022", temperature=0, api_key=anthropic_api_key)

# Define the prompt for the agent
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are my personal assistant"
            "You can retrieve project information, issues, and work items from Youtrack"
            "You can also view and set events in my Google Calendar"
            "Use the available tools to support me on execute daily task to improve my work"
            "Always try to provide specific details before to proceed"
        ),

        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

# Create the agent
agent = create_tool_calling_agent(llm, working_tools, prompt)

# Create the AgentExecutor
agent_executor = AgentExecutor(agent=agent, tools=working_tools, verbose=True)

# --- Demonstrate Agent-to-Agent communication (or human interaction) ---
if __name__ == "__main__":
    if "ANTHROPIC_API_KEY" not in os.environ:
        os.environ["ANTHROPIC_API_KEY"] = read_anthropic_token()

    # Example 1: Get all projects
    print("--- Example 1: Get all YouTrack projects ---")
    response = agent_executor.invoke({"input": "List all YouTrack projects.", "chat_history": []})
    print(f"\nAgent's Final Response: {response['output']}")
    print("-" * 50)

    # Example 2: Gell all events of the day
    print("\n--- Example 2: Get all events of today ---")
    response = agent_executor.invoke({"input": "List all events of today planned on my calendar.", "chat_history": []})
    print(f"\nAgent's Final Response: {response['output']}")
    print("-" * 50)

