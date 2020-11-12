#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
import tempfile
import time

import dotenv
from selenium.common.exceptions import (
    WebDriverException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, \
    CallbackContext

from utils import selenium, check_url_validity

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

dotenv.load_dotenv()
site_loading_timeout = int(os.getenv('WAIT_PAGE_TO_LOAD_SECONDS'))

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Send me a link and I will try making screenshot of that '
                              'place!')


def screenshot(update: Update, context: CallbackContext) -> None:
    """Send a screenshot of a webpage."""
    url = update.message.text

    if not check_url_validity(url):
        update.message.reply_text(f'Url {url} is not valid')
        return

    with selenium() as browser:
        browser.get(url)
        # we need separate sleep to let site load initial structure and elements
        time.sleep(site_loading_timeout/2)
        try:
            WebDriverWait(browser, site_loading_timeout/2).until(
                expected_conditions.visibility_of_element_located((By.TAG_NAME, "body"))
            )
        except WebDriverException:
            update.message.reply_text("Problem loading page")
            return
        try:
            browser.set_window_size(
                1920,
                browser.execute_script('return document.body.parentNode.scrollHeight')
            )
            body = browser.find_element_by_tag_name('body').screenshot_as_png
        # there is a chance of page having 0 height (e.g. Youtube)
        except Exception:
            update.message.reply_text("Error getting picture of the whole page")
            return
    # telegram expects file-like object to be sent, so we use temporaryfile
    update.message.reply_photo(body)
    tmp_file = tempfile.TemporaryFile()
    tmp_file.write(body)
    tmp_file.seek(0)
    update.message.reply_photo(tmp_file)
    tmp_file.close()


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary

    updater = Updater(os.getenv('TOKEN'),
                      use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, screenshot))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
