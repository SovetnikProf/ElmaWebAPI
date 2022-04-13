from . import base, decorators
from ..structure import Parser

import requests


START_PROCESS_ASYNC = "/API/REST/Workflow/StartProcessAsync"
STARTABLE_PROCESSES = "/API/REST/Workflow/StartableProcesses"


class WorkflowService(base.Service):
    """Сервис для работы с процессами"""

    @decorators.needs_auth
    @decorators.post(url=START_PROCESS_ASYNC)
    def StartProcess(self, result: requests.Response) -> dict:
        """Стандартная функция API элмы для запуска процесса.

        На вход необходимо передать словарь. Для конкретизации процесса в словаре должен быть один из двух следующих
        параметров:
            - ProcessHeaderId: Id заголовка процесса
            - ProcessToken: токен запуска процесса (находится в параметрах запуска в дизайнере)

        Помимо этого, в словарь необходимо положить контекст процесса Context.

        Args:
            result: результат запуска процесса (передается декоратором автоматически)

        Returns:
            dict: нормализованный словарь результата запуска процесса

        Examples:
            Запуск процесса с заголовком id=1 с передачей в контекст значения "value" в параметр ContextParameter

                result = StartProcess({"ProcessHeaderId": 1, "Context": {"ContextParameter": "value"}})
        """
        return Parser.normalize(result.json())

    @decorators.needs_auth
    @decorators.post(url=STARTABLE_PROCESSES)
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
