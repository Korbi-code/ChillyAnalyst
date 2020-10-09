import telepot


class TelegramHandler:
    def __init__(self, token):
        self.token = token
        self.bot = telepot.Bot(self.token)
        self.subscribed_users = []

    def start_listening(self):
        messages = self.bot.getUpdates()
        if len(messages) > 0:
            next_message_id = messages[-1]['update_id'] + 1
            for msg in messages:
                self.handle_new_message(msg['message'])
            self.bot.getUpdates(next_message_id)  # Tell telegram the next id we would like to recieve

    def handle_new_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        if content_type == "text":
            text_message = (msg["text"])
            if 'Password' in (msg["text"]):
                self.subscribed_users.append(chat_id)

    def send_message(self, txt):
        for chat_id in self.subscribed_users:
            self.bot.sendMessage(chat_id, txt)

    def send_png(self, chat_id, png_path):
        for chat_id in self.subscribed_users:
            self.bot.sendPhoto(chat_id, photo=open(png_path, 'rb'))
