from langchain_aws import ChatBedrock
from langgraph.graph import StateGraph, END

import asyncio
import logging

# Import AgentState from the common file
from agent_state import AgentState
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate

# Import the functions to create team sub-graphs
from agents.recube_team_lead import create_recube_team_graph
from agents.personal_team_lead import create_personal_team_graph

from tools.base_tools import BASE_TOOLS

# Configure logging
DEBUG_LEVEL = logging.DEBUG
logging.basicConfig(level=DEBUG_LEVEL, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define the Main Assistant Supervisor
async def main_supervisor(state: AgentState):
    logger.debug("main_supervisor - ENTRY")
    logger.debug(f"main_supervisor - State: {state}")
    print("MAIN ASSISTANT: Hello, I'm the Main Assistant Supervisor deciding using LLM...")
    
    try:
        user_input = state["input"]
        logger.debug(f"main_supervisor - User input: {user_input}")

        llm = ChatBedrock(
            model_id="eu.anthropic.claude-3-7-sonnet-20250219-v1:0",
            model_kwargs={"temperature": 0},
            streaming=False
        )

        # Create prompt for agent selection
        prompt = ChatPromptTemplate.from_messages([
            ("system",
                "You are a personal assistant that support user on business and personal task\n"
                "You are responsible to choose the appropriate team leader based on user input:\n"
                "- RecubeTeamLeader: for YouTrack, Calendar and Business activities\n"
                "- PersonalTeamLeader: for Task, Finance and Personal activities\n"
                "Respond with ONLY the agent name."),
            ("human", "{human_request}")
        ])

        response = llm.invoke(prompt.format(human_request=user_input))
        next_team_to_invoke = response.content.strip()

        # Validate LLM response
        valid_teams = ["RecubeTeamLeader", "PersonalTeamLeader"]
        if next_team_to_invoke not in valid_teams:
            next_team_to_invoke = "RecubeTeamLeader"       

        print(f"MAIN ASSISTANT: I want to ask support to: {next_team_to_invoke}")
        result = {"next_agent": next_team_to_invoke, "path": ["main_assistant"]}
        logger.debug(f"main_supervisor - Returning: {result}")
        return result
    
    except Exception as e:
        logger.error(f"main_supervisor - Exception: {str(e)}")
        print("MAIN ASSISTANT: Error ", e)
        result = {"next_agent": "RecubeTeamLeader", "path": ["main_assistant"]}
        logger.debug(f"main_supervisor - Error return: {result}")
        return result

# Define the Main Hierarchical Graph
def create_hierarchical_graph():
    logger.debug("create_hierarchical_graph - ENTRY")
    main_workflow = StateGraph(AgentState)

    # Compile the sub-graphs imported from their respective files
    logger.debug("create_hierarchical_graph - Creating recube team graph")
    recube_team_compiled = create_recube_team_graph()
    logger.debug("create_hierarchical_graph - Creating personal team graph")
    personal_team_compiled = create_personal_team_graph()

    main_workflow.add_node("main_supervisor", main_supervisor)
    main_workflow.add_node("recube_team_node", recube_team_compiled)
    main_workflow.add_node("personal_team_node", personal_team_compiled)

    # Set the entry point of the main graph
    main_workflow.set_entry_point("main_supervisor")

    # The main supervisor transitions to the appropriate sub-graph node
    main_workflow.add_conditional_edges(
        "main_supervisor",
        lambda state: state["next_agent"],
        {
            "RecubeTeamLeader": "recube_team_node",
            "PersonalTeamLeader": "personal_team_node",
        }
    )

    # When a sub-graph node finishes, the main graph also ends.
    main_workflow.add_edge("recube_team_node", END)
    main_workflow.add_edge("personal_team_node", END)

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
            user_input = input("You: ").strip()
            logger.debug(f"interactive_chat - User input: {user_input}")
            if user_input.lower() in ['exit', 'quit', 'bye']:
                logger.debug("interactive_chat - User requested exit")
                print("Goodbye!")
                break
            if not user_input:
                continue
            print(f"\nProcessing: {user_input}")
            inputs = {"input": user_input, "agent_output": "", "next_agent": "", "path": []}
            logger.debug(f"interactive_chat - Invoking app with inputs: {inputs}")
            result = await app.ainvoke(inputs)
            logger.debug(f"interactive_chat - App result: {result}")

            # Since result is already a dict, use it directly
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
