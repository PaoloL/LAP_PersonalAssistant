from langchain_aws import ChatBedrock
from langgraph.graph import StateGraph, END

import asyncio
import logging

# Import AgentState from the common file
from agent_state import AgentState
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate

# Import the functions to create team sub-graphs
from agents.calendar_manager import conversational_calendar
from agents.youtrack_manager import conversational_youtrack

from tools.base_tools import BASE_TOOLS

# Configure logging
DEBUG_LEVEL = logging.ERROR
logging.basicConfig(level=DEBUG_LEVEL, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define the Main Assistant Supervisor
async def main_supervisor(state: AgentState):
    logger.debug("main_supervisor - ENTRY")
    logger.debug(f"main_supervisor - State: {state}")
    print("MAIN ASSISTANT: Hello, I'm the Main Assistant Supervisor")
    
    try:
        request = state["human_request"]
        logger.debug(f"main_supervisor - User input: {request}")

        llm = ChatBedrock(
            model_id="eu.anthropic.claude-3-7-sonnet-20250219-v1:0",
            model_kwargs={"temperature": 0},
            streaming=False
        )

        # Create prompt for agent selection
        prompt = ChatPromptTemplate.from_messages([
            ("system",
                "You are a supervisor\n"
                "You are responsible to choose the appropriate agent for task execution based on user input:\n"
                 "- YoutrackManager: for YouTrack request as update work items or list issues\n"
                 "- CalendarManager: for calendar request as list or create meetings\n"
                "Respond with ONLY the agent name."),
            ("human", "{request}")
        ])
        print("MAIN ASSISTANT: I'm deciding the next agent using LLM ...")
        response = llm.invoke(prompt.format(request=request))
        next_team_to_invoke = response.content.strip()

        # Validate LLM response
        valid_teams = ["YoutrackManager", "CalendarManager"]
        if next_team_to_invoke not in valid_teams:
            print(f"MAIN ASSISTANT: I'm not able to decide, bye")  
            return
        else:
            print(f"MAIN ASSISTANT: I want to ask support to: {next_team_to_invoke}")
            result = {"next_agent": next_team_to_invoke, "current_path": ["main_assistant"]}
            logger.debug(f"main_supervisor - Returning: {result}")
            return result
    
    except Exception as e:
        logger.error(f"main_supervisor - Exception: {str(e)}")
        print("MAIN ASSISTANT: Error ", e)
        result = {"next_agent": "RecubeTeamLeader", "current_path": ["main_assistant"]}
        logger.debug(f"main_supervisor - Error return: {result}")
        return result

# Define the Main Hierarchical Graph
def create_hierarchical_graph():
    logger.debug("create_hierarchical_graph - entry")
    
    main_workflow = StateGraph(AgentState)
    main_workflow.add_node("main_supervisor", main_supervisor)
    main_workflow.add_node("calendar_manager_node", conversational_calendar)
    main_workflow.add_node("youtrack_manager_node", conversational_youtrack)
    main_workflow.set_entry_point("main_supervisor")

    # The main supervisor transitions to the appropriate sub-graph node
    main_workflow.add_conditional_edges(
        "main_supervisor",
        lambda state: state["next_agent"],
        {
            "YoutrackManager": "youtrack_manager_node",
            "CalendarManager": "calendar_manager_node",
        }
    )

    main_workflow.add_edge("youtrack_manager_node", END)
    main_workflow.add_edge("calendar_manager_node", END)

    # Compile the main graph
    logger.debug("create_hierarchical_graph - Compiling main workflow")
    app = main_workflow.compile(checkpointer=None)
    logger.debug("create_hierarchical_graph - Graph compiled successfully")
    return app

async def interactive_chat():
    logger.debug("interactive_chat - ENTRY")
    print("Multi-Agent Assistant Ready!")
    print("Type 'exit' or 'quit' to end the session\n")
    while True:
        try:
            request = input("YOU: ").strip()
            logger.debug(f"interactive_chat - User input: {request}")
            if request.lower() in ['exit', 'quit', 'bye']:
                logger.debug("interactive_chat - User requested exit")
                print("Goodbye!")
                break
            if not request:
                continue
            print(f"\nMAIN ASSISTANT: Processing: {request}")
            inputs = {"human_request": request, "agent_output": "", "next_agent": "", "current_path": []}
            logger.debug(f"interactive_chat - Invoking app with inputs: {inputs}")
            result = await app.ainvoke(inputs)
            logger.debug(f"interactive_chat - App result: {result}")

            final_agent_output = result.get("agent_output", "")
            logger.debug(f"interactive_chat - Final agent output: {final_agent_output}")
            formatted_output = final_agent_output.replace('\\n', '\n').replace('\\t', '\t')

            print(f"MAIN ASSISTANT: Final agent output: {formatted_output}\n")
            
        except KeyboardInterrupt:
            logger.debug("interactive_chat - KeyboardInterrupt received")
            print("\nGoodbye!")
            break
        except Exception as e:
            logger.error(f"interactive_chat - Exception: {str(e)}")
            print(f"Error: {str(e)}\n")
      
# Run the Application
if __name__ == "__main__":
    logger.debug("main - Starting application")
    app = create_hierarchical_graph()
    logger.debug("main - Running interactive chat")
    asyncio.run(interactive_chat())
