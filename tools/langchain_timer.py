from langchain.tools import tool
from datetime import datetime

@tool
def get_current_time() -> str:
    """Get the current time of day"""
    return datetime.now().strftime("%H:%M:%S")

@tool
def get_current_date() -> str:
    """Get the current date"""
    return datetime.now().strftime("%Y-%m-%d")

@tool
def get_my_business_hours() -> str:
    """Get the business hours of the day"""
    return "9:00 AM - 6:00 PM"

@tool
def get_my_business_days() -> str:
    """Get the business days of the week"""
    return "Monday - Friday"