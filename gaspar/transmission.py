from transmission_rpc import Client

def add_tor(scheme, hostname, port, username, password, path, tor_hash):
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

