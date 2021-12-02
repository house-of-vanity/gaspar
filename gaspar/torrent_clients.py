#from .transmission import easy_send
#from transmission_rpc import Client
import qbittorrentapi as qbt
import transmission_rpc as transm
from urllib import parse
import logging
from .rutracker import Torrent
from .transmission import send_to_client_rpc as send_to_transm
from .qbittorrent import send_to_client_rpc as send_to_qbt

log = logging.getLogger(__name__)

def easy_send(torrent_hash, user_id):
    try:
        torrent = Torrent()
        scheme, hostname, port, username, password, path = torrent.db.get_client_rpc(user_id)
        user_pass = f"{username}:{password}@" if password and username else ""
        tr_client_check = detect_client(f"{scheme}://{user_pass}{hostname}:{port}{path if path != None else ''}")
        if tr_client_check == "Transmission":
            if send_to_transm(scheme, hostname, port, username, password, path, torrent_hash):
                log.info(f"Push update to client {tr_client_check} RPC for %s", torrent_hash)
        elif tr_client_check == "qBittorrent":
            if send_to_qbt(scheme, hostname, port, username, password, path, torrent_hash):
                log.info(f"Push update to client {tr_client_check} RPC for %s", torrent_hash)
        else:
            return False

    except Exception as e:
        log.warning("Failed push update to client for %s: %s",
                    torrent_hash, e)
    return True

def _parse_address(address):
    client = {}
    try:
        tr = parse.urlparse(address)
        client["scheme"] = tr.scheme if tr.scheme else False
        client["hostname"] = tr.hostname if tr.hostname else False
        client["username"] = tr.username if tr.username else None
        client["password"] = tr.password if tr.password else None
        client["path"] = tr.path if tr.path else None
        client["port"] = tr.port if tr.port else (80 if client["scheme"] == 'http' else 443)
    except Exception as e:
        log.debug("_parse_address: %s", e)
        pass
    return client

def detect_client(address):
    client = False
    tr = _parse_address(address)
    # Check for qBittorrent v4.3.8+
    try:
        qbt_client = qbt.Client(
                host=f"{tr['scheme']}://{tr['hostname']}",
                port=tr['port'],
                username=tr['username'],
                password=tr['password'])
        try:    
                qbt_client.auth_log_in()
        except qbt.LoginFailed as e:
            pass
        client = "qBittorrent"
    except Exception as e:
        log.debug("detect_client.qBittorrent: %s", e)
        pass
    # Check for Transmission
    try:
        c = transm.Client(
            host=tr['hostname'],
            port=tr['port'],
            username=tr['username'],
            password=tr['password'],
            protocol=tr['scheme'],
            path=tr['path'])
        c.rpc_version
        client = "Transmission"
    except Exception as e:
        log.debug("detect_client.Transmission: %s", e)
        pass
    log.info(f"Detected {client}")
    return client

def add_client(address, u_id):
    tr = _parse_address(address)
    client = detect_client(address)
    if not client:
        return client
    if Torrent().db.add_client_rpc(
            u_id,
            tr['scheme'],
            tr['hostname'],
            tr['port'],
            tr['username'],
            tr['password'],
            tr['path']):
        return f"Added {client}"
