from langchain_aws import ChatBedrock
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool
from tenacity import retry, stop_after_attempt, wait_exponential
import os
import time
import logging

# Suppress verbose error logging
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('langchain_aws').setLevel(logging.CRITICAL)

from agents.finance_secretary import FinanceSecretary
from agents.recube_secretary import RecubeSecretary
from tools.base_tools import BASE_TOOLS

@tool
def delegate_to_secretary_recube(task: str) -> str:
    """Delegate tasks to Recube Secretary for YouTrack and calendar management"""
    recube_secretary_agent = RecubeSecretary()
    result = recube_secretary_agent.execute_task(task)
    return str(result['output'])

@tool
def delegate_to_secretary_finance(task: str) -> str:
    """Delegate tasks to Finance Secretary for portfolio and financial news"""
    finance_secretary_agent = FinanceSecretary()
    result = finance_secretary_agent.execute_task(task)
    return str(result['output'])

def main():
    print("General Secretary is ready to serve you!")
    print("You can delegate tasks to Recube Secretary or Finance Secretary.")
    print("Type 'exit' to quit.")

    llm = ChatBedrock(
        model_id="eu.anthropic.claude-3-7-sonnet-20250219-v1:0",
        model_kwargs={
            "temperature": 0,
        },
        streaming=False
    )

    collaborators = [
        delegate_to_secretary_recube,
        delegate_to_secretary_finance
    ] + BASE_TOOLS

    # Define the prompt for the agent
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are my personal assistant"
                "You can retrieve Youtrack information delegationg task to Recube_secretary"
                "You can also view and set events in my Google Calendar delegating task to Recube_secretary"
                "Use the available tools to support me on execute daily task to improve my work"
                "Always try to provide specific details before to proceed"
            ),

            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    # Create the agent
    agent = create_tool_calling_agent(llm, collaborators, prompt)

    # Create the AgentExecutor
    agent_executor = AgentExecutor(agent=agent, tools=collaborators, verbose=True)
    
    # I want to get prtompt from console and pass to agent executor
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit' or user_input.lower() == 'quit':
            break
        try:
            response = agent_executor.invoke({"input": user_input, "chat_history": []})
            print(f"\nAgent's Final Response: {response['output']}")
            print("-" * 50)
        except Exception as e:
                print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()