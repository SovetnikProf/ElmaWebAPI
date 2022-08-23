from .services import AuthService, EntityService, FeedService, FilesService, TaskService, WorkflowService


class API:
    def __init__(self, host: str, username: str, password: str, token: str):
        self.AuthService = AuthService(host=host, session_headers={})
        self.headers = self.AuthService.LoginWithUserName(username, password, token)

        self.EntityService = EntityService(host=host, session_headers=self.headers)
        self.FeedService = FeedService(host=host, session_headers=self.headers)
        self.FilesService = FilesService(host=host, session_headers=self.headers)
        self.TaskService = TaskService(host=host, session_headers=self.headers)
        self.WorkflowService = WorkflowService(host=host, session_headers=self.headers)
