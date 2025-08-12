import datetime
import os.path
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from .gcal_auth import get_credentials 

# If modifying these scopes, delete the file token.json.

def get_events(start_date, days_window):
    """ 
    Get events from Google Calendar starting from start_Date and for the specified number of days
    """
    creds = get_credentials()
    if not creds.valid and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    try:
        service = build("calendar", "v3", credentials=creds)
        # Handle different date formats
        try:
            start_date = datetime.datetime.fromisoformat(start_date)
        except ValueError:
            # Try parsing as YYYY-MM-DD format
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end_date = start_date + datetime.timedelta(days=int(days_window))
        # Convert date in Gcal required format
        start_iso = start_date.isoformat() + 'Z'
        end_iso = end_date.isoformat() + 'Z'
        # Call the Calendar API
        print("Getting the events from ", start_iso, " to ", end_iso, " ( ", days_window, " days window)", )
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=start_iso,
                timeMax=end_iso,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])
        filtered_events = []
        for event in events:
            filtered_event = {
                'title': event.get('summary', 'No Title'),
                'start': event['start'].get('dateTime', event['start'].get('date')),
                'end': event['end'].get('dateTime', event['end'].get('date'))
            }
            filtered_events.append(filtered_event)
        return filtered_events
    except HttpError as error:
        print(f"An error occurred: {error}")
