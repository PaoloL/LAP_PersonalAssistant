from typing import TypedDict, Annotated, List, Dict, Any
import operator

# 1. Define the State for the Graph
class AgentState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        input (str): The initial input query from the user.
        agent_output (str): The output from the last executed agent.
        next_agent (str): The name of the next agent/node to invoke.
        path (List[str]): A list of agents/nodes invoked so far to track the flow.
    """
    human_request: str
    agent_output: Annotated[str, operator.add]
    next_agent: str
    replan: bool
    calendar_plan_details: Dict[str, Any] | None
    youtrack_plan_details: Dict[str, Any]
    current_path: Annotated[List[str], operator.add]

