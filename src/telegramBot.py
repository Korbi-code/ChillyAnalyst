# !/usr/bin/env python
# -*- coding:utf-8 -*-

# Import Modules
import telepot
import os
import csv
import configparser
import sys
from pathlib import Path

from telegram import Update
import telegram
from telegram.ext import (Updater, MessageHandler, Filters, CallbackContext)


# Define global REPO_PATH
REPO_PATH = str((Path(sys.argv[0]).parents[1]).resolve())

# config handler
TELEGRAM_CFG = configparser.ConfigParser()
configFilePath = REPO_PATH + r'/config/config.cfg'
TELEGRAM_CFG.read(configFilePath)


class TelegramHandler:
    def __init__(self,token):
        self.token = token

        self.subscribed_users_path = REPO_PATH + str(TELEGRAM_CFG.get('telegram', 'subscribed_users_path'))

        self.subscribed_users_file = self.subscribed_users_path + \
                                     str(TELEGRAM_CFG.get('telegram', 'subscribed_users_filename'))
        self.password = TELEGRAM_CFG.get('telegram', 'password')

        Path(self.subscribed_users_path).mkdir(parents=True, exist_ok=True)
        try:
            open(str(self.subscribed_users_file), 'r')
        except FileNotFoundError:
            open(str(self.subscribed_users_file), "w")

    def start(self):
        # Create the Updater and pass it your bot's token.
        # Make sure to set use_context=True to use the new context based callbacks
        # Post version 12 this will no longer be necessary
        updater = Updater(self.token, use_context=True)

        # Get the dispatcher to register handlers
        dispatcher = updater.dispatcher

        dispatcher.add_handler(
            MessageHandler(Filters.text & ~Filters.command, self.handle_new_text_message, run_async=True))

        # Start the Bot
        updater.start_polling()


    def handle_new_text_message(self, update: Update, context: CallbackContext) -> int:
        # Get user properties
        user = update.message.from_user
        message = update.message.text
        id = user["id"]
        firstname = user["first_name"]
        try:
            lastname = user["last_name"]
        except KeyError:
            lastname = "None"

        # Register new user
        update.message.reply_text('Hallo ' + firstname + '!\n')

        # Get alive message from bot
        if message == 'Status':
            update.message.reply_text('Still running!')

        if message == str(TELEGRAM_CFG.get('telegram', 'Password')):
            self.handle_subscription_request(id)

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
            bot = telegram.Bot(self.token)
            with open(self.subscribed_users_file, newline='') as csvfile:
                reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
                for row in reader:
                    bot.send_message(row[0], txt)
                    print("Send Messag",txt)

    def send_html(self, png_path):
        if os.path.exists(self.subscribed_users_file):
            bot = telegram.Bot(self.token)
            with open(self.subscribed_users_file, newline='') as csvfile:
                reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
                for row in reader:
                    bot.send_document(row[0], document=open(png_path, 'rb'))
                    print("Send HTML",png_path)
