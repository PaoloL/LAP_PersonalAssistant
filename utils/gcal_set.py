import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .gcal_auth import set_credentials

def create_event(summary, start_time, end_time, description=None, attendees=None):
    """
    Create a new event in Google Calendar.

    Args:
        summary: Title of the event
        start_time: Start time in ISO format (e.g., '2025-06-01T10:00:00+02:00')
        end_time: End time in ISO format (e.g., '2025-06-01T11:00:00+02:00')
        description: Optional description for the event
        attendees: Optional list of email addresses to invite
        
    Returns:
        Event details if successful, error message otherwise
    """
        
    creds = set_credentials()
    if not creds.valid and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    try:
        service = build("calendar", "v3", credentials=creds)
        
        event = {
            'summary': summary,
            'start': {
                'dateTime': start_time,
                'timeZone': 'Europe/Rome',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'Europe/Rome',
            },
        }
        
        if description:
            event['description'] = description
            
        if attendees:
            event['attendees'] = [{'email': email} for email in attendees.split(',')]
            
        event = service.events().insert(calendarId='primary', body=event).execute()
        return f"Event created: {event.get('htmlLink')}"
    
    except Exception as error:
        return f"An error occurred: {error}"
