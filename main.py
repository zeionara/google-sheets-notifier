import os
import re
from datetime import datetime
from time import sleep
from typing import List

from adapters.GoogleSheetsAdapter import GoogleSheetsAdapter
from adapters.TelegramAdapter import TelegramAdapter

SECOND_NOTIFICATION_THRESHOLD = 3  # number of people before you
COMMAND_NAME_PATTERN = re.compile(f'^[Бб].+{os.environ["COMMAND_ID"]}$')
MESSAGE_PATTERNS = {
    'the-queue-has-begun': f'Hey! The queue has begun!',
    'get-ready': f'Get ready! There are {SECOND_NOTIFICATION_THRESHOLD} people left before you in the queue',
    'go': f'Hey! {{name}} is waiting for you!\n{{link}}'
}
DELAY = 5  # seconds


def is_there_command(row: List[str]):
    return len(row) >= 2 and row[0] == '' and COMMAND_NAME_PATTERN.fullmatch(row[1])


def is_there_link(row: List[str]):
    return len(row) >= 4 and len(row[2]) > 0 and len(row[3]) > 0


def make_notification_message(rows: List[List[str]], n_notifications_: int):
    for i, row in enumerate(rows):
        if is_there_command(row) and not is_there_link(row) and n_notifications_ == 0:
            return MESSAGE_PATTERNS['the-queue-has-begun']
        elif is_there_command(row) and not is_there_link(row) and n_notifications_ == 1 and (
                i >= SECOND_NOTIFICATION_THRESHOLD and is_there_link(rows[i - SECOND_NOTIFICATION_THRESHOLD - 1]) or i < SECOND_NOTIFICATION_THRESHOLD + 1
        ):
            return MESSAGE_PATTERNS['get-ready']
        elif is_there_command(row) and is_there_link(row) and n_notifications_ == 2:
            return MESSAGE_PATTERNS['go'].format(name=row[2], link=row[3])


if __name__ == "__main__":
    telegram_adapter = TelegramAdapter(token=os.environ['TG_API_KEY'], chat_id=int(os.environ['CHAT_ID']))
    sheets_adapter = GoogleSheetsAdapter(spreadsheet_id=os.environ['SHEETS_ID'], api_key_path=os.environ['GOOGLE_SHEETS_API_CREDS_PATH'])
    n_notifications = 0
    while True:
        notification_message = make_notification_message(sheets_adapter.read(int(os.environ['SHEET_ID'])), n_notifications_=n_notifications)
        if notification_message is not None:
            telegram_adapter.send(notification_message)
            n_notifications += 1
        if n_notifications < 3:
            print(f'{datetime.now()} Hmm... There are no changes')
            sleep(DELAY)
        else:
            break
