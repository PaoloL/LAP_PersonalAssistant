import logging
import time
from agent_state import AgentState # Import AgentState from the common file

from langgraph.graph import StateGraph, END
from langchain_aws import ChatBedrock
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent

from tools.youtrack_tool import *
from tools.gcalendar_tool import *
from tools.base_tools import BASE_TOOLS

# Suppress verbose error logging
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('langchain_aws').setLevel(logging.CRITICAL)

RECURSION_LIMIT=1000

def load_prompt(filename):
        try:
            with open(f"prompts/{filename}", 'r') as file:
                return file.read().strip()
        except FileNotFoundError as e:
            print(f"File not found error: error {str(e)}")
            return 

# Define Supervisor Agent for Recube team (Dynamic Control Flow)
def recube_supervisor(state: AgentState):
    print("RECUBE TEAM LEADER: I'm ready to choose the appropriate agent for this task")
    
    try:
        user_input = state["input"]

        llm = ChatBedrock(
            model_id="eu.anthropic.claude-3-7-sonnet-20250219-v1:0",
            model_kwargs={"temperature": 0},
            streaming=False
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system",
                "You are a team leader of recube team\n"
                "You are responsible to choose the appropriate agent for task execution based on user input:\n"
                 "- YoutrackAssistant: for YouTrack request as update work items or list issues\n"
                 "- CalendarAssistant: for calendar request as list or create meetings\n"
                "Respond with ONLY the agent name."),
            ("human", "{human_request}")
        ])

        response = llm.invoke(prompt.format(human_request=user_input))
        next_agent_to_invoke = response.content.strip()

        # Validate LLM response
        valid_agents = ["YoutrackAssistant", "CalendarAssistant"]
        if next_agent_to_invoke not in valid_agents:
            next_agent_to_invoke = "YoutrackAssistant"

        print(f"RECUBE TEAM LEADER: I'm choosed {next_agent_to_invoke}")
        return {"next_agent": next_agent_to_invoke, "path": ["recube_supervisor"]}
        
    except Exception as e:
        print(f"RECUBE TEAM LEADER: error {str(e)}")
        return {"next_agent": "recube_youtrack_assistant", "path": ["recube_supervisor"]}

# Define Router Agent to split Read from Write
# Write operation require a planning stage
def recube_youtrack_assistant_router(state: AgentState):
    print("YoutrackAssistant: selecting the right actions")
    
    try:
        user_input = state["input"]

        llm = ChatBedrock(
            model_id="eu.anthropic.claude-3-7-sonnet-20250219-v1:0",
            model_kwargs={"temperature": 0},
            streaming=False
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system",
                "You are a Youtrack assistant router\n"
                "You are responsible to choose the appropriate agent for Youtrack user request:\n"
                 "- YoutrackWriter: for request that require to update information on youtrack\n"
                 "- YoutrackReader: for request that require to get information from youtrack\n"
                "Respond with ONLY the agent name."),
            ("human", "{human_request}")
        ])

        response = llm.invoke(prompt.format(human_request=user_input))
        next_agent_to_invoke = response.content.strip()

        # Validate LLM response
        valid_agents = ["YoutrackWriter", "YoutrackReader"]
        if next_agent_to_invoke not in valid_agents:
            next_agent_to_invoke = "YoutrackReader"

        print(f"YoutrackAssistant: I'm choosed to proceed with {next_agent_to_invoke}")
        return {"next_agent": next_agent_to_invoke, "path": ["youtrack_assistant_router"]}
        
    except Exception as e:
        print(f"YoutrackAssistant: error {str(e)}")
        return {"next_agent": "recube_youtrack_assistant", "path": ["youtrack_assistant_router"]}

# Define a planner agent, before to write I want to see a plan
def recube_youtrack_writer_planner(state: AgentState):
    YOUTRACK_PLANNING_PROMPT = load_prompt("update_youtrack.txt")
    print("YoutrackAssistant: planning YouTrack work items...")

    try:
        llm = ChatBedrock(
            model_id="eu.anthropic.claude-3-7-sonnet-20250219-v1:0",
            model_kwargs={"temperature": 0},
            streaming=False
        )

        current_tools = [get_gcal_events, list_active_projects_name, get_issue_names_by_projectName, get_issue_id_from_issue_name] + BASE_TOOLS

        agent = create_react_agent(
            model=llm, 
            tools=current_tools,
            prompt=YOUTRACK_PLANNING_PROMPT,
            name="recube_youtrack_planner",
            checkpointer=None
        )

        # Determine if it is a replan or first execution
        if state.get("next_agent") == "replan" and state.get("agent_output"):
            task_description = state["input"] + state['agent_output']
            print(f"NEW PLAN: {task_description}")
        else:
            task_description = state["input"]
        
        response = agent.invoke(
            {"messages": [{"role": "user", "content": task_description}]}
        )
        
        # Extract plan from agent response messages
        plan = ""
        for message in reversed(response["messages"]):
            if hasattr(message, 'content') and message.content.strip():
                plan = message.content.strip()
                break
        
        print(f"\n=== Planned Work Items ===")
        print(plan)
        
        choice = input("\n(a)ccept, (m)odify, or (c)ancel? ").strip().lower()
        
        if choice == 'c':
            return {"agent_output": "Plan cancelled", "path": ["youtrack_planner"]}
        elif choice == 'm':
            modified_plan = input("\nSuggest improvement of the plan: ").strip()
            return {"agent_output": modified_plan, "next_agent": "replan", "path": ["youtrack_planner"]}
        else:
            return {"agent_output": plan, "next_agent": "execute", "path": ["youtrack_planner"]}
            
    except Exception as e:
        return {"agent_output": f"Error: {str(e)}", "path": ["youtrack_planner"]}

# Define an executor agent that execute the plan
def recube_youtrack_writer_executor(state: AgentState):
    print("YoutrackAssistant: executing YouTrack update ...")

    try:

        llm = ChatBedrock(
            model_id="eu.anthropic.claude-3-7-sonnet-20250219-v1:0",
            model_kwargs={"temperature": 0},
            streaming=False
        )

        current_tools = [get_issue_id_from_issue_name, get_project_id_from_project_name, create_work_item_by_issue_id] + BASE_TOOLS
        
        prompt = """
            You are a Youtrack assistant\n"
            You are responsible to execute the plan exactly as proposed:\n"
            """

        agent = create_react_agent(
            model=llm, 
            tools=current_tools,
            prompt=prompt,
            name="recube_youtrack_writer_executor",
            checkpointer=None
        )

        plan = state["agent_output"]
        print(f"YoutrackAssistant: Executing plan ...")
        
        response = agent.invoke(
            {"messages": [{"role": "user", "content": plan}]}
        )
        for message in reversed(response["messages"]):
                if hasattr(message, 'content') and message.content.strip():
                    return {"agent_output": message.content, "path": ["youtrack_writer_executor"]}
        return {"agent_output": "No response generated", "path": ["youtrack_writer_executor"]}
        
    except Exception as e:
        return {"agent_output": f"Error: {str(e)}", "path": ["youtrack_writer_executor"]}

# Define agent to read information baed on user requests        
def recube_youtrack_reader_executor(state: AgentState):
    print("YoutrackAssistant: executing user request ...")
    try:
       
        user_input = state["input"]
        print(f"Processing request: {user_input}")

        llm = ChatBedrock(
            model_id="eu.anthropic.claude-3-7-sonnet-20250219-v1:0",
            model_kwargs={"temperature": 0},
            streaming=False
        )

        prompt = """
            You are a Youtrack assistant\n
            You are responsible to answer to user request based on YouTrack information")
            """

        current_tools = [get_gcal_events, list_active_projects_by_name, list_issues_by_name] + BASE_TOOLS

        agent = create_react_agent(
            model=llm, 
            tools=current_tools,
            prompt=prompt,
            name="recube_youtrack_reader_executor",
            checkpointer=None
        )
        
        # Run the agent
        print("Invoking agent...")
        response = agent.invoke(
            {"messages": [{"role": "user", "content": user_input}]},
            config={"recursion_limit": RECURSION_LIMIT}
        )
        print("Agent response received")
        for message in reversed(response["messages"]):
            if hasattr(message, 'content') and message.content.strip():
                return {"agent_output": message.content, "path": ["recube_calendar_assistant"]}
        return {"agent_output": "No response generated", "path": ["recube_calendar_assistant"]}
            
    except Exception as e:
        return {"agent_output": f"Error: {str(e)}", "path": ["recube_calendar_assistant"]}

# Define Router Agent to split Read from Write
# Write operation require a planning stage
def recube_calendar_assistant_router(state: AgentState):
    print("Invoking Recube Calendar Assistant...")
    
    prompt = ChatPromptTemplate.from_messages([
            ("system",
                "You are a Calendar assistant\n"
                "You are responsible to choose the appropriate agent for Youtrack user request:\n"
                 "- CalendarkWriter: for request that require to update calendar events\n"
                 "- CalendarReader: for request that require to get information from calendar\n"
                "Respond with ONLY the agent name."),
            ("human", "{human_request}")
        ])
    
    try:

        llm = ChatBedrock(
            model_id="eu.anthropic.claude-3-7-sonnet-20250219-v1:0",
            model_kwargs={"temperature": 0},
            streaming=False
        )

        user_input = state["input"]
        response = llm.invoke(prompt.format(human_request=user_input))
        next_agent_to_invoke = response.content.strip()
        
        for message in reversed(response["messages"]):
            if hasattr(message, 'content') and message.content.strip():
                return {"agent_output": message.content, "path": ["recube_calendar_assistant"]}
        return {"agent_output": "No response generated", "path": ["recube_calendar_assistant"]}
            
    except Exception as e:
        return {"agent_output": f"Error: {str(e)}", "path": ["recube_calendar_assistant"]}

def recube_calendar_writer_planner(state: AgentState):
    CALENDAR_PLANNING_PROMPT = load_prompt("update_calendar.txt")
    print("CalendarAssistant: planning calendar events...")
    try:
        llm = ChatBedrock(
            model_id="eu.anthropic.claude-3-7-sonnet-20250219-v1:0",
            model_kwargs={"temperature": 0},
            streaming=False
        )

        current_tools = [get_gcal_events] + BASE_TOOLS

        agent = create_react_agent(
            model=llm,
            tools=current_tools,
            prompt=CALENDAR_PLANNING_PROMPT,
            name="recube_calendar_writer_planner",
            checkpointer=None
        )

        user_input = state["input"]

        response = agent.invoke(
            {"messages": [{"role": "user", "content": user_input}]}
        )

        # Extract plan from agent response messages
        plan = ""
        for message in reversed(response["messages"]):
            if hasattr(message, 'content') and message.content.strip():
                plan = message.content.strip()
                break

        print(f"\n=== Planned Calendar Events ===")
        print(plan)

        choice = input("\n(a)ccept, (m)odify, or (c)ancel? ").strip().lower()

        if choice == 'c':
            return {"agent_output": "Plan cancelled", "path": ["calendar_planner"]}
        elif choice == 'm':
            modified_plan = input("\nEnter modified plan (JSON format): ").strip()
            return {"plan": modified_plan, "next_agent": "replan", "path": ["calendar_planner"]}
        else:
            return {"plan": plan, "next_agent": "execute", "path": ["calendar_planner"]}
    except Exception as e:
        return {"agent_output": f"Error: {str(e)}", "path": ["calendar_planner"]}

def recube_calendar_writer_executor(state: AgentState):
    return None

def recube_calendar_reader_executor(state: AgentState):
    return None

# Define the Sub-graph for the Recube team
def create_recube_team_graph():
    recube_workflow = StateGraph(AgentState)
    recube_workflow.add_node("recube_supervisor", recube_supervisor)
    recube_workflow.add_node("youtrack_router", recube_youtrack_assistant_router)
    recube_workflow.add_node("youtrack_writer_planner", recube_youtrack_writer_planner)
    recube_workflow.add_node("youtrack_writer_executor", recube_youtrack_writer_executor)
    recube_workflow.add_node("youtrack_reader_executor", recube_youtrack_reader_executor)
    recube_workflow.add_node("calendar_router", recube_calendar_assistant_router)
    recube_workflow.add_node("calendar_writer_planner", recube_calendar_writer_planner)
    recube_workflow.add_node("calendar_writer_executor", recube_calendar_writer_executor)
    recube_workflow.add_node("calendar_reader_executor", recube_calendar_reader_executor)

    recube_workflow.set_entry_point("recube_supervisor")

    recube_workflow.add_conditional_edges(
        "recube_supervisor",
        lambda state: state["next_agent"],
        {
            "YoutrackAssistant": "youtrack_router",
            "CalendarAssistant": "calendar_router",
        }
    )
    
    recube_workflow.add_conditional_edges(
        "youtrack_router",
        lambda state: state.get("next_agent"),
        {
            "YoutrackWriter": "youtrack_writer_planner",
            "YoutrackReader": "youtrack_reader_executor"
        }
    )

    recube_workflow.add_conditional_edges(
    "youtrack_writer_planner",
    lambda state: state.get("next_agent", "end"),
    {
        "execute": "youtrack_writer_executor",
        "replan": "youtrack_writer_planner",
        "end": END
    }
)
    recube_workflow.add_conditional_edges(
        "calendar_router",
        lambda state: state.get("next_agent"),
        {
            "CalendarWriter": "calendar_writer_planner",
            "CalendarReader": "calendar_reader_executor"
        }
    )
    
    recube_workflow.add_edge("youtrack_writer_executor", END)
    recube_workflow.add_edge("calendar_writer_planner", "calendar_writer_executor")
    recube_workflow.add_edge("calendar_writer_executor", END)

    return recube_workflow.compile(checkpointer=None)