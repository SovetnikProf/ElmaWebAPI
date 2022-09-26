from typing import TYPE_CHECKING

import requests

if TYPE_CHECKING:
    from ..api import API


class Service:
    """
    Базовый класс для сервисов.
    """

    __slots__ = ("parent",)

    def __init__(self, parent: "API"):
        self.parent = parent

    @property
    def session(self) -> requests.Session:
        """
        Сессия для взаимодействия с сервером Elma.
        """
        session = requests.Session()
        session.headers = self.parent.headers
        return session
