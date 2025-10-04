from dataclasses import dataclass
from urllib.parse import urlparse

@dataclass
class ParsedUrl:
    scheme: str = ''
    user: str = ''
    password: str = ''
    host: str = ''
    port: int = 0
    path: str = ''

    @property
    def full_url(self) -> str:
        full_url = ''
        if not self.host:
            return ''
        if self.scheme:
            full_url += f"{self.scheme}://"
        if self.user:
            full_url += self.user
        if self.password:
            full_url += f":{self.password}"
        if self.user:
            full_url += f"@"
        full_url += self.host
        if self.port:
            full_url += f':{self.port}'
        if self.path:
            full_url += f'/{self.path}'
        return full_url

    @classmethod
    def from_url(cls, url: str) -> "ParsedUrl":
        # Add a default scheme if missing so urlparse works correctly
        if "://" not in url:
            url = "noscheme://" + url

        parsed = urlparse(url)        
        scheme = parsed.scheme if parsed.scheme else ''
        if scheme == 'noscheme':
            scheme = ''
        user=parsed.username if parsed.username else ''
        password=parsed.password if parsed.password else ''
        host = parsed.hostname if parsed.hostname else ''
        host = '127.0.0.1' if (host == 'localhost') else host
        port=parsed.port if parsed.port else 0
        path=parsed.path.lstrip('/') if parsed.path else ''
        
        return cls(
            scheme,
            user,
            password,
            host,
            port,
            path
        )
