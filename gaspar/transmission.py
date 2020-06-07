from transmission_rpc import Client

def add_tor(tor_hash):
  c = Client(host='msk.hexor.ru', port=80)
  m = f'magnet:?xt=urn:btih:{tor_hash}'
  c.add_torrent(m)


