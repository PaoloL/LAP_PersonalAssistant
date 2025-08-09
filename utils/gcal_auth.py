import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

def get_credentials():
    try:
        creds = None
        if os.path.exists("secrets/token.json"):
            creds = Credentials.from_authorized_user_file("secrets/token.json", SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file("secrets/credentials.json", SCOPES)
                creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
            with open("secrets/token.json", "w") as token:
                token.write(creds.to_json())
        return creds
    except Exception as error:
        print(f"An error occurred: {error}")

