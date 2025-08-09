import datetime
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .gcal_auth import set_credentials

# If modifying these scopes, delete the file token.json.

def get_events(start_date, days_window):
    """ 
    Get events from Google Calendar starting from start_Date and for the specified number of days
    """
    creds = set_credentials()
    if not creds.valid and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    try:
        service = build("calendar", "v3", credentials=creds)
        start_date = datetime.datetime.fromisoformat(start_date)
        end_date = (start_date + datetime.timedelta(days=int(days_window))).isoformat()
        # Call the Calendar API
        print("Getting the events from ", start_date, " to ", end_date, " ( ", days_window, " days window)", )
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin = start_date,
                timeMax = end_date,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])
        return events
    except HttpError as error:
        print(f"An error occurred: {error}")
