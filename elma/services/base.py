from typing import TYPE_CHECKING

import requests

if TYPE_CHECKING:
    from ..main import API


class Service:
    __slots__ = "host", "headers", "parent"

    def __init__(self, host: str, session_headers: dict, parent: "API"):
        self.host = host.rstrip("/")
        self.headers = session_headers
        self.parent = parent

    @property
    def session(self) -> requests.Session:
        session = requests.Session()
        session.headers = self.headers
        return session
