import logging
import time
from agent_state import AgentState # Import AgentState from the common file

from langgraph.graph import StateGraph, END
from langchain_aws import ChatBedrock
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent

from tools.langchain_youtrack import list_active_projects, list_issues_from_project, list_work_items_from_issue, create_work_item
from tools.langchain_gcal import get_gcal_events, set_gcal_event
from tools.base_tools import BASE_TOOLS

# Suppress verbose error logging
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('langchain_aws').setLevel(logging.CRITICAL)

def load_prompt(filename):
        try:
            with open(f"prompts/{filename}", 'r') as file:
                return file.read().strip()
        except FileNotFoundError as e:
            print(f"File not found error: error {str(e)}")
            return 

def recube_youtrack_assistant(state: AgentState):
    print("Invoking Recube YouTrack Assistant...")

    try:
        llm = ChatBedrock(
            model_id="eu.anthropic.claude-3-7-sonnet-20250219-v1:0",
            model_kwargs={"temperature": 0},
            streaming=False
        )

        user_input = state["input"]
        
        YOUTRACK_UPDATE_PREDEFINED_PROMPT = load_prompt("update_youtrack.txt")
        current_tools = [get_gcal_events, list_active_projects, list_issues_from_project, list_work_items_from_issue, create_work_item] + BASE_TOOLS

        agent = create_react_agent(
            model=llm, 
            tools=current_tools,
            prompt=YOUTRACK_UPDATE_PREDEFINED_PROMPT,
            name="recube_youtrack_assistant",
            checkpointer=None
        )
        
        response = agent.invoke(
            {"messages": [{"role": "user", "content": user_input}]}
        )

        for message in reversed(response["messages"]):
            if hasattr(message, 'content') and message.content.strip():
                return {"agent_output": message.content, "path": ["recube_youtrack_assistant"]}
        return {"agent_output": "No response generated", "path": ["recube_youtrack_assistant"]}
    
    except Exception as e:
        return {"agent_output": f"Error: {str(e)}", "path": ["recube_calendar_assistant"]}

def recube_calendar_assistant(state: AgentState):
    print("Invoking Recube Calendar Assistant...")
    
    CALENDAR_PREDEFINED_PROMPT = load_prompt("flexible_calendar.txt")

    try:

        llm = ChatBedrock(
            model_id="eu.anthropic.claude-3-7-sonnet-20250219-v1:0",
            model_kwargs={"temperature": 0},
            streaming=False
        )

        current_tools = [get_gcal_events, set_gcal_event] + BASE_TOOLS

        agent = create_react_agent(
            model=llm, 
            tools=current_tools,
            prompt=CALENDAR_PREDEFINED_PROMPT,
            name="recube_calendar_assistant",
            checkpointer=None
        )

        user_input = state["input"]
        
        # Run the agent
        response = agent.invoke(
            {"messages": [{"role": "user", "content": user_input}]}
        )
        for message in reversed(response["messages"]):
            if hasattr(message, 'content') and message.content.strip():
                return {"agent_output": message.content, "path": ["recube_calendar_assistant"]}
        return {"agent_output": "No response generated", "path": ["recube_calendar_assistant"]}
            
    except Exception as e:
        return {"agent_output": f"Error: {str(e)}", "path": ["recube_calendar_assistant"]}

# Define Supervisor Agent for Recube team (Dynamic Control Flow)
def recube_supervisor(state: AgentState):
    print("Recube Assistant Supervisor deciding within Recube Team...")
    
    try:
        user_input = state["input"]

        llm = ChatBedrock(
            model_id="eu.anthropic.claude-3-7-sonnet-20250219-v1:0",
            model_kwargs={"temperature": 0},
            streaming=False
        )

        # Create prompt for agent selection
        prompt = ChatPromptTemplate.from_messages([
            ("system", 
             "Choose the appropriate agent based on user input:\n"
             "- YoutrackAssistant: for YouTrack, issues, work items\n"
             "- CalendarAssistant: for calendar, meetings, scheduling\n"
             "Respond with ONLY the agent name."),
            ("human", user_input)
        ])

        chain = prompt | llm
        response = chain.invoke({"input": user_input})
        next_agent_to_invoke = response.content.strip()

        # Validate LLM response
        valid_agents = ["YoutrackAssistant", "CalendarAssistant"]
        if next_agent_to_invoke not in valid_agents:
            next_agent_to_invoke = "YoutrackAssistant"

        print(f"Recube Supervisor chose: {next_agent_to_invoke}")
        return {"next_agent": next_agent_to_invoke, "path": ["recube_supervisor"]}
        
    except Exception as e:
        print(f"Recube Supervisor: error {str(e)}")
        return {"next_agent": "recube_youtrack_assistant", "path": ["recube_supervisor"]}

# Define the Sub-graph for the Recube team
def create_recube_team_graph():
    recube_workflow = StateGraph(AgentState)
    recube_workflow.add_node("recube_supervisor", recube_supervisor)
    recube_workflow.add_node("recube_youtrack_assistant", recube_youtrack_assistant)
    recube_workflow.add_node("recube_calendar_assistant", recube_calendar_assistant)

    recube_workflow.set_entry_point("recube_supervisor")

    recube_workflow.add_conditional_edges(
        "recube_supervisor",
        lambda state: state["next_agent"],
        {
            "YoutrackAssistant": "recube_youtrack_assistant",
            "CalendarAssistant": "recube_calendar_assistant",
        }
    )
    recube_workflow.add_edge("recube_youtrack_assistant", END)
    recube_workflow.add_edge("recube_calendar_assistant", END)

    return recube_workflow.compile(checkpointer=None)