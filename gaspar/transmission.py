from transmission_rpc import Client
import logging

log = logging.getLogger(__name__)

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
