import telegram


class TelegramAdapter:
    def __init__(self, token: str, chat_id: int):
        self.bot = telegram.Bot(token=token)
        self.chat_id = chat_id

    def send(self, message: str):
        self.bot.send_message(chat_id=self.chat_id, text=message)
