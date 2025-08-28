#!/bin/bash

# This script sets environment variables required for LangChain/LangGraph to integrate with LangSmith.
# Replace the placeholder values with your actual LangSmith API key and desired project name.

# --- LangSmith Configuration ---
echo "Setting LangSmith environment variables"
export LANGSMITH_TRACING="true"
export LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
export LANGSMITH_API_KEY="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"
export LANGSMITH_PROJECT="laplab-main-assistant"
echo "LangSmith environment variables setted"
