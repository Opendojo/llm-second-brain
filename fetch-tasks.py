import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/tasks"]

def get_credentials():
    creds = None
    token_file = "token.json"
    credentials_file = "client_secret_908808669944-ig60rqvqmbmbv2s52o7i7oiff3s18v8n.apps.googleusercontent.com.json"

    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_file, "w") as token:
            token.write(creds.to_json())

    return creds

def fetch_tasks():
    creds = get_credentials()
    service = build("tasks", "v1", credentials=creds)

    try:
        tasks = service.tasks().list(tasklist="@default").execute()
        items = tasks.get("items", [])
        
        if not items:
            print("No tasks found.")
            return
        
        for item in items:
            print(f"Task: {item['title']}, Due: {item.get('due', 'No due date')}, Status: {item['status']}")
    
    except Exception as e:
        print(f"Error fetching tasks: {e}")

if __name__ == "__main__":
    fetch_tasks()
