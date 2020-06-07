from transmission_rpc import Client

def add_tor(host, port, tor_hash):
  c = Client(host=host, port=port)
  m = f'magnet:?xt=urn:btih:{tor_hash}'
  c.add_torrent(m)


