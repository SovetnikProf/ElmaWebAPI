import requests


class Service:
    def __init__(self, host: str, session_headers: dict):
        self.host = host.rstrip("/")
        self.headers = session_headers

    @property
    def session(self) -> requests.Session:
        session = requests.Session()
        session.headers = self.headers
        return session
