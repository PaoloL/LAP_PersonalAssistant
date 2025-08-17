from langchain.tools import tool
from datetime import datetime, timedelta
import calendar

@tool
def get_current_datetime() -> str:
    """Get the current date and time"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@tool
def get_current_date() -> str:
    """Get the current date"""
    return datetime.now().strftime("%Y-%m-%d")

@tool
def get_current_time() -> str:
    """Get the current time"""
    return datetime.now().strftime("%H:%M:%S")

@tool
def get_my_business_hours() -> str:
    """Get the business hours of the day"""
    return "9:00 AM - 6:00 PM"

@tool
def get_my_business_days() -> str:
    """Get the business days of the week"""
    return "Monday - Friday"

@tool
def get_today_date() -> str:
    """Get today's date (keyword: Today)"""
    return datetime.now().strftime("%Y-%m-%d")

@tool
def get_yesterday_date() -> str:
    """Get yesterday's date (keyword: Yesterday)"""
    return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

@tool
def get_tomorrow_date() -> str:
    """Get tomorrow's date (keyword: Tomorrow)"""
    return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

@tool
def get_this_week_range() -> str:
    """Get this week's date range (keyword: This Week)"""
    today = datetime.now()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    return f"{start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}"

@tool
def get_next_week_range() -> str:
    """Get next week's date range (keyword: Next Week)"""
    today = datetime.now()
    start = today + timedelta(days=7 - today.weekday())
    end = start + timedelta(days=6)
    return f"{start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}"

@tool
def get_this_month_range() -> str:
    """Get this month's date range (keyword: This Month)"""
    today = datetime.now()
    start = today.replace(day=1)
    end = today.replace(day=calendar.monthrange(today.year, today.month)[1])
    return f"{start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}"

@tool
def get_next_month_range() -> str:
    """Get next month's date range (keyword: Next Month)"""
    today = datetime.now()
    if today.month == 12:
        next_month = today.replace(year=today.year + 1, month=1, day=1)
    else:
        next_month = today.replace(month=today.month + 1, day=1)
    end = next_month.replace(day=calendar.monthrange(next_month.year, next_month.month)[1])
    return f"{next_month.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}"

@tool
def get_previous_month_range() -> str:
    """Get previous month's date range (keyword: Previous Month)"""
    today = datetime.now()
    if today.month == 1:
        prev_month = today.replace(year=today.year - 1, month=12, day=1)
    else:
        prev_month = today.replace(month=today.month - 1, day=1)
    end = prev_month.replace(day=calendar.monthrange(prev_month.year, prev_month.month)[1])
    return f"{prev_month.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}"

@tool
def get_this_year_range() -> str:
    """Get this year's date range (keyword: This Year)"""
    today = datetime.now()
    start = today.replace(month=1, day=1)
    end = today.replace(month=12, day=31)
    return f"{start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}"

# Base tools that all agents should have
BASE_TOOLS = [
    get_current_datetime, get_current_date, get_current_time, 
    get_my_business_days, get_my_business_hours,
    get_today_date, get_tomorrow_date, get_this_week_range, get_next_week_range, get_yesterday_date,
    get_this_month_range, get_next_month_range, get_previous_month_range, get_this_year_range
]