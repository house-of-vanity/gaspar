import logging
import threading
import time
from datetime import datetime

from .rutracker import Torrent
from .tools import format_topic
from .torrent_clients import easy_send

UPDATE_INTERVAL = 2 * 60 * 60  # in secs.

log = logging.getLogger(__name__)

torrent = Torrent()


def sizeof_fmt(num, suffix='B'):
    num = int(num)
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def update(tor_id):
    torrent.tor_id = tor_id
    if torrent.is_outdated():
        log.info("%s if outdated. Updating.", torrent.meta['topic_title'])
        torrent.update()
        return True
    else:
        return False


def update_watcher(bot):
    def __thread():
        while True:
            alerts = list()
            raw = torrent.db.get_alerts()
            for alert in raw:
                alerts.append(alert['id'])
                log.info("Checking for updates. Configured interval: %sh , [%s secs]", UPDATE_INTERVAL / 60 / 60,
                         UPDATE_INTERVAL)
                log.info("Checking alert %s", alert['topic_title'])
                if update(alert['id']):
                    log.info("Found update for [%s] %s", torrent.meta['id'], torrent.meta['topic_title'])
                    reg_time = datetime.utcfromtimestamp(int(torrent.meta['reg_time'])
                                                         ).strftime('%b-%d-%Y')
                    msg = format_topic(
                        torrent.meta['id'],
                        torrent.meta['topic_title'],
                        torrent.meta['size'],
                        torrent.meta['info_hash'],
                        torrent.meta['reg_time'],
                        pre='<i>Topic has been updated</i>\n')
                    subs = torrent.db.get_subscribers(alert['id'])
                    for sub in subs:
                        try:
                            scheme, hostname, port, username, password, path = torrent.db.get_client_rpc(sub)
                            if easy_send(torrent.meta['info_hash'], sub):
                                log.info("Push update to client %s", torrent.meta['info_hash'])
                                msg = f"{msg}📨 <b>Sent to RPC /client</b>"
                            else:
                                log.warning("Failed push update to client Transmission RPC for %s",
                                            torrent.meta['info_hash'])
                        except:
                            pass
                        bot.sendMessage(sub, msg, parse_mode='HTML', disable_web_page_preview=True)

                    time.sleep(1)
                else:
                    log.info("There is no update for %s", alert['topic_title'])
            time.sleep(UPDATE_INTERVAL)

    update_thread = threading.Thread(target=__thread)
    update_thread.start()
