import os
import time
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

# Suppress verbose error logging
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('langchain_aws').setLevel(logging.CRITICAL)

from langchain_aws import ChatBedrock
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from tools.langchain_youtrack import list_projects, list_issues_from_project, create_work_item
from tools.langchain_gcal import get_gcal_events, set_gcal_event
from tools.base_tools import BASE_TOOLS

class RecubeSecretary:
    
    def __init__(self):
        self.llm = ChatBedrock(
            model_id="eu.anthropic.claude-3-7-sonnet-20250219-v1:0",
            model_kwargs={
                "temperature": 0
            },
            streaming=False
        )
        self.tools = [list_projects, get_gcal_events, set_gcal_event, create_work_item] + BASE_TOOLS
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", 
             "You are the Recube Secretary. Your job is to: "
             "1. Check Google Calendar for business events "
             "2. Create corresponding work items in YouTrack "
             "3. Manage project tracking and time logging"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        self.agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
        self.executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)
    
    def execute_task(self, task: str):
        retry_count = 0
        max_retries = 3
        while retry_count < max_retries:
            try:
                response = self.executor.invoke({"input": task, "chat_history": []})
                return response
            except Exception as e:
                return {"output": f"Error: {str(e)}"}