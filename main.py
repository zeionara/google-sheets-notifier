import os
import re
from time import sleep
from typing import List

from GoogleSheetsAdapter import GoogleSheetsAdapter
from TelegramAdapter import TelegramAdapter

COMMAND_NAME_PATTERN = re.compile(f'^[Бб].+{os.environ["COMMAND_ID"]}$')
MESSAGE_PATTERN = f'Hey! {{name}} is waiting for you!\n{{link}}'
DELAY = 10  # seconds


def does_meet_conditions(row: List[str]):
    return len(row) == 4 and row[0] == '' and COMMAND_NAME_PATTERN.fullmatch(row[1]) and len(row[2]) > 0 and len(row[3]) > 0


def make_notification_message(rows: List[List[str]]):
    for row in rows:
        if does_meet_conditions(row):
            return MESSAGE_PATTERN.format(name=row[2], link=row[3])


if __name__ == "__main__":
    telegram_adapter = TelegramAdapter(token=os.environ['TG_API_KEY'], chat_id=int(os.environ['CHAT_ID']))
    sheets_adapter = GoogleSheetsAdapter(spreadsheet_id=os.environ['SHEETS_ID'], api_key_path=os.environ['GOOGLE_SHEETS_API_CREDS_PATH'])
    is_notified = False
    while not is_notified:
        notification_message = make_notification_message(
            sheets_adapter.read(int(os.environ['SHEET_ID']))
        )
        if notification_message is not None:
            telegram_adapter.send(notification_message)
            is_notified = True
        if not is_notified:
            sleep(DELAY)
