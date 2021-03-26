from transmission_rpc import Client
import logging

log = logging.getLogger(__name__)

def easy_send(torent, client_id):
    try:
        scheme, hostname, port, username, password, path = torent.db.get_client_rpc(client_id['id'])
        if send_to_client_rpc(scheme, hostname, port, username, password, path, torent.meta['info_hash']):
            log.info("Push update to client Transmission RPC for %s", torent.meta['topic_title'])
    except Exception as e:
        log.warning("Failed push update to client Transmission RPC for %s: %s",
                    torent.meta['topic_title'], e)


def send_to_client_rpc(scheme, hostname, port, username, password, path, tor_hash):
    try:
        c = Client(
            host=hostname,
            port=port,
            username=username,
            password=password,
            protocol=scheme,
            path=path)
        m = f'magnet:?xt=urn:btih:{tor_hash}'
        c.add_torrent(m)
        return True
    except:
        return False


def check_connection(scheme, hostname, port, username, password, path):
    try:
        c = Client(
            host=hostname,
            port=port,
            username=username,
            password=password,
            protocol=scheme,
            path=path)
        return True if c.rpc_version else False
    except:
        return False
