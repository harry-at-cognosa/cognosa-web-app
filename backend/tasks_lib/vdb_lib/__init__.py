from common.helpers import split2list

def get_host_port_from_url(url: str, default_port: int = 8000) -> tuple[str, int]:
    """
    Parse url e.g.:
      "localhost:8010" -> ("localhost", 8010)
      "localhost" -> ("localhost", 8000)
    """
    url_parts = split2list(url, ':')
    host = url_parts[0]
    port = int(url_parts[1]) if (len(url_parts) > 1) else default_port
    return host, port
