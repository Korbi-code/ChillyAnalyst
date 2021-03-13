# !/usr/bin/env python
# -*- coding:utf-8 -*-

# Import Modules
import os
import csv
from telegram import Update, ReplyKeyboardMarkup
import telegram
from telegram.ext import (Updater, MessageHandler, Filters, CallbackContext)
import configparser

# Import Class
from src.chillyLogger import *

# Define global REPO_PATH
REPO_PATH = str((Path(sys.argv[0]).parents[1]).resolve())

# Globals
_LOGGER = get_logger(__file__)

# config handler
TELEGRAM_CFG = configparser.ConfigParser()
configFilePath = REPO_PATH + r'/config/config.cfg'
TELEGRAM_CFG.read(configFilePath)


class TelegramHandler:
    def __init__(self, token):
        self.token = token

        self.subscribed_users_path = REPO_PATH + str(TELEGRAM_CFG.get('telegram', 'subscribed_users_path'))

        self.subscribed_users_file = self.subscribed_users_path + \
                                     str(TELEGRAM_CFG.get('telegram', 'subscribed_users_filename'))
        self.password = TELEGRAM_CFG.get('telegram', 'password')

        self.updater = False
        self.bot = False

        Path(self.subscribed_users_path).mkdir(parents=True, exist_ok=True)
        try:
            open(str(self.subscribed_users_file), 'r')
        except FileNotFoundError:
            open(str(self.subscribed_users_file), "w")

    def start(self):
        # Create the Updater and pass it your bot's token.
        # Make sure to set use_context=True to use the new context based callbacks
        # Post version 12 this will no longer be necessary
        self.updater = Updater(self.token, use_context=True)

        # Get the dispatcher to register handlers
        dispatcher = self.updater.dispatcher
        self.bot = self.updater.bot

        dispatcher.add_handler(
            MessageHandler(Filters.text & ~Filters.command, self.handle_new_text_message, run_async=True))

        # Start the Bot
        self.updater.start_polling()

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
        if message == str(TELEGRAM_CFG.get('telegram', 'Password')):
            self.handle_subscription_request(id)

        # Get alive message from bot
        if message == 'Status':
            update.message.reply_text('Still running!')

    def handle_subscription_request(self, chat_id):
        if os.path.exists(self.subscribed_users_file):
            append_write = 'a'  # append if already exists

            # if file exists check if user is already on the list
            with open(self.subscribed_users_file, newline='') as csvfile:
                reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
                for row in reader:
                    if int(chat_id) == int(row[0]):
                        _LOGGER.debug("User already on list: " + str(chat_id))
                        return False
        else:
            append_write = 'w'  # make a new file if not

        with open(self.subscribed_users_file, append_write, newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=' ',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow([chat_id])
            _LOGGER.info("New user registered with chat_id: " + str(chat_id))
            return True

    def send_message(self, txt):
        if os.path.exists(self.subscribed_users_file):
            with open(self.subscribed_users_file, newline='') as csvfile:
                reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
                for row in reader:
                    self.bot.send_message(row[0], txt)
                    _LOGGER.debug("Send Message: " + str(txt))

    def send_html(self, png_path):
        if os.path.exists(self.subscribed_users_file):
            with open(self.subscribed_users_file, newline='') as csvfile:
                reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
                for row in reader:
                    self.bot.send_document(row[0], document=open(png_path, 'rb'))
                    _LOGGER.debug("Send HTML: " + str(png_path))

    def send_user_question(self):
        reply_keyboard = [[' < 1 Stunde ', '>= 1 Stunde']]

        self.bot.reply_text(
            'Wird der Waschvorgang länger oder kürzer als eine Stunde laufen ?',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        )
