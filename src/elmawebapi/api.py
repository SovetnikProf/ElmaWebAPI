from dataclasses import dataclass
from typing import TYPE_CHECKING, NamedTuple

from .services import AuthService, EntityService, FeedService, FilesService, TaskService, WorkflowService

if TYPE_CHECKING:
    Credentials = NamedTuple("Credentials", [("username", str), ("password", str), ("apptoken", str)])


@dataclass(frozen=True)
class Settings:
    """
    Настройки инстанса API.
    """

    host: str
    username: str
    password: str
    apptoken: str
    max_retries: int = 5


class API:
    """
    Корневой объект для обращения к сервисам API.
    """

    # fmt: off
    __slots__ = (
        "AuthService", "EntityService", "FeedService", "FilesService", "TaskService", "WorkflowService",
        "settings", "headers"
    )
    # fmt: on

    def __init__(self, host: str, username: str, password: str, token: str, max_retries: int = 5):
        self.settings = Settings(host.rstrip("/"), username, password, token, max_retries=max_retries)

        self.AuthService = AuthService(parent=self)
        self.EntityService = EntityService(parent=self)
        self.FeedService = FeedService(parent=self)
        self.FilesService = FilesService(parent=self)
        self.TaskService = TaskService(parent=self)
        self.WorkflowService = WorkflowService(parent=self)

        self.headers = self.reconnect()

    def reconnect(self) -> dict:
        """
        (Пере-)подключиться к серверу Elma.

        Returns:
            dict: словарь заголовков для сессии.
        """
        headers = self.AuthService.LoginWithUserName(*self.credentials)
        return headers

    @property
    def host(self) -> str:
        """
        Адрес сервера Elma.
        """
        return self.settings.host

    @property
    def credentials(self) -> "Credentials":
        """
        Данные для подключения к серверу.
        """
        return self.settings.username, self.settings.password, self.settings.apptoken
