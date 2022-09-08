from typing import TYPE_CHECKING

import requests

if TYPE_CHECKING:
    from ..main import API


class Service:
    __slots__ = "parent"

    def __init__(self, parent: "API"):
        self.parent = parent

    @property
    def session(self) -> requests.Session:
        session = requests.Session()
        session.headers = self.parent.headers
        return session
