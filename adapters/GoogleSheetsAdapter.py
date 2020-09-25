import os
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


class GoogleSheetsAdapter:
    def __init__(self, spreadsheet_id: str, api_key_path: str):
        self.spreadsheet_id = spreadsheet_id
        creds = None

        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(api_key_path, ['https://www.googleapis.com/auth/spreadsheets', ])
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('sheets', 'v4', credentials=creds)
        self.service = service.spreadsheets()

    def read(self, sheet_id: int):
        sheet_name = next(
            filter(
                lambda sheet_: sheet_['properties']['sheetId'] == sheet_id,
                self.service.get(spreadsheetId=self.spreadsheet_id).execute()['sheets']
            )
        )['properties']['title']
        result = self.service.values().get(
            spreadsheetId=self.spreadsheet_id,
            range=f"{sheet_name}"
        ).execute()

        return result.get('values', [])
