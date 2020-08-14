"""
.. module:: models
   :synopsis: Contains database action primitives.
.. moduleauthor:: AB <github.com/house-of-vanity>
"""

import sqlite3
import logging
import os

log = logging.getLogger(__name__)

class DBInitException(Exception):
    """ Exception at DB Init """


# class DataBase create or use existent SQLite database file. It provides 
# high-level methods for database.
class DataBase:
    """This class create or use existent SQLite database file. It provides 
    high-level methods for database."""
    def __init__(self, scheme, basefile='/usr/share/gaspar/data.sqlite'):
        """
          Constructor creates new SQLite database if 
          it doesn't exist. Uses SQL code from file for DB init.
          :param scheme: sql filename
          :type scheme: string
          :return: None
        """
        self.scheme = ''
        self.basefile = basefile
        try:
            conn = self.connect(basefile=basefile)
            log.info("Using '%s' base file.", os.path.realpath(basefile))
        except:
            log.debug('Could not connect to DataBase.')
            return None
        with open(scheme, 'r') as scheme_sql:
            sql = scheme_sql.read()
            self.scheme = sql
            if conn is not None:
                try:
                    cursor = conn.cursor()
                    cursor.executescript(sql)
                except Exception as e:
                    log.debug('Could not create scheme - %s', e)
                    raise DBInitException
            else:
                log.debug("Error! cannot create the database connection.")
                raise DBInitException
        log.info('DB connected.')
        self.close(conn)

    def connect(self, basefile):
        """
          Create connect object for basefile
          :param basefile: SQLite database filename
          :type basefile: string
          :return: sqlite3 connect object
        """
        #log.debug("Open connection to %s", basefile)
        return sqlite3.connect(basefile, check_same_thread=False)

    def execute(self, sql, params):
        """
          Execute SQL code. First of all connect to self.basefile. Close 
          connection after execution.
          :param sql: SQL code
          :type sql: string
          :return: list of response. Empty list when no rows are available.
        """
        conn = self.connect(basefile=self.basefile)
        log.debug("Executing: %s %s", sql, params)
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        result = cursor.fetchall()
        self.close(conn)
        return result

    def close(self, conn):
        """
          Close connection object instance.
          :param conn: sqlite3 connection object
          :type conn: object
          :return: None
        """
        #log.debug("Close connection to %s", self.basefile)
        conn.close()

    def copy_to_history(self, tor_id):
        sql = "SELECT * FROM torrents WHERE id = ?"
        attrs = self.execute(sql, (tor_id,))[0]
        sql = """INSERT OR IGNORE INTO torrents_history(
                    'id', 
                    'info_hash', 
                    'forum_id', 
                    'poster_id', 
                    'size', 
                    'reg_time', 
                    'tor_status', 
                    'seeders', 
                    'topic_title', 
                    'seeder_last_seen'
                )  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ? )"""
        self.execute(sql, attrs)

    def add_client(self, user_id, scheme, hostname, port, username, password, path):
        sql = """INSERT OR REPLACE INTO tr_clients(user_id, scheme, hostname, port, username, password, path)
                    VALUES(?, ?, ?, ?, ?, ?, ?);"""
        self.execute(sql, (user_id, scheme, hostname, port, username, password, path))

    def get_client(self, user_id):
        sql = "SELECT scheme, hostname, port, username, password, path FROM tr_clients WHERE user_id = ?"
        return self.execute(sql, (user_id,))[0]

    def get_attr(self, tor_id, attr):
        sql = """SELECT %s FROM torrents WHERE id = ? ORDER BY reg_time DESC LIMIT 1""" % attr
        return self.execute(sql, (tor_id,))[0][0]

    def update(self, tor_data):
        self.copy_to_history(tor_data["id"])
        sql = """UPDATE torrents SET
                    'info_hash' = ?, 
                    'forum_id' = ?, 
                    'poster_id' = ?, 
                    'size' = ?, 
                    'reg_time' = ?, 
                    'tor_status' = ?, 
                    'seeders' = ?, 
                    'topic_title' = ?, 
                    'seeder_last_seen' = ?
                WHERE id = ?
        """
        self.execute(sql, (
                        tor_data["info_hash"],
                        tor_data["forum_id"],
                        tor_data["poster_id"],
                        int(tor_data["size"]),
                        int(tor_data["reg_time"]),
                        tor_data["tor_status"],
                        tor_data["seeders"],
                        tor_data["topic_title"],
                        tor_data["seeder_last_seen"],
                        tor_data["id"],
                    ))

    def save_tor(self, tor_data):
        sql = """INSERT OR IGNORE INTO torrents(
                    'id', 
                    'info_hash', 
                    'forum_id', 
                    'poster_id', 
                    'size', 
                    'reg_time', 
                    'tor_status', 
                    'seeders', 
                    'topic_title', 
                    'seeder_last_seen'
                )  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        self.execute(sql, (
                        tor_data["id"],
                        tor_data["info_hash"],
                        tor_data["forum_id"],
                        tor_data["poster_id"],
                        int(tor_data["size"]),
                        int(tor_data["reg_time"]),
                        tor_data["tor_status"],
                        tor_data["seeders"],
                        tor_data["topic_title"],
                        tor_data["seeder_last_seen"],
                    ))
    def save_user(self, chat_instance):
        sql = """INSERT OR IGNORE INTO users(
                'id',
                'username',
                'first_name',
                'last_name'
                ) VALUES (?, ?, ?, ?)"""
        self.execute(sql, (
                    chat_instance['id'],
                    chat_instance['username'],
                    chat_instance['first_name'],
                    chat_instance['last_name'],
                    ))
    def save_alert(self, user_id, tor_id):
        sql = """INSERT OR IGNORE INTO alerts(
                'user_id',
                'tor_id'
                ) VALUES (?, ?)"""
        self.execute(sql, (
                    user_id,
                    tor_id
                    ))

    def get_alerts(self, user_id=None):
        if user_id:
            sql = """SELECT t.size, t.reg_time, t.topic_title, t.id, t.info_hash FROM 
                    torrents t LEFT JOIN alerts a ON a.tor_id = t.id
                    WHERE a.user_id = ?"""
            raw = self.execute(sql, (
                        user_id,
                        ))
        else:
            sql = """SELECT t.size, t.reg_time, t.topic_title, t.id, t.info_hash FROM 
                    torrents t LEFT JOIN alerts a ON a.tor_id = t.id GROUP BY t.id"""
            raw = self.execute(sql, ())
        alerts = list()
        for alert in raw:
            tmp = dict()
            tmp['id'] = alert[3]
            tmp['reg_time'] = alert[1]
            tmp['topic_title'] = alert[2]
            tmp['size'] = alert[0]
            tmp['info_hash'] = alert[4]
            alerts.append(tmp)
        return alerts

    def get_subscribers(self, tor_id):
        sql = "SELECT user_id FROM alerts WHERE tor_id = ?"
        subs = list()
        for sub in self.execute(sql, (tor_id,)):
            subs.append(sub[0])
        return subs
    


