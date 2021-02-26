import json
import logging
import re
import urllib.request

from .database import DataBase

log = logging.getLogger(__name__)


class Torrent:
    def __init__(self, tor_id=None):
        self.db = DataBase()
        self.api_url = "http://api.rutracker.org/v1/"
        self.tor_id = tor_id
        self.meta = None
        if self.tor_id != None:
            self.get_tor_topic_data(self.tor_id)
            log.debug("Torrent info: %s", self.meta)

    @property
    def tor_id(self):
        return self.__tor_id

    @tor_id.setter
    def tor_id(self, tor_id):
        self.__tor_id = tor_id
        if tor_id:
            return self.get_tor_topic_data(tor_id)

    def get_tor_topic_data(self, tor_id):
        data = dict()
        with urllib.request.urlopen(
                "{}/get_tor_topic_data?by=topic_id&val={}".format(
                    self.api_url, tor_id)) as url:
            data = json.loads(url.read().decode())
        data = data["result"][tor_id]
        try:
            data["id"] = tor_id
            log.info("Getting info for [%s] %s%s", tor_id, data["topic_title"][:60], '...')
            self.meta = data
        except TypeError:
            log.warning("Tor_id %s fetch failed, maybe removed on server.", tor_id)
            return False

    def is_outdated(self):
        if not self.tor_id:
            log.warn("Torrent id not presented.")
            return False
        stored_reg_time = int(self.db.get_attr(self.meta["id"], 'reg_time'))
        actual_reg_time = self.meta["reg_time"]
        return actual_reg_time != stored_reg_time

    def update(self):
        if not self.tor_id:
            log.warn("Torrent id not presented.")
            return False
        self.db.update(self.meta)

    def episodes(self):
        if not self.tor_id:
            log.warn("Torrent id not presented.")
            return False
        ep_str = re.search(r"\[\d+(\+\d+)?(-\d+)?( +)?(из)?( +)?\d+(\+\d+)?(-\d+)?\]", self.meta["topic_title"]).group(
            0)
        return ep_str
