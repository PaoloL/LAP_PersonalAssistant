import logging
import time
from typing import Any, Dict

from langgraph.graph import StateGraph, END
from langchain_aws import ChatBedrock
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import AIMessage

from pydantic import ValidationError
from agent_response import CalendarResponse


from agent_state import AgentState
from tools.youtrack_tool import *
from tools.gcalendar_tool import *
from tools.base_tools import BASE_TOOLS

RECURSION_LIMIT=1000

def load_prompt(filename):
        try:
            with open(f"prompts/{filename}", 'r') as file:
                return file.read().strip()
        except FileNotFoundError as e:
            print(f"File not found error: error {str(e)}")
            return 

def conversational_youtrack(tate: AgentState):
    try:
        YOUTRACK_PROMPT = load_prompt("youtrack_manager_prompt.txt")
        checkpointer = InMemorySaver()

        llm = ChatBedrock(
            model_id="eu.anthropic.claude-3-7-sonnet-20250219-v1:0",
            model_kwargs={"temperature": 0},
            streaming=False
        )

        current_tools = [get_gcal_events, list_active_projects_name, get_issue_names_by_projectName, get_issue_id_from_issue_name, get_project_id_from_project_name, create_work_item_by_issue_id] + BASE_TOOLS

        agent = create_react_agent(
            model=llm,  
            tools=current_tools, 
            prompt=YOUTRACK_PROMPT,
            checkpointer=checkpointer,
            #response_format=CalendarResponse
        )

        config = {
            "configurable": {"thread_id": "1"},
            "recursion_limit": RECURSION_LIMIT
            }

        print("YOUTRACK ASSISTANT: Hello, how I can support you today ?")
        while True:
            request = input("YOU: ").strip()
            if request.lower() in ['exit', 'quit', 'bye']:
                print("Goodbye!")
                break
            if not request:
                continue
            print("YOUTRACK ASSISTANT: I'm thinking...")
            response = agent.invoke(
                {"messages": [{"role": "user", "content": request}]},
                config
            )
            if "messages" in response and response["messages"]:
                last_message = response["messages"][-1]
                if hasattr(last_message, 'content'):
                    print("YOUTRACK ASSISTANT:", last_message.content)
            #print("Assistant: ", response["structured_response"])
            
    except ValidationError:
        print("Error: Invalid response format. Please try again.")
        return response
    except Exception as e:
        print("Error:", e)
        return
    
if __name__ == "__main__":
    conversational_youtrack()