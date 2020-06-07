import os
import sys
import logging
from urllib import parse
from telegram import *
from telegram.ext import Updater, MessageHandler, CommandHandler, filters
from .rutracker import Torrent
from .notify import update_watcher
from .database import DataBase
from .tools import format_topic

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

torrent = Torrent()

def main():
    token = os.environ.get('TG_TOKEN')
    if not token:
        log.error("Env var TG_TOKEN isn't set.")
        sys.exit(1)
    """Run bot."""

    def add(update, context):
        if 'https://rutracker.org' in update.message.text:
            try:
                tor_id = parse.parse_qs(parse.urlsplit(update.message.text).query)['t'][0]
            except KeyError:
                log.warn("URL provided doesn't contains any torrent id.")
                update.message.reply_text("URL provided doesn't contains any torrent id.")
                return
        else:
            update.message.reply_text("Send me a URL to rutracker.org topic.")
            return
        log.info(
                "Got /add request from user [%s] %s",
                update.message.chat['id'],
                update.message.from_user.username)
        torrent = Torrent(tor_id)
        torrent.db.save_tor(torrent.meta)
        torrent.db.save_user(update.message.chat)
        torrent.db.save_alert(update.message.chat['id'], torrent.meta['id'])
        msg = format_topic(
                torrent.meta['id'],
                torrent.meta['topic_title'],
                torrent.meta['size'],
                torrent.meta['info_hash'],
                torrent.meta['reg_time'],
                pre='You will be alerted about\n')
        update.message.reply_text(msg, parse_mode='HTML', disable_web_page_preview=True)


    def list_alerts(update, context):
        log.info(
                "Got /list request from user [%s] %s",
                update.message.chat['id'],
                update.message.from_user.username)
        alerts = torrent.db.get_alerts(update.message.chat['id'])
        if len(alerts) == 0:
            update.message.reply_text("You have no configured alerts.")
            return True
        msg = "<b>Configured alerts:</b>\n"
        for alert in alerts:
            msg += format_topic(
                    alert['id'],
                    alert['topic_title'],
                    alert['size'],
                    alert['info_hash'],
                    alert['reg_time'],
                    pre="\n")
        update.message.reply_text(msg, parse_mode='HTML', disable_web_page_preview=True)


    updater = Updater(token, use_context=True)
    update_watcher(updater.bot)

    updater.dispatcher.add_handler(CommandHandler('list', list_alerts))
    updater.dispatcher.add_handler(MessageHandler(filters.Filters.text, add))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
