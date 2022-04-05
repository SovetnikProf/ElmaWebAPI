from .base import Service

from .decorators import needs_auth, post
from ..structure import Parser

import requests


START_PROCESS_ASYNC = "/API/REST/Workflow/StartProcessAsync"
STARTABLE_PROCESSES = "/API/REST/Workflow/StartableProcesses"


class WorkflowService(Service):
    @needs_auth
    @post(url=START_PROCESS_ASYNC)
    def StartProcess(self, result: requests.Response):
        return Parser.normalize(result.json())

    @needs_auth
    @post(url=STARTABLE_PROCESSES)
    def StartableProcesses(self, result: requests.Response):
        return Parser.normalize(result.json())

    def start_process(self, process_header: int, process_name: str = "", context: dict | None = None):
        if not context:
            context = {}
        data = {"ProcessHeaderId": process_header, "Context": context}
        if process_name:
            data["ProcessName"] = process_name

        data = Parser.uglify(data)
        return self.StartProcess(data)
