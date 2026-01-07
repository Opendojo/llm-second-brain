import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
import datetime
import aiofiles
import aiohttp
import asyncio

SCOPES = ["https://www.googleapis.com/auth/tasks"]


class Tools:
    def __init__(self):
        self.token_file = "token.json"
        ## self.credentials_file = "client_secret_908808669944-059ov6mjg2rksl538rrc3k755k2frfer.apps.googleusercontent.com.json"
        self.credentials_file = "client_secret_908808669944-ig60rqvqmbmbv2s52o7i7oiff3s18v8n.apps.googleusercontent.com.json"
        self.creds = None

    async def get_credentials(self):
        """Handles OAuth authentication asynchronously."""
        if os.path.exists(self.token_file):
            self.creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES
                )
                self.creds = flow.run_local_server(port=0)

            async with aiofiles.open(self.token_file, "w") as token:
                await token.write(self.creds.to_json())

    async def add_task(
        self,
        title: str,
        notes: str = None,
        due_date: str = None,
        __event_emitter__=None,
    ) -> str:
        """Adds a task asynchronously to Google Tasks."""
        await self.get_credentials()  # Ensure credentials are loaded
        await __event_emitter__(
            {
                "type": "message",  # We set the type here
                "data": {
                    "content": "Storing your tasks in Google Tasks...",
                    "done": False,
                },
                # Note that with message types we do NOT have to set a done condition
            }
        )
        try:
            service = build("tasks", "v1", credentials=self.creds)

            task = {"title": title}

            if notes:
                task["notes"] = notes

            if due_date:
                due_date_iso = (
                    datetime.datetime.strptime(due_date, "%Y-%m-%d").isoformat() + "Z"
                )
                task["due"] = due_date_iso
            # Insert the task into the default list
            result = service.tasks().insert(tasklist="@default", body=task).execute()
        except HttpError as e:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {"description": f"Google API error: {e}", "done": True},
                }
            )
            return f"Google API error: {e}"
        except Exception as e:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {"description": f"An error occured: {e}", "done": True},
                }
            )
            return f"An error occured: {e}"
        else:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"Completed successfully! {result}",
                        "done": True,
                    },
                }
            )
            return f'Task "{title}" ({result["id"]}) added successfully'
