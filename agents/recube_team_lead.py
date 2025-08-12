import logging
import time
from agent_state import AgentState # Import AgentState from the common file

from langgraph.graph import StateGraph, END
from langchain_aws import ChatBedrock
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_tool_calling_agent

from tools.langchain_youtrack import list_projects, list_issues_from_project, create_work_item
from tools.langchain_gcal import get_gcal_events, set_gcal_event
from tools.base_tools import BASE_TOOLS

# Suppress verbose error logging
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('langchain_aws').setLevel(logging.CRITICAL)

def load_prompt(filename):
        try:
            with open(f"prompts/{filename}", 'r') as file:
                return file.read().strip()
        except FileNotFoundError:
            return ""

def recube_youtrack_assistant(state: AgentState):
    print("Invoking Recube YouTrack Assistant...")
    response = f"Recube YouTrack Assistant handled: '{state['input']}'"

    YOUTRACK_UPDATE_PREDEFINED_PROMPT = load_prompt("update_youtrack.txt")

    llm = ChatBedrock(
            model_id="eu.anthropic.claude-3-7-sonnet-20250219-v1:0",
            model_kwargs={
                "temperature": 0
            },
            streaming=False
        )
    
    tools = [list_projects, create_work_item] + BASE_TOOLS

    prompt = ChatPromptTemplate.from_messages([
        ("system", YOUTRACK_UPDATE_PREDEFINED_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
        
    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    retry_count = 0
    max_retries = 5
    while retry_count < max_retries:
        try:
            response = executor.invoke({"input": state["input"], "chat_history": []})
            return {"agent_output": str(response.get("output", "")), "path": ["recube_youtrack_assistant"]}

        except Exception as e:
            if "ThrottlingException" in str(e) or "Too many requests" in str(e):
                retry_count += 1
                print("Throttling, I'm retrying")
                time.sleep(5)
                if retry_count >= max_retries:
                    return {"agent_output": "Service temporarily unavailable", "path": ["recube_youtrack_assistant"]}
            else:
                return {"agent_output": f"Error: {str(e)}", "path": ["recube_youtrack_assistant"]}
    return {"agent_output": "Max retries exceeded", "path": ["recube_youtrack_assistant"]}

def recube_calendar_assistant(state: AgentState):
    print("Invoking Recube Calendar Assistant...")
    
    CALENDAR_PREDEFINED_PROMPT = load_prompt("flexible_calendar.txt")

    llm = ChatBedrock(
        model_id="eu.anthropic.claude-3-7-sonnet-20250219-v1:0",
        model_kwargs={"temperature": 0},
        streaming=False
    )
    
    tools = [get_gcal_events, set_gcal_event] + BASE_TOOLS

    prompt = ChatPromptTemplate.from_messages([
        ("system", CALENDAR_PREDEFINED_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
        
    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    retry_count = 0
    max_retries = 5
    while retry_count < max_retries:
        try:
            response = executor.invoke({"input": state["input"], "chat_history": []})
            return {"agent_output": str(response.get("output", "")), "path": ["recube_youtrack_assistant"]}

        except Exception as e:
            if "ThrottlingException" in str(e) or "Too many requests" in str(e):
                retry_count += 1
                print("Throttling, I'm retrying")
                time.sleep(5)
                if retry_count >= max_retries:
                    return {"agent_output": "Service temporarily unavailable", "path": ["recube_calendar_assistant"]}
            else:
                return {"agent_output": f"Error: {str(e)}", "path": ["recube_calendar_assistant"]}
    return {"agent_output": "Max retries exceeded", "path": ["recube_calendar_assistant"]}

# Define Supervisor Agent for Recube team (Dynamic Control Flow)
def recube_assistant_supervisor(state: AgentState):
    print("Recube Assistant Supervisor deciding within Recube Team...")
    user_input = state["input"]
    
    # Initialize LLM for agent selection
    llm = ChatBedrock(
        model_id="eu.anthropic.claude-3-7-sonnet-20250219-v1:0",
        model_kwargs={"temperature": 0},
        streaming=False
    )
    
    # Create prompt for agent selection
    prompt = ChatPromptTemplate.from_messages([
        ("system", 
         "Choose the appropriate agent based on user input:\n"
         "- recube_youtrack_assistant: for YouTrack, issues, work items\n"
         "- recube_calendar_assistant: for calendar, meetings, scheduling\n"
         "Respond with ONLY the agent name."),
        ("human", "{input}")
    ])
    
    try:
        chain = prompt | llm
        response = chain.invoke({"input": user_input})
        next_agent_to_invoke = response.content.strip()
        
        # Validate LLM response
        valid_agents = ["recube_youtrack_assistant", "recube_calendar_assistant"]
        if next_agent_to_invoke not in valid_agents:
            print(f"RECUBE SUPERVISOR: error {str(e)}")
    except Exception as e:
        print(f"RECUBE SUPERVISOR: error {str(e)}")

    print(f"Recube Supervisor chose: {next_agent_to_invoke}")
    return {"next_agent": next_agent_to_invoke, "path": ["recube_assistant"]}

# Define the Sub-graph for the Recube team
def create_recube_team_graph():
    recube_workflow = StateGraph(AgentState)
    recube_workflow.add_node("recube_assistant", recube_assistant_supervisor)
    recube_workflow.add_node("recube_youtrack_assistant", recube_youtrack_assistant)
    recube_workflow.add_node("recube_calendar_assistant", recube_calendar_assistant)

    recube_workflow.set_entry_point("recube_assistant")

    recube_workflow.add_conditional_edges(
        "recube_assistant",
        lambda state: state["next_agent"],
        {
            "recube_youtrack_assistant": "recube_youtrack_assistant",
            "recube_calendar_assistant": "recube_calendar_assistant",
        }
    )
    recube_workflow.add_edge("recube_youtrack_assistant", END)
    recube_workflow.add_edge("recube_calendar_assistant", END)

    return recube_workflow.compile()