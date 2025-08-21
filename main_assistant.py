from langchain_aws import ChatBedrock
from langgraph.graph import StateGraph, END

import asyncio

# Import AgentState from the common file
from agent_state import AgentState
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate

# Import the functions to create team sub-graphs
from agents.recube_team_lead import create_recube_team_graph
from agents.personal_team_lead import create_personal_team_graph

from tools.base_tools import BASE_TOOLS

# Define the Main Assistant Supervisor
async def main_supervisor(state: AgentState):
    print("MAIN ASSISTANT: Hello, I'm the Main Assistant Supervisor deciding using LLM...")
    
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
        return {"next_agent": next_team_to_invoke, "path": ["main_assistant"]}
    
    except Exception as e:
        print("MAIN ASSISTANT: Error ", e)
        exit

# Define the Main Hierarchical Graph
def create_hierarchical_graph():
    main_workflow = StateGraph(AgentState)

    # Compile the sub-graphs imported from their respective files
    recube_team_compiled = create_recube_team_graph()
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
    app = main_workflow.compile(checkpointer=None)
    return app

async def interactive_chat():
    print("Multi-Agent Assistant Ready!")
    print("Type 'exit' or 'quit' to end the session\n")
    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("Goodbye!")
                break
            if not user_input:
                continue
            print(f"\nProcessing: {user_input}")
            inputs = {"input": user_input, "agent_output": "", "next_agent": "", "path": []}
            
            config = {"recursion_limit": 100}
            final_agent_output = ""
            async for step in app.astream(inputs, config):
                print(f"Step: {step}")
            
            formatted_output = final_agent_output.replace('\\n', '\n').replace('\\t', '\t')
            print(f"Assistant: {formatted_output}\n")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {str(e)}\n")
      
# Run the Application
if __name__ == "__main__":
    app = create_hierarchical_graph()
    asyncio.run(interactive_chat())
