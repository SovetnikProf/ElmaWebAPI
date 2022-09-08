from typing import TYPE_CHECKING, NamedTuple

from .services import AuthService, EntityService, FeedService, FilesService, TaskService, WorkflowService

from dataclasses import dataclass

if TYPE_CHECKING:
    Credentials = NamedTuple("Credentials", [("username", str), ("password", str), ("apptoken", str)])


@dataclass(frozen=True)
class Settings:
    username: str
    password: str
    apptoken: str
    max_retries: int = 5

    @property
    def credentials(self) -> "Credentials":
        return self.username, self.password, self.apptoken


class API:
    # fmt: off
    __slots__ = (
        "AuthService", "EntityService", "FeedService", "FilesService", "TaskService", "WorkflowService",
        "settings", "headers"
    )
    # fmt: on

    def __init__(self, host: str, username: str, password: str, token: str, max_retries: int = 5):
        self.settings = Settings(username, password, token, max_retries=max_retries)

        self.AuthService = AuthService(host=host, session_headers={}, parent=self)
        self.headers = self.reconnect()

        self.EntityService = EntityService(host=host, session_headers=self.headers, parent=self)
        self.FeedService = FeedService(host=host, session_headers=self.headers, parent=self)
        self.FilesService = FilesService(host=host, session_headers=self.headers, parent=self)
        self.TaskService = TaskService(host=host, session_headers=self.headers, parent=self)
        self.WorkflowService = WorkflowService(host=host, session_headers=self.headers, parent=self)

    def reconnect(self) -> dict:
        headers = self.AuthService.LoginWithUserName(*self.settings.credentials)
        return headers
