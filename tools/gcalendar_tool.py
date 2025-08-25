from langchain.tools import tool
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.gcal_get import get_events
from utils.gcal_set import create_event

@tool
def get_gcal_events(start_date: str, end_date: int) -> str:
    """Get events from Google Calendar starting from start_date for specified number of days"""
    try:
        events = get_events(start_date, end_date)
        return str(events)
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def set_gcal_event(summary: str, start_time: str, end_time: str, description: str = "", attendees: str = "") -> str:
    """Create a new event in Google Calendar"""
    try:
        result = create_event(summary, start_time, end_time, description, attendees)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"