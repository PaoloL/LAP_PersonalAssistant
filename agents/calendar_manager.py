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

# Configure logging
DEBUG_LEVEL = logging.ERROR
logging.basicConfig(level=DEBUG_LEVEL, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

RECURSION_LIMIT=1000

def load_prompt(filename):
        try:
            with open(f"prompts/{filename}", 'r') as file:
                return file.read().strip()
        except FileNotFoundError as e:
            print(f"File not found error: error {str(e)}")
            return 

def conversational_calendar(state: AgentState):
    print("CALENDAR ASSISTANT: Hello, I'm the Calendar Assistant")
    print("CALENDAR ASSISTANT: I'm here because you asked: ", state["human_request"])
    logger.debug("conversational_calendar - ENTRY")
    logger.debug(f"conversational_calendar - State: {state}")
    try:
        CALENDAR_PROMPT = load_prompt("calendar_manager_prompt.txt")
        logger.debug("conversational_calendar - Prompt loaded")
        checkpointer = InMemorySaver()

        llm = ChatBedrock(
            model_id="eu.anthropic.claude-3-7-sonnet-20250219-v1:0",
            model_kwargs={"temperature": 0},
            streaming=False
        )

        current_tools = [set_gcal_event, get_gcal_events] + BASE_TOOLS

        agent = create_react_agent(
            model=llm,  
            tools=current_tools,
            prompt=CALENDAR_PROMPT,
            checkpointer=checkpointer,
            #response_format=CalendarResponse
        )

        config = {
            "configurable": {"thread_id": "1"},
            "recursion_limit": RECURSION_LIMIT
            }

        print("CALENDAR ASSISTANT: How I can support you today ?")
        logger.debug("conversational_calendar - Starting conversation loop")
        while True:
            request = input("YOU: ").strip()
            logger.debug(f"conversational_calendar - User input: {request}")
            if request.lower() in ['exit', 'quit', 'bye']:
                logger.debug("conversational_calendar - User requested exit")
                print("CALENDAR ASSISTANT: I completed my task, see you soon")
                break
            if not request:
                continue
            print("CALENDAR ASSISTANT: I'm thinking...")
            logger.debug("conversational_calendar - Invoking agent")
            response = agent.invoke(
                {"messages": [{"role": "user", "content": request}]},
                config
            )
            logger.debug(f"conversational_calendar - Agent response received: {response}")
            if "messages" in response and response["messages"]:
                last_message = response["messages"][-1]
                if hasattr(last_message, 'content'):
                    print("CALENDAR ASSISTANT:", last_message.content)
            #print("Assistant: ", response["structured_response"])
            
    except ValidationError as e:
        logger.error(f"conversational_calendar - ValidationError: {str(e)}")
        print("Error: Invalid response format. Please try again.")
        return {"agent_output": f"ValidationError: {str(e)}", "current_path": ["calendar_manager"]}
    except Exception as e:
        logger.error(f"conversational_calendar - Exception: {str(e)}")
        print("Error:", e)
        return {"agent_output": f"Error: {str(e)}", "current_path": ["calendar_manager"]}
    
if __name__ == "__main__":
    conversational_calendar()