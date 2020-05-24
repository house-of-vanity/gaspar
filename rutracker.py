import urllib.request, json 
from database import DataBase
import logging
import re

log = logging.getLogger(__name__)

class Torrent:
    def __init__(self, tor_id, chat_instance):
        self.db = DataBase("scheme.sql")
        self.api_url = "http://api.rutracker.org/v1/"
        self.meta = self.get_tor_topic_data(tor_id)
        log.debug("Torrent info: %s", self.meta)
        self.db.save_tor(self.meta, chat_instance)

    def get_tor_topic_data(self, tor_id):
        data = dict()
        with urllib.request.urlopen(
                "{}/get_tor_topic_data?by=topic_id&val={}".format(
                    self.api_url, tor_id)) as url:
            data = json.loads(url.read().decode())
        data = data["result"][tor_id]
        data["id"] = tor_id
        return data

    def is_outdated(self):
        stored_reg_time = int(self.db.get_attr(self.meta["id"], 'reg_time'))
        actual_reg_time = self.meta["reg_time"]
        return actual_reg_time != stored_reg_time

    def update(self):
        self.db.update(self.meta)

    def episodes(self):
        ep_str = re.search(r"\[\d+(\+\d+)?(-\d+)?( +)?(из)?( +)?\d+(\+\d+)?(-\d+)?\]", self.meta["topic_title"]).group(0)
        return ep_str

