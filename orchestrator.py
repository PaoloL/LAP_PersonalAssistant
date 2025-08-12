from langchain_aws import ChatBedrock
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
import asyncio

# Import AgentState from the common file
from agent_state import AgentState

# Import the functions to create team sub-graphs
from agents.recube_team_lead import create_recube_team_graph
from agents.personal_team_lead import create_personal_team_graph

# Define the Main Assistant Supervisor
async def main_assistant_supervisor(state: AgentState):
    print("I'm the Main Assistant Supervisor deciding using LLM...")
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
         "- recube_team_node: for YouTrack, Calendar and Business activities\n"
         "- personal_team_node: for Task, Finance and Personal activities\n"
         "Respond with ONLY the agent name."),
        ("human", "{input}")
    ])
    
    try:
        chain = prompt | llm
        response = chain.invoke({"input": user_input})
        next_team_to_invoke = response.content.strip()
        
        # Validate LLM response
        valid_agents = ["recube_team_node", "personal_team_node"]
        if next_team_to_invoke not in valid_agents:
            next_team_to_invoke = "recube_team_node"
    except Exception as e:
        print(f"LLM error: {str(e)}. Using fallback.")
        next_team_to_invoke = "recube_team_node"

    print(f"Main Supervisor (LLM-based) chose team: {next_team_to_invoke}")
    return {"next_agent": next_team_to_invoke, "path": ["main_assistant"]}


# Define the Main Hierarchical Graph
def create_hierarchical_graph():
    main_workflow = StateGraph(AgentState)

    # Compile the sub-graphs imported from their respective files
    recube_team_compiled = create_recube_team_graph()
    personal_team_compiled = create_personal_team_graph()

    main_workflow.add_node("main_assistant", main_assistant_supervisor)
    main_workflow.add_node("recube_team_node", recube_team_compiled)
    main_workflow.add_node("personal_team_node", personal_team_compiled)

    # Set the entry point of the main graph
    main_workflow.set_entry_point("main_assistant")

    # The main supervisor transitions to the appropriate sub-graph node
    main_workflow.add_conditional_edges(
        "main_assistant",
        lambda state: state["next_agent"], # This `next_agent` will now be "recube_team_node" or "personal_team_node"
        {
            "recube_team_node": "recube_team_node",
            "personal_team_node": "personal_team_node",
        }
    )

    # When a sub-graph node finishes, the main graph also ends.
    main_workflow.add_edge("recube_team_node", END)
    main_workflow.add_edge("personal_team_node", END)

    # Compile the main graph
    app = main_workflow.compile()
    return app

# Run the Application
if __name__ == "__main__":
    app = create_hierarchical_graph()

    async def run_example(input_text):
        print(f"\n--- Running with '{input_text}' ---")
        inputs = {"input": input_text, "agent_output": "", "next_agent": "", "path": []}
        async for s in app.astream(inputs):
            print(s)
        print("-" * 30)

    async def main():
        await run_example("List all YouTrack Projects")
        await run_example("List all Google Calendar events")

    asyncio.run(main())
