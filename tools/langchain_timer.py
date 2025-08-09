from langchain.tools import tool
from datetime import datetime

@tool
def get_current_time() -> str:
    """Get the current time of day"""
    return datetime.now().strftime("%H:%M:%S")