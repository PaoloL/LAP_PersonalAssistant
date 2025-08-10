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
from langchain.tools import tool
import requests
from tools.base_tools import BASE_TOOLS

@tool
def get_portfolio_summary() -> str:
    """Get a summary of the current portfolio (mock implementation)"""
    return "Portfolio: AAPL: +2.3%, GOOGL: -1.1%, MSFT: +0.8%, Total: +1.2%"

@tool
def get_financial_news() -> str:
    """Get latest financial news headlines (mock implementation)"""
    return "Market News: Tech stocks rally, Fed signals rate cuts, Oil prices stable"

class FinanceSecretary:
    def __init__(self):
        self.llm = ChatBedrock(
            model_id="eu.anthropic.claude-3-7-sonnet-20250219-v1:0",
            model_kwargs={
                "temperature": 0
            },
            streaming=False
        )
        self.tools = [get_portfolio_summary, get_financial_news] + BASE_TOOLS
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", 
             "You are the Finance Secretary. Your job is to: "
             "1. Monitor portfolio performance "
             "2. Provide daily financial news insights "
             "3. Analyze market trends and provide recommendations"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        self.agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
        self.executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)
    
    def execute_task(self, task: str):
        try:
            response = self.executor.invoke({"input": task, "chat_history": []})
            return response
        except Exception as e:
            return {"output": f"Error: {str(e)}"}