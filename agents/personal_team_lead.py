from langgraph.graph import StateGraph, END
from agent_state import AgentState # Import AgentState from the common file

# Define Dummy Agents (Leaf Nodes) for Personal team
def personal_todo_assistant(state: AgentState):
    print("Invoking Personal Todo Assistant...")
    response = f"Personal Todo Assistant handled: '{state['input']}'"
    return {"agent_output": response, "path": ["personal_todo_assistant"]}

def personal_finance_assistant(state: AgentState):
    print("Invoking Personal Finance Assistant...")
    response = f"Personal Finance Assistant handled: '{state['input']}'"
    return {"agent_output": response, "path": ["personal_finance_assistant"]}

# Define Supervisor Agent for Personal team (Dynamic Control Flow)
def personal_assistant_supervisor(state: AgentState):
    print("Personal Assistant Supervisor deciding within Personal Team...")
    user_input = state["input"].lower()
    next_agent_to_invoke = ""
    if "todo" in user_input or "task" in user_input:
        next_agent_to_invoke = "personal_todo_assistant"
    elif "finance" in user_input or "budget" in user_input or "expense" in user_input:
        next_agent_to_invoke = "personal_finance_assistant"
    else:
        print("Personal Supervisor couldn't determine a specific Personal agent. Defaulting to Todo.")
        next_agent_to_invoke = "personal_todo_assistant" # Fallback

    print(f"Personal Supervisor chose: {next_agent_to_invoke}")
    return {"next_agent": next_agent_to_invoke, "path": ["personal_assistant"]}

# Define the Sub-graph for the Personal team
def create_personal_team_graph():
    personal_workflow = StateGraph(AgentState)
    personal_workflow.add_node("personal_assistant", personal_assistant_supervisor)
    personal_workflow.add_node("personal_todo_assistant", personal_todo_assistant)
    personal_workflow.add_node("personal_finance_assistant", personal_finance_assistant)

    personal_workflow.set_entry_point("personal_assistant")

    personal_workflow.add_conditional_edges(
        "personal_assistant",
        lambda state: state["next_agent"],
        {
            "personal_todo_assistant": "personal_todo_assistant",
            "personal_finance_assistant": "personal_finance_assistant",
        }
    )
    personal_workflow.add_edge("personal_todo_assistant", END)
    personal_workflow.add_edge("personal_finance_assistant", END)

    return personal_workflow.compile(checkpointer=None)