import time
import threading
import logging
from rutracker import Torrent
from datetime import datetime

UPDATE_INTERVAL = 6 * 60 * 60 # in secs

log = logging.getLogger("gaspar.%s" % __name__)

torrent = Torrent()

def sizeof_fmt(num, suffix='B'):
    num = int(num)
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
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
                log.info("Checking for updates. Configured interval: %sh , [%s secs]", UPDATE_INTERVAL/60/60, UPDATE_INTERVAL)
                if update(alert['id']):
                    log.info("Found update for [%s] %s", torrent.meta['id'], torrent.meta['topic_title'])
                    reg_time = datetime.utcfromtimestamp(int(torrent.meta['reg_time'])
                            ).strftime('%b-%d-%Y')
                    msg = f"""<i>Topic updated</i>\n<a href='https://rutracker.org/forum/viewtopic.php?t={torrent.meta['id']}'><b>{torrent.meta['topic_title']}</b></a>
        <b>💿Size:</b> {sizeof_fmt(torrent.meta['size'])}
        <b>#️⃣Hash: </b> {torrent.meta['info_hash']}
        <b>📅Updated: </b>{reg_time}\n"""
                    subs = torrent.db.get_subscribers(alert['id'])
                    for sub in subs:
                        bot.sendMessage(sub, msg, parse_mode='HTML', disable_web_page_preview=True)
                    time.sleep(UPDATE_INTERVAL / 60 / 60 / 4.)
                time.sleep(UPDATE_INTERVAL)
    update_thread = threading.Thread(target=__thread)
    update_thread.start()
