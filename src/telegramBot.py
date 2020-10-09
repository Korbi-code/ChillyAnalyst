import telepot
import os
import csv


class TelegramHandler:
    def __init__(self, token, password, subscribed_users):
        self.token = token
        self.bot = telepot.Bot(self.token)
        self.subscribed_users = subscribed_users
        self.password = password

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
            if str(self.password) in (msg["text"]):
                if self.handle_subscription_request(chat_id):
                    self.bot.sendMessage(chat_id, 'Your are now subscribed, Nice!')
                else:
                    self.bot.sendMessage(chat_id, 'You are already subscribed!')

    def handle_subscription_request(self, chat_id):
        if os.path.exists(self.subscribed_users):
            append_write = 'a'  # append if already exists

            # if file exists check if user is already on the list
            with open(self.subscribed_users, newline='') as csvfile:
                reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
                for row in reader:
                    if int(chat_id) == int(row[0]):
                        return False
        else:
            append_write = 'w'  # make a new file if not

        with open(self.subscribed_users, append_write, newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=' ',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow([chat_id])
            return True

    def send_message(self, txt):
        if os.path.exists(self.subscribed_users):
            with open(self.subscribed_users, newline='') as csvfile:
                reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
                for row in reader:
                    self.bot.sendMessage(row[0], txt)

    def send_png(self, chat_id, png_path):
        if os.path.exists(self.subscribed_users):
            with open(self.subscribed_users, newline='') as csvfile:
                reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
                for row in reader:
                    self.bot.sendPhoto(row[0], photo=open(png_path, 'rb'))
