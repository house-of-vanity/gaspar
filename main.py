import os
import logging
from urllib import parse
from rutracker import Torrent
from notify import update_watcher
from datetime import datetime
from database import DataBase
from telegram import *
from telegram.ext import Updater, MessageHandler, CommandHandler, filters

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger("gaspar.%s" % __name__)

torrent = Torrent()

def sizeof_fmt(num, suffix='B'):
    num = int(num)
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def main():
    token = os.environ.get('TG_TOKEN')
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
        reg_time = datetime.utcfromtimestamp(int(torrent.meta['reg_time'])
                ).strftime('%b-%d-%Y')
        msg = f"""{torrent.meta['topic_title']}
<b>Size:</b> {sizeof_fmt(torrent.meta['size'])}
<b>Hash: </b> {torrent.meta['info_hash']}
<b>Updated: </b>{reg_time}"""
        update.message.reply_text(msg, parse_mode='HTML')


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
            reg_time = datetime.utcfromtimestamp(int(alert['reg_time'])
                    ).strftime('%b-%d-%Y')
            msg += f"""<a href='https://rutracker.org/forum/viewtopic.php?t={alert['id']}'><b>{alert['topic_title']}</b></a>
    <b>💿Size:</b> {sizeof_fmt(alert['size'])}
    <b>#️⃣Hash: </b> {alert['info_hash']}
    <b>📅Updated: </b>{reg_time}\n"""
        update.message.reply_text(msg, parse_mode='HTML', disable_web_page_preview=True)


    updater = Updater(token, use_context=True)
    update_watcher(updater.bot)

    updater.dispatcher.add_handler(MessageHandler(filters.Filters.text, add))
    updater.dispatcher.add_handler(CommandHandler('list', list_alerts))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
