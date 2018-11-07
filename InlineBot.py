#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
    Bot für Telegram zur einfachen Integration der TH Köln
    in Telegram

    t.me/th_koeln_bot
"""
import requests
import logging
from bs4 import BeautifulSoup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ChatAction, ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from functools import wraps
from time import sleep
import random

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', # Logger. Gibt fehler in ausführender Kommandozeile aus
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Mensaplan Scraping
# Greift sich die aktuellen Mensapläne für heute und gibt sie
# in die Variable 'Mensaplan'
# /////////////////////////
def grab_mensaplan():
    Mensaplan = ''
    page = requests.get('https://www.imensa.de/koeln/mensa-iwz-deutz/index.html') # Lädt reinen HTML-Code runter
    soup = BeautifulSoup(page.content, 'html.parser') # gruppiert den HTML-Code als Database

    descriptionPool = soup.find_all('p', class_='aw-meal-description') # Alle Essensbeschreibungen für heute (starten bei index 0)
    pricePool = soup.find_all('div', title='Preis für Studierende') # Alle Preise für heute (starten bei index 1!!)

    for i in range(len(descriptionPool)):
        Mensaplan += (descriptionPool[i].get_text() + '\t' + pricePool[i+1].get_text() + '\n\n')

    random.seed()
    Mensaplan += '\nDer 🤖 empfiehlt:\n'
    Mensaplan += descriptionPool[random.randint(0,len(descriptionPool))].get_text()
    return Mensaplan
# /////////////////////////
# /Mensaplan

# Decorator
# Zeigt die "tippt..." Benachrichtigung an
# /////////////////////////
def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        def command_func(*args, **kwargs):
            bot, update = args
            bot.send_chat_action(chat_id=update.message.chat_id, action=action)
            func(bot, update, **kwargs)
        return command_func
    
    return decorator
# /////////////////////////
# /Decorator

linkList = open('./linklist.txt', 'r') # Txt File für Linkliste

def start(bot, update):
    keyboard = [[InlineKeyboardButton("Mensaplan", callback_data='1'),
                 InlineKeyboardButton("Linkliste", callback_data='2')],

                [InlineKeyboardButton("Holger", callback_data='3')]]

    reply_markup = ReplyKeyboardRemove()
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Hauptmenü', reply_markup=reply_markup)


def button(bot, update):
    query = update.callback_query

    #bot.edit_message_text(text="Selected option: {}".format(query.data), chat_id=query.message.chat_id, message_id=query.message.message_id)
    if query.data == '1':
        bot.edit_message_text(text=grab_mensaplan(), chat_id=query.message.chat_id, message_id=query.message.message_id)
    if query.data == '2':
        bot.edit_message_text(text=linkList.read(), chat_id=query.message.chat_id, message_id=query.message.message_id)
    if query.data == '3':
        bot.edit_message_text(text="Gott der Mathematik:", chat_id=query.message.chat_id, message_id=query.message.message_id)
        bot.send_photo(chat_id=query.message.chat_id, photo=open('holger.png', 'rb'))


def mensa(bot, update):
    update.message.reply_text(grab_mensaplan())
    pass

def holger(bot, update):
    bot.send_photo(chat_id=update.message.chat_id, photo=open('holger.png', 'rb'))
    pass

def comment(bot, update):
    update.message.reply_text('Ideen für Features oder Bugs gefunden? Einfach an @finncyr schreiben.')
    pass

@send_action(ChatAction.TYPING)
def help(bot, update):
    update.message.reply_text("Use /start to test this bot.")
    pass


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

@send_action(ChatAction.TYPING)
def unknown(bot, update):
    sleep(0.5)
    bot.send_message(chat_id=update.message.chat_id, text="Unbekannter Befehl. Hast du dich vertippt?")
    pass


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater('778389061:AAF9haioZq8oD_fvvKMjiu5Xq-PWDOPpl9s')

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_handler(CommandHandler('mensa', mensa))
    updater.dispatcher.add_handler(CommandHandler('holger', holger))
    updater.dispatcher.add_handler(CommandHandler('comment', comment))
    updater.dispatcher.add_error_handler(error)
    updater.dispatcher.add_handler(MessageHandler(Filters.command, unknown))

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
