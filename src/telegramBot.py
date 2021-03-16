# !/usr/bin/env python
# -*- coding:utf-8 -*-

# Import Modules
import os
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
import telegram
from telegram.ext import (Updater, MessageHandler, Filters, CallbackContext, CallbackQueryHandler, ConversationHandler,
                          CommandHandler)
import configparser

# Import Class
from src.chillyLogger import *
from src.userHandler import *

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
        self.password = TELEGRAM_CFG.get('telegram', 'password')
        self.updater = False
        self.bot = False

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

        dispatcher.add_handler(CallbackQueryHandler(self.selected_button))

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
        if message == str(TELEGRAM_CFG.get('telegram', 'password')):
            if not get_is_user_registered(id):
                register_new_user(id, firstname, lastname)

        # Get alive message from bot
        if message == 'Status':
            update.message.reply_text('Still running!')

        if message == 'Stumm':
            update_user_entry(id, 'notification', False)

        if message == 'Laut':
            update_user_entry(id, 'notification', True)

        if message == 'Expert':
            update_user_entry(id, 'type', 'Expert')

        if message == 'Basic':
            update_user_entry(id, 'type', 'Basic')

    def send_message(self, txt, level='Basic'):
        active_users = get_all_active_users()
        if active_users:
            for user in active_users:
                if user['notification']:
                    if level == user['type'] or level == 'Basic':
                        self.bot.send_message(user['id'], txt)
                        _LOGGER.debug("Send Message: " + str(txt))

    def send_html(self, png_path):
        active_users = get_all_active_users()
        if active_users:
            for user in active_users:
                if user['notification']:
                    self.bot.send_document(user['id'], document=open(png_path, 'rb'))
                    _LOGGER.debug("Send HTML: " + str(png_path))

    def send_user_question(self):
        keyboard = [
            [
                InlineKeyboardButton("< 1 Stunde", callback_data='1'),
                InlineKeyboardButton(">= 1 Stunde", callback_data='2'),
            ],
            [InlineKeyboardButton("Weiß nicht", callback_data='3')],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        active_users = get_all_active_users()
        if active_users:
            for user in active_users:
                self.bot.send_message(user['id'], 'Wird der Waschvorgang länger oder kürzer als eine Stunde laufen ?',
                                      reply_markup=reply_markup)

    def selected_button(self, update: Update, _: CallbackContext) -> None:
        query = update.callback_query
        query.answer()
        query.edit_message_text(text=f"Selected option: {query.data}")
