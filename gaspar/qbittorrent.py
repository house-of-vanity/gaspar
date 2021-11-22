import qbittorrentapi as qbt
import logging

log = logging.getLogger(__name__)

def easy_send(torent, client_id):
    try:
        scheme, hostname, port, username, password, path = torent.db.get_client_rpc(client_id['id'])
        if send_to_client_rpc(scheme, hostname, port, username, password, path, torent.meta['info_hash']):
            log.info("Push update to qBittorrent client for %s", torent.meta['topic_title'])
    except Exception as e:
        log.warning("Failed push update to qBittorrent client for %s: %s",
                    torent.meta['topic_title'], e)


def send_to_client_rpc(scheme, hostname, port, username, password, path, tor_hash):
    try:
        host = f"{scheme}://{hostname}{path if path != None else ''}"
        c = qbt.Client(
            host=host,
            port=port,
            username=username,
            password=password)
        m = f'magnet:?xt=urn:btih:{tor_hash}'
        c.torrents_add(urls=m)
        return True
    except Excepion as exc:
        log.warn("Failed to send to qBittorrent: %s", host)
        return False
