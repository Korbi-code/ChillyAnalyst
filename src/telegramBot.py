# !/usr/bin/env python
# -*- coding:utf-8 -*-

# Import Modules
import telepot
import os
import csv
import configparser
import sys
from pathlib import Path

# Define global REPO_PATH
REPO_PATH = str((Path(sys.argv[0]).parents[1]).resolve())

# config handler
TELEGRAM_CFG = configparser.ConfigParser()
configFilePath = REPO_PATH+r'/config/config.cfg'
TELEGRAM_CFG.read(configFilePath)


class TelegramHandler:
    def __init__(self):
        self.token = TELEGRAM_CFG.get('telegram', 'token')
        self.bot = telepot.Bot(self.token)
        self.subscribed_users_path = REPO_PATH+str(TELEGRAM_CFG.get('telegram', 'subscribed_users_path'))

        self.subscribed_users_file = self.subscribed_users_path +\
                                     str(TELEGRAM_CFG.get('telegram', 'subscribed_users_filename'))
        self.password = TELEGRAM_CFG.get('telegram', 'password')

        Path(self.subscribed_users_path).mkdir(parents=True, exist_ok=True)
        try:
            open(str(self.subscribed_users_file), 'r')
        except FileNotFoundError:
            open(str(self.subscribed_users_file), "w")

    def start_listening(self):
        messages = self.bot.getUpdates()
        if len(messages) > 0:
            next_message_id = messages[-1]['update_id'] + 1
            for msg in messages:
                self.handle_new_message(msg['message'])
            self.bot.getUpdates(next_message_id)  # Tell telegram the next id we would like to receive

    def handle_new_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        if content_type == "text":
            if str(self.password) in (msg["text"]):
                if self.handle_subscription_request(chat_id):
                    self.bot.sendMessage(chat_id, 'Your are now subscribed, Nice!')
                else:
                    self.bot.sendMessage(chat_id, 'You are already subscribed!')

    def handle_subscription_request(self, chat_id):
        if os.path.exists(self.subscribed_users_file):
            append_write = 'a'  # append if already exists

            # if file exists check if user is already on the list
            with open(self.subscribed_users_file, newline='') as csvfile:
                reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
                for row in reader:
                    if int(chat_id) == int(row[0]):
                        return False
        else:
            append_write = 'w'  # make a new file if not

        with open(self.subscribed_users_file, append_write, newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=' ',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow([chat_id])
            return True

    def send_message(self, txt):
        if os.path.exists(self.subscribed_users_file):
            with open(self.subscribed_users_file, newline='') as csvfile:
                reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
                for row in reader:
                    self.bot.sendMessage(row[0], txt)

    def send_html(self, png_path):
        if os.path.exists(self.subscribed_users_file):
            with open(self.subscribed_users_file, newline='') as csvfile:
                reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
                for row in reader:
                    self.bot.sendDocument(row[0], document=open(png_path, 'rb'))
