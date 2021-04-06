# !/usr/bin/env python
# -*- coding:utf-8 -*-

# Import Modules
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (Updater, MessageHandler, Filters, CallbackContext, CommandHandler, ConversationHandler)
import configparser
from pathlib import Path
import sys

# Import Class
from src.chillyLogger import get_logger
from src.userHandler import get_is_user_registered, register_new_user, get_all_active_users, update_user_entry

# Define global REPO_PATH
REPO_PATH = str((Path(sys.argv[0]).parents[1]).resolve())

# Globals
_LOGGER = get_logger(__file__)

# config handler
TELEGRAM_CFG = configparser.ConfigParser()
configFilePath = REPO_PATH + r'/config/config.cfg'
TELEGRAM_CFG.read(configFilePath)


def help(update: Update, _: CallbackContext) -> int:
    reply_keyboard = [['Stumm', 'Laut', 'Expert', 'Basic', 'Graph']]
    update.message.reply_text(
        "Wähle eine der folgenden Optionen", reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return ConversationHandler.END


def cancel(update: Update, _: CallbackContext) -> int:
    update.message.reply_text(
        'Hilfe abgebrochen!', reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


class TelegramHandler:
    def __init__(self, token):
        self.token = token
        self.password = TELEGRAM_CFG.get('telegram', 'password')
        self.updater = False
        self.bot = False
        self.graph_request = False

    def start(self):
        # Create the Updater and pass it your bot's token.
        # Make sure to set use_context=True to use the new context based callbacks
        # Post version 12 this will no longer be necessary
        self.updater = Updater(self.token, use_context=True)

        # Get the dispatcher to register handlers
        dispatcher = self.updater.dispatcher
        self.bot = self.updater.bot

        # Conversation handler is started with /help
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('help', help)],
            states={
                1: [MessageHandler(Filters.regex('^(Stumm|Laut|Expert|Basic|Graph)$'), self.handle_new_text_message)],
            },
            fallbacks=[CommandHandler('cancel', cancel)],
        )

        dispatcher.add_handler(conv_handler)

        # Message handler for message send outside the conversation handler
        dispatcher.add_handler(
            MessageHandler(Filters.text & ~Filters.command, self.handle_new_text_message, run_async=True))

        # Start the Bot
        self.updater.start_polling()

    def handle_new_text_message(self, update: Update, _: CallbackContext) -> int:
        # Get user properties
        local_user = update.message.from_user
        local_message = update.message.text
        local_id = local_user["id"]
        local_firstname = local_user["first_name"]
        try:
            local_lastname = local_user["last_name"]
        except KeyError:
            local_lastname = "None"

        # Register new user
        if not get_is_user_registered(local_id):
            if local_message == str(TELEGRAM_CFG.get('telegram', 'password')):
                if register_new_user(local_id, local_firstname, local_lastname):
                    update.message.reply_text('Du bist jetzt registriert!')
                else:
                    update.message.reply_text('Registrierung war nicht erfolgreich! ')
            else:
                update.message.reply_text('Du bist nicht registriert! Bitte passwort eingeben')

        else:
            if local_message == 'Status':
                update.message.reply_text('Ich bin noch da!')

            elif local_message == 'Stumm' and update_user_entry(local_id, 'notification', False):
                update.message.reply_text('Ich informiere dich nicht mehr!')

            elif local_message == 'Laut' and update_user_entry(local_id, 'notification', True):
                update.message.reply_text('Ich informiere dich absofort!')

            elif local_message == 'Expert' and update_user_entry(local_id, 'type', 'Expert'):
                update.message.reply_text('Du bist jetzt Experte! Nice!')

            elif local_message == 'Basic' and update_user_entry(local_id, 'type', 'Basic'):
                update.message.reply_text('Du bist jetzt Basic Nutzer!')

            elif local_message == 'Graph':
                self.graph_request = True

            else:
                update.message.reply_text('Das ist kein gültiger Befehl. Für hilfe /help ')

    def graph_requested(self):
        if self.graph_request:
            self.graph_request = False
            return True
        else:
            return False

    def send_message(self, txt, level='Basic'):
        local_active_users = get_all_active_users()
        if local_active_users:
            for user in local_active_users:
                if user['notification']:
                    if level == user['type'] or level == 'Basic':
                        self.bot.send_message(user['id'], txt)
                        _LOGGER.debug("Send Message: " + str(txt))

    def send_html(self, png_path):
        local_active_users = get_all_active_users()
        if local_active_users:
            for user in local_active_users:
                if user['notification']:
                    self.bot.send_document(user['id'], document=open(png_path, 'rb'))
                    _LOGGER.debug("Send HTML: " + str(png_path))
